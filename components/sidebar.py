"""Sidebar Navigation Component.

Provides clean enterprise navigation between all 12 modules of the application.
"""

from __future__ import annotations
import streamlit as st


PAGES = [
    ("📊 Overview Dashboard", "Overview Dashboard"),
    ("🔍 Historical Price Search", "Historical Price Search"),
    ("📈 Market Price Analytics", "Market Price Analytics"),
    ("🗺️ Regional Market Analysis", "Regional Market Analysis"),
    ("🥑 Product Type Analysis", "Product Type Analysis"),
    ("📦 Volume & Demand Analysis", "Volume & Demand Analysis"),
    ("📑 Ten SQL Reports", "Ten SQL Reports"),
    ("🔬 Interactive Data Explorer", "Interactive Data Explorer"),
    ("🗄️ Database Management", "Database Management"),
    ("📥 Dataset Import & Export", "Dataset Import & Export"),
    ("🤖 AI SQL Assistant", "AI SQL Assistant"),
    ("ℹ️ About Project", "About Project"),
]


def render_sidebar() -> str:
    """Renders sidebar branding and navigation, returns selected page name."""
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; padding: 12px 0 20px 0;">
                <div style="font-size: 38px; line-height: 1;">🌱</div>
                <h3 style="margin: 8px 0 2px 0; font-size: 17px; font-weight: 700; color: #1b4332;">AGRI-MARKET IQ</h3>
                <p style="margin: 0; font-size: 11px; color: #64748b; letter-spacing: 0.5px;">PRICE & SALES INTELLIGENCE</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        labels = [p[0] for p in PAGES]
        keys = [p[1] for p in PAGES]

        if "current_page" not in st.session_state:
            st.session_state.current_page = "Overview Dashboard"

        # Determine current index
        try:
            curr_index = keys.index(st.session_state.current_page)
        except ValueError:
            curr_index = 0

        selected_label = st.radio(
            "Navigation Menu",
            labels,
            index=curr_index,
            label_visibility="collapsed",
        )

        selected_page = keys[labels.index(selected_label)]
        st.session_state.current_page = selected_page

        st.markdown("---")

        st.markdown(
            """
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; font-size: 11px; color: #475569;">
                <div style="font-weight: 700; color: #1e293b; margin-bottom: 4px;">AGRI-MARKET IQ</div>
                <div>&bull; Agricultural Intelligence Suite</div>
                <div>&bull; Historical Market Analytics</div>
                <div style="margin-top: 8px; font-size: 10px; color: #94a3b8; border-top: 1px dashed #cbd5e1; padding-top: 6px;">
                    MySQL 8.x &bull; Streamlit &bull; Plotly
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state.current_page
