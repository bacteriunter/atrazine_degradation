#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
16_prepare_pda_bacteria_fungi.py

Procesa la hoja:
    Bacterias PDA serie 1

del archivo:
    data/raw/pdab1_bacterias.xlsx

Genera dos datasets:
    1. Bacterias en PDA
    2. Hongos en PDA

PRINCIPIO DE PROCESAMIENTO
--------------------------
El conteo de colonias es el dato primario.

Las UFC se recalculan de forma reproducible mediante:

    UFC = colony_count * 10^d / inoculated_volume_ml

Factores documentados en las fórmulas originales:
    Tepantitla = 0.842
    Capulin    = 0.851
    Santa Ana  = 0.948

Las UFC originales y sus fórmulas se conservan únicamente
para trazabilidad.

No se realizan análisis estadísticos.
No se modifican los datos raw.
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

OUTPUT_BACTERIA = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "pdab1_pda_bacteria.csv"
)

OUTPUT_FUNGI = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "pdab1_pda_fungi.csv"
)

OUTPUT_ALL = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "pdab1_pda_bacteria_fungi.csv"
)

OUTPUT_AUDIT = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "16_pda_cfu_per_ml_audit.csv"
)

OUTPUT_VALIDATION = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "16_pda_bacteria_fungi_validation.txt"
)


# ============================================================
# FACTORES DEL SUELO
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


# ============================================================
# CONFIGURACIÓN EXPLÍCITA
# ============================================================
#
# Cada entrada representa:
#
#   grupo
#   suelo
#   dilución
#   filas correspondientes a las 3 repeticiones
#   columnas correspondientes a B1, B2 y B3
#
# Cada tupla:
#
#   ("columna_conteo", "columna_UFC_original")
#
# ============================================================


BACTERIA_CONFIG = [

    # --------------------------------------------------------
    # TEPANTITLA
    # --------------------------------------------------------

    {
        "soil_code": "ST",
        "d": 2,
        "rows": [2, 3, 4],
        "blocks": [
            ("B", "C"),
            ("D", "E"),
            ("F", "G"),
        ],
    },

    {
        "soil_code": "ST",
        "d": 3,
        "rows": [7, 8, 9],
        "blocks": [
            ("B", "C"),
            ("D", "E"),
            ("F", "G"),
        ],
    },

    {
        "soil_code": "ST",
        "d": 4,
        "rows": [12, 13, 14],
        "blocks": [
            ("B", "C"),
            ("D", "E"),
            ("F", "G"),
        ],
    },

    {
        "soil_code": "ST",
        "d": 5,
        "rows": [17, 18, 19],
        "blocks": [
            ("B", "C"),
            ("D", "E"),
            ("F", "G"),
        ],
    },

    # --------------------------------------------------------
    # CAPULIN
    # --------------------------------------------------------

    {
        "soil_code": "SC",
        "d": 3,
        "rows": [2, 3, 4],
        "blocks": [
            ("J", "K"),
            ("L", "M"),
            ("N", "O"),
        ],
    },

    {
        "soil_code": "SC",
        "d": 4,
        "rows": [7, 8, 9],
        "blocks": [
            ("J", "K"),
            ("L", "M"),
            ("N", "O"),
        ],
    },

    {
        "soil_code": "SC",
        "d": 5,
        "rows": [12, 13, 14],
        "blocks": [
            ("J", "K"),
            ("L", "M"),
            ("N", "O"),
        ],
    },

    # --------------------------------------------------------
    # SANTA ANA
    # --------------------------------------------------------

    {
        "soil_code": "SS",
        "d": 3,
        "rows": [2, 3, 4],
        "blocks": [
            ("R", "S"),
            ("T", "U"),
            ("V", "W"),
        ],
    },

    {
        "soil_code": "SS",
        "d": 4,
        "rows": [7, 8, 9],
        "blocks": [
            ("R", "S"),
            ("T", "U"),
            ("V", "W"),
        ],
    },

    {
        "soil_code": "SS",
        "d": 5,
        "rows": [12, 13, 14],
        "blocks": [
            ("R", "S"),
            ("T", "U"),
            ("V", "W"),
        ],
    },
]


