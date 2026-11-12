#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
02_explore_lab_data.py

Exploración descriptiva del experimento de degradación de atrazina
en laboratorio.

Entrada:
    data/processed/lab_degradation_analysis.csv

El dataset analítico contiene exclusivamente:
    Te = testigo contaminado, sin microorganismos
    R  = Rhizobium
    T  = Trichoderma
    RT = Rhizobium + Trichoderma

Diseño:
    4 tratamientos × 4 tiempos × 3 réplicas
    = 48 unidades experimentales independientes.

El blanco B no participa en este análisis porque no recibió atrazina.

Salidas:
    results/tables/02_lab_descriptive_statistics.csv
    results/tables/02_lab_individual_observations.csv
    results/figures/02_biodegradation_trajectories.png
    results/figures/02_biodegradation_individual.png
    results/figures/02_biodegradation_by_treatment.png

Este script:
    - NO realiza pruebas de hipótesis.
    - NO realiza ANOVA.
    - NO ajusta modelos cinéticos.
    - NO elimina valores extremos.
    - NO modifica los datos procesados.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# ============================================================
# RUTAS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "lab_degradation_analysis.csv"
)

TABLE_DIR = PROJECT_DIR / "results" / "tables"
FIGURE_DIR = PROJECT_DIR / "results" / "figures"

SUMMARY_FILE = (
    TABLE_DIR
    / "02_lab_descriptive_statistics.csv"
)

OBSERVATIONS_FILE = (
    TABLE_DIR
    / "02_lab_individual_observations.csv"
)

FIG_TRAJECTORIES = (
    FIGURE_DIR
    / "02_biodegradation_trajectories.png"
)

FIG_INDIVIDUAL = (
    FIGURE_DIR
    / "02_biodegradation_individual.png"
)

