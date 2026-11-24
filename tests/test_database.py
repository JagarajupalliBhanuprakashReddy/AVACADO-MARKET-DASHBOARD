"""Database Connectivity and Schema Validation Tests."""

import pytest
from database.connection import check_connection_health, execute_scalar, execute_query


def test_mysql_connection_health():
    """Verifies that MySQL is reachable and returns health telemetry."""
    health = check_connection_health()
    assert health["ok"] is True, f"Connection failed: {health.get('error')}"
    assert health["database"] == "agricultural_market_db"
    assert health["latency_ms"] >= 0


def test_table_row_counts():
    """Verifies observation and dimension table counts."""
    obs_count = execute_scalar("SELECT COUNT(*) FROM avocado_observations")
    assert obs_count == 18249, f"Expected 18249 rows, found {obs_count}"

    dim_reg_count = execute_scalar("SELECT COUNT(*) FROM dim_region")
    assert dim_reg_count == 54, f"Expected 54 regions, found {dim_reg_count}"

    dim_date_count = execute_scalar("SELECT COUNT(*) FROM dim_date")
    assert dim_date_count == 169, f"Expected 169 dates, found {dim_date_count}"

    dim_type_count = execute_scalar("SELECT COUNT(*) FROM dim_avocado_type")
    assert dim_type_count == 2, f"Expected 2 types, found {dim_type_count}"


def test_referential_integrity():
    """Verifies that every observation maps to valid foreign keys."""
    orphan_dates = execute_scalar("""
        SELECT COUNT(*) FROM avocado_observations o 
        LEFT JOIN dim_date d ON o.date_id = d.date_id 
        WHERE d.date_id IS NULL
    """)
    assert orphan_dates == 0, "Found orphan date foreign keys"

    orphan_regions = execute_scalar("""
        SELECT COUNT(*) FROM avocado_observations o 
        LEFT JOIN dim_region r ON o.region_id = r.region_id 
        WHERE r.region_id IS NULL
    """)
    assert orphan_regions == 0, "Found orphan region foreign keys"
