"""Interactive Data Explorer Page.

Server-side paginated record inspector backed directly by MySQL queries.
Optimized to never load 18k+ records into client memory.
"""

from __future__ import annotations
import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import pandas as pd
from database.connection import execute_query, execute_scalar, query_to_dataframe
from services.analytics_service import AnalyticsService
from services.export_service import ExportService


def render_data_explorer_page():
    """Renders the server-side paginated Data Explorer."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h2 style="font-size: 22px; font-weight: 700; color: #1b4332; margin-bottom: 4px;">
                Interactive Database Explorer
            </h2>
            <p style="font-size: 13px; color: #64748b; margin: 0;">
                Directly inspect normalized observation records with server-side pagination, multi-field filtering, and sorting.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    opts = AnalyticsService.get_filter_options()

    # Filter Toolbar
    f_c1, f_c2, f_c3, f_c4 = st.columns(4)
    with f_c1:
        f_region = st.selectbox("Market Region", ["All"] + opts["regions"], key="exp_reg")
    with f_c2:
        f_year = st.selectbox("Year", ["All"] + [str(y) for y in opts["years"]], key="exp_yr")
    with f_c3:
        f_type = st.selectbox("Avocado Variety", ["All", "Conventional", "Organic"], key="exp_type")
    with f_c4:
        sort_by = st.selectbox("Sort Order", [
            "Date (Newest First)", "Date (Oldest First)",
            "Price (Highest First)", "Price (Lowest First)",
            "Volume (Highest First)", "Volume (Lowest First)"
        ], key="exp_sort")

    # Keyword search for region or market tier
    f_search = st.text_input("Quick Region Keyword Search", placeholder="e.g. California, Chicago, NewYork...", key="exp_kw")

    # Construct WHERE clause
    conditions = ["1=1"]
    params = []

    if f_region != "All":
        conditions.append("r.region_name = %s")
        params.append(f_region)
    if f_year != "All":
        conditions.append("d.year = %s")
        params.append(int(f_year))
    if f_type != "All":
        conditions.append("t.type_name = %s")
        params.append(f_type.lower())
    if f_search.strip():
        conditions.append("r.region_name LIKE %s")
        params.append(f"%{f_search.strip()}%")

    where_clause = " AND ".join(conditions)

    # Count matching records (server-side)
    count_sql = f"""
        SELECT COUNT(o.observation_id)
        FROM avocado_observations o
        JOIN dim_date d ON o.date_id = d.date_id
        JOIN dim_region r ON o.region_id = r.region_id
        JOIN dim_avocado_type t ON o.type_id = t.type_id
        WHERE {where_clause}
    """
    total_matching = execute_scalar(count_sql, params) or 0

    # Sort mappings
    sort_map = {
        "Date (Newest First)": "d.full_date DESC, o.observation_id DESC",
        "Date (Oldest First)": "d.full_date ASC, o.observation_id ASC",
        "Price (Highest First)": "o.average_price DESC",
        "Price (Lowest First)": "o.average_price ASC",
        "Volume (Highest First)": "o.total_volume DESC",
        "Volume (Lowest First)": "o.total_volume ASC",
    }
    order_by = sort_map.get(sort_by, "d.full_date DESC")

    # Pagination controls
    page_size = 50
    total_pages = max((total_matching + page_size - 1) // page_size, 1)

    c_p1, c_p2, c_p3 = st.columns([1, 1, 3])
    with c_p1:
        current_page = st.number_input("Page Number", min_value=1, max_value=total_pages, value=1, step=1, key="exp_page")
    with c_p2:
        st.markdown(f"<div style='margin-top: 28px; font-size: 13px; color: #64748b;'>of <b>{total_pages:,}</b> pages</div>", unsafe_allow_html=True)
    with c_p3:
        st.markdown(f"<div style='margin-top: 28px; text-align: right; font-size: 13px; font-weight: 600; color: #1e293b;'>Total Records: <span style='color: #2d6a4f;'>{total_matching:,}</span></div>", unsafe_allow_html=True)

    offset = (current_page - 1) * page_size

    # Fetch paginated records
    data_sql = f"""
        SELECT 
            o.observation_id,
            d.full_date AS price_date,
            d.year,
            r.region_name AS region,
            t.type_name AS avocado_type,
            o.average_price,
            o.total_volume,
            o.total_bags,
            o.small_bags,
            o.large_bags,
            o.xlarge_bags,
            o.plu_4046,
            o.plu_4225,
            o.plu_4770
        FROM avocado_observations o
        JOIN dim_date d ON o.date_id = d.date_id
        JOIN dim_region r ON o.region_id = r.region_id
        JOIN dim_avocado_type t ON o.type_id = t.type_id
        WHERE {where_clause}
        ORDER BY {order_by}
        LIMIT {page_size} OFFSET {offset}
    """

    df_page = query_to_dataframe(data_sql, params)

    if not df_page.empty:
        st.dataframe(df_page, use_container_width=True, height=400)
    else:
        st.info("No records match the selected filter criteria.")

    # Export
    st.markdown("---")
    c_e1, c_e2 = st.columns([4, 1])
    with c_e1:
        st.caption("Pagination is executed at the database engine level using MySQL `LIMIT` & `OFFSET`.")
    with c_e2:
        if not df_page.empty:
            csv_bytes = ExportService.dataframe_to_csv(df_page)
            st.download_button(
                "Export Current Page (CSV)",
                data=csv_bytes,
                file_name=f"data_page_{current_page}.csv",
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
    render_data_explorer_page()

