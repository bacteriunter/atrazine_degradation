#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
34_finalize_module4.py

Module 4 — Final greenhouse outputs.

No new statistical tests are performed.

This script consolidates results already obtained in:
    32_Table10_greenhouse_descriptive_statistics.csv
    33_Table13_greenhouse_Tukey.csv
    33_Table14_greenhouse_planned_contrasts.csv

Main manuscript figure:
    Soil atrazine biodegradation at 40 days.

Figure elements:
    - individual experimental observations
    - mean ± SD
    - Tukey HSD compact-letter display

Treatment B remains excluded because atrazine was not added.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

PROJECT = Path(__file__).resolve().parents[1]

DATA = (
    PROJECT
    / "data"
    / "processed"
    / "greenhouse_degradation_analysis.csv"
)

TABLES = PROJECT / "results" / "tables"
FIGURES = PROJECT / "results" / "figures"

TABLES.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA)

if len(df) != 15:
    raise ValueError(
        f"Expected 15 analytical observations; found {len(df)}."
    )


treatment_order = [
    "Tes",
    "F",
    "R",
    "RT",
    "T"
]


# ============================================================
# TREATMENT DEFINITIONS
# ============================================================

definitions = {
    "Tes": "Soil + atrazine",
    "F": "Soil + atrazine + bean",
    "R": "Bean + Rhizobium",
    "T": "Bean + Trichoderma",
    "RT": "Bean + Rhizobium + Trichoderma"
}


# ============================================================
# DESCRIPTIVE SUMMARY
# ============================================================

responses = [
    "soil_biodegradation_pct",
    "global_bioremediation_pct"
]

summary_rows = []

for response in responses:

    temp = (
        df
        .groupby("treatment")[response]
        .agg(
            n="count",
            Mean="mean",
            SD="std"
        )
        .reset_index()
    )

    for _, row in temp.iterrows():

        summary_rows.append(
            {
                "Response":
                    response,
                "Treatment":
                    row["treatment"],
                "Treatment description":
                    definitions[
                        row["treatment"]
                    ],
                "n":
                    int(row["n"]),
                "Mean (%)":
                    row["Mean"],
                "SD":
                    row["SD"]
            }
        )


summary = pd.DataFrame(
    summary_rows
)


# ============================================================
# TUKEY LETTERS
#
# Derived from the already completed Tukey HSD comparisons
# for soil_biodegradation_pct.
#
# T   = a
# RT  = ab
# R   = bc
# F   = cd
# Tes = d
#
# Shared letters indicate no significant difference.
# ============================================================

soil_letters = {
    "Tes": "d",
    "F": "cd",
    "R": "bc",
    "RT": "ab",
    "T": "a"
}


summary["Tukey group"] = ""

mask_soil = (
    summary["Response"]
    == "soil_biodegradation_pct"
)

summary.loc[
    mask_soil,
    "Tukey group"
] = (
    summary.loc[
        mask_soil,
        "Treatment"
    ]
    .map(soil_letters)
)


# ============================================================
# PLANNED CONTRAST SUMMARY
# Existing results only
# ============================================================

contrast_file = (
    TABLES /
    "33_Table14_greenhouse_planned_contrasts.csv"
)

contrasts = pd.read_csv(
    contrast_file
)


contrast_export = contrasts[
    [
        "Response",
        "Contrast",
        "Mean difference",
        "CI lower 95%",
        "CI upper 95%",
        "Holm-adjusted p",
        "Significant after Holm"
    ]
].copy()


# ============================================================
# SAVE MANUSCRIPT TABLES
# ============================================================

summary.to_csv(
    TABLES /
    "34_Table15_greenhouse_final_summary.csv",
    index=False
)

contrast_export.to_csv(
    TABLES /
    "34_Table16_greenhouse_planned_contrasts.csv",
    index=False
)


# ============================================================
# FIGURE 8
# Soil biodegradation
# ============================================================

response = "soil_biodegradation_pct"

soil_summary = (
    summary.loc[
        summary["Response"] == response
    ]
    .set_index("Treatment")
    .loc[treatment_order]
    .reset_index()
)


fig, ax = plt.subplots(
    figsize=(7.8, 5.8)
)


x = np.arange(
    len(treatment_order)
)


# ------------------------------------------------------------
# Individual observations
# Fixed offsets only for visibility; no random jitter.
# ------------------------------------------------------------

offsets = np.array(
    [-0.08, 0.00, 0.08]
)


