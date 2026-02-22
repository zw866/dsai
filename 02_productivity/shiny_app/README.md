# World Bank Indicator Explorer

A Shiny for Python app that queries the World Bank Open Data API and displays development indicators in an interactive table. Users select countries, an indicator, and a date range, then click **Fetch Data** to retrieve results.

Pairs with [`LAB_cursor_shiny_app.md`](../LAB_cursor_shiny_app.md) and uses the query logic from [`wb_query.py`](../../01_query_api/wb_query.py).

---

## Overview

The app provides a clean, modern UI for exploring World Bank data. It implements the same API query as the `wb_query.py` script but with:

- Interactive parameter selection (countries, indicator, date range)
- Formatted results table with sorting and filtering
- Graceful error handling for API failures and invalid inputs
- No API key required

---

## Installation

1. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   # If pip is not found: python3 -m pip install -r requirements.txt
   ```

---

## Usage

1. Navigate to the app folder (from project root):

   ```bash
   cd 02_productivity/shiny_app
   # Or from home: cd ~/Desktop/5381/dsai/02_productivity/shiny_app
   ```

2. Run the app:

   ```bash
   shiny run app.py
   # If shiny is not found: python3 -m shiny run app.py
   ```

3. Open the URL shown in the terminal (usually `http://127.0.0.1:8000`) in your browser.

4. Select parameters in the sidebar and click **Fetch Data** to query the World Bank API.

---

## API Requirements

- **No API key required** – the World Bank Open Data API is free and open.
- An internet connection is needed to fetch data.

---

## Project Structure

| File              | Description                                  |
|-------------------|----------------------------------------------|
| `app.py`          | Main Shiny app (UI and server logic)         |
| `wb_api.py`       | Helper module for World Bank API requests    |
| `requirements.txt`| Python dependencies                          |
| `README.md`       | This file                                    |

---

## Notes

- Rate limits apply to the World Bank API; avoid high-frequency polling.
- Some country–indicator–year combinations may return no data.
- Official API docs: [World Bank API Documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-api-documentation).
