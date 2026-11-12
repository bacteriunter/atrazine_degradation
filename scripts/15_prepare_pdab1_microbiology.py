#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
15_prepare_pdab1_microbiology.py

Construye un dataset estructurado a partir de:

    data/raw/pdab1_bacterias.xlsx

Hojas incluidas en esta etapa:
    - Actinomicetos
    - PDA acidificado
    - Extracto de suelo

Estructura experimental confirmada:
    suelo -> dilución -> bloque -> repetición

Suelos:
    ST = Tepantitla
    SC = Capulin
    SS = Santa Ana

Bloques:
    B1, B2, B3

Repeticiones:
    1, 2, 3

Conversión documentada en las fórmulas originales:

    UFC = colony_count * 10^d / inoculated_volume_ml

Factores observados en el archivo original:
    Tepantitla = 0.842
    Capulin    = 0.851
    Santa Ana  = 0.948

IMPORTANTE:
- No se modifica el Excel original.
- Se conserva la UFC reportada.
- Se recalcula una UFC independiente desde el conteo.
- No se corrigen silenciosamente los valores originales.
- No se realizan pruebas estadísticas.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import load_workbook


# ============================================================
# RUTAS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "pdab1_bacterias.xlsx"
)

OUTPUT_DATA = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "pdab1_microbiology.csv"
)

OUTPUT_MISMATCH = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "15_pdab1_cfu_per_ml_mismatches.csv"
)

OUTPUT_VALIDATION = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "15_pdab1_microbiology_validation.txt"
)


# ============================================================
# DEFINICIONES
# ============================================================

SOILS = {
    "ST": {
        "soil": "Tepantitla",
        "factor": 0.842,
    },
    "SC": {
        "soil": "Capulin",
        "factor": 0.851,
    },
    "SS": {
        "soil": "Santa Ana",
        "factor": 0.948,
    },
}


# ------------------------------------------------------------
# Cada bloque especifica:
#
# sheet
# microbial_group / medium
# soil
# dilution
# fila inicial
# columnas conteo/UFC para B1-B3
#
# Las coordenadas se basan en la estructura observada
# directamente en el libro.
# ------------------------------------------------------------

CONFIG = {

    "Actinomicetos": {
        "group": "Actinomicetos",
        "blocks": [
            # dilution 10^-3
            {
                "d": 3,
                "rows": [2, 3, 4],
                "ST": [("B", "C"), ("D", "E"), ("F", "G")],
                "SC": [("I", "J"), ("K", "L"), ("M", "N")],
                "SS": [("Q", "R"), ("S", "T"), ("U", "V")],
            },

            # dilution 10^-4
            {
                "d": 4,
                "rows": [6, 7, 8],
                "ST": [("B", "C"), ("D", "E"), ("F", "G")],
                "SC": [("I", "J"), ("K", "L"), ("M", "N")],
                "SS": [("Q", "R"), ("S", "T"), ("U", "V")],
            },

            # dilution 10^-5
            {
                "d": 5,
                "rows": [10, 11, 12],
                "ST": [("B", "C"), ("D", "E"), ("F", "G")],
                "SC": [("I", "J"), ("K", "L"), ("M", "N")],
                "SS": [("Q", "R"), ("S", "T"), ("U", "V")],
            },
        ],
    },

    "PDA acidificado": {
        "group": "PDA acidificado",
        "blocks": [
            {
                "d": 3,
                "rows": [2, 3, 4],
                "ST": [("B", "C"), ("D", "E"), ("F", "G")],
                "SC": [("I", "J"), ("K", "L"), ("M", "N")],
                "SS": [("P", "Q"), ("R", "S"), ("T", "U")],
            },
            {
                "d": 4,
                "rows": [7, 8, 9],
                "ST": [("B", "C"), ("D", "E"), ("F", "G")],
                "SC": [("I", "J"), ("K", "L"), ("M", "N")],
                "SS": [("P", "Q"), ("R", "S"), ("T", "U")],
            },
            {
                "d": 5,
                "rows": [12, 13, 14],
                "ST": [("B", "C"), ("D", "E"), ("F", "G")],
                "SC": [("I", "J"), ("K", "L"), ("M", "N")],
                "SS": [("P", "Q"), ("R", "S"), ("T", "U")],
            },
        ],
    },

    "Extracto de suelo": {
        "group": "Extracto de suelo",
        "blocks": [
            {
                "d": 3,
                "rows": [2, 3, 4],
                "ST": [("B", "C"), ("D", "E"), ("F", "G")],
                "SC": [("I", "J"), ("K", "L"), ("M", "N")],
                "SS": [("P", "Q"), ("R", "S"), ("T", "U")],
            },
            {
                "d": 4,
                "rows": [7, 8, 9],
                "ST": [("B", "C"), ("D", "E"), ("F", "G")],
                "SC": [("I", "J"), ("K", "L"), ("M", "N")],
                "SS": [("P", "Q"), ("R", "S"), ("T", "U")],
            },
            {
                "d": 5,
                "rows": [12, 13, 14],
                "ST": [("B", "C"), ("D", "E"), ("F", "G")],
                "SC": [("I", "J"), ("K", "L"), ("M", "N")],
                "SS": [("P", "Q"), ("R", "S"), ("T", "U")],
            },
        ],
    },
}


