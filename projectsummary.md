# KenyaPulse — Project Summary

## Project Overview

KenyaPulse is a multi-page Streamlit analytics dashboard that fetches live data from the World Bank Open Data API and presents Kenya's macroeconomic and social development indicators across 25 years. The application benchmarks Kenya against 6 African peer nations, rendering 10+ interactive Plotly chart types within a fully containerised Docker environment. No authentication is required — the World Bank API is completely public.

---

## Complete Project Structure

```
kenyapulse/
├── Home.py
├── config.py
├── pages/
│   ├── 1_Economic_Indicators.py
│   ├── 2_Social_Indicators.py
│   └── 3_Regional_Comparison.py
├── utils/
│   ├── __init__.py
│   └── api.py
│   └── charts.py
├── .streamlit/
│   └── config.toml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── readme.md
└── projectsummary.md
```

---

## File-by-File Breakdown

### `config.py`

This is the single source of truth for all application constants. No other file hardcodes indicator codes, country codes, or colour values — everything is imported from here.

It defines six structures:

**`ECONOMIC_INDICATORS`** — a `dict[str, str]` mapping human-readable labels to World Bank indicator codes for six macroeconomic metrics: GDP in current US dollars (`NY.GDP.MKTP.CD`), annual GDP growth rate (`NY.GDP.MKTP.KD.ZG`), GDP per capita (`NY.GDP.PCAP.CD`), CPI inflation (`FP.CPI.TOTL.ZG`), trade as a percentage of GDP (`NE.TRD.GNFS.ZS`), and FDI net inflows as a percentage of GDP (`BX.KLT.DINV.WD.GD.ZS`).

**`SOCIAL_INDICATORS`** — the same pattern for eight human development metrics: total population (`SP.POP.TOTL`), urban population percentage (`SP.URB.TOTL.IN.ZS`), life expectancy at birth (`SP.DYN.LE00.IN`), under-5 mortality rate (`SH.DYN.MORT`), adult literacy rate (`SE.ADT.LITR.ZS`), unemployment rate (`SL.UEM.TOTL.ZS`), internet users as a percentage of population (`IT.NET.USER.ZS`), and access to electricity (`EG.ELC.ACCS.ZS`).

**`ALL_INDICATORS`** — a merged dict combining both dicts above, used wherever a complete indicator list is needed without duplication.

**`COMPARISON_COUNTRIES`** — a `dict[str, str]` mapping display names to ISO 3166-1 alpha-2 country codes for Kenya (`KE`), Tanzania (`TZ`), Uganda (`UG`), Ethiopia (`ET`), Rwanda (`RW`), South Africa (`ZA`), and Nigeria (`NG`).

**`HOME_KPIS`** — a `list[dict]`, where each dict has four keys: `label` (display name), `code` (World Bank indicator code), `fmt` (one of four format strings: `billions_usd`, `percent`, `millions`, `years`), and `icon` (emoji for the KPI card label). There are six entries, one per KPI card on the home page.

**`RADAR_INDICATORS`** — a `dict[str, str]` defining the six indicators used in the radar chart on the Regional Comparison page: GDP per capita, life expectancy, literacy rate, electricity access, internet access, and urban population percentage. These six were selected because they cover economic, health, education, infrastructure, and digital dimensions, and all become comparable after min-max normalisation.

**Visual constants** — `KENYA_GREEN = "#006600"`, `KENYA_RED = "#BB0000"`, `KENYA_BLACK = "#1A1A1A"`, `ACCENT_GOLD = "#F5A623"`, `CHART_PALETTE` (a list of 7 hex colours used to assign a distinct colour to each country in multi-country charts), `PLOT_BG = "#FFFFFF"`, and `GRID_CLR = "#EEEEEE"`.

---

### `utils/__init__.py`

An empty file that makes `utils/` a Python package, enabling `from utils.api import ...` and `from utils.charts import ...` to resolve correctly when Streamlit runs `Home.py` or any page under `pages/`.

---

### `utils/api.py`

The World Bank API client. Every page in the application imports from this module. It contains four public functions and two private helpers, all using Streamlit's `@st.cache_data` decorator to cache results in-process for one hour (3600 seconds), so navigating between pages does not re-issue HTTP requests.

**Module-level constants:**
- `_BASE = "https://api.worldbank.org/v2"` — the API root
- `_TIMEOUT = 15` — seconds before a request is considered failed
- `_CACHE_TTL = 3600` — one-hour cache window

