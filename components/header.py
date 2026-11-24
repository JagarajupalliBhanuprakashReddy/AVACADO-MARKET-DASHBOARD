"""Application Header Component.

Displays enterprise title, system status, database connectivity,
record counts, and system telemetry.
"""

from __future__ import annotations
import streamlit as st
from datetime import datetime
from database.connection import check_connection_health, execute_scalar


def render_header():
    """Renders the top application header with live database status pills."""
    health = check_connection_health()

    try:
        record_count = execute_scalar("SELECT COUNT(*) FROM avocado_observations") or 0
    except Exception:
        record_count = 0

    status_color = "#10b981" if health["ok"] else "#ef4444"
    status_text = "CONNECTED" if health["ok"] else "DISCONNECTED"
    latency = f"{health['latency_ms']} ms" if health["ok"] else "N/A"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); 
                    border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; 
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15); color: white;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 26px;">🥑</span>
                        <h1 style="margin: 0; font-size: 24px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px;">
                            Agricultural Market Pricing & Sales Dashboard
                        </h1>
                    </div>
                    <div style="margin-top: 6px; font-size: 13px; color: #a0aec0; display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                        <span style="background: rgba(45, 106, 79, 0.5); padding: 3px 10px; border-radius: 20px; color: #d8f3dc; font-weight: 600; font-size: 11px;">
                            ENTERPRISE EDITION
                        </span>
                        <span><b>System:</b> Commodity Pricing & Supply Analytics Suite</span>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                    <div style="background: rgba(255, 255, 255, 0.08); padding: 8px 14px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.12); text-align: right;">
                        <div style="font-size: 10px; color: #cbd5e1; text-transform: uppercase; font-weight: 600;">MySQL Database</div>
                        <div style="font-size: 12px; font-weight: 600; color: {status_color}; display: flex; align-items: center; justify-content: flex-end; gap: 5px;">
                            <span style="height: 8px; width: 8px; background-color: {status_color}; border-radius: 50%; display: inline-block;"></span>
                            {status_text} ({latency})
                        </div>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.08); padding: 8px 14px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.12); text-align: right;">
                        <div style="font-size: 10px; color: #cbd5e1; text-transform: uppercase; font-weight: 600;">Verified Dataset</div>
                        <div style="font-size: 12px; font-weight: 600; color: #6ee7b7;">
                            {record_count:,} Observations
                        </div>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.08); padding: 8px 14px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.12); text-align: right;">
                        <div style="font-size: 10px; color: #cbd5e1; text-transform: uppercase; font-weight: 600;">Last Refreshed</div>
                        <div style="font-size: 12px; font-weight: 600; color: #e2e8f0;">
                            {current_time}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
