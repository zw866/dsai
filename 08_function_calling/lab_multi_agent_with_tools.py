# lab_multi_agent_with_tools.py
# LAB: Multi-Agent System with Tools
# World Bank Economic Data Workflow

# 0. SETUP ###################################

import requests
import json
import pandas as pd

from functions import agent_run, df_as_text

MODEL = "smollm2:1.7b"

# 1. DEFINE TOOL FUNCTION ###################################

def get_world_bank_data(country, indicator):
    """
    Fetch recent economic data from the World Bank API.

    Parameters:
    -----------
    country : str
        ISO 3166-1 alpha-2 country code (e.g., "US", "CN", "JP")
    indicator : str
        World Bank indicator code. Options:
        - "NY.GDP.MKTP.CD" (GDP in current USD)
        - "SP.POP.TOTL" (Total population)
        - "SL.UEM.TOTL.ZS" (Unemployment rate %)
        - "NY.GDP.PCAP.CD" (GDP per capita)

    Returns:
    --------
    pandas.DataFrame
        A DataFrame with columns: year, country, indicator, value
    """
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
    params = {
        "format": "json",
        "per_page": 10,
        "mrv": 10
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if len(data) < 2 or data[1] is None:
        return pd.DataFrame(columns=["year", "country", "indicator", "value"])

    records = []
    for item in data[1]:
        records.append({
            "year": int(item["date"]),
            "country": item["country"]["value"],
            "indicator": item["indicator"]["value"],
            "value": item["value"]
        })

    df = pd.DataFrame(records)
    df = df.dropna(subset=["value"])
    df = df.sort_values("year")
    return df

# 2. DEFINE TOOL METADATA ###################################

tool_get_world_bank_data = {
    "type": "function",
    "function": {
        "name": "get_world_bank_data",
        "description": "Fetch economic data from the World Bank API for a given country and indicator.",
        "parameters": {
            "type": "object",
            "required": ["country", "indicator"],
            "properties": {
                "country": {
                    "type": "string",
                    "description": "ISO country code, e.g. 'US', 'CN', 'JP', 'DE', 'IN', 'GB', 'FR', 'BR', 'CA', 'AU'"
                },
                "indicator": {
                    "type": "string",
                    "description": "World Bank indicator code. Options: 'NY.GDP.MKTP.CD' (GDP), 'SP.POP.TOTL' (Population), 'SL.UEM.TOTL.ZS' (Unemployment), 'NY.GDP.PCAP.CD' (GDP per capita)"
                }
            }
        }
    }
}

# 3. MULTI-AGENT WORKFLOW ###################################

# Agent 1: Data Fetcher (with tool)
# Uses get_world_bank_data to fetch GDP data for China
print("=" * 60)
print("Agent 1: Fetching data...")
print("=" * 60)

role1 = "I fetch economic data from the World Bank API."
task1 = "Get GDP data for China (country code: CN, indicator: NY.GDP.MKTP.CD)"

# Try tool call first; if LLM doesn't call the tool, call it directly
result1 = agent_run(role=role1, task=task1, model=MODEL, output="tools", tools=[tool_get_world_bank_data])

if isinstance(result1, list) and len(result1) > 0 and isinstance(result1[0].get("output"), pd.DataFrame):
    result1_df = result1[0]["output"]
else:
    # Fallback: call the tool directly
    result1_df = get_world_bank_data(country="CN", indicator="NY.GDP.MKTP.CD")

# Convert DataFrame to text for Agent 2
result1_text = df_as_text(result1_df)
print(result1_text)
print()

# Agent 2: Report Writer (no tools)
# Takes the data and writes an analysis report
print("=" * 60)
print("Agent 2: Writing analysis report...")
print("=" * 60)

role2 = "I am an economic analyst. I write brief analysis reports based on data provided."
task2 = f"Analyze the following GDP data for China and write a short report on trends:\n\n{result1_text}"

result2 = agent_run(role=role2, task=task2, model=MODEL, output="text", tools=None)
print(result2)
