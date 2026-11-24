"""REPORT 3: Average Price by Avocado Type."""
from services.report_service import ReportService

REPORT_ID = 3

def get_report_metadata():
    return ReportService.get_report(REPORT_ID)

def execute():
    return ReportService.run_report(REPORT_ID)
