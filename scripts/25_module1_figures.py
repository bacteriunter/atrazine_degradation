#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
25_module1_figures.py

Checkpoint 26
Figuras finales del Módulo 1.

Figuras:
1. Heatmap descriptivo de propiedades fisicoquímicas.
2. Perfiles microbiológicos por suelo, grupo y dilución.
3. Patrón cualitativo de aislamiento PDA.

No se realizan pruebas inferenciales.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


PROJECT = Path(__file__).resolve().parents[1]

TABLES = PROJECT / "results" / "tables"
FIGURES = PROJECT / "results" / "figures"

FIGURES.mkdir(parents=True, exist_ok=True)


# ============================================================
# FIGURA 1
# PERFIL FISICOQUÍMICO ESTANDARIZADO
# ============================================================

soil = pd.read_csv(
    TABLES / "24_table1_soil_physicochemical.csv"
)

matrix = (
    soil
    .pivot(
        index="variable_code",
        columns="soil",
        values="mean"
    )
)

# Orden explícito
variables = [
    "D",
    "pH",
    "H",
    "N",
    "CO",
    "MO",
    "CIC"
]

soils = [
    "Capulin",
    "Santa Ana",
    "Tepantitla"
]

matrix = matrix.loc[variables, soils]


# Estandarización descriptiva por variable
# Solo para visualización.
z = matrix.sub(
    matrix.mean(axis=1),
    axis=0
).div(
    matrix.std(axis=1, ddof=0),
    axis=0
)


fig, ax = plt.subplots(
    figsize=(6.5, 5.5)
)

im = ax.imshow(
    z.values,
    aspect="auto"
)

ax.set_xticks(
    np.arange(len(soils))
)

ax.set_xticklabels(
    ["Capulín", "Santa Ana", "Tepantitla"]
)

ax.set_yticks(
    np.arange(len(variables))
)

ax.set_yticklabels(
    variables
)

# Valor real dentro de cada celda
for i in range(len(variables)):
    for j in range(len(soils)):

        value = matrix.iloc[i, j]

        ax.text(
            j,
            i,
            f"{value:.2f}",
            ha="center",
            va="center"
        )

cbar = fig.colorbar(
    im,
    ax=ax
)

cbar.set_label(
    "Standardized value (z)"
)

ax.set_xlabel("Soil")
ax.set_ylabel("Property")

ax.set_title(
    "Physicochemical characterization of soil samples"
)

fig.tight_layout()

fig.savefig(
    FIGURES / "25_figure1_soil_physicochemical.png",
    dpi=300,
    bbox_inches="tight"
)

