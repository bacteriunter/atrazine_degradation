#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
28_module2_comparative_analysis.py

Module 2 — Comparative functional characterization.

Purpose
-------
Place Rhizobium sp. (R) and Trichoderma 1 (T), used in the
laboratory degradation experiment, within the broader collection
of 31 microorganisms tested for growth and inhibition under
increasing atrazine concentrations.

Important
---------
- Descriptive analysis only.
- No inferential comparisons among microorganisms.
- No MIC calculation or imputation.
- The three atrazine concentrations are repeated characteristics
  of each microorganism, not independent replicates.
- Growth % and inhibition % are complementary; inhibition % is
  used as the primary tolerance descriptor.
- All manuscript-facing tables and figures are in English.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


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
# CONSTANTS
# ============================================================

CONCENTRATIONS = [5000, 7500, 10000]

INHIBITION_COLUMNS = {
    5000: "inhibition_pct_5000",
    7500: "inhibition_pct_7500",
    10000: "inhibition_pct_10000",
}

TARGETS = {
    "Rhizobium sp": "R",
    "Trichoderma 1": "T",
}


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT)

if len(df) != 31:
    raise ValueError(
        f"Expected 31 microorganisms; found {len(df)}."
    )

for microorganism in TARGETS:
    n = (df["microorganism"] == microorganism).sum()

    if n != 1:
        raise ValueError(
            f"Expected exactly one row for {microorganism}; found {n}."
        )


# ============================================================
# 1. COLLECTION-LEVEL DESCRIPTIVE SUMMARY
# ============================================================

summary_rows = []

for concentration in CONCENTRATIONS:

    col = INHIBITION_COLUMNS[concentration]

    values = df[col].dropna()

    summary_rows.append(
        {
            "Atrazine concentration (ppm)": concentration,
            "Microorganisms with data (n)": len(values),
            "Mean inhibition (%)": values.mean(),
            "SD inhibition (%)": values.std(),
            "Median inhibition (%)": values.median(),
            "Q1 inhibition (%)": values.quantile(0.25),
            "Q3 inhibition (%)": values.quantile(0.75),
            "Minimum inhibition (%)": values.min(),
            "Maximum inhibition (%)": values.max(),
            "Zero inhibition (n)": (values == 0).sum(),
            "Zero inhibition (%)":
                100 * (values == 0).mean(),
        }
    )

summary = pd.DataFrame(summary_rows)

summary.to_csv(
    TABLES /
    "28_Table3_atrazine_tolerance_summary.csv",
    index=False
)


# ============================================================
# 2. R/T COMPARATIVE POSITION
# ============================================================

target_rows = []

for microorganism, treatment in TARGETS.items():

    row = df.loc[
        df["microorganism"] == microorganism
    ].iloc[0]

    result = {
        "Base 1 treatment": treatment,
        "Microorganism": microorganism,
        "Growth time (days)": row["growth_time_days"],
        "Growth rate (mm/day)": row["growth_rate_mm_day"],
    }

    for concentration in CONCENTRATIONS:

        col = INHIBITION_COLUMNS[concentration]
        value = row[col]

        all_values = df[col].dropna()

        # Descriptive empirical position:
        # proportion of microorganisms showing inhibition
        # equal to or lower than the target microorganism.
        equal_or_lower = (
            100 *
            (all_values <= value).sum()
            / len(all_values)
        )

        result[
            f"Inhibition at {concentration} ppm (%)"
        ] = value

        result[
            f"Collection with inhibition <= target "
            f"at {concentration} ppm (%)"
        ] = equal_or_lower

    target_rows.append(result)

target_table = pd.DataFrame(target_rows)

position_columns = [
    c for c in target_table.columns
    if c.startswith("Collection with inhibition <=")
]

target_table = target_table.drop(
    columns=position_columns
)

target_table.to_csv(
    TABLES /
    "28_Table4_RT_comparative_profile.csv",
    index=False
)


# ============================================================
# 3. LONG FORMAT FOR FIGURES
# ============================================================

long_rows = []

for _, row in df.iterrows():

    for concentration in CONCENTRATIONS:

        long_rows.append(
            {
                "Microorganism": row["microorganism"],
                "Concentration": concentration,
                "Inhibition": row[
                    INHIBITION_COLUMNS[concentration]
                ],
                "Linked to Base 1":
                    bool(row["linked_to_base1"]),
                "Base 1 treatment":
                    row["base1_treatment"],
            }
        )

long = pd.DataFrame(long_rows)


# ============================================================
# 4. FIGURE 4 — INHIBITION HEATMAP
# ============================================================

heatmap = (
    df[
        [
            "microorganism",
            "inhibition_pct_5000",
            "inhibition_pct_7500",
            "inhibition_pct_10000",
        ]
    ]
    .set_index("microorganism")
    .copy()
)

heatmap.columns = [
    "5,000 ppm",
    "7,500 ppm",
    "10,000 ppm",
]


# Sort microorganisms descriptively by mean inhibition.
# This ordering is only for visualization.
heatmap["_mean"] = heatmap.mean(axis=1)

heatmap = heatmap.sort_values(
    "_mean",
    ascending=True
)

heatmap = heatmap.drop(
    columns="_mean"
)


fig, ax = plt.subplots(
    figsize=(7.2, 10.0)
)

im = ax.imshow(
    heatmap.values,
    aspect="auto",
    vmin=0,
    vmax=100
)

ax.set_xticks(
    np.arange(len(heatmap.columns))
)

ax.set_xticklabels(
    heatmap.columns
)

ax.set_yticks(
    np.arange(len(heatmap.index))
)

labels = []

display_names = {
    "No identificada 1": "Unidentified 1",
    "No identificada 2": "Unidentified 2",
    "No identificada 3": "Unidentified 3",

}

