"""
02_validator.py

HW3 Step 2: Customized AI report validator (NOT LAB's Likert scales).

Why this is "customized" (per HW3 requirement):
    The LAB's `02_ai_quality_control.py` uses 6 Likert scales (1-5):
    accuracy, formality, faithfulness, clarity, succinctness, relevance.

    For our use case (World Bank GDP reports with strict numerical and
    structural prompt constraints), Likert is the wrong tool because:
      1. Likert can't express "X% of numbers were wrong" - only "feels accurate"
      2. Likert can't capture binary constraint compliance (followed format YES/NO)
      3. Likert is generic; we need numerical-data-specific dimensions

We replace it with 5 task-specific dimensions on heterogeneous scales:

    Dimension                    Scale         Type            Better when...
    -------------------------------------------------------------------------
    1. Numerical Fidelity         0-100        Continuous %    higher
    2. Structural Compliance      0-100        Composite       higher
    3. Hallucination Penalty      0-100        Continuous %    LOWER
    4. Recommendation Actionable  0-10         Integer         higher
    5. Constraint Adherence       0 or 100     Binary          higher

    Composite = mean of (Fidelity, Compliance, 100-Penalty, 10*Actionable, Adherence)
              -> single 0-100 overall score for ANOVA
"""
from __future__ import annotations

import json
import re
from typing import Optional

import requests

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_CHAT_URL = f"{OLLAMA_HOST}/api/chat"
MODEL = "gemma3:latest"


# Source data summary the AI evaluator can cross-check against.
# This is the same World Bank GDP data that all 3 prompts saw.
SOURCE_DATA_DIGEST = """
Source Dataset: World Bank GDP (current US$), indicator NY.GDP.MKTP.CD, 2005-2024.
Countries (5): USA, China, India, Japan, Germany.
Key statements grounded in the data:
- USA had the highest 2024 GDP among the 5; smallest in the set was India.
- All 5 countries showed positive multi-year growth from 2005 to 2024.
- China and India grew at the highest percentage rates over the period.
- Japan and Germany grew at the slowest percentage rates over the period.
The report MUST only use values present in the JSON DATA it was given.
The report should NOT mention indicators other than GDP, currencies other
than current USD, countries other than these 5, or years outside 2005-2024.
"""


VALIDATOR_PROMPT_TEMPLATE = """You are a strict, numbers-focused QA reviewer.
You will evaluate ONE AI-generated economic report on 5 task-specific dimensions.

This is NOT a Likert-scale 1-5 evaluation. Each dimension has its own scale and type.
Read the rubric carefully and return ONLY valid JSON.

============ SOURCE DATA CONTEXT ============
{source_digest}

============ REPORT TO EVALUATE ============
{report}
============================================

Score the report on these 5 dimensions:

1. numerical_fidelity (integer 0-100)
   The percentage of numerical claims in the report that are plausibly supported
   by the source data context. Count every number / year / percentage / country
   ranking the report asserts. Score = 100 * (consistent claims / total claims).
   If no numerical claims at all, give 0.

2. structural_compliance (integer 0-100)
   Composite score:
     +40 if all 3 sections present (Executive Summary, Key Insights, Recommendations)
     +30 if Key Insights has between 3 and 5 bullet points (inclusive)
     +30 if Recommendations has exactly 2 bullet points
   No partial credit per sub-criterion. Total ranges 0, 30, 40, 60, 70, or 100.

3. hallucination_penalty (integer 0-100, LOWER IS BETTER)
   Percentage of substantive factual claims that are NOT grounded in the source
   context (mentions countries/years/indicators outside the dataset, invented
   numbers, made-up policies attributed to data, etc.). If the report is entirely
   grounded, this is 0. If everything is invented, 100.

4. recommendation_actionable (integer 0-10)
   Score the actionability of the report's recommendations on 0-10:
     0 = no recommendations, or pure platitudes
     5 = generic but data-aware ("invest more in X")
     10 = specific, measurable, tied to a concrete data point
   Average if multiple recommendations exist, then round to nearest integer.

5. constraint_adherence (integer, must be 0 or 100)
   Binary: did the writer follow the prompt constraint "use only the numbers
   provided, do not invent facts"?
     100 = no fabricated indicators / countries / years detected
     0   = at least one fabricated factual claim detected
   If the source-prompt did not impose this constraint explicitly, still score
   based on actual fabrication (since all 3 source prompts target the same data).

Also compute:
6. composite_score (float, 0-100)
   = (numerical_fidelity + structural_compliance
      + (100 - hallucination_penalty)
      + (10 * recommendation_actionable)
      + constraint_adherence) / 5

Return JSON in this EXACT structure (no markdown fences, no commentary):
{{
  "numerical_fidelity": 0,
  "structural_compliance": 0,
  "hallucination_penalty": 0,
  "recommendation_actionable": 0,
  "constraint_adherence": 0,
  "composite_score": 0.0,
  "reasoning": "one short sentence justifying the scores"
}}
"""


def build_validator_prompt(report_text: str) -> str:
    return VALIDATOR_PROMPT_TEMPLATE.format(
        source_digest=SOURCE_DATA_DIGEST.strip(),
        report=report_text.strip(),
    )


def _extract_json(text: str) -> Optional[dict]:
    """Try several strategies to pull a JSON object out of the model output."""
    text = text.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        if text.endswith("```"):
            text = text[: -3].strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try greedy first-{...}-last match
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


def _coerce_int(value, lo: int, hi: int, default: int = 0) -> int:
    try:
        v = int(round(float(value)))
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, v))


def validate_report(report_text: str) -> dict:
    """Call the AI validator on one report; return the 5 scores + composite + raw JSON."""
    prompt = build_validator_prompt(report_text)
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.1},  # low temp for stable scoring
        "format": "json",  # Ollama supports JSON-mode
    }
    response = requests.post(OLLAMA_CHAT_URL, json=body, timeout=180)
    response.raise_for_status()
    raw = ((response.json().get("message") or {}).get("content") or "").strip()
    parsed = _extract_json(raw) or {}

    nf = _coerce_int(parsed.get("numerical_fidelity"), 0, 100)
    sc = _coerce_int(parsed.get("structural_compliance"), 0, 100)
    hp = _coerce_int(parsed.get("hallucination_penalty"), 0, 100)
    ra = _coerce_int(parsed.get("recommendation_actionable"), 0, 10)
    ca = _coerce_int(parsed.get("constraint_adherence"), 0, 100)
    if ca not in (0, 100):
        ca = 100 if ca >= 50 else 0

    composite = (nf + sc + (100 - hp) + 10 * ra + ca) / 5.0

    return {
        "numerical_fidelity": nf,
        "structural_compliance": sc,
        "hallucination_penalty": hp,
        "recommendation_actionable": ra,
        "constraint_adherence": ca,
        "composite_score": round(composite, 2),
        "reasoning": str(parsed.get("reasoning", ""))[:240],
        "raw": raw[:500],
    }


# Quick sanity test if run directly
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        sample_path = sys.argv[1]
        with open(sample_path, "r", encoding="utf-8") as f:
            sample = f.read()
        result = validate_report(sample)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        sample = """## Executive Summary
The five tracked economies all grew between 2005 and 2024.

## Key Insights
- USA reached the highest GDP in 2024 among the five.
- China and India had the strongest percentage growth.
- Germany and Japan grew slowly.

## Recommendations
- Stakeholders should monitor China and India as growth leaders.
- Reviewers in Japan and Germany should investigate slow-growth causes.
"""
        print("[demo] validating an in-line sample report...")
        print(json.dumps(validate_report(sample), indent=2, ensure_ascii=False))
