#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
18_prepare_greenhouse_data.py

Preparación reproducible de Base 4:
experimento de invernadero con suelo Capulín.

Diseño:
    6 tratamientos
    3 repeticiones por tratamiento
    18 observaciones

Tratamientos:
    R
    RT
    T
    B
    F
    Tes

Decisiones:
1. B es un blanco sin atrazina añadida.
2. B se conserva en el dataset completo.
3. B se excluye del dataset analítico de degradación.
4. La concentración nominal de atrazina para los demás
   tratamientos es 1000 ppm.
5. Las fórmulas originales se conservan para trazabilidad.
6. No se modifica el uso histórico de D*4 en B-12a y Tes-19a.
7. Valores de degradación por planta extremadamente próximos
   a cero se normalizan a 0 únicamente para eliminar residuos
   numéricos de punto flotante.
8. No se realizan análisis estadísticos.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import load_workbook


# ============================================================
# RUTAS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "base_4.xlsx"
)

OUTPUT_ALL = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "greenhouse_degradation.csv"
)

OUTPUT_ANALYSIS = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "greenhouse_degradation_analysis.csv"
)

OUTPUT_VALIDATION = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "18_greenhouse_validation.txt"
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

SHEET = "Hoja1"

TREATMENT_NAMES = {
    "R": "Rhizobium",
    "RT": "Rhizobium + Trichoderma",
    "T": "Trichoderma",
    "B": "Blank",
    "F": "Bean",
    "Tes": "Control + bean",
}

EXPECTED_COUNTS = {
    "R": 3,
    "RT": 3,
    "T": 3,
    "B": 3,
    "F": 3,
    "Tes": 3,
}


# ============================================================
# FUNCIONES
# ============================================================

def numeric(value):

    if value is None:
        return np.nan

    if isinstance(
        value,
        (int, float, np.integer, np.floating)
    ):
        return float(value)

    return np.nan


