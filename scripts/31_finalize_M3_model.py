#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
31_finalize_M3_model.py

Module 3 — Final categorical treatment × time model.

Final model:
    biodegradation_pct ~ C(treatment) * C(time_factor)

Scope:
    Prediction is restricted to the experimentally observed
    treatment × time combinations:
        Treatments: Te, R, T, RT
        Times: 5, 10, 20, 40 days

Outputs:
    - Final model metrics
    - Observed and model-estimated values with 95% CI
    - LOOCV predictions
    - Manuscript-ready figures

Important:
    - No nominal t=0 observation is introduced.
    - No prediction is made for unobserved sampling times.
    - Experimental units are independent destructive samples.
    - Manuscript-facing outputs are in English.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error
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
FIGURES = PROJECT / "results" / "figures"
MODELS = PROJECT / "results" / "models"

TABLES.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)
MODELS.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATA
# ============================================================

df = pd.read_csv(INPUT)

if len(df) != 48:
    raise ValueError(
        f"Expected 48 observations; found {len(df)}."
    )

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


treatment_order = ["Te", "R", "T", "RT"]
time_order = [5, 10, 20, 40]

df["time_factor"] = df["time_days"].astype(str)


# ============================================================
# FINAL MODEL
# ============================================================

formula = (
    "biodegradation_pct ~ "
    "C(treatment) * C(time_factor)"
)

model = smf.ols(
    formula=formula,
    data=df
).fit()


# ============================================================
# MODEL METRICS
# ============================================================

fitted = model.predict(df)

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


# AICc
n = int(model.nobs)
k = int(model.df_model) + 1

aicc = (
    model.aic
    + (2 * k * (k + 1))
    / (n - k - 1)
)


# ============================================================
# PREDICTION GRID
# Only experimentally observed combinations
# ============================================================

grid = pd.DataFrame(
    [
        {
            "treatment": treatment,
            "time_days": time,
            "time_factor": str(time)
        }
        for treatment in treatment_order
        for time in time_order
    ]
)


prediction = model.get_prediction(
    grid
).summary_frame(
    alpha=0.05
)


grid["Predicted biodegradation (%)"] = (
    prediction["mean"].to_numpy()
)

grid["Mean CI lower 95%"] = (
    prediction["mean_ci_lower"].to_numpy()
)

grid["Mean CI upper 95%"] = (
    prediction["mean_ci_upper"].to_numpy()
)


# ============================================================
# OBSERVED SUMMARY
# ============================================================

observed = (
    df
    .groupby(
        ["treatment", "time_days"],
        as_index=False
    )
    .agg(
        n=("biodegradation_pct", "count"),
        observed_mean=(
            "biodegradation_pct",
            "mean"
        ),
        observed_sd=(
            "biodegradation_pct",
            "std"
        ),
        observed_min=(
            "biodegradation_pct",
            "min"
        ),
        observed_max=(
            "biodegradation_pct",
            "max"
        )
    )
)


table8 = grid.merge(
    observed,
    on=["treatment", "time_days"],
    how="left"
)


table8 = table8[
    [
        "treatment",
        "time_days",
        "n",
        "observed_mean",
        "observed_sd",
        "Predicted biodegradation (%)",
        "Mean CI lower 95%",
        "Mean CI upper 95%",
        "observed_min",
        "observed_max",
    ]
].copy()


table8 = table8.rename(
    columns={
        "treatment": "Treatment",
        "time_days": "Time (days)",
        "n": "n",
        "observed_mean":
            "Observed mean biodegradation (%)",
        "observed_sd":
            "Observed SD",
        "observed_min":
            "Observed minimum (%)",
        "observed_max":
            "Observed maximum (%)",
    }
)


table8.to_csv(
    TABLES /
    "31_Table8_M3_observed_predicted.csv",
    index=False
)


# ============================================================
# LOOCV FOR FINAL M3
# ============================================================

loo = LeaveOneOut()

cv_rows = []

for train_index, test_index in loo.split(df):

    train = df.iloc[
        train_index
    ].copy()

    test = df.iloc[
        test_index
    ].copy()

    cv_model = smf.ols(
        formula=formula,
        data=train
    ).fit()

    pred = float(
        cv_model.predict(test).iloc[0]
    )

    obs = float(
        test["biodegradation_pct"].iloc[0]
    )

    cv_rows.append(
        {
            "Treatment":
                test["treatment"].iloc[0],
            "Time (days)":
                test["time_days"].iloc[0],
            "Observed biodegradation (%)":
                obs,
            "LOOCV predicted biodegradation (%)":
                pred,
            "Residual (observed - predicted)":
                obs - pred
        }
    )


