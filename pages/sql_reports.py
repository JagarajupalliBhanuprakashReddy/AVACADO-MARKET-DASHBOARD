"""Ten Core Analytical SQL Reports Page.

Interactive presentation of the 10 Comprehensive SQL Reports demonstrating
Window Functions, CTEs, Date Manipulations, Joins, and Aggregations.
"""

from __future__ import annotations
import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import pandas as pd
from services.report_service import ReportService
from services.export_service import ExportService
from components.charts import (
    create_line_chart,
    create_bar_chart,
    create_horizontal_bar,
    create_stacked_bar,
    create_donut_chart,
)


def render_sql_reports_page():
    """Renders the comprehensive Ten SQL Reports workbench."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h2 style="font-size: 22px; font-weight: 700; color: #1b4332; margin-bottom: 4px;">
                Ten Core Analytical SQL Reports
            </h2>
            <p style="font-size: 13px; color: #64748b; margin: 0;">
                Live database analytics demonstrating advanced SQL syntax, CTEs, Window functions, and business insights.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    report_list = [
        f"{r['id']}. {r['title'].split(': ')[1]}"
        for r in ReportService.REPORTS.values()
    ]

    selected_report_str = st.selectbox(
        "Select Report to Inspect & Execute",
        report_list,
        index=0,
        key="rep_selector"
    )

    report_id = int(selected_report_str.split(".")[0])

    with st.spinner(f"Executing SQL Report {report_id} on MySQL 8.x..."):
        report = ReportService.run_report(report_id)

    # Header Card
    concepts_pills = " ".join([
        f'<span style="background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-right: 4px;">{c}</span>'
        for c in report["sql_concepts"]
    ])

    st.markdown(
        f"""
        <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px; margin: 12px 0 18px 0;">
            <h3 style="margin: 0 0 6px 0; font-size: 18px; color: #0f172a;">{report['title']}</h3>
            <p style="margin: 0 0 10px 0; font-size: 13px; color: #475569;"><b>Objective:</b> {report['purpose']}</p>
            <div>{concepts_pills}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # View Controls: Chart vs Table vs SQL
    col_v1, col_v2, col_v3 = st.columns([1, 1, 2])
    with col_v1:
        view_mode = st.radio("Display View", ["Chart & Insights", "Raw Data Table"], horizontal=True, key=f"vm_{report_id}")
    with col_v2:
        show_sql = st.checkbox("Show SQL Code", value=True, key=f"ss_{report_id}")

    # Render SQL Code if checked
    if show_sql:
        with st.expander("📄 Executed MySQL 8.x Query", expanded=True):
            st.code(report["sql"], language="sql")

    df: pd.DataFrame = report["df"]

    if view_mode == "Chart & Insights":
        # Interactive Chart Rendering based on report ID
        if not df.empty:
            if report_id == 1:
                fig = create_line_chart(
                    df,
                    x="week_start_date",
                    y="avg_weekly_price",
                    title="Average Recorded Price by Calendar Week ($)",
                    x_label="Week Start Date",
                    y_label="Price ($)",
                )
                st.plotly_chart(fig, use_container_width=True)

            elif report_id == 2:
                fig = create_horizontal_bar(
                    df.head(20),
                    x="total_recorded_volume",
                    y="region",
                    title="Total Recorded Volume by Region (Top 20 Markets)",
                    x_label="Recorded Volume",
                    y_label="Region",
                )
                st.plotly_chart(fig, use_container_width=True)

            elif report_id == 3:
                fig = create_bar_chart(
                    df,
                    x="year",
                    y="avg_price",
                    color="avocado_type",
                    title="Average Price by Avocado Type Across Years ($)",
                    x_label="Year",
                    y_label="Average Price ($)",
                )
                st.plotly_chart(fig, use_container_width=True)

            elif report_id == 4:
                fig = create_bar_chart(
                    df,
                    x="year",
                    y="total_recorded_volume",
                    title="Total Recorded Volume by Calendar Year",
                    x_label="Year",
                    y_label="Recorded Volume",
                )
                st.plotly_chart(fig, use_container_width=True)

            elif report_id == 5:
                fig = create_horizontal_bar(
                    df,
                    x="total_volume",
                    y="region",
                    title="Top 10 Markets by Recorded Volume (Ranking)",
                    x_label="Recorded Volume",
                    y_label="Region",
                )
                st.plotly_chart(fig, use_container_width=True)

            elif report_id == 6:
                fig = create_line_chart(
                    df,
                    x="year_quarter",
                    y="avg_price",
                    color="region",
                    title="Regional Price Trends Over Time (Quarterly)",
                    x_label="Year-Quarter",
                    y_label="Price ($)",
                )
                st.plotly_chart(fig, use_container_width=True)

            elif report_id == 7:
                fig = create_bar_chart(
                    df,
                    x="year",
                    y="organic_premium_pct",
                    title="Organic Price Premium Gap (%) by Year",
                    x_label="Year",
                    y_label="Organic Premium (%)",
                )
                st.plotly_chart(fig, use_container_width=True)

            elif report_id == 8:
                fig = create_stacked_bar(
                    df,
                    x="region",
                    y_cols=["small_bags", "large_bags", "xlarge_bags"],
                    title="Bag Packaging Composition by Region",
                    x_label="Region",
                    y_label="Bags Volume",
                )
                st.plotly_chart(fig, use_container_width=True)

            elif report_id == 9:
                fig = create_stacked_bar(
                    df,
                    x="year",
                    y_cols=["plu_4046_volume", "plu_4225_volume", "plu_4770_volume"],
                    title="Annual Volume Distribution by PLU Size Code",
                    x_label="Year",
                    y_label="Volume",
                )
                st.plotly_chart(fig, use_container_width=True)

            elif report_id == 10:
                fig = create_bar_chart(
                    df,
                    x="month_name",
                    y="seasonality_index",
                    title="Monthly Seasonality Index (Baseline = 100)",
                    x_label="Calendar Month",
                    y_label="Index",
                )
                st.plotly_chart(fig, use_container_width=True)

        # Business Interpretation Box
        st.markdown(
            f"""
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 14px; margin-top: 14px;">
                <div style="font-size: 13px; font-weight: 700; color: #166534; margin-bottom: 4px;">💼 Academic & Business Insight</div>
                <div style="font-size: 13px; color: #15803d; line-height: 1.5;">{report['interpretation']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        # Raw Data Table View
        st.markdown(f"##### Data Table: {report['title']} ({len(df):,} Rows)")
        st.dataframe(df, use_container_width=True)

    # Download Controls
    st.markdown("---")
    c_dl1, c_dl2 = st.columns([1, 4])
    with c_dl1:
        csv_bytes = ExportService.dataframe_to_csv(df)
        st.download_button(
            "📥 Export Report (CSV)",
            data=csv_bytes,
            file_name=f"report_{report_id:02d}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c_dl2:
        pdf_bytes = ExportService.generate_pdf_report(
            report_title=report["title"],
            df=df,
            summary_stats={"Row Count": f"{len(df):,} Rows", "SQL Engine": "MySQL 8.x"},
            interpretation=report["interpretation"],
            sql_query=report["sql"],
        )
        st.download_button(
            "📄 Export Formal Report (PDF)",
            data=pdf_bytes,
            file_name=f"report_{report_id:02d}.pdf",
            mime="application/pdf",
        )


if __name__ == "__main__":
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from components.header import render_header
    render_header()
    render_sql_reports_page()

