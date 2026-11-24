"""About Project Page.

Contains system architecture, core capabilities, ER model description,
and official dataset provenance.
"""

from __future__ import annotations
import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st


def render_about_page():
    """Renders the comprehensive system overview and architecture page."""
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h2 style="font-size: 24px; font-weight: 800; color: #1b4332; margin-bottom: 6px;">
                Agricultural Market Pricing & Sales Dashboard
            </h2>
            <div style="font-size: 14px; color: #475569; line-height: 1.6;">
                <b>Platform Classification:</b> Enterprise Agricultural Intelligence & Sales Analytics Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Core Architectural Pillars Card
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); 
                    border-radius: 10px; padding: 20px; color: white; margin-bottom: 24px;">
            <h4 style="margin: 0 0 12px 0; color: #6ee7b7; font-size: 16px;">🏛️ System Architecture & Engineering Pillars</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px;">
                <div style="background: rgba(255,255,255,0.08); padding: 12px; border-radius: 6px;">
                    <div style="font-size: 14px; font-weight: 700;">1. High-Performance Relational OLAP</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 2px;">MySQL 8.x 3NF star schema with sub-5ms indexed aggregations</div>
                </div>
                <div style="background: rgba(255,255,255,0.08); padding: 12px; border-radius: 6px;">
                    <div style="font-size: 14px; font-weight: 700;">2. Schema-Aware AI SQL Assistant</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 2px;">Local LLM translation with strict read-only safety validation</div>
                </div>
                <div style="background: rgba(255,255,255,0.08); padding: 12px; border-radius: 6px;">
                    <div style="font-size: 14px; font-weight: 700;">3. Real-Time Price Intelligence</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 2px;">Multi-year percentage change engine and regional rankings</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Project Objectives & Mission")
        st.markdown(
            """
            The primary mission of the **Agricultural Market Pricing & Sales Dashboard** is to build a unified, 
            production-grade database intelligence platform that enables agricultural economists, supply chain managers, 
            and retail analysts to:
            
            - **Investigate Historical Price Movements:** Uncover macro and micro-trends across 2015 to 2018.
            - **Compare Multi-Year Baselines:** Calculate exact percentage changes across calendar periods.
            - **Analyze Regional Divergence:** Examine price-volume spreads across 54 tracked metropolitan and regional markets.
            - **Assess Variety Premiums:** Quantify the price gap between USDA Certified Organic and Conventional Hass avocados.
            - **Execute Sophisticated SQL Reports:** Demonstrate real-world CTEs, Window Functions (`RANK`, `DENSE_RANK`), aggregations, and joins.
            - **Leverage Natural Language SQL:** Enable intuitive ad-hoc queries via local Ollama LLM integration.
            """
        )

        st.markdown("### 🥑 Dataset Provenance & Attribution")
        st.markdown(
            """
            - **Dataset Name:** Avocado Prices
            - **Source Repository:** [Kaggle Dataset](https://www.kaggle.com/datasets/neuromusic/avocado-prices)
            - **Original Publisher:** Justin Kiggins (compiled from official Hass Avocado Board data)
            - **License:** Open Database License (ODbL) / Public Domain
            - **Total Verified Observations:** 18,249 rows (0 missing values)
            - **Temporal Coverage:** January 4, 2015 to March 25, 2018
            - **Key Distinction:** *Total Volume* represents recorded physical unit shipments reported to the Hass Avocado Board, not transaction-level sales revenue.
            """
        )

    with col2:
        st.markdown("### 🏗️ Database Architecture & Normalization")
        st.markdown(
            """
            The underlying database (`agricultural_market_db`) implements a **3NF Star Schema** to ensure referential integrity, eliminate data redundancy, and optimize OLAP queries:
            
            1. **`avocado_observations` (Fact Table):**
               Central observational grain containing metrics (`average_price`, `total_volume`, `plu_4046`, `plu_4225`, `plu_4770`, `total_bags`, `small_bags`, `large_bags`, `xlarge_bags`) with Foreign Keys to dimension tables.
            2. **`dim_date` (Dimension):**
               Calendar hierarchy (`full_date`, `day`, `month`, `month_name`, `quarter`, `year`, `week_number`, `is_weekend`).
            3. **`dim_region` (Dimension):**
               54 distinct markets classified into National, Multi-State, and Metro tiers.
            4. **`dim_avocado_type` (Dimension):**
               Standardized product varieties (`conventional`, `organic`).
            5. **`dataset_metadata` (Audit Table):**
               ETL provenance tracking import dates, record counts, and source versions.
            6. **`avocado_prices` (Staging Table):**
               High-performance canonical staging table for zero-loss ingestion.
            """
        )

        st.markdown("### 💻 Technology Stack")
        st.markdown(
            """
            - **Frontend:** Streamlit 1.66, Custom CSS Design System, Responsive Components
            - **Visualization:** Plotly Express & Plotly Graph Objects (Interactive SVG/WebGL)
            - **Backend Framework:** Python 3.13, Modular Service Architecture, Pandas, NumPy
            - **Database Engine:** MySQL 8.x Enterprise, Connection Pooling, Indexed Foreign Keys
            - **AI Engine:** Ollama Local AI (`llama3.2`) with Autonomous Rule-Based Fallback
            - **Document Generation:** ReportLab 5.x PDF Rendering & Openpyxl
            """
        )

    st.markdown("---")
    st.markdown("### 📐 Entity-Relationship (ER) Architecture Diagram")
    st.markdown(
        """
        ```mermaid
        erDiagram
            DIM_DATE ||--o{ AVOCADO_OBSERVATIONS : "records on"
            DIM_REGION ||--o{ AVOCADO_OBSERVATIONS : "originates from"
            DIM_AVOCADO_TYPE ||--o{ AVOCADO_OBSERVATIONS : "categorized by"
            DATASET_METADATA ||--|| AVOCADO_PRICES : "audits"

            DIM_DATE {
                int date_id PK
                date full_date UK
                tinyint day
                tinyint month
                varchar month_name
                tinyint quarter
                smallint year
                tinyint week_number
                boolean is_weekend
            }

            DIM_REGION {
                int region_id PK
                varchar region_name UK
                varchar market_tier
                timestamp created_at
            }

            DIM_AVOCADO_TYPE {
                int type_id PK
                varchar type_name UK
                varchar description
            }

            AVOCADO_OBSERVATIONS {
                int observation_id PK
                int date_id FK
                int region_id FK
                int type_id FK
                decimal average_price
                decimal total_volume
                decimal total_bags
                decimal small_bags
                decimal large_bags
                decimal xlarge_bags
                decimal plu_4046
                decimal plu_4225
                decimal plu_4770
            }

            DATASET_METADATA {
                int dataset_id PK
                varchar dataset_name
                varchar source_url
                timestamp import_date
                int record_count
                varchar source_file
                varchar data_version
            }
        ```
        """
    )


if __name__ == "__main__":
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from components.header import render_header
    render_header()
    render_about_page()

