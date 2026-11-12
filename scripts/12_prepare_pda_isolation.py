#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
12_prepare_pda_isolation.py

Preparación de pda_aislamiento.xlsx.

Decisiones confirmadas:
- Hoja Preliminar contiene observaciones de aislamiento.
- S.Tepantitla = Tepantitla.
- S. Capulin = Capulín.
- S. Herbicida = Santa Ana.
- "S. Herbicida" es una denominación contextual relacionada
  con el antecedente de herbicida del suelo de Santa Ana.
- Se preservan literalmente las observaciones.
- No se transforman categorías cualitativas en números.
- Las diluciones NO se consideran réplicas.
- No se realizan análisis estadísticos.
- Hoja2 está vacía.
- Hoja3 contiene un valor aislado "8" cuyo significado
  experimental no está documentado; no se incorpora al dataset.

Salidas:
    data/processed/pda_isolation_observations.csv
    results/tables/12_pda_isolation_validation.txt
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
    / "pda_aislamiento.xlsx"
)

OUTPUT_DATA = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "pda_isolation_observations.csv"
)

OUTPUT_VALIDATION = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "12_pda_isolation_validation.txt"
)


# ============================================================
# DEFINICIONES
# ============================================================

SOIL_COLUMNS = {
    1: {
        "soil": "Tepantitla",
        "original_name": "S.Tepantitla",
    },
    3: {
        "soil": "Capulin",
        "original_name": "S. Capulin",
    },
    5: {
        "soil": "Santa Ana",
        "original_name": "S. Herbicida",
    },
}

# Filas observadas en el archivo original.
# Los índices corresponden a lectura con header=None.

TIME_BLOCKS = {
    24: range(2, 8),
    48: range(11, 17),
    72: range(20, 26),
}


# ============================================================
# PROGRAMA
# ============================================================

def main():

    OUTPUT_DATA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_VALIDATION.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name="Preliminar",
        header=None
    )

    records = []

    # --------------------------------------------------------
    # Reconstrucción explícita de los bloques
    # --------------------------------------------------------

    for time_h, rows in TIME_BLOCKS.items():

        for row in rows:

            dilution = raw.iloc[row, 0]

            if pd.isna(dilution):
                raise ValueError(
                    f"Dilución faltante en fila {row}."
                )

            dilution = int(dilution)

            for col, soil_info in SOIL_COLUMNS.items():

                observation = raw.iloc[row, col]

                has_observation = pd.notna(observation)

                if has_observation:
                    observation = str(observation).strip()
                else:
                    observation = pd.NA

                records.append(
                    {
                        "time_h": time_h,
                        "dilution": dilution,
                        "soil": soil_info["soil"],
                        "original_soil_label":
                            soil_info["original_name"],
                        "observation": observation,
                        "has_observation":
                            bool(has_observation),
                    }
                )

    df = pd.DataFrame(records)

    # --------------------------------------------------------
    # Validaciones estructurales
    # --------------------------------------------------------

    expected_rows = (
        3      # tiempos
        * 6    # diluciones
        * 3    # suelos
    )

    if len(df) != expected_rows:
        raise ValueError(
            f"Se esperaban {expected_rows} registros; "
            f"se obtuvieron {len(df)}."
        )

    counts = (
        df.groupby(
            ["time_h", "soil"]
        )
        .size()
    )

    if not (counts == 6).all():
        raise ValueError(
            "No todas las combinaciones tiempo × suelo "
            "contienen las 6 diluciones."
        )

    # --------------------------------------------------------
    # Guardar
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_DATA,
        index=False
    )

    # --------------------------------------------------------
    # Resumen para validación
    # --------------------------------------------------------

    summary = (
        df.groupby(
            ["time_h", "soil"],
            as_index=False
        )
        .agg(
            n_dilutions=("dilution", "size"),
            n_with_observation=(
                "has_observation",
                "sum"
            ),
        )
    )

    # --------------------------------------------------------
    # Reporte
    # --------------------------------------------------------

    with OUTPUT_VALIDATION.open(
        "w",
        encoding="utf-8"
    ) as handle:

        handle.write(
            "=" * 78 + "\n"
        )

        handle.write(
            "VALIDACIÓN — PDA AISLAMIENTO\n"
        )

        handle.write(
            "=" * 78 + "\n\n"
        )

        handle.write(
            f"Registros procesados: {len(df)}\n"
        )

        handle.write(
            "Tiempos: "
            + ", ".join(
                str(x)
                for x in sorted(
                    df["time_h"].unique()
                )
            )
            + " h\n"
        )

        handle.write(
            "Diluciones: "
            + ", ".join(
                str(x)
                for x in sorted(
                    df["dilution"].unique()
                )
            )
            + "\n"
        )

        handle.write(
            "Suelos: "
            + ", ".join(
                df["soil"].unique()
            )
            + "\n\n"
        )

        handle.write(
            "CORRESPONDENCIA DE PROCEDENCIAS\n"
        )

        handle.write(
            "-" * 78 + "\n"
        )

        handle.write(
            "S.Tepantitla -> Tepantitla\n"
        )

        handle.write(
            "S. Capulin -> Capulin\n"
        )

        handle.write(
            "S. Herbicida -> Santa Ana\n\n"
        )

        handle.write(
            "REGISTROS POR TIEMPO Y SUELO\n"
        )

        handle.write(
            "-" * 78 + "\n"
        )

        handle.write(
            summary.to_string(
                index=False
            )
        )

        handle.write("\n\n")

        handle.write(
            "DECISIONES ANALÍTICAS\n"
        )

        handle.write(
            "-" * 78 + "\n"
        )

        handle.write(
            "- Las observaciones textuales se conservaron "
            "sin recodificación numérica.\n"
        )

        handle.write(
            "- Las diluciones no se interpretaron "
            "como réplicas.\n"
        )

        handle.write(
            "- No se realizaron pruebas estadísticas.\n"
        )

        handle.write(
            "- Los registros de 72 h se conservaron, "
            "aunque carecen de observaciones.\n"
        )

        handle.write(
            "- Hoja2 no aporta datos.\n"
        )

        handle.write(
            "- El valor aislado de Hoja3 no se incorporó "
            "por carecer de significado documentado.\n"
        )

        handle.write(
            "- Este dataset se conserva como información "
            "contextual del aislamiento inicial.\n"
        )

    # --------------------------------------------------------
    # TERMINAL
    # --------------------------------------------------------

    print("=" * 78)
    print("PREPARACIÓN PDA AISLAMIENTO COMPLETADA")
    print("=" * 78)

    print(
        f"\nDataset:\n{OUTPUT_DATA}"
    )

    print(
        f"\nValidación:\n{OUTPUT_VALIDATION}"
    )

    print(
        "\nResumen:"
    )

    print(
        summary.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
