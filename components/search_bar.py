"""Prominent Historical Search Bar Component.

Renders modern search input with example query pills as specified in Section 6.1.
"""

from __future__ import annotations
import streamlit as st
from typing import Callable, Optional

EXAMPLE_QUERIES = [
    "Compare avocado prices in 2015 and 2017.",
    "Compare avocado prices in 2015 and 2020.",
    "Show average avocado prices in 2017.",
    "Which region had the highest price in 2018?",
    "Compare Organic and Conventional prices.",
    "Show monthly price trends from 2016 to 2018.",
    "Which region recorded the lowest average price?",
    "Show the historical price trend for California.",
    "Identify the year with the highest recorded average price.",
    "Compare bag volumes across regions.",
]


def render_search_bar(default_query: str = "") -> Optional[str]:
    """Renders the primary search bar with styling and quick suggestion buttons."""
    st.markdown(
        """
        <div style="text-align: center; margin: 10px 0 16px 0;">
            <h2 style="font-size: 26px; font-weight: 800; color: #1b4332; margin-bottom: 4px;">
                Search Agricultural Market Prices
            </h2>
            <p style="font-size: 14px; color: #4b5563; max-width: 650px; margin: 0 auto;">
                Explore historical avocado prices, compare previous years, and discover regional market trends.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "search_input_val" not in st.session_state:
        st.session_state.search_input_val = default_query

    c1, c2 = st.columns([5, 1])
    with c1:
        query = st.text_input(
            "Search Query",
            value=st.session_state.search_input_val,
            placeholder="Ask anything about historical avocado prices (e.g. 'Compare avocado prices in 2016 and 2017')...",
            label_visibility="collapsed",
            key="main_search_input",
        )
    with c2:
        search_clicked = st.button("Search 🔍", use_container_width=True, type="primary")

    st.markdown("<div style='font-size: 12px; font-weight: 600; color: #64748b; margin: 8px 0 6px 0;'>💡 Try an example search:</div>", unsafe_allow_html=True)

    # Render example pills in 2 rows of 5
    r1 = EXAMPLE_QUERIES[:5]
    r2 = EXAMPLE_QUERIES[5:]

    cols1 = st.columns(len(r1))
    for idx, ex in enumerate(r1):
        if cols1[idx].button(ex, key=f"ex_pill_1_{idx}", use_container_width=True):
            st.session_state.search_input_val = ex
            st.rerun()

    cols2 = st.columns(len(r2))
    for idx, ex in enumerate(r2):
        if cols2[idx].button(ex, key=f"ex_pill_2_{idx}", use_container_width=True):
            st.session_state.search_input_val = ex
            st.rerun()

    if search_clicked or query:
        return query
    return None
