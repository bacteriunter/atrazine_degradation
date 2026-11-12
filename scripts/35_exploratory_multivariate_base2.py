#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
35_exploratory_multivariate_base2.py

Exploratory multivariate analysis of Base 2.

Analyses:
1. Standardized PCA.
2. Explained variance and PCA loadings.
3. PCA scores for all 31 microorganisms.
4. Spearman correlation matrix.
5. Spearman p-value matrix.

IMPORTANT:
- Exploratory analysis only.
- No PLS-DA.
- No clustering.
- No observations are removed.
- Rhizobium sp. and Trichoderma 1 are highlighted only because
  they correspond to isolates subsequently used in degradation experiments.
- Growth percentages are not included because they are algebraically
  complementary to inhibition percentages.

No manuscript figure is generated yet.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import spearmanr


# ============================================================
# PATHS
# ============================================================

PROJECT = Path(__file__).resolve().parents[1]

INPUT = (
    PROJECT
    / "data"
    / "processed"
    / "growth_inhibition.csv"
)

TABLES = PROJECT / "results" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(INPUT)

print("=" * 90)
print("BASE 2 — EXPLORATORY MULTIVARIATE ANALYSIS")
print("=" * 90)

print(f"\nDataset dimensions: {df.shape}")

print("\nColumns:")
for col in df.columns:
    print(f"  - {col}")


# ============================================================
# IDENTIFY VARIABLES
#
# We deliberately use the already validated quantitative
# variables from Base 2.
# ============================================================

candidate_sets = [

    # Most likely processed-column names
    {
        "Growth time (days)": "growth_time_days",
        "Growth rate (mm/day)": "growth_rate_mm_day",
        "Inhibition at 5000 ppm (%)": "inhibition_pct_5000",
        "Inhibition at 7500 ppm (%)": "inhibition_pct_7500",
        "Inhibition at 10000 ppm (%)": "inhibition_pct_10000",
    },

    # Alternative naming if inhibition was stored as CI
    {
        "Growth time (days)": "growth_time_days",
        "Growth rate (mm/day)": "growth_rate_mm_day",
        "Inhibition at 5000 ppm (%)": "CI_5000",
        "Inhibition at 7500 ppm (%)": "CI_7500",
        "Inhibition at 10000 ppm (%)": "CI_10000",
    },
]


variable_map = None

for candidate in candidate_sets:

    if all(
        col in df.columns
        for col in candidate.values()
    ):
        variable_map = candidate
        break


if variable_map is None:

    raise ValueError(
        "\nCould not identify the five expected quantitative variables.\n"
        "The complete column list was printed above.\n"
        "Do not rename or infer variables automatically."
    )


variables = list(
    variable_map.values()
)

display_names = list(
    variable_map.keys()
)


print("\nVariables selected for multivariate analysis:")

for display, internal in variable_map.items():
    print(f"  {display}: {internal}")


# ============================================================
# IDENTIFY MICROORGANISM NAME COLUMN
# ============================================================

name_candidates = [
    "microorganism",
    "Microorganism",
    "microorganismo",
    "Microorganismo",
    "name",
    "Name"
]

name_col = None

for candidate in name_candidates:

    if candidate in df.columns:
        name_col = candidate
        break


if name_col is None:

    raise ValueError(
        "\nCould not identify the microorganism-name column.\n"
        "The complete column list was printed above."
    )


print(
    f"\nMicroorganism identifier column: {name_col}"
)


# ============================================================
# CHECK NUMERIC DATA
# ============================================================

X = df[variables].copy()

for col in variables:
    X[col] = pd.to_numeric(
        X[col],
        errors="coerce"
    )


missing = X.isna().sum()

print("\nMissing values in PCA variables:")
print(missing.to_string())


if missing.sum() > 0:

    raise ValueError(
        "\nMissing/non-numeric values detected. "
        "No imputation will be performed automatically."
    )


# ============================================================
# CHECK VARIANCE
# ============================================================

variances = X.var(ddof=1)

print("\nVariable variances:")
print(variances.to_string())


zero_variance = variances[
    variances == 0
].index.tolist()


if zero_variance:

    raise ValueError(
        "\nZero-variance variables detected: "
        + ", ".join(zero_variance)
    )


# ============================================================
# STANDARDIZATION
# ============================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(
    X
)


# ============================================================
# PCA
# ============================================================

pca = PCA()

scores = pca.fit_transform(
    X_scaled
)


explained = (
    pca.explained_variance_ratio_
    * 100
)

cumulative = np.cumsum(
    explained
)