def main():

    OUTPUT_ALL.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_VALIDATION.parent.mkdir(
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

    ws_v = wb_values[SHEET]
    ws_f = wb_formulas[SHEET]

    records = []

    # ========================================================
    # EXTRAER LAS 18 OBSERVACIONES
    # ========================================================

    for row in range(2, 20):

        treatment = ws_v[f"A{row}"].value
        sample_id = ws_v[f"B{row}"].value

        if treatment is None:
            continue

        # ----------------------------------------------------
        # Atrazina nominal
        # ----------------------------------------------------

        if treatment == "B":

            initial_atrazine_nominal_ppm = 0.0
            include_analysis = False
            exclusion_reason = "no_atrazine_added"

        else:

            initial_atrazine_nominal_ppm = 1000.0
            include_analysis = True
            exclusion_reason = ""

        # ----------------------------------------------------
        # Valores originales
        # ----------------------------------------------------

        area = numeric(
            ws_v[f"C{row}"].value
        )

        mg_per_ml = numeric(
            ws_v[f"D{row}"].value
        )

        atrazine_extract_mg = numeric(
            ws_v[f"E{row}"].value
        )

        atrazine_retained_pct = numeric(
            ws_v[f"F{row}"].value
        )

        atrazine_retained_soil_mg = numeric(
            ws_v[f"G{row}"].value
        )

        atrazine_degraded_soil_mg = numeric(
            ws_v[f"H{row}"].value
        )

        soil_biodegradation_pct = numeric(
            ws_v[f"I{row}"].value
        )

        atrazine_retained_plant_mg = numeric(
            ws_v[f"J{row}"].value
        )

        atrazine_degraded_soil_considering_plant_mg = numeric(
            ws_v[f"K{row}"].value
        )

        atrazine_degraded_plant_original_mg = numeric(
            ws_v[f"L{row}"].value
        )

        total_atrazine_degraded_mg = numeric(
            ws_v[f"M{row}"].value
        )

        global_bioremediation_pct = numeric(
            ws_v[f"N{row}"].value
        )

        # ----------------------------------------------------
        # Corregir SOLO residuo de punto flotante cercano a 0
        # ----------------------------------------------------

        if pd.notna(
            atrazine_degraded_plant_original_mg
        ):

            if np.isclose(
                atrazine_degraded_plant_original_mg,
                0.0,
                atol=1e-10,
                rtol=0.0,
            ):

                atrazine_degraded_plant_mg = 0.0

            else:

                atrazine_degraded_plant_mg = (
                    atrazine_degraded_plant_original_mg
                )

        else:

            atrazine_degraded_plant_mg = np.nan

        # ----------------------------------------------------
        # Detectar multiplicador usado en columna E
        # ----------------------------------------------------

        formula_e = ws_f[f"E{row}"].value

        if isinstance(formula_e, str):

            if "*5" in formula_e:
                soil_mass_multiplier = 5.0

            elif "*4" in formula_e:
                soil_mass_multiplier = 4.0

            else:
                soil_mass_multiplier = np.nan

        else:
            soil_mass_multiplier = np.nan

        # ----------------------------------------------------
        # Registro
        # ----------------------------------------------------

        records.append(
            {
                "source_row":
                    row,

                "treatment":
                    treatment,

                "treatment_name":
                    TREATMENT_NAMES.get(
                        treatment,
                        treatment
                    ),

                "sample_id":
                    sample_id,

                "soil":
                    "Capulin",

                "system":
                    "greenhouse",

                "time_days":
                    40,

                "initial_atrazine_nominal_ppm":
                    initial_atrazine_nominal_ppm,

                "include_analysis":
                    include_analysis,

                "exclusion_reason":
                    exclusion_reason,

                # Medición instrumental
                "hplc_area":
                    area,

                # Cadena derivada C -> I
                "mg_per_ml":
                    mg_per_ml,

                "soil_mass_multiplier":
                    soil_mass_multiplier,

                "atrazine_extract_mg":
                    atrazine_extract_mg,

                "atrazine_retained_pct":
                    atrazine_retained_pct,

                "atrazine_retained_soil_mg":
                    atrazine_retained_soil_mg,

                "atrazine_degraded_soil_mg":
                    atrazine_degraded_soil_mg,

                "soil_biodegradation_pct":
                    soil_biodegradation_pct,

                # Valores registrados directamente
                "atrazine_retained_plant_mg":
                    atrazine_retained_plant_mg,

                "atrazine_degraded_soil_considering_plant_mg":
                    atrazine_degraded_soil_considering_plant_mg,

                # Original + corrección numérica
                "atrazine_degraded_plant_original_mg":
                    atrazine_degraded_plant_original_mg,

                "atrazine_degraded_plant_mg":
                    atrazine_degraded_plant_mg,

                "total_atrazine_degraded_mg":
                    total_atrazine_degraded_mg,

                "global_bioremediation_pct":
                    global_bioremediation_pct,

                # Fórmulas originales
                "formula_mg_per_ml":
                    ws_f[f"D{row}"].value,

                "formula_atrazine_extract_mg":
                    ws_f[f"E{row}"].value,

                "formula_atrazine_retained_pct":
                    ws_f[f"F{row}"].value,

                "formula_atrazine_retained_soil_mg":
                    ws_f[f"G{row}"].value,

                "formula_atrazine_degraded_soil_mg":
                    ws_f[f"H{row}"].value,

                "formula_soil_biodegradation_pct":
                    ws_f[f"I{row}"].value,

                "formula_atrazine_degraded_plant_mg":
                    ws_f[f"L{row}"].value,

                "formula_total_atrazine_degraded_mg":
                    ws_f[f"M{row}"].value,

                "formula_global_bioremediation_pct":
                    ws_f[f"N{row}"].value,
            }
        )

    df = pd.DataFrame(records)

    # ========================================================
    # DATASET ANALÍTICO
    # ========================================================

    analysis = (
        df.loc[
            df["include_analysis"]
        ]
        .copy()
        .reset_index(drop=True)
    )

    # ========================================================
    # VALIDACIONES
    # ========================================================

    treatment_counts = (
        df["treatment"]
        .value_counts()
        .sort_index()
    )

    expected_total = 18
    expected_analysis = 15

    all_counts_correct = all(
        treatment_counts.get(
            treatment,
            0
        ) == expected
        for treatment, expected
        in EXPECTED_COUNTS.items()
    )

    n_blank = (
        df["treatment"]
        .eq("B")
        .sum()
    )

    n_excluded = (
        (~df["include_analysis"])
        .sum()
    )

    n_times4 = (
        df["soil_mass_multiplier"]
        .eq(4)
        .sum()
    )

    n_times5 = (
        df["soil_mass_multiplier"]
        .eq(5)
        .sum()
    )

    n_fp_zero_corrected = (
        (
            df[
                "atrazine_degraded_plant_original_mg"
            ].abs() <= 1e-10
        )
        &
        (
            df[
                "atrazine_degraded_plant_original_mg"
            ] != 0
        )
    ).sum()

    # ========================================================
    # GUARDAR
    # ========================================================

    df.to_csv(
        OUTPUT_ALL,
        index=False
    )

    analysis.to_csv(
        OUTPUT_ANALYSIS,
        index=False
    )

    # ========================================================
    # REPORTE
    # ========================================================

    with OUTPUT_VALIDATION.open(
        "w",
        encoding="utf-8"
    ) as out:

        out.write("=" * 100 + "\n")
        out.write(
            "VALIDACIÓN — BASE 4 / INVERNADERO\n"
        )
        out.write("=" * 100 + "\n\n")

        out.write(
            f"Observaciones completas: "
            f"{len(df)} "
            f"(esperadas: {expected_total})\n"
        )

        out.write(
            f"Observaciones analíticas: "
            f"{len(analysis)} "
            f"(esperadas: {expected_analysis})\n\n"
        )

        out.write(
            "OBSERVACIONES POR TRATAMIENTO\n"
        )
        out.write("-" * 100 + "\n")

        out.write(
            treatment_counts.to_string()
        )

        out.write("\n\n")

        out.write(
            f"Todos los tratamientos tienen "
            f"n=3: {all_counts_correct}\n"
        )

        out.write(
            f"Blancos B: {n_blank}\n"
        )

        out.write(
            f"Observaciones excluidas: "
            f"{n_excluded}\n\n"
        )

        out.write(
            "MULTIPLICADOR HISTÓRICO "
            "DE COLUMNA E\n"
        )
        out.write("-" * 100 + "\n")

        out.write(
            f"Multiplicador x5: {n_times5}\n"
        )

        out.write(
            f"Multiplicador x4: {n_times4}\n\n"
        )

        special = df.loc[
            df["soil_mass_multiplier"] == 4,
            [
                "treatment",
                "sample_id",
                "source_row",
                "soil_mass_multiplier",
                "formula_atrazine_extract_mg",
            ],
        ]

        out.write(
            special.to_string(index=False)
        )

        out.write("\n\n")

        out.write(
            "RESIDUOS NUMÉRICOS "
            "NORMALIZADOS A CERO\n"
        )
        out.write("-" * 100 + "\n")

        out.write(
            f"N: {n_fp_zero_corrected}\n\n"
        )

        out.write(
            "DECISIONES\n"
        )
        out.write("-" * 100 + "\n")

        out.write(
            "1. B corresponde a blanco sin "
            "atrazina añadida.\n"
        )

        out.write(
            "2. B se conserva en el dataset "
            "completo y se excluye del "
            "dataset analítico.\n"
        )

        out.write(
            "3. La dosis nominal para R, RT, T, "
            "F y Tes es 1000 ppm.\n"
        )

        out.write(
            "4. La dosis nominal para B se "
            "registra como 0 ppm.\n"
        )

        out.write(
            "5. Los multiplicadores x4 de "
            "B-12a y Tes-19a se conservan "
            "sin reinterpretación.\n"
        )

        out.write(
            "6. No se imputaron valores "
            "ausentes.\n"
        )

        out.write(
            "7. No se realizaron pruebas "
            "estadísticas.\n"
        )

    # ========================================================
    # TERMINAL
    # ========================================================

    print("=" * 90)
    print("BASE 4 PREPARADA")
    print("=" * 90)

    print(
        f"\nDataset completo: "
        f"{len(df)} observaciones"
    )

    print(
        f"Dataset analítico: "
        f"{len(analysis)} observaciones"
    )

    print(
        f"\nB excluidos: {n_excluded}"
    )

    print(
        f"Multiplicadores x4: {n_times4}"
    )

    print(
        f"Residuos numéricos -> 0: "
        f"{n_fp_zero_corrected}"
    )

    print(
        f"\nDataset:\n{OUTPUT_ALL}"
    )

    print(
        f"\nDataset analítico:\n"
        f"{OUTPUT_ANALYSIS}"
    )

    print(
        f"\nValidación:\n"
        f"{OUTPUT_VALIDATION}"
    )


if __name__ == "__main__":
    main()