FUNGI_CONFIG = [

    # --------------------------------------------------------
    # TEPANTITLA
    # --------------------------------------------------------

    {
        "soil_code": "ST",
        "d": 3,
        "rows": [23, 24, 25],
        "blocks": [
            ("B", "C"),
            ("D", "E"),
            ("F", "G"),
        ],
    },

    {
        "soil_code": "ST",
        "d": 4,
        "rows": [28, 29, 30],
        "blocks": [
            ("B", "C"),
            ("D", "E"),
            ("F", "G"),
        ],
    },

    {
        "soil_code": "ST",
        "d": 5,
        "rows": [32, 33, 34],
        "blocks": [
            ("B", "C"),
            ("D", "E"),
            ("F", "G"),
        ],
    },

    # --------------------------------------------------------
    # CAPULIN
    # --------------------------------------------------------

    {
        "soil_code": "SC",
        "d": 3,
        "rows": [22, 23, 24],
        "blocks": [
            ("J", "K"),
            ("L", "M"),
            ("N", "O"),
        ],
    },

    {
        "soil_code": "SC",
        "d": 4,
        "rows": [27, 28, 29],
        "blocks": [
            ("J", "K"),
            ("L", "M"),
            ("N", "O"),
        ],
    },

    {
        "soil_code": "SC",
        "d": 5,
        "rows": [32, 33, 34],
        "blocks": [
            ("J", "K"),
            ("L", "M"),
            ("N", "O"),
        ],
    },

    # --------------------------------------------------------
    # SANTA ANA
    # --------------------------------------------------------

    {
        "soil_code": "SS",
        "d": 3,
        "rows": [22, 23, 24],
        "blocks": [
            ("R", "S"),
            ("T", "U"),
            ("V", "W"),
        ],
    },

    {
        "soil_code": "SS",
        "d": 4,
        "rows": [27, 28, 29],
        "blocks": [
            ("R", "S"),
            ("T", "U"),
            ("V", "W"),
        ],
    },

    {
        "soil_code": "SS",
        "d": 5,
        "rows": [31, 32, 33],
        "blocks": [
            ("R", "S"),
            ("T", "U"),
            ("V", "W"),
        ],
    },
]


# ============================================================
# FUNCIONES
# ============================================================

def numeric_or_nan(value):

    if value is None:
        return np.nan

    if isinstance(
        value,
        (int, float, np.integer, np.floating)
    ):
        return float(value)

    return np.nan


