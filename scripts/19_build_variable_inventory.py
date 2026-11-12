#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
19_build_variable_inventory.py

Construye un inventario reproducible de los datasets procesados
del proyecto de degradación de atrazina.

Objetivos:
1. Identificar datasets procesados disponibles.
2. Registrar dimensiones y columnas.
3. Clasificar las variables según su posible función analítica.
4. NO combinar datasets.
5. NO realizar análisis estadísticos.
6. NO seleccionar todavía un modelo predictivo.
"""

from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "processed"
RESULTS_DIR = PROJECT_DIR / "results" / "tables"

OUTPUT_INVENTORY = RESULTS_DIR / "19_variable_inventory.csv"
OUTPUT_SUMMARY = RESULTS_DIR / "19_dataset_inventory.txt"


# ============================================================
# DATASETS QUE FORMAN PARTE DEL PROYECTO
# ============================================================

DATASETS = {
    "lab_degradation": {
        "file": "lab_degradation.csv",
        "role": "primary_experimental",
        "description":
            "Laboratory atrazine degradation experiment",
    },

    "lab_degradation_analysis": {
        "file": "lab_degradation_analysis.csv",
        "role": "primary_analytical",
        "description":
            "Laboratory analytical dataset excluding blank",
    },

    "growth_inhibition": {
        "file": "growth_inhibition.csv",
        "role": "microbial_context",
        "description":
            "Microbial growth and inhibition observations",
    },

    "growth_inhibition_base1_isolates": {
        "file": "growth_inhibition_base1_isolates.csv",
        "role": "candidate_covariate_source",
        "description":
            "Growth/inhibition data for isolates R and T",
    },

    "soil_characterization": {
        "file": "soil_characterization.csv",
        "role": "environmental_context",
        "description":
            "Physicochemical characterization of soils",
    },

    "soil_characterization_capulin": {
        "file": "capulin_soil_characterization.csv",
        "role": "experimental_context",
        "description":
            "Capulin soil physicochemical characterization",
    },

    "pda_isolation": {
        "file": "pda_isolation_observations.csv",
        "role": "isolation_context",
        "description":
            "Qualitative PDA isolation observations",
    },

    "pdab1_microbiology": {
        "file": "pdab1_microbiology.csv",
        "role": "soil_microbiology_context",
        "description":
            "Actinomycetes and other microbiological media",
    },

    "pda_bacteria": {
        "file": "pdab1_pda_bacteria.csv",
        "role": "soil_microbiology_context",
        "description":
            "Bacterial colony counts and CFU/mL on PDA",
    },

    "pda_fungi": {
        "file": "pdab1_pda_fungi.csv",
        "role": "soil_microbiology_context",
        "description":
            "Fungal colony counts and CFU/mL on PDA",
    },

    "greenhouse_degradation": {
        "file": "greenhouse_degradation.csv",
        "role": "secondary_experimental",
        "description":
            "Greenhouse experiment including blank",
    },

    "greenhouse_degradation_analysis": {
        "file": "greenhouse_degradation_analysis.csv",
        "role": "secondary_analytical",
        "description":
            "Greenhouse analytical dataset excluding blank",
    },
}


# ============================================================
# CLASIFICACIÓN CONSERVADORA
# ============================================================

def classify_variable(dataset_name, variable):

    v = variable.lower()

    # --------------------------------------------------------
    # Identificadores / trazabilidad
    # --------------------------------------------------------

    identifiers = {
        "source_row",
        "sample_id",
        "count_cell",
        "cfu_cell",
        "replicate",
        "block",
        "soil_code",
    }

    if v in identifiers:
        return "identifier_or_traceability"

    if v.startswith("formula_"):
        return "traceability"

    # --------------------------------------------------------
    # Variables de diseño
    # --------------------------------------------------------

    design_variables = {
        "treatment",
        "treatment_name",
        "time_days",
        "time_factor",
        "system",
        "soil",
        "dilution",
        "dilution_exponent",
        "microbial_group",
        "organism_group",
        "medium",
    }

    if v in design_variables:
        return "experimental_design"

    # --------------------------------------------------------
    # Exclusión / control de análisis
    # --------------------------------------------------------

    if v in {
        "include_analysis",
        "exclusion_reason",
    }:
        return "analysis_control"

    # --------------------------------------------------------
    # Variables nominales
    # --------------------------------------------------------

    if "initial_atrazine_nominal" in v:
        return "experimental_condition"

    # --------------------------------------------------------
    # Medición instrumental
    # --------------------------------------------------------

    if v == "hplc_area":
        return "primary_measurement"

    if v == "colony_count":
        return "primary_measurement"

    # --------------------------------------------------------
    # UFC/mL
    # --------------------------------------------------------

    if "cfu_per_ml" in v:
        return "derived_measurement"

    if v == "inoculated_volume_ml":
        return "experimental_parameter"

    # --------------------------------------------------------
    # Variables derivadas de atrazina
    # --------------------------------------------------------

    greenhouse_derived = {
        "mg_per_ml",
        "soil_mass_multiplier",
        "atrazine_extract_mg",
        "atrazine_retained_pct",
        "atrazine_retained_soil_mg",
        "atrazine_degraded_soil_mg",
        "soil_biodegradation_pct",
        "atrazine_degraded_plant_original_mg",
        "atrazine_degraded_plant_mg",
        "total_atrazine_degraded_mg",
        "global_bioremediation_pct",
    }

    if v in greenhouse_derived:
        return "derived_measurement"

    # J y K de Base 4 estaban registrados directamente
    if v in {
        "atrazine_retained_plant_mg",
        "atrazine_degraded_soil_considering_plant_mg",
    }:
        return "recorded_measurement"

    # --------------------------------------------------------
    # Clasificación por nombres generales
    # --------------------------------------------------------

    if "biodegrad" in v:
        return "candidate_response"

    if "growth" in v or "inhibition" in v:
        return "candidate_contextual_predictor"

    # --------------------------------------------------------
    # No clasificamos automáticamente lo desconocido
    # --------------------------------------------------------

    return "review_required"


def main():

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    inventory = []
    dataset_summary = []

    for dataset_name, metadata in DATASETS.items():

        path = DATA_DIR / metadata["file"]

        if not path.exists():

            dataset_summary.append(
                {
                    "dataset": dataset_name,
                    "file": metadata["file"],
                    "exists": False,
                    "rows": None,
                    "columns": None,
                    "role": metadata["role"],
                }
            )

            continue

        df = pd.read_csv(path)

        dataset_summary.append(
            {
                "dataset": dataset_name,
                "file": metadata["file"],
                "exists": True,
                "rows": len(df),
                "columns": len(df.columns),
                "role": metadata["role"],
            }
        )

        for column in df.columns:

            inventory.append(
                {
                    "dataset": dataset_name,
                    "file": metadata["file"],
                    "dataset_role": metadata["role"],
                    "variable": column,
                    "dtype": str(df[column].dtype),
                    "non_missing": int(
                        df[column].notna().sum()
                    ),
                    "missing": int(
                        df[column].isna().sum()
                    ),
                    "unique_values": int(
                        df[column].nunique(
                            dropna=True
                        )
                    ),
                    "variable_class":
                        classify_variable(
                            dataset_name,
                            column
                        ),
                }
            )

    inventory_df = pd.DataFrame(inventory)
    summary_df = pd.DataFrame(dataset_summary)

    inventory_df.to_csv(
        OUTPUT_INVENTORY,
        index=False
    )

    with OUTPUT_SUMMARY.open(
        "w",
        encoding="utf-8"
    ) as out:

        out.write("=" * 110 + "\n")
        out.write(
            "INVENTARIO DE DATASETS PROCESADOS\n"
        )
        out.write("=" * 110 + "\n\n")

        out.write(
            summary_df.to_string(index=False)
        )

        out.write("\n\n")

        out.write("=" * 110 + "\n")
        out.write(
            "VARIABLES QUE REQUIEREN REVISIÓN\n"
        )
        out.write("=" * 110 + "\n\n")

        review = inventory_df.loc[
            inventory_df[
                "variable_class"
            ].eq("review_required"),
            [
                "dataset",
                "variable",
                "dtype",
                "non_missing",
                "unique_values",
            ],
        ]

        if len(review):

            out.write(
                review.to_string(index=False)
            )

        else:

            out.write(
                "Ninguna.\n"
            )

        out.write("\n\n")

        out.write("=" * 110 + "\n")
        out.write(
            "CLASES DE VARIABLES\n"
        )
        out.write("=" * 110 + "\n\n")

        counts = (
            inventory_df[
                "variable_class"
            ]
            .value_counts()
        )

        out.write(
            counts.to_string()
        )

        out.write("\n")

    print("=" * 90)
    print("INVENTARIO DE VARIABLES COMPLETADO")
    print("=" * 90)

    print(
        f"\nDatasets registrados: "
        f"{len(DATASETS)}"
    )

    print(
        f"Datasets encontrados: "
        f"{summary_df['exists'].sum()}"
    )

    print(
        f"Variables inventariadas: "
        f"{len(inventory_df)}"
    )

    print(
        "\nVariables que requieren revisión: "
        f"{(inventory_df['variable_class'] == 'review_required').sum()}"
    )

    print(
        f"\nInventario:\n{OUTPUT_INVENTORY}"
    )

    print(
        f"\nResumen:\n{OUTPUT_SUMMARY}"
    )


if __name__ == "__main__":
    main()
