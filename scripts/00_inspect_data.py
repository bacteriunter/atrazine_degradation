#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
00_inspect_data.py

Auditoría inicial de las bases de datos del proyecto de degradación
de atrazina.

Este script:
    - NO modifica los archivos originales.
    - NO limpia datos.
    - NO realiza pruebas estadísticas.
    - NO elimina duplicados.
    - NO transforma variables.

Para cada archivo Excel:
    1. Identifica las hojas.
    2. Obtiene dimensiones.
    3. Lista nombres de columnas.
    4. Identifica tipos de datos.
    5. Cuenta valores faltantes.
    6. Detecta filas completamente duplicadas.
    7. Muestra una vista preliminar de los datos.

Salida:
    results/tables/00_data_inspection.txt
"""

from pathlib import Path
import sys

import pandas as pd


# ============================================================
# RUTAS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_DIR / "data" / "raw"
RESULTS_DIR = PROJECT_DIR / "results" / "tables"

OUTPUT_FILE = RESULTS_DIR / "00_data_inspection.txt"


# ============================================================
# ARCHIVOS ESPERADOS
# ============================================================

FILES = [
    "base_1.xlsx",
    "base_2.xlsx",
    "base_3.xlsx",
    "base_4.xlsx",
    "pda_aislamiento.xlsx",
    "pdab1_bacterias.xlsx",
]


# ============================================================
# FUNCIONES
# ============================================================

def write_both(text, handle):
    """Imprime en terminal y escribe simultáneamente al reporte."""
    print(text)
    handle.write(text + "\n")


def inspect_sheet(file_path, sheet_name, handle):
    """Inspecciona una hoja individual sin modificarla."""

    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        engine="openpyxl"
    )

    write_both("\n" + "-" * 80, handle)
    write_both(f"HOJA: {sheet_name}", handle)
    write_both("-" * 80, handle)

    write_both(
        f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas",
        handle
    )

    # --------------------------------------------------------
    # Columnas
    # --------------------------------------------------------

    write_both("\nCOLUMNAS:", handle)

    if len(df.columns) == 0:
        write_both("  [Sin columnas]", handle)
    else:
        for i, column in enumerate(df.columns, start=1):
            write_both(f"  {i:02d}. {repr(column)}", handle)

    # --------------------------------------------------------
    # Tipos de datos
    # --------------------------------------------------------

    write_both("\nTIPOS DE DATOS:", handle)

    if len(df.columns) == 0:
        write_both("  [No aplicable]", handle)
    else:
        for column in df.columns:
            write_both(
                f"  {repr(column)}: {df[column].dtype}",
                handle
            )

    # --------------------------------------------------------
    # Valores faltantes
    # --------------------------------------------------------

    write_both("\nVALORES FALTANTES:", handle)

    if len(df.columns) == 0:
        write_both("  [No aplicable]", handle)
    else:
        missing = df.isna().sum()

        for column, value in missing.items():
            percentage = (
                (value / len(df) * 100)
                if len(df) > 0
                else 0
            )

            write_both(
                f"  {repr(column)}: "
                f"{value} ({percentage:.2f}%)",
                handle
            )

    # --------------------------------------------------------
    # Duplicados completos
    # --------------------------------------------------------

    if len(df) > 0:
        duplicated = int(df.duplicated().sum())
    else:
        duplicated = 0

    write_both(
        f"\nFilas completamente duplicadas: {duplicated}",
        handle
    )

    # --------------------------------------------------------
    # Columnas completamente vacías
    # --------------------------------------------------------

    empty_columns = [
        column
        for column in df.columns
        if df[column].isna().all()
    ]

    write_both("\nCOLUMNAS COMPLETAMENTE VACÍAS:", handle)

    if empty_columns:
        for column in empty_columns:
            write_both(f"  {repr(column)}", handle)
    else:
        write_both("  Ninguna", handle)

    # --------------------------------------------------------
    # Número de valores únicos
    # --------------------------------------------------------

    write_both("\nNÚMERO DE VALORES ÚNICOS:", handle)

    for column in df.columns:
        n_unique = df[column].nunique(dropna=True)

        write_both(
            f"  {repr(column)}: {n_unique}",
            handle
        )

    # --------------------------------------------------------
    # Vista preliminar
    # --------------------------------------------------------

    write_both("\nPRIMERAS 5 FILAS:", handle)

    if df.empty:
        write_both("  [Hoja vacía]", handle)
    else:
        preview = df.head(5).to_string(index=False)
        write_both(preview, handle)


def inspect_workbook(file_path, handle):
    """Inspecciona todas las hojas de un archivo Excel."""

    write_both("\n" + "=" * 80, handle)
    write_both(f"ARCHIVO: {file_path.name}", handle)
    write_both("=" * 80, handle)

    excel_file = pd.ExcelFile(
        file_path,
        engine="openpyxl"
    )

    sheets = excel_file.sheet_names

    write_both(
        f"Número de hojas: {len(sheets)}",
        handle
    )

    write_both(
        "Hojas: " + ", ".join(map(str, sheets)),
        handle
    )

    for sheet_name in sheets:
        try:
            inspect_sheet(
                file_path=file_path,
                sheet_name=sheet_name,
                handle=handle
            )

        except Exception as exc:
            write_both(
                f"\nERROR al leer la hoja "
                f"{sheet_name!r}: {exc}",
                handle
            )


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    missing_files = [
        filename
        for filename in FILES
        if not (RAW_DIR / filename).exists()
    ]

    if missing_files:
        print("ERROR: faltan archivos esperados:\n")

        for filename in missing_files:
            print(f"  - {filename}")

        sys.exit(1)

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as handle:

        write_both(
            "=" * 80,
            handle
        )

        write_both(
            "AUDITORÍA INICIAL DE DATOS — ATRAZINE DEGRADATION",
            handle
        )

        write_both(
            "=" * 80,
            handle
        )

        write_both(
            f"\nDirectorio del proyecto: {PROJECT_DIR}",
            handle
        )

        write_both(
            f"Directorio raw: {RAW_DIR}",
            handle
        )

        write_both(
            f"Número de archivos esperados: {len(FILES)}",
            handle
        )

        for filename in FILES:

            file_path = RAW_DIR / filename

            try:
                inspect_workbook(
                    file_path=file_path,
                    handle=handle
                )

            except Exception as exc:

                write_both(
                    "\n" + "!" * 80,
                    handle
                )

                write_both(
                    f"ERROR AL PROCESAR {filename}: {exc}",
                    handle
                )

                write_both(
                    "!" * 80,
                    handle
                )

        write_both(
            "\n" + "=" * 80,
            handle
        )

        write_both(
            "FIN DE LA AUDITORÍA",
            handle
        )

        write_both(
            "=" * 80,
            handle
        )

    print(
        f"\nReporte guardado en:\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()

