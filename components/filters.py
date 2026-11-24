"""Global and Page-Level Filter Components.

Provides intuitive dropdowns and selectors synchronized with MySQL metadata.
"""

from __future__ import annotations
import streamlit as st
from typing import Any, Dict, Optional, Tuple
from services.analytics_service import AnalyticsService


def render_global_filters(key_prefix: str = "global") -> Dict[str, Any]:
    """Renders a collapsible, cohesive filter bar across Year, Region, and Type."""
    options = AnalyticsService.get_filter_options()

    year_choices = ["All"] + [str(y) for y in options["years"]]
    region_choices = ["All"] + options["regions"]
    type_choices = ["All"] + [t.capitalize() for t in options["types"]]

    with st.expander("🔍 Global Filter Controls", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            selected_year = st.selectbox("Select Year", year_choices, index=0, key=f"{key_prefix}_year")
        with c2:
            selected_region = st.selectbox("Select Market / Region", region_choices, index=0, key=f"{key_prefix}_region")
        with c3:
            selected_type = st.selectbox("Avocado Type", type_choices, index=0, key=f"{key_prefix}_type")

    return {
        "year": None if selected_year == "All" else int(selected_year),
        "region": None if selected_region == "All" else selected_region,
        "type": None if selected_type == "All" else selected_type.lower(),
    }
