import streamlit as st
from utils.api import fetch_indicator
from utils.charts import bar_chart, donut_chart, line_chart

st.set_page_config(
    page_title="Social Indicators — KenyaPulse",
    page_icon="👥",
    layout="wide",
)

with st.sidebar:
    st.markdown("## 👥 Social Indicators")
    st.caption("Human development metrics for Kenya.")
    st.divider()
    year_range = st.slider(
        "Year range",
        min_value=2000,
        max_value=2024,
        value=(2005, 2024),
        key="social_year_range",
    )
    st.divider()
    st.page_link("Home.py",                         label="🏠 Overview")
    st.page_link("pages/1_Economic_Indicators.py",  label="💹 Economic Indicators")
    st.page_link("pages/3_Regional_Comparison.py",  label="🌍 Regional Comparison")

st.markdown("# 👥 Social Indicators")
st.caption(
    f"Kenya human development metrics · {year_range[0]}–{year_range[1]} · "
    "Source: World Bank Open Data"
)
st.divider()

def load(code: str):
    df = fetch_indicator("KE", code)
    if df.empty:
        return df
    return df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])].copy()

st.subheader("Population")

col1, col2 = st.columns(2)

with col1:
    df_pop = load("SP.POP.TOTL")
    if not df_pop.empty:
        df_pop["value"] = df_pop["value"] / 1e6
        fig = line_chart(
            df_pop,
            title="Total Population (Millions)",
            y_label="Population (Millions)",
            color="#006600",
        )
        st.plotly_chart(fig, use_container_width=True)
        latest = df_pop.iloc[-1]
        st.caption(
            f"**Latest ({int(latest['year'])}):** {latest['value']:.1f}M — "
            "Kenya is projected to reach 100M by 2050."
        )
    else:
        st.info("Population data unavailable.")

with col2:
    df_urb = fetch_indicator("KE", "SP.URB.TOTL.IN.ZS")
    if not df_urb.empty:
        latest_urb = df_urb.iloc[-1]
        urban_pct  = float(latest_urb["value"])
        rural_pct  = 100.0 - urban_pct
        fig = donut_chart(
            labels=["Urban", "Rural"],
            values=[urban_pct, rural_pct],
            title=f"Urban vs Rural Population Split ({int(latest_urb['year'])})",
            colors=["#006600", "#A5D6A7"],
        )
        st.plotly_chart(fig, use_container_width=True)

        df_urb_f = df_urb[(df_urb["year"] >= year_range[0]) & (df_urb["year"] <= year_range[1])]
        if not df_urb_f.empty:
            fig2 = line_chart(
                df_urb_f,
                title="Urbanisation Rate Over Time (%)",
                y_label="Urban Population (%)",
                color="#2E7D32",
                fill=False,
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Urban population data unavailable.")

st.divider()

st.subheader("Health")

col3, col4 = st.columns(2)

with col3:
    df_le = load("SP.DYN.LE00.IN")
    if not df_le.empty:
        fig = line_chart(
            df_le,
            title="Life Expectancy at Birth (Years)",
            y_label="Years",
            color="#1565C0",
        )
        st.plotly_chart(fig, use_container_width=True)

        first = df_le.iloc[0]
        last  = df_le.iloc[-1]
        gain  = last["value"] - first["value"]
        st.caption(
            f"**Gained {gain:.1f} years** since {int(first['year'])} · "
            f"Latest: **{last['value']:.1f} years** ({int(last['year'])})"
        )
    else:
        st.info("Life expectancy data unavailable.")

with col4:
    df_mort = load("SH.DYN.MORT")
    if not df_mort.empty:
        fig = line_chart(
            df_mort,
            title="Under-5 Mortality Rate (per 1,000 Live Births)",
            y_label="Deaths per 1,000",
            color="#C62828",
        )
        st.plotly_chart(fig, use_container_width=True)

        first = df_mort.iloc[0]
        last  = df_mort.iloc[-1]
        pct_reduction = (first["value"] - last["value"]) / first["value"] * 100
        st.caption(
            f"**{pct_reduction:.0f}% reduction** since {int(first['year'])} — "
            f"Latest: **{last['value']:.1f}** per 1,000 ({int(last['year'])})"
        )
    else:
        st.info("Mortality data unavailable.")

st.divider()

st.subheader("Education & Labour")

col5, col6 = st.columns(2)

with col5:
    df_lit = load("SE.ADT.LITR.ZS")
    if not df_lit.empty:
        fig = bar_chart(
            df_lit,
            title="Adult Literacy Rate (% aged 15+)",
            y_label="Literacy Rate (%)",
            color="#006600",
        )
        st.plotly_chart(fig, use_container_width=True)
        latest = df_lit.iloc[-1]
        st.caption(
            f"**Latest ({int(latest['year'])}):** {latest['value']:.1f}% — "
            "Note: World Bank updates literacy data infrequently; gaps are normal."
        )
    else:
        st.info("Literacy rate data unavailable or infrequently reported.")

with col6:
    df_unem = load("SL.UEM.TOTL.ZS")
    if not df_unem.empty:
        fig = bar_chart(
            df_unem,
            title="Unemployment Rate (% of Total Labour Force)",
            y_label="Unemployment (%)",
            color="#F57F17",
        )
        st.plotly_chart(fig, use_container_width=True)
        latest = df_unem.iloc[-1]
        st.caption(
            f"**Latest ({int(latest['year'])}):** {latest['value']:.1f}% — "
            "Youth unemployment is significantly higher than the national average."
        )
    else:
        st.info("Unemployment data unavailable.")

st.divider()

st.subheader("Digital & Infrastructure Access")

col7, col8 = st.columns(2)

with col7:
    df_net = load("IT.NET.USER.ZS")
    if not df_net.empty:
        fig = line_chart(
            df_net,
            title="Internet Users (% of Population)",
            y_label="Internet Users (%)",
            color="#0277BD",
        )
        st.plotly_chart(fig, use_container_width=True)
        first = df_net.iloc[0]
        last  = df_net.iloc[-1]
        st.caption(
            f"**From {first['value']:.1f}% ({int(first['year'])}) → "
            f"{last['value']:.1f}% ({int(last['year'])})** — "
            "Driven by mobile broadband and M-PESA ecosystem growth."
        )
    else:
        st.info("Internet access data unavailable.")

with col8:
    df_elec = load("EG.ELC.ACCS.ZS")
    if not df_elec.empty:
        fig = line_chart(
            df_elec,
            title="Access to Electricity (% of Population)",
            y_label="Electricity Access (%)",
            color="#F9A825",
        )
        st.plotly_chart(fig, use_container_width=True)
        first = df_elec.iloc[0]
        last  = df_elec.iloc[-1]
        gain  = last["value"] - first["value"]
        st.caption(
            f"**+{gain:.1f} percentage points** since {int(first['year'])} — "
            f"Latest: **{last['value']:.1f}%** ({int(last['year'])}) — "
            "Rural electrification remains the key frontier."
        )
    else:
        st.info("Electricity access data unavailable.")

st.divider()

st.subheader("Human Development Summary")
st.info(
    "Kenya's social indicators show **sustained improvement** across all dimensions:\n\n"
    "- Life expectancy has risen steadily, and under-5 mortality has fallen dramatically\n"
    "- Internet penetration has expanded from near-zero to 40%+ in 20 years, driven by mobile\n"
    "- Electricity access has accelerated since 2013's Last Mile Connectivity rollout\n"
    "- **Challenge:** Urbanisation is outpacing infrastructure capacity in Nairobi and Mombasa"
)
