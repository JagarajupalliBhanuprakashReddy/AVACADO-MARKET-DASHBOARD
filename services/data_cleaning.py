"""Data Cleaning, Validation, and Preprocessing Service.

Implements rigorous data hygiene for the Avocado Prices dataset according
to production data quality standards.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Tuple
import pandas as pd
import numpy as np


class DataCleaningService:
    """Performs validation, quality checks, and sanitization on raw avocado records."""

    REQUIRED_COLUMNS = [
        "Date", "AveragePrice", "Total Volume", "4046", "4225", "4770",
        "Total Bags", "Small Bags", "Large Bags", "XLarge Bags", "type", "year", "region"
    ]

    COLUMN_MAPPING = {
        "Date": "price_date",
        "AveragePrice": "average_price",
        "Total Volume": "total_volume",
        "4046": "plu_4046",
        "4225": "plu_4225",
        "4770": "plu_4770",
        "Total Bags": "total_bags",
        "Small Bags": "small_bags",
        "Large Bags": "large_bags",
        "XLarge Bags": "xlarge_bags",
        "type": "avocado_type",
        "year": "year",
        "region": "region",
    }

    @classmethod
    def clean_and_validate(cls, file_path_or_df: Any) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Cleans, validates, and reports on the avocado dataset.

        Returns:
            Tuple of (cleaned_df, quality_report)
        """
        if isinstance(file_path_or_df, (str, Path)):
            df = pd.read_csv(file_path_or_df)
        elif isinstance(file_path_or_df, pd.DataFrame):
            df = file_path_or_df.copy()
        else:
            raise ValueError("Input must be a file path or pandas DataFrame")

        raw_count = len(df)
        initial_columns = df.columns.tolist()

        # Check required columns
        missing_cols = [c for c in cls.REQUIRED_COLUMNS if c not in df.columns]
        if missing_cols:
            raise ValueError(f"Dataset is missing required columns: {missing_cols}")

        # Drop index column if present (e.g. 'Unnamed: 0')
        if "Unnamed: 0" in df.columns:
            df = df.drop(columns=["Unnamed: 0"])

        # Check and count missing values
        null_counts = df[cls.REQUIRED_COLUMNS].isnull().sum().to_dict()
        total_nulls = sum(null_counts.values())

        # Check duplicate rows
        subset_keys = ["Date", "region", "type"]
        duplicate_count = df.duplicated(subset=subset_keys).sum()
        df = df.drop_duplicates(subset=subset_keys, keep="first")

        # Standardize column names
        cleaned_df = df.rename(columns=cls.COLUMN_MAPPING)

        # Date validation & parsing
        cleaned_df["price_date"] = pd.to_datetime(cleaned_df["price_date"], errors="coerce")
        invalid_dates = cleaned_df["price_date"].isnull().sum()
        cleaned_df = cleaned_df.dropna(subset=["price_date"])
        cleaned_df["price_date"] = cleaned_df["price_date"].dt.date

        # String cleaning & standardizing
        cleaned_df["avocado_type"] = (
            cleaned_df["avocado_type"].astype(str).str.strip().str.lower()
        )
        cleaned_df["region"] = cleaned_df["region"].astype(str).str.strip()

        # Numeric conversions and domain constraint checks
        numeric_cols = [
            "average_price", "total_volume", "plu_4046", "plu_4225", "plu_4770",
            "total_bags", "small_bags", "large_bags", "xlarge_bags"
        ]
        for col in numeric_cols:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors="coerce").fillna(0.0)
            cleaned_df[col] = cleaned_df[col].clip(lower=0.0)

        cleaned_df["year"] = pd.to_numeric(cleaned_df["year"], errors="coerce").astype(int)

        # Remove rows violating domain logic
        valid_types = {"conventional", "organic"}
        cleaned_df = cleaned_df[cleaned_df["avocado_type"].isin(valid_types)]
        cleaned_df = cleaned_df[cleaned_df["average_price"] > 0]

        cleaned_count = len(cleaned_df)

        report = {
            "raw_record_count": raw_count,
            "cleaned_record_count": cleaned_count,
            "removed_records": raw_count - cleaned_count,
            "missing_values_found": total_nulls,
            "duplicate_records_found": int(duplicate_count),
            "invalid_dates_found": int(invalid_dates),
            "min_date": str(cleaned_df["price_date"].min()) if not cleaned_df.empty else None,
            "max_date": str(cleaned_df["price_date"].max()) if not cleaned_df.empty else None,
            "unique_regions_count": int(cleaned_df["region"].nunique()),
            "years_covered": sorted(cleaned_df["year"].unique().tolist()),
            "types_covered": cleaned_df["avocado_type"].value_counts().to_dict(),
            "overall_avg_price": round(float(cleaned_df["average_price"].mean()), 2) if not cleaned_df.empty else 0.0,
            "total_volume": round(float(cleaned_df["total_volume"].sum()), 2) if not cleaned_df.empty else 0.0,
        }

        return cleaned_df, report
