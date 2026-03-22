import requests

BASE = "https://api.worldbank.org/v2"
PER_PAGE = 200


def fetch_world_bank_data(countries: list[str], indicator_id: str, date_range: str) -> list[dict]:
    if not countries:
        return []

    country_str = ";".join(countries)
    url = f"{BASE}/country/{country_str}/indicator/{indicator_id}"
    params = {"format": "json", "per_page": PER_PAGE, "date": date_range}
    rows = _fetch_all_pages(url, params)
    return _clean_records(rows)


def _fetch_all_pages(url: str, params: dict) -> list[dict]:
    all_rows: list[dict] = []
    page = 1

    while True:
        params_with_page = dict(params)
        params_with_page["page"] = page
        response = requests.get(url, params=params_with_page, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(
                f"API request failed with status {response.status_code}. "
                f"Response: {response.text[:300]}"
            )

        payload = response.json()
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
