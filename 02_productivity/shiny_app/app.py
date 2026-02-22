# app.py
# World Bank Indicator Explorer – Shiny for Python
# Implements World Bank API query with user-selectable parameters
# Pairs with LAB_cursor_shiny_app.md

import pandas as pd
from shiny import App, Inputs, Outputs, Session, reactive, render, ui

from wb_api import fetch_world_bank_data

# 0. Setup #################################

## 0.1 Constants ############################

# Common indicators: id -> display label
INDICATORS = {
    "NY.GDP.MKTP.CD": "GDP (current US$)",
    "NY.GDP.MKTP.KD.ZG": "GDP growth (annual %)",
    "SP.POP.TOTL": "Population, total",
    "NY.GDP.PCAP.CD": "GDP per capita (current US$)",
    "SL.UEM.TOTL.ZS": "Unemployment, total (% of labor force)",
    "GC.DOD.TOTL.GD.ZS": "Central government debt, total (% of GDP)",
}

# Countries: code -> display label
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

## 0.2 UI ###################################

app_ui = ui.page_fluid(
    # Custom CSS for a clean, modern look
    ui.tags.head(
        ui.tags.style(
            """
            :root { --accent: #0066b3; }
            .navbar { background: linear-gradient(135deg, #005a9e 0%, #0077b6 100%) !important; }
            .btn-primary { background: var(--accent) !important; border-color: var(--accent) !important; }
            .card { border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
            .form-label { font-weight: 500; color: #333; }
            """
        )
    ),
    ui.navset_card_pill(
        ui.nav_panel(
            "Query",
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
                    ui.input_action_button("fetch_btn", "Fetch Data", class_="btn-primary"),
                    width=280,
                ),
                ui.card(
                    ui.card_header("Results"),
                    ui.output_ui("results_ui"),
                    full_screen=True,
                ),
            ),
        ),
        ui.nav_panel(
            "About",
            ui.card(
                ui.card_header("About World Bank Indicator Explorer"),
                ui.markdown(
                    """
                    This app queries the **World Bank Open Data API** for development indicators.
                    Select countries, an indicator, and a date range, then click **Fetch Data**
                    to retrieve and display the data in a sortable, filterable table.

                    - **No API key required** – the World Bank API is free and open.
                    - **Data source**: [World Bank Open Data](https://data.worldbank.org/)
                    - **API docs**: [World Bank API Documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-api-documentation)
                    """
                ),
            ),
        ),
    ),
    title="World Bank Indicator Explorer",
    fillable=True,
)


## 0.3 Server ################################

def server(input: Inputs, output: Outputs, session: Session):
    # Reactive value: None, ("validation", msg), ("error", msg), ("empty", msg), or ("data", df)
    fetch_result = reactive.Value(None)

    @reactive.effect
    @reactive.event(input.fetch_btn)
    def _on_fetch():
        start = input.year_start()
        end = input.year_end()
        if start is None or end is None:
            fetch_result.set(("validation", "Please enter valid start and end years."))
            return
        if start > end:
            fetch_result.set(
                ("validation", "Start year must be less than or equal to end year.")
            )
            return

        sel = input.countries()
        countries = [sel] if isinstance(sel, str) else (list(sel) if sel else [])
        if not countries:
            fetch_result.set(("validation", "Please select at least one country."))
            return

        indicator_id = input.indicator()
        date_range = f"{int(start)}:{int(end)}"

        try:
            rows = fetch_world_bank_data(
                countries=countries,
                indicator_id=indicator_id,
                date_range=date_range,
            )
        except Exception as e:
            fetch_result.set(("error", str(e)))
            return

        if not rows:
            fetch_result.set(
                ("empty", "No data returned. Try a different date range or indicator.")
            )
            return

        df = pd.DataFrame(rows)
        if "value" in df.columns and df["value"].dtype in ["float64", "int64"]:
            df = df.copy()
            df["value"] = df["value"].apply(_format_value)
        fetch_result.set(("data", df))

    @output
    @render.ui
    def results_ui():
        result = fetch_result.get()
        if result is None:
            return ui.div(
                ui.p(
                    "Select parameters and click **Fetch Data** to query the World Bank API.",
                    class_="text-muted",
                ),
                class_="p-3",
            )

        status, payload = result
        if status == "validation":
            return ui.div(
                ui.p(payload, class_="text-warning"),
                class_="p-3",
            )
        if status == "error":
            return ui.div(
                ui.p("An error occurred while fetching data:", class_="text-danger fw-bold"),
                ui.pre(payload, class_="bg-light p-3 rounded mt-2 small"),
                class_="p-3",
            )
        if status == "empty":
            return ui.div(
                ui.p(payload, class_="text-muted"),
                class_="p-3",
            )
        # status == "data"
        return ui.output_data_frame("data_table")

    @output
    @render.data_frame
    def data_table():
        result = fetch_result.get()
        if result is None or result[0] != "data":
            return pd.DataFrame()
        return result[1]


def _format_value(x):
    """Format large numbers with commas and optional billions suffix."""
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
