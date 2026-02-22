"""
LAB AI Reporter (World Bank + Local Ollama, HTML output only)

Pipeline:
1) Query World Bank API with pagination
2) Clean and aggregate data
3) Build prompt (v1/v2/v3 kept for iteration record)
4) Query local Ollama with model fallback
5) Save report.html

Prompt iteration notes for submission:
- v1 issue: too broad, output lacked structure.
- v2 improvement: enforced fixed sections and item counts.
- v3 improvement: constrained model to provided numbers only (no fabrication).
"""

from __future__ import annotations

import json
from datetime import datetime
from html import escape

import requests

# World Bank query config (aligned with 01_query_api/wb_query.py)
BASE = "https://api.worldbank.org/v2"
COUNTRIES = "USA;CHN;IND;JPN;DEU"
INDICATOR = "NY.GDP.MKTP.CD"
DATE_RANGE = "2005:2024"
PER_PAGE = 200

# Ollama config
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_CHAT_URL = f"{OLLAMA_HOST}/api/chat"
MODEL_CANDIDATES = ["gemma3:latest", "smollm2:1.7b"]

# Output
OUTPUT_HTML = "03_query_ai/report.html"
PROMPT_VERSION = "v3"


def fetch_all_pages(url: str, params: dict) -> list[dict]:
    all_rows: list[dict] = []
    page = 1

    while True:
        params_with_page = dict(params)
        params_with_page["page"] = page

        try:
            response = requests.get(url, params=params_with_page, timeout=30)
        except requests.RequestException as exc:
            raise RuntimeError(
                "World Bank API request failed. Check internet/DNS and retry."
            ) from exc
        print(f"[WB] status={response.status_code} page={page}")

        if response.status_code != 200:
            print("[WB] response text (first 300 chars):", response.text[:300])
            raise RuntimeError(f"Request failed: {response.status_code}")

        payload = response.json()
        if not isinstance(payload, list) or len(payload) < 2:
            raise RuntimeError("Unexpected response format")

        meta, data = payload[0], payload[1]
        if not data:
            break

        all_rows.extend(data)

        pages = meta.get("pages", 1)
        if page >= pages:
            break
        page += 1

    return all_rows


def clean_rows(rows: list[dict]) -> list[dict]:
    cleaned = []
    for row in rows:
        value = row.get("value")
        if value is None:
            continue
        country = (row.get("country") or {}).get("value")
        year_raw = row.get("date")
        if not country or not year_raw:
            continue
        cleaned.append(
            {
                "country": country,
                "year": int(year_raw),
                "value": float(value),
            }
        )
    return cleaned


def aggregate_for_reporting(cleaned: list[dict]) -> dict:
    by_country: dict[str, list[dict]] = {}
    for row in cleaned:
        by_country.setdefault(row["country"], []).append(row)

    country_summaries = []
    latest_values = []
    growth_rates = []

    for country, rows in by_country.items():
        rows_sorted = sorted(rows, key=lambda r: r["year"])
        start_row = rows_sorted[0]
        end_row = rows_sorted[-1]

        start_value = start_row["value"]
        end_value = end_row["value"]
        growth_pct = None
        if start_value != 0:
            growth_pct = ((end_value - start_value) / start_value) * 100.0
            growth_rates.append(growth_pct)

        summary = {
            "country": country,
            "start_year": start_row["year"],
            "end_year": end_row["year"],
            "start_value": round(start_value, 2),
            "latest_value": round(end_value, 2),
            "growth_pct": None if growth_pct is None else round(growth_pct, 2),
        }
        country_summaries.append(summary)
        latest_values.append((country, end_value))

    if not country_summaries:
        raise RuntimeError("no cleaned records")

    highest_country = max(latest_values, key=lambda x: x[1])
    lowest_country = min(latest_values, key=lambda x: x[1])
    avg_growth_pct = None
    if growth_rates:
        avg_growth_pct = sum(growth_rates) / len(growth_rates)

    global_summary = {
        "records": len(cleaned),
        "countries": len(country_summaries),
        "indicator": INDICATOR,
        "date_range": DATE_RANGE,
        "highest_latest_country": highest_country[0],
        "highest_latest_value": round(highest_country[1], 2),
        "lowest_latest_country": lowest_country[0],
        "lowest_latest_value": round(lowest_country[1], 2),
        "average_growth_pct": None if avg_growth_pct is None else round(avg_growth_pct, 2),
        "average_growth_direction": (
            "upward" if avg_growth_pct is not None and avg_growth_pct >= 0 else "downward"
        ),
    }

    return {
        "global_summary": global_summary,
        "country_summaries": sorted(country_summaries, key=lambda x: x["country"]),
    }


