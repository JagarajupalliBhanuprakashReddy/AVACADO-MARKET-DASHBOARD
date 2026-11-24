"""REPORT 1: Average Recorded Price by Calendar Week."""
from services.report_service import ReportService

REPORT_ID = 1

def get_report_metadata():
    return ReportService.get_report(REPORT_ID)

def execute():
    return ReportService.run_report(REPORT_ID)
