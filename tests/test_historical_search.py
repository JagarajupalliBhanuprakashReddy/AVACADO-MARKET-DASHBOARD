"""Validation Tests for Historical Search and Year Comparison Engine."""

import pytest
from services.historical_search_service import HistoricalSearchService


def test_year_comparison_math():
    """Verifies percentage change formula: ((New - Old) / Old) * 100."""
    res = HistoricalSearchService.compare_historical_years(2016, 2017)
    assert res["valid"] is True
    assert "pct_price_change" in res

    data_a = res["data_a"]
    data_b = res["data_b"]
    avg_a = float(data_a["avg_price"])
    avg_b = float(data_b["avg_price"])

    expected_pct = round(((avg_b - avg_a) / avg_a) * 100, 2)
    assert res["pct_price_change"] == expected_pct


def test_out_of_bounds_year_validation():
    """Verifies that out-of-bounds years like 2020 are safely rejected with informative messages."""
    res = HistoricalSearchService.compare_historical_years(2016, 2020)
    assert res["valid"] is False
    assert "2020" in res["error"]
    assert "2015" in res["error"] and "2018" in res["error"]


def test_natural_language_intent_resolution():
    """Verifies NL parsing for common queries."""
    res = HistoricalSearchService.parse_natural_language_query("Which region had the highest price in 2018?")
    assert not res.get("coverage_warning")
    assert not res["df"].empty
    assert "highest" in res["interpretation"].lower()
