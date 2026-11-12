#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "lab_degradation_analysis.csv"
)

OUTPUT = (
    PROJECT_DIR
    / "results"
    / "tables"
    / "21_lab_algebra_validation.txt"
)


def check(a, b, atol=1e-5):
    return np.isclose(
        a,
        b,
        atol=atol,
        rtol=1e-6,
        equal_nan=False
    )


def main():

    df = pd.read_csv(INPUT)

    tests = {
        "mg_per_50g_soil = 10 * mg_per_5g_soil":
            check(
                df["mg_per_50g_soil"],
                10 * df["mg_per_5g_soil"]
            ),

        "mg_degraded_original = 10 - mg_per_50g_soil":
            check(
                df["mg_degraded_original"],
                10 - df["mg_per_50g_soil"]
            ),

        "removal_pct_original = 10 * mg_degraded_original":
            check(
                df["removal_pct_original"],
                10 * df["mg_degraded_original"]
            ),

        "retained_pct = 100 - removal_pct_original":
            check(
                df["retained_pct"],
                100 - df["removal_pct_original"]
            ),

        "mg_retained = 500 * retained_pct / 100":
            check(
                df["mg_retained"],
                500 * df["retained_pct"] / 100
            ),

        "mg_degraded = 500 - mg_retained":
            check(
                df["mg_degraded"],
                500 - df["mg_retained"]
            ),

        "mg_degraded = hplc_500ppm":
            check(
                df["mg_degraded"],
                df["hplc_500ppm"]
            ),

        "biodegradation_pct = removal_pct_original":
            check(
                df["biodegradation_pct"],
                df["removal_pct_original"]
            ),

        "biodegradation_pct = 100 * mg_degraded / 500":
            check(
                df["biodegradation_pct"],
                100 * df["mg_degraded"] / 500
            ),
    }

    with OUTPUT.open(
        "w",
        encoding="utf-8"
    ) as out:

        out.write("=" * 100 + "\n")
        out.write(
            "VALIDACIÓN ALGEBRAICA — BASE 1 ANALÍTICA\n"
        )
        out.write("=" * 100 + "\n\n")

        out.write(
            f"Observaciones analizadas: {len(df)}\n\n"
        )

        for name, result in tests.items():

            n_ok = int(result.sum())
            n_fail = int((~result).sum())

            out.write(
                f"{name}\n"
                f"  Coinciden: {n_ok}/{len(df)}\n"
                f"  No coinciden: {n_fail}\n\n"
            )

        out.write("=" * 100 + "\n")
        out.write("CONCLUSIÓN AUTOMÁTICA\n")
        out.write("=" * 100 + "\n\n")

        all_pass = all(
            result.all()
            for result in tests.values()
        )

        out.write(
            f"Todas las relaciones se cumplen: "
            f"{all_pass}\n"
        )

    print("=" * 90)
    print("VALIDACIÓN ALGEBRAICA COMPLETADA")
    print("=" * 90)

    print(
        f"\nObservaciones: {len(df)}"
    )

    for name, result in tests.items():
        print(
            f"{int(result.sum()):2d}/{len(df)}  "
            f"{name}"
        )

    print(f"\nReporte:\n{OUTPUT}")


if __name__ == "__main__":
    main()

