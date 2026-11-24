"""Regional Market Analysis Page.

Investigates geographic market variances, regional volume ranking,
and price divergence across metropolitan and regional territories.
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
    create_horizontal_bar,
    create_bar_chart,
    create_line_chart,
)


def render_regional_analysis_page():
    """Renders the Regional Market Analysis interface."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h2 style="font-size: 22px; font-weight: 700; color: #1b4332; margin-bottom: 4px;">
                Regional Market Differences & Rankings
            </h2>
            <p style="font-size: 13px; color: #64748b; margin: 0;">
                Compare prices, volumes, and market tiers across 54 tracked agricultural regions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    opts = AnalyticsService.get_filter_options()

    c1, c2 = st.columns([3, 1])
    with c1:
        selected_regions = st.multiselect(
            "Select Regions to Compare",
            [r for r in opts["regions"] if r != "TotalUS"],
            default=["California", "NewYork", "Chicago", "Houston", "Atlanta", "Seattle"],
            key="reg_multisel"
        )
    with c2:
        reg_year = st.selectbox("Year", ["All"] + [str(y) for y in opts["years"]], key="reg_year")

    year_filter = f"AND d.year = {reg_year}" if reg_year != "All" else ""

    # Top Rankings Section
    col_rank1, col_rank2 = st.columns(2)

    with col_rank1:
        st.markdown("##### 💎 Highest-Priced Regions (Top 10)")
        high_sql = f"""
            SELECT 
                r.region_name AS region,
                r.market_tier,
                ROUND(AVG(o.average_price), 2) AS avg_price,
                ROUND(SUM(o.total_volume), 2) AS total_volume,
                DENSE_RANK() OVER (ORDER BY AVG(o.average_price) DESC) AS price_rank
            FROM avocado_observations o
            JOIN dim_region r ON o.region_id = r.region_id
            JOIN dim_date d ON o.date_id = d.date_id
            WHERE r.region_name != 'TotalUS' {year_filter}
            GROUP BY r.region_id, r.region_name, r.market_tier
            ORDER BY avg_price DESC
            LIMIT 10;
        """
        high_df = query_to_dataframe(high_sql)
        if not high_df.empty:
            fig_high = create_horizontal_bar(
                high_df,
                x="avg_price",
                y="region",
                title="Top 10 Highest Average Prices ($)",
                x_label="Average Price ($)",
                y_label="Region",
            )
            st.plotly_chart(fig_high, use_container_width=True)

    with col_rank2:
        st.markdown("##### 🏷️ Lowest-Priced Regions (Most Affordable 10)")
        low_sql = f"""
            SELECT 
                r.region_name AS region,
                r.market_tier,
                ROUND(AVG(o.average_price), 2) AS avg_price,
                ROUND(SUM(o.total_volume), 2) AS total_volume,
                DENSE_RANK() OVER (ORDER BY AVG(o.average_price) ASC) AS affordability_rank
            FROM avocado_observations o
            JOIN dim_region r ON o.region_id = r.region_id
            JOIN dim_date d ON o.date_id = d.date_id
            WHERE r.region_name != 'TotalUS' {year_filter}
            GROUP BY r.region_id, r.region_name, r.market_tier
            ORDER BY avg_price ASC
            LIMIT 10;
        """
        low_df = query_to_dataframe(low_sql)
        if not low_df.empty:
            fig_low = create_horizontal_bar(
                low_df,
                x="avg_price",
                y="region",
                title="Top 10 Lowest Average Prices ($)",
                x_label="Average Price ($)",
                y_label="Region",
            )
            st.plotly_chart(fig_low, use_container_width=True)

    st.markdown("---")

    # Multi-Region Comparison View
    if selected_regions:
        st.markdown("##### 📍 Selected Region Multi-Comparison")
        placeholders = ", ".join(["%s"] * len(selected_regions))
        params = selected_regions[:]

        comp_sql = f"""
            SELECT 
                r.region_name AS region,
                ROUND(AVG(o.average_price), 2) AS avg_price,
                ROUND(MIN(o.average_price), 2) AS min_price,
                ROUND(MAX(o.average_price), 2) AS max_price,
                ROUND(SUM(o.total_volume), 2) AS total_volume,
                ROUND(SUM(o.total_bags), 2) AS total_bags,
                ROUND(AVG(CASE WHEN t.type_name = 'organic' THEN o.average_price END), 2) AS organic_avg_price,
                ROUND(AVG(CASE WHEN t.type_name = 'conventional' THEN o.average_price END), 2) AS conventional_avg_price
            FROM avocado_observations o
            JOIN dim_region r ON o.region_id = r.region_id
            JOIN dim_avocado_type t ON o.type_id = t.type_id
            JOIN dim_date d ON o.date_id = d.date_id
            WHERE r.region_name IN ({placeholders}) {year_filter}
            GROUP BY r.region_id, r.region_name
            ORDER BY total_volume DESC;
        """
        comp_df = query_to_dataframe(comp_sql, params)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_p = create_bar_chart(
                comp_df,
                x="region",
                y="avg_price",
                title="Average Price Comparison Across Selected Regions ($)",
                x_label="Region",
                y_label="Average Price ($)",
            )
            st.plotly_chart(fig_p, use_container_width=True)

        with col_c2:
            fig_v = create_bar_chart(
                comp_df,
                x="region",
                y="total_volume",
                title="Total Recorded Volume Across Selected Regions (Units)",
                x_label="Region",
                y_label="Recorded Volume",
            )
            st.plotly_chart(fig_v, use_container_width=True)

        st.dataframe(comp_df, use_container_width=True)

        # Export
        st.download_button(
            "Export Selected Regional Comparison (CSV)",
            data=ExportService.dataframe_to_csv(comp_df),
            file_name="regional_comparison.csv",
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
    render_regional_analysis_page()

