#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
36_final_multivariate_base2.py

Final exploratory multivariate analysis of Base 2.

Variables:
    - Growth time (days)
    - Inhibition at 5000 ppm (%)
    - Inhibition at 7500 ppm (%)
    - Inhibition at 10000 ppm (%)

growth_rate_mm_day is deliberately excluded because it is
deterministically derived from growth_time_days:

    growth_rate_mm_day = 80 / growth_time_days

Analyses:
    1. Standardized PCA
    2. Explained variance
    3. PCA loadings
    4. PCA scores
    5. Spearman correlations
    6. PCA biplot
    7. Spearman correlation heatmap

This analysis is exploratory/descriptive.
No PLS-DA or clustering is performed.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
FIGURES = PROJECT / "results" / "figures"

TABLES.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT)

if len(df) != 31:
    raise ValueError(
        f"Expected 31 microorganisms; found {len(df)}."
    )


# ============================================================
# VARIABLES
# ============================================================

variable_map = {
    "Growth time (days)":
        "growth_time_days",

    "Inhibition at 5000 ppm (%)":
        "inhibition_pct_5000",

    "Inhibition at 7500 ppm (%)":
        "inhibition_pct_7500",

    "Inhibition at 10000 ppm (%)":
        "inhibition_pct_10000",
}

variables = list(variable_map.values())
display_names = list(variable_map.keys())


required = {
    "microorganism",
    *variables
}

missing_columns = required - set(df.columns)

if missing_columns:
    raise ValueError(
        "Missing required columns: "
        + ", ".join(sorted(missing_columns))
    )


# ============================================================
# NUMERIC VALIDATION
# ============================================================

X = df[variables].copy()

for col in variables:
    X[col] = pd.to_numeric(
        X[col],
        errors="coerce"
    )

missing = X.isna().sum()

if missing.sum() > 0:
    raise ValueError(
        "Missing or non-numeric values detected:\n"
        + missing.to_string()
    )


variances = X.var(ddof=1)

if (variances == 0).any():
    raise ValueError(
        "At least one PCA variable has zero variance."
    )


# ============================================================
# STANDARDIZATION
# ============================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


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
            for i in range(len(variables))
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
# PCA LOADINGS
#
# Correlations between standardized original variables
# and principal components.
# ============================================================

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
# PCA SCORES
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
    df["microorganism"]
    .astype(str)
    .values
)


def isolate_class(name):

    text = str(name).strip().lower()

    if text == "rhizobium sp":
        return "Rhizobium sp."

    if text == "trichoderma 1":
        return "Trichoderma 1"

    return "Other microorganisms"


scores_df["Group"] = (
    scores_df["Microorganism"]
    .apply(isolate_class)
)


# ============================================================
# SPEARMAN CORRELATIONS
# ============================================================

X_named = X.copy()
X_named.columns = display_names


