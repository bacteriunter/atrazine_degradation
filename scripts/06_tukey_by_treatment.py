#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
06_tukey_by_treatment.py

Comparaciones múltiples entre tiempos dentro de cada tratamiento
del experimento de degradación de atrazina en laboratorio.

Entrada:
    data/processed/lab_degradation_analysis.csv

Diseño:
    4 tratamientos × 4 tiempos × 3 réplicas
    = 48 unidades experimentales independientes.

Antecedente:
    El ANOVA factorial mostró interacción significativa
    Treatment × Time.

Objetivo:
    Comparar 5, 10, 20 y 40 días dentro de cada tratamiento:
        Te
        R
        T
        RT

Método:
    Tukey HSD aplicado independientemente dentro de cada tratamiento.

Cada tratamiento constituye una familia de 6 comparaciones.

NO se eliminan observaciones.
NO se transforma la respuesta.
"""

from pathlib import Path

import pandas as pd
from statsmodels.stats.multicomp import pairwise_tukeyhsd


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

TABLE_DIR = (
    PROJECT_DIR
    / "results"
    / "tables"
)

ALL_RESULTS_FILE = (
    TABLE_DIR
    / "06_tukey_by_treatment_all.csv"
)

MEANS_FILE = (
    TABLE_DIR
    / "06_tukey_by_treatment_means.csv"
)

REPORT_FILE = (
    TABLE_DIR
    / "06_tukey_by_treatment_report.txt"
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

TREATMENTS = [
    "Te",
    "R",
    "T",
    "RT",
]

TIMES = [
    5,
    10,
    20,
    40,
]

ALPHA = 0.05


# ============================================================
# PROGRAMA
# ============================================================

def main():

    TABLE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Lectura
    # --------------------------------------------------------

    df = pd.read_csv(INPUT_FILE)

    # --------------------------------------------------------
    # Validaciones
    # --------------------------------------------------------

    required_columns = {
        "sample_code",
        "treatment",
        "time_days",
        "replicate",
        "include_analysis",
        "biodegradation_pct",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            "Faltan columnas requeridas: "
            + ", ".join(sorted(missing))
        )

    if len(df) != 48:
        raise ValueError(
            f"Se esperaban 48 observaciones; "
            f"se encontraron {len(df)}."
        )

    if set(df["treatment"].unique()) != set(TREATMENTS):
        raise ValueError(
            "Los tratamientos no corresponden "
            "a Te, R, T y RT."
        )

    if set(df["time_days"].unique()) != set(TIMES):
        raise ValueError(
            "Los tiempos no corresponden "
            "a 5, 10, 20 y 40 días."
        )

    if not df["include_analysis"].all():
        raise ValueError(
            "Hay observaciones no elegibles "
            "en el dataset analítico."
        )

    if df["biodegradation_pct"].isna().any():
        raise ValueError(
            "Hay valores faltantes en biodegradation_pct."
        )

    counts = (
        df
        .groupby(
            ["treatment", "time_days"]
        )
        .size()
        .unstack(fill_value=0)
        .reindex(
            index=TREATMENTS,
            columns=TIMES
        )
    )

    if not (counts == 3).all().all():
        raise ValueError(
            "El diseño no corresponde a "
            "4 × 4 × 3."
        )

    # --------------------------------------------------------
    # Medias descriptivas
    # --------------------------------------------------------

    means = (
        df
        .groupby(
            ["treatment", "time_days"]
        )
        ["biodegradation_pct"]
        .agg(
            n="count",
            mean="mean",
            sd="std"
        )
        .reset_index()
    )

    means["treatment"] = pd.Categorical(
        means["treatment"],
        categories=TREATMENTS,
        ordered=True
    )

    means = means.sort_values(
        ["treatment", "time_days"]
    )

    means.to_csv(
        MEANS_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Tukey HSD dentro de cada tratamiento
    # --------------------------------------------------------

    all_results = []
    text_results = []

    for treatment in TREATMENTS:

        subset = df.loc[
            df["treatment"] == treatment
        ].copy()

        # Se convierte el tiempo a texto para que Tukey
        # lo trate explícitamente como grupo categórico.
        subset["time_group"] = (
            subset["time_days"]
            .astype(int)
            .astype(str)
        )

        tukey = pairwise_tukeyhsd(
            endog=subset["biodegradation_pct"],
            groups=subset["time_group"],
            alpha=ALPHA
        )

        table_data = tukey._results_table.data

        result = pd.DataFrame(
            table_data[1:],
            columns=table_data[0]
        )

        result.insert(
            0,
            "treatment",
            treatment
        )

        all_results.append(result)

        individual_file = (
            TABLE_DIR
            / f"06_tukey_treatment_{treatment}.csv"
        )

        result.to_csv(
            individual_file,
            index=False
        )

        text_results.append(
            "=" * 72
        )

        text_results.append(
            f"TRATAMIENTO: {treatment}"
        )

        text_results.append(
            "=" * 72
        )

        text_results.append(
            str(tukey)
        )

        text_results.append("")

    # --------------------------------------------------------
    # Combinar las 24 comparaciones
    # --------------------------------------------------------

    combined = pd.concat(
        all_results,
        ignore_index=True
    )

    combined.to_csv(
        ALL_RESULTS_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Reporte
    # --------------------------------------------------------

    with REPORT_FILE.open(
        "w",
        encoding="utf-8"
    ) as handle:

        handle.write(
            "=" * 72 + "\n"
        )

        handle.write(
            "TUKEY HSD — TIEMPOS DENTRO DE CADA TRATAMIENTO\n"
        )

        handle.write(
            "=" * 72 + "\n\n"
        )

        handle.write(
            "Respuesta: biodegradation_pct\n"
        )

        handle.write(
            "Tratamientos: Te, R, T, RT\n"
        )

        handle.write(
            "Tiempos: 5, 10, 20, 40 días\n"
        )

        handle.write(
            "n = 3 por tratamiento × tiempo\n"
        )

        handle.write(
            "alpha = 0.05\n\n"
        )

        handle.write(
            "Cada tratamiento se analiza como una familia "
            "independiente de 6 comparaciones Tukey.\n\n"
        )

        handle.write(
            "MEDIAS DESCRIPTIVAS\n"
        )

        handle.write(
            "-" * 72 + "\n"
        )

        handle.write(
            means.to_string(
                index=False,
                float_format=lambda x: f"{x:.4f}"
            )
        )

        handle.write(
            "\n\n"
        )

        for block in text_results:
            handle.write(
                block + "\n"
            )

        handle.write(
            "\nNo se eliminaron observaciones.\n"
        )

        handle.write(
            "No se transformó la respuesta.\n"
        )

    # --------------------------------------------------------
    # TERMINAL
    # --------------------------------------------------------

    print("=" * 72)
    print(
        "TUKEY HSD — TIEMPOS DENTRO DE CADA TRATAMIENTO"
    )
    print("=" * 72)

    print("\nMedias descriptivas:")

    print(
        means.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )

    print()

    for block in text_results:
        print(block)

    print("\nArchivos generados:")
    print(ALL_RESULTS_FILE)
    print(MEANS_FILE)
    print(REPORT_FILE)

    for treatment in TREATMENTS:
        print(
            TABLE_DIR
            / f"06_tukey_treatment_{treatment}.csv"
        )


if __name__ == "__main__":
    main()
