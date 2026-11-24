"""Dataset Import and ETL Service.

Orchestrates creation of the schema, dimensional modeling (dim_date, dim_region,
dim_avocado_type, avocado_observations), staging imports, and view definitions.
"""

from __future__ import annotations
import calendar
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple
import pandas as pd
from database.connection import get_connection, execute_query, execute_scalar, execute_dml
from services.data_cleaning import DataCleaningService

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class DatasetImportService:
    """ETL engine for populating normalized MySQL star schema."""

    @classmethod
    def initialize_schema(cls) -> bool:
        """Executes database/schema.sql to build relational tables."""
        schema_path = PROJECT_ROOT / "database" / "schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file missing at {schema_path}")

        sql_script = schema_path.read_text(encoding="utf-8")
        conn = get_connection()
        cursor = conn.cursor()
        try:
            for statement in sql_script.split(";"):
                stmt = statement.strip()
                if stmt:
                    cursor.execute(stmt)
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def apply_indexes_and_views(cls) -> bool:
        """Applies database/indexes.sql and database/views.sql."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Views
            views_path = PROJECT_ROOT / "database" / "views.sql"
            if views_path.exists():
                views_sql = views_path.read_text(encoding="utf-8")
                for statement in views_sql.split(";"):
                    stmt = statement.strip()
                    if stmt:
                        cursor.execute(stmt)

            # Indexes (ignore if duplicate)
            indexes_path = PROJECT_ROOT / "database" / "indexes.sql"
            if indexes_path.exists():
                indexes_sql = indexes_path.read_text(encoding="utf-8")
                for statement in indexes_sql.split(";"):
                    stmt = statement.strip()
                    if stmt:
                        try:
                            cursor.execute(stmt)
                        except Exception:
                            # Index might already exist
                            pass
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def populate_dimensions_and_facts(
        cls, progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """Populates dim_date, dim_region, dim_avocado_type, and avocado_observations from avocado_prices."""
        if progress_callback:
            progress_callback(0.1, "Checking base avocado_prices records...")

        total_prices = execute_scalar("SELECT COUNT(*) FROM avocado_prices")
        if not total_prices or total_prices == 0:
            raise ValueError("Base table avocado_prices is empty. Please import raw dataset first.")

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # 1. Populate dim_date
            if progress_callback:
                progress_callback(0.25, "Building and populating Date Dimension (dim_date)...")

            cursor.execute("SELECT DISTINCT price_date FROM avocado_prices ORDER BY price_date")
            dates = [row["price_date"] for row in cursor.fetchall()]

            date_inserts = []
            for d in dates:
                month_name = calendar.month_name[d.month]
                quarter = (d.month - 1) // 3 + 1
                week_number = d.isocalendar()[1]
                is_weekend = d.weekday() >= 5
                date_inserts.append((d, d.day, d.month, month_name, quarter, d.year, week_number, is_weekend))

            date_sql = """
                INSERT IGNORE INTO dim_date 
                (full_date, day, month, month_name, quarter, year, week_number, is_weekend)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(date_sql, date_inserts)
            conn.commit()

            # 2. Populate dim_region
            if progress_callback:
                progress_callback(0.45, "Populating Region Dimension (dim_region)...")

            cursor.execute("SELECT DISTINCT region FROM avocado_prices ORDER BY region")
            regions = [row["region"] for row in cursor.fetchall()]

            region_inserts = []
            for r in regions:
                tier = "National Market" if r == "TotalUS" else (
                    "Multi-State Region" if r in {"West", "California", "Northeast", "Southeast", "SouthCentral", "Midsouth", "GreatLakes", "Plains"}
                    else "Metro / Sub-Regional Market"
                )
                region_inserts.append((r, tier))

            region_sql = """
                INSERT IGNORE INTO dim_region (region_name, market_tier)
                VALUES (%s, %s)
            """
            cursor.executemany(region_sql, region_inserts)
            conn.commit()

            # 3. Populate dim_avocado_type
            if progress_callback:
                progress_callback(0.60, "Populating Product Type Dimension (dim_avocado_type)...")

            type_inserts = [
                ("conventional", "Standard commercial Hass avocados, non-certified organic"),
                ("organic", "USDA certified organic Hass avocados produced without synthetic inputs"),
            ]
            type_sql = """
                INSERT IGNORE INTO dim_avocado_type (type_name, description)
                VALUES (%s, %s)
            """
            cursor.executemany(type_sql, type_inserts)
            conn.commit()

            # 4. Populate avocado_observations (Fact Table)
            if progress_callback:
                progress_callback(0.75, "Loading Fact Table (avocado_observations)...")

            fact_count = execute_scalar("SELECT COUNT(*) FROM avocado_observations")
            if fact_count == 0 or fact_count < total_prices:
                cursor.execute("TRUNCATE TABLE avocado_observations")
                populate_fact_sql = """
                    INSERT INTO avocado_observations (
                        date_id, region_id, type_id, average_price, total_volume,
                        total_bags, small_bags, large_bags, xlarge_bags,
                        plu_4046, plu_4225, plu_4770
                    )
                    SELECT 
                        d.date_id,
                        r.region_id,
                        t.type_id,
                        p.average_price,
                        p.total_volume,
                        p.total_bags,
                        p.small_bags,
                        p.large_bags,
                        p.xlarge_bags,
                        p.plu_4046,
                        p.plu_4225,
                        p.plu_4770
                    FROM avocado_prices p
                    JOIN dim_date d ON p.price_date = d.full_date
                    JOIN dim_region r ON p.region = r.region_name
                    JOIN dim_avocado_type t ON p.avocado_type = t.type_name
                """
                cursor.execute(populate_fact_sql)
                conn.commit()

            # 5. Populate dataset_metadata
            if progress_callback:
                progress_callback(0.90, "Recording dataset provenance metadata...")

            metadata_sql = """
                INSERT INTO dataset_metadata (
                    dataset_name, source_url, record_count, source_file, data_version, data_license, data_publisher
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
            """
            meta_params = (
                "Avocado Prices 2015-2018",
                "https://www.kaggle.com/datasets/neuromusic/avocado-prices",
                total_prices,
                "avocado.csv",
                "v1.0 (Official Hass Avocado Board Data)",
                "Open Database License (ODbL) / Public Domain",
                "Justin Kiggins / Hass Avocado Board (HAB)"
            )
            cursor.execute(metadata_sql, meta_params)
            conn.commit()

            # 6. Build views & indexes
            if progress_callback:
                progress_callback(0.98, "Compiling database analytical views and performance indexes...")

            cls.apply_indexes_and_views()

            if progress_callback:
                progress_callback(1.0, "Database ETL complete!")

            return {
                "total_staged_prices": total_prices,
                "dim_date_count": execute_scalar("SELECT COUNT(*) FROM dim_date"),
                "dim_region_count": execute_scalar("SELECT COUNT(*) FROM dim_region"),
                "dim_type_count": execute_scalar("SELECT COUNT(*) FROM dim_avocado_type"),
                "fact_observations_count": execute_scalar("SELECT COUNT(*) FROM avocado_observations"),
                "views_created": [
                    "vw_avocado_complete",
                    "vw_weekly_price_trends",
                    "vw_regional_performance",
                    "vw_yearly_price_gap",
                    "vw_monthly_seasonality",
                    "vw_bag_distribution",
                ]
            }
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def import_csv_to_staging(
        cls, csv_path_or_df: Any, truncate_first: bool = False,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """Cleans and loads a CSV file into avocado_prices table, then triggers star schema ETL."""
        if progress_callback:
            progress_callback(0.05, "Cleaning and validating input dataset...")

        cleaned_df, report = DataCleaningService.clean_and_validate(csv_path_or_df)

        cls.initialize_schema()

        conn = get_connection()
        cursor = conn.cursor()
        try:
            if truncate_first:
                if progress_callback:
                    progress_callback(0.15, "Clearing previous records...")
                cursor.execute("TRUNCATE TABLE avocado_prices")
                conn.commit()

            if progress_callback:
                progress_callback(0.25, f"Inserting {len(cleaned_df):,} cleaned records into avocado_prices...")

            insert_sql = """
                INSERT INTO avocado_prices (
                    price_date, average_price, total_volume, plu_4046, plu_4225, plu_4770,
                    total_bags, small_bags, large_bags, xlarge_bags, avocado_type, year, region
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Batch insert
            records = cleaned_df[[
                "price_date", "average_price", "total_volume", "plu_4046", "plu_4225", "plu_4770",
                "total_bags", "small_bags", "large_bags", "xlarge_bags", "avocado_type", "year", "region"
            ]].values.tolist()

            batch_size = 2000
            total_batches = (len(records) + batch_size - 1) // batch_size
            for i in range(total_batches):
                batch = records[i * batch_size:(i + 1) * batch_size]
                cursor.executemany(insert_sql, batch)
                conn.commit()
                if progress_callback:
                    prog = 0.25 + 0.35 * ((i + 1) / total_batches)
                    progress_callback(prog, f"Staged {min((i + 1) * batch_size, len(records)):,} / {len(records):,} records...")

            # Run dimensional population
            etl_result = cls.populate_dimensions_and_facts(progress_callback=progress_callback)

            return {
                "cleaning_report": report,
                "etl_result": etl_result,
                "status": "success"
            }
        finally:
            cursor.close()
            conn.close()
