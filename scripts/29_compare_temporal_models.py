#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
29_compare_temporal_models.py

Module 3 — Temporal atrazine degradation.

Comparison of parsimonious temporal models using the 48
independent laboratory observations.

Response:
    biodegradation_pct

Candidate models:
    M1 Linear time
    M2 Quadratic time
    M3 Categorical time reference

Model comparison:
    AIC
    AICc
    RMSE
    MAE
    LOOCV RMSE
    LOOCV MAE

Important:
- Each row is an independent destructive experimental unit.
- No nominal t=0 observation is added.
- The 500 ppm initial concentration is NOT treated as an
  experimentally measured HPLC observation.
- No first-order or monotonic kinetic behavior is imposed.
- M3 is an observed-time reference model, not an interpolation model.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import mean_squared_error, mean_absolute_error


# ============================================================
# PATHS
# ============================================================

PROJECT = Path(__file__).resolve().parents[1]

INPUT = (
    PROJECT
    / "data"
    / "processed"
    / "lab_degradation_analysis.csv"
)

TABLES = PROJECT / "results" / "tables"
MODELS = PROJECT / "results" / "models"

TABLES.mkdir(parents=True, exist_ok=True)
MODELS.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT)

if len(df) != 48:
    raise ValueError(
        f"Expected 48 analytical observations; found {len(df)}."
    )


# ============================================================
# REQUIRED VARIABLES
# ============================================================

required = {
    "treatment",
    "time_days",
    "biodegradation_pct"
}

missing = required - set(df.columns)

if missing:
    raise ValueError(
        "Missing required columns: "
        + ", ".join(sorted(missing))
    )


# Explicit categorical time variable
df["time_factor"] = df["time_days"].astype(str)


# ============================================================
# CANDIDATE MODELS
# ============================================================

models = {
    "M1_linear":
        "biodegradation_pct ~ C(treatment) * time_days",

    "M2_quadratic":
        "biodegradation_pct ~ "
        "C(treatment) * (time_days + I(time_days ** 2))",

    "M3_categorical_reference":
        "biodegradation_pct ~ "
        "C(treatment) * C(time_factor)",
}


# ============================================================
# FUNCTIONS
# ============================================================

def aicc(model):

    n = int(model.nobs)
    k = int(model.df_model) + 1

    denominator = n - k - 1

    if denominator <= 0:
        return np.nan

    return (
        model.aic
        + (2 * k * (k + 1))
        / denominator
    )


def loocv_predictions(data, formula):

    loo = LeaveOneOut()

    observed = []
    predicted = []

    for train_index, test_index in loo.split(data):

        train = data.iloc[train_index].copy()
        test = data.iloc[test_index].copy()

        model = smf.ols(
            formula=formula,
            data=train
        ).fit()

        pred = model.predict(test)

        observed.append(
            float(test["biodegradation_pct"].iloc[0])
        )

        predicted.append(
            float(pred.iloc[0])
        )

    return (
        np.asarray(observed),
        np.asarray(predicted)
    )


# ============================================================
# FIT AND COMPARE
# ============================================================

comparison_rows = []

fitted_models = {}

for model_name, formula in models.items():

    fit = smf.ols(
        formula=formula,
        data=df
    ).fit()

    fitted_models[model_name] = fit

    fitted = fit.predict(df)

    rmse = np.sqrt(
        mean_squared_error(
            df["biodegradation_pct"],
            fitted
        )
    )

    mae = mean_absolute_error(
        df["biodegradation_pct"],
        fitted
    )

    observed_cv, predicted_cv = loocv_predictions(
        df,
        formula
    )

    cv_rmse = np.sqrt(
        mean_squared_error(
            observed_cv,
            predicted_cv
        )
    )

    cv_mae = mean_absolute_error(
        observed_cv,
        predicted_cv
    )

    comparison_rows.append(
        {
            "Model": model_name,
            "Formula": formula,
            "n": int(fit.nobs),
            "Parameters": int(fit.df_model) + 1,
            "R2": fit.rsquared,
            "Adjusted R2": fit.rsquared_adj,
            "AIC": fit.aic,
            "AICc": aicc(fit),
            "RMSE": rmse,
            "MAE": mae,
            "LOOCV RMSE": cv_rmse,
            "LOOCV MAE": cv_mae,
        }
    )


comparison = pd.DataFrame(
    comparison_rows
)

comparison = comparison.sort_values(
    ["LOOCV RMSE", "AICc"],
    ascending=True
).reset_index(drop=True)


# ============================================================
# DELTA AICc
# ============================================================

comparison["Delta AICc"] = (
    comparison["AICc"]
    - comparison["AICc"].min()
)


# ============================================================
# SAVE TABLE
# ============================================================

comparison.to_csv(
    TABLES /
    "29_Table5_temporal_model_comparison.csv",
    index=False
)


# ============================================================
# SAVE MODEL SUMMARIES
# ============================================================

for model_name, fit in fitted_models.items():

    output = (
        MODELS /
        f"29_{model_name}_summary.txt"
    )

    with output.open(
        "w",
        encoding="utf-8"
    ) as handle:

        handle.write(
            fit.summary().as_text()
        )


# ============================================================
# REPORT
# ============================================================

report = (
    TABLES /
    "29_temporal_model_comparison_summary.txt"
)

with report.open(
    "w",
    encoding="utf-8"
) as out:

    out.write(
        "=" * 90 + "\n"
    )

    out.write(
        "MODULE 3 — TEMPORAL MODEL COMPARISON\n"
    )

    out.write(
        "=" * 90 + "\n\n"
    )

    out.write(
        comparison.to_string(
            index=False
        )
    )

    out.write(
        "\n\nMODEL ROLES\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        "M1: continuous linear temporal model.\n"
    )

    out.write(
        "M2: continuous quadratic temporal model.\n"
    )

    out.write(
        "M3: categorical-time reference model restricted "
        "to the observed sampling times.\n"
    )

    out.write(
        "\nNo nominal t=0 observation was included.\n"
    )

    out.write(
        "No monotonic kinetic model was imposed.\n"
    )


# ============================================================
# TERMINAL
# ============================================================

print("=" * 90)
print("MODULE 3 — TEMPORAL MODEL COMPARISON")
print("=" * 90)

print(
    comparison.to_string(
        index=False
    )
)

print("\nSaved:")
print(
    TABLES /
    "29_Table5_temporal_model_comparison.csv"
)
print(report)

for model_name in models:
    print(
        MODELS /
        f"29_{model_name}_summary.txt"
    )
