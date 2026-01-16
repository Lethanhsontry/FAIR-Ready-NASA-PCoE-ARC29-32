# FAIR-Ready Lithium-Ion Battery Aging Dataset (NASA PCoE ARC 29–32)

## Overview

This repository provides a FAIR-ready reorganization and standardization of
lithium-ion battery aging data originally released by the NASA Ames Prognostics
Center of Excellence (PCoE).

The work focuses on the ARC 29–32 subset of the NASA PCoE Battery Aging Dataset,
covering four lithium-ion cells (B0029–B0032) with charge, discharge, and
electrochemical impedance spectroscopy (EIS) measurements.

The primary contribution of this repository is not the generation of new
experimental data, but the systematic curation, structuring, and documentation
of existing data to improve its findability, accessibility, interoperability,
and reusability (FAIR principles).

---

## Original Data Source

The original experimental measurements were produced and released by:

**NASA Ames Prognostics Center of Excellence (PCoE)**  
Li-ion Battery Aging Datasets (ARC 29–32 subset)

According to the metadata available on the NASA Open Data Portal, the original
dataset is distributed with **“License not specified”**.

This repository does not claim ownership of the original NASA data.

---

## Data Redistribution Policy

Due to the unspecified license status of the original NASA PCoE dataset, raw and
derived measurement files are not redistributed in this repository.

Specifically, this repository does **not** contain:
- Original `.mat` files from NASA,
- Derived tabular data files (e.g., `.parquet`, `.csv`, `.pkl`),
- Any measurement-level data that could be directly reused without accessing
  the original source.

Users who wish to reproduce the FAIR-ready dataset must obtain the original
data directly from the official NASA PCoE distribution channels.

---

## Repository Contents

This repository contains:

- **Metadata** describing the dataset structure, variables, and provenance
  (`metadata/`),
- **Scripts** for data extraction, transformation, validation, and FAIR
  assessment (`scripts/`),
- **Documentation** supporting reproducible research and academic peer review,
  including materials prepared for peer-reviewed academic dissemination (`docs/`),
- **Citation and licensing information** for the FAIR-ready contribution
  (`CITATION.cff`, `LICENSE`).

No experimental data files are included.

---

## License

The FAIR-ready reorganization, metadata, documentation, and supporting scripts
in this repository are released under the **Creative Commons Attribution 4.0
International (CC BY 4.0)** license.

This license applies **only** to the FAIR-ready contribution and does **not**
alter the legal status of the original NASA PCoE dataset, which remains under
“License not specified”.

See the `LICENSE` file for full details.

---

## Citation

If you use this FAIR-ready curation or the materials provided in this repository, please cite it according to the instructions in the
`CITATION.cff` file.

Users are also expected to appropriately acknowledge the original NASA PCoE
data source in any derivative work.

---

## Intended Use

This repository is intended for:
- Research on battery aging, prognostics, and remaining useful life (RUL),
- FAIR data practices and reproducible research workflows,
- Academic publication and peer review (e.g., ICGEA 2026).

It is **not** intended to serve as a primary data distribution platform for
NASA PCoE experimental measurements.

Additional documentation on data availability and the FAIR assessment of this FAIR-ready contribution is provided in the `docs/` directory.
---

## Contact

For questions related to the FAIR-ready curation, metadata, or repository
structure, please refer to the corresponding authors listed in
`CITATION.cff`.
