# wb_api.py
# World Bank API helper module for Shiny app
# Fetches development indicators from World Bank Open Data API
# Pairs with app.py in 02_productivity/shiny_app

import requests
from typing import Optional

BASE = "https://api.worldbank.org/v2"
PER_PAGE = 200


def fetch_world_bank_data(
    countries: list[str],
    indicator_id: str,
    date_range: str,
) -> list[dict]:
    """
    Fetch indicator data from World Bank API for selected countries.
    Handles pagination and returns cleaned records.

    Parameters
    ----------
    countries : list[str]
        List of ISO country codes (e.g., ["USA", "CHN", "IND"]).
    indicator_id : str
        World Bank indicator code (e.g., NY.GDP.MKTP.CD for GDP).
    date_range : str
        Year range as "start:end" (e.g., "2005:2024").

    Returns
    -------
    list[dict]
        List of cleaned record dicts with keys:
        country, country_id, year, indicator, indicator_id, value, unit, obs_status.

    Raises
    ------
    RuntimeError
        If request fails or response format is unexpected.
    """
    if not countries:
        return []

    country_str = ";".join(countries)
    url = f"{BASE}/country/{country_str}/indicator/{indicator_id}"
    params: dict = {"format": "json", "per_page": PER_PAGE, "date": date_range}

    all_rows = _fetch_all_pages(url, params)
    return _clean_records(all_rows)


def _fetch_all_pages(url: str, params: dict) -> list[dict]:
    """
    Iterate through all API pages and collect data.
    """
    all_rows: list[dict] = []
    page = 1

    while True:
        params_with_page = dict(params)
        params_with_page["page"] = page

        r = requests.get(url, params=params_with_page, timeout=30)

        if r.status_code != 200:
            raise RuntimeError(
                f"API request failed with status {r.status_code}. "
                f"Response: {r.text[:300]}"
            )

        payload = r.json()

        if not isinstance(payload, list) or len(payload) < 2:
            raise RuntimeError("Unexpected API response format")

        meta, data = payload[0], payload[1]
        if not data:
            break

        all_rows.extend(data)

        pages = meta.get("pages", 1)
        if page >= pages:
            break
        page += 1

    return all_rows


def _clean_records(rows: list[dict]) -> list[dict]:
    """
    Extract key fields and filter out null values.
    """
    cleaned = []
    for row in rows:
        rec = {
            "country": (row.get("country") or {}).get("value"),
            "country_id": (row.get("country") or {}).get("id"),
            "year": row.get("date"),
            "indicator": (row.get("indicator") or {}).get("value"),
            "indicator_id": (row.get("indicator") or {}).get("id"),
            "value": row.get("value"),
            "unit": row.get("unit"),
            "obs_status": row.get("obs_status"),
        }
        if rec["value"] is not None:
            cleaned.append(rec)
    return cleaned
