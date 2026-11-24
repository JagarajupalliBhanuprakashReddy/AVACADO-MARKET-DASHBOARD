"""Dataset Management: Import & Export Center.

Provides full CSV upload pipelines, automated data hygiene validation,
reproducible dimensional ETL, and multi-format CSV / ReportLab PDF generation.
"""

from __future__ import annotations
import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import pandas as pd
from pathlib import Path
from services.data_cleaning import DataCleaningService
from services.dataset_import import DatasetImportService
from services.export_service import ExportService
from database.connection import query_to_dataframe, execute_scalar
from config.database_config import AppConfig


def render_dataset_management_page():
    """Renders the Dataset Import and Export Center."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h2 style="font-size: 22px; font-weight: 700; color: #1b4332; margin-bottom: 4px;">
                Dataset Provenance, Import & Export Center
            </h2>
            <p style="font-size: 13px; color: #64748b; margin: 0;">
                Validated CSV ingestion, reproducible ETL to dimensional star schema, and multi-format document exporting.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_import, tab_export, tab_provenance = st.tabs([
        "📥 Dataset Ingestion & Validation",
        "📤 Multi-Format Export Center",
        "📜 Provenance & Audit Metadata"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: DATASET INGESTION & VALIDATION
    # --------------------------------------------------------------------------
    with tab_import:
        st.markdown("##### 📁 Upload & Validate Avocado Dataset (CSV)")
        st.caption("Upload a replacement or updated avocado CSV file to trigger data quality checks and star-schema loading.")

        uploaded_file = st.file_uploader("Choose an avocado dataset CSV file", type=["csv"], key="csv_uploader")

        target_file = None
        if uploaded_file is not None:
            target_file = uploaded_file
        else:
            local_raw = AppConfig.DATA_RAW_DIR / "avocado.csv"
            if local_raw.exists():
                st.info(f"💡 Default official dataset available: `{local_raw.name}` ({local_raw.stat().st_size:,} bytes)")
                if st.button("Load and Validate Default avocado.csv", key="btn_load_default"):
                    target_file = str(local_raw)

        if target_file:
            with st.spinner("Executing rigorous data hygiene and constraint validation..."):
                try:
                    cleaned_df, report = DataCleaningService.clean_and_validate(target_file)
                    st.success("Dataset successfully passed validation criteria!")

                    # Quality Report Metrics
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.metric("Raw Observations", f"{report['raw_record_count']:,}")
                    with c2:
                        st.metric("Valid Observations", f"{report['cleaned_record_count']:,}")
                    with c3:
                        st.metric("Duplicates Filtered", f"{report['duplicate_records_found']:,}")
                    with c4:
                        st.metric("Missing Values", f"{report['missing_values_found']:,}")

                    st.markdown("###### Preview of Cleaned & Standardized Data")
                    st.dataframe(cleaned_df.head(10), use_container_width=True)

                    st.markdown("---")
                    st.markdown("##### ⚙️ Execute Database Staging & Dimensional ETL")
                    re_etl = st.checkbox("Truncate staging before import (replaces existing records)", value=False)

                    if st.button("Execute Full ETL into MySQL Database", type="primary"):
                        progress_bar = st.progress(0.0)
                        status_box = st.empty()

                        def update_prog(p, msg):
                            progress_bar.progress(p)
                            status_box.markdown(f"**Step:** {msg}")

                        import_res = DatasetImportService.import_csv_to_staging(
                            cleaned_df, truncate_first=re_etl, progress_callback=update_prog
                        )
                        st.balloons()
                        st.success("ETL process completed successfully!")
                        st.json(import_res["etl_result"])

                except Exception as e:
                    st.error(f"Validation / Import Failed: {str(e)}")

    # --------------------------------------------------------------------------
    # TAB 2: MULTI-FORMAT EXPORT CENTER
    # --------------------------------------------------------------------------
    with tab_export:
        st.markdown("##### 📤 Academic Export Center (CSV & ReportLab PDF)")
        st.caption("Generate formal academic deliverables and raw data extractions.")

        c_exp1, c_exp2 = st.columns(2)

        with c_exp1:
            st.markdown("###### 📊 Complete Staged Observations (CSV)")
            st.write("Extract verified records directly from MySQL `avocado_prices`.")
            if st.button("Generate CSV Extract"):
                full_df = query_to_dataframe("SELECT * FROM avocado_prices LIMIT 5000")
                csv_bytes = ExportService.dataframe_to_csv(full_df)
                st.download_button(
                    "Download Observations CSV (5k Preview)",
                    data=csv_bytes,
                    file_name="avocado_prices_extract.csv",
                    mime="text/csv",
                )

        with c_exp2:
            st.markdown("###### 📄 Executive Market Intelligence Report (PDF)")
            st.write("Generate a formatted enterprise executive brief rendered via ReportLab.")
            report_kind = st.selectbox("Select Report Domain for PDF Export", [
                "Overall Historical Market Summary",
                "Organic vs Conventional Premium Analysis",
                "Top 10 Volume Markets & Rankings",
                "Monthly Price Seasonality Index"
            ])

            if st.button("Generate Executive PDF Report", type="primary"):
                with st.spinner("Compiling executive PDF document via ReportLab..."):
                    if "Organic" in report_kind:
                        pdf_df = query_to_dataframe("SELECT * FROM vw_yearly_price_gap")
                        interp = "Organic avocados consistently trade at an average premium of 34% to 55% over conventional Hass."
                    elif "Top 10" in report_kind:
                        pdf_df = query_to_dataframe("SELECT * FROM vw_regional_performance LIMIT 10")
                        interp = "West and California regions command the highest recorded volume distributions nationwide."
                    else:
                        pdf_df = query_to_dataframe("SELECT * FROM vw_monthly_seasonality")
                        interp = "September and October demonstrate the sharpest price peaks due to seasonal volume troughs."

                    pdf_bytes = ExportService.generate_pdf_report(
                        report_title=f"Executive Market Intelligence: {report_kind}",
                        df=pdf_df,
                        summary_stats={
                            "Platform": "Agricultural Market Pricing & Sales Intelligence Suite",
                            "Database Engine": "MySQL 8.x Enterprise",
                            "Dataset Source": "Hass Avocado Board (HAB) / Kaggle",
                            "Records Covered": "18,249 Observations (2015-2018)"
                        },
                        interpretation=interp,
                        sql_query="SELECT * FROM vw_... [Analyzed Database View]",
                    )

                    st.download_button(
                        "📥 Download Generated PDF Report",
                        data=pdf_bytes,
                        file_name=f"{report_kind.lower().replace(' ', '_')}.pdf",
                        mime="application/pdf",
                    )

    # --------------------------------------------------------------------------
    # TAB 3: PROVENANCE & AUDIT METADATA
    # --------------------------------------------------------------------------
    with tab_provenance:
        st.markdown("##### 📜 Dataset Provenance & Audit Log")
        meta_sql = "SELECT * FROM dataset_metadata ORDER BY dataset_id DESC"
        meta_df = query_to_dataframe(meta_sql)
        if not meta_df.empty:
            st.dataframe(meta_df, use_container_width=True)
        else:
            st.info("No metadata records logged yet. Run ETL to register provenance.")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from components.header import render_header
    render_header()
    render_dataset_management_page()

