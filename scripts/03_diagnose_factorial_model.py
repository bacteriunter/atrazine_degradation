#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
03_diagnose_factorial_model.py

Diagnóstico de supuestos del modelo factorial del experimento
de degradación de atrazina en laboratorio.

Entrada:
    data/processed/lab_degradation_analysis.csv

Diseño:
    4 tratamientos × 4 tiempos × 3 réplicas
    = 48 unidades experimentales independientes.

Tratamientos:
    Te = testigo contaminado sin microorganismos
    R  = Rhizobium
    T  = Trichoderma
    RT = Rhizobium + Trichoderma

Modelo utilizado exclusivamente para diagnóstico:
    biodegradation_pct ~ C(treatment) * C(time_factor)

El tiempo se trata como factor categórico.

Este script:
    - ajusta el modelo para obtener residuos;
    - evalúa visualmente los residuos;
    - calcula Shapiro-Wilk sobre los residuos;
    - calcula Brown-Forsythe entre las 16 celdas experimentales;
    - identifica residuos estandarizados extremos sin eliminarlos;
    - NO calcula ANOVA;
    - NO realiza comparaciones post hoc;
    - NO transforma la respuesta;
    - NO elimina observaciones.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
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

TABLE_DIR = PROJECT_DIR / "results" / "tables"
FIGURE_DIR = PROJECT_DIR / "results" / "figures"

DIAGNOSTIC_FILE = (
    TABLE_DIR
    / "03_factorial_diagnostics.txt"
)

RESIDUAL_FILE = (
    TABLE_DIR
    / "03_factorial_residuals.csv"
)

CELL_FILE = (
    TABLE_DIR
    / "03_factorial_cell_variability.csv"
)

FIG_RESIDUALS = (
    FIGURE_DIR
    / "03_residuals_vs_fitted.png"
)

