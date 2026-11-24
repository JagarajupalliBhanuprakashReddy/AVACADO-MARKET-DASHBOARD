"""Market Price Analytics Page.

Comprehensive macroeconomic price tracking, volatility analysis,
and seasonal pattern detection across all recorded avocado markets.
"""

from __future__ import annotations
import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import pandas as pd
from services.analytics_service import AnalyticsService
from database.connection import query_to_dataframe
from components.charts import (
    create_line_chart,
    create_bar_chart,
    create_histogram,
    create_heatmap,
)
from services.export_service import ExportService


def render_market_analytics_page():
    """Renders the Market Price Analytics interface."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h2 style="font-size: 22px; font-weight: 700; color: #1b4332; margin-bottom: 4px;">
                Market Price Analytics & Volatility
            </h2>
            <p style="font-size: 13px; color: #64748b; margin: 0;">
                Macroeconomic price movements, price distributions, and temporal seasonality indexes.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    opts = AnalyticsService.get_filter_options()

    c1, c2 = st.columns(2)
    with c1:
        sel_year = st.selectbox("Filter Calendar Year", ["All"] + [str(y) for y in opts["years"]], key="ma_year")
    with c2:
        sel_type = st.selectbox("Filter Product Type", ["All", "Conventional", "Organic"], key="ma_type")

    year_val = None if sel_year == "All" else int(sel_year)
    type_val = None if sel_type == "All" else sel_type.lower()

    # Dynamic KPI Cards
    kpis = AnalyticsService.get_global_kpis(year=year_val, avocado_type=type_val)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Overall Average Price", f"${kpis['overall_avg_price']:.2f}")
    with m2:
        st.metric("Highest Recorded Price", f"${kpis['highest_price']:.2f}")
    with m3:
        st.metric("Lowest Recorded Price", f"${kpis['lowest_price']:.2f}")
    with m4:
        spread = round(kpis['highest_price'] - kpis['lowest_price'], 2)
        st.metric("Price Spread (Range)", f"${spread:.2f}")

    st.markdown("---")

    # Section 1: Price Distribution & Weekly Movements
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 📊 Price Distribution Histogram")
        dist_sql = """
            SELECT o.average_price, t.type_name AS avocado_type
            FROM avocado_observations o
            JOIN dim_avocado_type t ON o.type_id = t.type_id
            JOIN dim_date d ON o.date_id = d.date_id
            WHERE 1=1
        """
        if year_val:
            dist_sql += f" AND d.year = {year_val}"
        if type_val:
            dist_sql += f" AND t.type_name = '{type_val}'"

        dist_df = query_to_dataframe(dist_sql)
        if not dist_df.empty:
            fig_hist = create_histogram(
                dist_df,
                x="average_price",
                color="avocado_type",
                title="Frequency of Recorded Average Prices ($)",
                x_label="Average Price ($)",
            )
            st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        st.markdown("##### 📈 Weekly Price Movement with Rolling Average")
        weekly_sql = """
            SELECT 
                d.year,
                d.week_number,
                MIN(d.full_date) AS week_start_date,
                ROUND(AVG(o.average_price), 2) AS weekly_avg_price
            FROM avocado_observations o
            JOIN dim_date d ON o.date_id = d.date_id
            JOIN dim_avocado_type t ON o.type_id = t.type_id
            WHERE 1=1
        """
        if year_val:
            weekly_sql += f" AND d.year = {year_val}"
        if type_val:
            weekly_sql += f" AND t.type_name = '{type_val}'"
        weekly_sql += " GROUP BY d.year, d.week_number ORDER BY d.year, d.week_number"

        weekly_df = query_to_dataframe(weekly_sql)
        if not weekly_df.empty:
            fig_week = create_line_chart(
                weekly_df,
                x="week_start_date",
                y="weekly_avg_price",
                title="Weekly Average Price ($)",
                x_label="Calendar Date",
                y_label="Price ($)",
            )
            st.plotly_chart(fig_week, use_container_width=True)

    # Section 2: Monthly Seasonality
    st.markdown("##### 🗓️ Monthly Seasonality & Average Price Matrix")
    seas_df = AnalyticsService.get_monthly_seasonality()
    if not seas_df.empty:
        fig_seas = create_bar_chart(
            seas_df,
            x="month_name",
            y="avg_price",
            title="Average Price by Calendar Month across All Recorded Years",
            x_label="Month",
            y_label="Average Price ($)",
        )
        st.plotly_chart(fig_seas, use_container_width=True)

    # Export
    st.markdown("---")
    st.download_button(
        "Download Market Analytics Data (CSV)",
        data=ExportService.dataframe_to_csv(weekly_df),
        file_name="market_analytics_weekly.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from components.header import render_header
    render_header()
    render_market_analytics_page()