def build_prompt(aggregated: dict, version: str = "v3") -> str:
    data_json = json.dumps(aggregated, indent=2)

    prompt_v1 = f"""
You are a data reporter. Summarize the GDP dataset below.

DATA:
{data_json}
""".strip()

    prompt_v2 = f"""
You are a data reporter.
Write:
1) 3-5 bullet insights on trends/patterns.
2) 2 bullet recommendations.
Keep it concise and practical.

DATA:
{data_json}
""".strip()

    prompt_v3 = f"""
You are an economic data reporter writing in English.
Use ONLY the numbers provided in the DATA. Do not invent facts.
If something is missing, say it is unavailable.

Output format (Markdown):
## Executive Summary
2-3 sentences.

## Key Insights
- Provide 3 to 5 bullet points based on the DATA.

## Recommendations
- Provide exactly 2 actionable bullet points.

DATA:
{data_json}
""".strip()

    prompt_map = {"v1": prompt_v1, "v2": prompt_v2, "v3": prompt_v3}
    if version not in prompt_map:
        raise ValueError(f"Unknown prompt version: {version}")
    return prompt_map[version]


def query_ollama(prompt: str) -> tuple[str, str]:
    last_error = None

    for model in MODEL_CANDIDATES:
        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        try:
            print(f"[OLLAMA] trying model={model}")
            response = requests.post(OLLAMA_CHAT_URL, json=body, timeout=120)
            response.raise_for_status()
            payload = response.json()
            content = ((payload.get("message") or {}).get("content") or "").strip()
            if not content:
                raise RuntimeError("Empty model response")
            print(f"[OLLAMA] success model={model}")
            return content, model
        except Exception as exc:  # pylint: disable=broad-except
            last_error = exc
            print(f"[OLLAMA] failed model={model} error={exc}")

    raise RuntimeError(
        "All candidate models failed. Please check `ollama list` and run a model first "
        "(e.g., `ollama run gemma3:latest`)."
    ) from last_error


def markdownish_to_html(text: str) -> str:
    lines = text.splitlines()
    html_parts = []
    in_list = False

    for raw in lines:
        line = raw.strip()
        if not line:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            continue

        if line.startswith("## "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h2>{escape(line[3:])}</h2>")
        elif line.startswith("# "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h1>{escape(line[2:])}</h1>")
        elif line.startswith("- "):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{escape(line[2:])}</li>")
        else:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<p>{escape(line)}</p>")

    if in_list:
        html_parts.append("</ul>")

    return "\n".join(html_parts)


def write_html(report_markdown: str, aggregated: dict, model_used: str) -> None:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_html = markdownish_to_html(report_markdown)

    stats = aggregated["global_summary"]
    header_meta = (
        f"Prompt: {PROMPT_VERSION} | Model: {model_used} | "
        f"Records: {stats['records']} | Generated: {generated_at}"
    )

    html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI GDP Reporter</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 16px; color: #222; }}
    h1 {{ margin-bottom: 8px; }}
    h2 {{ margin-top: 28px; color: #444; }}
    .meta {{ color: #666; font-size: 14px; margin-bottom: 24px; }}
    .card {{ background: #f7f7f8; border: 1px solid #e9e9ea; border-radius: 8px; padding: 12px 14px; }}
    li {{ margin: 6px 0; }}
  </style>
</head>
<body>
  <h1>World Bank GDP AI Report</h1>
  <div class="meta">{escape(header_meta)}</div>
  <div class="card">{report_html}</div>
</body>
</html>
"""
    with open(OUTPUT_HTML, "w", encoding="utf-8") as file:
        file.write(html_document)


def main() -> None:
    try:
        print("[INFO] Starting LAB AI Reporter...")
        url = f"{BASE}/country/{COUNTRIES}/indicator/{INDICATOR}"
        params = {"format": "json", "per_page": PER_PAGE, "date": DATE_RANGE}

        rows = fetch_all_pages(url, params)
        cleaned = clean_rows(rows)
        if not cleaned:
            raise RuntimeError("no cleaned records")

        aggregated = aggregate_for_reporting(cleaned)
        print("[INFO] records:", aggregated["global_summary"]["records"])
        print("[INFO] countries:", aggregated["global_summary"]["countries"])
        print("[INFO] prompt version:", PROMPT_VERSION)

        prompt = build_prompt(aggregated, version=PROMPT_VERSION)
        report_markdown, model_used = query_ollama(prompt)
        write_html(report_markdown, aggregated, model_used)

        print(f"[INFO] saved {OUTPUT_HTML}")
        print("[INFO] Done.")
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
