# 02_ai_quality_control.py
# AI-Assisted Text Quality Control
# Tim Fraser

# This script demonstrates how to use AI (Ollama or OpenAI) to perform quality control
# on AI-generated text reports. It implements quality control criteria including
# boolean accuracy checks and Likert scales for multiple quality dimensions.
# Students learn to design quality control prompts and structure AI outputs as JSON.

# 0. Setup #################################

## 0.1 Load Packages #################################

# If you haven't already, install required packages:
# pip install pandas requests python-dotenv

import pandas as pd  # for data wrangling
import re  # for text processing
import requests  # for HTTP requests
import json  # for JSON operations
import os  # for environment variables

try:
    from dotenv import load_dotenv  # for loading .env file
except ImportError:
    def load_dotenv():
        return False

## 0.2 Configuration #################################

# Choose your AI provider: "ollama" or "openai"
AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")

# Ollama configuration
PORT = 11434
OLLAMA_HOST = f"http://localhost:{PORT}"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:latest")

# OpenAI configuration
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"  # Low-cost model

## 0.3 Load Sample Data #################################

# Load sample report text for quality control
with open("09_text_analysis/data/sample_reports.txt", "r", encoding="utf-8") as f:
    sample_text = f.read()

# Split text into individual reports
reports = [r.strip() for r in sample_text.split("\n\n") if r.strip()]
report = reports[0]

source_df = pd.read_csv("09_text_analysis/data/sample_data.csv")


def format_source_data(df):
    metadata = df.iloc[0][["county", "state", "year", "pollutant", "metric"]]
    header = (
        f"{metadata['county']}, {metadata['state']} | "
        f"{metadata['year']} | {metadata['pollutant']} | {metadata['metric']}"
    )
    table_rows = ["type | label_value | label_percent", "--- | --- | ---"]
    for _, row in df[["type", "label_value", "label_percent"]].iterrows():
        table_rows.append(f"{row['type']} | {row['label_value']} | {row['label_percent']}")
    data_table = "\n".join(table_rows)
    return f"{header}\n{data_table}"


source_data = format_source_data(source_df)

print("📝 Report for Quality Control:")
print("---")
print(report)
print("---\n")

# 1. AI Quality Control Function #################################

## 1.1 Create Quality Control Prompt #################################

def create_quality_control_prompt(report_text, source_data=None, prompt_version="refined"):
    instructions = (
        "You are a meticulous quality control validator for AI-generated policy reports. "
        "Evaluate the report using the supplied source data and return only valid JSON."
    )

    data_context = ""
    if source_data is not None:
        data_context = f"\n\nSource Data:\n{source_data}\n"

    if prompt_version == "baseline":
        criteria = """

Quality Control Criteria:

1. accurate (boolean): TRUE only if the report does not misinterpret the supplied data.
2. accuracy (1-5): 1 = many interpretation errors, 5 = no interpretation errors.
3. formality (1-5): 1 = casual writing, 5 = professional government-report style.
4. faithfulness (1-5): 1 = unsupported claims, 5 = claims directly grounded in the data.
5. clarity (1-5): 1 = confusing, 5 = clear and precise.
6. succinctness (1-5): 1 = wordy, 5 = concise.
7. relevance (1-5): 1 = irrelevant commentary, 5 = fully relevant commentary.

Return JSON in this exact structure:
{
  "accurate": true,
  "accuracy": 1,
  "formality": 1,
  "faithfulness": 1,
  "clarity": 1,
  "succinctness": 1,
  "relevance": 1,
  "details": "brief explanation"
}
"""
    else:
        criteria = """

Quality Control Criteria:

Score every dimension with whole numbers from 1 to 5.

1. accurate (boolean)
- TRUE only if every numerical claim, comparison, and recommendation is consistent with the source data.
- FALSE if there is any fabrication, incorrect percentage, incorrect ranking, or unsupported causal claim.

2. accuracy (1-5)
- 5 = all claims match the data exactly
- 4 = mostly correct with only minor imprecision
- 3 = mixed accuracy with noticeable issues
- 2 = several factual or interpretive mistakes
- 1 = major misinterpretation of the data

3. formality (1-5)
- 5 = professional, neutral, report-style language
- 3 = somewhat conversational but acceptable
- 1 = casual, dramatic, or colloquial language

4. faithfulness (1-5)
- 5 = conclusions stay close to the data and avoid exaggeration
- 3 = some extrapolation beyond the data
- 1 = grandiose or unsupported claims

5. clarity (1-5)
- 5 = easy to follow, specific, and precise
- 3 = understandable but somewhat vague
- 1 = confusing, fragmented, or imprecise

6. succinctness (1-5)
- 5 = concise with little redundancy
- 3 = somewhat repetitive or padded
- 1 = very wordy or repetitive

7. relevance (1-5)
- 5 = all content is directly tied to the data and task
- 3 = some generic commentary
- 1 = mostly off-topic or weakly connected to the data

Additional rules:
- Use the source data as the authority for factual evaluation.
- Penalize unsupported urgency words such as "critical," "obviously," or "absolutely."
- Penalize vague recommendations that do not clearly connect back to the emissions pattern.
- In "details", explain the strongest reason for the score in 35 words or fewer.

Return JSON in this exact structure:
{
  "accurate": true,
  "accuracy": 1,
  "formality": 1,
  "faithfulness": 1,
  "clarity": 1,
  "succinctness": 1,
  "relevance": 1,
  "details": "brief explanation"
}
"""

    return f"{instructions}{data_context}\n\nReport Text to Validate:\n{report_text}\n{criteria}"

