# Atrazine Biodegradation: Experimental Data and Reproducible Analyses

## Overview

This repository contains the original experimental spreadsheets, processed datasets, Python analysis scripts, statistical outputs, and figures for a study investigating atrazine biodegradation under microbial treatments. The project also includes microbial growth and inhibition measurements, physicochemical and microbiological soil characterization, and a greenhouse experiment.

The repository preserves both the analytical workflow and intermediate outputs to facilitate inspection, traceability, and future reproduction of the analyses. A complete clean-environment, end-to-end rerun has not yet been independently verified.

## Repository layout

```text
atrazine_degradation/
├── data/
│   ├── raw/              Original experimental Excel workbooks
│   └── processed/        Standardized datasets used in analyses
├── scripts/              Numbered Python scripts and figure variants
├── results/
│   ├── figures/          Generated figures
│   ├── models/           Model summaries
│   └── tables/           Statistical tables and validation outputs
├── docs/
│   ├── analysis_log.md
│   ├── conda_packages.txt
│   ├── python_version.txt
│   └── raw_data_sha256.txt
├── environment.yml
└── README.md
```

## Original datasets

The original workbooks are retained in `data/raw/` and treated as immutable records.

| Workbook | Experimental component |
| --- | --- |
| `base_1.xlsx` | Laboratory atrazine biodegradation |
| `base_2.xlsx` | Microbial growth and inhibition |
| `base_3.xlsx` | Soil physicochemical characterization |
| `base_4.xlsx` | Greenhouse experiment |
| `pda_aislamiento.xlsx` | Microbial isolation |
| `pdab1_bacterias.xlsx` | Bacterial enumeration |

SHA-256 checksums for the original datasets are recorded in `docs/raw_data_sha256.txt`. Derived datasets are stored separately under `data/processed/`.

## Analysis scripts

The numbered scripts document the progression from inspection and data preparation to statistical analyses and manuscript-oriented outputs.

| Scripts | Main purpose |
| --- | --- |
| `00`–`06` | Laboratory dataset preparation, exploration, factorial analysis, and Tukey comparisons |
| `07`–`08` | Growth and inhibition data inspection and preparation |
| `09`–`16` | Soil characterization, microbial isolation, and microbiological count processing |
| `17`–`23` | Greenhouse preparation, formula checks, dataset inventory, and descriptive validation |
| `24`–`27` | Soil and microbiology summary tables and figures |
| `28` | Comparative analysis of microbial growth/inhibition measurements |
| `29`–`31` | Temporal model comparison, leave-one-time-out validation, and final model outputs |
| `32`–`34` | Greenhouse model diagnostics, statistical inference, and final outputs |
| `35`–`36` | Exploratory multivariate analysis, PCA, and Spearman correlations |

Two additional scripts preserve manuscript-oriented graphical adjustments while retaining the corresponding original scripts:

- `scripts/28_module2_comparative_analysis_italics_friendly.py`
- `scripts/36_final_multivariate_base2_italics.py`

These variants should not be interpreted as independent experimental analyses. Some scripts may overwrite existing processed data, tables, or figures when rerun. Review their input and output paths before execution.

## Experimental design and interpretation

### Laboratory biodegradation

The laboratory experiment used sterilized Capulín soil, destructive sampling at 5, 10, 20, and 40 days, and three independent experimental replicates for each treatment–time combination. Five experimental groups were recorded:

- **B:** blank soil without atrazine or microbial inoculation;
- **Te:** atrazine-contaminated soil without microbial inoculation;
- **R:** atrazine with *Rhizobium*;
- **T:** atrazine with *Trichoderma*;
- **RT:** atrazine with *Rhizobium* and *Trichoderma*.

The nominal initial atrazine concentration was 500 ppm; this value was not an HPLC measurement at time zero. The five-group design contains 60 experimental observations (5 groups × 4 times × 3 replicates). The four atrazine-exposed groups contain 48 observations. The distinction between the original experimental inventory and the analytical subsets must be preserved when interpreting model results.

### Soil and microbiological measurements

The three physicochemical determinations per soil variable were subsamples of a composite soil sample, not independent biological soil replicates. Similarly, microbiological blocks and Petri dish replicates derived from composite samples were not treated as independent biological soil samples. These observations were used for descriptive characterization without pseudoreplicated between-soil inference.

The historically selected dilutions in the bacterial enumeration workbook were retained. Colony-forming unit values were recalculated from recorded colony counts, dilution factors, and inoculated volumes, while preserving original values for traceability. Further details are available in `docs/analysis_log.md`.

## Software environment

The project uses Python 3.10 and the scientific Python ecosystem, including NumPy, pandas, SciPy, statsmodels, scikit-learn, Matplotlib, and openpyxl. The currently documented local interpreter version is **Python 3.10.21**. A package inventory is retained in `docs/conda_packages.txt`.

Create the Conda environment from the repository root:

```bash
conda env create -f environment.yml
conda activate atrazine_model
```

To run an individual script, for example:

```bash
python scripts/01_prepare_lab_data.py
```

Scripts are organized numerically, but a complete dependency-checked execution order has not yet been validated. Do not assume that running every numbered script in sequence is necessary or that it will leave all archived outputs unchanged.

## Data integrity and reproducibility

- Keep `data/raw/` unchanged and use `docs/raw_data_sha256.txt` to verify the original workbooks.
- Retain historical scripts and analytical outputs for traceability.
- Treat technical and composite-sample measurements according to their documented replication structure.
- Use version control to document any changes to scripts or analytical assumptions.
- Check the destination of generated outputs before rerunning scripts, as existing files may be replaced.

## Citation, release, and licensing

Formal citation metadata, a software/data license, and a permanent archival DOI will be added when the repository's public release is prepared. No DOI or license is asserted at this stage.

## License

- **Source code:** MIT License (see `LICENSE`).
- **Experimental and processed data:** Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0), unless otherwise indicated (see `data/LICENSE.md`).
- **Research manuscript:** Subject to the publishing agreement and journal license.