fig.savefig(
    FIGURES / "25_figure1_soil_physicochemical.pdf",
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# FIGURA 2
# PERFILES MICROBIOLÓGICOS
# ============================================================

micro = pd.read_csv(
    TABLES / "24_table2_soil_microbiology.csv"
)

group_order = [
    "PDA_bacteria",
    "PDA_fungi",
    "Actinomicetos",
    "Extracto de suelo",
    "PDA acidificado"
]

soil_order = [
    "Capulin",
    "Santa Ana",
    "Tepantitla"
]

dilution_order = [
    "10^-2",
    "10^-3",
    "10^-4",
    "10^-5"
]


for group in group_order:

    d = micro.loc[
        micro["microbial_group"] == group
    ].copy()

    fig, ax = plt.subplots(
        figsize=(7.5, 5.5)
    )

    positions = np.arange(
        len(dilution_order)
    )

    width = 0.23

    for k, soil_name in enumerate(soil_order):

        ds = d.loc[
            d["soil"] == soil_name
        ].copy()

        values = []
        errors = []

        for dilution in dilution_order:

            row = ds.loc[
                ds["dilution"] == dilution
            ]

            if row.empty:
                values.append(np.nan)
                errors.append(np.nan)
            else:
                values.append(
                    row["mean_cfu_ml"].iloc[0]
                )
                errors.append(
                    row["sd_cfu_ml"].iloc[0]
                )

        x = positions + (
            k - 1
        ) * width

        ax.errorbar(
            x,
            values,
            yerr=errors,
            fmt="o",
            capsize=3,
            label=soil_name
        )

    ax.set_xticks(positions)

    ax.set_xticklabels(
        [
            r"$10^{-2}$",
            r"$10^{-3}$",
            r"$10^{-4}$",
            r"$10^{-5}$"
        ]
    )

    ax.set_yscale(
        "symlog",
        linthresh=1
    )

    ax.set_xlabel(
        "Dilution"
    )

    ax.set_ylabel(
        "CFU/mL recalculadas"
    )

    ax.set_title(
        group.replace("_", " ")
    )

    ax.legend(
        frameon=False
    )

    ax.grid(
        axis="y",
        alpha=0.25
    )

    fig.tight_layout()

    safe_name = (
        group
        .lower()
        .replace(" ", "_")
    )

    fig.savefig(
        FIGURES /
        f"25_figure2_{safe_name}.png",
        dpi=300,
        bbox_inches="tight"
    )

    fig.savefig(
        FIGURES /
        f"25_figure2_{safe_name}.pdf",
        bbox_inches="tight"
    )

    plt.close(fig)


# ============================================================
# FIGURA 3
# AISLAMIENTO PDA
# ============================================================

iso = pd.read_csv(
    PROCESSED := (
        PROJECT
        / "data"
        / "processed"
        / "pda_isolation_classified.csv"
    )
)

# Solo tiempos con observaciones reales
iso = iso.loc[
    iso["time_h"].isin([24, 48])
].copy()

soil_order = [
    "Capulin",
    "Santa Ana",
    "Tepantitla"
]

for time in [24, 48]:

    d = iso.loc[
        iso["time_h"] == time
    ].copy()

    matrix_growth = np.full(
        (
            len(soil_order),
            6
        ),
        np.nan
    )

    # 0 = ausencia
    # 1 = presencia
    # NaN = no determinado
    for i, soil_name in enumerate(soil_order):

        for dilution in range(1, 7):

            row = d.loc[
                (d["soil"] == soil_name)
                &
                (d["dilution"] == dilution)
            ]

            if row.empty:
                continue

            status = (
                row["overall_growth"]
                .iloc[0]
            )

            if status == "present":
                matrix_growth[i, dilution - 1] = 1

            elif status == "absent":
                matrix_growth[i, dilution - 1] = 0

    fig, ax = plt.subplots(
        figsize=(7.5, 3.5)
    )

    im = ax.imshow(
        matrix_growth,
        aspect="auto",
        vmin=0,
        vmax=1
    )

    ax.set_xticks(
        np.arange(6)
    )

    ax.set_xticklabels(
        [
            r"$10^{-1}$",
            r"$10^{-2}$",
            r"$10^{-3}$",
            r"$10^{-4}$",
            r"$10^{-5}$",
            r"$10^{-6}$"
        ]
    )

    ax.set_yticks(
        np.arange(3)
    )

    ax.set_yticklabels(
        [
            "Capulín",
            "Santa Ana",
            "Tepantitla"
        ]
    )

    for i in range(3):
        for j in range(6):

            value = matrix_growth[i, j]

            if np.isnan(value):
                text = "ND"
            elif value == 1:
                text = "+"
            else:
                text = "−"

            ax.text(
                j,
                i,
                text,
                ha="center",
                va="center",
                fontsize=12
            )

    ax.set_xlabel(
        "Dilution"
    )

    ax.set_ylabel(
        "Soil"
    )

    ax.set_title(
        f"Observed growth on PDA — {time} h"
    )

    cbar = fig.colorbar(
        im,
        ax=ax,
        ticks=[0, 1]
    )

    cbar.ax.set_yticklabels(
        [
            "Absent",
            "Present"
        ]
    )

    fig.tight_layout()

    fig.savefig(
        FIGURES /
        f"25_figure3_pda_isolation_{time}h.png",
        dpi=300,
        bbox_inches="tight"
    )

    fig.savefig(
        FIGURES /
        f"25_figure3_pda_isolation_{time}h.pdf",
        bbox_inches="tight"
    )

    plt.close(fig)


print("=" * 90)
print("FIGURAS DEL MÓDULO 1 COMPLETADAS")
print("=" * 90)

for f in sorted(
    FIGURES.glob("25_*")
):
    print(f.name)
