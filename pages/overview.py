"""Overview Dashboard Page.

Displays high-level KPI cards and aggregated executive charts powered by live MySQL queries.
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
from components.kpi_cards import render_overview_kpis
from components.charts import (
    create_line_chart,
    create_horizontal_bar,
    create_bar_chart,
    create_donut_chart,
)
from services.export_service import ExportService


def render_overview_page():
    """Renders the comprehensive overview landing dashboard."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h2 style="font-size: 22px; font-weight: 700; color: #1b4332; margin-bottom: 4px;">
                Executive Market Intelligence Overview
            </h2>
            <p style="font-size: 13px; color: #64748b; margin: 0;">
                Consolidated price, volume, and regional metrics calculated from live MySQL database records.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filter Controls
    options = AnalyticsService.get_filter_options()
    with st.expander("⚙️ Dashboard Scope & Filters", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            sel_year = st.selectbox("Calendar Year", ["All"] + [str(y) for y in options["years"]], key="ov_year")
        with c2:
            sel_region = st.selectbox("Market Region", ["All"] + options["regions"], key="ov_region")
        with c3:
            sel_type = st.selectbox("Avocado Type", ["All"] + [t.capitalize() for t in options["types"]], key="ov_type")

    year_val = None if sel_year == "All" else int(sel_year)
    region_val = None if sel_region == "All" else sel_region
    type_val = None if sel_type == "All" else sel_type.lower()

    # Dynamic KPI Cards
    kpis = AnalyticsService.get_global_kpis(year=year_val, region=region_val, avocado_type=type_val)
    render_overview_kpis(kpis)

    st.markdown("---")

    # Main Visualizations Row 1
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("##### 📈 Historical Price Movement Over Time")
        trend_df = AnalyticsService.get_price_trend_over_time(
            year=year_val, region=region_val, avocado_type=type_val, granularity="month"
        )
        if not trend_df.empty:
            fig_trend = create_line_chart(
                trend_df,
                x="period",
                y="avg_price",
                color="avocado_type",
                title="Monthly Average Recorded Price ($)",
                x_label="Year-Month",
                y_label="Average Price ($)",
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No price trend records found for current filters.")

    with col_right:
        st.markdown("##### 🥑 Organic vs Conventional Price & Volume")
        comp_df = AnalyticsService.get_organic_vs_conventional_comparison(year=year_val)
        if not comp_df.empty:
            fig_comp = create_bar_chart(
                comp_df,
                x="year",
                y="avg_price",
                color="avocado_type",
                title="Annual Average Price by Variety ($)",
                x_label="Year",
                y_label="Average Price ($)",
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("No comparative records available.")

    # Visualizations Row 2
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.markdown("##### 🏆 Top 10 Markets by Recorded Volume")
        top_reg_df = AnalyticsService.get_top_regions_by_volume(limit=10, exclude_total_us=True)
        if not top_reg_df.empty:
            fig_reg = create_horizontal_bar(
                top_reg_df,
                x="total_volume",
                y="region",
                title="Top 10 Metropolitan & Regional Markets (Recorded Units)",
                x_label="Total Volume",
                y_label="Region",
            )
            st.plotly_chart(fig_reg, use_container_width=True)
        else:
            st.info("No regional volume records available.")

    with col_b2:
        st.markdown("##### 📦 Recorded Product Volume Distribution (PLU Codes)")
        dist = AnalyticsService.get_bag_and_plu_distribution(region=region_val, year=year_val)
        plu_df = dist["plu_distribution"]
        if not plu_df.empty:
            fig_plu = create_donut_chart(
                plu_df,
                names="plu_code",
                values="volume",
                title="Hass PLU Proportion (4046 / 4225 / 4770)",
            )
            st.plotly_chart(fig_plu, use_container_width=True)
        else:
            st.info("No PLU distribution data available.")

    # Export Section
    st.markdown("---")
    c_exp1, c_exp2 = st.columns([4, 1])
    with c_exp1:
        st.caption("All metrics are computed via aggregated queries on `avocado_observations` and dimension tables.")
    with c_exp2:
        csv_data = ExportService.dataframe_to_csv(trend_df)
        st.download_button(
            "Export Overview Data (CSV)",
            data=csv_data,
            file_name="overview_metrics.csv",
            mime="text/csv",
            use_container_width=True,
        )


if __name__ == "__main__":
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from components.header import render_header
    render_header()
    render_overview_page()

