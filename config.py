ECONOMIC_INDICATORS: dict[str, str] = {
    "GDP (Current US$)": "NY.GDP.MKTP.CD",
    "GDP Growth Rate (%)": "NY.GDP.MKTP.KD.ZG",
    "GDP Per Capita (US$)": "NY.GDP.PCAP.CD",
    "Inflation, CPI (%)": "FP.CPI.TOTL.ZG",
    "Trade (% of GDP)": "NE.TRD.GNFS.ZS",
    "FDI Net Inflows (% of GDP)": "BX.KLT.DINV.WD.GD.ZS",
}

SOCIAL_INDICATORS: dict[str, str] = {
    "Population, Total": "SP.POP.TOTL",
    "Urban Population (%)": "SP.URB.TOTL.IN.ZS",
    "Life Expectancy at Birth (years)": "SP.DYN.LE00.IN",
    "Under-5 Mortality (per 1,000 live births)": "SH.DYN.MORT",
    "Adult Literacy Rate (%)": "SE.ADT.LITR.ZS",
    "Unemployment Rate (%)": "SL.UEM.TOTL.ZS",
    "Internet Users (% of population)": "IT.NET.USER.ZS",
    "Access to Electricity (%)": "EG.ELC.ACCS.ZS",
}

ALL_INDICATORS: dict[str, str] = {**ECONOMIC_INDICATORS, **SOCIAL_INDICATORS}

COMPARISON_COUNTRIES: dict[str, str] = {
    "Kenya": "KE",
    "Tanzania": "TZ",
    "Uganda": "UG",
    "Ethiopia": "ET",
    "Rwanda": "RW",
    "South Africa": "ZA",
    "Nigeria": "NG",
}

HOME_KPIS: list[dict] = [
    {"label": "GDP",             "code": "NY.GDP.MKTP.CD",    "fmt": "billions_usd", "icon": "💰"},
    {"label": "GDP Growth",      "code": "NY.GDP.MKTP.KD.ZG", "fmt": "percent",      "icon": "📈"},
    {"label": "Inflation",       "code": "FP.CPI.TOTL.ZG",    "fmt": "percent",      "icon": "🏷️"},
    {"label": "Population",      "code": "SP.POP.TOTL",       "fmt": "millions",     "icon": "👥"},
    {"label": "Life Expectancy", "code": "SP.DYN.LE00.IN",    "fmt": "years",        "icon": "❤️"},
    {"label": "Internet Access", "code": "IT.NET.USER.ZS",    "fmt": "percent",      "icon": "🌐"},
]

RADAR_INDICATORS: dict[str, str] = {
    "GDP Per Capita":   "NY.GDP.PCAP.CD",
    "Life Expectancy":  "SP.DYN.LE00.IN",
    "Literacy Rate":    "SE.ADT.LITR.ZS",
    "Electricity":      "EG.ELC.ACCS.ZS",
    "Internet Access":  "IT.NET.USER.ZS",
    "Urban Population": "SP.URB.TOTL.IN.ZS",
}

KENYA_GREEN   = "#006600"
KENYA_RED     = "#BB0000"
KENYA_BLACK   = "#1A1A1A"
ACCENT_GOLD   = "#F5A623"
CHART_PALETTE = [
    "#006600", "#2196F3", "#FF5722", "#9C27B0",
    "#FF9800", "#00BCD4", "#E91E63",
]
PLOT_BG  = "#FFFFFF"
GRID_CLR = "#EEEEEE"