**`_parse_response(payload: list) -> list[dict]`** — a private helper that receives the raw JSON response from the World Bank API, which is always a two-element list: index 0 is metadata (page count, total records, etc.) and index 1 is the actual data array. This function returns the data array filtered to only records where `value` is not `None`, since the API includes null placeholders for years where a country has not reported a given indicator.

**`_get(url: str, params: dict) -> list | None`** — a private helper that wraps `requests.get` with error handling for three failure modes: request timeout (raises `requests.exceptions.Timeout`), non-2xx HTTP status (raises `requests.exceptions.HTTPError`), and any other unexpected exception. On any failure it logs a warning and returns `None` rather than raising, so callers receive an empty DataFrame rather than a crash.

**`fetch_indicator(country_code: str, indicator_code: str) -> pd.DataFrame`** — fetches a single indicator for a single country, returning up to the 30 most recent data points (`mrv=30`). Returns a DataFrame with columns `year` (int) and `value` (float), sorted ascending by year. If the API returns no data or an error, it returns an empty DataFrame with those same two columns so callers can safely call `.empty` without a KeyError.

**`fetch_multi_country(indicator_code: str, country_codes: list[str], most_recent: int = 25) -> pd.DataFrame`** — fetches a single indicator for multiple countries in one HTTP request by joining their ISO codes with semicolons (e.g. `KE;TZ;UG;ET;RW;ZA;NG`), which the World Bank API supports natively. Returns a DataFrame with columns `country` (str, the full country name as returned by the API), `year` (int), and `value` (float). `most_recent` defaults to 25 and controls the `mrv` parameter. `per_page=500` ensures all countries' data fits in a single page response.

**`fetch_latest_snapshot(indicator_code: str, country_codes: list[str]) -> pd.DataFrame`** — a convenience wrapper around `fetch_multi_country` that calls it with `most_recent=5` (allowing the API to return up to 5 recent years per country), then groups by country and keeps the row with the highest year. This produces a single-row-per-country DataFrame showing the most recent available value. Used by `3_Regional_Comparison.py` for the horizontal bar charts.

**`get_latest_value(country_code: str, indicator_code: str) -> tuple[float | None, int | None]`** — a thin wrapper around `fetch_indicator` that returns a `(value, year)` tuple from the last row of the result. Returns `(None, None)` if the DataFrame is empty. Used by `Home.py`'s KPI card loop before the more complete KPI logic was implemented inline.

---

### `utils/charts.py`

Contains all Plotly figure construction logic. No page file contains any `go.Figure()` calls or `px.line()` calls directly — all charting is delegated here, keeping the page files clean and the chart styling consistent.

Imports `CHART_PALETTE`, `GRID_CLR`, `KENYA_GREEN`, and `PLOT_BG` from `config.py`.

