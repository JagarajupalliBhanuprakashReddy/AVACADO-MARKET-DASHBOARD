"""REPORT 7: Organic vs Conventional Price Gap by Year."""
from services.report_service import ReportService

REPORT_ID = 7

def get_report_metadata():
    return ReportService.get_report(REPORT_ID)

def execute():
    return ReportService.run_report(REPORT_ID)
