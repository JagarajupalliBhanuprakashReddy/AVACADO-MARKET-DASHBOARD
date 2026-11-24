"""Analytics Service for Agricultural Market Intelligence.

Provides optimized, database-driven analytical queries for overview,
market trends, regional rankings, product dynamics, and volume composition.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from database.connection import execute_query, execute_scalar, query_to_dataframe


class AnalyticsService:
    """Encapsulates all analytical calculations backed by MySQL queries."""

    @classmethod
    def get_global_kpis(
        cls,
        year: Optional[int] = None,
        region: Optional[str] = None,
        avocado_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calculates global KPI card metrics directly from MySQL with optional filter criteria."""
        conditions = ["1=1"]
        params: List[Any] = []

        if year and year != "All":
            conditions.append("d.year = %s")
            params.append(int(year))
        if region and region != "All":
            conditions.append("r.region_name = %s")
            params.append(region)
        if avocado_type and avocado_type != "All":
            conditions.append("t.type_name = %s")
            params.append(avocado_type.lower())
        if start_date:
            conditions.append("d.full_date >= %s")
            params.append(str(start_date))
        if end_date:
            conditions.append("d.full_date <= %s")
            params.append(str(end_date))

        where_clause = " AND ".join(conditions)

        sql = f"""
            SELECT 
                COUNT(o.observation_id) AS total_records,
                ROUND(AVG(o.average_price), 2) AS overall_avg_price,
                ROUND(SUM(o.total_volume), 2) AS total_volume,
                COUNT(DISTINCT r.region_id) AS num_regions,
                COUNT(DISTINCT t.type_id) AS num_types,
                MIN(d.full_date) AS min_date,
                MAX(d.full_date) AS max_date,
                ROUND(MAX(o.average_price), 2) AS highest_price,
                ROUND(MIN(o.average_price), 2) AS lowest_price,
                ROUND(SUM(o.total_bags), 2) AS total_bags
            FROM avocado_observations o
            JOIN dim_date d ON o.date_id = d.date_id
            JOIN dim_region r ON o.region_id = r.region_id
            JOIN dim_avocado_type t ON o.type_id = t.type_id
            WHERE {where_clause}
        """

        rows = execute_query(sql, params)
        res = rows[0] if rows else {}
        return {
            "total_records": int(res.get("total_records") or 0),
            "overall_avg_price": float(res.get("overall_avg_price") or 0.0),
            "total_volume": float(res.get("total_volume") or 0.0),
            "num_regions": int(res.get("num_regions") or 0),
            "num_types": int(res.get("num_types") or 0),
            "min_date": str(res.get("min_date") or "N/A"),
            "max_date": str(res.get("max_date") or "N/A"),
            "highest_price": float(res.get("highest_price") or 0.0),
            "lowest_price": float(res.get("lowest_price") or 0.0),
            "total_bags": float(res.get("total_bags") or 0.0),
        }

    @classmethod
    def get_filter_options(cls) -> Dict[str, List[Any]]:
        """Returns distinct filter choices directly from database."""
        years_sql = "SELECT DISTINCT year FROM dim_date ORDER BY year"
        years = [row["year"] for row in execute_query(years_sql)]

        regions_sql = "SELECT DISTINCT region_name FROM dim_region ORDER BY region_name"
        regions = [row["region_name"] for row in execute_query(regions_sql)]

        types_sql = "SELECT DISTINCT type_name FROM dim_avocado_type ORDER BY type_name"
        types = [row["type_name"] for row in execute_query(types_sql)]

        date_range_sql = "SELECT MIN(full_date) AS min_date, MAX(full_date) AS max_date FROM dim_date"
        dates = execute_query(date_range_sql)[0]

        return {
            "years": years,
            "regions": regions,
            "types": types,
            "min_date": dates["min_date"],
            "max_date": dates["max_date"],
        }

    @classmethod
    def get_price_trend_over_time(
        cls,
        year: Optional[int] = None,
        region: Optional[str] = None,
        avocado_type: Optional[str] = None,
        granularity: str = "week",
    ) -> pd.DataFrame:
        """Retrieves price trend data grouped by week, month, or date."""
        conditions = ["1=1"]
        params: List[Any] = []

        if year and year != "All":
            conditions.append("d.year = %s")
            params.append(int(year))
        if region and region != "All":
            conditions.append("r.region_name = %s")
            params.append(region)
        if avocado_type and avocado_type != "All":
            conditions.append("t.type_name = %s")
            params.append(avocado_type.lower())

        where_clause = " AND ".join(conditions)

        if granularity == "month":
            sql = f"""
                SELECT 
                    CONCAT(d.year, '-', LPAD(d.month, 2, '0')) AS period,
                    d.year,
                    d.month,
                    d.month_name,
                    t.type_name AS avocado_type,
                    ROUND(AVG(o.average_price), 2) AS avg_price,
                    ROUND(SUM(o.total_volume), 2) AS total_volume
                FROM avocado_observations o
                JOIN dim_date d ON o.date_id = d.date_id
                JOIN dim_region r ON o.region_id = r.region_id
                JOIN dim_avocado_type t ON o.type_id = t.type_id
                WHERE {where_clause}
                GROUP BY d.year, d.month, d.month_name, t.type_name
                ORDER BY d.year, d.month, t.type_name
            """
        else:
            sql = f"""
                SELECT 
                    d.full_date AS period,
                    d.year,
                    d.week_number,
                    t.type_name AS avocado_type,
                    ROUND(AVG(o.average_price), 2) AS avg_price,
                    ROUND(SUM(o.total_volume), 2) AS total_volume
                FROM avocado_observations o
                JOIN dim_date d ON o.date_id = d.date_id
                JOIN dim_region r ON o.region_id = r.region_id
                JOIN dim_avocado_type t ON o.type_id = t.type_id
                WHERE {where_clause}
                GROUP BY d.full_date, d.year, d.week_number, t.type_name
                ORDER BY d.full_date, t.type_name
            """

        return query_to_dataframe(sql, params)

    @classmethod
    def get_top_regions_by_volume(cls, limit: int = 10, exclude_total_us: bool = True) -> pd.DataFrame:
        """Retrieves top regions by recorded volume using SQL ranking."""
        where_filter = "WHERE r.region_name != 'TotalUS'" if exclude_total_us else ""
        sql = f"""
            SELECT 
                r.region_name AS region,
                r.market_tier,
                ROUND(SUM(o.total_volume), 2) AS total_volume,
                ROUND(AVG(o.average_price), 2) AS avg_price,
                ROUND(SUM(o.total_bags), 2) AS total_bags,
                DENSE_RANK() OVER (ORDER BY SUM(o.total_volume) DESC) AS ranking
            FROM avocado_observations o
            JOIN dim_region r ON o.region_id = r.region_id
            {where_filter}
            GROUP BY r.region_id, r.region_name, r.market_tier
            ORDER BY total_volume DESC
            LIMIT {limit}
        """
        return query_to_dataframe(sql)

    @classmethod
    def get_organic_vs_conventional_comparison(cls, year: Optional[int] = None) -> pd.DataFrame:
        """Retrieves Organic vs Conventional breakdown by year."""
        filter_clause = "WHERE d.year = %s" if year and year != "All" else ""
        params = [int(year)] if year and year != "All" else []

        sql = f"""
            SELECT 
                d.year,
                t.type_name AS avocado_type,
                ROUND(AVG(o.average_price), 2) AS avg_price,
                ROUND(MIN(o.average_price), 2) AS min_price,
                ROUND(MAX(o.average_price), 2) AS max_price,
                ROUND(SUM(o.total_volume), 2) AS total_volume,
                ROUND(SUM(o.total_bags), 2) AS total_bags,
                COUNT(o.observation_id) AS observations
            FROM avocado_observations o
            JOIN dim_date d ON o.date_id = d.date_id
            JOIN dim_avocado_type t ON o.type_id = t.type_id
            {filter_clause}
            GROUP BY d.year, t.type_name
            ORDER BY d.year, t.type_name
        """
        return query_to_dataframe(sql, params)

    @classmethod
    def get_monthly_seasonality(cls, region: Optional[str] = None) -> pd.DataFrame:
        """Analyzes monthly price and volume trends."""
        filter_clause = "WHERE r.region_name = %s" if region and region != "All" else ""
        params = [region] if region and region != "All" else []

        sql = f"""
            SELECT 
                d.month,
                d.month_name,
                ROUND(AVG(o.average_price), 2) AS avg_price,
                ROUND(MIN(o.average_price), 2) AS min_price,
                ROUND(MAX(o.average_price), 2) AS max_price,
                ROUND(SUM(o.total_volume), 2) AS total_volume,
                COUNT(o.observation_id) AS record_count
            FROM avocado_observations o
            JOIN dim_date d ON o.date_id = d.date_id
            JOIN dim_region r ON o.region_id = r.region_id
            {filter_clause}
            GROUP BY d.month, d.month_name
            ORDER BY d.month
        """
        return query_to_dataframe(sql, params)

    @classmethod
    def get_bag_and_plu_distribution(cls, region: Optional[str] = None, year: Optional[int] = None) -> Dict[str, Any]:
        """Calculates volume breakdown across PLU codes (4046, 4225, 4770) and Bag sizes."""
        conditions = ["1=1"]
        params: List[Any] = []
        if region and region != "All":
            conditions.append("r.region_name = %s")
            params.append(region)
        if year and year != "All":
            conditions.append("d.year = %s")
            params.append(int(year))

        where_clause = " AND ".join(conditions)

        sql = f"""
            SELECT 
                ROUND(SUM(o.plu_4046), 2) AS total_4046,
                ROUND(SUM(o.plu_4225), 2) AS total_4225,
                ROUND(SUM(o.plu_4770), 2) AS total_4770,
                ROUND(SUM(o.small_bags), 2) AS total_small_bags,
                ROUND(SUM(o.large_bags), 2) AS total_large_bags,
                ROUND(SUM(o.xlarge_bags), 2) AS total_xlarge_bags,
                ROUND(SUM(o.total_bags), 2) AS total_bags,
                ROUND(SUM(o.total_volume), 2) AS total_volume
            FROM avocado_observations o
            JOIN dim_date d ON o.date_id = d.date_id
            JOIN dim_region r ON o.region_id = r.region_id
            WHERE {where_clause}
        """
        rows = execute_query(sql, params)
        res = rows[0] if rows else {}

        plu_df = pd.DataFrame([
            {"plu_code": "4046 (Small/Medium)", "volume": float(res.get("total_4046") or 0)},
            {"plu_code": "4225 (Large)", "volume": float(res.get("total_4225") or 0)},
            {"plu_code": "4770 (Extra Large)", "volume": float(res.get("total_4770") or 0)},
        ])

        bags_df = pd.DataFrame([
            {"bag_type": "Small Bags", "volume": float(res.get("total_small_bags") or 0)},
            {"bag_type": "Large Bags", "volume": float(res.get("total_large_bags") or 0)},
            {"bag_type": "XLarge Bags", "volume": float(res.get("total_xlarge_bags") or 0)},
        ])

        return {
            "plu_distribution": plu_df,
            "bag_distribution": bags_df,
            "total_bags": float(res.get("total_bags") or 0),
            "total_volume": float(res.get("total_volume") or 0),
        }
