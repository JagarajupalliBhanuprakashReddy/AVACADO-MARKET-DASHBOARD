"""REPORT 2: Total Recorded Volume by Region."""
from services.report_service import ReportService

REPORT_ID = 2

def get_report_metadata():
    return ReportService.get_report(REPORT_ID)

def execute():
    return ReportService.run_report(REPORT_ID)
