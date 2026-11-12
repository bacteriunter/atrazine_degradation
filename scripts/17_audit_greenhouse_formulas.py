#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
17_audit_greenhouse_formulas.py

Auditoría de base_4.xlsx (experimento de invernadero).

Objetivos:
1. Identificar hojas y dimensiones.
2. Recuperar encabezados originales.
3. Mostrar valores almacenados.
4. Recuperar fórmulas originales de Excel.
5. Detectar columnas calculadas mediante fórmulas.
6. No modificar ni interpretar los datos.
7. No realizar análisis estadísticos.
"""

from pathlib import Path
from openpyxl import load_workbook


PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "base_4.xlsx"
)

OUTPUT_FILE = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "17_greenhouse_formula_audit.txt"
)


def main():

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Libro con resultados almacenados
    wb_values = load_workbook(
        INPUT_FILE,
        data_only=True
    )

    # Libro conservando fórmulas
    wb_formulas = load_workbook(
        INPUT_FILE,
        data_only=False
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as out:

        out.write("=" * 110 + "\n")
        out.write("AUDITORÍA DE BASE 4 — INVERNADERO\n")
        out.write("=" * 110 + "\n\n")

        out.write("ARCHIVO\n")
        out.write("-" * 110 + "\n")
        out.write(f"{INPUT_FILE}\n\n")

        out.write("HOJAS\n")
        out.write("-" * 110 + "\n")

        for sheet in wb_formulas.sheetnames:

            ws = wb_formulas[sheet]

            out.write(
                f"{sheet}: "
                f"{ws.max_row} filas x "
                f"{ws.max_column} columnas\n"
            )

        out.write("\n")

        # ====================================================
        # INSPECCIÓN COMPLETA
        # ====================================================

        for sheet in wb_formulas.sheetnames:

            ws_f = wb_formulas[sheet]
            ws_v = wb_values[sheet]

            out.write("\n")
            out.write("=" * 110 + "\n")
            out.write(f"HOJA: {sheet}\n")
            out.write("=" * 110 + "\n\n")

            # -----------------------------------------------
            # Filas con contenido
            # -----------------------------------------------

            out.write("CONTENIDO POR FILA\n")
            out.write("-" * 110 + "\n")

            for row in range(
                1,
                ws_f.max_row + 1
            ):

                values = []

                for col in range(
                    1,
                    ws_f.max_column + 1
                ):

                    cell = ws_f.cell(
                        row=row,
                        column=col
                    )

                    if cell.value is not None:

                        values.append(
                            f"{cell.coordinate}="
                            f"{cell.value!r}"
                        )

                if values:

                    out.write(
                        " | ".join(values)
                        + "\n"
                    )

            # -----------------------------------------------
            # Fórmulas
            # -----------------------------------------------

            out.write("\n")
            out.write("FÓRMULAS DETECTADAS\n")
            out.write("-" * 110 + "\n")

            n_formulas = 0

            for row in ws_f.iter_rows():

                for cell in row:

                    value = cell.value

                    if (
                        isinstance(value, str)
                        and value.startswith("=")
                    ):

                        n_formulas += 1

                        stored_value = (
                            ws_v[cell.coordinate]
                            .value
                        )

                        out.write(
                            f"{cell.coordinate}: "
                            f"{value} "
                            f"-> valor almacenado: "
                            f"{stored_value!r}\n"
                        )

            out.write(
                f"\nTotal de fórmulas: "
                f"{n_formulas}\n"
            )

            # -----------------------------------------------
            # Encabezados
            # -----------------------------------------------

            out.write("\n")
            out.write(
                "PRIMERAS 10 FILAS "
                "VALOR + FÓRMULA\n"
            )
            out.write("-" * 110 + "\n")

            upper_row = min(
                ws_f.max_row,
                10
            )

            for row_number in range(
                1,
                upper_row + 1
            ):

                out.write(
                    f"\nFILA {row_number}\n"
                )

                for col in range(
                    1,
                    ws_f.max_column + 1
                ):

                    formula_cell = (
                        ws_f.cell(
                            row=row_number,
                            column=col
                        )
                    )

                    value_cell = (
                        ws_v.cell(
                            row=row_number,
                            column=col
                        )
                    )

                    if (
                        formula_cell.value
                        is not None
                        or value_cell.value
                        is not None
                    ):

                        out.write(
                            f"  "
                            f"{formula_cell.coordinate}: "
                            f"stored="
                            f"{value_cell.value!r}; "
                            f"original="
                            f"{formula_cell.value!r}\n"
                        )

    print("=" * 90)
    print("AUDITORÍA BASE 4 COMPLETADA")
    print("=" * 90)

    print(
        f"\nReporte:\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
