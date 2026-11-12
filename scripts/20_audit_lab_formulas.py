#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
20_audit_lab_formulas.py

Auditoría algebraica de base_1.xlsx.

Objetivos:
1. Recuperar valores y fórmulas originales.
2. Identificar qué columnas son mediciones y cuáles derivadas.
3. Examinar la cadena de cálculo de degradación de atrazina.
4. No modificar datos.
5. No realizar estadística.
"""

from pathlib import Path
from openpyxl import load_workbook


PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "base_1.xlsx"
)

OUTPUT_FILE = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "20_lab_formula_audit.txt"
)


def main():

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    wb_values = load_workbook(
        INPUT_FILE,
        data_only=True
    )

    wb_formulas = load_workbook(
        INPUT_FILE,
        data_only=False
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as out:

        out.write("=" * 110 + "\n")
        out.write("AUDITORÍA ALGEBRAICA — BASE 1 / LABORATORIO\n")
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

        # ====================================================
        # CADA HOJA
        # ====================================================

        for sheet in wb_formulas.sheetnames:

            ws_f = wb_formulas[sheet]
            ws_v = wb_values[sheet]

            out.write("\n")
            out.write("=" * 110 + "\n")
            out.write(f"HOJA: {sheet}\n")
            out.write("=" * 110 + "\n\n")

            # -----------------------------------------------
            # Encabezados
            # -----------------------------------------------

            out.write("FILA 1 / ENCABEZADOS\n")
            out.write("-" * 110 + "\n")

            for col in range(
                1,
                ws_f.max_column + 1
            ):

                cell = ws_f.cell(
                    row=1,
                    column=col
                )

                out.write(
                    f"{cell.coordinate}: "
                    f"{cell.value!r}\n"
                )

            # -----------------------------------------------
            # Fórmulas
            # -----------------------------------------------

            out.write("\n")
            out.write("FÓRMULAS DETECTADAS\n")
            out.write("-" * 110 + "\n")

            formula_count = 0
            formula_columns = {}

            for row in ws_f.iter_rows():

                for cell in row:

                    value = cell.value

                    if (
                        isinstance(value, str)
                        and value.startswith("=")
                    ):

                        formula_count += 1

                        column = cell.column_letter

                        formula_columns[column] = (
                            formula_columns.get(
                                column,
                                0
                            ) + 1
                        )

                        stored = (
                            ws_v[cell.coordinate]
                            .value
                        )

                        out.write(
                            f"{cell.coordinate}: "
                            f"{value} "
                            f"-> {stored!r}\n"
                        )

            out.write(
                f"\nTotal de fórmulas: "
                f"{formula_count}\n"
            )

            out.write(
                "\nFórmulas por columna:\n"
            )

            for column, count in sorted(
                formula_columns.items()
            ):

                out.write(
                    f"  {column}: {count}\n"
                )

            # -----------------------------------------------
            # Primeras observaciones
            # -----------------------------------------------

            out.write("\n")
            out.write(
                "PRIMERAS 12 FILAS — "
                "VALOR Y CONTENIDO ORIGINAL\n"
            )
            out.write("-" * 110 + "\n")

            max_row = min(
                ws_f.max_row,
                12
            )

            for row_number in range(
                1,
                max_row + 1
            ):

                out.write(
                    f"\nFILA {row_number}\n"
                )

                for col in range(
                    1,
                    ws_f.max_column + 1
                ):

                    original = (
                        ws_f.cell(
                            row=row_number,
                            column=col
                        ).value
                    )

                    stored = (
                        ws_v.cell(
                            row=row_number,
                            column=col
                        ).value
                    )

                    if (
                        original is not None
                        or stored is not None
                    ):

                        coordinate = (
                            ws_f.cell(
                                row=row_number,
                                column=col
                            ).coordinate
                        )

                        out.write(
                            f"  {coordinate}: "
                            f"stored={stored!r}; "
                            f"original={original!r}\n"
                        )

            # -----------------------------------------------
            # Últimas filas
            # -----------------------------------------------

            out.write("\n")
            out.write(
                "ÚLTIMAS 5 FILAS\n"
            )
            out.write("-" * 110 + "\n")

            start = max(
                1,
                ws_f.max_row - 4
            )

            for row_number in range(
                start,
                ws_f.max_row + 1
            ):

                values = []

                for col in range(
                    1,
                    ws_f.max_column + 1
                ):

                    cell = ws_f.cell(
                        row=row_number,
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

    print("=" * 90)
    print("AUDITORÍA ALGEBRAICA BASE 1 COMPLETADA")
    print("=" * 90)

    print(
        f"\nReporte:\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