explained_df = pd.DataFrame(
    {
        "Principal component": [
            f"PC{i+1}"
            for i in range(len(explained))
        ],
        "Explained variance (%)":
            explained,
        "Cumulative variance (%)":
            cumulative,
        "Eigenvalue":
            pca.explained_variance_
    }
)


# ============================================================
# LOADINGS
#
# Components contain coefficients of standardized variables.
# We save both coefficients and correlations approximated as:
#
# loading correlation =
# component coefficient * sqrt(eigenvalue)
# ============================================================

component_coefficients = pd.DataFrame(
    pca.components_.T,
    index=display_names,
    columns=[
        f"PC{i+1}"
        for i in range(len(variables))
    ]
)


loading_correlations = (
    pca.components_.T
    * np.sqrt(
        pca.explained_variance_
    )
)

loading_df = pd.DataFrame(
    loading_correlations,
    index=display_names,
    columns=[
        f"PC{i+1}"
        for i in range(len(variables))
    ]
)


# ============================================================
# SCORES
# ============================================================

scores_df = pd.DataFrame(
    scores,
    columns=[
        f"PC{i+1}"
        for i in range(len(variables))
    ]
)

scores_df.insert(
    0,
    "Microorganism",
    df[name_col].astype(str).values
)


# ============================================================
# FLAG R AND T
# ============================================================

def classify_isolate(name):

    text = str(name).strip().lower()

    if text == "rhizobium sp":
        return "Rhizobium sp."

    if text == "trichoderma 1":
        return "Trichoderma 1"

    return "Other"


scores_df[
    "Experimental isolate"
] = (
    scores_df["Microorganism"]
    .apply(classify_isolate)
)


print("\nExperimental-isolate matches:")
print(
    scores_df[
        "Experimental isolate"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# SPEARMAN CORRELATIONS
# ============================================================

X_named = X.copy()

X_named.columns = display_names


rho_matrix = (
    X_named
    .corr(
        method="spearman"
    )
)


p_matrix = pd.DataFrame(
    np.ones(
        (
            len(display_names),
            len(display_names)
        )
    ),
    index=display_names,
    columns=display_names
)


for i, var1 in enumerate(display_names):

    for j, var2 in enumerate(display_names):

        rho, p = spearmanr(
            X_named[var1],
            X_named[var2]
        )

        p_matrix.loc[
            var1,
            var2
        ] = p


# ============================================================
# SAVE TABLES
# ============================================================

explained_df.to_csv(
    TABLES /
    "35_Table17_PCA_explained_variance.csv",
    index=False
)

component_coefficients.to_csv(
    TABLES /
    "35_Table18_PCA_component_coefficients.csv"
)

loading_df.to_csv(
    TABLES /
    "35_Table19_PCA_loadings.csv"
)

scores_df.to_csv(
    TABLES /
    "35_Table20_PCA_scores.csv",
    index=False
)

rho_matrix.to_csv(
    TABLES /
    "35_Table21_Spearman_correlations.csv"
)

p_matrix.to_csv(
    TABLES /
    "35_Table22_Spearman_pvalues.csv"
)


# ============================================================
# TERMINAL OUTPUT
# ============================================================

print("\n" + "=" * 90)
print("PCA — EXPLAINED VARIANCE")
print("=" * 90)

print(
    explained_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}"
    )
)


print("\n" + "=" * 90)
print("PCA — LOADINGS")
print("=" * 90)

print(
    loading_df.to_string(
        float_format=lambda x: f"{x:.6f}"
    )
)


print("\n" + "=" * 90)
print("RHIZOBIUM AND TRICHODERMA PCA SCORES")
print("=" * 90)

selected_scores = scores_df.loc[
    scores_df[
        "Experimental isolate"
    ] != "Other"
]

print(
    selected_scores.to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}"
    )
)


print("\n" + "=" * 90)
print("SPEARMAN CORRELATION MATRIX")
print("=" * 90)

print(
    rho_matrix.to_string(
        float_format=lambda x: f"{x:.4f}"
    )
)


print("\n" + "=" * 90)
print("SPEARMAN P-VALUE MATRIX")
print("=" * 90)

print(
    p_matrix.to_string(
        float_format=lambda x: f"{x:.6f}"
    )
)


print("\nSaved:")

for filename in [
    "35_Table17_PCA_explained_variance.csv",
    "35_Table18_PCA_component_coefficients.csv",
    "35_Table19_PCA_loadings.csv",
    "35_Table20_PCA_scores.csv",
    "35_Table21_Spearman_correlations.csv",
    "35_Table22_Spearman_pvalues.csv",
]:

    print(
        TABLES / filename
    )
