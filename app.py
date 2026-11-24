"""Agricultural Market Pricing & Sales Dashboard.

Enterprise Database-Driven Market Intelligence & Pricing Analytics Platform
"""

from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Page configuration
st.set_page_config(
    page_title="Agricultural Market Pricing & Sales Dashboard",
    page_icon="🥑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Enterprise CSS Design System (Forest Green & Dark Navy Palette)
st.markdown(
    """
    <style>
        /* Modern Font and Clean Backgrounds */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .main {
            background-color: #f8fafc;
        }
        
        /* Metric Card styling */
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        
        div[data-testid="stMetricLabel"] {
            font-size: 11px;
            text-transform: uppercase;
            font-weight: 600;
            color: #64748b;
        }
        
        div[data-testid="stMetricValue"] {
            font-size: 20px;
            font-weight: 700;
            color: #1b4332;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 44px;
            border-radius: 6px 6px 0 0;
            font-weight: 600;
            color: #475569;
            background-color: transparent;
            padding: 0 16px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #ffffff;
            color: #1b4332 !important;
            border-bottom: 3px solid #2d6a4f !important;
        }
        
        /* Primary button styling */
        button[kind="primary"] {
            background-color: #1b4332 !important;
            border-color: #1b4332 !important;
            color: white !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
        }
        button[kind="primary"]:hover {
            background-color: #2d6a4f !important;
            border-color: #2d6a4f !important;
        }

        /* Clean table headers */
        div[data-testid="stDataFrame"] {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Expander headers */
        .streamlit-expanderHeader {
            font-weight: 600;
            color: #1e293b;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

from components.header import render_header
from pages.overview import render_overview_page
from pages.historical_search import render_historical_search_page
from pages.market_analytics import render_market_analytics_page
from pages.regional_analysis import render_regional_analysis_page
from pages.product_analysis import render_product_analysis_page
from pages.volume_analysis import render_volume_analysis_page
from pages.sql_reports import render_sql_reports_page
from pages.data_explorer import render_data_explorer_page
from pages.database_management import render_database_management_page
from pages.dataset_management import render_dataset_management_page
from pages.ai_assistant import render_ai_assistant_page
from pages.about import render_about_page


# Page action wrappers that ensure the application header is always rendered
def p_overview():
    render_header()
    render_overview_page()


def p_historical_search():
    render_header()
    render_historical_search_page()


def p_market_analytics():
    render_header()
    render_market_analytics_page()


def p_regional_analysis():
    render_header()
    render_regional_analysis_page()


def p_product_analysis():
    render_header()
    render_product_analysis_page()


def p_volume_analysis():
    render_header()
    render_volume_analysis_page()


def p_sql_reports():
    render_header()
    render_sql_reports_page()


def p_data_explorer():
    render_header()
    render_data_explorer_page()


def p_database_management():
    render_header()
    render_database_management_page()


def p_dataset_management():
    render_header()
    render_dataset_management_page()


def p_ai_assistant():
    render_header()
    render_ai_assistant_page()


def p_about():
    render_header()
    render_about_page()


# Multi-Page Navigation Configuration with Categories and Icons
pages_config = {
    "Market Intelligence": [
        st.Page(p_overview, title="Overview Dashboard", icon="📊", default=True),
        st.Page(p_historical_search, title="Historical Price Search", icon="🔍"),
        st.Page(p_market_analytics, title="Market Price Analytics", icon="📈"),
        st.Page(p_regional_analysis, title="Regional Market Analysis", icon="🗺️"),
        st.Page(p_product_analysis, title="Product Type Analysis", icon="🥑"),
        st.Page(p_volume_analysis, title="Volume & Demand Analysis", icon="📦"),
    ],
    "Analytics & Reports": [
        st.Page(p_sql_reports, title="Ten SQL Reports", icon="📑"),
        st.Page(p_data_explorer, title="Interactive Data Explorer", icon="🔬"),
    ],
    "System & Administration": [
        st.Page(p_database_management, title="Database Management", icon="🗄️"),
        st.Page(p_dataset_management, title="Dataset Import & Export", icon="📥"),
        st.Page(p_ai_assistant, title="AI SQL Assistant", icon="🤖"),
        st.Page(p_about, title="About Project", icon="ℹ️"),
    ],
}

pg = st.navigation(pages_config)

# Sidebar System Metadata Card
with st.sidebar:
    st.markdown(
        """
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; font-size: 11px; color: #475569; margin-top: 20px;">
            <div style="font-weight: 700; color: #1e293b; margin-bottom: 4px;">AGRI-MARKET IQ</div>
            <div>&bull; Market Intelligence Suite</div>
            <div>&bull; Real-time Historical Analytics</div>
            <div style="margin-top: 8px; font-size: 10px; color: #94a3b8; border-top: 1px dashed #cbd5e1; padding-top: 6px;">
                MySQL 8.x &bull; Streamlit &bull; Plotly
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Execute the active page
pg.run()