## 1.2 Query AI Function #################################

# Function to query AI and get quality control results
def query_ai_quality_control(prompt, provider=AI_PROVIDER):
    if provider == "ollama":
        # Query Ollama
        url = f"{OLLAMA_HOST}/api/chat"
        
        body = {
            "model": OLLAMA_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "format": "json",  # Request JSON output
            "stream": False
        }
        
        response = requests.post(url, json=body)
        response.raise_for_status()
        response_data = response.json()
        output = response_data["message"]["content"]
        
    elif provider == "openai":
        # Query OpenAI
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in .env file. Please set it up first.")
        
        url = "https://api.openai.com/v1/chat/completions"
        
        body = {
            "model": OPENAI_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a quality control validator. Always return your responses as valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "response_format": {"type": "json_object"},  # Request JSON output
            "temperature": 0.3  # Lower temperature for more consistent validation
        }
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        response_data = response.json()
        output = response_data["choices"][0]["message"]["content"]
        
    else:
        raise ValueError("Invalid provider. Use 'ollama' or 'openai'.")
    
    return output

## 1.3 Parse Quality Control Results #################################

# Parse JSON response and convert to DataFrame
EXPECTED_FIELDS = [
    "accurate",
    "accuracy",
    "formality",
    "faithfulness",
    "clarity",
    "succinctness",
    "relevance",
    "details",
]


def parse_quality_control_results(json_response):
    # Try to parse JSON
    # Sometimes AI returns text with JSON, so we extract JSON if needed
    json_match = re.search(r"\{.*\}", json_response, re.DOTALL)
    if json_match:
        json_response = json_match.group(0)
    
    # Parse JSON
    quality_data = json.loads(json_response)

    missing_fields = [field for field in EXPECTED_FIELDS if field not in quality_data]
    if missing_fields:
        raise ValueError(f"Missing expected fields: {missing_fields}")

    numeric_fields = [
        "accuracy",
        "formality",
        "faithfulness",
        "clarity",
        "succinctness",
        "relevance",
    ]
    for field in numeric_fields:
        quality_data[field] = int(quality_data[field])
        if quality_data[field] < 1 or quality_data[field] > 5:
            raise ValueError(f"{field} must be between 1 and 5")

    quality_data["accurate"] = bool(quality_data["accurate"])
    quality_data["details"] = str(quality_data["details"]).strip()

    results = pd.DataFrame([{field: quality_data[field] for field in EXPECTED_FIELDS}])

    return results


def add_overall_score(results_df):
    likert_columns = [
        "accuracy",
        "formality",
        "faithfulness",
        "clarity",
        "succinctness",
        "relevance",
    ]
    results_df = results_df.copy()
    results_df["overall_score"] = results_df[likert_columns].mean(axis=1).round(2)
    return results_df


def manual_quality_snapshot(report_text):
    has_numbers = bool(re.search(r"\d+", report_text))
    has_percentages = bool(re.search(r"\d+%", report_text))
    has_recommendations = bool(re.search(r"recommend|suggest|should|must", report_text, re.IGNORECASE))
    has_hyperbole = bool(re.search(r"crucial|critical|extremely|absolutely", report_text, re.IGNORECASE))
    has_belittling = bool(re.search(r"it is clear that|obviously|as you can see", report_text, re.IGNORECASE))
    sentence_count = len(re.findall(r"[.!?]+", report_text))
    word_count = len(report_text.split())

    return pd.DataFrame({
        "word_count": [word_count],
        "sentence_count": [sentence_count],
        "has_numbers": [has_numbers],
        "has_percentages": [has_percentages],
        "has_recommendations": [has_recommendations],
        "has_hyperbole": [has_hyperbole],
        "has_belittling": [has_belittling],
    })


