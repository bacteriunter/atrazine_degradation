#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
30_leave_one_time_out_cv.py

Module 3 — Temporal atrazine degradation.

Leave-one-time-point-out cross-validation (LOTO-CV)
for continuous temporal models.

Candidate models:
    M1 Linear:
        biodegradation_pct ~ C(treatment) * time_days

    M2 Quadratic:
        biodegradation_pct ~
        C(treatment) * (time_days + I(time_days ** 2))

Validation:
    One complete sampling time is excluded per fold.
    The model is fitted to the remaining three times and
    predicts all 12 independent observations at the excluded time.

Important:
- Experimental units are independent destructive samples.
- No nominal t=0 observation is introduced.
- M3 categorical-time model is not evaluated because it cannot
  predict a temporal category absent from the training data.
- No new model family is introduced at this checkpoint.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
)


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

TABLES.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT)

if len(df) != 48:
    raise ValueError(
        f"Expected 48 observations; found {len(df)}."
    )


required = {
    "treatment",
    "time_days",
    "biodegradation_pct",
}

missing = required - set(df.columns)

if missing:
    raise ValueError(
        "Missing required columns: "
        + ", ".join(sorted(missing))
    )


times = sorted(
    df["time_days"].unique()
)

expected_times = [5, 10, 20, 40]

if times != expected_times:
    raise ValueError(
        f"Expected times {expected_times}; found {times}."
    )


# ============================================================
# MODELS
# ============================================================

models = {
    "M1_linear":
        "biodegradation_pct ~ "
        "C(treatment) * time_days",

    "M2_quadratic":
        "biodegradation_pct ~ "
        "C(treatment) * "
        "(time_days + I(time_days ** 2))",
}


# ============================================================
# CROSS-VALIDATION
# ============================================================

prediction_rows = []
fold_rows = []


for model_name, formula in models.items():

    for excluded_time in times:

        train = df.loc[
            df["time_days"] != excluded_time
        ].copy()

        test = df.loc[
            df["time_days"] == excluded_time
        ].copy()

        if len(train) != 36:
            raise ValueError(
                f"{model_name}, excluded {excluded_time}: "
                f"expected 36 training observations; "
                f"found {len(train)}."
            )

        if len(test) != 12:
            raise ValueError(
                f"{model_name}, excluded {excluded_time}: "
                f"expected 12 test observations; "
                f"found {len(test)}."
            )

        fit = smf.ols(
            formula=formula,
            data=train
        ).fit()

        predicted = fit.predict(test)

        observed = (
            test["biodegradation_pct"]
            .to_numpy(dtype=float)
        )

        predicted_array = (
            predicted.to_numpy(dtype=float)
        )

        residuals = (
            observed - predicted_array
        )

        rmse = np.sqrt(
            mean_squared_error(
                observed,
                predicted_array
            )
        )

        mae = mean_absolute_error(
            observed,
            predicted_array
        )

        bias = np.mean(
            predicted_array - observed
        )

        fold_type = (
            "Interpolation"
            if excluded_time in [10, 20]
            else "Extrapolation"
        )

        fold_rows.append(
            {
                "Model": model_name,
                "Excluded time (days)": excluded_time,
                "Validation type": fold_type,
                "Training n": len(train),
                "Test n": len(test),
                "RMSE": rmse,
                "MAE": mae,
                "Mean prediction bias": bias,
            }
        )

        test_reset = test.reset_index(drop=True)

        for i in range(len(test_reset)):

            prediction_rows.append(
                {
                    "Model": model_name,
                    "Excluded time (days)":
                        excluded_time,
                    "Validation type":
                        fold_type,
                    "Treatment":
                        test_reset.loc[
                            i,
                            "treatment"
                        ],
                    "Observed biodegradation (%)":
                        observed[i],
                    "Predicted biodegradation (%)":
                        predicted_array[i],
                    "Residual (observed - predicted)":
                        residuals[i],
                }
            )


# ============================================================
# DATA FRAMES
# ============================================================

fold_results = pd.DataFrame(
    fold_rows
)

predictions = pd.DataFrame(
    prediction_rows
)


# ============================================================
# OVERALL PERFORMANCE
# ============================================================

overall_rows = []

