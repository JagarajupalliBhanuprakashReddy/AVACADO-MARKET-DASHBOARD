"""REPORT 4: Total Recorded Volume by Year."""
from services.report_service import ReportService

REPORT_ID = 4

def get_report_metadata():
    return ReportService.get_report(REPORT_ID)

def execute():
    return ReportService.run_report(REPORT_ID)
