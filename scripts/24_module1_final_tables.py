#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
24_module1_final_tables.py

Checkpoint 25
Tablas finales del Módulo 1:
caracterización fisicoquímica y microbiológica de los suelos.

IMPORTANTE
----------
- No se realizan pruebas inferenciales.
- Las mediciones fisicoquímicas son submuestras de muestras compuestas.
- B1-B3 no son réplicas biológicas independientes.
- Las cajas Petri son réplicas técnicas.
- Las diluciones se mantienen separadas.
- No se combinan diluciones.
- Se utilizan CFU/mL recalculados.
"""

from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# RUTAS
# ============================================================

PROJECT = Path(__file__).resolve().parents[1]

PROCESSED = PROJECT / "data" / "processed"
TABLES = PROJECT / "results" / "tables"

TABLES.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. CARACTERIZACIÓN FISICOQUÍMICA
# ============================================================

soil = pd.read_csv(
    PROCESSED / "soil_characterization.csv"
)

soil_summary = (
    soil
    .groupby(
        [
            "soil",
            "variable_code",
            "variable_description",
            "unit"
        ],
        dropna=False
    )
    .agg(
        n_subsamples=("value", "count"),
        mean=("value", "mean"),
        sd=("value", "std"),
        minimum=("value", "min"),
        maximum=("value", "max")
    )
    .reset_index()
)

soil_summary.to_csv(
    TABLES / "24_table1_soil_physicochemical.csv",
    index=False
)


# Versión ancha para manuscrito

soil_manuscript = (
    soil_summary
    .assign(
        mean_sd=lambda x:
        x["mean"].map(lambda z: f"{z:.4f}")
        + " ± "
        + x["sd"].map(lambda z: f"{z:.4f}")
    )
    .pivot(
        index=[
            "variable_code",
            "variable_description",
            "unit"
        ],
        columns="soil",
        values="mean_sd"
    )
    .reset_index()
)

soil_manuscript.to_csv(
    TABLES / "24_table1_soil_physicochemical_manuscript.csv",
    index=False
)


# ============================================================
# 2. PDA — BACTERIAS
# ============================================================

bacteria = pd.read_csv(
    PROCESSED / "pdab1_pda_bacteria.csv"
)

bacteria_summary = (
    bacteria
    .groupby(
        ["soil", "dilution"],
        dropna=False
    )
    .agg(
        n_counts=("colony_count", "count"),
        mean_cfu_ml=("cfu_per_ml_recalculated", "mean"),
        sd_cfu_ml=("cfu_per_ml_recalculated", "std"),
        median_cfu_ml=("cfu_per_ml_recalculated", "median"),
        min_cfu_ml=("cfu_per_ml_recalculated", "min"),
        max_cfu_ml=("cfu_per_ml_recalculated", "max")
    )
    .reset_index()
)

bacteria_summary["microbial_group"] = "PDA_bacteria"


# ============================================================
# 3. PDA — HONGOS
# ============================================================

fungi = pd.read_csv(
    PROCESSED / "pdab1_pda_fungi.csv"
)

fungi_summary = (
    fungi
    .groupby(
        ["soil", "dilution"],
        dropna=False
    )
    .agg(
        n_counts=("colony_count", "count"),
        mean_cfu_ml=("cfu_per_ml_recalculated", "mean"),
        sd_cfu_ml=("cfu_per_ml_recalculated", "std"),
        median_cfu_ml=("cfu_per_ml_recalculated", "median"),
        min_cfu_ml=("cfu_per_ml_recalculated", "min"),
        max_cfu_ml=("cfu_per_ml_recalculated", "max")
    )
    .reset_index()
)

fungi_summary["microbial_group"] = "PDA_fungi"


# ============================================================
# 4. OTROS GRUPOS / MEDIOS
# ============================================================

micro = pd.read_csv(
    PROCESSED / "pdab1_microbiology.csv"
)

# Cada hoja se conserva como categoría independiente.
other_summary = (
    micro
    .groupby(
        ["sheet", "soil", "dilution"],
        dropna=False
    )
    .agg(
        n_counts=("colony_count", "count"),
        mean_cfu_ml=("cfu_per_ml_recalculated", "mean"),
        sd_cfu_ml=("cfu_per_ml_recalculated", "std"),
        median_cfu_ml=("cfu_per_ml_recalculated", "median"),
        min_cfu_ml=("cfu_per_ml_recalculated", "min"),
        max_cfu_ml=("cfu_per_ml_recalculated", "max")
    )
    .reset_index()
    .rename(
        columns={"sheet": "microbial_group"}
    )
)


# ============================================================
# 5. TABLA MICROBIOLÓGICA INTEGRADA
# ============================================================

columns = [
    "microbial_group",
    "soil",
    "dilution",
    "n_counts",
    "mean_cfu_ml",
    "sd_cfu_ml",
    "median_cfu_ml",
    "min_cfu_ml",
    "max_cfu_ml"
]

microbiology_summary = pd.concat(
    [
        bacteria_summary[columns],
        fungi_summary[columns],
        other_summary[columns]
    ],
    ignore_index=True
)

microbiology_summary.to_csv(
    TABLES / "24_table2_soil_microbiology.csv",
    index=False
)


# ============================================================
# 6. AISLAMIENTO PDA CUALITATIVO
# ============================================================

isolation = pd.read_csv(
    PROCESSED / "pda_isolation_classified.csv"
)

isolation_table = isolation[
    [
        "soil",
        "time_h",
        "dilution",
        "observation",
        "has_observation",
        "bacterial_growth",
        "fungal_growth",
        "overall_growth"
    ]
].copy()

isolation_table.to_csv(
    TABLES / "24_tableS1_pda_isolation.csv",
    index=False
)


# Resumen de presencia/ausencia
# Solo 24 y 48 h tienen observaciones.

observed = isolation.loc[
    isolation["has_observation"] == True
].copy()

isolation_summary = (
    observed
    .groupby(
        [
            "soil",
            "time_h",
            "overall_growth"
        ],
        dropna=False
    )
    .size()
    .rename("n_dilutions")
    .reset_index()
)

isolation_summary.to_csv(
    TABLES / "24_pda_isolation_summary.csv",
    index=False
)


# ============================================================
# 7. PERFIL ESPECÍFICO DE CAPULÍN
# ============================================================

capulin_phys = soil_summary.loc[
    soil_summary["soil"] == "Capulin"
].copy()

capulin_phys.to_csv(
    TABLES / "24_capulin_physicochemical_profile.csv",
    index=False
)

capulin_micro = microbiology_summary.loc[
    microbiology_summary["soil"] == "Capulin"
].copy()

capulin_micro.to_csv(
    TABLES / "24_capulin_microbiological_profile.csv",
    index=False
)


# ============================================================
# 8. RESUMEN PARA INTERPRETACIÓN
# ============================================================

report = TABLES / "24_module1_results_summary.txt"

with report.open("w", encoding="utf-8") as out:

    out.write("=" * 100 + "\n")
    out.write(
        "CHECKPOINT 25 — RESULTADOS FINALES DEL MÓDULO 1\n"
    )
    out.write("=" * 100 + "\n\n")

    out.write(
        "CARACTERIZACIÓN FISICOQUÍMICA\n"
    )
    out.write("-" * 100 + "\n")

    out.write(
        soil_summary[
            [
                "soil",
                "variable_code",
                "unit",
                "n_subsamples",
                "mean",
                "sd"
            ]
        ].to_string(index=False)
    )

    out.write("\n\n")

    out.write(
        "RECUENTOS MICROBIOLÓGICOS POR DILUCIÓN\n"
    )
    out.write("-" * 100 + "\n")

    out.write(
        microbiology_summary[
            [
                "microbial_group",
                "soil",
                "dilution",
                "n_counts",
                "mean_cfu_ml",
                "sd_cfu_ml",
                "median_cfu_ml"
            ]
        ].to_string(index=False)
    )

    out.write("\n\n")

    out.write(
        "AISLAMIENTO PDA — CRECIMIENTO GENERAL\n"
    )
    out.write("-" * 100 + "\n")

    out.write(
        isolation_summary.to_string(index=False)
    )

    out.write("\n\n")

    out.write(
        "CRITERIOS DE INTERPRETACIÓN\n"
    )
    out.write("-" * 100 + "\n")

    out.write(
        "1. Las propiedades fisicoquímicas se resumen "
        "descriptivamente; las tres determinaciones son "
        "submuestras de una muestra compuesta.\n"
    )

    out.write(
        "2. Los recuentos microbiológicos se presentan "
        "separados por dilución.\n"
    )

    out.write(
        "3. B1-B3 y las cajas Petri no se consideran "
        "réplicas biológicas independientes.\n"
    )

    out.write(
        "4. No se realizaron pruebas inferenciales "
        "entre suelos.\n"
    )

    out.write(
        "5. Los valores microbiológicos corresponden a "
        "CFU/mL recalculados a partir de los conteos.\n"
    )

    out.write(
        "6. Los ceros se conservaron como ceros y los "
        "conteos ausentes no fueron imputados.\n"
    )

    out.write(
        "7. La clasificación del aislamiento PDA no "
        "representa una escala cuantitativa de abundancia.\n"
    )


# ============================================================
# SALIDA
# ============================================================

print("=" * 90)
print("CHECKPOINT 25 COMPLETADO")
print("=" * 90)

print("\nTabla 1:")
print(
    TABLES /
    "24_table1_soil_physicochemical_manuscript.csv"
)

print("\nTabla 2:")
print(
    TABLES /
    "24_table2_soil_microbiology.csv"
)

print("\nTabla suplementaria PDA:")
print(
    TABLES /
    "24_tableS1_pda_isolation.csv"
)

print("\nPerfil Capulín:")
print(
    TABLES /
    "24_capulin_physicochemical_profile.csv"
)
print(
    TABLES /
    "24_capulin_microbiological_profile.csv"
)

print("\nResumen:")
print(report)
