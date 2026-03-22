from __future__ import annotations

import json
import re
from datetime import datetime
from html import escape
from pathlib import Path

import pandas as pd
import requests
from shiny import App, Inputs, Outputs, Session, reactive, render, ui

from wb_api import fetch_world_bank_data

INDICATORS = {
    "NY.GDP.MKTP.CD": "GDP (current US$)",
    "NY.GDP.MKTP.KD.ZG": "GDP growth (annual %)",
    "SP.POP.TOTL": "Population, total",
    "NY.GDP.PCAP.CD": "GDP per capita (current US$)",
    "SL.UEM.TOTL.ZS": "Unemployment, total (% of labor force)",
    "GC.DOD.TOTL.GD.ZS": "Central government debt, total (% of GDP)",
}

COUNTRIES = {
    "USA": "United States",
    "CHN": "China",
    "IND": "India",
    "JPN": "Japan",
    "DEU": "Germany",
    "GBR": "United Kingdom",
    "FRA": "France",
    "BRA": "Brazil",
    "CAN": "Canada",
    "AUS": "Australia",
}

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_CANDIDATES = ["gemma3:latest", "smollm2:1.7b"]
PROMPT_VERSION = "v3"
REPORT_PATH = Path(__file__).resolve().parent / "report.html"


def clean_for_report(rows: list[dict]) -> list[dict]:
    cleaned = []
    for row in rows:
        value = row.get("value")
        if value is None:
            continue
        country = row.get("country")
        year_raw = row.get("year")
        if not country or not year_raw:
            continue
        cleaned.append({"country": country, "year": int(year_raw), "value": float(value)})
    return cleaned


def fill_unit_display(df: pd.DataFrame) -> pd.DataFrame:
    if "indicator" not in df.columns:
        return df

    out = df.copy()
    if "unit" not in out.columns:
        out["unit"] = ""

    def _extract_unit(indicator: str, raw_unit: str) -> str:
        if isinstance(raw_unit, str) and raw_unit.strip():
            return raw_unit.strip()
        if not isinstance(indicator, str):
            return ""
        match = re.search(r"\(([^()]*)\)\s*$", indicator)
        if not match:
            return ""
        return match.group(1).strip()

    out["unit_display"] = [
        _extract_unit(ind, unit)
        for ind, unit in zip(out["indicator"], out["unit"])
    ]
    return out