**`_base_layout(fig: go.Figure, title: str = "") -> go.Figure`** — a private helper applied at the end of every chart builder. It sets: left-aligned title in dark grey at 16px, white plot and paper backgrounds, Arial font, consistent margins (`l=40, r=20, t=50, b=40`), `hovermode="x unified"` (so hovering any point shows all series' values at that x position), horizontal legend anchored above the chart, and light grey grid lines on both axes.

**`line_chart(df, title, y_label, color, fill=True) -> go.Figure`** — builds a `go.Scatter` trace in `lines+markers` mode. When `fill=True`, it fills the area between the line and y=0 using `fill="tozeroy"` and a semi-transparent version of the line colour (achieved by appending `14` as the hex alpha channel, giving ~8% opacity). Used for time-series indicators like GDP, life expectancy, internet access, and electricity.

**`bar_chart(df, title, y_label, color, show_negative_red=False) -> go.Figure`** — builds a `go.Bar` trace. When `show_negative_red=True`, bar colours are computed per-value: positive bars use `KENYA_GREEN` and negative bars use `#BB0000` (Kenya red). This is used for the GDP growth rate chart so contraction years are visually distinct. The inflation chart calls this function but overrides bar colours after the fact with a three-tier heat scale (`#FF8A65` for <5%, `#EF5350` for 5–10%, `#B71C1C` for >10%).

**`multi_line_chart(df, title, y_label) -> go.Figure`** — uses `px.line` with `color="country"` to assign each country a distinct colour from `CHART_PALETTE`. All seven countries use the same palette consistently across any chart that renders them simultaneously.

**`horizontal_bar(df, title, x_label, highlight_country="Kenya") -> go.Figure`** — builds a horizontal `go.Bar` with `orientation="h"`. Countries are sorted ascending by value so the highest-ranked country appears at the top. Kenya's bar is rendered in `KENYA_GREEN`; all other countries use `#90CAF9` (light blue), making Kenya's position immediately readable at a glance.

**`radar_chart(scores: dict[str, dict[str, float]], title) -> go.Figure`** — builds a `go.Scatterpolar` trace per country. The polygon is closed by appending the first category value and category name to the end of each list. Kenya's fill opacity is set to `0.40`; all other countries use `0.25`, so Kenya's shape is visually dominant. The radial axis range is forced to `[0, 1]` with percentage tick labels.

**`donut_chart(labels, values, title, colors=None) -> go.Figure`** — builds a `go.Pie` with `hole=0.55`. Used on the Social Indicators page to show the urban/rural population split for the latest available year.

**`normalise_for_radar(raw: dict[str, dict[str, float | None]]) -> dict[str, dict[str, float]]`** — a mathematical utility, not a chart builder. Takes raw indicator values grouped by country and indicator, then applies min-max normalisation per indicator across all countries so every axis maps to `[0, 1]`. For an indicator where all countries have the same value (range = 0), the denominator is replaced with `1.0` to prevent division by zero. Countries missing a value for a given indicator receive `0.0`.

---

### `Home.py`

The Streamlit entry point. This is the file passed to `streamlit run`. Streamlit automatically registers all `.py` files inside `pages/` as additional pages and links them in the sidebar navigation.

`st.set_page_config` is called first (Streamlit requires this to be the first Streamlit call in the file) with `layout="wide"` and the Kenyan flag emoji as the page icon.

A `st.markdown` block injects global CSS that styles three elements: the sidebar background colour (`#f7f9f7`), Streamlit's `[data-testid="metric-container"]` components (adding a left green border, white background, uppercase label, and bold value), and `.nav-card` div elements (white card with rounded corners and a hover shadow effect).

The sidebar renders the Kenyan flag image from `flagcdn.com`, the app title, data source attribution, and `st.page_link` calls for each of the four pages. These page links are replicated in every page's sidebar for consistent navigation across the app.

The KPI card row loops over `HOME_KPIS` from `config.py` using `zip(st.columns(6), HOME_KPIS)`. For each KPI it calls `fetch_indicator("KE", kpi["code"])`, reads the last row as the latest value, reads the second-to-last row as the previous year, formats both using a `_FMT` dict of lambdas keyed on the `fmt` field, computes a signed delta string, and renders `st.metric`. For inflation, unemployment, and under-5 mortality (where lower is better), `delta_color="inverse"` is set so Streamlit renders a downward delta in green rather than red.

The narrative section uses a `st.columns([3, 2])` split: the left column contains a written summary of Kenya's economic trajectory, and the right column renders a hardcoded `facts` dict as bold-key markdown lines.

The navigation section renders three `<div class="nav-card">` HTML blocks using `st.markdown(..., unsafe_allow_html=True)`, styled by the CSS injected earlier.

---

### `pages/1_Economic_Indicators.py`

Displays six economic charts across three `st.columns(2)` rows.

A `load(code)` helper function is defined locally at module scope. It calls `fetch_indicator("KE", code)` and applies a year-range boolean filter using the `year_range` tuple from the sidebar slider. This avoids repeating the filter logic at every chart call site.

Row 1 — GDP absolute value (line chart) and GDP growth rate (bar chart with `show_negative_red=True`). The GDP line divides raw values by `1e9` before passing to `line_chart` so the y-axis reads in billions rather than raw dollar amounts.

Row 2 — GDP per capita (line chart) and inflation (bar chart). The inflation bar chart calls `bar_chart` then calls `fig.update_traces` on the returned figure to override bar colours with a three-tier heat scale based on each bar's value — this is the only instance in the project where a page directly modifies a figure returned by a chart builder.

Row 3 — Trade as a percentage of GDP (line chart) and FDI net inflows (line chart).

A "Key Takeaways" section at the bottom re-fetches GDP growth and GDP absolute data (these are already cached, so no new HTTP requests occur) and computes: average annual growth since 2015, the absolute percentage expansion in GDP from 2015 to the latest year, and renders this as a formatted `st.info` block.

---

### `pages/2_Social_Indicators.py`

Displays eight social and human development charts across four `st.columns(2)` rows.

Row 1 — Population total (line chart, values divided by `1e6` for millions display) and urban/rural split. The urban split section makes two separate chart calls: a `donut_chart` showing the latest year's split as a proportion, and a `line_chart` showing the urbanisation rate trend over the selected year range. These two charts appear stacked vertically within the right column.

Row 2 — Life expectancy (line chart) and under-5 mortality rate (line chart). Both captions compute a change since the first year in the filtered range: life expectancy shows years gained, mortality shows percentage reduction.

Row 3 — Adult literacy rate (bar chart) and unemployment rate (bar chart). The literacy bar chart includes a note that World Bank updates literacy data infrequently, explaining potential multi-year gaps in the bars.

Row 4 — Internet users percentage (line chart) and electricity access percentage (line chart). Both captions show the start and end values for the selected range to communicate the magnitude of change.

---

### `pages/3_Regional_Comparison.py`

The most complex page. It uses all four multi-country functions from `utils/api.py` and all four multi-country chart builders from `utils/charts.py`.

The sidebar has three interactive controls: a `st.multiselect` for country selection (Kenya is always forced into the list with a `st.warning` if removed), a year range slider for the trend chart, and a `st.selectbox` for choosing which indicator to display in the time-series comparison. A local `INDICATOR_MAP` dict inside the sidebar block maps the seven selectbox options to their World Bank codes.

`sel_codes` is computed by list-comprehending `COMPARISON_COUNTRIES[c]` for each selected country name. This is used as the `country_codes` argument for all multi-country API calls on the page.

**Radar chart** — iterates over `RADAR_INDICATORS` from `config.py`, calling `fetch_latest_snapshot` for each indicator. The World Bank API returns country names as full strings (e.g., "Kenya" or "South Africa"), which are matched against `selected_countries` using a case-insensitive substring check (`n.lower() in country_name.lower() or country_name.lower() in n.lower()`). Matched values are stored in `raw_scores`, which is then passed to `normalise_for_radar` to produce the `[0, 1]`-scaled dict, then to `radar_chart` to produce the figure.

**Trend comparison** — calls `fetch_multi_country` with `most_recent=30` and the indicator code from `INDICATOR_MAP[compare_indicator]`, then filters by `year_range` before passing to `multi_line_chart`.

**Ranked snapshot sections** — call `fetch_latest_snapshot` for GDP per capita, life expectancy, internet access, and electricity in four separate calls across two `st.columns(2)` pairs, each rendered as a `horizontal_bar` with `highlight_country="Kenya"`.

---

### `.streamlit/config.toml`

Streamlit's theme and server configuration file. It is automatically read by Streamlit at startup before any Python code runs.

The `[theme]` section sets `primaryColor = "#006600"` (Kenya green), which controls button colours, slider handles, and active input highlights. `backgroundColor = "#FFFFFF"` and `secondaryBackgroundColor = "#F7F9F7"` (a very light green tint) set the main content and sidebar backgrounds respectively. `textColor = "#1A1A1A"` sets body text. `font = "sans serif"` prevents Streamlit from loading its default Google Font.

The `[server]` section sets `headless = true` (suppresses the browser-open prompt on startup, required for Docker), `port = 8501`, `enableCORS = false`, and `enableXsrfProtection = true`.

The `[browser]` section sets `gatherUsageStats = false` to disable telemetry.

---

### `Dockerfile`

A two-stage build. The first stage (`base`) starts from `python:3.11-slim`, sets `/app` as the working directory, copies only `requirements.txt`, and runs `pip install --no-cache-dir`. Copying requirements before the rest of the source code means Docker caches the pip install layer — if only application code changes and not dependencies, Docker reuses the cached layer and skips reinstalling packages.

The second stage (`runtime`) inherits from `base` and copies the entire project into `/app`. It exposes port `8501` and adds a `HEALTHCHECK` that polls `http://localhost:8501/_stcore/health` (Streamlit's built-in health endpoint) every 30 seconds. The `ENTRYPOINT` runs `streamlit run Home.py` with `--server.port=8501`, `--server.address=0.0.0.0` (binds to all interfaces so Docker's port mapping works), and `--server.headless=true`.

---

### `docker-compose.yml`

Defines a single service `kenyapulse` that builds from the local Dockerfile. Maps host port `8501` to container port `8501`. Sets `restart: unless-stopped` so the container auto-restarts on failure or system reboot. Repeats the health check from the Dockerfile at the Compose level so `docker-compose ps` reports container health status.

---

### `requirements.txt`

Five pinned dependencies:

| Package | Version | Role |
| :--- | :--- | :--- |
| `streamlit` | 1.32.2 | Multi-page app framework, KPI metrics, sidebars, layout |
| `plotly` | 5.20.0 | All chart types (Scatter, Bar, Pie, Scatterpolar) |
| `pandas` | 2.2.1 | DataFrames for API response parsing, filtering, groupby |
| `requests` | 2.31.0 | HTTP client for World Bank API calls |
| `numpy` | 1.26.4 | Imported in `charts.py`; available for numeric operations |

All versions are pinned for reproducibility so `docker-compose up` produces the same environment regardless of when it is run.

---

### `.env.example`

Documents that this project requires no secrets. The World Bank Open Data API is entirely public with no API key or OAuth token. The file exists as a repository convention and to allow optional Streamlit server setting overrides via environment variables if needed for deployment.

---

### `.gitignore`

Excludes: Python bytecode (`__pycache__/`, `*.pyc`), virtual environments (`.venv/`, `venv/`, `env/`), the real `.env` file, `.streamlit/secrets.toml` (Streamlit's secret store, not used here but excluded by convention), OS metadata (`.DS_Store`, `Thumbs.db`), IDE directories, and log files.

---

## Data Flow — How Files Interact

```
User opens browser at localhost:8501
         │
         ▼
  Streamlit loads Home.py
         │
         ├── reads .streamlit/config.toml (theme + server settings)
         │
         ├── imports HOME_KPIS from config.py
         │
         └── imports fetch_indicator from utils/api.py
                      │
                      └── calls World Bank API → returns pd.DataFrame
                                   │
                                   └── st.metric renders KPI cards

User clicks "Economic Indicators" in sidebar
         │
         ▼
  Streamlit loads pages/1_Economic_Indicators.py
         │
         ├── imports fetch_indicator from utils/api.py
         │           (cached — no new HTTP request if within 1hr TTL)
         │
         ├── imports line_chart, bar_chart from utils/charts.py
         │           which imports KENYA_GREEN, CHART_PALETTE from config.py
         │
         └── local load() helper applies year_range filter to cached DataFrame
                      │
                      └── chart builders return go.Figure → st.plotly_chart renders

User clicks "Regional Comparison" in sidebar
         │
         ▼
  Streamlit loads pages/3_Regional_Comparison.py
         │
         ├── imports COMPARISON_COUNTRIES, RADAR_INDICATORS from config.py
         │
         ├── imports fetch_latest_snapshot, fetch_multi_country from utils/api.py
         │
         └── imports radar_chart, normalise_for_radar, multi_line_chart,
                     horizontal_bar from utils/charts.py
                      │
                      ├── fetch_latest_snapshot → per-country latest value dict
                      │        → normalise_for_radar → [0,1] scores
                      │        → radar_chart → go.Figure → st.plotly_chart
                      │
                      └── fetch_multi_country → multi-country time-series DataFrame
                               → multi_line_chart → go.Figure → st.plotly_chart
```

The dependency graph is strictly one-directional: page files import from `utils/api.py` and `utils/charts.py`; `utils/charts.py` imports from `config.py`; `utils/api.py` imports nothing from the project. No circular dependencies exist. `config.py` has no project-level imports and can always be read first.

---

## Why Each Design Decision Was Made

| Decision | Reason |
| :--- | :--- |
| `@st.cache_data(ttl=3600)` on all API functions | Prevents re-fetching on every Streamlit widget interaction; makes page navigation instant after the first load |
| `_parse_response` strips nulls before DataFrame construction | World Bank returns null placeholders for years with no data; including them causes dtype issues and broken chart axes |
| `mrv=30` for single-country fetch, `mrv=25` for multi-country | 30 years covers the full analytical window for Kenya pages; 25 is sufficient for regional trends while keeping response sizes small |
| `per_page=500` in `fetch_multi_country` | 7 countries × 25 years = 175 records maximum; 500 guarantees single-page responses without pagination logic |
| `normalise_for_radar` in `charts.py`, not in the page | Normalisation is a chart concern — it exists to make the radar chart work; keeping it in `charts.py` next to `radar_chart` makes the coupling explicit |
| Inflation bars override colours post-construction | The `bar_chart` builder's `show_negative_red` parameter handles the general case; the inflation heat scale is a one-off visual decision specific to that indicator, so overriding after construction keeps the reusable function clean |
| Donut chart uses raw fetch, not `load()` | The donut shows the most recent overall value regardless of the year range slider, because the urban/rural split is a snapshot, not a time-series comparison |
| Kenya always forced into regional comparison | Every chart on that page benchmarks against Kenya; removing Kenya would make the page meaningless |
| Two-stage Dockerfile | Separates the dependency installation layer from the application code layer; code-only changes skip pip reinstall, reducing build time |
