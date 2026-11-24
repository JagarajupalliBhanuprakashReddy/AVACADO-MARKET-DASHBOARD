"""Volume & Market Supply Analysis Page.

Examines recorded physical avocado shipments, PLU size distribution,
and bulk bag packaging composition across tracked market areas.
"""

from __future__ import annotations
import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import pandas as pd
from database.connection import query_to_dataframe
from services.analytics_service import AnalyticsService
from services.export_service import ExportService
from components.charts import (
    create_bar_chart,
    create_donut_chart,
    create_stacked_bar,
    create_horizontal_bar,
)


def render_volume_analysis_page():
    """Renders the Volume & Market Supply Analysis interface."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h2 style="font-size: 22px; font-weight: 700; color: #1b4332; margin-bottom: 4px;">
                Recorded Product Volume & Packaging Composition
            </h2>
            <p style="font-size: 13px; color: #64748b; margin: 0;">
                Analysis of Hass Avocado Board recorded shipment volumes, PLU size groupings, and packaging types.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "ℹ️ **Methodological Note:** Values represent **recorded physical volume** tracked by the Hass Avocado Board. "
        "These metrics measure product movements and shipments, and do not represent individual retail transactions or dollar revenues."
    )

    opts = AnalyticsService.get_filter_options()

    c1, c2 = st.columns(2)
    with c1:
        sel_year = st.selectbox("Calendar Year", ["All"] + [str(y) for y in opts["years"]], key="vol_year")
    with c2:
        sel_region = st.selectbox("Market Region", ["All"] + opts["regions"], key="vol_region")

    year_val = None if sel_year == "All" else int(sel_year)
    region_val = None if sel_region == "All" else sel_region

    dist = AnalyticsService.get_bag_and_plu_distribution(region=region_val, year=year_val)
    tot_vol = dist["total_volume"]
    tot_bags = dist["total_bags"]
    bulk_vol = max(tot_vol - tot_bags, 0.0)

    # Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        v_str = f"{tot_vol/1e9:.2f}B" if tot_vol >= 1e9 else f"{tot_vol/1e6:.1f}M"
        st.metric("Total Recorded Volume", v_str)
    with m2:
        b_str = f"{tot_bags/1e9:.2f}B" if tot_bags >= 1e9 else f"{tot_bags/1e6:.1f}M"
        st.metric("Total Bagged Volume", b_str)
    with m3:
        bulk_str = f"{bulk_vol/1e9:.2f}B" if bulk_vol >= 1e9 else f"{bulk_vol/1e6:.1f}M"
        st.metric("Loose / Bulk Volume", bulk_str)
    with m4:
        bag_ratio = round((tot_bags / tot_vol) * 100, 1) if tot_vol > 0 else 0.0
        st.metric("Bagged Volume Share", f"{bag_ratio}%")

    st.markdown("---")

    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.markdown("##### 🥑 PLU Size Distribution (4046 / 4225 / 4770)")
        plu_df = dist["plu_distribution"]
        if not plu_df.empty:
            fig_plu = create_donut_chart(
                plu_df,
                names="plu_code",
                values="volume",
                title="Recorded Volume by Standard Hass PLU Size",
            )
            st.plotly_chart(fig_plu, use_container_width=True)

    with col_v2:
        st.markdown("##### 🛍️ Packaging Size Breakdown (Bags)")
        bags_df = dist["bag_distribution"]
        if not bags_df.empty:
            fig_bags = create_bar_chart(
                bags_df,
                x="bag_type",
                y="volume",
                color="bag_type",
                title="Recorded Bagged Volume: Small, Large & XLarge",
                x_label="Packaging Size",
                y_label="Units",
            )
            st.plotly_chart(fig_bags, use_container_width=True)

    # Annual Volume Progression
    st.markdown("##### 📅 Annual Recorded Volume Trend")
    yr_sql = """
        SELECT 
            d.year,
            ROUND(SUM(o.total_volume), 2) AS total_volume,
            ROUND(SUM(o.total_bags), 2) AS total_bags,
            ROUND(SUM(o.plu_4046), 2) AS plu_4046,
            ROUND(SUM(o.plu_4225), 2) AS plu_4225,
            ROUND(SUM(o.plu_4770), 2) AS plu_4770
        FROM avocado_observations o
        JOIN dim_date d ON o.date_id = d.date_id
        GROUP BY d.year
        ORDER BY d.year;
    """
    yr_df = query_to_dataframe(yr_sql)
    if not yr_df.empty:
        fig_yr = create_bar_chart(
            yr_df,
            x="year",
            y="total_volume",
            title="Total Recorded Volume by Calendar Year",
            x_label="Year",
            y_label="Recorded Volume",
        )
        st.plotly_chart(fig_yr, use_container_width=True)

    st.markdown("---")
    st.dataframe(yr_df, use_container_width=True)

    st.download_button(
        "Export Annual Volume Data (CSV)",
        data=ExportService.dataframe_to_csv(yr_df),
        file_name="volume_analysis_yearly.csv",
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
    render_volume_analysis_page()

