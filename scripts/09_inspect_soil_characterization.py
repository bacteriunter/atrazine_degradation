#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
09_inspect_soil_characterization.py

Auditoría específica de Base 3:
caracterización fisicoquímica de suelos.

Objetivos:
1. Leer todas las hojas con header=None.
2. Preservar exactamente la estructura original.
3. Mostrar todas las filas y columnas.
4. Identificar dimensiones y celdas vacías.
5. Examinar la estructura de las etiquetas.
6. NO asignar todavía nombres definitivos de variables.
7. NO limpiar ni transformar datos.
8. NO realizar análisis estadístico.

Entrada:
    data/raw/base_3.xlsx

Salida:
    results/tables/09_soil_characterization_inspection.txt
"""

from pathlib import Path

import pandas as pd


# ============================================================
# RUTAS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "base_3.xlsx"
)

OUTPUT_FILE = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "09_soil_characterization_inspection.txt"
)


# ============================================================
# FUNCIONES
# ============================================================

def write_section(handle, title):

    handle.write("\n")
    handle.write("=" * 80 + "\n")
    handle.write(title + "\n")
    handle.write("=" * 80 + "\n\n")


def inspect_sheet(handle, sheet_name):

    # Lectura deliberadamente SIN encabezado
    df = pd.read_excel(
        INPUT_FILE,
        sheet_name=sheet_name,
        header=None
    )

    write_section(
        handle,
        f"HOJA: {sheet_name}"
    )

    handle.write(
        f"Dimensiones con header=None: "
        f"{df.shape[0]} filas × "
        f"{df.shape[1]} columnas\n\n"
    )

    # --------------------------------------------------------
    # Contenido completo
    # --------------------------------------------------------

    handle.write(
        "CONTENIDO COMPLETO\n"
    )
    handle.write(
        "-" * 80 + "\n"
    )

    handle.write(
        df.to_string(
            index=True,
            header=True,
            max_rows=None
        )
    )

    handle.write("\n\n")

    # --------------------------------------------------------
    # Número de valores no vacíos por columna
    # --------------------------------------------------------

    handle.write(
        "VALORES NO VACÍOS POR COLUMNA\n"
    )
    handle.write(
        "-" * 80 + "\n"
    )

    for col in df.columns:

        n_nonmissing = int(
            df[col].notna().sum()
        )

        handle.write(
            f"Columna {col}: {n_nonmissing}\n"
        )

    # --------------------------------------------------------
    # Filas completamente vacías
    # --------------------------------------------------------

    empty_rows = df.index[
        df.isna().all(axis=1)
    ].tolist()

    handle.write(
        "\nFILAS COMPLETAMENTE VACÍAS\n"
    )
    handle.write(
        "-" * 80 + "\n"
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
        handle.write(
            "Ninguna\n"
        )

    # --------------------------------------------------------
    # Columnas completamente vacías
    # --------------------------------------------------------

    empty_cols = [
        col
        for col in df.columns
        if df[col].isna().all()
    ]

    handle.write(
        "\nCOLUMNAS COMPLETAMENTE VACÍAS\n"
    )
    handle.write(
        "-" * 80 + "\n"
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
        handle.write(
            "Ninguna\n"
        )

    # --------------------------------------------------------
    # Valores de cada columna
    # --------------------------------------------------------

    handle.write(
        "\nVALORES POR COLUMNA\n"
    )
    handle.write(
        "-" * 80 + "\n"
    )

    for col in df.columns:

        handle.write(
            f"\nColumna {col}\n"
        )

        for idx, value in df[col].items():

            if pd.notna(value):

                handle.write(
                    f"  fila {idx}: "
                    f"{repr(value)}\n"
                )


# ============================================================
# PROGRAMA
# ============================================================

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
            "=" * 80 + "\n"
        )

        handle.write(
            "AUDITORÍA ESPECÍFICA — BASE 3\n"
        )

        handle.write(
            "CARACTERIZACIÓN FISICOQUÍMICA DE SUELOS\n"
        )

        handle.write(
            "=" * 80 + "\n\n"
        )

        handle.write(
            f"Archivo: {INPUT_FILE.name}\n"
        )

        handle.write(
            "Lectura: header=None\n"
        )

        handle.write(
            "Hojas encontradas: "
            + ", ".join(xls.sheet_names)
            + "\n"
        )

        for sheet_name in xls.sheet_names:

            inspect_sheet(
                handle,
                sheet_name
            )

        handle.write(
            "\n"
            + "=" * 80
            + "\n"
        )

        handle.write(
            "NOTA\n"
        )

        handle.write(
            "=" * 80
            + "\n"
        )

        handle.write(
            "Esta auditoría no asigna significado "
            "a las etiquetas ni modifica valores.\n"
        )

        handle.write(
            "No se realizó limpieza, transformación "
            "ni análisis estadístico.\n"
        )

    print("=" * 80)

    print(
        "AUDITORÍA BASE 3 COMPLETADA"
    )

    print("=" * 80)

    print(
        f"\nArchivo analizado: {INPUT_FILE}"
    )

    print(
        f"Reporte generado: {OUTPUT_FILE}"
    )

    print(
        "\nLectura realizada con header=None."
    )

    print(
        "No se modificaron los datos."
    )


if __name__ == "__main__":
    main()