# ============================================================
# FUNCIONES
# ============================================================

def numeric_or_nan(value):
    """Convierte un valor numérico a float."""

    if value is None:
        return np.nan

    if isinstance(
        value,
        (int, float, np.integer, np.floating)
    ):
        return float(value)

    return np.nan


def main():

    OUTPUT_DATA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_VALIDATION.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Dos aperturas:
    #
    # wb_values   -> resultado calculado guardado por Excel
    # wb_formulas -> fórmula original para trazabilidad
    # --------------------------------------------------------

    wb_values = load_workbook(
        INPUT_FILE,
        data_only=True
    )

    wb_formulas = load_workbook(
        INPUT_FILE,
        data_only=False
    )

    records = []

    # ========================================================
    # EXTRACCIÓN
    # ========================================================

    for sheet_name, sheet_config in CONFIG.items():

        ws_values = wb_values[sheet_name]
        ws_formulas = wb_formulas[sheet_name]

        group = sheet_config["group"]

        for dilution_block in sheet_config["blocks"]:

            d = dilution_block["d"]

            dilution_factor = 10 ** d

            rows = dilution_block["rows"]

            for soil_code, soil_info in SOILS.items():

                soil = soil_info["soil"]

                inoculated_volume_ml = (
                    soil_info["factor"]
                )

                column_pairs = (
                    dilution_block[soil_code]
                )

                for block_number, (
                    count_col,
                    ufc_col
                ) in enumerate(
                    column_pairs,
                    start=1
                ):

                    block = f"B{block_number}"

                    for replicate, row in enumerate(
                        rows,
                        start=1
                    ):

                        count_cell = (
                            f"{count_col}{row}"
                        )

                        cfu_cell = (
                            f"{ufc_col}{row}"
                        )

                        colony_count = numeric_or_nan(
                            ws_values[
                                count_cell
                            ].value
                        )

                        cfu_per_ml_reported = numeric_or_nan(
                            ws_values[
                                cfu_cell
                            ].value
                        )

                        ufc_formula = (
                            ws_formulas[
                                cfu_cell
                            ].value
                        )

                        # ----------------------------
                        # Recalcular UFC
                        # ----------------------------

                        if pd.notna(colony_count):

                            cfu_per_ml_recalculated = (
                                colony_count
                                * dilution_factor
                                / inoculated_volume_ml
                            )

                        else:

                            cfu_per_ml_recalculated = np.nan

                        # ----------------------------
                        # Diferencia
                        # ----------------------------

                        if (
                            pd.notna(cfu_per_ml_reported)
                            and
                            pd.notna(cfu_per_ml_recalculated)
                        ):

                            cfu_per_ml_difference = (
                                cfu_per_ml_reported
                                - cfu_per_ml_recalculated
                            )

                            cfu_per_ml_abs_difference = abs(
                                cfu_per_ml_difference
                            )

                            cfu_per_ml_match = bool(
                                np.isclose(
                                    cfu_per_ml_reported,
                                    cfu_per_ml_recalculated,
                                    rtol=1e-6,
                                    atol=1e-6,
                                )
                            )

                        else:

                            cfu_per_ml_difference = np.nan
                            cfu_per_ml_abs_difference = np.nan
                            cfu_per_ml_match = False

                        records.append(
                            {
                                "sheet":
                                    sheet_name,

                                "microbial_group":
                                    group,

                                "soil_code":
                                    soil_code,

                                "soil":
                                    soil,

                                "dilution_exponent":
                                    d,

                                "dilution":
                                    f"10^-{d}",

                                "block":
                                    block,

                                "replicate":
                                    replicate,

                                "source_row":
                                    row,

                                "count_cell":
                                    count_cell,

                                "cfu_cell":
                                    cfu_cell,

                                "colony_count":
                                    colony_count,

                                "inoculated_volume_ml":
                                    inoculated_volume_ml,

                                "cfu_per_ml_reported":
                                    cfu_per_ml_reported,

                                "cfu_formula_original":
                                    ufc_formula,

                                "cfu_per_ml_recalculated":
                                    cfu_per_ml_recalculated,

                                "cfu_per_ml_difference":
                                    cfu_per_ml_difference,

                                "cfu_per_ml_abs_difference":
                                    cfu_per_ml_abs_difference,

                                "cfu_per_ml_match":
                                    cfu_per_ml_match,
                            }
                        )

    # ========================================================
    # DATAFRAME
    # ========================================================

    df = pd.DataFrame(records)

    # --------------------------------------------------------
    # Guardar dataset completo
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_DATA,
        index=False
    )

    # --------------------------------------------------------
    # Inconsistencias
    # --------------------------------------------------------

    mismatches = df.loc[
        ~df["cfu_per_ml_match"],
        [
            "sheet",
            "soil",
            "dilution",
            "block",
            "replicate",
            "count_cell",
            "cfu_cell",
            "colony_count",
            "cfu_per_ml_reported",
            "cfu_formula_original",
            "cfu_per_ml_recalculated",
            "cfu_per_ml_difference",
        ]
    ].copy()

    mismatches.to_csv(
        OUTPUT_MISMATCH,
        index=False
    )

    # ========================================================
    # VALIDACIONES
    # ========================================================

    expected_rows_per_sheet = (
        3   # diluciones
        * 3 # suelos
        * 3 # bloques
        * 3 # repeticiones
    )

    expected_total = (
        expected_rows_per_sheet
        * len(CONFIG)
    )

    structure = (
        df.groupby(
            [
                "sheet",
                "soil",
                "dilution",
                "block"
            ]
        )
        .size()
        .rename("n_replicates")
        .reset_index()
    )

    # ========================================================
    # REPORTE
    # ========================================================

    with OUTPUT_VALIDATION.open(
        "w",
        encoding="utf-8"
    ) as handle:

        handle.write(
            "=" * 90 + "\n"
        )

        handle.write(
            "VALIDACIÓN DEL DATASET "
            "MICROBIOLÓGICO\n"
        )

        handle.write(
            "=" * 90 + "\n\n"
        )

        handle.write(
            f"Filas procesadas: {len(df)}\n"
        )

        handle.write(
            f"Filas esperadas: {expected_total}\n"
        )

        handle.write(
            f"Filas esperadas por hoja: "
            f"{expected_rows_per_sheet}\n\n"
        )

        handle.write(
            "HOJAS INCLUIDAS\n"
        )

        handle.write(
            "-" * 90 + "\n"
        )

        for sheet in CONFIG:
            handle.write(
                f"- {sheet}\n"
            )

        handle.write("\n")

        handle.write(
            "FACTORES ESPECÍFICOS DEL SUELO\n"
        )

        handle.write(
            "-" * 90 + "\n"
        )

        for code, info in SOILS.items():

            handle.write(
                f"{code} -> "
                f"{info['soil']}: "
                f"{info['factor']}\n"
            )

        handle.write("\n")

        handle.write(
            "ESTRUCTURA EXPERIMENTAL\n"
        )

        handle.write(
            "-" * 90 + "\n"
        )

        handle.write(
            structure.to_string(
                index=False
            )
        )

        handle.write("\n\n")

        handle.write(
            "CONTEOS AUSENTES\n"
        )

        handle.write(
            "-" * 90 + "\n"
        )

        handle.write(
            f"{df['colony_count'].isna().sum()}\n\n"
        )

        handle.write(
            "UFC REPORTADAS AUSENTES\n"
        )

        handle.write(
            "-" * 90 + "\n"
        )

        handle.write(
            f"{df['cfu_per_ml_reported'].isna().sum()}\n\n"
        )

        handle.write(
            "COINCIDENCIA UFC ORIGINAL "
            "VS RECALCULADA\n"
        )

        handle.write(
            "-" * 90 + "\n"
        )

        handle.write(
            df["cfu_per_ml_match"]
            .value_counts(
                dropna=False
            )
            .to_string()
        )

        handle.write("\n\n")

        handle.write(
            f"Inconsistencias detectadas: "
            f"{len(mismatches)}\n\n"
        )

        if len(mismatches) > 0:

            handle.write(
                "DETALLE DE INCONSISTENCIAS\n"
            )

            handle.write(
                "-" * 90 + "\n"
            )

            handle.write(
                mismatches.to_string(
                    index=False
                )
            )

            handle.write("\n\n")

        handle.write(
            "DECISIONES DE PROCESAMIENTO\n"
        )

        handle.write(
            "-" * 90 + "\n"
        )

        handle.write(
            "1. colony_count conserva el "
            "conteo primario del Excel.\n"
        )

        handle.write(
            "2. cfu_per_ml_reported conserva el resultado "
            "almacenado originalmente.\n"
        )

        handle.write(
            "3. cfu_per_ml_recalculated expresa la UFC/mL "
            "recalculada desde el conteo primario.\n"
        )

        handle.write(
            "4. El cálculo utilizado es: colony_count * 10^d / "
            "inoculated_volume_ml.\n"
        )

        handle.write(
            "5. Los volúmenes inoculados son 0.842 mL para Tepantitla, "
            "0.851 mL para Capulin y 0.948 mL para Santa Ana.\n"
        )

        handle.write(
            "6. Los errores inequívocos de las fórmulas originales  "
            "no se propagan al valor recalculado.\n"
        )

        handle.write(
            "7. No se realizaron pruebas "
            "estadísticas.\n"
        )

        handle.write(
            "8. No se modificó el archivo "
            "original.\n"
        )

        handle.write(
            "9. Bacterias PDA serie 1 se "
            "procesará separadamente.\n"
        )

    # ========================================================
    # TERMINAL
    # ========================================================

    print("=" * 90)
    print(
        "DATASET MICROBIOLÓGICO PREPARADO"
    )
    print("=" * 90)

    print(
        f"\nFilas: {len(df)} "
        f"(esperadas: {expected_total})"
    )

    print(
        f"\nInconsistencias UFC: "
        f"{len(mismatches)}"
    )

    print(
        f"\nDataset:\n{OUTPUT_DATA}"
    )

    print(
        f"\nInconsistencias:\n"
        f"{OUTPUT_MISMATCH}"
    )

    print(
        f"\nValidación:\n"
        f"{OUTPUT_VALIDATION}"
    )


if __name__ == "__main__":
    main()
