# lab_multi_agent.py
# Lab: Design Effective Prompts for Multi-Agent Systems
# A 3-agent workflow for drug shortage analysis and reporting

# 0. SETUP ###################################

import pandas as pd
from functions import agent_run, get_shortages, df_as_text

# Select model
MODEL = "smollm2:1.7b"

# 1. GET DATA ###################################

# Fetch drug shortage data for multiple categories
categories_to_check = ["Oncology", "Psychiatry", "Cardiovascular"]
all_data = []

for cat in categories_to_check:
    try:
        df = get_shortages(category=cat, limit=500)
        df["category"] = cat
        all_data.append(df)
    except Exception as e:
        print(f"Warning: Could not fetch data for {cat}: {e}")

data = pd.concat(all_data, ignore_index=True)

# Get most recent record per drug, filter for unavailable
stat = (data
        .groupby("generic_name")
        .apply(lambda x: x.loc[x["update_date"].idxmax()])
        .reset_index(drop=True)
        .query("availability == 'Unavailable'"))

raw_text = df_as_text(stat)

print("=== Raw Data ===")
print(raw_text)
print()

# 2. AGENT 1 - Data Analyst ###################################
# Analyzes raw shortage data and identifies key patterns

role1 = (
    "You are a pharmaceutical data analyst. "
    "Given a table of drug shortage data, do the following: "
    "1. Count every row in the table to get the total number of unavailable drugs. Count carefully - each row is one drug. "
    "2. List each drug name, its category, and its estimated recovery date. "
    "3. Group the drugs by therapeutic category and count how many are in each category. "
    "Return your analysis as a structured bullet-point list."
)

result1 = agent_run(role=role1, task=raw_text, model=MODEL, output="text")

print("=== Agent 1 (Data Analyst) Output ===")
print(result1)
print()

# 3. AGENT 2 - Risk Assessor ###################################
# Evaluates severity and impact based on the analysis

role2 = (
    "You are a healthcare risk assessor. "
    "Given an analysis of drug shortages, evaluate the risk: "
    "1. Rate the overall severity as Low, Medium, or High. "
    "2. Explain which patient populations are most affected. "
    "3. Suggest 2-3 immediate actions hospitals should take. "
    "Keep your assessment to one paragraph for each point."
)

result2 = agent_run(role=role2, task=result1, model=MODEL, output="text")

print("=== Agent 2 (Risk Assessor) Output ===")
print(result2)
print()

# 4. AGENT 3 - Report Writer ###################################
# Produces a final executive summary combining all findings

role3 = (
    "You are a medical report writer. "
    "Given a risk assessment of drug shortages, write a short executive summary for hospital leadership. "
    "Format: "
    "- Title: 'Drug Shortage Executive Summary' "
    "- Section 1: Current Situation (2-3 sentences) "
    "- Section 2: Risk Level and Impact (2-3 sentences) "
    "- Section 3: Recommended Actions (bullet list) "
    "Keep the total length under 200 words."
)

result3 = agent_run(role=role3, task=result2, model=MODEL, output="text")

print("=== Agent 3 (Report Writer) Output ===")
print(result3)
