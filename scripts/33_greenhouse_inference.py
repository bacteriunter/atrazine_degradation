#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
33_greenhouse_inference.py

Module 4 — Greenhouse soil–plant experiment.

Inferential analyses for:

Primary response:
    soil_biodegradation_pct

Secondary response:
    global_bioremediation_pct

Analytical treatments:
    Tes, F, R, T, RT

Analyses:
    1. One-way ANOVA
    2. Tukey HSD for all pairwise comparisons
    3. Four pre-specified planned contrasts:
           F  - Tes
           R  - F
           T  - F
           RT - F
       with Holm adjustment across the four planned contrasts.

Treatment B is excluded because atrazine was not added.

No observations are removed.
The two original observations using a multiplier of 4 remain unchanged.
"""

from pathlib import Path

import numpy as np
import pandas as pd

import statsmodels.api as sm
import statsmodels.formula.api as smf

from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.multitest import multipletests
from scipy.stats import t as t_dist


# ============================================================
# PATHS
# ============================================================

PROJECT = Path(__file__).resolve().parents[1]

INPUT = (
    PROJECT
    / "data"
    / "processed"
    / "greenhouse_degradation_analysis.csv"
)

TABLES = PROJECT / "results" / "tables"
MODELS = PROJECT / "results" / "models"

TABLES.mkdir(
    parents=True,
    exist_ok=True
)

MODELS.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT)

if len(df) != 15:
    raise ValueError(
        f"Expected 15 analytical observations; found {len(df)}."
    )


responses = [
    "soil_biodegradation_pct",
    "global_bioremediation_pct"
]

expected_treatments = [
    "Tes",
    "F",
    "R",
    "T",
    "RT"
]


required = {
    "treatment",
    *responses
}

missing = required - set(df.columns)

if missing:
    raise ValueError(
        "Missing required columns: "
        + ", ".join(sorted(missing))
    )


observed_treatments = set(
    df["treatment"].astype(str)
)

if observed_treatments != set(expected_treatments):
    raise ValueError(
        "Unexpected treatment structure.\n"
        f"Expected: {expected_treatments}\n"
        f"Found: {sorted(observed_treatments)}"
    )


counts = (
    df["treatment"]
    .value_counts()
)

if not (counts == 3).all():
    raise ValueError(
        "Expected exactly 3 observations per treatment."
    )


# ============================================================
# PLANNED CONTRASTS
# ============================================================

# Direction is always:
# second treatment minus first treatment

planned_contrasts = [
    ("F - Tes", "Tes", "F"),
    ("R - F", "F", "R"),
    ("T - F", "F", "T"),
    ("RT - F", "F", "RT"),
]


# ============================================================
# STORAGE
# ============================================================

anova_rows = []
tukey_frames = []
contrast_frames = []


# ============================================================
# ANALYSIS
# ============================================================

for response in responses:

    # --------------------------------------------------------
    # ONE-WAY MODEL
    # --------------------------------------------------------

    formula = (
        f"{response} ~ C(treatment)"
    )

    model = smf.ols(
        formula=formula,
        data=df
    ).fit()


    # --------------------------------------------------------
    # ANOVA
    # --------------------------------------------------------

    anova = anova_lm(
        model,
        typ=2
    )

    treatment_row = (
        anova.loc["C(treatment)"]
    )

    residual_row = (
        anova.loc["Residual"]
    )

    ss_treatment = float(
        treatment_row["sum_sq"]
    )

    ss_residual = float(
        residual_row["sum_sq"]
    )

    eta_squared = (
        ss_treatment
        /
        (ss_treatment + ss_residual)
    )


    anova_rows.append(
        {
            "Response": response,
            "Treatment df":
                int(treatment_row["df"]),
            "Residual df":
                int(residual_row["df"]),
            "Treatment SS":
                ss_treatment,
            "Residual SS":
                ss_residual,
            "F":
                float(treatment_row["F"]),
            "p":
                float(treatment_row["PR(>F)"]),
            "Eta squared":
                eta_squared
        }
    )


    # --------------------------------------------------------
    # TUKEY HSD
    # --------------------------------------------------------

    tukey = pairwise_tukeyhsd(
        endog=df[response],
        groups=df["treatment"],
        alpha=0.05
    )

    tukey_table = pd.DataFrame(
        data=tukey._results_table.data[1:],
        columns=tukey._results_table.data[0]
    )

    tukey_table.insert(
        0,
        "Response",
        response
    )

    tukey_frames.append(
        tukey_table
    )


    # --------------------------------------------------------
    # PLANNED CONTRASTS
    #
    # Because the design is balanced, each treatment mean
    # contains n = 3 observations.
    #
    # Standard error of difference:
    #
    # sqrt(MSE * (1/n1 + 1/n2))
    #
    # The common residual MSE and df come from the one-way
    # ANOVA model.
    # --------------------------------------------------------

    mse = (
        ss_residual
        / float(residual_row["df"])
    )

    residual_df = int(
        residual_row["df"]
    )

    treatment_means = (
        df
        .groupby("treatment")[response]
        .mean()
    )

    treatment_n = (
        df
        .groupby("treatment")[response]
        .count()
    )


    contrast_rows = []

    for (
        contrast_name,
        reference,
        comparison
    ) in planned_contrasts:

        mean_reference = float(
            treatment_means.loc[
                reference
            ]
        )

        mean_comparison = float(
            treatment_means.loc[
                comparison
            ]
        )

        n_reference = int(
            treatment_n.loc[
                reference
            ]
        )

        n_comparison = int(
            treatment_n.loc[
                comparison
            ]
        )

        difference = (
            mean_comparison
            - mean_reference
        )

        se = np.sqrt(
            mse
            * (
                1 / n_reference
                + 1 / n_comparison
            )
        )

        t_value = (
            difference / se
        )


        # Two-sided p-value using model residual df
        p_raw = (
            2
            * t_dist.sf(
                np.abs(t_value),
                df=residual_df
            )
        )


        # 95% CI
        t_critical = (
            t_dist.ppf(
                0.975,
                df=residual_df
            )
        )

        ci_lower = (
            difference
            - t_critical * se
        )

        ci_upper = (
            difference
            + t_critical * se
        )


        contrast_rows.append(
            {
                "Response":
                    response,
                "Contrast":
                    contrast_name,
                "Reference treatment":
                    reference,
                "Comparison treatment":
                    comparison,
                "Reference mean":
                    mean_reference,
                "Comparison mean":
                    mean_comparison,
                "Mean difference":
                    difference,
                "SE":
                    se,
                "t":
                    t_value,
                "Residual df":
                    residual_df,
                "Raw p":
                    p_raw,
                "CI lower 95%":
                    ci_lower,
                "CI upper 95%":
                    ci_upper
            }
        )


    contrast_df = pd.DataFrame(
        contrast_rows
    )


    # --------------------------------------------------------
    # HOLM ADJUSTMENT
    # Applied only across the four pre-specified contrasts
    # within this response.
    # --------------------------------------------------------

    reject, p_holm, _, _ = (
        multipletests(
            contrast_df["Raw p"],
            alpha=0.05,
            method="holm"
        )
    )

    contrast_df[
        "Holm-adjusted p"
    ] = p_holm

    contrast_df[
        "Significant after Holm"
    ] = reject

    contrast_frames.append(
        contrast_df
    )


    # --------------------------------------------------------
    # SAVE MODEL SUMMARY
    # --------------------------------------------------------

    with (
        MODELS /
        f"33_{response}_oneway_model_summary.txt"
    ).open(
        "w",
        encoding="utf-8"
    ) as out:

        out.write(
            model.summary().as_text()
        )


# ============================================================
# COMBINE TABLES
# ============================================================

anova_results = pd.DataFrame(
    anova_rows
)

tukey_results = pd.concat(
    tukey_frames,
    ignore_index=True
)

contrast_results = pd.concat(
    contrast_frames,
    ignore_index=True
)


# ============================================================
# SAVE
# ============================================================

anova_results.to_csv(
    TABLES /
    "33_Table12_greenhouse_ANOVA.csv",
    index=False
)

tukey_results.to_csv(
    TABLES /
    "33_Table13_greenhouse_Tukey.csv",
    index=False
)

contrast_results.to_csv(
    TABLES /
    "33_Table14_greenhouse_planned_contrasts.csv",
    index=False
)


# ============================================================
# REPORT
# ============================================================

REPORT = (
    TABLES /
    "33_greenhouse_inference_summary.txt"
)

with REPORT.open(
    "w",
    encoding="utf-8"
) as out:

    out.write(
        "=" * 90 + "\n"
    )

    out.write(
        "MODULE 4 — GREENHOUSE INFERENTIAL ANALYSIS\n"
    )

    out.write(
        "=" * 90 + "\n\n"
    )

    out.write(
        "ONE-WAY ANOVA\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        anova_results.to_string(
            index=False
        )
    )

    out.write(
        "\n\nTUKEY HSD\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        tukey_results.to_string(
            index=False
        )
    )

    out.write(
        "\n\nPLANNED CONTRASTS\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        contrast_results.to_string(
            index=False
        )
    )

    out.write(
        "\n\nANALYTICAL NOTES\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        "1. Treatment B was excluded because atrazine "
        "was not added.\n"
    )

    out.write(
        "2. Separate one-way ANOVAs were fitted for soil "
        "biodegradation and global bioremediation.\n"
    )

    out.write(
        "3. Tukey HSD controls family-wise error across "
        "all pairwise treatment comparisons within each "
        "response.\n"
    )

    out.write(
        "4. Four pre-specified contrasts were evaluated "
        "within each response: F-Tes, R-F, T-F, and RT-F.\n"
    )

    out.write(
        "5. Holm correction was applied across the four "
        "planned contrasts within each response.\n"
    )

    out.write(
        "6. Positive planned-contrast differences indicate "
        "a higher response in the second treatment named "
        "in each comparison.\n"
    )

    out.write(
        "7. The two original observations using a multiplier "
        "of 4 remain unchanged.\n"
    )


# ============================================================
# TERMINAL
# ============================================================

print("=" * 90)
print(
    "MODULE 4 — GREENHOUSE INFERENTIAL ANALYSIS"
)
print("=" * 90)

print("\nOne-way ANOVA:")
print(
    anova_results.to_string(
        index=False
    )
)

print("\nTukey HSD:")
print(
    tukey_results.to_string(
        index=False
    )
)

print("\nPlanned contrasts:")
print(
    contrast_results.to_string(
        index=False
    )
)

print("\nSaved:")
print(
    TABLES /
    "33_Table12_greenhouse_ANOVA.csv"
)
print(
    TABLES /
    "33_Table13_greenhouse_Tukey.csv"
)
print(
    TABLES /
    "33_Table14_greenhouse_planned_contrasts.csv"
)
print(REPORT)
