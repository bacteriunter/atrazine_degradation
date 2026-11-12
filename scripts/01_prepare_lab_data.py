#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
01_prepare_lab_data.py

Preparación reproducible del experimento de laboratorio con atrazina.

Diseño original:
- Suelo: Capulín
- Suelo completamente esterilizado
- Muestreo destructivo
- Tiempos: 5, 10, 20 y 40 días
- 3 unidades experimentales independientes por tratamiento × tiempo

Tratamientos:
B  = blanco; sin atrazina, sin microorganismos
Te = testigo; 500 ppm atrazina, sin microorganismos
R  = 500 ppm atrazina + Rhizobium
T  = 500 ppm atrazina + Trichoderma
RT = 500 ppm atrazina + Rhizobium + Trichoderma

B se conserva para trazabilidad, pero se excluye del dataset analítico
porque no recibió atrazina y, por tanto, el porcentaje de biodegradación
reportado para B no se considera interpretable como degradación de
atrazina añadida.

La concentración inicial de 500 ppm es nominal/teórica y no corresponde
a una medición HPLC en t=0.

Salidas:
1. lab_degradation.csv
   60 observaciones procesadas, incluyendo B.

2. lab_degradation_analysis.csv
   48 observaciones elegibles para análisis: Te, R, T y RT.

3. 01_lab_data_validation.txt
   Registro de validación y criterios de inclusión.

