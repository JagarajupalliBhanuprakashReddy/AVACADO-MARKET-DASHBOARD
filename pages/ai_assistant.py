"""AI-Powered Natural Language SQL Assistant Page.

Interfaces with local Ollama service for schema-aware SQL synthesis,
with strict read-only validation, live execution, and smart fallback.
"""

from __future__ import annotations
import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import pandas as pd
from services.ai_sql_service import AISQLService
from services.export_service import ExportService
from components.charts import (
    create_bar_chart,
    create_line_chart,
    create_donut_chart,
)


EXAMPLE_PROMPTS = [
    "Show the top five regions by volume.",
    "Which year had the highest average recorded price?",
    "Compare Organic and Conventional prices.",
    "Show the price trend for California.",
    "What is the monthly average price across all recorded years?",
    "Which regions have prices above the overall average?",
    "Compare avocado prices in 2015 and 2017.",
]


def render_ai_assistant_page():
    """Renders the AI SQL Assistant interface."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h2 style="font-size: 22px; font-weight: 700; color: #1b4332; margin-bottom: 4px;">
                AI-Powered Natural Language SQL Assistant
            </h2>
            <p style="font-size: 13px; color: #64748b; margin: 0;">
                Ask questions in plain English to synthesize, safely validate, and execute MySQL 8.x queries against agricultural datasets.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ollama_info = AISQLService.check_ollama_status()
    is_online = ollama_info["available"]

    # Status Pill
    status_bg = "#ecfdf5" if is_online else "#fffbeb"
    status_border = "#10b981" if is_online else "#f59e0b"
    status_text = "#065f46" if is_online else "#92400e"
    badge_label = f"Ollama Online ({ollama_info['host']})" if is_online else "Ollama Standby / Autonomous NL-to-SQL Fallback Active"

    st.markdown(
        f"""
        <div style="background: {status_bg}; border: 1px solid {status_border}; border-radius: 8px; padding: 12px 16px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center;">
            <div style="color: {status_text}; font-size: 13px; font-weight: 600;">
                🤖 <b>AI Engine Status:</b> {badge_label}
            </div>
            <div style="font-size: 11px; color: {status_text};">
                Model: <code>{ollama_info['default_model']}</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not is_online:
        with st.expander("ℹ️ How to launch Ollama locally (Optional)", expanded=False):
            st.markdown(
                """
                To connect the full local LLM:
                1. Open a terminal and run: `ollama serve`
                2. In another terminal, pull the model: `ollama run llama3.2`
                3. The application will immediately switch from autonomous fallback to local LLM synthesis!
                """
            )

    # Prompt input
    st.markdown("##### 💬 Enter Your Natural Language Question")

    if "ai_prompt_val" not in st.session_state:
        st.session_state.ai_prompt_val = "Show the top five regions by volume."

    user_prompt = st.text_input(
        "Ask a question about avocado market prices or volumes",
        value=st.session_state.ai_prompt_val,
        key="ai_input_text"
    )

    # Quick example pills
    st.markdown("<div style='font-size: 12px; color: #64748b; margin: 4px 0 8px 0;'>Quick suggestions:</div>", unsafe_allow_html=True)
    pill_cols = st.columns(len(EXAMPLE_PROMPTS[:4]))
    for idx, p_text in enumerate(EXAMPLE_PROMPTS[:4]):
        if pill_cols[idx].button(p_text, key=f"ai_p_{idx}", use_container_width=True):
            st.session_state.ai_prompt_val = p_text
            st.rerun()

    btn_exec = st.button("Generate & Execute SQL 🚀", type="primary", key="btn_run_ai")

    if btn_exec or user_prompt:
        with st.spinner("Translating natural language to validated SQL & executing on MySQL..."):
            ai_res = AISQLService.process_natural_language_query(user_prompt)

        if not ai_res.get("success"):
            st.error(f"❌ {ai_res.get('error')}")
            if "attempted_sql" in ai_res:
                st.code(ai_res["attempted_sql"], language="sql")
        else:
            if ai_res.get("coverage_warning"):
                st.warning(f"⚠️ {ai_res['explanation']}")
            else:
                st.success(f"Query processed via: **{ai_res['source']}**")

                c_m1, c_m2 = st.columns([3, 1])
                with c_m1:
                    st.markdown(f"**Insight:** {ai_res['explanation']}")
                with c_m2:
                    st.metric("Records Found", f"{ai_res['row_count']:,}")

                # Display SQL
                with st.expander("📄 Generated & Verified MySQL 8.x Query", expanded=True):
                    st.code(ai_res["sql"], language="sql")

                df: pd.DataFrame = ai_res.get("df", pd.DataFrame())
                if not df.empty:
                    # Dynamic Chart Recommendation
                    chart_type = ai_res.get("chart_type", "bar")
                    if chart_type == "line" and ("price_date" in df.columns or "week_start_date" in df.columns):
                        date_c = "price_date" if "price_date" in df.columns else "week_start_date"
                        val_c = [c for c in df.select_dtypes(include=["number"]).columns][0]
                        fig = create_line_chart(df, x=date_c, y=val_c, title=f"{val_c.replace('_', ' ').title()} Over Time")
                        st.plotly_chart(fig, use_container_width=True)

                    elif chart_type == "bar":
                        cat_c = df.columns[0]
                        num_c = df.select_dtypes(include=["number"]).columns
                        val_c = num_c[0] if len(num_c) > 0 else df.columns[1]
                        fig = create_bar_chart(df, x=cat_c, y=val_c, title=f"{val_c.replace('_', ' ').title()} by {cat_c.replace('_', ' ').title()}")
                        st.plotly_chart(fig, use_container_width=True)

                    # Table Display
                    st.markdown("##### 📊 Query Results Table")
                    st.dataframe(df, use_container_width=True)

                    # Export
                    csv_b = ExportService.dataframe_to_csv(df)
                    st.download_button(
                        "📥 Download Query Results (CSV)",
                        data=csv_b,
                        file_name="ai_query_results.csv",
                        mime="text/csv",
                    )


if __name__ == "__main__":
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from components.header import render_header
    render_header()
    render_ai_assistant_page()

