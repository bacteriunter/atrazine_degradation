#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
07_inspect_growth_inhibition.py

Auditoría específica de base_2.xlsx.

Objetivos:
1. Inspeccionar íntegramente Hoja1 y Hoja2.
2. Conservar nombres y valores originales.
3. Identificar estructura de las pruebas de crecimiento/inhibición.
4. Detectar columnas vacías.
5. Examinar tipos de datos y valores únicos.
6. Buscar referencias textuales a Rhizobium y Trichoderma.
7. NO limpiar ni transformar todavía los datos.
8. NO realizar análisis estadístico.
"""

from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "base_2.xlsx"
)

OUTPUT_FILE = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "07_growth_inhibition_inspection.txt"
)


def write_section(handle, title):
    handle.write("\n")
    handle.write("=" * 80 + "\n")
    handle.write(title + "\n")
    handle.write("=" * 80 + "\n\n")


def inspect_sheet(handle, sheet_name, df):

    write_section(
        handle,
        f"HOJA: {sheet_name}"
    )

    handle.write(
        f"Dimensiones: {df.shape[0]} filas × "
        f"{df.shape[1]} columnas\n\n"
    )

    handle.write("COLUMNAS\n")
    handle.write("-" * 80 + "\n")

    for i, col in enumerate(df.columns, start=1):
        handle.write(
            f"{i:02d}. {repr(col)}\n"
        )

    handle.write("\nTIPOS DE DATOS\n")
    handle.write("-" * 80 + "\n")
    handle.write(
        df.dtypes.to_string()
    )
    handle.write("\n")

    handle.write("\nVALORES FALTANTES\n")
    handle.write("-" * 80 + "\n")

    missing = pd.DataFrame({
        "missing_n": df.isna().sum(),
        "missing_pct": (
            df.isna().mean() * 100
        ).round(2)
    })

    handle.write(
        missing.to_string()
    )
    handle.write("\n")

    empty_columns = [
        col
        for col in df.columns
        if df[col].isna().all()
    ]

    handle.write("\nCOLUMNAS COMPLETAMENTE VACÍAS\n")
    handle.write("-" * 80 + "\n")

    if empty_columns:
        for col in empty_columns:
            handle.write(
                f"{repr(col)}\n"
            )
    else:
        handle.write("Ninguna\n")

    handle.write("\nNÚMERO DE VALORES ÚNICOS\n")
    handle.write("-" * 80 + "\n")

    handle.write(
        df.nunique(
            dropna=True
        ).to_string()
    )
    handle.write("\n")

    handle.write("\nCONTENIDO COMPLETO DE LA HOJA\n")
    handle.write("-" * 80 + "\n")

    handle.write(
        df.to_string(
            index=True,
            max_rows=None,
           )
    )
    handle.write("\n")

    # --------------------------------------------------------
    # Búsqueda exclusivamente textual
    # --------------------------------------------------------

    handle.write(
        "\nBÚSQUEDA TEXTUAL: Rhizobium / Trichoderma\n"
    )
    handle.write("-" * 80 + "\n")

    found_any = False

    for idx, row in df.iterrows():

        row_text = " | ".join(
            str(value)
            for value in row.values
            if pd.notna(value)
        )

        lower = row_text.lower()

        if (
            "rhizobium" in lower
            or "trichoderma" in lower
        ):
            found_any = True

            handle.write(
                f"Fila {idx}: {row_text}\n"
            )

    if not found_any:
        handle.write(
            "No se encontraron coincidencias textuales.\n"
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
            "=" * 80 + "\n"
        )

        handle.write(
            "AUDITORÍA ESPECÍFICA — BASE 2\n"
        )

        handle.write(
            "PRUEBAS DE CRECIMIENTO / INHIBICIÓN\n"
        )

        handle.write(
            "=" * 80 + "\n\n"
        )

        handle.write(
            f"Archivo: {INPUT_FILE.name}\n"
        )

        handle.write(
            "Hojas encontradas: "
            + ", ".join(xls.sheet_names)
            + "\n"
        )

        for sheet_name in xls.sheet_names:

            df = pd.read_excel(
                INPUT_FILE,
                sheet_name=sheet_name
            )

            inspect_sheet(
                handle,
                sheet_name,
                df
            )

    print("=" * 80)
    print("AUDITORÍA BASE 2 COMPLETADA")
    print("=" * 80)
    print(f"\nArchivo analizado: {INPUT_FILE}")
    print(f"Reporte generado: {OUTPUT_FILE}")
    print(
        "\nNo se modificaron los datos originales."
    )
    print(
        "No se realizó análisis estadístico."
    )


if __name__ == "__main__":
    main()

