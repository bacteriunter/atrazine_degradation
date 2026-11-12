#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
04_factorial_anova.py

ANOVA factorial del experimento de degradación de atrazina
en laboratorio.

Entrada:
    data/processed/lab_degradation_analysis.csv

Diseño:
    4 tratamientos × 4 tiempos × 3 réplicas
    = 48 unidades experimentales independientes.

Factores:
    treatment:
        Te = testigo contaminado sin microorganismos
        R  = Rhizobium
        T  = Trichoderma
        RT = Rhizobium + Trichoderma

    time_days:
        5, 10, 20 y 40 días

Respuesta:
    biodegradation_pct

Modelo:
    biodegradation_pct ~ C(treatment) * C(time_factor)

Se calculan:
    - suma de cuadrados
    - grados de libertad
    - estadístico F
    - valor p
    - eta cuadrado parcial (partial eta squared)

NO realiza comparaciones post hoc.
NO elimina observaciones.
NO transforma la respuesta.
"""

from pathlib import Path
import sys

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


# ============================================================
# RUTAS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "lab_degradation_analysis.csv"
)

TABLE_DIR = (
    PROJECT_DIR
    / "results"
    / "tables"
)

ANOVA_CSV = (
    TABLE_DIR
    / "04_factorial_anova.csv"
)

ANOVA_TXT = (
    TABLE_DIR
    / "04_factorial_anova.txt"
)

MODEL_TXT = (
    TABLE_DIR
    / "04_factorial_model_summary.txt"
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

TREATMENT_ORDER = [
    "Te",
    "R",
    "T",
    "RT",
]

TIME_ORDER = [
    5,
    10,
    20,
    40,
]


# ============================================================
# PROGRAMA
# ============================================================

def main():

    TABLE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Lectura
    # --------------------------------------------------------

    df = pd.read_csv(INPUT_FILE)

    # --------------------------------------------------------
    # Validaciones
    # --------------------------------------------------------

    required_columns = {
        "sample_code",
        "treatment",
        "time_days",
        "replicate",
        "include_analysis",
        "biodegradation_pct",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            "Faltan columnas requeridas: "
            + ", ".join(sorted(missing))
        )

    if len(df) != 48:
        raise ValueError(
            f"Se esperaban 48 observaciones; "
            f"se encontraron {len(df)}."
        )

    observed_treatments = set(
        df["treatment"].astype(str).unique()
    )

    if observed_treatments != set(TREATMENT_ORDER):
        raise ValueError(
            "Tratamientos inesperados: "
            f"{sorted(observed_treatments)}"
        )

    if "B" in observed_treatments:
        raise ValueError(
            "B no debe participar en el ANOVA."
        )

    if not df["include_analysis"].all():
        raise ValueError(
            "Existen observaciones marcadas "
            "como include_analysis=False."
        )

    if df["biodegradation_pct"].isna().any():
        raise ValueError(
            "Hay valores faltantes en biodegradation_pct."
        )

    # --------------------------------------------------------
    # Definición explícita de factores
    # --------------------------------------------------------

    df["treatment"] = pd.Categorical(
        df["treatment"],
        categories=TREATMENT_ORDER,
        ordered=True
    )

    df["time_factor"] = pd.Categorical(
        df["time_days"],
        categories=TIME_ORDER,
        ordered=True
    )

    # --------------------------------------------------------
    # Comprobación del diseño
    # --------------------------------------------------------

    counts = (
        df
        .groupby(
            ["treatment", "time_factor"],
            observed=False
        )
        .size()
        .unstack(fill_value=0)
    )

    design_ok = (counts == 3).all().all()

    if not design_ok:
        raise ValueError(
            "El diseño no corresponde a "
            "4 tratamientos × 4 tiempos × 3 réplicas."
        )

    # --------------------------------------------------------
    # Modelo factorial
    # --------------------------------------------------------

    model = smf.ols(
        "biodegradation_pct ~ "
        "C(treatment) * C(time_factor)",
        data=df
    ).fit()

    # --------------------------------------------------------
    # ANOVA
    #
    # Diseño completamente balanceado.
    # Se utiliza Type II para la tabla inferencial.
    # --------------------------------------------------------

    anova = sm.stats.anova_lm(
        model,
        typ=2
    )

    # --------------------------------------------------------
    # Eta cuadrado parcial
    #
    # eta_p² = SS_effect /
    #          (SS_effect + SS_error)
    # --------------------------------------------------------

    ss_error = anova.loc[
        "Residual",
        "sum_sq"
    ]

    anova["partial_eta_sq"] = pd.NA

    effects = [
        "C(treatment)",
        "C(time_factor)",
        "C(treatment):C(time_factor)",
    ]

    for effect in effects:

        ss_effect = anova.loc[
            effect,
            "sum_sq"
        ]

        anova.loc[
            effect,
            "partial_eta_sq"
        ] = (
            ss_effect
            / (ss_effect + ss_error)
        )

    # --------------------------------------------------------
    # Nombres legibles
    # --------------------------------------------------------

    name_map = {
        "C(treatment)": "Treatment",
        "C(time_factor)": "Time",
        "C(treatment):C(time_factor)":
            "Treatment × Time",
        "Residual": "Residual",
    }

    output = (
        anova
        .reset_index()
        .rename(
            columns={
                "index": "effect",
                "sum_sq": "sum_sq",
                "df": "df",
                "F": "F",
                "PR(>F)": "p_value",
            }
        )
    )

    output["effect"] = (
        output["effect"]
        .replace(name_map)
    )

    # --------------------------------------------------------
    # Guardar CSV
    # --------------------------------------------------------

    output.to_csv(
        ANOVA_CSV,
        index=False
    )

    # --------------------------------------------------------
    # Guardar resumen completo del modelo
    # --------------------------------------------------------

    with MODEL_TXT.open(
        "w",
        encoding="utf-8"
    ) as handle:

        handle.write(
            model.summary().as_text()
        )

        handle.write("\n")

    # --------------------------------------------------------
    # Guardar reporte legible
    # --------------------------------------------------------

    with ANOVA_TXT.open(
        "w",
        encoding="utf-8"
    ) as handle:

        handle.write(
            "=" * 72 + "\n"
        )

        handle.write(
            "ANOVA FACTORIAL — DEGRADACIÓN DE ATRAZINA\n"
        )

        handle.write(
            "=" * 72 + "\n\n"
        )

        handle.write(
            "Respuesta: biodegradation_pct\n"
        )

        handle.write(
            "Modelo: biodegradation_pct ~ "
            "C(treatment) * C(time_factor)\n\n"
        )

        handle.write(
            "Unidades experimentales independientes: "
            f"{len(df)}\n"
        )

        handle.write(
            "Tratamientos: Te, R, T, RT\n"
        )

        handle.write(
            "Tiempos: 5, 10, 20, 40 días\n"
        )

        handle.write(
            "Réplicas por celda: 3\n\n"
        )

        handle.write(
            "Diseño:\n"
        )

        handle.write(
            counts.to_string()
        )

        handle.write(
            "\n\n"
        )

        handle.write(
            "TABLA ANOVA\n"
        )

        handle.write(
            "-" * 72 + "\n"
        )

        handle.write(
            output.to_string(
                index=False,
                float_format=lambda x: f"{x:.6g}"
            )
        )

        handle.write(
            "\n\n"
        )

        handle.write(
            "Tamaño de efecto:\n"
        )

        handle.write(
            "partial eta squared = "
            "SS_effect / (SS_effect + SS_error)\n\n"
        )

        handle.write(
            "No se realizaron comparaciones post hoc.\n"
        )

        handle.write(
            "No se eliminaron observaciones.\n"
        )

        handle.write(
            "No se transformó la variable respuesta.\n"
        )

    # --------------------------------------------------------
    # TERMINAL
    # --------------------------------------------------------

    print("=" * 72)
    print("ANOVA FACTORIAL — DEGRADACIÓN DE ATRAZINA")
    print("=" * 72)

    print("\nDiseño:")
    print(counts.to_string())

    print("\nTabla ANOVA:")

    print(
        output.to_string(
            index=False,
            float_format=lambda x: f"{x:.6g}"
        )
    )

    print("\nArchivos generados:")
    print(ANOVA_CSV)
    print(ANOVA_TXT)
    print(MODEL_TXT)


if __name__ == "__main__":
    main()
