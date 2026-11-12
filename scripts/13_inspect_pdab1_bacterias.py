#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
13_inspect_pdab1_bacterias.py

Auditoría estructural de:
    data/raw/pdab1_bacterias.xlsx

Objetivo:
- Leer todas las hojas con header=None.
- Preservar la estructura original.
- Mostrar coordenadas de las celdas.
- Identificar filas/columnas vacías.
- NO reconstruir todavía bloques, diluciones o repeticiones.
- NO realizar cálculos ni estadística.

Salida:
    results/tables/13_pdab1_bacterias_inspection.txt
"""

from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "pdab1_bacterias.xlsx"
)

OUTPUT_FILE = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "13_pdab1_bacterias_inspection.txt"
)


def section(handle, title):

    handle.write("\n")
    handle.write("=" * 100 + "\n")
    handle.write(title + "\n")
    handle.write("=" * 100 + "\n\n")


def inspect_sheet(handle, sheet_name):

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name=sheet_name,
        header=None
    )

    section(
        handle,
        f"HOJA: {sheet_name}"
    )

    handle.write(
        f"Dimensiones: "
        f"{df.shape[0]} filas × "
        f"{df.shape[1]} columnas\n\n"
    )

    if df.empty:

        handle.write("Hoja vacía.\n")
        return

    # ========================================================
    # CONTENIDO COMPLETO
    # ========================================================

    handle.write(
        "CONTENIDO COMPLETO\n"
    )

    handle.write(
        "-" * 100 + "\n"
    )

    handle.write(
        df.to_string(
            index=True,
            header=True,
            max_rows=None,
            max_cols=None
        )
    )

    handle.write("\n\n")

    # ========================================================
    # VALORES NO VACÍOS
    # ========================================================

    handle.write(
        "VALORES NO VACÍOS POR COLUMNA\n"
    )

    handle.write(
        "-" * 100 + "\n"
    )

    for col in df.columns:

        handle.write(
            f"Columna {col}: "
            f"{int(df[col].notna().sum())}\n"
        )

    # ========================================================
    # FILAS VACÍAS
    # ========================================================

    empty_rows = (
        df.index[
            df.isna().all(axis=1)
        ]
        .tolist()
    )

    handle.write(
        "\nFILAS COMPLETAMENTE VACÍAS\n"
    )

    handle.write(
        "-" * 100 + "\n"
    )

    if empty_rows:

        handle.write(
            ", ".join(
                str(x)
                for x in empty_rows
            )
            + "\n"
        )

    else:

        handle.write("Ninguna\n")

    # ========================================================
    # COLUMNAS VACÍAS
    # ========================================================

    empty_cols = [
        col
        for col in df.columns
        if df[col].isna().all()
    ]

    handle.write(
        "\nCOLUMNAS COMPLETAMENTE VACÍAS\n"
    )

    handle.write(
        "-" * 100 + "\n"
    )

    if empty_cols:

        handle.write(
            ", ".join(
                str(x)
                for x in empty_cols
            )
            + "\n"
        )

    else:

        handle.write("Ninguna\n")

    # ========================================================
    # TIPOS
    # ========================================================

    handle.write(
        "\nTIPOS DE CONTENIDO POR COLUMNA\n"
    )

    handle.write(
        "-" * 100 + "\n"
    )

    for col in df.columns:

        values = df[col].dropna()

        numeric = 0
        text = 0
        other = 0

        for value in values:

            if isinstance(
                value,
                (int, float)
            ):
                numeric += 1

            elif isinstance(
                value,
                str
            ):
                text += 1

            else:
                other += 1

        handle.write(
            f"Columna {col}: "
            f"numéricos={numeric}, "
            f"texto={text}, "
            f"otros={other}\n"
        )

    # ========================================================
    # CELDAS CON COORDENADAS
    # ========================================================

    handle.write(
        "\nCELDAS NO VACÍAS CON COORDENADAS\n"
    )

    handle.write(
        "-" * 100 + "\n"
    )

    for row in df.index:

        for col in df.columns:

            value = df.loc[row, col]

            if pd.notna(value):

                handle.write(
                    f"fila={row:02d}, "
                    f"columna={col:02d}: "
                    f"{repr(value)}\n"
                )


def main():

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    xls = pd.ExcelFile(
        INPUT_FILE
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as handle:

        handle.write(
            "=" * 100 + "\n"
        )

        handle.write(
            "AUDITORÍA ESTRUCTURAL — "
            "PDAB1 BACTERIAS\n"
        )

        handle.write(
            "=" * 100 + "\n\n"
        )

        handle.write(
            f"Archivo: {INPUT_FILE.name}\n"
        )

        handle.write(
            "Lectura: header=None\n"
        )

        handle.write(
            f"Número de hojas: "
            f"{len(xls.sheet_names)}\n"
        )

        handle.write(
            "Hojas:\n"
        )

        for sheet in xls.sheet_names:

            handle.write(
                f"  - {sheet}\n"
            )

        for sheet in xls.sheet_names:

            inspect_sheet(
                handle,
                sheet
            )

        section(
            handle,
            "NOTA METODOLÓGICA"
        )

        handle.write(
            "Esta auditoría preserva la estructura "
            "original del libro.\n"
        )

        handle.write(
            "No se asignó todavía significado a bloques, "
            "repeticiones o diluciones.\n"
        )

        handle.write(
            "No se eliminaron ni transformaron datos.\n"
        )

        handle.write(
            "No se realizaron cálculos ni "
            "pruebas estadísticas.\n"
        )

    print("=" * 100)

    print(
        "AUDITORÍA PDAB1 BACTERIAS COMPLETADA"
    )

    print("=" * 100)

    print(
        f"\nArchivo:\n{INPUT_FILE}"
    )

    print(
        f"\nReporte:\n{OUTPUT_FILE}"
    )

    print(
        "\nNo se modificaron los datos."
    )


if __name__ == "__main__":
    main()
