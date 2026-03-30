"""
KenyaPulse — Home / Overview Page

Displays six live KPI cards sourced from the World Bank API, a brief
narrative about Kenya's development trajectory, and quick-navigation
cards to the three analytical sections.
"""

import streamlit as st

from config import HOME_KPIS
from utils.api import fetch_indicator

# ---------------------------------------------------------------------------
# Page config  (must be the very first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="KenyaPulse — Kenya Intelligence Dashboard",
    page_icon="🇰🇪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
        /* ── Sidebar ── */
        section[data-testid="stSidebar"] { background-color: #f7f9f7; }

        /* ── KPI card ── */
        div[data-testid="metric-container"] {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-left: 4px solid #006600;
            border-radius: 6px;
            padding: 12px 16px;
        }
        div[data-testid="metric-container"] label {
            font-size: 0.78rem !important;
            color: #555 !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
            font-weight: 700;
            color: #1a1a1a;
        }

        /* ── Nav cards ── */
        .nav-card {
            background: #ffffff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: box-shadow 0.2s;
        }
        .nav-card:hover { box-shadow: 0 4px 12px rgba(0,102,0,0.15); }
        .nav-card h3 { color: #006600; margin-bottom: 6px; }
        .nav-card p  { color: #666; font-size: 0.9rem; margin: 0; }

        /* ── Divider accent ── */
        hr { border-top: 2px solid #006600 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.image(
        "https://flagcdn.com/w80/ke.png",
        width=80,
    )
    st.markdown("## KenyaPulse")
    st.caption(
        "Kenya Economic & Development Intelligence Dashboard  \n"
        "**Data:** World Bank Open Data API  \n"
        "**Refresh:** Hourly cache"
    )
    st.divider()
    st.markdown("**Navigate**")
    st.page_link("Home.py",                         label="🏠 Overview")
    st.page_link("pages/1_Economic_Indicators.py",  label="💹 Economic Indicators")
    st.page_link("pages/2_Social_Indicators.py",    label="👥 Social Indicators")
    st.page_link("pages/3_Regional_Comparison.py",  label="🌍 Regional Comparison")
    st.divider()
    st.caption("Built by Ian Mwendwa · Powered by [World Bank Open Data](https://data.worldbank.org/)")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <h1 style='color:#006600; margin-bottom:0'>🇰🇪 KenyaPulse</h1>
    <p style='color:#555; font-size:1.1rem; margin-top:4px'>
        Kenya Economic & Development Intelligence Dashboard
    </p>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Live indicators sourced from the **World Bank Open Data API**. "
    "Data is cached for 1 hour. All monetary values in current US dollars."
)

st.divider()

# ---------------------------------------------------------------------------
# KPI Cards  — one row of 6 metrics
# ---------------------------------------------------------------------------

st.subheader("At a Glance — Kenya Key Indicators")

_FMT = {
    "billions_usd": lambda v: f"${v / 1e9:.1f}B",
    "percent":      lambda v: f"{v:.1f}%",
    "millions":     lambda v: f"{v / 1e6:.1f}M",
    "years":        lambda v: f"{v:.1f} yrs",
}

cols = st.columns(len(HOME_KPIS))

for col, kpi in zip(cols, HOME_KPIS):
    df = fetch_indicator("KE", kpi["code"])
    if df.empty:
        col.metric(label=kpi["label"], value="N/A")
        continue

    latest = df.iloc[-1]
    prev   = df.iloc[-2] if len(df) >= 2 else None

    raw_val = float(latest["value"])
    display = _FMT[kpi["fmt"]](raw_val)

    # Compute delta for trend arrow
    delta_str = None
    delta_clr = "normal"
    if prev is not None:
        prev_val  = float(prev["value"])
        raw_delta = raw_val - prev_val
        delta_str = _FMT[kpi["fmt"]](abs(raw_delta))
        delta_str = ("+" if raw_delta >= 0 else "−") + delta_str
        # Inflation & unemployment: lower is better → invert colour
        if kpi["code"] in ("FP.CPI.TOTL.ZG", "SL.UEM.TOTL.ZS", "SH.DYN.MORT"):
            delta_clr = "inverse"

    col.metric(
        label=f"{kpi['icon']} {kpi['label']} ({int(latest['year'])})",
        value=display,
        delta=delta_str,
        delta_color=delta_clr,
    )

st.divider()

# ---------------------------------------------------------------------------
# Kenya Narrative
# ---------------------------------------------------------------------------

col_text, col_facts = st.columns([3, 2])

with col_text:
    st.subheader("Kenya's Development Story")
    st.markdown(
        """
        Kenya stands as **East Africa's largest economy** and a key tech and financial hub
        on the continent. Since 2015, GDP has grown from **USD 70.1 billion** to an estimated **USD 136 billion**,
        driven by services, manufacturing, and a thriving digital economy anchored by M-Pesa
        and a world-leading fintech ecosystem.

        The country has made significant strides in **social development**: life expectancy
        has risen steadily, internet penetration has surpassed 40%, and access to electricity
        continues to expand through off-grid and last-mile initiatives like the
        Last Mile Connectivity Project.

        However, Kenya still faces structural headwinds — elevated inflation driven by
        currency pressure, a youth unemployment rate above 10%, and urban-rural inequality
        that demands targeted policy attention.

        **This dashboard tracks Kenya's trajectory across 14 World Bank indicators,
        benchmarked against 6 regional peers, from 2000 to present.**
        """
    )

with col_facts:
    st.subheader("Quick Facts")
    facts = {
        "Capital":        "Nairobi",
        "Region":         "Sub-Saharan Africa",
        "Income Level":   "Lower Middle Income",
        "Currency":       "Kenyan Shilling (KES)",
        "Official Lang.": "Swahili, English",
        "Government":     "Presidential Republic",
        "Area":           "580,367 km²",
        "Neighbour EAC":  "TZ, UG, ET, SS, SO",
    }
    for k, v in facts.items():
        st.markdown(f"**{k}:** {v}")

st.divider()

# ---------------------------------------------------------------------------
# Navigation Cards
# ---------------------------------------------------------------------------

st.subheader("Explore the Dashboard")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        """
        <div class="nav-card">
            <h3>💹 Economic Indicators</h3>
            <p>GDP, GDP growth, inflation, trade, FDI, and per-capita income trends from 2000–present.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="nav-card">
            <h3>👥 Social Indicators</h3>
            <p>Population dynamics, life expectancy, literacy, unemployment, internet access, and electricity penetration.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class="nav-card">
            <h3>🌍 Regional Comparison</h3>
            <p>Benchmark Kenya against Tanzania, Uganda, Ethiopia, Rwanda, South Africa, and Nigeria.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption("Use the sidebar or the page navigation at the top to switch sections.")
