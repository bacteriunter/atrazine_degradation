#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
05_tukey_by_time.py

Comparaciones múltiples entre tratamientos dentro de cada tiempo
del experimento de degradación de atrazina.

Entrada:
    data/processed/lab_degradation_analysis.csv

Diseño:
    4 tratamientos × 4 tiempos × 3 réplicas
    = 48 unidades experimentales independientes.

Antecedente:
    El ANOVA factorial mostró interacción significativa
    Treatment × Time.

Objetivo:
    Comparar Te, R, T y RT entre sí dentro de cada tiempo.

Método:
    Tukey HSD, aplicado independientemente en:
        5 días
        10 días
        20 días
        40 días

Cada tiempo constituye una familia de 6 comparaciones.

Se generan:
    - tabla completa de las 24 comparaciones;
    - tabla de medias por tratamiento y tiempo;
    - archivos individuales de Tukey para cada tiempo.

NO se eliminan observaciones.
NO se transforma la respuesta.
NO se comparan todavía tiempos dentro de cada tratamiento.
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
    / "05_tukey_by_time_all.csv"
)

MEANS_FILE = (
    TABLE_DIR
    / "05_tukey_by_time_means.csv"
)

REPORT_FILE = (
    TABLE_DIR
    / "05_tukey_by_time_report.txt"
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
            ["time_days", "treatment"]
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
        ["time_days", "treatment"]
    )

    means.to_csv(
        MEANS_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Tukey HSD por tiempo
    # --------------------------------------------------------

    all_results = []
    text_results = []

    for time in TIMES:

        subset = df.loc[
            df["time_days"] == time
        ].copy()

        tukey = pairwise_tukeyhsd(
            endog=subset["biodegradation_pct"],
            groups=subset["treatment"],
            alpha=ALPHA
        )

        # Tabla interna producida por statsmodels
        table_data = tukey._results_table.data

        result = pd.DataFrame(
            table_data[1:],
            columns=table_data[0]
        )

        result.insert(
            0,
            "time_days",
            time
        )

        all_results.append(result)

        # Guardar también archivo individual
        individual_file = (
            TABLE_DIR
            / f"05_tukey_day_{time}.csv"
        )

        result.to_csv(
            individual_file,
            index=False
        )

        # Salida legible
        text_results.append(
            "=" * 72
        )

        text_results.append(
            f"TIEMPO: {time} DÍAS"
        )

        text_results.append(
            "=" * 72
        )

        text_results.append(
            str(tukey)
        )

        text_results.append("")

    # --------------------------------------------------------
    # Combinar 24 comparaciones
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
            "TUKEY HSD — TRATAMIENTOS DENTRO DE CADA TIEMPO\n"
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
            "Cada tiempo se analiza como una familia "
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
            "\nNo se compararon tiempos "
            "dentro de cada tratamiento.\n"
        )

        handle.write(
            "No se eliminaron observaciones.\n"
        )

        handle.write(
            "No se transformó la respuesta.\n"
        )

    # --------------------------------------------------------
    # TERMINAL
    # --------------------------------------------------------

    print("=" * 72)
    print(
        "TUKEY HSD — TRATAMIENTOS DENTRO DE CADA TIEMPO"
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

    for time in TIMES:
        print(
            TABLE_DIR
            / f"05_tukey_day_{time}.csv"
        )


if __name__ == "__main__":
    main()
