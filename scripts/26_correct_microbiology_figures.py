#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
26_correct_microbiology_figures.py

Figuras microbiológicas finales del Módulo 1.

- Cada círculo pequeño representa una caja Petri (réplica técnica).
- Cada diamante representa la mediana.
- Los colores identifican el suelo.
- Eje Y = log10(CFU/mL + 1).
- Las diluciones se representan como categorías.
- No se realizan pruebas inferenciales.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


PROJECT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT / "data" / "processed"
FIGURES = PROJECT / "results" / "figures"
TABLES = PROJECT / "results" / "tables"

FIGURES.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURACIÓN
# ============================================================

soil_order = [
    "Capulin",
    "Santa Ana",
    "Tepantitla"
]

soil_labels = {
    "Capulin": "Capulín",
    "Santa Ana": "Santa Ana",
    "Tepantitla": "Tepantitla"
}

colors = {
    "Capulin": "tab:blue",
    "Santa Ana": "tab:orange",
    "Tepantitla": "tab:green"
}

dilution_order = [
    "10^-2",
    "10^-3",
    "10^-4",
    "10^-5"
]

dilution_labels = [
    r"$10^{-2}$",
    r"$10^{-3}$",
    r"$10^{-4}$",
    r"$10^{-5}$"
]

offsets = {
    "Capulin": -0.20,
    "Santa Ana": 0.00,
    "Tepantitla": 0.20
}


# ============================================================
# CARGAR DATOS
# ============================================================

bacteria = pd.read_csv(
    PROCESSED / "pdab1_pda_bacteria.csv"
)

fungi = pd.read_csv(
    PROCESSED / "pdab1_pda_fungi.csv"
)

other = pd.read_csv(
    PROCESSED / "pdab1_microbiology.csv"
)


# ============================================================
# FUNCIÓN DE GRAFICACIÓN
# ============================================================

def plot_group(df, title, output_name):

    fig, ax = plt.subplots(figsize=(8.5, 5.8))

    for soil in soil_order:

        soil_df = df.loc[
            df["soil"] == soil
        ].copy()

        for d_idx, dilution in enumerate(dilution_order):

            subset = soil_df.loc[
                soil_df["dilution"] == dilution,
                "cfu_per_ml_recalculated"
            ].dropna()

            if subset.empty:
                continue

            values = subset.to_numpy(dtype=float)

            # Transformación exclusiva para visualización
            transformed = np.log10(values + 1.0)

            center = d_idx + offsets[soil]

            # --------------------------------------------
            # Cajas Petri individuales
            # --------------------------------------------

            if len(transformed) == 1:
                jitter = np.array([0.0])
            else:
                jitter = np.linspace(
                    -0.055,
                    0.055,
                    len(transformed)
                )

            ax.scatter(
                center + jitter,
                transformed,
                s=30,
                alpha=0.35,
                marker="o",
                color=colors[soil],
                edgecolors=colors[soil],
                linewidths=0.6,
                zorder=2
            )

            # --------------------------------------------
            # Mediana
            # --------------------------------------------

            median_original = np.median(values)

            median_transformed = np.log10(
                median_original + 1.0
            )

            ax.scatter(
                center,
                median_transformed,
                s=105,
                marker="D",
                color=colors[soil],
                edgecolor="black",
                linewidth=0.9,
                zorder=5
            )

    # ========================================================
    # EJES
    # ========================================================

    ax.set_xticks(
        np.arange(len(dilution_order))
    )

    ax.set_xticklabels(
        dilution_labels
    )

    ax.set_xlabel("Dilution")

    ax.set_ylabel(
        r"$\log_{10}(\mathrm{CFU/mL}+1)$"
    )

    ax.set_title(title)

    ax.grid(
        axis="y",
        alpha=0.20
    )

    # ========================================================
    # LEYENDA
    # ========================================================

    soil_handles = []

    for soil in soil_order:

        handle = Line2D(
            [0],
            [0],
            marker="o",
            linestyle="None",
            markerfacecolor=colors[soil],
            markeredgecolor=colors[soil],
            alpha=0.55,
            markersize=7,
            label=soil_labels[soil]
        )

        soil_handles.append(handle)

    median_handle = Line2D(
        [0],
        [0],
        marker="D",
        linestyle="None",
        markerfacecolor="white",
        markeredgecolor="black",
        markersize=8,
        label="Median"
    )

    handles = soil_handles + [median_handle]

    ax.legend(
        handles=handles,
        title="Soil",
        frameon=False,
        loc="best"
    )

    fig.tight_layout()

    # ========================================================
    # GUARDAR
    # ========================================================

    fig.savefig(
        FIGURES / f"{output_name}.png",
        dpi=300,
        bbox_inches="tight"
    )

    fig.savefig(
        FIGURES / f"{output_name}.pdf",
        bbox_inches="tight"
    )

    plt.close(fig)


# ============================================================
# PDA BACTERIAS
# ============================================================

plot_group(
    bacteria,
    "Culturable bacteria on PDA",
    "26_pda_bacteria_corrected"
)


# ============================================================
# PDA HONGOS
# ============================================================

plot_group(
    fungi,
    "Culturable fungi on PDA",
    "26_pda_fungi_corrected"
)


# ============================================================
# ACTINOMICETOS
# ============================================================

actino = other.loc[
    other["sheet"] == "Actinomicetos"
].copy()

plot_group(
    actino,
    "Actinomycetes",
    "26_actinomicetos_corrected"
)


# ============================================================
# EXTRACTO DE SUELO
# ============================================================

extracto = other.loc[
    other["sheet"] == "Extracto de suelo"
].copy()

plot_group(
    extracto,
    "Counts on soil extract medium",
    "26_extracto_suelo_corrected"
)


# ============================================================
# PDA ACIDIFICADO
# ============================================================

acid = other.loc[
    other["sheet"] == "PDA acidificado"
].copy()

plot_group(
    acid,
    "Counts on acidified PDA",
    "26_pda_acidificado_corrected"
)


# ============================================================
# NOTA DE TRAZABILIDAD
# ============================================================

report = TABLES / "26_microbiology_figures_note.txt"

with report.open("w", encoding="utf-8") as out:

    out.write(
        "CHECKPOINT 26 — FIGURAS MICROBIOLÓGICAS FINALES\n\n"
    )

    out.write(
        "1. Cada círculo representa una caja Petri "
        "(réplica técnica).\n"
    )

    out.write(
        "2. Cada diamante representa la mediana de las "
        "cajas disponibles para suelo y dilución.\n"
    )

    out.write(
        "3. El color identifica exclusivamente el suelo.\n"
    )

    out.write(
        "4. El eje Y corresponde a log10(CFU/mL + 1).\n"
    )

    out.write(
        "5. La transformación se utiliza exclusivamente "
        "para visualización.\n"
    )

    out.write(
        "6. Los valores originales de CFU/mL no fueron "
        "modificados.\n"
    )

    out.write(
        "7. Las diluciones se representan como categorías.\n"
    )

    out.write(
        "8. B1-B3 y las cajas Petri no se consideran "
        "réplicas biológicas independientes.\n"
    )

    out.write(
        "9. No se realizaron pruebas inferenciales.\n"
    )


print("=" * 90)
print("FIGURAS MICROBIOLÓGICAS FINALES GENERADAS")
print("=" * 90)

for f in sorted(FIGURES.glob("26_*")):
    print(f.name)

print("\nNota metodológica:")
print(report)
