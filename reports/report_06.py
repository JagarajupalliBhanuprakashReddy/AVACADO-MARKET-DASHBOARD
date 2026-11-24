"""REPORT 6: Regional Price Trends Over Time."""
from services.report_service import ReportService

REPORT_ID = 6

def get_report_metadata():
    return ReportService.get_report(REPORT_ID)

def execute():
    return ReportService.run_report(REPORT_ID)
