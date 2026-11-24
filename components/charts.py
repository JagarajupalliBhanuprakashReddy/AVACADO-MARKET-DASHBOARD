"""Plotly Visualization Engine.

Renders interactive charts styled consistently in the Forest Green & Dark Navy theme.
Provides tooltips, readable axis formatting, and responsive containers.
"""

from __future__ import annotations
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Optional

# Color Palette: Forest green, dark navy, emerald, teal, gold
THEME_COLORS = [
    "#2d6a4f",  # Forest Green
    "#1e3a8a",  # Deep Navy Blue
    "#52b788",  # Mint / Light Green
    "#0284c7",  # Sky Blue
    "#d97706",  # Amber / Gold
    "#7c3aed",  # Purple
    "#dc2626",  # Crimson
    "#059669",  # Emerald
]

BASE_LAYOUT = dict(
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", size=12, color="#1e293b"),
    plot_bgcolor="rgba(248, 250, 252, 0.6)",
    paper_bgcolor="rgba(0, 0, 0, 0)",
    margin=dict(l=40, r=30, t=50, b=40),
    hovermode="closest",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=11),
    ),
)


def create_line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: Optional[str] = None,
    title: str = "",
    x_label: str = "",
    y_label: str = "",
) -> go.Figure:
    """Generates a polished line chart with markers and hover cards."""
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        title=title,
        color_discrete_sequence=THEME_COLORS,
        markers=True,
    )
    fig.update_layout(**BASE_LAYOUT)
    fig.update_layout(
        xaxis_title=x_label or x,
        yaxis_title=y_label or y,
        title_font=dict(size=14, color="#0f172a"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
    return fig


def create_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: Optional[str] = None,
    barmode: str = "group",
    title: str = "",
    x_label: str = "",
    y_label: str = "",
) -> go.Figure:
    """Generates a vertical or grouped bar chart."""
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        barmode=barmode,
        title=title,
        color_discrete_sequence=THEME_COLORS,
    )
    fig.update_layout(**BASE_LAYOUT)
    fig.update_layout(
        xaxis_title=x_label or x,
        yaxis_title=y_label or y,
        title_font=dict(size=14, color="#0f172a"),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
    return fig


def create_horizontal_bar(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: Optional[str] = None,
    title: str = "",
    x_label: str = "",
    y_label: str = "",
) -> go.Figure:
    """Generates a horizontal ranking bar chart."""
    # Reverse so top item is at the top
    sorted_df = df.iloc[::-1] if not df.empty else df
    fig = px.bar(
        sorted_df,
        x=x,
        y=y,
        orientation="h",
        color=color,
        title=title,
        color_discrete_sequence=THEME_COLORS,
    )
    fig.update_layout(**BASE_LAYOUT)
    fig.update_layout(
        xaxis_title=x_label or x,
        yaxis_title=y_label or y,
        title_font=dict(size=14, color="#0f172a"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
    fig.update_yaxes(showgrid=False)
    return fig


def create_donut_chart(
    df: pd.DataFrame,
    names: str,
    values: str,
    title: str = "",
) -> go.Figure:
    """Generates a sleek donut chart."""
    fig = px.pie(
        df,
        names=names,
        values=values,
        title=title,
        hole=0.45,
        color_discrete_sequence=THEME_COLORS,
    )
    fig.update_layout(**BASE_LAYOUT)
    fig.update_layout(title_font=dict(size=14, color="#0f172a"))
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig


def create_stacked_bar(
    df: pd.DataFrame,
    x: str,
    y_cols: List[str],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
) -> go.Figure:
    """Generates a multi-category stacked bar chart."""
    fig = go.Figure()
    for idx, col in enumerate(y_cols):
        fig.add_trace(
            go.Bar(
                name=col,
                x=df[x],
                y=df[col],
                marker_color=THEME_COLORS[idx % len(THEME_COLORS)],
            )
        )
    fig.update_layout(barmode="stack", **BASE_LAYOUT)
    fig.update_layout(
        title=title,
        xaxis_title=x_label or x,
        yaxis_title=y_label or "Volume",
        title_font=dict(size=14, color="#0f172a"),
    )
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
    return fig


def create_heatmap(
    df: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    title: str = "",
    x_label: str = "",
    y_label: str = "",
) -> go.Figure:
    """Generates a 2D density heatmap."""
    pivot_df = df.pivot(index=y, columns=x, values=z)
    fig = px.imshow(
        pivot_df,
        labels=dict(x=x_label or x, y=y_label or y, color=z),
        title=title,
        color_continuous_scale="Viridis",
        aspect="auto",
    )
    fig.update_layout(**BASE_LAYOUT)
    fig.update_layout(title_font=dict(size=14, color="#0f172a"))
    return fig


def create_histogram(
    df: pd.DataFrame,
    x: str,
    nbins: int = 30,
    color: Optional[str] = None,
    title: str = "",
    x_label: str = "",
) -> go.Figure:
    """Generates a distribution histogram."""
    fig = px.histogram(
        df,
        x=x,
        nbins=nbins,
        color=color,
        title=title,
        color_discrete_sequence=THEME_COLORS,
        opacity=0.8,
    )
    fig.update_layout(**BASE_LAYOUT)
    fig.update_layout(
        xaxis_title=x_label or x,
        yaxis_title="Frequency Count",
        title_font=dict(size=14, color="#0f172a"),
    )
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
    return fig
