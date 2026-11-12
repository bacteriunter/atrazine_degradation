#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
08_prepare_growth_inhibition.py

Preparación reproducible de Base 2:
pruebas de crecimiento/inhibición frente a atrazina.

FUENTE VÁLIDA:
    data/raw/base_2.xlsx
    Hoja1

DECISIONES DOCUMENTADAS:
- Hoja1 es la fuente primaria/correcta.
- Hoja2 no se utiliza para análisis.
- Las columnas CMI y CMI.1 están vacías y se excluyen
  del dataset procesado.
- Rhizobium sp corresponde al tratamiento R de Base 1.
- Trichoderma 1 corresponde al tratamiento T de Base 1.
- No se calculan valores de CMI.
- No se realizan pruebas estadísticas.
- No se modifican los datos raw.

Salidas:
    data/processed/growth_inhibition.csv
    data/processed/growth_inhibition_base1_isolates.csv
    results/tables/08_growth_inhibition_validation.txt
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# RUTAS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "base_2.xlsx"
)

PROCESSED_DIR = (
    PROJECT_DIR
    / "data"
    / "processed"
)

TABLE_DIR = (
    PROJECT_DIR
    / "results"
    / "tables"
)

OUTPUT_ALL = (
    PROCESSED_DIR
    / "growth_inhibition.csv"
)

OUTPUT_LINKED = (
    PROCESSED_DIR
    / "growth_inhibition_base1_isolates.csv"
)

VALIDATION_FILE = (
    TABLE_DIR
    / "08_growth_inhibition_validation.txt"
)


# ============================================================
# COLUMNAS ORIGINALES
# ============================================================

COL_GENUS = "Género"
COL_CONTROL = "Ø micro-control (mm)"
COL_TIME = "tiempo crecimiento (días)"
COL_LOW_GROWTH = "Ø de crecimiento  de 0-2500 ppm"

COL_INH_5000 = "Ø de inhibición mm (5000 ppm)"
COL_GROWTH_5000 = "Ø crecimiento(5000)"
COL_PCT_GROWTH_5000 = "%Crecimiento-5000"
COL_PCT_INH_5000 = "% CI a 5000 ppm"

COL_INH_7500 = "Ø mm de inhibición (7500 ppm)"
COL_GROWTH_7500 = "Ø crecimiento-7500"
COL_PCT_GROWTH_7500 = "%creci-7500"
COL_PCT_INH_7500 = "%CI-7500"

COL_INH_10000 = "Ø mm inhibición(10000 ppm)"
COL_GROWTH_10000 = "Ø crecimien-10000"
COL_PCT_GROWTH_10000 = "% crecim-10000"
COL_PCT_INH_10000 = "%CI-10000"

COL_RATE = "Velocidad de crecimiento"

COL_REFERENCE = (
    "referencias donde se mencionan que resieten conc. De atrazina"
)


# ============================================================
# PROGRAMA
# ============================================================

