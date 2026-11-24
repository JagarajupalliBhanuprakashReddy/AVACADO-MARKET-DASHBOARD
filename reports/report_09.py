"""REPORT 9: PLU-Based Product Volume Distribution."""
from services.report_service import ReportService

REPORT_ID = 9

def get_report_metadata():
    return ReportService.get_report(REPORT_ID)

def execute():
    return ReportService.run_report(REPORT_ID)
