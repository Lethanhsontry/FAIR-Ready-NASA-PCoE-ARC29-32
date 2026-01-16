import argparse
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def spearman_corr(x: np.ndarray, y: np.ndarray) -> float:
    x = pd.Series(x).rank(method="average").to_numpy()
    y = pd.Series(y).rank(method="average").to_numpy()
    if len(x) < 3:
        return float("nan")
    x = x - np.mean(x)
    y = y - np.mean(y)
    denom = np.sqrt(np.sum(x**2) * np.sum(y**2))
    if denom == 0:
        return float("nan")
    return float(np.sum(x * y) / denom)


def voltage_monotonic_fraction(v: np.ndarray) -> float:
    dv = np.diff(v)
    if dv.size == 0:
        return float("nan")
    return float(np.mean(dv < 0))


def pick_representative_discharge_cycle(meas_dis: pd.DataFrame, cell_id: str) -> Tuple[int, pd.DataFrame]:
    sub = meas_dis[meas_dis["cell_id"] == cell_id].copy()
    if sub.empty:
        raise ValueError(f"No discharge samples for cell {cell_id}")
    cycle_idx = int(sub["cycle_index"].min())
    cyc = sub[sub["cycle_index"] == cycle_idx].copy().sort_values("t_index")
    return cycle_idx, cyc


def time_monotonicity_violations(meas_dis: pd.DataFrame) -> int:
    violations = 0
    for (_, _), df in meas_dis.groupby(["cell_id", "cycle_index"], sort=True):
        t = df.sort_values("t_index")["t_index"].to_numpy()
        if np.any(np.diff(t) <= 0):
            violations += 1
    return violations


