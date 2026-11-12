#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
22_describe_soil_profiles.py

Checkpoint 23
Caracterización descriptiva fisicoquímica y microbiológica
de Santa Ana, Capulín y Tepantitla.

Decisiones metodológicas:
- No se combinan diluciones.
- Cada dilución se resume por separado.
- Bloques y repeticiones se conservan.
- Se utiliza cfu_per_ml_recalculated.
- No se imputan datos ausentes.
- No se realizan pruebas inferenciales.
"""

from pathlib import Path
import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "processed"
OUT_DIR = PROJECT_DIR / "results" / "tables"

OUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# ARCHIVOS
# ============================================================

SOIL_FILE = DATA_DIR / "soil_characterization.csv"

PDA_BACTERIA_FILE = (
    DATA_DIR / "pdab1_pda_bacteria.csv"
)

PDA_FUNGI_FILE = (
    DATA_DIR / "pdab1_pda_fungi.csv"
)

MICROBIOLOGY_FILE = (
    DATA_DIR / "pdab1_microbiology.csv"
)


# ============================================================
# FUNCIÓN DESCRIPTIVA
# ============================================================

def summarize(
    df,
    group_cols,
    value_col
):

    result = (
        df
        .groupby(
            group_cols,
            dropna=False
        )[value_col]
        .agg(
            n="count",
            mean="mean",
            sd="std",
            median="median",
            minimum="min",
            maximum="max",
        )
        .reset_index()
    )

    return result


# ============================================================
# BASE 3 — FISICOQUÍMICA
# ============================================================

def summarize_soil():

    df = pd.read_csv(SOIL_FILE)

    summary = summarize(
        df=df,
        group_cols=[
            "soil",
            "variable_code",
            "variable",
            "unit",
        ],
        value_col="value",
    )

    summary.to_csv(
        OUT_DIR
        / "22_soil_physicochemical_summary.csv",
        index=False,
    )

    return df, summary


# ============================================================
# PDA — BACTERIAS Y HONGOS
# ============================================================

def summarize_pda():

    bacteria = pd.read_csv(
        PDA_BACTERIA_FILE
    )

    fungi = pd.read_csv(
        PDA_FUNGI_FILE
    )

    bacteria_summary = summarize(
        df=bacteria,
        group_cols=[
            "soil",
            "dilution_exponent",
            "dilution",
        ],
        value_col="cfu_per_ml_recalculated",
    )

    fungi_summary = summarize(
        df=fungi,
        group_cols=[
            "soil",
            "dilution_exponent",
            "dilution",
        ],
        value_col="cfu_per_ml_recalculated",
    )

    bacteria_summary.to_csv(
        OUT_DIR
        / "22_pda_bacteria_by_dilution.csv",
        index=False,
    )

    fungi_summary.to_csv(
        OUT_DIR
        / "22_pda_fungi_by_dilution.csv",
        index=False,
    )

    return (
        bacteria,
        fungi,
        bacteria_summary,
        fungi_summary,
    )


# ============================================================
# OTROS GRUPOS/MEDIOS MICROBIOLÓGICOS
# ============================================================

def summarize_microbiology():

    df = pd.read_csv(
        MICROBIOLOGY_FILE
    )

    summary = summarize(
        df=df,
        group_cols=[
            "sheet",
            "microbial_group",
            "soil",
            "dilution_exponent",
            "dilution",
        ],
        value_col="cfu_per_ml_recalculated",
    )

    summary.to_csv(
        OUT_DIR
        / "22_microbiology_by_dilution.csv",
        index=False,
    )

    return df, summary


# ============================================================
# VALIDACIÓN
# ============================================================

def main():

    soil, soil_summary = summarize_soil()

    (
        bacteria,
        fungi,
        bacteria_summary,
        fungi_summary,
    ) = summarize_pda()

    microbiology, microbiology_summary = (
        summarize_microbiology()
    )

    validation_file = (
        OUT_DIR
        / "22_soil_profiles_validation.txt"
    )

    with validation_file.open(
        "w",
        encoding="utf-8"
    ) as out:

        out.write("=" * 100 + "\n")
        out.write(
            "CHECKPOINT 23 — "
            "CARACTERIZACIÓN DESCRIPTIVA DE SUELOS\n"
        )
        out.write("=" * 100 + "\n\n")

        # ----------------------------------------------------
        # Base 3
        # ----------------------------------------------------

        out.write(
            "1. CARACTERIZACIÓN FISICOQUÍMICA\n"
        )
        out.write("-" * 100 + "\n")

        out.write(
            f"Observaciones originales: "
            f"{len(soil)}\n"
        )

        out.write(
            f"Filas resumen: "
            f"{len(soil_summary)}\n\n"
        )

        out.write(
            soil_summary.to_string(
                index=False
            )
        )

        # ----------------------------------------------------
        # PDA bacterias
        # ----------------------------------------------------

        out.write("\n\n")
        out.write(
            "2. BACTERIAS EN PDA — "
            "RESUMEN POR DILUCIÓN\n"
        )
        out.write("-" * 100 + "\n")

        out.write(
            f"Observaciones: "
            f"{len(bacteria)}\n\n"
        )

        out.write(
            bacteria_summary.to_string(
                index=False
            )
        )

        # ----------------------------------------------------
        # PDA hongos
        # ----------------------------------------------------

        out.write("\n\n")
        out.write(
            "3. HONGOS EN PDA — "
            "RESUMEN POR DILUCIÓN\n"
        )
        out.write("-" * 100 + "\n")

        out.write(
            f"Observaciones: "
            f"{len(fungi)}\n\n"
        )

        out.write(
            fungi_summary.to_string(
                index=False
            )
        )

        # ----------------------------------------------------
        # Otros medios
        # ----------------------------------------------------

        out.write("\n\n")
        out.write(
            "4. OTROS GRUPOS/MEDIOS — "
            "RESUMEN POR DILUCIÓN\n"
        )
        out.write("-" * 100 + "\n")

        out.write(
            f"Observaciones: "
            f"{len(microbiology)}\n\n"
        )

        out.write(
            microbiology_summary.to_string(
                index=False
            )
        )

        # ----------------------------------------------------
        # Control de estructura
        # ----------------------------------------------------

        out.write("\n\n")
        out.write(
            "5. CONTROL DE ESTRUCTURA\n"
        )
        out.write("-" * 100 + "\n")

        out.write(
            "Bacterias PDA:\n"
        )

        check_b = (
            bacteria
            .groupby(
                [
                    "soil",
                    "dilution",
                    "block",
                ]
            )
            .size()
        )

        out.write(
            check_b.to_string()
        )

        out.write("\n\nHongos PDA:\n")

        check_f = (
            fungi
            .groupby(
                [
                    "soil",
                    "dilution",
                    "block",
                ]
            )
            .size()
        )

        out.write(
            check_f.to_string()
        )

        out.write(
            "\n\n"
            "CRITERIOS DEL CHECKPOINT\n"
        )
        out.write("-" * 100 + "\n")

        out.write(
            "1. Las diluciones se mantienen separadas.\n"
        )

        out.write(
            "2. No se promedian diluciones entre sí.\n"
        )

        out.write(
            "3. Se utilizan CFU/mL recalculadas.\n"
        )

        out.write(
            "4. Los valores ausentes no se imputan.\n"
        )

        out.write(
            "5. No se realizaron pruebas inferenciales.\n"
        )

    print("=" * 90)
    print(
        "CARACTERIZACIÓN DESCRIPTIVA COMPLETADA"
    )
    print("=" * 90)

    print(
        f"\nFisicoquímica: "
        f"{len(soil)} observaciones -> "
        f"{len(soil_summary)} resúmenes"
    )

    print(
        f"Bacterias PDA: "
        f"{len(bacteria)} observaciones -> "
        f"{len(bacteria_summary)} resúmenes"
    )

    print(
        f"Hongos PDA: "
        f"{len(fungi)} observaciones -> "
        f"{len(fungi_summary)} resúmenes"
    )

    print(
        f"Otros grupos/medios: "
        f"{len(microbiology)} observaciones -> "
        f"{len(microbiology_summary)} resúmenes"
    )

    print(
        f"\nValidación:\n"
        f"{validation_file}"
    )


if __name__ == "__main__":
    main()