cv = pd.DataFrame(
    cv_rows
)


cv_rmse = np.sqrt(
    mean_squared_error(
        cv["Observed biodegradation (%)"],
        cv[
            "LOOCV predicted biodegradation (%)"
        ]
    )
)

cv_mae = mean_absolute_error(
    cv["Observed biodegradation (%)"],
    cv[
        "LOOCV predicted biodegradation (%)"
    ]
)


cv.to_csv(
    TABLES /
    "31_TableS3_M3_LOOCV_predictions.csv",
    index=False
)


# ============================================================
# FINAL METRICS TABLE
# ============================================================

metrics = pd.DataFrame(
    [
        {
            "Model":
                "Treatment × categorical time",
            "n": n,
            "Parameters": k,
            "R2": model.rsquared,
            "Adjusted R2":
                model.rsquared_adj,
            "AIC":
                model.aic,
            "AICc":
                aicc,
            "In-sample RMSE":
                rmse,
            "In-sample MAE":
                mae,
            "LOOCV RMSE":
                cv_rmse,
            "LOOCV MAE":
                cv_mae,
            "Prediction domain":
                "Te/R/T/RT at 5, 10, 20, and 40 days"
        }
    ]
)


metrics.to_csv(
    TABLES /
    "31_Table9_M3_performance.csv",
    index=False
)


# ============================================================
# SAVE MODEL SUMMARY
# ============================================================

with (
    MODELS /
    "31_M3_final_model_summary.txt"
).open(
    "w",
    encoding="utf-8"
) as out:

    out.write(
        model.summary().as_text()
    )


# ============================================================
# FIGURE 6
# Individual observations + final M3 estimates
# ============================================================

fig, ax = plt.subplots(
    figsize=(8.2, 5.8)
)

colors = {
    "Te": "tab:blue",
    "R": "tab:orange",
    "T": "tab:green",
    "RT": "tab:red"
}

markers = {
    "Te": "o",
    "R": "s",
    "T": "^",
    "RT": "D"
}

offsets = {
    "Te": -0.6,
    "R": -0.2,
    "T": 0.2,
    "RT": 0.6
}

for treatment in treatment_order:

    color = colors[treatment]
    marker = markers[treatment]

    # --------------------------------------------------------
    # Individual experimental observations
    # --------------------------------------------------------

    d = df.loc[
        df["treatment"] == treatment
    ].copy()

    ax.scatter(
        d["time_days"].to_numpy(dtype=float)
        + offsets[treatment],
        d["biodegradation_pct"],
        s=28,
        marker=marker,
        facecolor=color,
        edgecolor=color,
        alpha=0.28,
        zorder=2
    )

    # --------------------------------------------------------
    # M3 estimated means and 95% CI
    # --------------------------------------------------------

    pred = table8.loc[
        table8["Treatment"] == treatment
    ].sort_values(
        "Time (days)"
    )

    x = pred[
        "Time (days)"
    ].to_numpy(dtype=float)

    y = pred[
        "Predicted biodegradation (%)"
    ].to_numpy(dtype=float)

    lower = pred[
        "Mean CI lower 95%"
    ].to_numpy(dtype=float)

    upper = pred[
        "Mean CI upper 95%"
    ].to_numpy(dtype=float)

    ax.fill_between(
        x,
        lower,
        upper,
        color=color,
        alpha=0.10,
        linewidth=0,
        zorder=1
    )

    ax.plot(
        x,
        y,
        color=color,
        marker=marker,
        markersize=7,
        linewidth=1.8,
        label=treatment,
        zorder=4
    )


ax.set_xticks(
    time_order
)

ax.set_xlabel(
    "Time (days)"
)

ax.set_ylabel(
    "Atrazine biodegradation (%)"
)

ax.set_title(
    "Model-estimated atrazine biodegradation within the experimental domain"
)

ax.legend(
    title="Treatment",
    frameon=False,
    ncol=4
)

ax.grid(
    axis="y",
    alpha=0.20
)

fig.tight_layout()

