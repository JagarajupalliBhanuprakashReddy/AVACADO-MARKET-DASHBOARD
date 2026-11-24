"""REPORT 5: Top 10 Markets by Recorded Volume."""
from services.report_service import ReportService

REPORT_ID = 5

def get_report_metadata():
    return ReportService.get_report(REPORT_ID)

def execute():
    return ReportService.run_report(REPORT_ID)
