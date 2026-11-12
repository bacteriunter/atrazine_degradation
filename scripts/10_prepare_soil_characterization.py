#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
10_prepare_soil_characterization.py

Preparación de Base 3:
caracterización fisicoquímica de tres suelos.

Estructura confirmada:
    7 variables × 3 suelos × 3 réplicas = 63 observaciones.

Variables:
    D   = densidad (g/cm3)
    pH  = pH (adimensional)
    H   = humedad gravimétrica (% en peso)
    N   = nitrógeno (%)
    CO  = carbono orgánico (%)
    MO  = materia orgánica (%)
    CIC = capacidad de intercambio catiónico (cmol(+)/kg)

Sufijos:
    s = Santa Ana
    c = Capulín
    t = Tepantitla

IMPORTANTE:
- No se modifica el archivo raw.
- No se realizan pruebas inferenciales.
- No se comparan estadísticamente los suelos.
- Las tres observaciones por combinación se conservan como réplicas.
- Capulín se marca como suelo utilizado en los experimentos
  posteriores de degradación.

Salidas:
    data/processed/soil_characterization.csv
    data/processed/capulin_soil_characterization.csv
    results/tables/10_soil_characterization_summary.csv
    results/tables/10_soil_characterization_validation.txt
"""

from pathlib import Path
import re

import pandas as pd


# ============================================================
# RUTAS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "base_3.xlsx"
)

PROCESSED_DIR = (
    PROJECT_DIR
    / "data"
    / "processed"
)

TABLE_DIR = (
    PROJECT_DIR
    / "results"
    / "tables"
)

OUTPUT_ALL = (
    PROCESSED_DIR
    / "soil_characterization.csv"
)

OUTPUT_CAPULIN = (
    PROCESSED_DIR
    / "capulin_soil_characterization.csv"
)

OUTPUT_SUMMARY = (
    TABLE_DIR
    / "10_soil_characterization_summary.csv"
)

OUTPUT_VALIDATION = (
    TABLE_DIR
    / "10_soil_characterization_validation.txt"
)


# ============================================================
# DEFINICIONES CONFIRMADAS
# ============================================================

VARIABLES = {
    "D": {
        "name": "density",
        "description": "Densidad",
        "unit": "g/cm3",
    },
    "pH": {
        "name": "pH",
        "description": "pH",
        "unit": "dimensionless",
    },
    "H": {
        "name": "gravimetric_moisture",
        "description": "Humedad gravimétrica",
        "unit": "% w/w",
    },
    "N": {
        "name": "nitrogen",
        "description": "Nitrógeno",
        "unit": "%",
    },
    "CO": {
        "name": "organic_carbon",
        "description": "Carbono orgánico",
        "unit": "%",
    },
    "MO": {
        "name": "organic_matter",
        "description": "Materia orgánica",
        "unit": "%",
    },
    "CIC": {
        "name": "cation_exchange_capacity",
        "description": "Capacidad de intercambio catiónico",
        "unit": "cmol(+)/kg",
    },
}

SOILS = {
    "s": "Santa Ana",
    "c": "Capulin",
    "t": "Tepantitla",
}


# ============================================================
# FUNCIÓN PARA SEPARAR VARIABLE Y SUELO
# ============================================================

def parse_label(label):

    label = str(label).strip()

    match = re.fullmatch(
        r"(CIC|CO|MO|pH|D|H|N)([sct])",
        label
    )

    if match is None:
        raise ValueError(
            f"Etiqueta no reconocida: {label}"
        )

    variable_code = match.group(1)
    soil_code = match.group(2)

    return variable_code, soil_code


# ============================================================
# PROGRAMA
# ============================================================

def main():

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    TABLE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Lectura sin encabezado
    # --------------------------------------------------------

    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name="Hoja1",
        header=None,
        names=["original_label", "value"]
    )

    # --------------------------------------------------------
    # Validación inicial
    # --------------------------------------------------------

    if len(raw) != 63:
        raise ValueError(
            f"Se esperaban 63 observaciones; "
            f"se encontraron {len(raw)}."
        )

    if raw.isna().any().any():
        raise ValueError(
            "Se encontraron valores faltantes en Base 3."
        )

    # --------------------------------------------------------
    # Separar variable y suelo
    # --------------------------------------------------------

    parsed = raw["original_label"].apply(
        parse_label
    )

    raw["variable_code"] = [
        x[0] for x in parsed
    ]

    raw["soil_code"] = [
        x[1] for x in parsed
    ]

    # --------------------------------------------------------
    # Metadatos
    # --------------------------------------------------------

    raw["variable"] = raw[
        "variable_code"
    ].map(
        lambda x: VARIABLES[x]["name"]
    )

    raw["variable_description"] = raw[
        "variable_code"
    ].map(
        lambda x: VARIABLES[x]["description"]
    )

    raw["unit"] = raw[
        "variable_code"
    ].map(
        lambda x: VARIABLES[x]["unit"]
    )

    raw["soil"] = raw[
        "soil_code"
    ].map(SOILS)

    raw["value"] = pd.to_numeric(
        raw["value"],
        errors="raise"
    )

    # --------------------------------------------------------
    # Asignación de réplica
    #
    # Se asigna 1, 2, 3 según el orden original dentro de
    # cada combinación variable × suelo.
    # --------------------------------------------------------

    raw["replicate"] = (
        raw.groupby(
            [
                "variable_code",
                "soil_code"
            ],
            sort=False
        )
        .cumcount()
        + 1
    )

    # --------------------------------------------------------
    # Marcar suelo utilizado en degradación
    # --------------------------------------------------------

    raw["used_in_degradation_experiments"] = (
        raw["soil_code"] == "c"
    )

    # --------------------------------------------------------
    # Orden final de columnas
    # --------------------------------------------------------

    df = raw[
        [
            "original_label",
            "variable_code",
            "variable",
            "variable_description",
            "unit",
            "soil_code",
            "soil",
            "replicate",
            "value",
            "used_in_degradation_experiments",
        ]
    ].copy()

    # --------------------------------------------------------
    # Validación del diseño
    # --------------------------------------------------------

    counts = (
        df.groupby(
            [
                "variable_code",
                "soil_code"
            ]
        )
        .size()
    )

    if not (counts == 3).all():
        raise ValueError(
            "No todas las combinaciones "
            "variable × suelo tienen 3 réplicas."
        )

    if len(counts) != 21:
        raise ValueError(
            f"Se esperaban 21 combinaciones "
            f"variable × suelo; se encontraron {len(counts)}."
        )

    # --------------------------------------------------------
    # Guardar dataset completo
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_ALL,
        index=False
    )

    # --------------------------------------------------------
    # Dataset específico de Capulín
    # --------------------------------------------------------

    capulin = (
        df.loc[
            df["soil_code"] == "c"
        ]
        .copy()
        .reset_index(drop=True)
    )

    if len(capulin) != 21:
        raise ValueError(
            f"Se esperaban 21 observaciones de Capulín; "
            f"se encontraron {len(capulin)}."
        )

    capulin.to_csv(
        OUTPUT_CAPULIN,
        index=False
    )

    # --------------------------------------------------------
    # Estadística descriptiva
    # --------------------------------------------------------

    summary = (
        df.groupby(
            [
                "soil",
                "variable_code",
                "variable",
                "variable_description",
                "unit"
            ],
            as_index=False,
            sort=False
        )
        .agg(
            n=("value", "size"),
            mean=("value", "mean"),
            sd=("value", "std"),
            minimum=("value", "min"),
            maximum=("value", "max"),
        )
    )

    summary.to_csv(
        OUTPUT_SUMMARY,
        index=False
    )

    # --------------------------------------------------------
    # Reporte de validación
    # --------------------------------------------------------

    with OUTPUT_VALIDATION.open(
        "w",
        encoding="utf-8"
    ) as handle:

        handle.write(
            "=" * 78 + "\n"
        )

        handle.write(
            "VALIDACIÓN — BASE 3: "
            "CARACTERIZACIÓN FISICOQUÍMICA\n"
        )

        handle.write(
            "=" * 78 + "\n\n"
        )

        handle.write(
            f"Observaciones originales: {len(raw)}\n"
        )

        handle.write(
            f"Observaciones procesadas: {len(df)}\n"
        )

        handle.write(
            f"Número de variables: "
            f"{df['variable_code'].nunique()}\n"
        )

        handle.write(
            f"Número de suelos: "
            f"{df['soil_code'].nunique()}\n"
        )

        handle.write(
            "Réplicas esperadas por variable × suelo: 3\n"
        )

        handle.write(
            "Todas las combinaciones tienen 3 réplicas: "
            f"{bool((counts == 3).all())}\n"
        )

        handle.write(
            f"Observaciones de Capulín: {len(capulin)}\n\n"
        )

        handle.write(
            "UNIDADES DOCUMENTADAS\n"
        )

        handle.write(
            "-" * 78 + "\n"
        )

        for code, info in VARIABLES.items():

            handle.write(
                f"{code}: "
                f"{info['description']} "
                f"[{info['unit']}]\n"
            )

        handle.write(
            "\nRESUMEN DESCRIPTIVO — CAPULÍN\n"
        )

        handle.write(
            "-" * 78 + "\n"
        )

        capulin_summary = (
            summary.loc[
                summary["soil"] == "Capulin"
            ]
            [
                [
                    "variable_code",
                    "variable_description",
                    "unit",
                    "n",
                    "mean",
                    "sd",
                    "minimum",
                    "maximum",
                ]
            ]
        )

        handle.write(
            capulin_summary.to_string(
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
            "- No se realizaron pruebas inferenciales "
            "entre suelos.\n"
        )

        handle.write(
            "- No se utilizaron las propiedades del suelo "
            "como predictores del modelo de degradación.\n"
        )

        handle.write(
            "- Capulín se identifica como el suelo utilizado "
            "en los experimentos de degradación.\n"
        )

        handle.write(
            "- Las tres réplicas originales se conservaron "
            "individualmente.\n"
        )

    # --------------------------------------------------------
    # TERMINAL
    # --------------------------------------------------------

    print("=" * 78)
    print(
        "PREPARACIÓN BASE 3 COMPLETADA"
    )
    print("=" * 78)

    print(
        f"\nDataset completo:\n{OUTPUT_ALL}"
    )

    print(
        f"\nDataset Capulín:\n{OUTPUT_CAPULIN}"
    )

    print(
        f"\nResumen descriptivo:\n{OUTPUT_SUMMARY}"
    )

    print(
        f"\nValidación:\n{OUTPUT_VALIDATION}"
    )

    print(
        "\nResumen de Capulín:"
    )

    print(
        capulin_summary.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