fig.savefig(
    FIGURES /
    "31_figure6_M3_observed_predicted.png",
    dpi=300,
    bbox_inches="tight"
)

fig.savefig(
    FIGURES /
    "31_figure6_M3_observed_predicted.pdf",
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# FIGURE 7
# Observed vs LOOCV predicted
# ============================================================

fig, ax = plt.subplots(
    figsize=(6.2, 6.0)
)


for treatment in treatment_order:

    d = cv.loc[
        cv["Treatment"] == treatment
    ]

    ax.scatter(
        d[
            "Observed biodegradation (%)"
        ],
        d[
            "LOOCV predicted biodegradation (%)"
        ],
        marker=markers[treatment],
        s=55,
        alpha=0.75,
        label=treatment
    )


all_values = np.concatenate(
    [
        cv[
            "Observed biodegradation (%)"
        ].to_numpy(),
        cv[
            "LOOCV predicted biodegradation (%)"
        ].to_numpy()
    ]
)

low = min(
    0,
    np.floor(all_values.min() / 10) * 10
)

high = max(
    100,
    np.ceil(all_values.max() / 10) * 10
)


ax.plot(
    [low, high],
    [low, high],
    linestyle="--",
    linewidth=1
)

ax.set_xlim(
    low,
    high
)

ax.set_ylim(
    low,
    high
)

ax.set_aspect(
    "equal",
    adjustable="box"
)

ax.set_xlabel(
    "Observed biodegradation (%)"
)

ax.set_ylabel(
    "LOOCV-predicted biodegradation (%)"
)

ax.set_title(
    "Cross-validated prediction within the experimental domain"
)

ax.legend(
    title="Treatment",
    frameon=False
)

ax.grid(
    alpha=0.20
)

fig.tight_layout()

fig.savefig(
    FIGURES /
    "31_figure7_M3_LOOCV_observed_vs_predicted.png",
    dpi=300,
    bbox_inches="tight"
)

fig.savefig(
    FIGURES /
    "31_figure7_M3_LOOCV_observed_vs_predicted.pdf",
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# FINAL REPORT
# ============================================================

REPORT = (
    TABLES /
    "31_M3_final_results_summary.txt"
)

with REPORT.open(
    "w",
    encoding="utf-8"
) as out:

    out.write(
        "=" * 90 + "\n"
    )

    out.write(
        "MODULE 3 — FINAL M3 MODEL\n"
    )

    out.write(
        "=" * 90 + "\n\n"
    )

    out.write(
        "FINAL MODEL\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        "biodegradation_pct ~ "
        "C(treatment) * C(time_factor)\n\n"
    )

    out.write(
        metrics.to_string(
            index=False
        )
    )

    out.write(
        "\n\nOBSERVED AND MODEL-ESTIMATED VALUES\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        table8.to_string(
            index=False
        )
    )

    out.write(
        "\n\nINTERPRETATION LIMITS\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        "1. Predictions are restricted to experimentally "
        "observed treatment × time combinations.\n"
    )

    out.write(
        "2. The model does not support prediction at "
        "unobserved sampling times.\n"
    )

    out.write(
        "3. The nominal 500 ppm initial concentration is "
        "not treated as an observed t=0 HPLC measurement.\n"
    )

    out.write(
        "4. LOOCV evaluates prediction of an independent "
        "experimental unit while retaining other replicates "
        "from the same treatment × time combination.\n"
    )

    out.write(
        "5. Leave-one-time-point-out validation showed "
        "poor generalization of continuous linear and "
        "quadratic temporal models to unseen times.\n"
    )


# ============================================================
# TERMINAL
# ============================================================

print("=" * 90)
print("MODULE 3 — FINAL M3 MODEL COMPLETED")
print("=" * 90)

print("\nFinal model performance:")
print(
    metrics.to_string(
        index=False
    )
)

print("\nObserved and predicted values:")
print(
    table8.to_string(
        index=False
    )
)

print("\nSaved:")
print(
    TABLES /
    "31_Table8_M3_observed_predicted.csv"
)
print(
    TABLES /
    "31_Table9_M3_performance.csv"
)
print(
    TABLES /
    "31_TableS3_M3_LOOCV_predictions.csv"
)
print(
    FIGURES /
    "31_figure6_M3_observed_predicted.png"
)
print(
    FIGURES /
    "31_figure7_M3_LOOCV_observed_vs_predicted.png"
)
print(REPORT)
