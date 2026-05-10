"""
01_generate_reports.py

HW3 Step 1: Batch-generate AI reports using 3 different prompts.

Reuses the World Bank API + 3 prompt versions (v1/v2/v3) from
03_query_ai/lab_ai_reporter.py (Homework 1).

For each prompt (relabeled A/B/C), generate N reports with
non-zero temperature so we get natural variation across runs.

Output:
    reports/A/report_001.md ... reports/A/report_030.md   (Prompt A = v1)
    reports/B/report_001.md ... reports/B/report_030.md   (Prompt B = v2)
    reports/C/report_001.md ... reports/C/report_030.md   (Prompt C = v3)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

# ---------- Config ----------
BASE = "https://api.worldbank.org/v2"
COUNTRIES = "USA;CHN;IND;JPN;DEU"
INDICATOR = "NY.GDP.MKTP.CD"
DATE_RANGE = "2005:2024"
PER_PAGE = 200

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_CHAT_URL = f"{OLLAMA_HOST}/api/chat"
MODEL = "gemma3:latest"

REPORTS_PER_PROMPT = 30
TEMPERATURE = 0.8  # introduces variation across runs

OUTPUT_ROOT = Path(__file__).parent / "reports"


# ---------- World Bank fetching (copied from lab_ai_reporter.py) ----------
def fetch_all_pages(url: str, params: dict) -> list[dict]:
    all_rows: list[dict] = []
    page = 1
    while True:
        params_with_page = dict(params)
        params_with_page["page"] = page
        response = requests.get(url, params=params_with_page, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"WB request failed: {response.status_code}")
        payload = response.json()
        if not isinstance(payload, list) or len(payload) < 2:
            raise RuntimeError("Unexpected WB response format")
        meta, data = payload[0], payload[1]
        if not data:
            break
        all_rows.extend(data)
        if page >= meta.get("pages", 1):
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
        cleaned.append({"country": country, "year": int(year_raw), "value": float(value)})
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
        start_row, end_row = rows_sorted[0], rows_sorted[-1]
        start_v, end_v = start_row["value"], end_row["value"]
        growth_pct = None
        if start_v != 0:
            growth_pct = ((end_v - start_v) / start_v) * 100.0
            growth_rates.append(growth_pct)
        country_summaries.append({
            "country": country,
            "start_year": start_row["year"],
            "end_year": end_row["year"],
            "start_value": round(start_v, 2),
            "latest_value": round(end_v, 2),
            "growth_pct": None if growth_pct is None else round(growth_pct, 2),
        })
        latest_values.append((country, end_v))

    highest = max(latest_values, key=lambda x: x[1])
    lowest = min(latest_values, key=lambda x: x[1])
    avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else None

    return {
        "global_summary": {
            "records": len(cleaned),
            "countries": len(country_summaries),
            "indicator": INDICATOR,
            "date_range": DATE_RANGE,
            "highest_latest_country": highest[0],
            "highest_latest_value": round(highest[1], 2),
            "lowest_latest_country": lowest[0],
            "lowest_latest_value": round(lowest[1], 2),
            "average_growth_pct": None if avg_growth is None else round(avg_growth, 2),
            "average_growth_direction": (
                "upward" if avg_growth is not None and avg_growth >= 0 else "downward"
            ),
        },
        "country_summaries": sorted(country_summaries, key=lambda x: x["country"]),
    }


# ---------- 3 prompt versions (from lab_ai_reporter.py) ----------
def build_prompt(aggregated: dict, version: str) -> str:
    data_json = json.dumps(aggregated, indent=2)

    prompt_A = f"""
You are a data reporter. Summarize the GDP dataset below.

DATA:
{data_json}
""".strip()

    prompt_B = f"""
You are a data reporter.
Write:
1) 3-5 bullet insights on trends/patterns.
2) 2 bullet recommendations.
Keep it concise and practical.

DATA:
{data_json}
""".strip()

    prompt_C = f"""
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

    return {"A": prompt_A, "B": prompt_B, "C": prompt_C}[version]


# ---------- Ollama call ----------
def query_ollama(prompt: str, temperature: float = TEMPERATURE) -> str:
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": temperature},
    }
    response = requests.post(OLLAMA_CHAT_URL, json=body, timeout=180)
    response.raise_for_status()
    payload = response.json()
    content = ((payload.get("message") or {}).get("content") or "").strip()
    if not content:
        raise RuntimeError("Empty model response")
    return content


# ---------- Main batch loop ----------
def main() -> None:
    print(f"[INFO] Fetching World Bank data from {INDICATOR} for {COUNTRIES}...")
    url = f"{BASE}/country/{COUNTRIES}/indicator/{INDICATOR}"
    params = {"format": "json", "per_page": PER_PAGE, "date": DATE_RANGE}
    rows = fetch_all_pages(url, params)
    cleaned = clean_rows(rows)
    aggregated = aggregate_for_reporting(cleaned)
    print(f"[INFO] Records: {aggregated['global_summary']['records']}, "
          f"Countries: {aggregated['global_summary']['countries']}")

    total_target = REPORTS_PER_PROMPT * 3
    done = 0
    start_time = time.time()

    for prompt_id in ["A", "B", "C"]:
        out_dir = OUTPUT_ROOT / prompt_id
        out_dir.mkdir(parents=True, exist_ok=True)
        prompt_text = build_prompt(aggregated, version=prompt_id)

        for n in range(1, REPORTS_PER_PROMPT + 1):
            done += 1
            out_path = out_dir / f"report_{n:03d}.md"
            if out_path.exists():
                print(f"[SKIP] {out_path.name} (exists)")
                continue
            try:
                print(f"[{done:>3}/{total_target}] generating prompt={prompt_id} run={n} ...", end="", flush=True)
                report = query_ollama(prompt_text)
                out_path.write_text(report, encoding="utf-8")
                elapsed = time.time() - start_time
                avg_time = elapsed / done
                eta_min = avg_time * (total_target - done) / 60.0
                print(f" ok ({len(report)} chars)  [ETA ~{eta_min:.1f} min]")
            except Exception as exc:
                print(f" FAILED: {exc}")
                # Save error placeholder
                out_path.write_text(f"[ERROR] {exc}\n", encoding="utf-8")

    print(f"\n[DONE] generated {done} reports under {OUTPUT_ROOT}")
    print(f"[DONE] total time: {(time.time() - start_time)/60:.1f} minutes")


if __name__ == "__main__":
    main()
