"""
03_run_experiment.py

HW3 Step 3: Run the customized validator on every generated report
and collect scores into a CSV for statistical analysis.

Inputs:
    reports/{A,B,C}/report_NNN.md   -> 30 reports per prompt = 90 total

Output:
    results/validation_scores.csv   -> 90 rows, one per report

CSV columns:
    prompt_id, report_id, file_path,
    numerical_fidelity, structural_compliance, hallucination_penalty,
    recommendation_actionable, constraint_adherence, composite_score,
    reasoning
"""
from __future__ import annotations

import csv
import time
from pathlib import Path

# Local import (this file lives in the same directory as 02_validator.py)
import importlib.util
import sys

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("validator_mod", HERE / "02_validator.py")
validator_mod = importlib.util.module_from_spec(spec)
sys.modules["validator_mod"] = validator_mod
spec.loader.exec_module(validator_mod)
validate_report = validator_mod.validate_report

REPORTS_ROOT = HERE / "reports"
OUTPUT_CSV = HERE / "results" / "validation_scores.csv"

CSV_FIELDS = [
    "prompt_id",
    "report_id",
    "file_path",
    "numerical_fidelity",
    "structural_compliance",
    "hallucination_penalty",
    "recommendation_actionable",
    "constraint_adherence",
    "composite_score",
    "reasoning",
]


def collect_reports() -> list[dict]:
    """Walk reports/{A,B,C}/*.md and return list of {prompt_id, report_id, path}."""
    items: list[dict] = []
    for prompt_id in ["A", "B", "C"]:
        prompt_dir = REPORTS_ROOT / prompt_id
        if not prompt_dir.exists():
            continue
        for path in sorted(prompt_dir.glob("report_*.md")):
            report_id = int(path.stem.split("_")[-1])
            items.append({
                "prompt_id": prompt_id,
                "report_id": report_id,
                "path": path,
            })
    return items


def main() -> None:
    items = collect_reports()
    if not items:
        print("[ERROR] no reports found. Run 01_generate_reports.py first.")
        return

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] validating {len(items)} reports -> {OUTPUT_CSV}")

    start_time = time.time()
    rows: list[dict] = []
    failures = 0

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for idx, item in enumerate(items, 1):
            text = item["path"].read_text(encoding="utf-8").strip()
            print(f"[{idx:>3}/{len(items)}] validating {item['prompt_id']}/"
                  f"report_{item['report_id']:03d} ...", end="", flush=True)

            try:
                scores = validate_report(text)
                row = {
                    "prompt_id": item["prompt_id"],
                    "report_id": item["report_id"],
                    "file_path": str(item["path"].relative_to(HERE)),
                    "numerical_fidelity": scores["numerical_fidelity"],
                    "structural_compliance": scores["structural_compliance"],
                    "hallucination_penalty": scores["hallucination_penalty"],
                    "recommendation_actionable": scores["recommendation_actionable"],
                    "constraint_adherence": scores["constraint_adherence"],
                    "composite_score": scores["composite_score"],
                    "reasoning": scores["reasoning"],
                }
                writer.writerow(row)
                f.flush()  # progress is durable if interrupted
                rows.append(row)
                elapsed = time.time() - start_time
                eta_min = (elapsed / idx) * (len(items) - idx) / 60.0
                print(f" composite={row['composite_score']:.1f}  [ETA ~{eta_min:.1f} min]")
            except Exception as exc:
                failures += 1
                print(f" FAILED: {exc}")

    print(f"\n[DONE] wrote {len(rows)} rows to {OUTPUT_CSV}")
    print(f"[DONE] failures: {failures}")
    print(f"[DONE] total time: {(time.time() - start_time)/60:.1f} minutes")


if __name__ == "__main__":
    main()