def main():

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    TABLE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Lectura: SOLO Hoja1
    # --------------------------------------------------------

    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name="Hoja1"
    )

    # --------------------------------------------------------
    # Validaciones básicas
    # --------------------------------------------------------

    if len(raw) != 31:
        raise ValueError(
            f"Se esperaban 31 filas en Hoja1; "
            f"se encontraron {len(raw)}."
        )

    required_columns = {
        COL_GENUS,
        COL_CONTROL,
        COL_TIME,
        COL_LOW_GROWTH,
        COL_INH_5000,
        COL_GROWTH_5000,
        COL_PCT_GROWTH_5000,
        COL_PCT_INH_5000,
        COL_INH_7500,
        COL_GROWTH_7500,
        COL_PCT_GROWTH_7500,
        COL_PCT_INH_7500,
        COL_INH_10000,
        COL_GROWTH_10000,
        COL_PCT_GROWTH_10000,
        COL_PCT_INH_10000,
        COL_RATE,
        COL_REFERENCE,
    }

    missing = required_columns - set(raw.columns)

    if missing:
        raise ValueError(
            "Faltan columnas requeridas: "
            + ", ".join(sorted(missing))
        )

    # --------------------------------------------------------
    # Construcción del dataset procesado
    # --------------------------------------------------------

    df = pd.DataFrame()

    # Identificador interno reproducible
    df["microorganism_id"] = [
        f"M{i:02d}"
        for i in range(1, len(raw) + 1)
    ]

    # Nombre original, sin reinterpretación taxonómica
    df["microorganism"] = (
        raw[COL_GENUS]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # Variables de crecimiento
    # --------------------------------------------------------

    df["control_diameter_mm"] = (
        pd.to_numeric(
            raw[COL_CONTROL],
            errors="coerce"
        )
    )

    df["growth_time_days"] = (
        pd.to_numeric(
            raw[COL_TIME],
            errors="coerce"
        )
    )

    df["growth_0_2500_diameter_mm"] = (
        pd.to_numeric(
            raw[COL_LOW_GROWTH],
            errors="coerce"
        )
    )

    df["growth_rate_mm_day"] = (
        pd.to_numeric(
            raw[COL_RATE],
            errors="coerce"
        )
    )

    # --------------------------------------------------------
    # 5000 ppm
    # --------------------------------------------------------

    df["inhibition_diameter_5000_mm"] = (
        pd.to_numeric(
            raw[COL_INH_5000],
            errors="coerce"
        )
    )

    df["growth_diameter_5000_mm"] = (
        pd.to_numeric(
            raw[COL_GROWTH_5000],
            errors="coerce"
        )
    )

    df["growth_pct_5000"] = (
        pd.to_numeric(
            raw[COL_PCT_GROWTH_5000],
            errors="coerce"
        )
    )

    df["inhibition_pct_5000"] = (
        pd.to_numeric(
            raw[COL_PCT_INH_5000],
            errors="coerce"
        )
    )

    # --------------------------------------------------------
    # 7500 ppm
    # --------------------------------------------------------

    df["inhibition_diameter_7500_mm"] = (
        pd.to_numeric(
            raw[COL_INH_7500],
            errors="coerce"
        )
    )

    df["growth_diameter_7500_mm"] = (
        pd.to_numeric(
            raw[COL_GROWTH_7500],
            errors="coerce"
        )
    )

    df["growth_pct_7500"] = (
        pd.to_numeric(
            raw[COL_PCT_GROWTH_7500],
            errors="coerce"
        )
    )

    df["inhibition_pct_7500"] = (
        pd.to_numeric(
            raw[COL_PCT_INH_7500],
            errors="coerce"
        )
    )

    # --------------------------------------------------------
    # 10000 ppm
    # --------------------------------------------------------

    df["inhibition_diameter_10000_mm"] = (
        pd.to_numeric(
            raw[COL_INH_10000],
            errors="coerce"
        )
    )

    df["growth_diameter_10000_mm"] = (
        pd.to_numeric(
            raw[COL_GROWTH_10000],
            errors="coerce"
        )
    )

    df["growth_pct_10000"] = (
        pd.to_numeric(
            raw[COL_PCT_GROWTH_10000],
            errors="coerce"
        )
    )

    df["inhibition_pct_10000"] = (
        pd.to_numeric(
            raw[COL_PCT_INH_10000],
            errors="coerce"
        )
    )

    # --------------------------------------------------------
    # Referencia original
    # --------------------------------------------------------

    df["reference_original"] = (
        raw[COL_REFERENCE]
    )

    # --------------------------------------------------------
    # Correspondencia con Base 1
    # --------------------------------------------------------

    df["linked_to_base1"] = False
    df["base1_treatment"] = pd.NA

    rhizobium_mask = (
        df["microorganism"] == "Rhizobium sp"
    )

    trichoderma_mask = (
        df["microorganism"] == "Trichoderma 1"
    )

    if rhizobium_mask.sum() != 1:
        raise ValueError(
            "No se encontró exactamente una fila "
            "para 'Rhizobium sp'."
        )

    if trichoderma_mask.sum() != 1:
        raise ValueError(
            "No se encontró exactamente una fila "
            "para 'Trichoderma 1'."
        )

    df.loc[
        rhizobium_mask,
        "linked_to_base1"
    ] = True

    df.loc[
        rhizobium_mask,
        "base1_treatment"
    ] = "R"

    df.loc[
        trichoderma_mask,
        "linked_to_base1"
    ] = True

    df.loc[
        trichoderma_mask,
        "base1_treatment"
    ] = "T"

    # --------------------------------------------------------
    # Validaciones algebraicas
    #
    # Estas NO modifican los datos.
    # Solo comprueban relaciones presentes en la hoja.
    # --------------------------------------------------------

    concentrations = [
        5000,
        7500,
        10000,
    ]

    algebra_checks = {}

    for conc in concentrations:

        growth_col = f"growth_pct_{conc}"
        inhibition_col = f"inhibition_pct_{conc}"

        expected = (
            df[growth_col]
            + df[inhibition_col]
        )

        valid = np.isclose(
            expected,
            100.0,
            atol=1e-8,
            equal_nan=False
        )

        algebra_checks[conc] = bool(
            valid.all()
        )

    # --------------------------------------------------------
    # Dataset completo
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_ALL,
        index=False
    )

    # --------------------------------------------------------
    # Dataset vinculado a Base 1
    # --------------------------------------------------------

    linked = (
        df.loc[
            df["linked_to_base1"]
        ]
        .copy()
        .sort_values(
            "base1_treatment"
        )
    )

    linked.to_csv(
        OUTPUT_LINKED,
        index=False
    )

    # --------------------------------------------------------
    # Reporte de validación
    # --------------------------------------------------------

    with VALIDATION_FILE.open(
        "w",
        encoding="utf-8"
    ) as handle:

        handle.write(
            "=" * 72 + "\n"
        )

        handle.write(
            "VALIDACIÓN — BASE 2: CRECIMIENTO / INHIBICIÓN\n"
        )

        handle.write(
            "=" * 72 + "\n\n"
        )

        handle.write(
            "Fuente utilizada: base_2.xlsx / Hoja1\n"
        )

        handle.write(
            "Hoja2 excluida del procesamiento analítico.\n"
        )

        handle.write(
            "Razón: el usuario confirmó que Hoja1 "
            "contiene los datos correctos.\n\n"
        )

        handle.write(
            f"Filas originales Hoja1: {len(raw)}\n"
        )

        handle.write(
            f"Filas dataset procesado: {len(df)}\n"
        )

        handle.write(
            f"Microorganismos vinculados a Base 1: "
            f"{len(linked)}\n\n"
        )

        handle.write(
            "COLUMNAS CMI\n"
        )

        handle.write(
            "-" * 72 + "\n"
        )

        for col in ["CMI", "CMI.1"]:

            if col in raw.columns:

                handle.write(
                    f"{col}: "
                    f"{raw[col].isna().sum()}/{len(raw)} "
                    f"valores faltantes\n"
                )

        handle.write(
            "\nNo se calculó ni imputó CMI.\n\n"
        )

        handle.write(
            "VALIDACIÓN ALGEBRAICA\n"
        )

        handle.write(
            "-" * 72 + "\n"
        )

        for conc in concentrations:

            handle.write(
                f"% crecimiento + % inhibición = 100 "
                f"a {conc} ppm: "
                f"{algebra_checks[conc]}\n"
            )

        handle.write(
            "\nAISLAMIENTOS VINCULADOS A BASE 1\n"
        )

        handle.write(
            "-" * 72 + "\n"
        )

        columns_to_show = [
            "base1_treatment",
            "microorganism",
            "growth_time_days",
            "growth_rate_mm_day",
            "inhibition_pct_5000",
            "inhibition_pct_7500",
            "inhibition_pct_10000",
        ]

        handle.write(
            linked[
                columns_to_show
            ].to_string(
                index=False
            )
        )

        handle.write("\n\n")

        handle.write(
            "No se realizaron pruebas estadísticas.\n"
        )

        handle.write(
            "No se calcularon valores de CMI.\n"
        )

        handle.write(
            "No se utilizaron datos de Hoja2.\n"
        )

    # --------------------------------------------------------
    # TERMINAL
    # --------------------------------------------------------

    print("=" * 72)
    print(
        "PREPARACIÓN BASE 2 COMPLETADA"
    )
    print("=" * 72)

    print(
        f"\nDataset completo: {OUTPUT_ALL}"
    )

    print(
        f"Dataset vinculado a Base 1: {OUTPUT_LINKED}"
    )

    print(
        f"Validación: {VALIDATION_FILE}"
    )

    print(
        "\nMicroorganismos vinculados a Base 1:"
    )

    print(
        linked[
            [
                "base1_treatment",
                "microorganism",
                "growth_time_days",
                "growth_rate_mm_day",
                "inhibition_pct_5000",
                "inhibition_pct_7500",
                "inhibition_pct_10000",
            ]
        ].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