FIG_TREATMENTS = (
    FIGURE_DIR
    / "02_biodegradation_by_treatment.png"
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

TREATMENT_ORDER = [
    "Te",
    "R",
    "T",
    "RT",
]

TIME_ORDER = [
    5,
    10,
    20,
    40,
]


# ============================================================
# PROGRAMA
# ============================================================

def main():

    TABLE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    FIGURE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Lectura
    # --------------------------------------------------------

    df = pd.read_csv(INPUT_FILE)

    # --------------------------------------------------------
    # Validación
    # --------------------------------------------------------

    required_columns = {
        "sample_code",
        "treatment",
        "time_days",
        "replicate",
        "initial_atrazine_nominal_ppm",
        "include_analysis",
        "biodegradation_pct",
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Faltan columnas requeridas: "
            + ", ".join(sorted(missing_columns))
        )

    if len(df) != 48:
        raise ValueError(
            f"Se esperaban 48 observaciones analíticas "
            f"y se encontraron {len(df)}."
        )

    observed_treatments = set(
        df["treatment"].astype(str).unique()
    )

    expected_treatments = set(TREATMENT_ORDER)

    if observed_treatments != expected_treatments:
        raise ValueError(
            "Los tratamientos encontrados no corresponden "
            "a Te, R, T y RT. "
            f"Encontrados: {sorted(observed_treatments)}"
        )

    if "B" in observed_treatments:
        raise ValueError(
            "ERROR: B aparece en el dataset analítico."
        )

    if not df["include_analysis"].all():
        raise ValueError(
            "El dataset analítico contiene observaciones "
            "marcadas como include_analysis=False."
        )

    if not (
        df["initial_atrazine_nominal_ppm"] == 500
    ).all():
        raise ValueError(
            "El dataset analítico contiene una concentración "
            "nominal distinta de 500 ppm."
        )

    counts = (
        df
        .groupby(
            ["treatment", "time_days"]
        )
        .size()
        .unstack(fill_value=0)
        .reindex(
            index=TREATMENT_ORDER,
            columns=TIME_ORDER
        )
    )

    if not (counts == 3).all().all():
        raise ValueError(
            "El diseño no corresponde a "
            "4 tratamientos × 4 tiempos × 3 réplicas."
        )

    # --------------------------------------------------------
    # Orden
    # --------------------------------------------------------

    df["treatment"] = pd.Categorical(
        df["treatment"],
        categories=TREATMENT_ORDER,
        ordered=True
    )

    df = df.sort_values(
        [
            "treatment",
            "time_days",
            "replicate",
        ]
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Tabla de observaciones individuales
    # --------------------------------------------------------

    individual = df[
        [
            "sample_code",
            "treatment",
            "time_days",
            "replicate",
            "initial_atrazine_nominal_ppm",
            "biodegradation_pct",
        ]
    ].copy()

    individual.to_csv(
        OBSERVATIONS_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Estadística descriptiva
    # --------------------------------------------------------

    summary = (
        df
        .groupby(
            ["treatment", "time_days"],
            observed=True
        )
        ["biodegradation_pct"]
        .agg(
            n="count",
            mean="mean",
            sd="std",
            median="median",
            minimum="min",
            maximum="max",
        )
        .reset_index()
    )

    summary.to_csv(
        SUMMARY_FILE,
        index=False
    )

    # --------------------------------------------------------
    # FIGURA 1
    # Media ± desviación estándar
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(8, 6)
    )

    for treatment in TREATMENT_ORDER:

        subset = summary[
            summary["treatment"] == treatment
        ].sort_values("time_days")

        ax.errorbar(
            subset["time_days"],
            subset["mean"],
            yerr=subset["sd"],
            marker="o",
            capsize=4,
            label=treatment
        )

    ax.set_xlabel("Time (days)")
    ax.set_ylabel("Biodegradation (%)")
    ax.set_xticks(TIME_ORDER)

    ax.legend(
        title="Treatment"
    )

    fig.tight_layout()

    fig.savefig(
        FIG_TRAJECTORIES,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    # --------------------------------------------------------
    # FIGURA 2
    # Todas las observaciones individuales
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(8, 6)
    )

    markers = {
        "Te": "s",
        "R": "^",
        "T": "D",
        "RT": "v",
    }

    for treatment in TREATMENT_ORDER:

        subset = df[
            df["treatment"] == treatment
        ]

        ax.scatter(
            subset["time_days"],
            subset["biodegradation_pct"],
            marker=markers[treatment],
            label=treatment,
            alpha=0.8
        )

    ax.set_xlabel("Time (days)")
    ax.set_ylabel("Biodegradation (%)")
    ax.set_xticks(TIME_ORDER)

    ax.legend(
        title="Treatment"
    )

    fig.tight_layout()

    fig.savefig(
        FIG_INDIVIDUAL,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    # --------------------------------------------------------
    # FIGURA 3
    # Panel independiente por tratamiento
    # --------------------------------------------------------

    fig, axes = plt.subplots(
        nrows=4,
        ncols=1,
        figsize=(7, 12),
        sharex=True,
        sharey=True
    )

    for ax, treatment in zip(
        axes,
        TREATMENT_ORDER
    ):

        raw_subset = df[
            df["treatment"] == treatment
        ]

        mean_subset = summary[
            summary["treatment"] == treatment
        ].sort_values("time_days")

        ax.scatter(
            raw_subset["time_days"],
            raw_subset["biodegradation_pct"],
            alpha=0.7
        )

        ax.errorbar(
            mean_subset["time_days"],
            mean_subset["mean"],
            yerr=mean_subset["sd"],
            marker="o",
            capsize=4
        )

        ax.set_title(
            f"Treatment {treatment}"
        )

        ax.set_ylabel(
            "Biodegradation (%)"
        )

        ax.set_xticks(TIME_ORDER)

    axes[-1].set_xlabel(
        "Time (days)"
    )

    fig.tight_layout()

    fig.savefig(
        FIG_TREATMENTS,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    # --------------------------------------------------------
    # SALIDA EN TERMINAL
    # --------------------------------------------------------

    print("=" * 80)
    print("EXPLORACIÓN DESCRIPTIVA — LABORATORIO")
    print("=" * 80)

    print("\nNúmero de observaciones:")
    print(len(df))

    print("\nDiseño:")
    print(counts.to_string())

    print(
        "\nBiodegradación (%) por tratamiento y tiempo:"
    )

    print(
        summary.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )

    print("\nArchivos generados:")
    print(SUMMARY_FILE)
    print(OBSERVATIONS_FILE)
    print(FIG_TRAJECTORIES)
    print(FIG_INDIVIDUAL)
    print(FIG_TREATMENTS)


if __name__ == "__main__":
    main()
