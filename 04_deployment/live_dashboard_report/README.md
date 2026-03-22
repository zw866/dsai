# Live Dashboard + AI Report

This app links dashboard fetch and AI report generation in one place.

## What it does

- Query World Bank data with user-selected countries, indicator, and year range.
- Refresh the data table when you click fetch.
- Regenerate AI report immediately after each fetch.
- Save latest report to `04_deployment/live_dashboard_report/report.html`.

## Run

```bash
cd /Users/jackwen/Desktop/5381/dsai/04_deployment/live_dashboard_report
python3 -m pip install -r requirements.txt
python3 -m shiny run app.py --port 8002
```

Open:

`http://127.0.0.1:8002`

## Notes

- Requires local Ollama running at `http://localhost:11434`.
- Model fallback: `gemma3:latest`, `smollm2:1.7b`.
