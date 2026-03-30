"""
KenyaPulse — Economic Indicators Page

Interactive time-series analysis of Kenya's macroeconomic performance:
GDP, growth rate, per-capita income, inflation, trade, and FDI.
"""

import streamlit as st

from config import ECONOMIC_INDICATORS
from utils.api import fetch_indicator
from utils.charts import bar_chart, line_chart

st.set_page_config(
    page_title="Economic Indicators — KenyaPulse",
    page_icon="💹",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 💹 Economic Indicators")
    st.caption("Adjust filters to customise the charts below.")
    st.divider()
    year_range = st.slider(
        "Year range",
        min_value=2000,
        max_value=2024,
        value=(2005, 2024),
        step=1,
        key="econ_year_range",
    )
    st.divider()
    st.page_link("Home.py",                         label="🏠 Overview")
    st.page_link("pages/2_Social_Indicators.py",    label="👥 Social Indicators")
    st.page_link("pages/3_Regional_Comparison.py",  label="🌍 Regional Comparison")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown("# 💹 Economic Indicators")
st.caption(
    f"Kenya macroeconomic performance · {year_range[0]}–{year_range[1]} · "
    "Source: World Bank Open Data"
)
st.divider()

# ---------------------------------------------------------------------------
# Helper: filtered fetch
# ---------------------------------------------------------------------------

def load(code: str) -> "pd.DataFrame":  # noqa: F821
    import pandas as pd
    df = fetch_indicator("KE", code)
    if df.empty:
        return df
    return df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])].copy()


# ---------------------------------------------------------------------------
# Row 1 — GDP absolute + GDP growth
# ---------------------------------------------------------------------------

st.subheader("Gross Domestic Product")

col1, col2 = st.columns(2)

with col1:
    df_gdp = load("NY.GDP.MKTP.CD")
    if not df_gdp.empty:
        df_gdp["value"] = df_gdp["value"] / 1e9  # convert to billions
        fig = line_chart(
            df_gdp,
            title="GDP — Current US$ (Billions)",
            y_label="GDP (US$ Billions)",
            color="#006600",
        )
        st.plotly_chart(fig, use_container_width=True)

        latest = df_gdp.iloc[-1]
        st.caption(
            f"**Latest ({int(latest['year'])}):** ${latest['value']:.1f}B — "
            "Kenya is East Africa's largest economy."
        )
    else:
        st.info("GDP data currently unavailable.")

with col2:
    df_growth = load("NY.GDP.MKTP.KD.ZG")
    if not df_growth.empty:
        fig = bar_chart(
            df_growth,
            title="GDP Growth Rate (Annual %)",
            y_label="Growth Rate (%)",
            show_negative_red=True,
        )
        st.plotly_chart(fig, use_container_width=True)

        avg = df_growth["value"].mean()
        st.caption(
            f"**Average growth ({year_range[0]}–{year_range[1]}):** {avg:.1f}% — "
            "Bars in red indicate contraction years."
        )
    else:
        st.info("GDP growth data currently unavailable.")

st.divider()

# ---------------------------------------------------------------------------
# Row 2 — GDP Per Capita + Inflation
# ---------------------------------------------------------------------------

st.subheader("Per Capita Income & Inflation")

col3, col4 = st.columns(2)

with col3:
    df_pcap = load("NY.GDP.PCAP.CD")
    if not df_pcap.empty:
        fig = line_chart(
            df_pcap,
            title="GDP Per Capita (Current US$)",
            y_label="US$ per Person",
            color="#1B5E20",
        )
        st.plotly_chart(fig, use_container_width=True)

        latest = df_pcap.iloc[-1]
        st.caption(
            f"**Latest ({int(latest['year'])}):** ${latest['value']:,.0f} per person"
        )
    else:
        st.info("GDP per capita data currently unavailable.")

with col4:
    df_inf = load("FP.CPI.TOTL.ZG")
    if not df_inf.empty:
        fig = bar_chart(
            df_inf,
            title="Inflation Rate — Consumer Price Index (Annual %)",
            y_label="Inflation (%)",
            color="#BB0000",
            show_negative_red=False,
        )
        # Override bar colour: use a red scale for inflation
        fig.update_traces(
            marker_color=[
                "#FF8A65" if v < 5 else "#EF5350" if v < 10 else "#B71C1C"
                for v in df_inf["value"]
            ]
        )
        st.plotly_chart(fig, use_container_width=True)

        latest = df_inf.iloc[-1]
        flag = "⚠️ Elevated" if latest["value"] > 7 else "✅ Moderate"
        st.caption(
            f"**Latest ({int(latest['year'])}):** {latest['value']:.1f}% — {flag}"
        )
    else:
        st.info("Inflation data currently unavailable.")

st.divider()

# ---------------------------------------------------------------------------
# Row 3 — Trade + FDI
# ---------------------------------------------------------------------------

st.subheader("Trade & Foreign Investment")

col5, col6 = st.columns(2)

with col5:
    df_trade = load("NE.TRD.GNFS.ZS")
    if not df_trade.empty:
        fig = line_chart(
            df_trade,
            title="Trade as % of GDP",
            y_label="Trade (% of GDP)",
            color="#0277BD",
        )
        st.plotly_chart(fig, use_container_width=True)

        latest = df_trade.iloc[-1]
        st.caption(
            f"**Latest ({int(latest['year'])}):** {latest['value']:.1f}% of GDP — "
            "Measures openness to global markets."
        )
    else:
        st.info("Trade data currently unavailable.")

with col6:
    df_fdi = load("BX.KLT.DINV.WD.GD.ZS")
    if not df_fdi.empty:
        fig = line_chart(
            df_fdi,
            title="Foreign Direct Investment, Net Inflows (% of GDP)",
            y_label="FDI Net Inflows (% GDP)",
            color="#6A1B9A",
        )
        st.plotly_chart(fig, use_container_width=True)

        latest = df_fdi.iloc[-1]
        st.caption(
            f"**Latest ({int(latest['year'])}):** {latest['value']:.2f}% of GDP"
        )
    else:
        st.info("FDI data currently unavailable.")

st.divider()

# ---------------------------------------------------------------------------
# Summary insight box
# ---------------------------------------------------------------------------

st.subheader("Key Takeaways")

df_g = fetch_indicator("KE", "NY.GDP.MKTP.KD.ZG")
df_gdp_abs = fetch_indicator("KE", "NY.GDP.MKTP.CD")

if not df_g.empty and not df_gdp_abs.empty:
    avg_growth  = df_g[df_g["year"] >= 2015]["value"].mean()
    gdp_2015    = df_gdp_abs[df_gdp_abs["year"] == 2015]["value"].values
    gdp_latest  = df_gdp_abs.iloc[-1]
    gdp_growth_pct = (
        ((gdp_latest["value"] - gdp_2015[0]) / gdp_2015[0] * 100)
        if len(gdp_2015) > 0 else 0
    )

    st.info(
        f"**2015–{int(gdp_latest['year'])} GDP Growth:** Kenya's economy expanded by "
        f"**{gdp_growth_pct:.0f}%** in absolute terms, from $70B to "
        f"${gdp_latest['value']/1e9:.0f}B.  \n"
        f"**Average Annual Growth Rate (2015–{int(df_g.iloc[-1]['year'])}):** "
        f"{avg_growth:.1f}%  \n"
        f"**Inflation challenge:** Persistent inflation above the CBK target of 5% ±2.5% "
        f"remains Kenya's primary macroeconomic policy challenge."
    )
