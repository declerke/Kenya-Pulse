from __future__ import annotations

import logging
import time

import pandas as pd
import requests
import streamlit as st

logger = logging.getLogger(__name__)

_BASE = "https://api.worldbank.org/v2"
_TIMEOUT = 30  
_CACHE_TTL = 3600  
_MAX_RETRIES = 3
_RETRY_DELAY = 2  

def _parse_response(payload: list) -> list[dict]:
    if len(payload) < 2 or not payload[1]:
        return []
    return [item for item in payload[1] if item.get("value") is not None]

def _get(url: str, params: dict) -> list | None:
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            r = requests.get(url, params=params, timeout=_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.Timeout:
            logger.warning("World Bank API timeout (attempt %d/%d): %s", attempt, _MAX_RETRIES, url)
        except requests.exceptions.HTTPError as exc:
            logger.warning("World Bank API HTTP error: %s — %s", exc.response.status_code, url)
            break  
        except Exception as exc:  
            logger.warning("World Bank API error (attempt %d/%d): %s", attempt, _MAX_RETRIES, exc)
        if attempt < _MAX_RETRIES:
            time.sleep(_RETRY_DELAY)
    return None

@st.cache_data(ttl=_CACHE_TTL, show_spinner="Fetching data from World Bank...")
def fetch_indicator(country_code: str, indicator_code: str) -> pd.DataFrame:
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
    country_str = ";".join(country_codes)
    url = f"{_BASE}/country/{country_str}/indicator/{indicator_code}"
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
    df = fetch_multi_country(indicator_code, country_codes, most_recent=5)
    if df.empty:
        return df
    return (
        df.sort_values("year", ascending=False)
        .groupby("country", as_index=False)
        .first()
    )

def get_latest_value(country_code: str, indicator_code: str) -> tuple[float | None, int | None]:
    df = fetch_indicator(country_code, indicator_code)
    if df.empty:
        return None, None
    row = df.iloc[-1]
    return float(row["value"]), int(row["year"])