def discharge_cycle_level_stats(meas_dis: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (cell, cyc), df in meas_dis.groupby(["cell_id", "cycle_index"], sort=True):
        df = df.sort_values("t_index")
        i = df["Current_measured"].to_numpy()
        v = df["Voltage_measured"].to_numpy()
        temp = df["Temperature_measured"].to_numpy()
        cap = df["Capacity"].to_numpy()

        rows.append({
            "cell_id": cell,
            "cycle_index": int(cyc),
            "n_samples": int(len(df)),
            "i_mean_A": float(np.mean(i)),
            "i_std_A": float(np.std(i, ddof=1)) if len(i) > 1 else float("nan"),
            "v_mono_frac": float(voltage_monotonic_fraction(v)),
            "t_min_C": float(np.min(temp)),
            "t_max_C": float(np.max(temp)),
            "cap_max_Ah": float(np.nanmax(cap)),
        })
    return pd.DataFrame(rows)


def impedance_positivity(imp: pd.DataFrame) -> Dict[str, float]:
    re_nonpos = int((imp["Re"] <= 0).sum())
    rct_nonpos = int((imp["Rct"] <= 0).sum())
    return {
        "impedance_rows": int(len(imp)),
        "re_nonpos_count": re_nonpos,
        "rct_nonpos_count": rct_nonpos,
    }


def plot_capacity_fade_all_cells(cycle_stats: pd.DataFrame, outpath: Path) -> None:
    plt.figure()
    for cell, sub in cycle_stats.groupby("cell_id", sort=True):
        sub = sub.sort_values("cycle_index")
        plt.plot(sub["cycle_index"], sub["cap_max_Ah"], label=cell)
    plt.xlabel("Cycle index")
    plt.ylabel("Discharge capacity (Ah)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()


def plot_discharge_profile(df_cycle: pd.DataFrame, cell_id: str, cycle_idx: int, outpath: Path) -> None:
    t = df_cycle["Time"].to_numpy()
    i = df_cycle["Current_measured"].to_numpy()
    v = df_cycle["Voltage_measured"].to_numpy()
    temp = df_cycle["Temperature_measured"].to_numpy()

    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(6.5, 6.0))
    axes[0].plot(t, i)
    axes[0].set_ylabel("Current (A)")
    axes[0].set_title(f"Representative discharge profile ({cell_id}, cycle {cycle_idx})")
    axes[1].plot(t, v)
    axes[1].set_ylabel("Voltage (V)")
    axes[2].plot(t, temp)
    axes[2].set_ylabel("Temperature (°C)")
    axes[2].set_xlabel("Time (s)")
    fig.tight_layout()
    fig.savefig(outpath, dpi=300)
    plt.close(fig)


def build_cell_summary_table(cycle_stats: pd.DataFrame, meas_dis: pd.DataFrame, imp: pd.DataFrame) -> pd.DataFrame:
    time_viol = time_monotonicity_violations(meas_dis)
    imp_pos = impedance_positivity(imp)

    out = []
    for cell, sub in cycle_stats.groupby("cell_id", sort=True):
        sub = sub.sort_values("cycle_index")

        i_mean = float(np.mean(sub["i_mean_A"]))
        i_std_median = float(np.nanmedian(sub["i_std_A"]))
        v_mono_mean = float(np.mean(sub["v_mono_frac"]))
        tmin_mean = float(np.mean(sub["t_min_C"]))
        tmax_mean = float(np.mean(sub["t_max_C"]))
        n_cycles = int(sub["cycle_index"].nunique())
        corr = spearman_corr(sub["cycle_index"].to_numpy(), sub["cap_max_Ah"].to_numpy())

        out.append({
            "Cell": cell,
            "N_discharge_cycles": n_cycles,
            "I_mean_A": i_mean,
            "I_std_median_A": i_std_median,
            "V_monotonic_frac_mean": v_mono_mean,
            "Tmin_mean_C": tmin_mean,
            "Tmax_mean_C": tmax_mean,
# Monotonicity indicator used solely for sanity checking.
# This value is NOT intended as a statistical result or
# for quantitative inference.
            "capacity_cycle_monotonicity_indicator": float(corr),
            "TimeMonotonicityViolations_allCells": int(time_viol),
            "Re_nonpos_allRows": int(imp_pos["re_nonpos_count"]),
            "Rct_nonpos_allRows": int(imp_pos["rct_nonpos_count"]),
            "Impedance_rows": int(imp_pos["impedance_rows"]),
        })

    return pd.DataFrame(out)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Physical sanity checks and evidence extraction from finalized Parquet artifacts."
    )
    parser.add_argument(
        "--raw_parquet_dir",
        type=str,
        default="PATH_TO_PROCESSED_PARQUET",
        help="Directory containing finalized raw Parquet artifacts"
    )
    parser.add_argument("--out_dir", type=str, default=str(Path.cwd() / "sanity_outputs_parquet_evidence"))
    parser.add_argument("--rep_cell", type=str, default="B0029")
    args = parser.parse_args()

    raw_dir = Path(args.raw_parquet_dir)
    out_dir = Path(args.out_dir)
    figs_dir = out_dir / "figures"
    evidence_dir = out_dir / "evidence"
    ensure_dir(figs_dir)
    ensure_dir(evidence_dir)

    cycles_path = raw_dir / "cycles_raw.parquet"
    meas_path = raw_dir / "measurements_raw.parquet"
    imp_path = raw_dir / "impedance_raw.parquet"

    print("=" * 100)
    print("PARQUET SANITY (EVIDENCE EXPORT) — READ-ONLY")
    print("=" * 100)
    print(f"cycles_raw: {cycles_path} exists={cycles_path.exists()}")
    print(f"measurements_raw: {meas_path} exists={meas_path.exists()}")
    print(f"impedance_raw: {imp_path} exists={imp_path.exists()}")
    if not (cycles_path.exists() and meas_path.exists() and imp_path.exists()):
        raise FileNotFoundError("Missing one or more required Parquet files.")

    cycles = pd.read_parquet(cycles_path)
    meas = pd.read_parquet(meas_path)
    imp = pd.read_parquet(imp_path)

    print("\n[SHAPES]")
    print(f"cycles_raw: {cycles.shape}")
    print(f"measurements_raw: {meas.shape}")
    print(f"impedance_raw: {imp.shape}")

    meas_dis = meas[meas["operation_type"] == "discharge"].copy()
    print("\n[DISCHARGE]")
    print(f"Discharge samples: {len(meas_dis)}")
    print(f"Unique discharge cycles: {meas_dis[['cell_id','cycle_index']].drop_duplicates().shape[0]}")

    cycle_stats = discharge_cycle_level_stats(meas_dis)
    print("\n[CYCLE-LEVEL STATS]")
    print(f"Rows: {cycle_stats.shape[0]}")

    # Figures
    fig_capacity = figs_dir / "fig_capacity_fade_all_cells.png"
    plot_capacity_fade_all_cells(cycle_stats, fig_capacity)
    print(f"SAVED FIG: {fig_capacity}")

    rep_cycle_idx, rep_df = pick_representative_discharge_cycle(meas_dis, args.rep_cell)
    fig_discharge = figs_dir / f"fig_discharge_profile_{args.rep_cell}.png"
    plot_discharge_profile(rep_df, args.rep_cell, rep_cycle_idx, fig_discharge)
    print(f"SAVED FIG: {fig_discharge}")

    # Evidence tables
    cell_summary = build_cell_summary_table(cycle_stats, meas_dis, imp)
    cell_summary_csv = evidence_dir / "table_physical_sanity_summary.csv"
    cell_summary.to_csv(cell_summary_csv, index=False)
    print(f"SAVED EVIDENCE: {cell_summary_csv}")

    # Export a compact JSON for Section IV numbers
    # Keep it minimal: global + per-cell summary
    global_evidence = {
        "discharge_samples": int(len(meas_dis)),
        "unique_discharge_cycles": int(meas_dis[['cell_id','cycle_index']].drop_duplicates().shape[0]),
        "time_monotonicity_violations_allCells": int(time_monotonicity_violations(meas_dis)),
        "impedance": impedance_positivity(imp),
        "rep_cell": args.rep_cell,
        "rep_cycle_index": int(rep_cycle_idx),
        "rep_cycle_samples": int(len(rep_df)),
        "fig_capacity": str(fig_capacity),
        "fig_discharge": str(fig_discharge),
        "table_summary_csv": str(cell_summary_csv),
    }
    json_path = evidence_dir / "evidence_section_iv.json"
    pd.Series(global_evidence).to_json(json_path, indent=2, force_ascii=False)
    print(f"SAVED EVIDENCE: {json_path}")

    print("\nDONE: Evidence exported (no LaTeX generated, no data modified).")


if __name__ == "__main__":
    main()
