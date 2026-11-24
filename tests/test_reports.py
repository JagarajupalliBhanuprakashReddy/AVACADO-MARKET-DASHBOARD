"""Validation Tests for all Ten Mandatory SQL Reports."""

import pytest
from services.report_service import ReportService


@pytest.mark.parametrize("report_id", list(range(1, 11)))
def test_report_execution(report_id):
    """Ensures each of the 10 reports executes without SQL syntax error and returns data."""
    rep = ReportService.run_report(report_id)
    assert rep["id"] == report_id
    assert rep["row_count"] > 0, f"Report {report_id} returned 0 rows"
    assert rep["df"] is not None
    assert len(rep["sql_concepts"]) > 0
    assert len(rep["interpretation"]) > 20
