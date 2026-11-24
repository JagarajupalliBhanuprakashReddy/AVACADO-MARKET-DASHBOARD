"""Product Type Analysis Page.

Deep dive into Organic vs Conventional pricing dynamics,
market share evolution, price premiums, and monthly trends.
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
    create_line_chart,
)


def render_product_analysis_page():
    """Renders the Product Type Analysis interface."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h2 style="font-size: 22px; font-weight: 700; color: #1b4332; margin-bottom: 4px;">
                Product Type Analysis: Organic vs Conventional
            </h2>
            <p style="font-size: 13px; color: #64748b; margin: 0;">
                Comparative evaluation of certified organic vs conventional Hass avocados across price, volume, and premium ratios.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    opts = AnalyticsService.get_filter_options()

    c_f1, c_f2 = st.columns(2)
    with c_f1:
        sel_year = st.selectbox("Calendar Year", ["All"] + [str(y) for y in opts["years"]], key="prod_year")
    with c_f2:
        sel_region = st.selectbox("Market Region", ["All"] + opts["regions"], key="prod_region")

    conditions = ["1=1"]
    params = []
    if sel_year != "All":
        conditions.append("d.year = %s")
        params.append(int(sel_year))
    if sel_region != "All":
        conditions.append("r.region_name = %s")
        params.append(sel_region)

    where_clause = " AND ".join(conditions)

    # Aggregated Summary SQL
    summary_sql = f"""
        SELECT 
            t.type_name AS avocado_type,
            COUNT(o.observation_id) AS total_records,
            ROUND(AVG(o.average_price), 2) AS avg_price,
            ROUND(MIN(o.average_price), 2) AS min_price,
            ROUND(MAX(o.average_price), 2) AS max_price,
            ROUND(SUM(o.total_volume), 2) AS total_volume,
            ROUND(SUM(o.total_bags), 2) AS total_bags
        FROM avocado_observations o
        JOIN dim_avocado_type t ON o.type_id = t.type_id
        JOIN dim_date d ON o.date_id = d.date_id
        JOIN dim_region r ON o.region_id = r.region_id
        WHERE {where_clause}
        GROUP BY t.type_id, t.type_name;
    """
    summary_df = query_to_dataframe(summary_sql, params)

    conv_row = summary_df[summary_df["avocado_type"] == "conventional"].to_dict(orient="records")
    org_row = summary_df[summary_df["avocado_type"] == "organic"].to_dict(orient="records")

    conv_data = conv_row[0] if conv_row else {}
    org_data = org_row[0] if org_row else {}

    conv_avg = float(conv_data.get("avg_price") or 0.0)
    org_avg = float(org_data.get("avg_price") or 0.0)
    price_gap = round(org_avg - conv_avg, 2)
    premium_pct = round(((org_avg - conv_avg) / conv_avg) * 100, 2) if conv_avg > 0 else 0.0

    # Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Conventional Avg Price", f"${conv_avg:.2f}")
    with m2:
        st.metric("Organic Avg Price", f"${org_avg:.2f}")
    with m3:
        st.metric("Organic Premium ($)", f"${price_gap:.2f}", delta=f"+${price_gap:.2f}")
    with m4:
        st.metric("Premium Percentage", f"{premium_pct}%", delta=f"{premium_pct}%")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("##### 📦 Recorded Volume Share by Variety")
        if not summary_df.empty:
            fig_share = create_donut_chart(
                summary_df,
                names="avocado_type",
                values="total_volume",
                title="Market Share of Recorded Volume",
            )
            st.plotly_chart(fig_share, use_container_width=True)

    with col_right:
        st.markdown("##### 💵 Average Price Comparison")
        if not summary_df.empty:
            fig_price = create_bar_chart(
                summary_df,
                x="avocado_type",
                y="avg_price",
                color="avocado_type",
                title="Average Unit Price by Variety ($)",
                x_label="Avocado Type",
                y_label="Price ($)",
            )
            st.plotly_chart(fig_price, use_container_width=True)

    # Monthly Trends by Type
    st.markdown("##### 🗓️ Monthly Average Price Trends: Organic vs Conventional")
    monthly_sql = f"""
        SELECT 
            d.month,
            d.month_name,
            t.type_name AS avocado_type,
            ROUND(AVG(o.average_price), 2) AS monthly_avg_price,
            ROUND(SUM(o.total_volume), 2) AS monthly_volume
        FROM avocado_observations o
        JOIN dim_date d ON o.date_id = d.date_id
        JOIN dim_avocado_type t ON o.type_id = t.type_id
        JOIN dim_region r ON o.region_id = r.region_id
        WHERE {where_clause}
        GROUP BY d.month, d.month_name, t.type_name
        ORDER BY d.month, t.type_name;
    """
    monthly_df = query_to_dataframe(monthly_sql, params)
    if not monthly_df.empty:
        fig_month = create_line_chart(
            monthly_df,
            x="month_name",
            y="monthly_avg_price",
            color="avocado_type",
            title="Monthly Price Cycles by Product Variety ($)",
            x_label="Month",
            y_label="Average Price ($)",
        )
        st.plotly_chart(fig_month, use_container_width=True)

    st.markdown("---")
    st.dataframe(summary_df, use_container_width=True)

    st.download_button(
        "Download Product Type Analysis (CSV)",
        data=ExportService.dataframe_to_csv(summary_df),
        file_name="product_type_analysis.csv",
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
    render_product_analysis_page()

