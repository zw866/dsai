# Homework 3 — AI Report Validation System

Module 11 deliverable that builds on Module 9 (LAB_ai_quality_control).
Validates the GDP reports my Homework 1 reporter produces, comparing 3 prompt
variants (A/B/C) using a customized 5-dimension rubric and ANOVA.

---

## Contents

```
homework3/
├── 01_generate_reports.py        # Batch-generate 30×3 = 90 reports via Ollama
├── 02_validator.py               # Customized AI validator (5 task-specific dimensions)
├── 03_run_experiment.py          # Score every report, write CSV
├── 04_statistical_analysis.py    # Bartlett + t-test + ANOVA + Tukey + boxplots
├── 05_build_docx.py              # Assemble final HW3 .docx deliverable
├── reports/{A,B,C}/report_NNN.md # 90 generated reports
└── results/
    ├── validation_scores.csv     # 90 rows, 6 score columns
    ├── statistical_results.txt   # Human-readable stats summary
    ├── statistical_results.json  # Same numbers, machine-readable
    ├── boxplot_composite.png     # Composite-score boxplot
    └── boxplot_dimensions.png    # All-dimension boxplot panel
```

---

## Run order

Prerequisites:
- Python 3.11+
- Ollama running locally (`http://localhost:11434`) with `gemma3:latest` pulled
- `pip install requests pandas scipy pingouin matplotlib python-docx`

```bash
cd 11_decision_support/homework3

# 1) Generate 90 reports (3 prompts × 30 each).  ~30 min on Ollama gemma3:latest.
python3 01_generate_reports.py

# 2) Score all 90 reports with the customized validator.  ~25 min.
python3 03_run_experiment.py

# 3) Run statistics and produce boxplots.  ~5 seconds.
python3 04_statistical_analysis.py

# 4) Assemble homework3_DRAFT.docx.  ~2 seconds.
python3 05_build_docx.py
```

---

## Customized validation rubric (5 dimensions, NOT LAB Likert)

| Dimension                  | Scale     | Type           | Direction |
|----------------------------|-----------|----------------|-----------|
| Numerical Fidelity         | 0-100     | Continuous %   | higher ✅ |
| Structural Compliance      | 0-100     | 40+30+30 add.  | higher ✅ |
| Hallucination Penalty      | 0-100     | Continuous %   | LOWER ✅  |
| Recommendation Actionable  | 0-10      | Integer        | higher ✅ |
| Constraint Adherence       | 0 or 100  | Binary         | higher ✅ |
| **Composite Score**        | 0-100     | Derived avg    | higher ✅ |

Composite = `(Fidelity + Compliance + (100 - Penalty) + 10*Actionable + Adherence) / 5`

### Why this differs from the Module 9 LAB

The LAB uses six 1-5 Likert scales (accuracy, formality, faithfulness, clarity,
succinctness, relevance). Likert can't express:
- Binary constraint compliance (did the model follow 'use only the numbers I gave you'?)
- Continuous numerical-claim accuracy (87% of numbers match the source)
- Negative-direction dimensions (hallucination — higher is worse)

So I replaced it with task-specific dimensions on heterogeneous scales.

---

## Three prompts compared

Taken directly from my Homework 1 prompt iteration in
[`03_query_ai/lab_ai_reporter.py`](../../03_query_ai/lab_ai_reporter.py):

| ID | HW1 label | Description                                                        |
|----|-----------|--------------------------------------------------------------------|
| A  | v1        | Terse: "summarize the GDP dataset below"                           |
| B  | v2        | Structured: 3-5 insights + 2 recommendations                       |
| C  | v3        | Constrained: required sections + bullet counts + "do not invent"  |

30 reports per prompt × 3 prompts = 90 total reports.

---

## Statistical tests

- **Bartlett's test** for homogeneity of variance (decides standard vs Welch ANOVA)
- **3 pairwise t-tests** (A vs B, A vs C, B vs C) on `composite_score`
- **One-way ANOVA** across A/B/C
- **Welch's ANOVA** as robustness check
- **Per-dimension ANOVAs** (each dimension tested separately)
- **Tukey HSD post-hoc** to identify which pairs differ significantly

Hypothesis: H0 = mean composite scores are equal across prompts; H1 = at least one differs.
