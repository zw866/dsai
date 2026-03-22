# my_2agent_workflow.py
# Activity 2: A simple 2-agent chain workflow

# 0. SETUP ###################################

import pandas as pd
from functions import agent_run, get_shortages, df_as_text

# Select model
MODEL = "smollm2:1.7b"

# 1. GET DATA ###################################

# Fetch drug shortage data for Oncology category
data = get_shortages(category="Oncology", limit=500)

# Get the most recent record per drug, filter for unavailable ones
stat = (data
        .groupby("generic_name")
        .apply(lambda x: x.loc[x["update_date"].idxmax()])
        .reset_index(drop=True)
        .query("availability == 'Unavailable'"))

# Convert data to text for the agents
raw_text = df_as_text(stat)

# 2. AGENT 1 - Summarizer ###################################
# Takes raw data and produces a summary

role1 = "You are a data summarizer. Given a table of drug shortage data, write a brief 3-5 sentence summary highlighting the key findings: how many drugs are unavailable and which ones."
result1 = agent_run(role=role1, task=raw_text, model=MODEL, output="text")

print("=== Agent 1 (Summarizer) Output ===")
print(result1)
print()

# 3. AGENT 2 - Formatter ###################################
# Takes the summary and produces a formatted email-style report

role2 = "You are a report formatter. Given a summary, format it as a short professional email to a hospital administrator about current drug shortages. Include a subject line and sign off as 'Drug Supply Team'."
result2 = agent_run(role=role2, task=result1, model=MODEL, output="text")

print("=== Agent 2 (Formatter) Output ===")
print(result2)
