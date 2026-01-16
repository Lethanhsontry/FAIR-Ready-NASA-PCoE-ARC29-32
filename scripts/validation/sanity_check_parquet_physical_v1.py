"""
Physical sanity checks for inspection and traceability only.

This script performs read-only inspections on finalized Parquet artifacts
to verify basic physical plausibility and internal consistency of discharge,
voltage, temperature, and impedance signals.

No data modification, interpolation, smoothing, or statistical inference
is performed. The script does NOT generate figures or numerical results
reported in any manuscript.
"""

import os
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------
# Input / Output configuration
# ---------------------------------------------------------------------

RAW_DIR = "PATH_TO_PROCESSED_PARQUET"
OUT_DIR = "sanity_outputs_parquet"

os.makedirs(OUT_DIR, exist_ok=True)

CYCLES_FP = os.path.join(RAW_DIR, "cycles_raw.parquet")
MEAS_FP = os.path.join(RAW_DIR, "measurements_raw.parquet")
IMP_FP = os.path.join(RAW_DIR, "impedance_raw.parquet")


def main():
    print("=" * 100)
    print("PHYSICAL SANITY CHECKS — PARQUET (INSPECTION AND TRACEABILITY)")
    print("=" * 100)

    # ------------------------------------------------------------------
    print("\n[LOAD DATA]")
    cycles = pd.read_parquet(CYCLES_FP)
    meas = pd.read_parquet(MEAS_FP)
    imp = pd.read_parquet(IMP_FP)

    print("cycles_raw:", cycles.shape)
    print("measurements_raw:", meas.shape)
    print("impedance_raw:", imp.shape)

    # ------------------------------------------------------------------
    print("\n[CHECK 1] DISCHARGE SELECTION")
    dis = meas[meas["operation_type"] == "discharge"].copy()
    print("Discharge samples:", dis.shape[0])
    print(
        "Unique discharge cycles:",
        dis.groupby(["cell_id", "cycle_index"]).ngroups,
    )

    # ------------------------------------------------------------------
    print("\n[CHECK 2] TIME MONOTONICITY (t_index)")
    time_viol = []
    for (cell, cyc), g in dis.groupby(["cell_id", "cycle_index"]):
        idx = g.sort_values("t_index")["t_index"].to_numpy()
        if len(idx) > 1:
            frac_non_inc = np.mean(np.diff(idx) <= 0)
            if frac_non_inc > 0:
                time_viol.append((cell, cyc, frac_non_inc))

    print("Cycles with non-increasing t_index:", len(time_viol))
    if time_viol:
        print("Sample violations:", time_viol[:5])

    # ------------------------------------------------------------------
    print("\n[CHECK 3] CURRENT STABILITY (DISCHARGE)")
    cur_stats = []
    for (cell, cyc), g in dis.groupby(["cell_id", "cycle_index"]):
        cur = g["Current_measured"].to_numpy()
        if len(cur) >= 20:
            cur_stats.append(
                {
                    "cell_id": cell,
                    "cycle_index": cyc,
                    "mean_A": float(np.mean(cur)),
                    "std_A": float(np.std(cur)),
                }
            )

    cur_df = pd.DataFrame(cur_stats)
    if not cur_df.empty:
        print(cur_df.groupby("cell_id")[["mean_A", "std_A"]].describe())

    # ------------------------------------------------------------------
    print("\n[CHECK 4] VOLTAGE MONOTONICITY (DISCHARGE)")
    v_rows = []
    for (cell, cyc), g in dis.groupby(["cell_id", "cycle_index"]):
        v = g.sort_values("t_index")["Voltage_measured"].to_numpy()
        if len(v) > 2:
            frac_dv_neg = np.mean(np.diff(v) < 0)
            v_rows.append(
                {
                    "cell_id": cell,
                    "cycle_index": cyc,
                    "frac_dV_negative": frac_dv_neg,
                }
            )

    v_df = pd.DataFrame(v_rows)
    if not v_df.empty:
        print(v_df.groupby("cell_id")["frac_dV_negative"].describe())

    # ------------------------------------------------------------------
    print("\n[CHECK 5] TEMPERATURE RANGE (DISCHARGE)")
    t_rows = []
    for (cell, cyc), g in dis.groupby(["cell_id", "cycle_index"]):
        T = g["Temperature_measured"].to_numpy()
        if len(T) > 0:
            t_rows.append(
                {
                    "cell_id": cell,
                    "cycle_index": cyc,
                    "Tmin_C": float(np.min(T)),
                    "Tmax_C": float(np.max(T)),
                }
            )

    t_df = pd.DataFrame(t_rows)
    if not t_df.empty:
        print(t_df.groupby("cell_id")[["Tmin_C", "Tmax_C"]].describe())

    # ------------------------------------------------------------------
    print("\n[CHECK 6] IMPEDANCE POSITIVITY")
    re_nonpos = int((imp["Re"] <= 0).sum())
    rct_nonpos = int((imp["Rct"] <= 0).sum())

    print("Re <= 0 count:", re_nonpos, "/", len(imp))
    print("Rct <= 0 count:", rct_nonpos, "/", len(imp))

    print("\nSANITY CHECK COMPLETE — NO DATA MODIFIED")


if __name__ == "__main__":
    main()
