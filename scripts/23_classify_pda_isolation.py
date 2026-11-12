#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
23_classify_pda_isolation.py

Checkpoint 24
Clasificación conservadora de las observaciones cualitativas
del ensayo de aislamiento en PDA.

No se cuantifica intensidad de crecimiento.
No se corrige ni modifica el texto original.

Estados:
- present
- absent
- not_determined
"""

from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "pda_isolation_observations.csv"
)

OUTPUT = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "pda_isolation_classified.csv"
)

VALIDATION = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "23_pda_isolation_classification_validation.txt"
)


# ============================================================
# CLASIFICACIÓN EXPLÍCITA
# ============================================================
#
# Formato:
# (soil, time_h, dilution):
# (bacterial_growth, fungal_growth, overall_growth)
#
# No se asigna ausencia de un grupo cuando el texto simplemente
# no lo menciona.
# ============================================================

classification = {

    # --------------------------------------------------------
    # CAPULÍN — 24 h
    # --------------------------------------------------------

    ("Capulin", 24, 1):
        ("not_determined", "not_determined", "absent"),

    ("Capulin", 24, 2):
        ("not_determined", "not_determined", "absent"),

    ("Capulin", 24, 3):
        ("present", "not_determined", "present"),

    ("Capulin", 24, 4):
        ("not_determined", "not_determined", "absent"),

    ("Capulin", 24, 5):
        ("not_determined", "not_determined", "absent"),

    ("Capulin", 24, 6):
        ("not_determined", "not_determined", "absent"),

    # --------------------------------------------------------
    # CAPULÍN — 48 h
    # --------------------------------------------------------

    ("Capulin", 48, 1):
        ("not_determined", "not_determined", "absent"),

    ("Capulin", 48, 2):
        ("present", "not_determined", "present"),

    ("Capulin", 48, 3):
        ("present", "not_determined", "present"),

    ("Capulin", 48, 4):
        ("not_determined", "not_determined", "present"),

    ("Capulin", 48, 5):
        ("present", "not_determined", "present"),

    ("Capulin", 48, 6):
        ("not_determined", "not_determined", "absent"),

    # --------------------------------------------------------
    # SANTA ANA — 24 h
    # --------------------------------------------------------

    ("Santa Ana", 24, 1):
        ("present", "not_determined", "present"),

    ("Santa Ana", 24, 2):
        ("not_determined", "not_determined", "absent"),

    ("Santa Ana", 24, 3):
        ("present", "present", "present"),

    ("Santa Ana", 24, 4):
        ("present", "not_determined", "present"),

    ("Santa Ana", 24, 5):
        ("not_determined", "not_determined", "absent"),

    ("Santa Ana", 24, 6):
        ("not_determined", "not_determined", "absent"),

    # --------------------------------------------------------
    # SANTA ANA — 48 h
    # --------------------------------------------------------

    ("Santa Ana", 48, 1):
        ("not_determined", "present", "present"),

    ("Santa Ana", 48, 2):
        ("present", "not_determined", "present"),

    ("Santa Ana", 48, 3):
        ("present", "present", "present"),

    ("Santa Ana", 48, 4):
        ("present", "present", "present"),

    ("Santa Ana", 48, 5):
        ("not_determined", "not_determined", "absent"),

    ("Santa Ana", 48, 6):
        ("not_determined", "not_determined", "absent"),

    # --------------------------------------------------------
    # TEPANTITLA — 24 h
    # --------------------------------------------------------

    ("Tepantitla", 24, 1):
        ("present", "not_determined", "present"),

    ("Tepantitla", 24, 2):
        ("present", "not_determined", "present"),

    ("Tepantitla", 24, 3):
        ("present", "not_determined", "present"),

    ("Tepantitla", 24, 4):
        ("present", "not_determined", "present"),

    ("Tepantitla", 24, 5):
        ("present", "not_determined", "present"),

    ("Tepantitla", 24, 6):
        ("present", "not_determined", "present"),

    # --------------------------------------------------------
    # TEPANTITLA — 48 h
    # --------------------------------------------------------

    ("Tepantitla", 48, 1):
        ("present", "present", "present"),

    ("Tepantitla", 48, 2):
        ("present", "present", "present"),

    ("Tepantitla", 48, 3):
        ("not_determined", "present", "present"),

    ("Tepantitla", 48, 4):
        ("present", "absent", "present"),

    ("Tepantitla", 48, 5):
        ("present", "absent", "present"),

    ("Tepantitla", 48, 6):
        ("present", "not_determined", "present"),
}


def main():

    df = pd.read_csv(INPUT)

    bacterial = []
    fungal = []
    overall = []

    classified_count = 0

    for _, row in df.iterrows():

        # Sin observación registrada
        if not bool(row["has_observation"]):

            bacterial.append("not_determined")
            fungal.append("not_determined")
            overall.append("not_determined")

            continue

        key = (
            row["soil"],
            int(row["time_h"]),
            int(row["dilution"]),
        )

        if key not in classification:

            raise ValueError(
                "Observación con registro sin "
                f"clasificación explícita: {key}"
            )

        b, f, o = classification[key]

        bacterial.append(b)
        fungal.append(f)
        overall.append(o)

        classified_count += 1

    df["bacterial_growth"] = bacterial
    df["fungal_growth"] = fungal
    df["overall_growth"] = overall

    df.to_csv(
        OUTPUT,
        index=False
    )

    # --------------------------------------------------------
    # Validaciones
    # --------------------------------------------------------

    observed = df[
        df["has_observation"] == True
    ]

    unobserved = df[
        df["has_observation"] == False
    ]

    with VALIDATION.open(
        "w",
        encoding="utf-8"
    ) as out:

        out.write("=" * 100 + "\n")
        out.write(
            "CHECKPOINT 24 — "
            "CLASIFICACIÓN PDA AISLAMIENTO\n"
        )
        out.write("=" * 100 + "\n\n")

        out.write(
            f"Registros totales: {len(df)}\n"
        )

        out.write(
            f"Con observación: {len(observed)}\n"
        )

        out.write(
            f"Sin observación: {len(unobserved)}\n"
        )

        out.write(
            f"Clasificados explícitamente: "
            f"{classified_count}\n\n"
        )

        for variable in [
            "overall_growth",
            "bacterial_growth",
            "fungal_growth",
        ]:

            out.write(
                f"{variable}\n"
            )

            out.write("-" * 100 + "\n")

            table = (
                df
                .groupby(
                    [
                        "soil",
                        "time_h",
                        variable,
                    ],
                    dropna=False
                )
                .size()
                .rename("n")
                .reset_index()
            )

            out.write(
                table.to_string(
                    index=False
                )
            )

            out.write("\n\n")

        out.write(
            "CRITERIOS\n"
        )
        out.write("-" * 100 + "\n")

        out.write(
            "1. Se conserva íntegra la observación original.\n"
        )

        out.write(
            "2. No se asignaron puntuaciones de intensidad.\n"
        )

        out.write(
            "3. not_determined no equivale a ausencia.\n"
        )

        out.write(
            "4. Los registros sin observación no se "
            "clasificaron como ausencia.\n"
        )

        out.write(
            "5. La ausencia específica de bacterias u hongos "
            "solo se asignó cuando el texto lo indicó.\n"
        )

        out.write(
            "6. No se realizaron pruebas estadísticas.\n"
        )

    print("=" * 90)
    print("CLASIFICACIÓN PDA COMPLETADA")
    print("=" * 90)

    print(
        f"\nRegistros totales: {len(df)}"
    )

    print(
        f"Con observación: {len(observed)}"
    )

    print(
        f"Sin observación: {len(unobserved)}"
    )

    print(
        f"Clasificados explícitamente: "
        f"{classified_count}"
    )

    print(
        f"\nDataset:\n{OUTPUT}"
    )

    print(
        f"\nValidación:\n{VALIDATION}"
    )


if __name__ == "__main__":
    main()