FIG_QQ = (
    FIGURE_DIR
    / "03_residuals_qq.png"
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
# FUNCIÓN AUXILIAR
# ============================================================

def write_both(text, handle):
    print(text)
    handle.write(text + "\n")


# ============================================================
# PROGRAMA
# ============================================================

def main():

    TABLE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    FIGURE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Lectura
    # --------------------------------------------------------

    df = pd.read_csv(INPUT_FILE)

    # --------------------------------------------------------
    # Validación del dataset
    # --------------------------------------------------------

    required_columns = {
        "sample_code",
        "treatment",
        "time_days",
        "replicate",
        "include_analysis",
        "biodegradation_pct",
    }

    missing_columns = (
        required_columns - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Faltan columnas requeridas: "
            + ", ".join(sorted(missing_columns))
        )

    if len(df) != 48:
        raise ValueError(
            f"Se esperaban 48 observaciones y "
            f"se encontraron {len(df)}."
        )

    treatments_found = set(
        df["treatment"].astype(str).unique()
    )

    if treatments_found != set(TREATMENT_ORDER):
        raise ValueError(
            "Tratamientos inesperados: "
            f"{sorted(treatments_found)}"
        )

    if "B" in treatments_found:
        raise ValueError(
            "B no debe aparecer en el dataset analítico."
        )

    if not df["include_analysis"].all():
        raise ValueError(
            "Existen observaciones no elegibles "
            "en el dataset analítico."
        )

    # --------------------------------------------------------
    # Factores
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

    counts = (
        df
        .groupby(
            ["treatment", "time_factor"],
            observed=False
        )
        .size()
        .unstack(fill_value=0)
    )

    if not (counts == 3).all().all():
        raise ValueError(
            "El diseño no corresponde a "
            "4 × 4 × 3."
        )

    # --------------------------------------------------------
    # Modelo factorial completo
    #
    # Con interacción completa, los fitted values
    # corresponden a las medias de las 16 celdas.
    # --------------------------------------------------------

    model = smf.ols(
        "biodegradation_pct ~ "
        "C(treatment) * C(time_factor)",
        data=df
    ).fit()

    # --------------------------------------------------------
    # Residuos
    # --------------------------------------------------------

    influence = model.get_influence()

    df["fitted"] = model.fittedvalues
    df["residual"] = model.resid

    df["standardized_residual"] = (
        influence.resid_studentized_internal
    )

    # --------------------------------------------------------
    # Shapiro-Wilk
    # --------------------------------------------------------

    shapiro_w, shapiro_p = stats.shapiro(
        df["residual"]
    )

    # --------------------------------------------------------
    # Brown-Forsythe
    #
    # Levene con center="median".
    # Se comparan las varianzas de las 16 celdas.
    # --------------------------------------------------------

    groups = []

    for treatment in TREATMENT_ORDER:
        for time in TIME_ORDER:

            values = df.loc[
                (df["treatment"] == treatment)
                & (df["time_days"] == time),
                "biodegradation_pct"
            ].to_numpy()

            groups.append(values)

    bf_stat, bf_p = stats.levene(
        *groups,
        center="median"
    )

    # --------------------------------------------------------
    # Variabilidad por celda
    # --------------------------------------------------------

    cell_variability = (
        df
        .groupby(
            ["treatment", "time_days"],
            observed=True
        )
        ["biodegradation_pct"]
        .agg(
            n="count",
            mean="mean",
            sd="std",
            minimum="min",
            maximum="max"
        )
        .reset_index()
    )

    cell_variability["cv_pct"] = (
        cell_variability["sd"]
        / cell_variability["mean"]
        * 100
    )

    cell_variability.to_csv(
        CELL_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Exportar residuos
    # --------------------------------------------------------

    residual_output = df[
        [
            "sample_code",
            "treatment",
            "time_days",
            "replicate",
            "biodegradation_pct",
            "fitted",
            "residual",
            "standardized_residual",
        ]
    ].copy()

    residual_output[
        "abs_standardized_residual"
    ] = (
        residual_output[
            "standardized_residual"
        ].abs()
    )

    residual_output = residual_output.sort_values(
        "abs_standardized_residual",
        ascending=False
    )

    residual_output.to_csv(
        RESIDUAL_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Conteo de residuos grandes
    # --------------------------------------------------------

    n_gt_2 = int(
        (
            df["standardized_residual"].abs() > 2
        ).sum()
    )

    n_gt_3 = int(
        (
            df["standardized_residual"].abs() > 3
        ).sum()
    )

    # --------------------------------------------------------
    # FIGURA 1
    # Residuos vs fitted
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(7, 6)
    )

    ax.scatter(
        df["fitted"],
        df["residual"],
        alpha=0.8
    )

    ax.axhline(
        y=0,
        linestyle="--",
        linewidth=1
    )

    ax.set_xlabel(
        "Fitted biodegradation (%)"
    )

    ax.set_ylabel(
        "Residual"
    )

    fig.tight_layout()

    fig.savefig(
        FIG_RESIDUALS,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    # --------------------------------------------------------
    # FIGURA 2
    # Q-Q plot
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(7, 6)
    )

    sm.qqplot(
        df["residual"],
        line="45",
        fit=True,
        ax=ax
    )

    ax.set_title(
        "Q-Q plot of factorial-model residuals"
    )

    fig.tight_layout()

    fig.savefig(
        FIG_QQ,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    # --------------------------------------------------------
    # REPORTE
    # --------------------------------------------------------

    with DIAGNOSTIC_FILE.open(
        "w",
        encoding="utf-8"
    ) as handle:

        write_both(
            "=" * 72,
            handle
        )

        write_both(
            "DIAGNÓSTICO DEL MODELO FACTORIAL",
            handle
        )

        write_both(
            "=" * 72,
            handle
        )

        write_both(
            f"\nObservaciones: {len(df)}",
            handle
        )

        write_both(
            "\nDiseño:",
            handle
        )

        write_both(
            counts.to_string(),
            handle
        )

        write_both(
            "\nModelo diagnóstico:",
            handle
        )

        write_both(
            "biodegradation_pct ~ "
            "C(treatment) * C(time_factor)",
            handle
        )

        write_both(
            "\nGrados de libertad residuales:",
            handle
        )

        write_both(
            f"{int(model.df_resid)}",
            handle
        )

        write_both(
            "\nShapiro-Wilk sobre residuos:",
            handle
        )

        write_both(
            f"W = {shapiro_w:.6f}",
            handle
        )

        write_both(
            f"p = {shapiro_p:.6g}",
            handle
        )

        write_both(
            "\nBrown-Forsythe entre las 16 celdas:",
            handle
        )

        write_both(
            f"Statistic = {bf_stat:.6f}",
            handle
        )

        write_both(
            f"p = {bf_p:.6g}",
            handle
        )

        write_both(
            "\nResiduos estandarizados:",
            handle
        )

        write_both(
            f"|residuo| > 2: {n_gt_2}",
            handle
        )

        write_both(
            f"|residuo| > 3: {n_gt_3}",
            handle
        )

        write_both(
            "\nIMPORTANTE:",
            handle
        )

        write_both(
            "Estos resultados son diagnósticos.",
            handle
        )

        write_both(
            "No se calculó ANOVA.",
            handle
        )

        write_both(
            "No se realizaron comparaciones post hoc.",
            handle
        )

        write_both(
            "No se eliminaron observaciones.",
            handle
        )

        write_both(
            "No se transformó la respuesta.",
            handle
        )

    # --------------------------------------------------------
    # TERMINAL
    # --------------------------------------------------------

    print("\n10 residuos estandarizados de mayor magnitud:")

    print(
        residual_output.head(10).to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )

    print("\nArchivos generados:")
    print(DIAGNOSTIC_FILE)
    print(RESIDUAL_FILE)
    print(CELL_FILE)
    print(FIG_RESIDUALS)
    print(FIG_QQ)


if __name__ == "__main__":
    main()
