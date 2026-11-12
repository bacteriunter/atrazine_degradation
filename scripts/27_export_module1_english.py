#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
TABLES = PROJECT / "results" / "tables"

# ============================================================
# LABELS
# ============================================================

soil_names = {
    "Capulin": "Capulín",
    "Santa Ana": "Santa Ana",
    "Tepantitla": "Tepantitla"
}

variable_names = {
    "D": "Density",
    "pH": "pH",
    "H": "Gravimetric moisture",
    "N": "Nitrogen",
    "CO": "Organic carbon",
    "MO": "Organic matter",
    "CIC": "Cation exchange capacity"
}

group_names = {
    "PDA_bacteria": "PDA bacteria",
    "PDA_fungi": "PDA fungi",
    "Actinomicetos": "Actinomycetes",
    "Extracto de suelo": "Soil extract medium",
    "PDA acidificado": "Acidified PDA"
}

growth_names = {
    "present": "Present",
    "absent": "Absent",
    "not_determined": "Not determined"
}


# ============================================================
# TABLE 1 — SOIL PHYSICOCHEMICAL CHARACTERIZATION
# ============================================================

df = pd.read_csv(
    TABLES / "24_table1_soil_physicochemical.csv"
)

df["Soil"] = df["soil"].replace(soil_names)

df["Property"] = df["variable_code"].replace(
    variable_names
)

df["Unit"] = df["unit"]

df["Mean ± SD"] = (
    df["mean"].map(lambda x: f"{x:.4f}")
    + " ± "
    + df["sd"].map(lambda x: f"{x:.4f}")
)

table1 = df[
    [
        "Soil",
        "Property",
        "Unit",
        "Mean ± SD"
    ]
].copy()

table1.to_csv(
    TABLES /
    "27_Table1_soil_physicochemical_characterization.csv",
    index=False
)


# ============================================================
# TABLE 2 — SOIL MICROBIOLOGICAL CHARACTERIZATION
# ============================================================

df = pd.read_csv(
    TABLES / "24_table2_soil_microbiology.csv"
)

df["Microbial group / medium"] = (
    df["microbial_group"]
    .replace(group_names)
)

df["Soil"] = (
    df["soil"]
    .replace(soil_names)
)

df["Dilution"] = df["dilution"]

table2 = df[
    [
        "Microbial group / medium",
        "Soil",
        "Dilution",
        "n_counts",
        "mean_cfu_ml",
        "sd_cfu_ml",
        "median_cfu_ml",
        "min_cfu_ml",
        "max_cfu_ml"
    ]
].copy()

table2 = table2.rename(
    columns={
        "n_counts": "Technical observations (n)",
        "mean_cfu_ml": "Mean CFU/mL",
        "sd_cfu_ml": "SD CFU/mL",
        "median_cfu_ml": "Median CFU/mL",
        "min_cfu_ml": "Minimum CFU/mL",
        "max_cfu_ml": "Maximum CFU/mL"
    }
)

table2.to_csv(
    TABLES /
    "27_Table2_soil_microbiological_characterization.csv",
    index=False
)


# ============================================================
# SUPPLEMENTARY TABLE — PDA ISOLATION
# ============================================================

df = pd.read_csv(
    TABLES / "24_tableS1_pda_isolation.csv"
)

df["soil"] = df["soil"].replace(soil_names)

for column in [
    "bacterial_growth",
    "fungal_growth",
    "overall_growth"
]:
    df[column] = df[column].replace(growth_names)

df = df.rename(
    columns={
        "soil": "Soil",
        "time_h": "Time (h)",
        "dilution": "Dilution exponent",
        "observation": "Original observation",
        "has_observation": "Observation recorded",
        "bacterial_growth": "Bacterial growth",
        "fungal_growth": "Fungal growth",
        "overall_growth": "Overall growth"
    }
)

df.to_csv(
    TABLES /
    "27_TableS1_PDA_isolation_classification.csv",
    index=False
)


# ============================================================
# CAPULÍN PROFILE
# ============================================================

cap = table1.loc[
    table1["Soil"] == "Capulín"
].copy()

cap.to_csv(
    TABLES /
    "27_Capulin_physicochemical_profile.csv",
    index=False
)

capm = table2.loc[
    table2["Soil"] == "Capulín"
].copy()

capm.to_csv(
    TABLES /
    "27_Capulin_microbiological_profile.csv",
    index=False
)


print("=" * 80)
print("MODULE 1 — ENGLISH TABLES EXPORTED")
print("=" * 80)

for f in sorted(TABLES.glob("27_*.csv")):
    print(f.name)
