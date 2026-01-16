# Physical Sanity Check and Validation Evidence

This directory contains machine-readable evidence supporting the physical sanity checks
and data validation reported in Section IV of the IEEE ICGEA 2026 paper.

All artifacts in this folder are generated in a **read-only, evidence-first manner** from
the processed Parquet files and do not modify the underlying dataset.

## Contents

- `table_physical_sanity_summary.csv`  
  A cell-level summary table reporting key physical sanity metrics, including:
  discharge current stability, voltage monotonicity, temperature range,
  cycle-level capacity degradation correlation, and impedance positivity checks
  for cells B0029–B0032.

- `evidence_section_iv.json`  
  A structured JSON file recording the exact numerical results, dataset shapes,
  and validation outcomes used to support the claims in Section IV.
  This file enables transparent inspection and independent verification.

## Scope and Limitations

- These artifacts support **physical consistency and data validity only**.
- No FAIR compliance scoring or data quality ranking is performed here.
- No data cleaning, correction, or modification is applied.

## Reproducibility

All files in this directory are reproducible using the validation scripts provided
under `scripts/validation/`, with the processed Parquet inputs stored separately.