for model_name in models:

    d = predictions.loc[
        predictions["Model"] == model_name
    ].copy()

    obs = d[
        "Observed biodegradation (%)"
    ].to_numpy()

    pred = d[
        "Predicted biodegradation (%)"
    ].to_numpy()

    overall_rows.append(
        {
            "Model": model_name,
            "n predictions": len(d),
            "LOTO-CV RMSE":
                np.sqrt(
                    mean_squared_error(
                        obs,
                        pred
                    )
                ),
            "LOTO-CV MAE":
                mean_absolute_error(
                    obs,
                    pred
                ),
            "Mean prediction bias":
                np.mean(pred - obs),
        }
    )


overall = pd.DataFrame(
    overall_rows
)


# ============================================================
# INTERPOLATION VS EXTRAPOLATION
# ============================================================

type_rows = []

for model_name in models:

    for validation_type in [
        "Interpolation",
        "Extrapolation"
    ]:

        d = predictions.loc[
            (predictions["Model"] == model_name)
            &
            (
                predictions["Validation type"]
                == validation_type
            )
        ].copy()

        obs = d[
            "Observed biodegradation (%)"
        ].to_numpy()

        pred = d[
            "Predicted biodegradation (%)"
        ].to_numpy()

        type_rows.append(
            {
                "Model": model_name,
                "Validation type":
                    validation_type,
                "n predictions": len(d),
                "RMSE":
                    np.sqrt(
                        mean_squared_error(
                            obs,
                            pred
                        )
                    ),
                "MAE":
                    mean_absolute_error(
                        obs,
                        pred
                    ),
                "Mean prediction bias":
                    np.mean(pred - obs),
            }
        )


by_type = pd.DataFrame(
    type_rows
)


# ============================================================
# SAVE
# ============================================================

fold_results.to_csv(
    TABLES /
    "30_Table6_leave_one_time_out_by_fold.csv",
    index=False
)

overall.to_csv(
    TABLES /
    "30_Table7_leave_one_time_out_overall.csv",
    index=False
)

by_type.to_csv(
    TABLES /
    "30_TableS2_interpolation_extrapolation.csv",
    index=False
)

predictions.to_csv(
    TABLES /
    "30_leave_one_time_out_predictions.csv",
    index=False
)


# ============================================================
# REPORT
# ============================================================

REPORT = (
    TABLES /
    "30_leave_one_time_out_summary.txt"
)

with REPORT.open(
    "w",
    encoding="utf-8"
) as out:

    out.write(
        "=" * 90 + "\n"
    )

    out.write(
        "MODULE 3 — LEAVE-ONE-TIME-POINT-OUT "
        "CROSS-VALIDATION\n"
    )

    out.write(
        "=" * 90 + "\n\n"
    )

    out.write(
        "PERFORMANCE BY EXCLUDED TIME\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        fold_results.to_string(
            index=False
        )
    )

    out.write(
        "\n\nOVERALL PERFORMANCE\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        overall.to_string(
            index=False
        )
    )

    out.write(
        "\n\nINTERPOLATION VS EXTRAPOLATION\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        by_type.to_string(
            index=False
        )
    )

    out.write(
        "\n\nINTERPRETATION NOTES\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        "1. Each fold excludes one complete experimental "
        "sampling time.\n"
    )

    out.write(
        "2. Excluding 10 or 20 days evaluates temporal "
        "interpolation.\n"
    )

    out.write(
        "3. Excluding 5 or 40 days evaluates temporal "
        "extrapolation relative to the training range.\n"
    )

    out.write(
        "4. M3 categorical-time reference model is not "
        "eligible for this validation because an unseen "
        "time category cannot be predicted.\n"
    )

    out.write(
        "5. No nominal t=0 observation was introduced.\n"
    )


# ============================================================
# TERMINAL OUTPUT
# ============================================================

print("=" * 90)
print(
    "MODULE 3 — LEAVE-ONE-TIME-POINT-OUT CROSS-VALIDATION"
)
print("=" * 90)

print("\nPerformance by excluded time:")
print(
    fold_results.to_string(
        index=False
    )
)

print("\nOverall performance:")
print(
    overall.to_string(
        index=False
    )
)

print("\nInterpolation vs extrapolation:")
print(
    by_type.to_string(
        index=False
    )
)

print("\nSaved:")
print(
    TABLES /
    "30_Table6_leave_one_time_out_by_fold.csv"
)
print(
    TABLES /
    "30_Table7_leave_one_time_out_overall.csv"
)
print(
    TABLES /
    "30_TableS2_interpolation_extrapolation.csv"
)
print(
    TABLES /
    "30_leave_one_time_out_predictions.csv"
)
print(REPORT)
