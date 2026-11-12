#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
32_diagnose_greenhouse_models.py

Module 4 — Greenhouse soil–plant experiment.

Diagnostic evaluation of two responses:

Primary:
    soil_biodegradation_pct

Secondary:
    global_bioremediation_pct

Analytical treatments:
    Tes, F, R, T, RT

B is explicitly excluded because atrazine was not added.

Experimental context:
    - Capulin soil
    - 1000 ppm nominal atrazine
    - 40 days
    - n = 3 independent observations per analytical treatment

Treatment interpretation:
    Tes = soil + atrazine, no plant, no inoculation
    F   = soil + atrazine + bean, no inoculation
    R   = soil + atrazine + bean + Rhizobium
    T   = soil + atrazine + bean + Trichoderma
    RT  = soil + atrazine + bean + Rhizobium + Trichoderma

This script performs diagnostics only.
It does NOT run ANOVA, Welch ANOVA, Tukey, or Games-Howell.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from scipy.stats import (
    shapiro,
    levene
)


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

TABLES.mkdir(
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


# ============================================================
# VARIABLES
# ============================================================

treatment_col = "treatment"

responses = [
    "soil_biodegradation_pct",
    "global_bioremediation_pct"
]

required = {
    treatment_col,
    *responses
}

missing = required - set(df.columns)

if missing:
    raise ValueError(
        "Missing required columns: "
        + ", ".join(sorted(missing))
    )


# ============================================================
# VERIFY ANALYTICAL STRUCTURE
# ============================================================

expected_treatments = {
    "Tes",
    "F",
    "R",
    "T",
    "RT"
}

observed_treatments = set(
    df[treatment_col].astype(str)
)

if observed_treatments != expected_treatments:

    raise ValueError(
        "Unexpected analytical treatments.\n"
        f"Expected: {sorted(expected_treatments)}\n"
        f"Found: {sorted(observed_treatments)}"
    )


counts = (
    df[treatment_col]
    .value_counts()
    .sort_index()
)

if not (counts == 3).all():

    raise ValueError(
        "Expected exactly 3 observations per treatment.\n"
        f"{counts}"
    )


if "B" in observed_treatments:

    raise ValueError(
        "Treatment B must not be present in the analytical dataset."
    )


# ============================================================
# DESCRIPTIVE STATISTICS
# ============================================================

descriptive_rows = []


for response in responses:

    summary = (
        df
        .groupby(
            treatment_col
        )[response]
        .agg(
            [
                "count",
                "mean",
                "std",
                "median",
                "min",
                "max"
            ]
        )
        .reset_index()
    )

    for _, row in summary.iterrows():

        descriptive_rows.append(
            {
                "Response": response,
                "Treatment":
                    row[treatment_col],
                "n":
                    int(row["count"]),
                "Mean":
                    row["mean"],
                "SD":
                    row["std"],
                "Median":
                    row["median"],
                "Minimum":
                    row["min"],
                "Maximum":
                    row["max"]
            }
        )


descriptives = pd.DataFrame(
    descriptive_rows
)


# ============================================================
# MODEL DIAGNOSTICS
# ============================================================

diagnostic_rows = []
residual_rows = []


for response in responses:

    formula = (
        f"{response} ~ C({treatment_col})"
    )

    model = smf.ols(
        formula=formula,
        data=df
    ).fit()


    # --------------------------------------------------------
    # Shapiro-Wilk on model residuals
    # --------------------------------------------------------

    shapiro_result = shapiro(
        model.resid
    )


    # --------------------------------------------------------
    # Brown-Forsythe
    # Levene test centered on median
    # --------------------------------------------------------

    groups = [
        group[response].to_numpy(
            dtype=float
        )
        for _, group in df.groupby(
            treatment_col
        )
    ]

    bf_stat, bf_p = levene(
        *groups,
        center="median"
    )


    # --------------------------------------------------------
    # Standardized residuals
    # --------------------------------------------------------

    influence = (
        model.get_influence()
    )

    standardized_residuals = (
        influence.resid_studentized_internal
    )


    diagnostic_rows.append(
        {
            "Response": response,
            "n": int(model.nobs),
            "Residual df":
                int(model.df_resid),
            "Shapiro-Wilk W":
                shapiro_result.statistic,
            "Shapiro-Wilk p":
                shapiro_result.pvalue,
            "Brown-Forsythe statistic":
                bf_stat,
            "Brown-Forsythe p":
                bf_p,
            "|standardized residual| > 2":
                int(
                    np.sum(
                        np.abs(
                            standardized_residuals
                        ) > 2
                    )
                ),
            "|standardized residual| > 3":
                int(
                    np.sum(
                        np.abs(
                            standardized_residuals
                        ) > 3
                    )
                ),
            "Maximum |standardized residual|":
                np.max(
                    np.abs(
                        standardized_residuals
                    )
                )
        }
    )


    # --------------------------------------------------------
    # Save observation-level diagnostics
    # --------------------------------------------------------

    temp = df[
        [
            treatment_col,
            response
        ]
    ].copy()

    temp["Response"] = response

    temp["Fitted value"] = (
        model.fittedvalues.to_numpy()
    )

    temp["Raw residual"] = (
        model.resid.to_numpy()
    )

    temp["Standardized residual"] = (
        standardized_residuals
    )

    temp = temp.rename(
        columns={
            treatment_col:
                "Treatment",
            response:
                "Observed value"
        }
    )

    residual_rows.append(
        temp[
            [
                "Response",
                "Treatment",
                "Observed value",
                "Fitted value",
                "Raw residual",
                "Standardized residual"
            ]
        ]
    )


diagnostics = pd.DataFrame(
    diagnostic_rows
)

residuals = pd.concat(
    residual_rows,
    ignore_index=True
)


# ============================================================
# SAVE TABLES
# ============================================================

descriptives.to_csv(
    TABLES /
    "32_Table10_greenhouse_descriptive_statistics.csv",
    index=False
)

diagnostics.to_csv(
    TABLES /
    "32_Table11_greenhouse_model_diagnostics.csv",
    index=False
)

residuals.to_csv(
    TABLES /
    "32_greenhouse_residual_diagnostics.csv",
    index=False
)


# ============================================================
# TEXT REPORT
# ============================================================

REPORT = (
    TABLES /
    "32_greenhouse_diagnostic_summary.txt"
)

with REPORT.open(
    "w",
    encoding="utf-8"
) as out:

    out.write(
        "=" * 90 + "\n"
    )

    out.write(
        "MODULE 4 — GREENHOUSE MODEL DIAGNOSTICS\n"
    )

    out.write(
        "=" * 90 + "\n\n"
    )

    out.write(
        "ANALYTICAL DESIGN\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        "Treatments: Tes, F, R, T, RT\n"
    )

    out.write(
        "n = 3 independent observations per treatment\n"
    )

    out.write(
        "Total analytical n = 15\n"
    )

    out.write(
        "Treatment B excluded because atrazine was not added.\n\n"
    )

    out.write(
        "DESCRIPTIVE STATISTICS\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        descriptives.to_string(
            index=False
        )
    )

    out.write(
        "\n\nMODEL DIAGNOSTICS\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        diagnostics.to_string(
            index=False
        )
    )

    out.write(
        "\n\nNOTES\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        "1. Diagnostics correspond to separate one-factor "
        "models: response ~ treatment.\n"
    )

    out.write(
        "2. Shapiro-Wilk was applied to model residuals.\n"
    )

    out.write(
        "3. Brown-Forsythe was calculated using median-centered "
        "absolute deviations.\n"
    )

    out.write(
        "4. No inferential treatment comparison is performed "
        "by this script.\n"
    )

    out.write(
        "5. The two original observations using a multiplier "
        "of 4 remain unchanged.\n"
    )


# ============================================================
# TERMINAL
# ============================================================

print("=" * 90)
print(
    "MODULE 4 — GREENHOUSE MODEL DIAGNOSTICS"
)
print("=" * 90)

print("\nAnalytical treatment counts:")
print(
    counts.to_string()
)

print("\nDescriptive statistics:")
print(
    descriptives.to_string(
        index=False
    )
)

print("\nModel diagnostics:")
print(
    diagnostics.to_string(
        index=False
    )
)

print("\nSaved:")
print(
    TABLES /
    "32_Table10_greenhouse_descriptive_statistics.csv"
)
print(
    TABLES /
    "32_Table11_greenhouse_model_diagnostics.csv"
)
print(
    TABLES /
    "32_greenhouse_residual_diagnostics.csv"
)
print(REPORT)
