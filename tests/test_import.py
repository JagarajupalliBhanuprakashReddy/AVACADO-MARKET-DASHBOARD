"""Dataset Cleaning and Preprocessing Validation Tests."""

import pytest
import pandas as pd
from services.data_cleaning import DataCleaningService
from config.database_config import AppConfig


def test_data_cleaning_with_raw_csv():
    """Verifies that DataCleaningService properly sanitizes avocado.csv."""
    raw_path = AppConfig.DATA_RAW_DIR / "avocado.csv"
    assert raw_path.exists(), f"Raw dataset missing at {raw_path}"

    cleaned_df, report = DataCleaningService.clean_and_validate(raw_path)

    assert report["cleaned_record_count"] == 18249
    assert report["missing_values_found"] == 0
    assert report["duplicate_records_found"] == 0
    assert report["unique_regions_count"] == 54
    assert report["years_covered"] == [2015, 2016, 2017, 2018]
    assert "conventional" in report["types_covered"]
    assert "organic" in report["types_covered"]
    assert report["overall_avg_price"] > 0
    assert len(cleaned_df) == 18249