def print_submission_summary(label, results_df, prompt_version):
    row = results_df.iloc[0]
    print(f"=== {label} ({prompt_version} prompt) ===")
    print(results_df.to_string(index=False))
    print(
        f"\nOverall score: {row['overall_score']:.2f} / 5.00"
        f"\nAccuracy check: {'PASS' if row['accurate'] else 'FAIL'}"
        f"\nExplanation: {row['details']}\n"
    )


def compare_prompt_versions(report_text, source_data=None):
    comparison_rows = []

    for version in ["baseline", "refined"]:
        prompt = create_quality_control_prompt(report_text, source_data, prompt_version=version)
        response = query_ai_quality_control(prompt, provider=AI_PROVIDER)
        parsed = add_overall_score(parse_quality_control_results(response))
        parsed["prompt_version"] = version
        comparison_rows.append(parsed)

    return pd.concat(comparison_rows, ignore_index=True)

# 2. Run Quality Control #################################

## 2.1 Create Quality Control Prompt #################################

quality_prompt = create_quality_control_prompt(report, source_data, prompt_version="refined")

print("🤖 Querying AI for quality control with the refined prompt...\n")

ai_response = query_ai_quality_control(quality_prompt, provider=AI_PROVIDER)

print("📥 AI Response (raw JSON):")
print(ai_response)
print()

quality_results = add_overall_score(parse_quality_control_results(ai_response))
print_submission_summary("Quality Control Results", quality_results, "refined")

print("📋 Manual Quality Snapshot:")
print(manual_quality_snapshot(report).to_string(index=False))
print()

print("🔁 Comparing baseline prompt vs refined prompt...\n")
prompt_comparison = compare_prompt_versions(report, source_data)
comparison_view = prompt_comparison[
    [
        "prompt_version",
        "accurate",
        "accuracy",
        "formality",
        "faithfulness",
        "clarity",
        "succinctness",
        "relevance",
        "overall_score",
    ]
]
print(comparison_view.to_string(index=False))
print()

baseline_score = prompt_comparison.loc[
    prompt_comparison["prompt_version"] == "baseline", "overall_score"
].iloc[0]
refined_score = prompt_comparison.loc[
    prompt_comparison["prompt_version"] == "refined", "overall_score"
].iloc[0]

print("🧾 Submission Notes Draft:")
print(
    "- The refined prompt uses explicit scoring anchors and penalizes vague or exaggerated language.\n"
    "- The AI quality control system evaluates nuanced traits such as faithfulness, formality, and clarity that manual keyword checks cannot score directly.\n"
    f"- In this run, the refined prompt changed the overall score by {refined_score - baseline_score:+.2f} points relative to the baseline prompt.\n"
    "- Manual quality control is still useful for fast pattern checks, but AI quality control provides a richer judgment about whether the writing is accurate and professionally written.\n"
)

# 3. Quality Control Multiple Reports #################################

## 3.1 Batch Quality Control Function #################################

# Function to check multiple reports
def check_multiple_reports(reports, source_data=None, prompt_version="refined"):
    print(f"🔄 Performing quality control on {len(reports)} reports...\n")
    
    all_results = []
    
    for i, report_text in enumerate(reports, 1):
        print(f"Checking report {i} of {len(reports)}...")
        
        # Create prompt
        prompt = create_quality_control_prompt(report_text, source_data, prompt_version=prompt_version)
        
        # Query AI
        try:
            response = query_ai_quality_control(prompt, provider=AI_PROVIDER)
            results = add_overall_score(parse_quality_control_results(response))
            results["report_id"] = i
            all_results.append(results)
        except Exception as e:
            print(f"❌ Error checking report {i}: {e}")
        
        # Small delay to avoid rate limiting
        import time
        time.sleep(1)
    
    # Combine all results
    if all_results:
        combined_results = pd.concat(all_results, ignore_index=True)
        return combined_results
    else:
        return pd.DataFrame()

## 3.2 Run Batch Quality Control (Optional) #################################

# Uncomment to check all reports
# if len(reports) > 1:
#     batch_results = check_multiple_reports(reports, source_data)
#     print("\n📊 Batch Quality Control Results:")
#     print(batch_results)

print("✅ AI quality control complete!")
print("💡 Compare these results with manual quality control (01_manual_quality_control.py) to see how AI performs.")