for microorganism in heatmap.index:

    if microorganism == "Rhizobium sp":
        labels.append("Rhizobium sp. (R)")
    elif microorganism == "Trichoderma 1":
        labels.append("Trichoderma 1 (T)")
    else:
        labels.append(
            display_names.get(
                microorganism,
                microorganism
            )
        )

ax.set_yticklabels(
    labels,
    fontsize=8
)

ax.set_xlabel(
    "Atrazine concentration"
)

ax.set_ylabel(
    "Microorganism"
)

ax.set_title(
    "Atrazine inhibition profiles across the microbial collection"
)

cbar = fig.colorbar(
    im,
    ax=ax
)

cbar.set_label(
    "Growth inhibition (%)"
)


# Values inside cells
for i in range(heatmap.shape[0]):

    for j in range(heatmap.shape[1]):

        value = heatmap.iloc[i, j]

        if pd.notna(value):

            ax.text(
                j,
                i,
                f"{value:.1f}",
                ha="center",
                va="center",
                fontsize=6
            )


# Highlight R and T labels
for tick, microorganism in zip(
    ax.get_yticklabels(),
    heatmap.index
):

    if microorganism in TARGETS:
        tick.set_fontweight("bold")


fig.tight_layout()

fig.savefig(
    FIGURES /
    "28_figure4_atrazine_inhibition_heatmap.png",
    dpi=300,
    bbox_inches="tight"
)

fig.savefig(
    FIGURES /
    "28_figure4_atrazine_inhibition_heatmap.pdf",
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# 5. FIGURE 5 — R/T WITHIN COLLECTION
# ============================================================

fig, ax = plt.subplots(
    figsize=(7.5, 5.5)
)


# Background: all 31 microorganisms
for microorganism, d in long.groupby(
    "Microorganism",
    sort=False
):

    if microorganism in TARGETS:
        continue

    d = d.sort_values(
        "Concentration"
    )

    ax.plot(
        d["Concentration"],
        d["Inhibition"],
        marker="o",
        linewidth=0.8,
        alpha=0.22
    )


# R and T highlighted
target_markers = {
    "Rhizobium sp": "s",
    "Trichoderma 1": "^",
}

for microorganism, treatment in TARGETS.items():

    d = long.loc[
        long["Microorganism"] == microorganism
    ].sort_values(
        "Concentration"
    )

    ax.plot(
        d["Concentration"],
        d["Inhibition"],
        marker=target_markers[microorganism],
        markersize=8,
        linewidth=2.2,
        label=f"{microorganism} ({treatment})"
    )


ax.set_xticks(
    CONCENTRATIONS
)

ax.set_xticklabels(
    ["5,000", "7,500", "10,000"]
)

ax.set_xlabel(
    "Atrazine concentration (ppm)"
)

ax.set_ylabel(
    "Growth inhibition (%)"
)

ax.set_ylim(
    bottom=0
)

ax.set_title(
    "Atrazine inhibition profiles of R and T within the microbial collection"
)

ax.legend(
    frameon=False
)

ax.grid(
    axis="y",
    alpha=0.2
)

fig.tight_layout()

fig.savefig(
    FIGURES /
    "28_figure5_RT_comparative_profile.png",
    dpi=300,
    bbox_inches="tight"
)

fig.savefig(
    FIGURES /
    "28_figure5_RT_comparative_profile.pdf",
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# 6. TEXT SUMMARY
# ============================================================

REPORT = (
    TABLES /
    "28_module2_results_summary.txt"
)

with REPORT.open(
    "w",
    encoding="utf-8"
) as out:

    out.write(
        "=" * 90 + "\n"
    )

    out.write(
        "MODULE 2 — COMPARATIVE FUNCTIONAL CHARACTERIZATION\n"
    )

    out.write(
        "=" * 90 + "\n\n"
    )

    out.write(
        "COLLECTION-LEVEL ATRAZINE INHIBITION\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        summary.to_string(
            index=False
        )
    )

    out.write(
        "\n\n"
    )

    out.write(
        "R AND T WITHIN THE MICROBIAL COLLECTION\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        target_table.to_string(
            index=False
        )
    )

    out.write(
        "\n\nINTERPRETATION RULES\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        "1. Results are descriptive; microorganisms are not "
        "treated as biological replicates.\n"
    )

    out.write(
        "2. Inhibition percentages at 5,000, 7,500, and "
        "10,000 ppm are repeated characteristics of each "
        "microorganism.\n"
    )

    out.write(
        "3. Growth percentage is not analyzed separately "
        "because growth and inhibition percentages are "
        "algebraically complementary.\n"
    )

    out.write(
        "4. MIC values are neither calculated nor imputed.\n"
    )

    out.write(
        "5. The empirical position of R and T is descriptive "
        "and refers only to this 31-microorganism collection.\n"
    )

    out.write(
        "6. No causal relationship between tolerance and "
        "atrazine biodegradation is assumed.\n"
    )


# ============================================================
# TERMINAL
# ============================================================

print("=" * 90)
print("MODULE 2 — COMPARATIVE ANALYSIS COMPLETED")
print("=" * 90)

print("\nCollection summary:")
print(summary.to_string(index=False))

print("\nR/T comparative profile:")
print(target_table.to_string(index=False))

print("\nFiles:")
print(
    TABLES /
    "28_Table3_atrazine_tolerance_summary.csv"
)
print(
    TABLES /
    "28_Table4_RT_comparative_profile.csv"
)
print(REPORT)

print(
    FIGURES /
    "28_figure4_atrazine_inhibition_heatmap.png"
)
print(
    FIGURES /
    "28_figure5_RT_comparative_profile.png"
)
