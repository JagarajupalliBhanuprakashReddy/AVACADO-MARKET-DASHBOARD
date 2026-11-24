"""SQL Safety and Validation Guardrail Tests."""

import pytest
from services.ai_sql_service import AISQLService


def test_safe_select_allowed():
    """Ensures benign SELECT queries pass validation."""
    sql = "SELECT region_name, AVG(average_price) FROM vw_avocado_complete GROUP BY region_name;"
    is_safe, cleaned = AISQLService.sanitize_and_validate_sql(sql)
    assert is_safe is True
    assert "limit" in cleaned.lower()


def test_destructive_sql_rejected():
    """Ensures destructive statements (DROP, DELETE, UPDATE, INSERT) are blocked."""
    destructive_queries = [
        "DROP TABLE avocado_prices;",
        "DELETE FROM avocado_observations WHERE 1=1;",
        "UPDATE avocado_prices SET average_price = 0;",
        "INSERT INTO avocado_prices (average_price) VALUES (99);",
        "ALTER TABLE dim_date ADD COLUMN test_col INT;",
        "TRUNCATE TABLE dim_region;",
    ]
    for q in destructive_queries:
        is_safe, msg = AISQLService.sanitize_and_validate_sql(q)
        assert is_safe is False, f"Expected query to be rejected: {q}"
        assert "Security Violation" in msg