def aggregate_for_reporting(cleaned: list[dict], indicator_id: str, date_range: str) -> dict:
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

        country_summaries.append(
            {
                "country": country,
                "start_year": start_row["year"],
                "end_year": end_row["year"],
                "start_value": round(start_value, 2),
                "latest_value": round(end_value, 2),
                "growth_pct": None if growth_pct is None else round(growth_pct, 2),
            }
        )
        latest_values.append((country, end_value))

    if not country_summaries:
        raise RuntimeError("No cleaned records available for reporting.")

    highest_country = max(latest_values, key=lambda x: x[1])
    lowest_country = min(latest_values, key=lambda x: x[1])
    avg_growth_pct = sum(growth_rates) / len(growth_rates) if growth_rates else None

    global_summary = {
        "records": len(cleaned),
        "countries": len(country_summaries),
        "indicator": indicator_id,
        "date_range": date_range,
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
    if version != "v3":
        raise ValueError(f"Unknown prompt version: {version}")
    return prompt_v3


def query_ollama(prompt: str) -> tuple[str, str]:
    last_error = None
    for model in MODEL_CANDIDATES:
        try:
            body = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}
            response = requests.post(OLLAMA_CHAT_URL, json=body, timeout=120)
            response.raise_for_status()
            payload = response.json()
            content = ((payload.get("message") or {}).get("content") or "").strip()
            if not content:
                raise RuntimeError("Empty model response")
            return content, model
        except Exception as exc:  # pylint: disable=broad-except
            last_error = exc
    raise RuntimeError(
        "All candidate models failed. Start Ollama and ensure one model exists, "
        "for example: `ollama run gemma3:latest`."
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


def write_html(report_markdown: str, aggregated: dict, model_used: str) -> str:
    stats = aggregated["global_summary"]
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_html = markdownish_to_html(report_markdown)
    meta = (
        f"Prompt: {PROMPT_VERSION} | Model: {model_used} | "
        f"Records: {stats['records']} | Generated: {generated_at}"
    )
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>World Bank Live AI Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 980px; margin: 24px auto; padding: 0 16px; color: #222; }}
    .meta {{ color: #666; font-size: 14px; margin-bottom: 18px; }}
    .card {{ background: #f7f7f8; border: 1px solid #e9e9ea; border-radius: 8px; padding: 12px 14px; }}
    h2 {{ margin-top: 24px; }}
  </style>
</head>
<body>
  <h1>World Bank Live AI Report</h1>
  <div class="meta">{escape(meta)}</div>
  <div class="card">{report_html}</div>
</body>
</html>
"""
    REPORT_PATH.write_text(doc, encoding="utf-8")
    return doc


app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.style(
            """
            :root { --accent: #0066b3; }
            .navbar { background: linear-gradient(135deg, #005a9e 0%, #0077b6 100%) !important; }
            .btn-primary { background: var(--accent) !important; border-color: var(--accent) !important; }
            .card { border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
            .form-label { font-weight: 500; color: #333; }
            iframe { width: 100%; min-height: 720px; border: 0; background: #fff; }
            """
        )
    ),
    ui.navset_card_pill(
        ui.nav_panel(
            "Query + Live Report",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.panel_title("Parameters", "⚙️"),
                    ui.input_select(
                        "countries",
                        "Countries",
                        choices=COUNTRIES,
                        selected=["USA", "CHN", "IND", "JPN", "DEU"],
                        multiple=True,
                    ),
                    ui.input_select(
                        "indicator",
                        "Indicator",
                        choices=INDICATORS,
                        selected="NY.GDP.MKTP.CD",
                    ),
                    ui.input_numeric("year_start", "Start Year", value=2005, min=1960, max=2025),
                    ui.input_numeric("year_end", "End Year", value=2024, min=1960, max=2025),
                    ui.input_action_button("fetch_btn", "Fetch Data + Refresh Report", class_="btn-primary"),
                    width=300,
                ),
                ui.card(
                    ui.card_header("Data Results"),
                    ui.output_ui("results_ui"),
                    full_screen=True,
                ),
                ui.card(
                    ui.card_header("AI Report (auto-updated on each fetch)"),
                    ui.output_ui("report_status_ui"),
                    ui.output_ui("report_ui"),
                    full_screen=True,
                ),
            ),
        ),
        ui.nav_panel(
            "About",
            ui.markdown(
                """
This app links the dashboard and AI report in one flow.

- Click **Fetch Data + Refresh Report**
- Data table updates from World Bank API
- AI report is regenerated immediately using current selections
- Latest HTML report is saved to:
  `04_deployment/live_dashboard_report/report.html`
"""
            ),
        ),
    ),
    title="World Bank Dashboard with Live AI Report",
    fillable=True,
)


def server(input: Inputs, output: Outputs, session: Session):
    fetch_result = reactive.Value(None)  # ("kind", payload)
    report_state = reactive.Value(("idle", "Run fetch to generate report."))
    latest_report_html = reactive.Value("")
    current_unit = reactive.Value("")

    @reactive.effect
    @reactive.event(input.fetch_btn)
    def _on_fetch():
        start = input.year_start()
        end = input.year_end()
        if start is None or end is None:
            fetch_result.set(("validation", "Please enter valid start and end years."))
            return
        if start > end:
            fetch_result.set(("validation", "Start year must be less than or equal to end year."))
            return

        sel = input.countries()
        countries = [sel] if isinstance(sel, str) else (list(sel) if sel else [])
        if not countries:
            fetch_result.set(("validation", "Please select at least one country."))
            return

        indicator_id = input.indicator()
        date_range = f"{int(start)}:{int(end)}"

        try:
            rows = fetch_world_bank_data(countries=countries, indicator_id=indicator_id, date_range=date_range)
        except Exception as exc:  # pylint: disable=broad-except
            fetch_result.set(("error", str(exc)))
            report_state.set(("error", f"Data fetch failed: {exc}"))
            return

        if not rows:
            fetch_result.set(("empty", "No data returned. Try a different date range or indicator."))
            report_state.set(("error", "No data returned, report not generated."))
            return

        df = pd.DataFrame(rows)
        df = fill_unit_display(df)
        unit_text = ""
        if "unit_display" in df.columns and not df["unit_display"].empty:
            for val in df["unit_display"]:
                txt = str(val).strip()
                if txt:
                    unit_text = txt
                    break
        current_unit.set(unit_text)

        drop_cols = [col for col in ["unit", "unit_display"] if col in df.columns]
        if drop_cols:
            df = df.drop(columns=drop_cols)

        if "value" in df.columns and df["value"].dtype in ["float64", "int64"]:
            df = df.copy()
            df["value"] = df["value"].apply(_format_value)
        fetch_result.set(("data", df))

        try:
            cleaned = clean_for_report(rows)
            aggregated = aggregate_for_reporting(cleaned, indicator_id=indicator_id, date_range=date_range)
            prompt = build_prompt(aggregated, version=PROMPT_VERSION)
            report_markdown, model_used = query_ollama(prompt)
            html_doc = write_html(report_markdown, aggregated, model_used=model_used)
            latest_report_html.set(html_doc)
            report_state.set(("ok", f"Updated at {datetime.now().strftime('%H:%M:%S')} with model {model_used}"))
        except Exception as exc:  # pylint: disable=broad-except
            report_state.set(("error", f"Report generation failed: {exc}"))

    @output
    @render.ui
    def results_ui():
        result = fetch_result.get()
        if result is None:
            return ui.div("Select parameters and click fetch.", class_="p-3 text-muted")
        kind, payload = result
        if kind == "validation":
            return ui.div(payload, class_="p-3 text-warning")
        if kind == "error":
            return ui.div(ui.p("Data error", class_="fw-bold text-danger"), ui.pre(payload), class_="p-3")
        if kind == "empty":
            return ui.div(payload, class_="p-3 text-muted")
        unit_text = current_unit.get()
        if unit_text:
            return ui.div(
                ui.p(f"Unit: {unit_text}", class_="text-muted mb-2"),
                ui.output_data_frame("data_table"),
            )
        return ui.output_data_frame("data_table")

    @output
    @render.data_frame
    def data_table():
        result = fetch_result.get()
        if result is None or result[0] != "data":
            return pd.DataFrame()
        return result[1]

    @output
    @render.ui
    def report_status_ui():
        kind, message = report_state.get()
        if kind == "ok":
            return ui.div(message, class_="mb-2 text-success")
        if kind == "error":
            return ui.div(message, class_="mb-2 text-danger")
        return ui.div(message, class_="mb-2 text-muted")

    @output
    @render.ui
    def report_ui():
        html_doc = latest_report_html.get()
        if not html_doc:
            return ui.div("No report yet. Fetch data first.", class_="text-muted")
        return ui.tags.iframe(srcdoc=html_doc)


def _format_value(x):
    if x is None or pd.isna(x):
        return ""
    if abs(x) >= 1e12:
        return f"{x / 1e12:,.1f} T"
    if abs(x) >= 1e9:
        return f"{x / 1e9:,.1f} B"
    if abs(x) >= 1e6:
        return f"{x / 1e6:,.1f} M"
    return f"{x:,.2f}"


app = App(app_ui, server)
