"""KPI Cards Component.

Renders high-impact metric cards with icons, deltas, and consistent enterprise styling.
"""

from __future__ import annotations
import streamlit as st
from typing import Any, Dict, List, Optional


def render_kpi_card(
    title: str,
    value: str,
    subtitle: Optional[str] = None,
    icon: str = "📊",
    color: str = "#1b4332",
    badge: Optional[str] = None,
):
    """Renders a single responsive KPI card."""
    badge_html = (
        f'<span style="background: rgba(255,255,255,0.25); font-size: 10px; padding: 2px 6px; border-radius: 10px; font-weight: 600;">{badge}</span>'
        if badge else ""
    )
    subtitle_html = (
        f'<div style="font-size: 11px; opacity: 0.85; margin-top: 4px;">{subtitle}</div>'
        if subtitle else ""
    )

    st.markdown(
        f"""
        <div style="background: {color}; color: white; border-radius: 10px; padding: 16px 18px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: transform 0.2s ease; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9;">
                    {title}
                </div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    {badge_html}
                    <span style="font-size: 20px;">{icon}</span>
                </div>
            </div>
            <div style="font-size: 24px; font-weight: 700; margin-top: 8px; letter-spacing: -0.5px;">
                {value}
            </div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview_kpis(kpis: Dict[str, Any]):
    """Renders the 8 mandatory global KPI cards specified in Section 5."""
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_kpi_card(
            title="Total Records",
            value=f"{kpis.get('total_records', 0):,}",
            subtitle="Verified observations in MySQL",
            icon="🗄️",
            color="linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%)",
            badge="100% Valid"
        )
    with c2:
        render_kpi_card(
            title="Overall Avg Price",
            value=f"${kpis.get('overall_avg_price', 0.0):.2f}",
            subtitle="Unweighted retail observation mean",
            icon="💲",
            color="linear-gradient(135deg, #0f2027 0%, #203a43 100%)",
            badge="USD / Unit"
        )
    with c3:
        tot_vol = kpis.get("total_volume", 0.0)
        vol_str = f"{tot_vol/1e9:.2f}B" if tot_vol >= 1e9 else f"{tot_vol/1e6:.1f}M"
        render_kpi_card(
            title="Total Recorded Volume",
            value=vol_str,
            subtitle="Cumulative units tracked",
            icon="📦",
            color="linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)",
            badge="HAB Tracked"
        )
    with c4:
        render_kpi_card(
            title="Covered Regions",
            value=f"{kpis.get('num_regions', 0)} Markets",
            subtitle="Metro, regional & national tiers",
            icon="🗺️",
            color="linear-gradient(135deg, #312e81 0%, #4f46e5 100%)",
            badge="US Coverage"
        )

    c5, c6, c7, c8 = st.columns(4)

    with c5:
        render_kpi_card(
            title="Avocado Types",
            value=f"{kpis.get('num_types', 0)} Varieties",
            subtitle="Organic & Conventional",
            icon="🥑",
            color="linear-gradient(135deg, #064e3b 0%, #059669 100%)",
            badge="Categorized"
        )
    with c6:
        render_kpi_card(
            title="Earliest Date",
            value=str(kpis.get("min_date", "N/A")),
            subtitle="First recorded week",
            icon="📅",
            color="linear-gradient(135deg, #134e4a 0%, #0d9488 100%)",
            badge="Historical Base"
        )
    with c7:
        render_kpi_card(
            title="Latest Date",
            value=str(kpis.get("max_date", "N/A")),
            subtitle="Most recent observation",
            icon="🕒",
            color="linear-gradient(135deg, #1f2937 0%, #374151 100%)",
            badge="Archive End"
        )
    with c8:
        render_kpi_card(
            title="Highest Avg Price",
            value=f"${kpis.get('highest_price', 0.0):.2f}",
            subtitle=f"Lowest: ${kpis.get('lowest_price', 0.0):.2f}",
            icon="📈",
            color="linear-gradient(135deg, #7c2d12 0%, #ea580c 100%)",
            badge="Peak Spike"
        )