rho_matrix = X_named.corr(
    method="spearman"
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


for var1 in display_names:

    for var2 in display_names:

        rho, p = spearmanr(
            X_named[var1],
            X_named[var2]
        )

        p_matrix.loc[
            var1,
            var2
        ] = p


# ============================================================
# SAVE NUMERIC RESULTS
# ============================================================

explained_df.to_csv(
    TABLES /
    "36_Table17_final_PCA_explained_variance.csv",
    index=False
)

loading_df.to_csv(
    TABLES /
    "36_Table18_final_PCA_loadings.csv"
)

scores_df.to_csv(
    TABLES /
    "36_Table19_final_PCA_scores.csv",
    index=False
)

rho_matrix.to_csv(
    TABLES /
    "36_Table20_final_Spearman_correlations.csv"
)

p_matrix.to_csv(
    TABLES /
    "36_Table21_final_Spearman_pvalues.csv"
)


# ============================================================
# FIGURE 9 — PCA BIPLOT
# Corrected manuscript version
# ============================================================

fig, ax = plt.subplots(
    figsize=(8.4, 6.4)
)


# ------------------------------------------------------------
# Other microorganisms
# ------------------------------------------------------------

other = (
    scores_df["Group"]
    == "Other microorganisms"
)

ax.scatter(
    scores_df.loc[other, "PC1"],
    scores_df.loc[other, "PC2"],
    s=42,
    alpha=0.40,
    label="Other microorganisms",
    zorder=2
)


# ------------------------------------------------------------
# Rhizobium
# ------------------------------------------------------------

rhiz = (
    scores_df["Group"]
    == "Rhizobium sp."
)

ax.scatter(
    scores_df.loc[rhiz, "PC1"],
    scores_df.loc[rhiz, "PC2"],
    s=125,
    marker="D",
    edgecolors="black",
    linewidths=0.9,
    label="Rhizobium sp.",
    zorder=4
)


# ------------------------------------------------------------
# Trichoderma
# ------------------------------------------------------------

trich = (
    scores_df["Group"]
    == "Trichoderma 1"
)

ax.scatter(
    scores_df.loc[trich, "PC1"],
    scores_df.loc[trich, "PC2"],
    s=135,
    marker="^",
    edgecolors="black",
    linewidths=0.9,
    label="Trichoderma 1",
    zorder=4
)


# ------------------------------------------------------------
# Experimental-isolate labels
# ------------------------------------------------------------

for group_mask in [rhiz, trich]:

    for _, row in scores_df.loc[
        group_mask
    ].iterrows():

        ax.annotate(
            row["Microorganism"],
            (
                row["PC1"],
                row["PC2"]
            ),
            xytext=(8, 7),
            textcoords="offset points",
            fontsize=9.5,
            zorder=5
        )


# ------------------------------------------------------------
# Variable vectors
# ------------------------------------------------------------

pc1_range = (
    scores_df["PC1"].max()
    - scores_df["PC1"].min()
)

pc2_range = (
    scores_df["PC2"].max()
    - scores_df["PC2"].min()
)

vector_scale = (
    0.30
    * min(
        pc1_range,
        pc2_range
    )
)


short_labels = {
    "Growth time (days)":
        "Growth time",

    "Inhibition at 5000 ppm (%)":
        "Inhibition 5000 ppm",

    "Inhibition at 7500 ppm (%)":
        "Inhibition 7500 ppm",

    "Inhibition at 10000 ppm (%)":
        "Inhibition 10000 ppm",
}


# Manual label offsets are graphical only.
# They do not alter vector coordinates or PCA results.

label_offsets = {
    "Growth time (days)":
        (-10, 10),

    "Inhibition at 5000 ppm (%)":
        (16, 18),

    "Inhibition at 7500 ppm (%)":
        (18, 3),

    "Inhibition at 10000 ppm (%)":
        (18, -13),
}


for variable in display_names:

    x_loading = (
        loading_df.loc[
            variable,
            "PC1"
        ]
        * vector_scale
    )

    y_loading = (
        loading_df.loc[
            variable,
            "PC2"
        ]
        * vector_scale
    )

    ax.annotate(
        "",
        xy=(
            x_loading,
            y_loading
        ),
        xytext=(0, 0),
        arrowprops=dict(
            arrowstyle="->",
            linewidth=1.5
        ),
        zorder=3
    )

    dx, dy = label_offsets[
        variable
    ]

    ax.annotate(
        short_labels[variable],
        (
            x_loading,
            y_loading
        ),
        xytext=(dx, dy),
        textcoords="offset points",
        fontsize=9,
        ha="center",
        va="center",
        zorder=5
    )


# ------------------------------------------------------------
# Reference axes
# ------------------------------------------------------------

ax.axhline(
    0,
    linewidth=0.8,
    alpha=0.25,
    zorder=1
)

ax.axvline(
    0,
    linewidth=0.8,
    alpha=0.25,
    zorder=1
)


# ------------------------------------------------------------
# Axis labels
# ------------------------------------------------------------

ax.set_xlabel(
    f"PC1 ({explained[0]:.1f}% explained variance)"
)

ax.set_ylabel(
    f"PC2 ({explained[1]:.1f}% explained variance)"
)

ax.set_title(
    "PCA of microbial growth and atrazine inhibition profiles"
)


# ------------------------------------------------------------
# Compact plotting limits
# ------------------------------------------------------------

pc1_min = scores_df["PC1"].min()
pc1_max = scores_df["PC1"].max()

pc2_min = scores_df["PC2"].min()
pc2_max = scores_df["PC2"].max()

ax.set_xlim(
    pc1_min - 0.35,
    pc1_max + 0.30
)

ax.set_ylim(
    pc2_min - 0.20,
    pc2_max + 0.20
)


# ------------------------------------------------------------
# Legend
# ------------------------------------------------------------

ax.legend(
    frameon=False,
    loc="lower right"
)


fig.tight_layout()


fig.savefig(
    FIGURES /
    "36_figure9_PCA_microorganisms.png",
    dpi=300,
    bbox_inches="tight"
)

fig.savefig(
    FIGURES /
    "36_figure9_PCA_microorganisms.pdf",
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# FIGURE 10 — SPEARMAN CORRELATION HEATMAP
# ============================================================

fig, ax = plt.subplots(
    figsize=(8.0, 6.7)
)


matrix = rho_matrix.to_numpy(
    dtype=float
)

image = ax.imshow(
    matrix,
    vmin=-1,
    vmax=1,
    aspect="equal"
)


heatmap_labels = [
    "Growth time",
    "Inhibition\n5000 ppm",
    "Inhibition\n7500 ppm",
    "Inhibition\n10000 ppm"
]


ax.set_xticks(
    np.arange(
        len(heatmap_labels)
    )
)

ax.set_yticks(
    np.arange(
        len(heatmap_labels)
    )
)

ax.set_xticklabels(
    heatmap_labels,
    rotation=35,
    ha="right"
)

ax.set_yticklabels(
    heatmap_labels
)


# ------------------------------------------------------------
# Correlation coefficients and significance
# ------------------------------------------------------------

for i in range(
    len(display_names)
):

    for j in range(
        len(display_names)
    ):

        rho = matrix[i, j]

        p = p_matrix.iloc[i, j]

        if i == j:
            text = f"{rho:.2f}"

        elif p < 0.001:
            text = f"{rho:.2f}\n***"

        elif p < 0.01:
            text = f"{rho:.2f}\n**"

        elif p < 0.05:
            text = f"{rho:.2f}\n*"

        else:
            text = f"{rho:.2f}\nns"

        ax.text(
            j,
            i,
            text,
            ha="center",
            va="center",
            fontsize=9
        )


colorbar = fig.colorbar(
    image,
    ax=ax,
    fraction=0.046,
    pad=0.04
)

colorbar.set_label(
    "Spearman's rho"
)


ax.set_title(
    "Spearman correlations among microbial phenotypic variables"
)


fig.tight_layout()


fig.savefig(
    FIGURES /
    "36_figure10_Spearman_heatmap.png",
    dpi=300,
    bbox_inches="tight"
)

fig.savefig(
    FIGURES /
    "36_figure10_Spearman_heatmap.pdf",
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# REPORT
# ============================================================

REPORT = (
    TABLES /
    "36_final_multivariate_summary.txt"
)


with REPORT.open(
    "w",
    encoding="utf-8"
) as out:

    out.write(
        "=" * 90 + "\n"
    )

    out.write(
        "FINAL EXPLORATORY MULTIVARIATE ANALYSIS — BASE 2\n"
    )

    out.write(
        "=" * 90 + "\n\n"
    )

    out.write(
        "Variables included:\n"
    )

    for name in display_names:
        out.write(
            f"- {name}\n"
        )

    out.write(
        "\nGrowth rate was excluded because it is "
        "deterministically derived from growth time "
        "(growth rate = 80 / growth time).\n"
    )

    out.write(
        "\nPCA EXPLAINED VARIANCE\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        explained_df.to_string(
            index=False
        )
    )

    out.write(
        "\n\nPCA LOADINGS\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        loading_df.to_string()
    )

    out.write(
        "\n\nEXPERIMENTAL ISOLATE SCORES\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        scores_df.loc[
            scores_df["Group"]
            != "Other microorganisms"
        ].to_string(
            index=False
        )
    )

    out.write(
        "\n\nSPEARMAN CORRELATIONS\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        rho_matrix.to_string()
    )

    out.write(
        "\n\nSPEARMAN P VALUES\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        p_matrix.to_string()
    )

    out.write(
        "\n\nInterpretive restriction:\n"
        "PCA and correlation analyses describe phenotypic "
        "structure within the microorganism collection. "
        "They do not demonstrate atrazine degradation "
        "capacity or causal relationships.\n"
    )


# ============================================================
# TERMINAL OUTPUT
# ============================================================

print("=" * 90)
print(
    "FINAL EXPLORATORY MULTIVARIATE ANALYSIS — BASE 2"
)
print("=" * 90)

print("\nPCA explained variance:")
print(
    explained_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}"
    )
)

print("\nPCA loadings:")
print(
    loading_df.to_string(
        float_format=lambda x: f"{x:.6f}"
    )
)

print("\nExperimental isolate scores:")
print(
    scores_df.loc[
        scores_df["Group"]
        != "Other microorganisms"
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}"
    )
)

print("\nSpearman correlations:")
print(
    rho_matrix.to_string(
        float_format=lambda x: f"{x:.4f}"
    )
)

print("\nSpearman p-values:")
print(
    p_matrix.to_string(
        float_format=lambda x: f"{x:.6f}"
    )
)

print("\nSaved:")

for path in [
    TABLES /
    "36_Table17_final_PCA_explained_variance.csv",

    TABLES /
    "36_Table18_final_PCA_loadings.csv",

    TABLES /
    "36_Table19_final_PCA_scores.csv",

    TABLES /
    "36_Table20_final_Spearman_correlations.csv",

    TABLES /
    "36_Table21_final_Spearman_pvalues.csv",

    FIGURES /
    "36_figure9_PCA_microorganisms.png",

    FIGURES /
    "36_figure10_Spearman_heatmap.png",

    REPORT
]:
    print(path)