for i, treatment in enumerate(
    treatment_order
):

    values = (
        df.loc[
            df["treatment"] == treatment,
            response
        ]
        .to_numpy(dtype=float)
    )

    values = np.sort(values)

    ax.scatter(
        np.full(
            len(values),
            x[i]
        ) + offsets,
        values,
        s=38,
        alpha=0.50,
        zorder=3
    )


# ------------------------------------------------------------
# Mean ± SD
# ------------------------------------------------------------

means = soil_summary[
    "Mean (%)"
].to_numpy(dtype=float)

sds = soil_summary[
    "SD"
].to_numpy(dtype=float)


ax.errorbar(
    x,
    means,
    yerr=sds,
    fmt="o",
    markersize=8,
    capsize=5,
    linewidth=1.6,
    zorder=4,
    label="Mean ± SD"
)


# ------------------------------------------------------------
# Tukey letters
# ------------------------------------------------------------

letters = (
    soil_summary[
        "Tukey group"
    ].to_list()
)


for i, (
    mean,
    sd,
    letter
) in enumerate(
    zip(
        means,
        sds,
        letters
    )
):

    ax.text(
        x[i],
        mean + sd + 4.0,
        letter,
        ha="center",
        va="bottom",
        fontsize=11
    )


# ------------------------------------------------------------
# Formatting
# ------------------------------------------------------------

ax.set_xticks(
    x
)

ax.set_xticklabels(
    treatment_order
)

ax.set_xlabel(
    "Treatment"
)

ax.set_ylabel(
    "Soil atrazine biodegradation (%)"
)

ax.set_title(
    "Atrazine biodegradation in the greenhouse experiment at 40 days"
)

ax.grid(
    axis="y",
    alpha=0.20
)

ax.legend(
    frameon=False
)

upper_limit = max(
    75,
    np.max(means + sds) + 10
)

ax.set_ylim(
    0,
    upper_limit
)

fig.tight_layout()


fig.savefig(
    FIGURES /
    "34_figure8_greenhouse_soil_biodegradation.png",
    dpi=300,
    bbox_inches="tight"
)

fig.savefig(
    FIGURES /
    "34_figure8_greenhouse_soil_biodegradation.pdf",
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# FINAL REPORT
# ============================================================

REPORT = (
    TABLES /
    "34_module4_final_summary.txt"
)


with REPORT.open(
    "w",
    encoding="utf-8"
) as out:

    out.write(
        "=" * 90 + "\n"
    )

    out.write(
        "MODULE 4 — FINAL GREENHOUSE RESULTS\n"
    )

    out.write(
        "=" * 90 + "\n\n"
    )

    out.write(
        "FINAL DESCRIPTIVE SUMMARY\n"
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
        "\n\nPLANNED CONTRASTS\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        contrast_export.to_string(
            index=False
        )
    )

    out.write(
        "\n\nINTERPRETATION\n"
    )

    out.write(
        "-" * 90 + "\n"
    )

    out.write(
        "Soil biodegradation differed among treatments "
        "(one-way ANOVA, p < 0.001).\n"
    )

    out.write(
        "Trichoderma and the Rhizobium + Trichoderma "
        "treatment showed significantly higher soil "
        "biodegradation than the uninoculated plant "
        "control in the pre-specified Holm-adjusted "
        "contrasts.\n"
    )

    out.write(
        "Rhizobium alone did not differ significantly "
        "from the uninoculated plant control.\n"
    )

    out.write(
        "The consortium was not significantly different "
        "from Trichoderma in Tukey HSD.\n"
    )

    out.write(
        "Treatment B was excluded because atrazine "
        "was not added.\n"
    )

    out.write(
        "Results are restricted to the greenhouse "
        "experiment at 40 days and 1000 ppm nominal "
        "initial atrazine concentration.\n"
    )


# ============================================================
# TERMINAL
# ============================================================

print("=" * 90)
print(
    "MODULE 4 — FINAL OUTPUTS COMPLETED"
)
print("=" * 90)

print("\nFinal summary:")
print(
    summary.to_string(
        index=False
    )
)

print("\nPlanned contrasts:")
print(
    contrast_export.to_string(
        index=False
    )
)

print("\nSaved:")
print(
    TABLES /
    "34_Table15_greenhouse_final_summary.csv"
)
print(
    TABLES /
    "34_Table16_greenhouse_planned_contrasts.csv"
)
print(
    FIGURES /
    "34_figure8_greenhouse_soil_biodegradation.png"
)
print(REPORT)
