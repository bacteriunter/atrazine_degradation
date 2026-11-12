#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
14_audit_ufc_conversion.py

Auditoría de la conversión:
    conteo de colonias -> UFC reportadas

Archivo:
    data/raw/pdab1_bacterias.xlsx

Objetivo:
- Identificar pares numéricos conteo/UFC.
- Calcular UFC / conteo.
- Examinar los factores de conversión observados.
- NO recalcular ni corregir las UFC originales.
- NO realizar pruebas estadísticas.
- NO generar todavía el dataset definitivo.

La estructura experimental confirmada es:

    ST = Tepantitla
    SC = Capulin
    SS = Santa Ana

    sufijo -n = dilución 10^-n

    B1, B2, B3 = bloques

    Cada bloque contiene 3 repeticiones.

Salidas:
    results/tables/14_ufc_conversion_pairs.csv
    results/tables/14_ufc_conversion_factors.csv
    results/tables/14_ufc_conversion_audit.txt
"""

from pathlib import Path
import re

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
    / "pdab1_bacterias.xlsx"
)

OUTPUT_PAIRS = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "14_ufc_conversion_pairs.csv"
)

OUTPUT_FACTORS = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "14_ufc_conversion_factors.csv"
)

OUTPUT_REPORT = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "14_ufc_conversion_audit.txt"
)


# ============================================================
# HOJAS A INSPECCIONAR
# ============================================================

SHEETS = [
    "Bacterias PDA serie 1",
    "Actinomicetos",
    "PDA acidificado",
    "Extracto de suelo",
]


# ============================================================
# CORRESPONDENCIA DE SUELOS
# ============================================================

SOIL_MAP = {
    "ST": "Tepantitla",
    "SC": "Capulin",
    "SS": "Santa Ana",
}


# ============================================================
# FUNCIONES
# ============================================================

def is_number(value):

    return (
        pd.notna(value)
        and isinstance(
            value,
            (int, float, np.integer, np.floating)
        )
        and not isinstance(value, bool)
    )


def parse_sample_label(value):

    """
    Reconoce etiquetas como:
        ST-2
        ST-3
        SC-4
        SS-3

    Devuelve:
        codigo_suelo, exponente_dilucion

    Ejemplo:
        ST-3 -> ("ST", 3)
    """

    if not isinstance(value, str):
        return None

    value = value.strip()

    match = re.fullmatch(
        r"(ST|SC|SS)-(\d+)",
        value,
        flags=re.IGNORECASE
    )

    if match is None:
        return None

    soil_code = match.group(1).upper()
    dilution_exponent = int(match.group(2))

    return (
        soil_code,
        dilution_exponent
    )


def extract_pairs(sheet_name):

    """
    Busca bloques definidos por etiquetas ST-n, SC-n o SS-n.

    A partir de cada etiqueta se inspeccionan las columnas
    hacia la derecha hasta encontrar la siguiente etiqueta
    de suelo/dilución.

    Dentro del bloque se buscan encabezados B1/B2/B3.

    Para cada bloque:
        columna del bloque = conteo
        columna inmediatamente siguiente = UFC reportadas

    Se conservan solamente filas donde ambos valores
    sean numéricos.
    """

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name=sheet_name,
        header=None
    )

    records = []

    # --------------------------------------------------------
    # Buscar todas las etiquetas suelo-dilución
    # --------------------------------------------------------

    labels = []

    for row in df.index:

        for col in df.columns:

            parsed = parse_sample_label(
                df.iloc[row, col]
            )

            if parsed is not None:

                soil_code, dilution_exp = parsed

                labels.append(
                    {
                        "row": row,
                        "col": col,
                        "soil_code": soil_code,
                        "dilution_exponent":
                            dilution_exp,
                    }
                )

    # --------------------------------------------------------
    # Procesar cada etiqueta
    # --------------------------------------------------------

    for label in labels:

        header_row = label["row"]
        start_col = label["col"]

        soil_code = label["soil_code"]
        dilution_exp = (
            label["dilution_exponent"]
        )

        # Buscar siguiente etiqueta ST/SC/SS
        # en la misma fila para delimitar bloque

        next_label_cols = []

        for col in range(
            start_col + 1,
            df.shape[1]
        ):

            parsed = parse_sample_label(
                df.iloc[header_row, col]
            )

            if parsed is not None:
                next_label_cols.append(col)

        if next_label_cols:
            end_col = min(next_label_cols)
        else:
            end_col = df.shape[1]

        # ----------------------------------------------------
        # Buscar B1/B2/B3 dentro del bloque
        # ----------------------------------------------------

        block_columns = []

        for col in range(
            start_col + 1,
            end_col
        ):

            value = df.iloc[
                header_row,
                col
            ]

            if (
                isinstance(value, str)
                and value.strip().upper()
                in {"B1", "B2", "B3"}
            ):

                block_columns.append(
                    (
                        value.strip().upper(),
                        col
                    )
                )

        # ----------------------------------------------------
        # Extraer pares conteo / UFC
        # ----------------------------------------------------

        for block, count_col in block_columns:

            ufc_col = count_col + 1

            if ufc_col >= df.shape[1]:
                continue

            repetition = 0

            # Solo buscamos debajo del encabezado,
            # hasta encontrar una fila que claramente
            # deja de contener pares numéricos.
            #
            # Para esta auditoría NO asumimos todavía
            # que todas las filas numéricas sean
            # observaciones primarias.

            for row in range(
                header_row + 1,
                df.shape[0]
            ):

                count_value = df.iloc[
                    row,
                    count_col
                ]

                ufc_value = df.iloc[
                    row,
                    ufc_col
                ]

                if (
                    is_number(count_value)
                    and is_number(ufc_value)
                ):

                    repetition += 1

                    if count_value != 0:

                        factor = (
                            float(ufc_value)
                            / float(count_value)
                        )

                    else:

                        factor = np.nan

                    records.append(
                        {
                            "sheet": sheet_name,
                            "source_row": row,
                            "soil_code": soil_code,
                            "soil": SOIL_MAP[
                                soil_code
                            ],
                            "dilution_exponent":
                                dilution_exp,
                            "dilution_label":
                                f"10^-{dilution_exp}",
                            "block": block,
                            "numeric_sequence":
                                repetition,
                            "colony_count":
                                float(count_value),
                            "ufc_reported":
                                float(ufc_value),
                            "ufc_per_colony":
                                factor,
                        }
                    )

    return records


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    OUTPUT_PAIRS.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    all_records = []

    for sheet in SHEETS:

        records = extract_pairs(sheet)

        all_records.extend(records)

    pairs = pd.DataFrame(all_records)

    if pairs.empty:

        raise ValueError(
            "No se detectaron pares "
            "conteo/UFC."
        )

    # --------------------------------------------------------
    # Guardar todos los pares detectados
    # --------------------------------------------------------

    pairs.to_csv(
        OUTPUT_PAIRS,
        index=False
    )

    # --------------------------------------------------------
    # Resumir factores observados
    # --------------------------------------------------------

    factors = (
        pairs
        .groupby(
            [
                "sheet",
                "soil",
                "dilution_exponent",
                "dilution_label",
            ],
            as_index=False
        )
        .agg(
            n_pairs=(
                "ufc_per_colony",
                "count"
            ),
            factor_min=(
                "ufc_per_colony",
                "min"
            ),
            factor_max=(
                "ufc_per_colony",
                "max"
            ),
            factor_mean=(
                "ufc_per_colony",
                "mean"
            ),
            factor_sd=(
                "ufc_per_colony",
                "std"
            ),
        )
    )

    factors["factor_range"] = (
        factors["factor_max"]
        - factors["factor_min"]
    )

    factors.to_csv(
        OUTPUT_FACTORS,
        index=False
    )

    # --------------------------------------------------------
    # Reporte
    # --------------------------------------------------------

    with OUTPUT_REPORT.open(
        "w",
        encoding="utf-8"
    ) as handle:

        handle.write(
            "=" * 90 + "\n"
        )

        handle.write(
            "AUDITORÍA DE CONVERSIÓN "
            "CONTEO -> UFC\n"
        )

        handle.write(
            "=" * 90 + "\n\n"
        )

        handle.write(
            f"Pares numéricos detectados: "
            f"{len(pairs)}\n"
        )

        handle.write(
            f"Hojas inspeccionadas: "
            f"{len(SHEETS)}\n\n"
        )

        # ----------------------------------------------------
        # Conteos por hoja
        # ----------------------------------------------------

        handle.write(
            "PARES DETECTADOS POR HOJA\n"
        )

        handle.write(
            "-" * 90 + "\n"
        )

        sheet_counts = (
            pairs
            .groupby("sheet")
            .size()
        )

        handle.write(
            sheet_counts.to_string()
        )

        handle.write("\n\n")

        # ----------------------------------------------------
        # Factores
        # ----------------------------------------------------

        handle.write(
            "FACTORES UFC / CONTEO "
            "POR HOJA, SUELO Y DILUCIÓN\n"
        )

        handle.write(
            "-" * 90 + "\n"
        )

        handle.write(
            factors.to_string(
                index=False
            )
        )

        handle.write("\n\n")

        # ----------------------------------------------------
        # Factores únicos aproximados
        # ----------------------------------------------------

        handle.write(
            "FACTORES APROXIMADOS "
            "OBSERVADOS\n"
        )

        handle.write(
            "-" * 90 + "\n"
        )

        rounded = (
            pairs["ufc_per_colony"]
            .dropna()
            .round(6)
            .value_counts()
            .sort_index()
        )

        handle.write(
            rounded.to_string()
        )

        handle.write("\n\n")

        # ----------------------------------------------------
        # Por dilución
        # ----------------------------------------------------

        handle.write(
            "FACTOR GLOBAL POR "
            "EXPONENTE DE DILUCIÓN\n"
        )

        handle.write(
            "-" * 90 + "\n"
        )

        dilution_summary = (
            pairs
            .groupby(
                "dilution_exponent"
            )["ufc_per_colony"]
            .agg(
                [
                    "count",
                    "min",
                    "max",
                    "mean",
                    "std",
                ]
            )
        )

        handle.write(
            dilution_summary.to_string()
        )

        handle.write("\n\n")

        # ----------------------------------------------------
        # Nota
        # ----------------------------------------------------

        handle.write(
            "INTERPRETACIÓN DE ESTA ETAPA\n"
        )

        handle.write(
            "-" * 90 + "\n"
        )

        handle.write(
            "Este reporte es exclusivamente "
            "diagnóstico.\n"
        )

        handle.write(
            "ufc_per_colony = "
            "ufc_reported / colony_count.\n"
        )

        handle.write(
            "No se recalcularon ni corrigieron "
            "las UFC del archivo original.\n"
        )

        handle.write(
            "numeric_sequence NO se interpreta "
            "todavía como repetición experimental.\n"
        )

        handle.write(
            "Su única función es permitir rastrear "
            "la secuencia de pares numéricos "
            "detectados debajo de cada bloque.\n"
        )

        handle.write(
            "La fórmula original de conversión "
            "se determinará únicamente si los "
            "factores observados permiten "
            "reconstruirla sin ambigüedad.\n"
        )

    # --------------------------------------------------------
    # TERMINAL
    # --------------------------------------------------------

    print("=" * 90)

    print(
        "AUDITORÍA CONTEO -> UFC COMPLETADA"
    )

    print("=" * 90)

    print(
        f"\nPares detectados: "
        f"{len(pairs)}"
    )

    print(
        f"\nPares:\n{OUTPUT_PAIRS}"
    )

    print(
        f"\nFactores:\n{OUTPUT_FACTORS}"
    )

    print(
        f"\nReporte:\n{OUTPUT_REPORT}"
    )

    print(
        "\nNo se modificaron ni "
        "recalcularon las UFC."
    )


if __name__ == "__main__":
    main()
