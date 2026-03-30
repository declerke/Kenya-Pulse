"""
KenyaPulse — Regional Comparison Page

Benchmarks Kenya against 6 African peers across economic and social
indicators. Includes a radar / spider chart for multi-dimensional scoring,
ranked horizontal bar charts, and time-series multi-line comparisons.
"""

import streamlit as st

from config import COMPARISON_COUNTRIES, RADAR_INDICATORS
from utils.api import fetch_latest_snapshot, fetch_multi_country
from utils.charts import (
    horizontal_bar,
    multi_line_chart,
    normalise_for_radar,
    radar_chart,
)

st.set_page_config(
    page_title="Regional Comparison — KenyaPulse",
    page_icon="🌍",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 🌍 Regional Comparison")
    st.caption("Benchmark Kenya against African peers.")
    st.divider()

    selected_countries = st.multiselect(
        "Countries to compare",
        options=list(COMPARISON_COUNTRIES.keys()),
        default=list(COMPARISON_COUNTRIES.keys()),
        key="region_countries",
    )
    if "Kenya" not in selected_countries:
        selected_countries.insert(0, "Kenya")
        st.warning("Kenya is always included.")

    year_range = st.slider(
        "Trend year range",
        min_value=2000,
        max_value=2024,
        value=(2010, 2024),
        key="region_years",
    )

    compare_indicator = st.selectbox(
        "Time-series indicator",
        options=[
            "GDP Per Capita (US$)",
            "GDP Growth Rate (%)",
            "Life Expectancy at Birth (years)",
            "Internet Users (% of population)",
            "Access to Electricity (%)",
            "Inflation, CPI (%)",
            "Unemployment Rate (%)",
        ],
        index=0,
        key="region_indicator",
    )

    INDICATOR_MAP = {
        "GDP Per Capita (US$)":               "NY.GDP.PCAP.CD",
        "GDP Growth Rate (%)":                "NY.GDP.MKTP.KD.ZG",
        "Life Expectancy at Birth (years)":   "SP.DYN.LE00.IN",
        "Internet Users (% of population)":   "IT.NET.USER.ZS",
        "Access to Electricity (%)":          "EG.ELC.ACCS.ZS",
        "Inflation, CPI (%)":                 "FP.CPI.TOTL.ZG",
        "Unemployment Rate (%)":              "SL.UEM.TOTL.ZS",
    }

    st.divider()
    st.page_link("Home.py",                         label="🏠 Overview")
    st.page_link("pages/1_Economic_Indicators.py",  label="💹 Economic Indicators")
    st.page_link("pages/2_Social_Indicators.py",    label="👥 Social Indicators")

# ---------------------------------------------------------------------------
# Resolve selected country codes
# ---------------------------------------------------------------------------

sel_codes = [COMPARISON_COUNTRIES[c] for c in selected_countries]

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown("# 🌍 Regional Comparison")
st.caption(
    f"Benchmarking Kenya vs {', '.join([c for c in selected_countries if c != 'Kenya'])} · "
    "Source: World Bank Open Data"
)
st.divider()

# ---------------------------------------------------------------------------
# Section 1 — Radar Chart (multi-indicator snapshot)
# ---------------------------------------------------------------------------

st.subheader("Multi-Indicator Performance Snapshot")
st.caption(
    "Each axis is normalised to [0, 1] across all selected countries so indicators "
    "with different units are comparable. Higher = better on all axes."
)

with st.spinner("Building radar chart..."):
    raw_scores: dict[str, dict[str, float | None]] = {c: {} for c in selected_countries}

    for ind_label, ind_code in RADAR_INDICATORS.items():
        df_snap = fetch_latest_snapshot(ind_code, sel_codes)
        if df_snap.empty:
            continue
        for _, row in df_snap.iterrows():
            country_name = row["country"]
            # Resolve the country name as returned by World Bank → match our list
            match = next(
                (n for n in selected_countries if n.lower() in country_name.lower()
                 or country_name.lower() in n.lower()),
                None,
            )
            if match:
                raw_scores[match][ind_label] = row["value"]

    if any(raw_scores.values()):
        normalised = normalise_for_radar(raw_scores)
        fig_radar  = radar_chart(normalised, title="Country Performance Radar (Normalised)")
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Radar data could not be loaded. Check your internet connection.")

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Multi-line trend
# ---------------------------------------------------------------------------

st.subheader(f"Trend Comparison: {compare_indicator}")

ind_code = INDICATOR_MAP[compare_indicator]
df_trend = fetch_multi_country(ind_code, sel_codes, most_recent=30)

if not df_trend.empty:
    df_trend = df_trend[
        (df_trend["year"] >= year_range[0]) & (df_trend["year"] <= year_range[1])
    ]
    # Normalise country name display
    fig_line = multi_line_chart(
        df_trend,
        title=f"{compare_indicator} — {year_range[0]}–{year_range[1]}",
        y_label=compare_indicator,
    )
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("Trend data currently unavailable for the selected indicator.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Ranked bar: GDP per capita
# ---------------------------------------------------------------------------

st.subheader("Ranked Comparison — GDP Per Capita (Latest Available)")

col_a, col_b = st.columns(2)

with col_a:
    df_gdp_snap = fetch_latest_snapshot("NY.GDP.PCAP.CD", sel_codes)
    if not df_gdp_snap.empty:
        fig_hbar = horizontal_bar(
            df_gdp_snap,
            title="GDP Per Capita (Current US$)",
            x_label="US$ per Person",
            highlight_country="Kenya",
        )
        st.plotly_chart(fig_hbar, use_container_width=True)
    else:
        st.info("GDP per capita snapshot unavailable.")

with col_b:
    df_le_snap = fetch_latest_snapshot("SP.DYN.LE00.IN", sel_codes)
    if not df_le_snap.empty:
        fig_le = horizontal_bar(
            df_le_snap,
            title="Life Expectancy at Birth (years)",
            x_label="Years",
            highlight_country="Kenya",
        )
        st.plotly_chart(fig_le, use_container_width=True)
    else:
        st.info("Life expectancy snapshot unavailable.")

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Internet + Electricity snapshot
# ---------------------------------------------------------------------------

st.subheader("Digital & Infrastructure Access — Latest Snapshot")

col_c, col_d = st.columns(2)

with col_c:
    df_net_snap = fetch_latest_snapshot("IT.NET.USER.ZS", sel_codes)
    if not df_net_snap.empty:
        fig_net = horizontal_bar(
            df_net_snap,
            title="Internet Users (% of Population)",
            x_label="Internet Users (%)",
            highlight_country="Kenya",
        )
        st.plotly_chart(fig_net, use_container_width=True)
    else:
        st.info("Internet access snapshot unavailable.")

with col_d:
    df_elec_snap = fetch_latest_snapshot("EG.ELC.ACCS.ZS", sel_codes)
    if not df_elec_snap.empty:
        fig_elec = horizontal_bar(
            df_elec_snap,
            title="Access to Electricity (% of Population)",
            x_label="Electricity Access (%)",
            highlight_country="Kenya",
        )
        st.plotly_chart(fig_elec, use_container_width=True)
    else:
        st.info("Electricity access snapshot unavailable.")

st.divider()

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

st.subheader("Regional Intelligence Summary")
st.info(
    "**Kenya's position in the East African context:**\n\n"
    "- **GDP Per Capita:** Kenya leads the EAC bloc (excluding South Africa in broader comparison), "
    "reflecting services and fintech maturity.\n"
    "- **Internet Access:** Kenya's mobile-first internet penetration is among the highest in "
    "Sub-Saharan Africa, underpinned by the world's most advanced M-Pesa ecosystem.\n"
    "- **Life Expectancy:** Mid-tier relative to peers; Rwanda's post-1994 recovery has been "
    "exceptional and now rivals Kenya on health outcomes.\n"
    "- **Electricity:** Kenya trails South Africa significantly but leads Uganda and Ethiopia, "
    "with rapid rural electrification ongoing.\n\n"
    "Kenya's strongest comparative advantage is its **digital economy infrastructure** — a "
    "differentiator that is widening relative to EAC peers."
)
