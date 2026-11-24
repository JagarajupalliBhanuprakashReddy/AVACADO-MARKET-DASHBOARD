"""Database Management & Administration Page.

Provides schema inspection, live table statistics, index monitoring,
and controlled, validated CRUD operations on MySQL.
"""

from __future__ import annotations
import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import pandas as pd
from datetime import date
from database.connection import (
    check_connection_health,
    execute_query,
    execute_scalar,
    execute_dml,
    query_to_dataframe,
)
from services.analytics_service import AnalyticsService


def render_database_management_page():
    """Renders the administrative Database Management workbench."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h2 style="font-size: 22px; font-weight: 700; color: #1b4332; margin-bottom: 4px;">
                Database Architecture & Administration
            </h2>
            <p style="font-size: 13px; color: #64748b; margin: 0;">
                Live schema inspection, table metadata, index health, and validated CRUD database operations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    health = check_connection_health()

    # Connection Status Banner
    status_color = "#10b981" if health["ok"] else "#ef4444"
    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 18px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-weight: 700; color: #0f172a; font-size: 14px;">MySQL Database Instance</span>
                <div style="font-size: 12px; color: #64748b; margin-top: 2px;">
                    <b>Database:</b> {health['database']} &bull; <b>Server Version:</b> {health['server_version']} &bull; <b>Host:</b> {health['host']}:{health['port']}
                </div>
            </div>
            <div style="text-align: right;">
                <span style="color: {status_color}; font-weight: 700; font-size: 13px;">● {health['status'].upper()}</span>
                <div style="font-size: 11px; color: #94a3b8;">Latency: {health['latency_ms']} ms</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_tables, tab_crud, tab_indexes = st.tabs([
        "📋 Tables & Statistics",
        "✏️ Controlled CRUD Workbench",
        "⚡ Index & Optimization Health"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: TABLES & STATISTICS
    # --------------------------------------------------------------------------
    with tab_tables:
        st.markdown("##### 🗄️ Relational Tables Overview")
        tables_sql = """
            SELECT 
                TABLE_NAME AS table_name,
                TABLE_ROWS AS approximate_rows,
                ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024, 2) AS size_kb,
                TABLE_COLLATION AS collation,
                ENGINE AS engine
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME;
        """
        tables_df = query_to_dataframe(tables_sql)
        st.dataframe(tables_df, use_container_width=True)

        st.markdown("##### 🔍 Table Schema Inspector")
        all_tables = tables_df["table_name"].tolist() if not tables_df.empty else ["avocado_observations", "avocado_prices", "dim_date", "dim_region", "dim_avocado_type", "dataset_metadata"]
        sel_tbl = st.selectbox("Select Table to Inspect Columns & Types", all_tables, key="inspect_tbl")

        col_sql = f"""
            SELECT 
                COLUMN_NAME AS column_name,
                COLUMN_TYPE AS data_type,
                IS_NULLABLE AS is_nullable,
                COLUMN_KEY AS column_key,
                COLUMN_DEFAULT AS default_value,
                EXTRA AS extra
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{sel_tbl}'
            ORDER BY ORDINAL_POSITION;
        """
        cols_df = query_to_dataframe(col_sql)
        st.dataframe(cols_df, use_container_width=True)

    # --------------------------------------------------------------------------
    # TAB 2: CONTROLLED CRUD WORKBENCH
    # --------------------------------------------------------------------------
    with tab_crud:
        st.markdown("##### 🛠️ Database CRUD Management (avocado_prices)")
        st.caption("Perform validated INSERT, READ, UPDATE, and DELETE operations with strict constraint checks.")

        crud_action = st.radio("Select Operation", ["Read Record", "Insert New Record", "Update Record", "Delete Record"], horizontal=True)

        if crud_action == "Read Record":
            c_r1, c_r2 = st.columns([1, 3])
            with c_r1:
                read_id = st.number_input("Lookup by price_id", min_value=1, value=1, step=1)
                btn_read = st.button("Query Record", type="primary")
            with c_r2:
                if btn_read:
                    row_sql = "SELECT * FROM avocado_prices WHERE price_id = %s"
                    rows = execute_query(row_sql, [read_id])
                    if rows:
                        st.json(rows[0])
                    else:
                        st.warning(f"No record found with price_id = {read_id}")

        elif crud_action == "Insert New Record":
            st.markdown("###### Add a New Market Observation")
            opts = AnalyticsService.get_filter_options()
            with st.form("insert_form"):
                ci1, ci2, ci3 = st.columns(3)
                with ci1:
                    new_date = st.date_input("Date", value=date(2018, 4, 1))
                    new_region = st.selectbox("Region", opts["regions"])
                    new_type = st.selectbox("Type", ["conventional", "organic"])
                with ci2:
                    new_price = st.number_input("Average Price ($)", min_value=0.01, max_value=10.0, value=1.45, step=0.01)
                    new_vol = st.number_input("Total Volume", min_value=0.0, value=50000.0, step=100.0)
                    new_year = st.number_input("Year", min_value=2015, max_value=2025, value=2018)
                with ci3:
                    new_4046 = st.number_input("PLU 4046", min_value=0.0, value=15000.0)
                    new_4225 = st.number_input("PLU 4225", min_value=0.0, value=20000.0)
                    new_4770 = st.number_input("PLU 4770", min_value=0.0, value=1000.0)
                    new_bags = st.number_input("Total Bags", min_value=0.0, value=14000.0)

                submit_insert = st.form_submit_button("Insert Record into Database", type="primary")

                if submit_insert:
                    ins_sql = """
                        INSERT INTO avocado_prices (
                            price_date, average_price, total_volume, plu_4046, plu_4225, plu_4770,
                            total_bags, small_bags, large_bags, xlarge_bags, avocado_type, year, region
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    params = (
                        str(new_date), new_price, new_vol, new_4046, new_4225, new_4770,
                        new_bags, new_bags * 0.8, new_bags * 0.2, 0.0, new_type, new_year, new_region
                    )
                    try:
                        res = execute_dml(ins_sql, params)
                        st.success(f"Record inserted successfully! Generated price_id: {res['lastrowid']}")
                    except Exception as e:
                        st.error(f"Insert Failed: {e}")

        elif crud_action == "Update Record":
            st.markdown("###### Update an Existing Observation")
            up_id = st.number_input("Enter price_id to update", min_value=1, value=1, step=1, key="up_id")
            existing = execute_query("SELECT * FROM avocado_prices WHERE price_id = %s", [up_id])

            if existing:
                curr = existing[0]
                with st.form("update_form"):
                    cu1, cu2 = st.columns(2)
                    with cu1:
                        up_price = st.number_input("New Average Price ($)", min_value=0.01, max_value=10.0, value=float(curr["average_price"]), step=0.01)
                    with cu2:
                        up_vol = st.number_input("New Total Volume", min_value=0.0, value=float(curr["total_volume"]), step=100.0)

                    confirm_up = st.checkbox("I confirm this update to the database record", key="chk_conf_up")
                    submit_up = st.form_submit_button("Update Record", type="primary")

                    if submit_up:
                        if not confirm_up:
                            st.warning("Please check the confirmation box before updating.")
                        else:
                            up_sql = "UPDATE avocado_prices SET average_price = %s, total_volume = %s WHERE price_id = %s"
                            try:
                                res = execute_dml(up_sql, [up_price, up_vol, up_id])
                                st.success(f"Record {up_id} updated successfully! (Rows affected: {res['rowcount']})")
                            except Exception as e:
                                st.error(f"Update Failed: {e}")
            else:
                st.warning(f"No record exists with price_id = {up_id}")

        elif crud_action == "Delete Record":
            st.markdown("###### Delete an Observation")
            del_id = st.number_input("Enter price_id to delete", min_value=1, value=18249, step=1, key="del_id")
            del_existing = execute_query("SELECT * FROM avocado_prices WHERE price_id = %s", [del_id])

            if del_existing:
                st.write("Target Record Details:", del_existing[0])
                confirm_del = st.checkbox(f"⚠️ I confirm permanent deletion of record price_id={del_id}", key="chk_conf_del")
                if st.button("Execute Permanent Delete", type="primary"):
                    if not confirm_del:
                        st.error("Deletion rejected: Confirmation checkbox must be checked.")
                    else:
                        del_sql = "DELETE FROM avocado_prices WHERE price_id = %s"
                        try:
                            res = execute_dml(del_sql, [del_id])
                            st.success(f"Record {del_id} deleted successfully! (Rows affected: {res['rowcount']})")
                        except Exception as e:
                            st.error(f"Delete Failed: {e}")
            else:
                st.warning(f"No record found with price_id = {del_id}")

    # --------------------------------------------------------------------------
    # TAB 3: INDEX HEALTH
    # --------------------------------------------------------------------------
    with tab_indexes:
        st.markdown("##### ⚡ Database Indexes & Optimization")
        idx_sql = """
            SELECT 
                TABLE_NAME AS table_name,
                INDEX_NAME AS index_name,
                COLUMN_NAME AS column_name,
                NON_UNIQUE AS non_unique,
                INDEX_TYPE AS index_type
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
            ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;
        """
        idx_df = query_to_dataframe(idx_sql)
        st.dataframe(idx_df, use_container_width=True)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from components.header import render_header
    render_header()
    render_database_management_page()

