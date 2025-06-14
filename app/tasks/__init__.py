from .celery_app import celery_app
from .data_processing import process_excel_data
from .ai_analysis import generate_ai_analysis
from .report_generation import generate_pdf_report, generate_ppt_report

# 导出所有任务
__all__ = [
    "celery_app",
    "process_excel_data",
    "generate_ai_analysis",
    "generate_pdf_report",
    "generate_ppt_report"
] 