"""REPORT 10: Monthly and Seasonal Price Analysis."""
from services.report_service import ReportService

REPORT_ID = 10

def get_report_metadata():
    return ReportService.get_report(REPORT_ID)

def execute():
    return ReportService.run_report(REPORT_ID)
