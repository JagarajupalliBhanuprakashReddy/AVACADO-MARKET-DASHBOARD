"""Export Service for CSV and Enterprise PDF Reports.

Implements ReportLab PDF rendering with formal executive headers,
tabular summaries, statistical interpretations, and CSV streaming.
"""

from __future__ import annotations
import io
from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class ExportService:
    """Generates structured exports for academic deliverables and executive summaries."""

    @classmethod
    def dataframe_to_csv(cls, df: pd.DataFrame) -> bytes:
        """Converts DataFrame to downloadable CSV bytes."""
        return df.to_csv(index=False).encode("utf-8")

    @classmethod
    def generate_pdf_report(
        cls,
        report_title: str,
        df: pd.DataFrame,
        summary_stats: Optional[Dict[str, Any]] = None,
        filters_applied: Optional[Dict[str, Any]] = None,
        interpretation: Optional[str] = None,
        sql_query: Optional[str] = None,
    ) -> bytes:
        """Constructs an enterprise-grade PDF report with executive layout and tables."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # Custom styling
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#1b4332"),  # Forest green
            fontName="Helvetica-Bold",
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#2d6a4f"),
        )
        meta_style = ParagraphStyle(
            "MetaText",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#495057"),
        )
        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#081c15"),
            spaceBefore=10,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#212529"),
        )
        code_style = ParagraphStyle(
            "CodeBlock",
            parent=styles["Normal"],
            fontSize=7,
            leading=9,
            fontName="Courier",
            textColor=colors.HexColor("#1e293b"),
            backColor=colors.HexColor("#f1f5f9"),
            borderPadding=4,
        )

        elements = []

        # Header
        elements.append(Paragraph("AGRICULTURAL MARKET PRICING & SALES DASHBOARD", title_style))
        elements.append(Paragraph("Enterprise Agricultural Market Intelligence & Historical Pricing Analytics", subtitle_style))
        elements.append(Spacer(1, 4))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2d6a4f"), spaceBefore=2, spaceAfter=8))

        # Metadata bar
        gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"<b>Document:</b> {report_title} | <b>Generated:</b> {gen_time} | <b>Dataset:</b> Avocado Prices (Hass Avocado Board)", meta_style))
        elements.append(Spacer(1, 10))

        # Filters Applied
        if filters_applied:
            elements.append(Paragraph("Active Filter Criteria", h2_style))
            filter_text = " | ".join([f"<b>{k}:</b> {v}" for k, v in filters_applied.items() if v])
            elements.append(Paragraph(filter_text or "No selective filters applied (Full dataset scope)", body_style))
            elements.append(Spacer(1, 8))

        # Key Metrics / Summary Statistics
        if summary_stats:
            elements.append(Paragraph("Summary Statistics", h2_style))
            stat_cells = [[Paragraph(f"<b>{k}</b>", meta_style), Paragraph(str(v), meta_style)] for k, v in summary_stats.items()]
            # Arrange into 2 columns if multiple stats
            stat_table = Table(stat_cells, colWidths=[200, 300])
            stat_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(stat_table)
            elements.append(Spacer(1, 10))

        # Business & Analytical Interpretation
        if interpretation:
            elements.append(Paragraph("Analytical Interpretation", h2_style))
            elements.append(Paragraph(interpretation, body_style))
            elements.append(Spacer(1, 10))

        # SQL Query Documentation
        if sql_query:
            elements.append(Paragraph("SQL Query Executed (MySQL 8.x Engine)", h2_style))
            clean_sql = sql_query.strip().replace("\n", "<br/>&nbsp;&nbsp;")
            elements.append(Paragraph(clean_sql, code_style))
            elements.append(Spacer(1, 10))

        # Tabular Data (preview top 25 rows)
        if not df.empty:
            elements.append(Paragraph(f"Dataset Output Table (Showing Top {min(len(df), 25)} of {len(df):,} Rows)", h2_style))
            preview_df = df.head(25)

            col_names = [Paragraph(f"<b>{c}</b>", meta_style) for c in preview_df.columns]
            table_data = [col_names]

            for _, row in preview_df.iterrows():
                row_cells = []
                for val in row:
                    if isinstance(val, (float, int)):
                        cell_str = f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"
                    else:
                        cell_str = str(val)[:25]
                    row_cells.append(Paragraph(cell_str, meta_style))
                table_data.append(row_cells)

            # Auto-calculate col widths
            num_cols = len(preview_df.columns)
            col_width = 540 / max(num_cols, 1)

            t = Table(table_data, colWidths=[col_width] * num_cols)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b4332")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            elements.append(t)

        # Build document
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