NO realiza análisis estadístico.
"""

from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd


# ============================================================
# RUTAS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR / "data" / "raw" / "base_1.xlsx"
)

PROCESSED_FILE = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "lab_degradation.csv"
)

ANALYSIS_FILE = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "lab_degradation_analysis.csv"
)

REPORT_FILE = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "01_lab_data_validation.txt"
)


# ============================================================
# FUNCIONES
# ============================================================

def parse_sample(value):

    if pd.isna(value):
        return None, None

    value = str(value).strip()

    match = re.fullmatch(
        r"(RT|Te|R|T|B)(5|10|20|40)",
        value,
        flags=re.IGNORECASE
    )

    if match is None:
        return None, None

    treatment_raw = match.group(1)
    time_days = int(match.group(2))

    treatment_map = {
        "b": "B",
        "te": "Te",
        "r": "R",
        "t": "T",
        "rt": "RT",
    }

    treatment = treatment_map[
        treatment_raw.lower()
    ]

    return treatment, time_days


def write_both(text, handle):
    print(text)
    handle.write(text + "\n")


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    PROCESSED_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Lectura del archivo original
    # --------------------------------------------------------

    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name="Hoja1",
        engine="openpyxl"
    )

    raw.columns = [
        str(column).strip()
        for column in raw.columns
    ]

    # --------------------------------------------------------
    # Identificación de unidades experimentales
    # --------------------------------------------------------

    parsed = raw["Muestra"].apply(parse_sample)

    raw["treatment"] = [
        value[0] for value in parsed
    ]

    raw["time_days"] = [
        value[1] for value in parsed
    ]

    experimental = raw.loc[
        raw["treatment"].notna()
        & raw["time_days"].notna()
    ].copy()

    # --------------------------------------------------------
    # Réplicas
    # --------------------------------------------------------

    experimental["replicate"] = (
        experimental
        .groupby(
            ["treatment", "time_days"],
            sort=False
        )
        .cumcount()
        + 1
    )

    # --------------------------------------------------------
    # Concentración nominal inicial
    # --------------------------------------------------------

    experimental[
        "initial_atrazine_nominal_ppm"
    ] = np.where(
        experimental["treatment"].eq("B"),
        0.0,
        500.0
    )

    # --------------------------------------------------------
    # Elegibilidad analítica
    # --------------------------------------------------------

    experimental["include_analysis"] = (
        experimental["treatment"] != "B"
    )

    experimental["exclusion_reason"] = np.where(
        experimental["treatment"].eq("B"),
        "no_atrazine_added",
        ""
    )

    # --------------------------------------------------------
    # Dataset procesado
    # --------------------------------------------------------

    processed = pd.DataFrame({

        "sample_code":
            experimental["Muestra"]
            .astype(str)
            .str.strip(),

        "treatment":
            experimental["treatment"],

        "time_days":
            experimental["time_days"]
            .astype(int),

        "replicate":
            experimental["replicate"]
            .astype(int),

        "initial_atrazine_nominal_ppm":
            experimental[
                "initial_atrazine_nominal_ppm"
            ],

        "include_analysis":
            experimental["include_analysis"],

        "exclusion_reason":
            experimental["exclusion_reason"],

        "hplc_500ppm":
            experimental["500 ppm"],

        "mg_per_5g_soil":
            experimental["mg/5g suelo"],

        "mg_per_50g_soil":
            experimental["10mg/50 suelo"],

        "mg_degraded_original":
            experimental["mg degradados"],

        "removal_pct_original":
            experimental["% remosión"],

        "retained_pct":
            experimental["% retenido"],

        "mg_retained":
            experimental["mg reteni"],

        "mg_degraded":
            experimental["mg degrada"],

        "biodegradation_pct":
            experimental["% biodegra"],
    })

    # --------------------------------------------------------
    # Dataset analítico
    # --------------------------------------------------------

    analysis = (
        processed.loc[
            processed["include_analysis"]
        ]
        .copy()
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Validaciones
    # --------------------------------------------------------

    processed_counts = (
        processed
        .groupby(
            ["treatment", "time_days"]
        )
        .size()
        .unstack(fill_value=0)
        .reindex(
            index=["B", "Te", "R", "T", "RT"],
            columns=[5, 10, 20, 40]
        )
    )

    analysis_counts = (
        analysis
        .groupby(
            ["treatment", "time_days"]
        )
        .size()
        .unstack(fill_value=0)
        .reindex(
            index=["Te", "R", "T", "RT"],
            columns=[5, 10, 20, 40]
        )
    )

    duplicate_processed = int(
        processed.duplicated(
            subset=[
                "treatment",
                "time_days",
                "replicate"
            ]
        ).sum()
    )

    duplicate_analysis = int(
        analysis.duplicated(
            subset=[
                "treatment",
                "time_days",
                "replicate"
            ]
        ).sum()
    )

    removal_equal = np.allclose(
        processed["removal_pct_original"],
        processed["biodegradation_pct"],
        equal_nan=True
    )

    processed_ok = (
        len(processed) == 60
        and (processed_counts == 3).all().all()
        and duplicate_processed == 0
    )

    analysis_ok = (
        len(analysis) == 48
        and set(analysis["treatment"]) ==
        {"Te", "R", "T", "RT"}
        and (analysis_counts == 3).all().all()
        and duplicate_analysis == 0
        and analysis["include_analysis"].all()
    )

    b_ok = (
        len(
            processed[
                processed["treatment"] == "B"
            ]
        ) == 12
        and not processed.loc[
            processed["treatment"] == "B",
            "include_analysis"
        ].any()
        and (
            processed.loc[
                processed["treatment"] == "B",
                "initial_atrazine_nominal_ppm"
            ] == 0
        ).all()
    )

    # --------------------------------------------------------
    # Exportación
    # --------------------------------------------------------

    processed.to_csv(
        PROCESSED_FILE,
        index=False,
        encoding="utf-8"
    )

    analysis.to_csv(
        ANALYSIS_FILE,
        index=False,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Reporte
    # --------------------------------------------------------

    with REPORT_FILE.open(
        "w",
        encoding="utf-8"
    ) as handle:

        write_both(
            "=" * 72,
            handle
        )

        write_both(
            "VALIDACIÓN — PREPARACIÓN DE DATOS DE LABORATORIO",
            handle
        )

        write_both(
            "=" * 72,
            handle
        )

        write_both(
            f"\nFilas originales del Excel: {len(raw)}",
            handle
        )

        write_both(
            f"Unidades experimentales reconocidas: "
            f"{len(processed)}",
            handle
        )

        write_both(
            f"Filas auxiliares/no experimentales: "
            f"{len(raw) - len(processed)}",
            handle
        )

        write_both(
            "\nDATASET PROCESADO:",
            handle
        )

        write_both(
            f"n = {len(processed)}",
            handle
        )

        write_both(
            processed_counts.to_string(),
            handle
        )

        write_both(
            "\nDATASET ANALÍTICO:",
            handle
        )

        write_both(
            f"n = {len(analysis)}",
            handle
        )

        write_both(
            analysis_counts.to_string(),
            handle
        )

        write_both(
            "\nTratamientos analíticos:",
            handle
        )

        write_both(
            ", ".join(
                sorted(
                    analysis["treatment"].unique()
                )
            ),
            handle
        )

        write_both(
            "\nTratamiento B:",
            handle
        )

        write_both(
            "Conservado en dataset procesado: Sí",
            handle
        )

        write_both(
            "Incluido en dataset analítico: No",
            handle
        )

        write_both(
            "Razón: no_atrazine_added",
            handle
        )

        write_both(
            "\nConcentración nominal:",
            handle
        )

        write_both(
            "B = 0 ppm",
            handle
        )

        write_both(
            "Te/R/T/RT = 500 ppm",
            handle
        )

        write_both(
            "500 ppm corresponde a concentración "
            "nominal/teórica, no a una medición HPLC "
            "en t=0.",
            handle
        )

        write_both(
            "\n% remoción == % biodegradación:",
            handle
        )

        write_both(
            str(removal_equal),
            handle
        )

        write_both(
            "\nValidaciones:",
            handle
        )

        write_both(
            f"Dataset procesado 5 × 4 × 3: "
            f"{processed_ok}",
            handle
        )

        write_both(
            f"Dataset analítico 4 × 4 × 3: "
            f"{analysis_ok}",
            handle
        )

        write_both(
            f"B correctamente marcado para exclusión: "
            f"{b_ok}",
            handle
        )

        write_both(
            "\nNo se realizaron análisis estadísticos.",
            handle
        )

    if not (
        processed_ok
        and analysis_ok
        and b_ok
        and removal_equal
    ):
        sys.exit(
            "\nERROR: alguna validación no fue superada."
        )

    print("\nArchivos generados:")
    print(PROCESSED_FILE)
    print(ANALYSIS_FILE)
    print(REPORT_FILE)


if __name__ == "__main__":
    main()
