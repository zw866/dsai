"""
04_statistical_analysis.py

HW3 Step 4: Statistical comparison of prompt performance.

Inputs:
    results/validation_scores.csv

Outputs:
    results/statistical_results.txt   - human-readable summary
    results/statistical_results.json  - machine-readable for docx generator
    results/boxplot_composite.png     - boxplot of composite_score by prompt
    results/boxplot_dimensions.png    - boxplot of every dimension by prompt
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import bartlett, f_oneway, ttest_ind
import pingouin as pg

HERE = Path(__file__).parent
CSV_PATH = HERE / "results" / "validation_scores.csv"
TXT_OUT = HERE / "results" / "statistical_results.txt"
JSON_OUT = HERE / "results" / "statistical_results.json"
BOXPLOT_COMPOSITE = HERE / "results" / "boxplot_composite.png"
BOXPLOT_DIMENSIONS = HERE / "results" / "boxplot_dimensions.png"

DIMENSIONS = [
    "numerical_fidelity",
    "structural_compliance",
    "hallucination_penalty",
    "recommendation_actionable",
    "constraint_adherence",
    "composite_score",
]


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    print(f"[INFO] loaded {len(df)} rows from {CSV_PATH}")
    print(f"[INFO] prompts: {sorted(df['prompt_id'].unique())}")

    lines: list[str] = []
    out: dict = {"n_per_prompt": {}, "summary": {}}

    def emit(s: str) -> None:
        print(s)
        lines.append(s)

    emit("=" * 70)
    emit("HW3 STATISTICAL ANALYSIS  -  Prompt Performance Comparison")
    emit("=" * 70)
    emit("")

    # 1. Descriptive stats
    emit("1. DESCRIPTIVE STATISTICS BY PROMPT")
    emit("-" * 70)
    summary = df.groupby("prompt_id")[DIMENSIONS].agg(["mean", "std", "count"]).round(2)
    emit(summary.to_string())
    emit("")
    for pid in ["A", "B", "C"]:
        sub = df[df["prompt_id"] == pid]
        out["n_per_prompt"][pid] = int(len(sub))
        out["summary"][pid] = {
            d: {
                "mean": float(sub[d].mean()),
                "std": float(sub[d].std()),
                "n": int(sub[d].count()),
            }
            for d in DIMENSIONS
        }

    # 2. Bartlett's test on composite_score
    emit("2. BARTLETT'S TEST FOR HOMOGENEITY OF VARIANCE (composite_score)")
    emit("-" * 70)
    a = df.query("prompt_id == 'A'")["composite_score"].dropna()
    b = df.query("prompt_id == 'B'")["composite_score"].dropna()
    c = df.query("prompt_id == 'C'")["composite_score"].dropna()
    bart_stat, bart_p = bartlett(a, b, c)
    var_equal = bart_p >= 0.05
    emit(f"  Bartlett's test statistic = {bart_stat:.4f}")
    emit(f"  p-value                   = {bart_p:.4f}")
    emit(f"  Equal-variance assumption: {'yes (use standard ANOVA)' if var_equal else 'no (use Welch ANOVA)'}")
    emit("")
    out["bartlett"] = {"statistic": float(bart_stat), "p_value": float(bart_p), "equal_var": bool(var_equal)}

    # 3. Pairwise t-tests on composite_score
    emit("3. PAIRWISE T-TESTS (composite_score)")
    emit("-" * 70)
    pairs = [("A", "B", a, b), ("A", "C", a, c), ("B", "C", b, c)]
    out["t_tests"] = {}
    for (p1, p2, x, y) in pairs:
        t_stat, t_p = ttest_ind(x, y, equal_var=var_equal)
        sig = "***" if t_p < 0.001 else ("**" if t_p < 0.01 else ("*" if t_p < 0.05 else "ns"))
        emit(f"  Prompt {p1} vs {p2}: "
             f"means {x.mean():.2f} vs {y.mean():.2f} | "
             f"t = {t_stat:.3f}, p = {t_p:.4f} {sig}")
        out["t_tests"][f"{p1}_vs_{p2}"] = {
            "mean_1": float(x.mean()), "mean_2": float(y.mean()),
            "t_stat": float(t_stat), "p_value": float(t_p),
        }
    emit("")

    # 4. ANOVA across all three prompts
    emit("4. ONE-WAY ANOVA (composite_score across A, B, C)")
    emit("-" * 70)
    f_stat, f_p = f_oneway(a, b, c)
    sig = "***" if f_p < 0.001 else ("**" if f_p < 0.01 else ("*" if f_p < 0.05 else "ns"))
    emit(f"  F = {f_stat:.3f}, p = {f_p:.4f} {sig}")
    out["anova"] = {"f_stat": float(f_stat), "p_value": float(f_p)}

    # Welch's ANOVA via pingouin (robust to unequal variances)
    try:
        welch = pg.welch_anova(data=df, dv="composite_score", between="prompt_id")
        # pingouin uses "p_unc" (with underscore) in newer versions, "p-unc" (with hyphen) in older.
        p_col = "p_unc" if "p_unc" in welch.columns else "p-unc"
        w_F = float(welch["F"].iloc[0])
        w_p = float(welch[p_col].iloc[0])
        emit(f"  Welch's F = {w_F:.3f}, Welch's p = {w_p:.4f}")
        out["welch_anova"] = {"f_stat": w_F, "p_value": w_p}
    except Exception as exc:
        emit(f"  [warn] Welch's ANOVA failed: {exc}")
    emit("")

    # 4b. Per-dimension ANOVAs - some individual dimensions may show significance
    # even when the composite does not (because the composite averages out the signal).
    emit("4b. PER-DIMENSION ANOVAS (each dimension separately, across A, B, C)")
    emit("-" * 70)
    out["per_dimension_anova"] = {}
    for dim in DIMENSIONS:
        if dim == "composite_score":
            continue  # already done above
        x_a = df.query("prompt_id == 'A'")[dim].dropna()
        x_b = df.query("prompt_id == 'B'")[dim].dropna()
        x_c = df.query("prompt_id == 'C'")[dim].dropna()
        # Skip dimensions with zero variance everywhere (ANOVA undefined)
        if x_a.var() == 0 and x_b.var() == 0 and x_c.var() == 0:
            emit(f"  {dim:30s}  zero variance everywhere - skipped")
            continue
        try:
            d_F, d_p = f_oneway(x_a, x_b, x_c)
            sig = "***" if d_p < 0.001 else ("**" if d_p < 0.01 else ("*" if d_p < 0.05 else "ns"))
            emit(f"  {dim:30s}  F = {d_F:7.3f}, p = {d_p:.4f} {sig}  "
                 f"(means A={x_a.mean():.2f}, B={x_b.mean():.2f}, C={x_c.mean():.2f})")
            out["per_dimension_anova"][dim] = {
                "f_stat": float(d_F), "p_value": float(d_p),
                "mean_A": float(x_a.mean()), "mean_B": float(x_b.mean()), "mean_C": float(x_c.mean()),
            }
        except Exception as exc:
            emit(f"  {dim:30s}  ANOVA failed: {exc}")
    emit("")

    # 5. Tukey HSD post-hoc
    emit("5. TUKEY HSD POST-HOC (composite_score)")
    emit("-" * 70)
    try:
        tukey = pg.pairwise_tukey(data=df, dv="composite_score", between="prompt_id")
        tukey_str = tukey.round(4).to_string(index=False)
        emit(tukey_str)
        out["tukey_hsd"] = tukey.to_dict(orient="records")
    except Exception as exc:
        emit(f"  [warn] Tukey HSD failed: {exc}")
    emit("")

    # 6. Conclusion
    emit("6. CONCLUSION")
    emit("-" * 70)
    means = {pid: float(df.query(f"prompt_id == '{pid}'")["composite_score"].mean()) for pid in ["A", "B", "C"]}
    best_prompt = max(means, key=means.get)
    if f_p < 0.05:
        emit(f"  Composite ANOVA p < 0.05: prompts differ significantly on the composite score.")
        emit(f"  Highest mean composite_score: Prompt {best_prompt} ({means[best_prompt]:.2f}).")
    else:
        emit(f"  Composite ANOVA p >= 0.05: no significant difference on the composite metric.")
        emit(f"  Composite numeric ranking: best mean = Prompt {best_prompt} ({means[best_prompt]:.2f}).")
    emit(f"  Composite means: " + ", ".join(f"{p}={v:.2f}" for p, v in means.items()))
    emit("")

    sig_dims = {d: r for d, r in out.get("per_dimension_anova", {}).items() if r["p_value"] < 0.05}
    if sig_dims:
        emit(f"  Per-dimension findings (p < 0.05 dimensions):")
        for dim, r in sig_dims.items():
            best_d = max(["A", "B", "C"], key=lambda p: r[f"mean_{p}"])
            emit(f"    - {dim}: F={r['f_stat']:.3f}, p={r['p_value']:.4f}; "
                 f"best = Prompt {best_d} (mean={r[f'mean_{best_d}']:.2f})")
    else:
        emit(f"  No individual dimension reached p < 0.05.")
    emit("")
    out["conclusion"] = {
        "means": means,
        "best_prompt": best_prompt,
        "anova_significant_at_0.05": bool(f_p < 0.05),
        "significant_dimensions": list(sig_dims.keys()),
    }

    TXT_OUT.write_text("\n".join(lines), encoding="utf-8")
    JSON_OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\n[saved] {TXT_OUT}")
    print(f"[saved] {JSON_OUT}")

    # 7. Boxplots
    fig, ax = plt.subplots(figsize=(7, 5))
    data_for_plot = [df.query(f"prompt_id == '{p}'")["composite_score"].values for p in ["A", "B", "C"]]
    ax.boxplot(data_for_plot, labels=["Prompt A\n(v1: too broad)",
                                      "Prompt B\n(v2: structured)",
                                      "Prompt C\n(v3: constrained)"])
    ax.set_ylabel("Composite Score (0-100)")
    ax.set_title("HW3 - Composite Validation Score by Prompt")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(BOXPLOT_COMPOSITE, dpi=150)
    plt.close(fig)
    print(f"[saved] {BOXPLOT_COMPOSITE}")

    # All-dimensions panel
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    for ax, dim in zip(axes.flat, DIMENSIONS):
        data_for_plot = [df.query(f"prompt_id == '{p}'")[dim].values for p in ["A", "B", "C"]]
        ax.boxplot(data_for_plot, labels=["A", "B", "C"])
        ax.set_title(dim.replace("_", " "))
        ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.suptitle("HW3 - All 5 Validation Dimensions + Composite by Prompt")
    fig.tight_layout()
    fig.savefig(BOXPLOT_DIMENSIONS, dpi=150)
    plt.close(fig)
    print(f"[saved] {BOXPLOT_DIMENSIONS}")


if __name__ == "__main__":
    main()
