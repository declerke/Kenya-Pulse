"""
World Bank Open Data API client.

All fetch functions are wrapped with @st.cache_data so results are reused
for the configured TTL (default 1 hour) without hitting the API on every
page reload.

API reference: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
"""

from __future__ import annotations

import logging
import time

import pandas as pd
import requests
import streamlit as st

logger = logging.getLogger(__name__)

_BASE = "https://api.worldbank.org/v2"
_TIMEOUT = 30  # seconds
_CACHE_TTL = 3600  # 1 hour
_MAX_RETRIES = 3
_RETRY_DELAY = 2  # seconds between retries


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_response(payload: list) -> list[dict]:
    """Extract non-null data records from a World Bank API response."""
    if len(payload) < 2 or not payload[1]:
        return []
    return [item for item in payload[1] if item.get("value") is not None]


def _get(url: str, params: dict) -> list | None:
    """Execute a GET request with retries and return the parsed JSON list, or None on error."""
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            r = requests.get(url, params=params, timeout=_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.Timeout:
            logger.warning("World Bank API timeout (attempt %d/%d): %s", attempt, _MAX_RETRIES, url)
        except requests.exceptions.HTTPError as exc:
            logger.warning("World Bank API HTTP error: %s — %s", exc.response.status_code, url)
            break  # don't retry HTTP errors
        except Exception as exc:  # noqa: BLE001
            logger.warning("World Bank API error (attempt %d/%d): %s", attempt, _MAX_RETRIES, exc)
        if attempt < _MAX_RETRIES:
            time.sleep(_RETRY_DELAY)
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@st.cache_data(ttl=_CACHE_TTL, show_spinner="Fetching data from World Bank...")
def fetch_indicator(country_code: str, indicator_code: str) -> pd.DataFrame:
    """
    Return a time-series DataFrame for a single country and indicator.

    Columns: year (int), value (float)
    """
    url = f"{_BASE}/country/{country_code}/indicator/{indicator_code}"
    params = {"format": "json", "per_page": 100, "mrv": 30}
    payload = _get(url, params)
    if payload is None:
        return pd.DataFrame(columns=["year", "value"])

    records = _parse_response(payload)
    if not records:
        return pd.DataFrame(columns=["year", "value"])

    df = pd.DataFrame(
        [{"year": int(r["date"]), "value": float(r["value"])} for r in records]
    )
    return df.sort_values("year").reset_index(drop=True)


@st.cache_data(ttl=_CACHE_TTL, show_spinner="Fetching regional comparison data...")
def fetch_multi_country(
    indicator_code: str,
    country_codes: list[str],
    most_recent: int = 25,
) -> pd.DataFrame:
    """
    Return time-series data for multiple countries in a single request.

    Columns: country (str), year (int), value (float)
    """
    country_str = ";".join(country_codes)
    url = f"{_BASE}/country/{country_str}/indicator/{indicator_code}"
    # Fetch enough pages; World Bank allows up to 500 per_page
    params = {"format": "json", "per_page": 500, "mrv": most_recent}
    payload = _get(url, params)
    if payload is None:
        return pd.DataFrame(columns=["country", "year", "value"])

    records = _parse_response(payload)
    if not records:
        return pd.DataFrame(columns=["country", "year", "value"])

    df = pd.DataFrame(
        [
            {
                "country": r["country"]["value"],
                "year": int(r["date"]),
                "value": float(r["value"]),
            }
            for r in records
        ]
    )
    return df.sort_values(["country", "year"]).reset_index(drop=True)


@st.cache_data(ttl=_CACHE_TTL, show_spinner="Fetching latest snapshot...")
def fetch_latest_snapshot(
    indicator_code: str,
    country_codes: list[str],
) -> pd.DataFrame:
    """
    Return only the most recent available value for each country.

    Columns: country (str), value (float), year (int)
    """
    df = fetch_multi_country(indicator_code, country_codes, most_recent=5)
    if df.empty:
        return df
    # Keep the most recent non-null entry per country
    return (
        df.sort_values("year", ascending=False)
        .groupby("country", as_index=False)
        .first()
    )


def get_latest_value(country_code: str, indicator_code: str) -> tuple[float | None, int | None]:
    """
    Return (value, year) for the most recent data point, or (None, None).
    Convenience wrapper used by the home-page KPI cards.
    """
    df = fetch_indicator(country_code, indicator_code)
    if df.empty:
        return None, None
    row = df.iloc[-1]
    return float(row["value"]), int(row["year"])