def extract_group(
    ws_values,
    ws_formulas,
    config,
    organism_group,
):

    records = []

    for section in config:

        soil_code = section["soil_code"]
        soil = SOILS[soil_code]["soil"]
        inoculated_volume_ml = (
            SOILS[soil_code]["factor"]
        )

        d = section["d"]
        dilution_factor = 10 ** d

        rows = section["rows"]

        for block_number, (
            count_col,
            ufc_col
        ) in enumerate(
            section["blocks"],
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
                    ws_values[count_cell].value
                )

                cfu_per_ml_reported = numeric_or_nan(
                    ws_values[cfu_cell].value
                )

                original_formula = (
                    ws_formulas[
                        cfu_cell
                    ].value
                )

                # --------------------------------------------
                # UFC corregida/recalculada
                # --------------------------------------------

                if pd.notna(colony_count):

                    cfu_per_ml_recalculated = (
                        colony_count
                        * dilution_factor
                        / inoculated_volume_ml
                    )

                else:

                    cfu_per_ml_recalculated = np.nan

                # --------------------------------------------
                # Clasificar trazabilidad
                # --------------------------------------------

                if pd.isna(colony_count):

                    status = "missing_count"

                elif (
                    colony_count == 0
                    and pd.isna(cfu_per_ml_reported)
                ):

                    status = (
                        "zero_count_missing_ufc"
                    )

                elif (
                    colony_count == 0
                    and cfu_per_ml_reported == 0
                ):

                    status = "zero_consistent"

                elif pd.isna(cfu_per_ml_reported):

                    status = (
                        "missing_reported_ufc"
                    )

                else:

                    abs_diff = abs(
                        cfu_per_ml_reported
                        - cfu_per_ml_recalculated
                    )

                    # ------------------------------------------------
                    # Clasificación del valor original
                    # ------------------------------------------------
                    # Una fórmula con suma del factor de dilución
                    # (+10000/... o +100000/...) es un error de
                    # fórmula aunque el resultado numérico quede
                    # accidentalmente cerca del valor correcto.
                    # ------------------------------------------------

                    formula_error = (
                        isinstance(original_formula, str)
                        and (
                            "+10000/" in original_formula
                            or "+100000/" in original_formula
                        )
                    )

                    if formula_error:

                        status = "formula_error"

                    elif np.isclose(
                        cfu_per_ml_reported,
                        cfu_per_ml_recalculated,
                        rtol=1e-6,
                        atol=1e-6,
                    ):

                        status = "exact_match"

                    elif np.isclose(
                        cfu_per_ml_reported,
                        cfu_per_ml_recalculated,
                        rtol=1e-4,
                        atol=1.0,
                    ):

                        status = "rounding_only"

                    else:

                        status = "formula_or_value_error"

                # --------------------------------------------
                # Diferencias
                # --------------------------------------------

                if (
                    pd.notna(cfu_per_ml_reported)
                    and
                    pd.notna(cfu_per_ml_recalculated)
                ):

                    difference = (
                        cfu_per_ml_reported
                        - cfu_per_ml_recalculated
                    )

                else:

                    difference = np.nan

                records.append(
                    {
                        "organism_group":
                            organism_group,

                        "medium":
                            "PDA",

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
                            original_formula,

                        "cfu_per_ml_recalculated":
                            cfu_per_ml_recalculated,

                        "cfu_per_ml_difference":
                            difference,

                        "cfu_per_ml_status":
                            status,
                    }
                )

    return pd.DataFrame(records)


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_BACTERIA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_VALIDATION.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    sheet = "Bacterias PDA serie 1"

    wb_values = load_workbook(
        INPUT_FILE,
        data_only=True
    )

    wb_formulas = load_workbook(
        INPUT_FILE,
        data_only=False
    )

    ws_values = wb_values[sheet]
    ws_formulas = wb_formulas[sheet]

    # --------------------------------------------------------
    # EXTRAER
    # --------------------------------------------------------

    bacteria = extract_group(
        ws_values,
        ws_formulas,
        BACTERIA_CONFIG,
        "Bacteria",
    )

    fungi = extract_group(
        ws_values,
        ws_formulas,
        FUNGI_CONFIG,
        "Fungi",
    )

    combined = pd.concat(
        [bacteria, fungi],
        ignore_index=True
    )

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    bacteria.to_csv(
        OUTPUT_BACTERIA,
        index=False
    )

    fungi.to_csv(
        OUTPUT_FUNGI,
        index=False
    )

    combined.to_csv(
        OUTPUT_ALL,
        index=False
    )

    # --------------------------------------------------------
    # AUDITORÍA
    # --------------------------------------------------------

    audit = combined.loc[
        combined["cfu_per_ml_status"]
        != "exact_match"
    ].copy()

    audit.to_csv(
        OUTPUT_AUDIT,
        index=False
    )

    # --------------------------------------------------------
    # VALIDACIONES
    # --------------------------------------------------------

    structure = (
        combined
        .groupby(
            [
                "organism_group",
                "soil",
                "dilution",
                "block",
            ]
        )
        .size()
        .rename("n_replicates")
        .reset_index()
    )

    # Número esperado:
    #
    # bacteria:
    # Tepantitla = 4 dil × 3 blocks × 3 reps = 36
    # Capulin    = 3 × 3 × 3 = 27
    # Santa Ana  = 3 × 3 × 3 = 27
    # total bacteria = 90
    #
    # fungi:
    # 3 soils × 3 dil × 3 blocks × 3 reps = 81

    expected_bacteria = 90
    expected_fungi = 81
    expected_total = 171

    # ========================================================
    # REPORTE
    # ========================================================

    with OUTPUT_VALIDATION.open(
        "w",
        encoding="utf-8"
    ) as handle:

        handle.write(
            "=" * 95 + "\n"
        )

        handle.write(
            "VALIDACIÓN — BACTERIAS Y "
            "HONGOS EN PDA\n"
        )

        handle.write(
            "=" * 95 + "\n\n"
        )

        handle.write(
            f"Bacterias procesadas: "
            f"{len(bacteria)} "
            f"(esperadas: "
            f"{expected_bacteria})\n"
        )

        handle.write(
            f"Hongos procesados: "
            f"{len(fungi)} "
            f"(esperados: "
            f"{expected_fungi})\n"
        )

        handle.write(
            f"Total: {len(combined)} "
            f"(esperado: "
            f"{expected_total})\n\n"
        )

        handle.write(
            "CONTEOS AUSENTES\n"
        )

        handle.write(
            "-" * 95 + "\n"
        )

        handle.write(
            combined[
                "colony_count"
            ]
            .isna()
            .groupby(
                combined[
                    "organism_group"
                ]
            )
            .sum()
            .to_string()
        )

        handle.write("\n\n")

        handle.write(
            "ESTADO DE UFC ORIGINALES\n"
        )

        handle.write(
            "-" * 95 + "\n"
        )

        status_table = (
            combined
            .groupby(
                [
                    "organism_group",
                    "cfu_per_ml_status",
                ]
            )
            .size()
            .rename("n")
            .reset_index()
        )

        handle.write(
            status_table.to_string(
                index=False
            )
        )

        handle.write("\n\n")

        handle.write(
            "ESTRUCTURA\n"
        )

        handle.write(
            "-" * 95 + "\n"
        )

        handle.write(
            structure.to_string(
                index=False
            )
        )

        handle.write("\n\n")

        handle.write(
            "REGISTROS QUE REQUIEREN "
            "TRAZABILIDAD\n"
        )

        handle.write(
            "-" * 95 + "\n"
        )

        if audit.empty:

            handle.write(
                "Ninguno.\n"
            )

        else:

            cols = [
                "organism_group",
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
                "cfu_per_ml_status",
            ]

            handle.write(
                audit[cols]
                .to_string(
                    index=False
                )
            )

            handle.write("\n")

        handle.write("\n")

        handle.write(
            "CRITERIOS\n"
        )

        handle.write(
            "-" * 95 + "\n"
        )

        handle.write(
            "1. colony_count es el "
            "dato primario.\n"
        )

        handle.write(
            "2. cfu_per_ml_reported se conserva "
            "para trazabilidad.\n"
        )

        handle.write(
            "3. cfu_per_ml_recalculated es la "
            "UFC armonizada/corregida.\n"
        )

        handle.write(
            "4. Los errores inequívocos de "
            "fórmula no se propagan al "
            "valor recalculado.\n"
        )

        handle.write(
            "5. Los ceros de conteo se "
            "conservan como cero UFC.\n"
        )

        handle.write(
            "6. No se imputan conteos "
            "ausentes.\n"
        )

        handle.write(
            "7. Las distintas diluciones "
            "no se consideran réplicas "
            "biológicas independientes.\n"
        )

        handle.write(
            "8. No se realizaron pruebas "
            "estadísticas.\n"
        )

    # --------------------------------------------------------
    # TERMINAL
    # --------------------------------------------------------

    print("=" * 95)

    print(
        "PDA BACTERIAS/HONGOS PROCESADO"
    )

    print("=" * 95)

    print(
        f"\nBacterias: "
        f"{len(bacteria)} "
        f"(esperadas 90)"
    )

    print(
        f"Hongos: "
        f"{len(fungi)} "
        f"(esperados 81)"
    )

    print(
        f"Total: "
        f"{len(combined)} "
        f"(esperado 171)"
    )

    print(
        "\nEstados UFC:"
    )

    print(
        combined["cfu_per_ml_status"]
        .value_counts()
        .to_string()
    )

    print(
        f"\nValidación:\n"
        f"{OUTPUT_VALIDATION}"
    )

    print(
        f"\nAuditoría:\n"
        f"{OUTPUT_AUDIT}"
    )


if __name__ == "__main__":
    main()
