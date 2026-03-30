"""
Reusable Plotly chart builders for KenyaPulse.

All functions return a plotly.graph_objects.Figure that can be passed
directly to st.plotly_chart().
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import CHART_PALETTE, GRID_CLR, KENYA_GREEN, PLOT_BG


# ---------------------------------------------------------------------------
# Shared layout helper
# ---------------------------------------------------------------------------

def _base_layout(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#1A1A1A"), x=0),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PLOT_BG,
        font=dict(family="Arial, sans-serif", color="#444"),
        margin=dict(l=40, r=20, t=50, b=40),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID_CLR, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID_CLR, zeroline=False)
    return fig


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _to_rgba(color: str, alpha: float = 0.08) -> str:
    """Convert any supported color string to rgba() for fillcolor."""
    if color.startswith("rgb"):
        return color.replace(")", f", {alpha})").replace("rgb(", "rgba(")
    hex_c = color.lstrip("#")
    r, g, b = int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


# ---------------------------------------------------------------------------
# Single-country time series
# ---------------------------------------------------------------------------

def line_chart(
    df: pd.DataFrame,
    title: str,
    y_label: str,
    color: str = KENYA_GREEN,
    fill: bool = True,
) -> go.Figure:
    """Area/line chart for a single-country time series."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["value"],
            mode="lines+markers",
            name=y_label,
            line=dict(color=color, width=2.5),
            marker=dict(size=5, color=color),
            fill="tozeroy" if fill else "none",
            fillcolor=_to_rgba(color),
            hovertemplate=f"<b>%{{x}}</b><br>{y_label}: %{{y:,.2f}}<extra></extra>",
        )
    )
    fig.update_yaxes(title_text=y_label)
    fig.update_xaxes(title_text="Year", dtick=2)
    return _base_layout(fig, title)


def bar_chart(
    df: pd.DataFrame,
    title: str,
    y_label: str,
    color: str = KENYA_GREEN,
    show_negative_red: bool = False,
) -> go.Figure:
    """Vertical bar chart for annual comparisons."""
    if show_negative_red:
        bar_colors = [KENYA_GREEN if v >= 0 else "#BB0000" for v in df["value"]]
    else:
        bar_colors = color

    fig = go.Figure(
        go.Bar(
            x=df["year"],
            y=df["value"],
            marker_color=bar_colors,
            hovertemplate=f"<b>%{{x}}</b><br>{y_label}: %{{y:,.2f}}<extra></extra>",
        )
    )
    fig.update_yaxes(title_text=y_label)
    fig.update_xaxes(title_text="Year", dtick=2)
    return _base_layout(fig, title)


# ---------------------------------------------------------------------------
# Multi-country charts
# ---------------------------------------------------------------------------

def multi_line_chart(
    df: pd.DataFrame,
    title: str,
    y_label: str,
) -> go.Figure:
    """Multi-line chart for regional comparisons over time."""
    fig = px.line(
        df,
        x="year",
        y="value",
        color="country",
        markers=True,
        color_discrete_sequence=CHART_PALETTE,
        hover_data={"year": True, "value": ":.2f", "country": True},
    )
    fig.update_traces(line_width=2, marker_size=5)
    fig.update_yaxes(title_text=y_label)
    fig.update_xaxes(title_text="Year", dtick=2)
    fig.update_layout(legend_title_text="Country")
    return _base_layout(fig, title)


def horizontal_bar(
    df: pd.DataFrame,
    title: str,
    x_label: str,
    highlight_country: str = "Kenya",
) -> go.Figure:
    """Ranked horizontal bar chart with Kenya highlighted."""
    df_s = df.sort_values("value", ascending=True).copy()
    colors = [
        KENYA_GREEN if c == highlight_country else "#90CAF9"
        for c in df_s["country"]
    ]
    fig = go.Figure(
        go.Bar(
            x=df_s["value"],
            y=df_s["country"],
            orientation="h",
            marker_color=colors,
            hovertemplate=f"<b>%{{y}}</b><br>{x_label}: %{{x:,.2f}}<extra></extra>",
        )
    )
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(title_text="")
    return _base_layout(fig, title)


def radar_chart(
    scores: dict[str, dict[str, float]],
    title: str,
) -> go.Figure:
    """
    Radar / spider chart comparing countries across normalised indicators.

    `scores` format: { "Kenya": {"Indicator A": 0.8, "Indicator B": 0.6, ...}, ... }
    """
    categories = list(next(iter(scores.values())).keys())
    categories_closed = categories + [categories[0]]  # close the polygon

    fig = go.Figure()
    for idx, (country, vals) in enumerate(scores.items()):
        values = [vals.get(c, 0) for c in categories]
        values_closed = values + [values[0]]
        fig.add_trace(
            go.Scatterpolar(
                r=values_closed,
                theta=categories_closed,
                fill="toself",
                name=country,
                line=dict(color=CHART_PALETTE[idx % len(CHART_PALETTE)], width=2),
                fillcolor=CHART_PALETTE[idx % len(CHART_PALETTE)],
                opacity=0.25 if country != "Kenya" else 0.40,
                hovertemplate=f"<b>{country}</b><br>%{{theta}}: %{{r:.2f}}<extra></extra>",
            )
        )
    fig.update_layout(
        title=dict(text=title, font=dict(size=16), x=0),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], tickformat=".0%"),
            angularaxis=dict(tickfont=dict(size=11)),
        ),
        paper_bgcolor=PLOT_BG,
        font=dict(family="Arial, sans-serif", color="#444"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
    )
    return fig


def donut_chart(
    labels: list[str],
    values: list[float],
    title: str,
    colors: list[str] | None = None,
) -> go.Figure:
    """Simple donut chart."""
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker_colors=colors or [KENYA_GREEN, "#90CAF9"],
            hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
            textinfo="label+percent",
        )
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=16), x=0),
        paper_bgcolor=PLOT_BG,
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#444"),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


# ---------------------------------------------------------------------------
# Normalisation utility for radar chart
# ---------------------------------------------------------------------------

def normalise_for_radar(
    raw: dict[str, dict[str, float | None]],
) -> dict[str, dict[str, float]]:
    """
    Min-max normalise values per indicator across all countries so all axes
    share a [0, 1] range on the radar chart.

    `raw` format: { "Kenya": {"GDP Per Capita": 2100, ...}, "Tanzania": {...}, ... }
    """
    indicators = list(next(iter(raw.values())).keys())
    result: dict[str, dict[str, float]] = {c: {} for c in raw}

    for ind in indicators:
        vals = {c: raw[c].get(ind) for c in raw if raw[c].get(ind) is not None}
        if not vals:
            for c in raw:
                result[c][ind] = 0.0
            continue
        mn, mx = min(vals.values()), max(vals.values())
        rng = mx - mn if mx != mn else 1.0
        for c in raw:
            v = raw[c].get(ind)
            result[c][ind] = float((v - mn) / rng) if v is not None else 0.0

    return result
