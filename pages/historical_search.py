"""Historical Agricultural Price Search Engine Page.

Primary application feature allowing natural language and structured investigation
of historical prices, year comparisons, regional movements, and plain-English explanations.
"""

from __future__ import annotations
import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import pandas as pd
from services.historical_search_service import HistoricalSearchService
from services.analytics_service import AnalyticsService
from services.export_service import ExportService
from components.search_bar import render_search_bar
from components.charts import (
    create_line_chart,
    create_bar_chart,
    create_horizontal_bar,
    create_histogram,
)


def render_historical_search_page():
    """Renders the comprehensive Historical Agricultural Price Search Engine."""

    # Top search bar with suggestion pills
    user_query = render_search_bar()

    st.markdown("---")

    tab_nl, tab_compare, tab_filter = st.tabs([
        "🧠 Natural Language Search Results",
        "⚖️ Dedicated Year Comparison Engine",
        "🎛️ Advanced Multi-Filter Investigation"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: NATURAL LANGUAGE SEARCH RESULTS
    # --------------------------------------------------------------------------
    with tab_nl:
        active_query = user_query or st.session_state.get("search_input_val", "Compare avocado prices in 2016 and 2017.")
        st.markdown(f"#### Results for: *\"{active_query}\"*")

        with st.spinner("Analyzing historical market records in MySQL..."):
            res = HistoricalSearchService.parse_natural_language_query(active_query)

        # Coverage Warning check (e.g. user asked for 2020)
        if res.get("coverage_warning"):
            st.warning(f"⚠️ **Temporal Boundary Notice:** {res.get('explanation')}")
            st.info("💡 **Supported Range:** The official Hass Avocado Board dataset contains records from **2015-01-04** to **2018-03-25**.")
        else:
            # Metadata pill row
            c_meta1, c_meta2 = st.columns([3, 1])
            with c_meta1:
                st.markdown(
                    f"""
                    <div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 10px 14px; border-radius: 6px; margin-bottom: 14px;">
                        <div style="font-size: 13px; font-weight: 700; color: #166534;">Interpretation</div>
                        <div style="font-size: 13px; color: #14532d;">{res.get('interpretation')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_meta2:
                df = res.get("df", pd.DataFrame())
                row_cnt = len(df)
                st.metric("Matching Observations", f"{row_cnt:,}")

            # Business Explanation
            st.markdown(f"**Market Insight:** {res.get('explanation')}")

            # Visualization
            if not df.empty:
                chart_type = res.get("chart_type", "bar")
                if res.get("is_comparison"):
                    comp_data = res.get("comp_data", {})
                    c_a, c_b, c_diff = st.columns(3)
                    with c_a:
                        st.metric(f"Avg Price {comp_data['year_a']}", f"${comp_data['data_a'].get('avg_price', 0):.2f}")
                    with c_b:
                        st.metric(f"Avg Price {comp_data['year_b']}", f"${comp_data['data_b'].get('avg_price', 0):.2f}")
                    with c_diff:
                        st.metric("Price Change (%)", f"{comp_data['pct_price_change']}%", delta=f"{comp_data['pct_price_change']}%")

                    fig = create_bar_chart(
                        df,
                        x="year",
                        y="avg_price",
                        title=f"Year Comparison: {comp_data['year_a']} vs {comp_data['year_b']} Average Price ($)",
                        x_label="Year",
                        y_label="Average Price ($)",
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    if "regional_df" in res and not res["regional_df"].empty:
                        st.markdown("##### 📍 Regional Price Discrepancies (% Change)")
                        reg_fig = create_horizontal_bar(
                            res["regional_df"].head(10),
                            x="pct_price_change",
                            y="region_name",
                            title=f"Top 10 Regional Price Moves ({comp_data['year_a']} to {comp_data['year_b']})",
                            x_label="Price Change (%)",
                            y_label="Region",
                        )
                        st.plotly_chart(reg_fig, use_container_width=True)

                elif chart_type == "line":
                    fig = create_line_chart(
                        df,
                        x="price_date",
                        y="average_price",
                        color="avocado_type" if "avocado_type" in df.columns else None,
                        title="Historical Price Trend",
                        x_label="Observation Date",
                        y_label="Average Price ($)",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_type == "gap_chart":
                    fig = create_bar_chart(
                        df,
                        x="year",
                        y="organic_premium_pct",
                        title="Organic Price Premium Over Conventional (%)",
                        x_label="Year",
                        y_label="Premium (%)",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    val_col = "avg_price" if "avg_price" in df.columns else df.columns[1]
                    name_col = df.columns[0]
                    fig = create_bar_chart(
                        df,
                        x=name_col,
                        y=val_col,
                        title=f"{val_col.replace('_', ' ').title()} by {name_col.replace('_', ' ').title()}",
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # View switcher: Toggle between Table & SQL
            col_t1, col_t2 = st.columns([1, 1])
            with col_t1:
                show_table = st.checkbox("Show Detailed Result Table", value=True, key="nl_show_tbl")
            with col_t2:
                show_sql = st.checkbox("Show Executed SQL Statement", value=True, key="nl_show_sql")

            if show_table and not df.empty:
                st.dataframe(df, use_container_width=True, height=220)

            if show_sql and res.get("sql"):
                st.code(res.get("sql"), language="sql")

            # CSV Download
            if not df.empty:
                c_dl, _ = st.columns([2, 3])
                with c_dl:
                    csv_b = ExportService.dataframe_to_csv(df)
                    st.download_button(
                        "📥 Download Search Results (CSV)",
                        data=csv_b,
                        file_name="search_results.csv",
                        mime="text/csv",
                    )

    # --------------------------------------------------------------------------
    # TAB 2: DEDICATED HISTORICAL YEAR COMPARISON ENGINE
    # --------------------------------------------------------------------------
    with tab_compare:
        st.markdown("#### ⚖️ Historical Year Comparison Engine")
        st.caption("Compare market performance across two calendar years using unweighted arithmetic mean price deltas.")

        c_y1, c_y2, c_yr, c_yt = st.columns(4)
        with c_y1:
            cmp_year_a = st.selectbox("Baseline Year (Year A)", [2015, 2016, 2017, 2018], index=1, key="cmp_y_a")
        with c_y2:
            cmp_year_b = st.selectbox("Comparison Year (Year B)", [2015, 2016, 2017, 2018, 2020], index=2, key="cmp_y_b")
        with c_yr:
            opts = AnalyticsService.get_filter_options()
            cmp_reg = st.selectbox("Region Scope", ["All"] + opts["regions"], key="cmp_reg")
        with c_yt:
            cmp_typ = st.selectbox("Product Variety", ["All", "Conventional", "Organic"], key="cmp_typ")

        if st.button("Execute Year Comparison", type="primary", key="btn_exec_cmp"):
            with st.spinner("Executing comparative SQL aggregation..."):
                comp_result = HistoricalSearchService.compare_historical_years(
                    year_a=cmp_year_a,
                    year_b=cmp_year_b,
                    region=cmp_reg,
                    avocado_type=cmp_typ,
                )

            if not comp_result.get("valid"):
                st.error(f"❌ {comp_result.get('error')}")
            else:
                st.success("Comparison calculated successfully!")
                st.markdown(f"**Analysis:** {comp_result.get('explanation')}")

                da = comp_result.get("data_a", {})
                db = comp_result.get("data_b", {})

                # Metric Cards Row
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric(f"Avg Price {cmp_year_a}", f"${da.get('avg_price', 0):.2f}")
                with m2:
                    st.metric(f"Avg Price {cmp_year_b}", f"${db.get('avg_price', 0):.2f}")
                with m3:
                    pct_p = comp_result.get("pct_price_change", 0.0)
                    st.metric("Price Delta (%)", f"{pct_p}%", delta=f"{pct_p}%")
                with m4:
                    pct_v = comp_result.get("pct_volume_change", 0.0)
                    st.metric("Volume Delta (%)", f"{pct_v}%", delta=f"{pct_v}%")

                # Visualizations
                st.markdown("##### 📊 Comparative Breakdown Table")
                st.dataframe(comp_result.get("summary_df"), use_container_width=True)

                reg_diff = comp_result.get("regional_diff_df")
                if reg_diff is not None and not reg_diff.empty:
                    st.markdown("##### 🗺️ Regional Shifts Between Selected Years")
                    st.dataframe(reg_diff.head(20), use_container_width=True, height=250)

                with st.expander("Show Underlying SQL Query"):
                    st.code(comp_result.get("sql"), language="sql")

    # --------------------------------------------------------------------------
    # TAB 3: ADVANCED MULTI-FILTER INVESTIGATION
    # --------------------------------------------------------------------------
    with tab_filter:
        st.markdown("#### 🎛️ Structured Multi-Dimensional Query Builder")

        f_opts = AnalyticsService.get_filter_options()

        row1_c1, row1_c2, row1_c3 = st.columns(3)
        with row1_c1:
            f_years = st.multiselect("Select Years", [2015, 2016, 2017, 2018], default=[2017])
        with row1_c2:
            f_regions = st.multiselect("Select Regions", f_opts["regions"], default=["California", "NewYork", "Chicago"])
        with row1_c3:
            f_types = st.multiselect("Product Type", ["Conventional", "Organic"], default=["Conventional", "Organic"])

        row2_c1, row2_c2, row2_c3, row2_c4 = st.columns(4)
        with row2_c1:
            f_min_p = st.number_input("Min Price ($)", min_value=0.0, max_value=4.0, value=0.5, step=0.1)
        with row2_c2:
            f_max_p = st.number_input("Max Price ($)", min_value=0.5, max_value=5.0, value=2.5, step=0.1)
        with row2_c3:
            f_quarter = st.selectbox("Filter Quarter", ["Any", 1, 2, 3, 4], index=0)
        with row2_c4:
            f_month = st.selectbox("Filter Month", ["Any"] + list(range(1, 13)), index=0)

        if st.button("Apply Structured Filter Search", type="primary", key="btn_apply_struct"):
            with st.spinner("Filtering database records..."):
                s_res = HistoricalSearchService.execute_structured_search(
                    years=f_years,
                    regions=f_regions,
                    avocado_types=f_types,
                    min_price=f_min_p,
                    max_price=f_max_p,
                    quarter=None if f_quarter == "Any" else int(f_quarter),
                    month=None if f_month == "Any" else int(f_month),
                    limit=500
                )

            st.success(f"Query completed: {s_res['record_count']:,} observations found.")
            st.markdown(f"**Interpretation:** {s_res['explanation']}")

            sdf = s_res["df"]
            if not sdf.empty:
                st.dataframe(sdf, use_container_width=True, height=250)

                hist_fig = create_histogram(
                    sdf,
                    x="average_price",
                    color="avocado_type",
                    title="Price Distribution for Filtered Subset",
                    x_label="Average Price ($)",
                )
                st.plotly_chart(hist_fig, use_container_width=True)

                with st.expander("View Parameterized SQL"):
                    st.code(s_res["sql"], language="sql")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from components.header import render_header
    render_header()
    render_historical_search_page()

