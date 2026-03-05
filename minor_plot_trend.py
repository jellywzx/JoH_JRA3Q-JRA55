#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spin-up convergence diagnostics:
1) Monthly land-mean series (as before)
2) Yearly means (as before)
3) Deseasonalized anomalies (monthly climatology removed) for:
   - land_mean_f_rnof
   - land_mean_f_rsur
   - land_mean_f_etr
4) Linear trend slope of anomalies over 1996-2000 (printed + saved)

No CLI args required.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# USER CONFIG (edit here)
# ============================================================
CSV_PATH = Path("landmean_1996_2000.csv")
OUT_DIR  = Path("./")
# ============================================================


# ---------- helpers ----------
def read_data(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    if "date" not in df.columns:
        raise ValueError("CSV must contain a 'date' column in YYYY-MM format.")

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m", errors="coerce")
    if df["date"].isna().any():
        bad = df[df["date"].isna()]
        raise ValueError(f"Failed to parse some dates. Problem rows:\n{bad}")

    # numeric columns
    for c in df.columns:
        if c != "date":
            df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.sort_values("date").reset_index(drop=True)
    return df


def plot_monthly(df: pd.DataFrame, out_png: Path) -> None:
    cols = [c for c in df.columns if c != "date"]
    plt.figure(figsize=(10, 4.5))
    for c in cols:
        plt.plot(df["date"], df[c], linewidth=1.6, label=c)
    plt.xlabel("Date")
    plt.ylabel("Land-mean value")
    plt.title("Spin-up monthly land-mean trend (1996–2000)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=250)
    plt.close()


def plot_yearly(df: pd.DataFrame, out_png: Path) -> None:
    cols = [c for c in df.columns if c != "date"]
    df2 = df.copy()
    df2["year"] = df2["date"].dt.year
    yearly = df2.groupby("year")[cols].mean(numeric_only=True).reset_index()

    plt.figure(figsize=(8, 4.5))
    for c in cols:
        plt.plot(yearly["year"], yearly[c], marker="o", linewidth=1.8, label=c)
    plt.xlabel("Year")
    plt.ylabel("Annual mean (land-mean)")
    plt.title("Spin-up yearly mean trend (1996–2000)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=250)
    plt.close()


def compute_deseasonalized_anomaly(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """
    Remove monthly climatology (1996-2000 mean for each calendar month).
    anomaly(t) = value(t) - climatology(month_of_t)
    """
    out = df[["date"]].copy()
    out["month"] = df["date"].dt.month

    for c in cols:
        clim = df.groupby(df["date"].dt.month)[c].mean(numeric_only=True)  # 1..12
        out[c + "_anom"] = df[c] - out["month"].map(clim)

    return out


def linear_trend_slope(anom_df: pd.DataFrame, col_anom: str) -> tuple[float, float]:
    """
    Fit anomaly = a + b*t, where t is time in years since start.
    Returns:
      b (slope per year), and b_per_decade.
    """
    # time axis in years
    t = (anom_df["date"] - anom_df["date"].iloc[0]).dt.days.values / 365.25
    y = anom_df[col_anom].values

    # drop NaNs
    mask = np.isfinite(t) & np.isfinite(y)
    t = t[mask]
    y = y[mask]

    if len(y) < 3:
        return np.nan, np.nan

    # polyfit: y = p0*t + p1
    b, a = np.polyfit(t, y, 1)
    return float(b), float(b * 10.0)


def plot_anomalies(anom_df: pd.DataFrame, cols_anom: list[str], out_png: Path) -> None:
    plt.figure(figsize=(10, 4.5))

    # --- collect y values for auto ylim ---
    y_all = []
    for c in cols_anom:
        y = anom_df[c].to_numpy()
        y_all.append(y[np.isfinite(y)])
        plt.plot(anom_df["date"], anom_df[c], linewidth=1.5, label=c)

    # horizontal zero line
    plt.axhline(0.0, linewidth=1.0)

    # --- expand y-limits by margin ---
    y_all = np.concatenate(y_all) if len(y_all) > 0 else np.array([0.0])
    ymin, ymax = float(np.nanmin(y_all)), float(np.nanmax(y_all))

    span = ymax - ymin
    if span == 0:
        span = abs(ymax) if ymax != 0 else 1.0

    margin = 0.20  # 25% padding, you can tune (0.2~0.5)
    plt.ylim(ymin - span * margin, ymax + span * margin)

    plt.xlabel("Date")
    plt.ylabel("Deseasonalized anomaly")
    plt.title("Deseasonalized anomalies (monthly climatology removed, 1996–2000)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=250)
    plt.close()


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = read_data(CSV_PATH)

    # Determine which of the three target variables exist
    targets = ["land_mean_f_rnof", "land_mean_f_rsur", "land_mean_f_etr"]
    cols = [c for c in targets if c in df.columns]

    if len(cols) == 0:
        raise ValueError(
            "None of the expected columns found. Expected one or more of:\n"
            f"{targets}\n"
            f"Found: {list(df.columns)}"
        )

    # (1) monthly + (2) yearly plots
    plot_monthly(df[["date"] + cols], OUT_DIR / "spinup_trend.png")
    plot_yearly(df[["date"] + cols], OUT_DIR / "spinup_yearly.png")

    # (3) deseasonalized anomalies
    anom = compute_deseasonalized_anomaly(df[["date"] + cols], cols)
    anom_cols = [c + "_anom" for c in cols]
    plot_anomalies(anom, anom_cols, OUT_DIR / "spinup_anomaly.png")

    # (4) linear trend slopes
    lines = []
    lines.append("Deseasonalized anomaly linear trend slopes (1996–2000)")
    lines.append("Model: anomaly = a + b*t (t in years since 1996-01)")
    lines.append("Units: same as the original variable per year / per decade")
    lines.append("")

    print("\n" + "=" * 72)
    print("Deseasonalized anomaly linear trend slopes (1996–2000)")
    print("=" * 72)

    for c in cols:
        b_year, b_decade = linear_trend_slope(anom, c + "_anom")
        msg = f"{c}_anom: slope = {b_year:.6e} per year;  {b_decade:.6e} per decade"
        print(msg)
        lines.append(msg)

    print("=" * 72 + "\n")

    # Save slopes to txt for easy copy-paste
    out_txt = OUT_DIR / "spinup_anomaly_trend_slopes.txt"
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[DONE] Saved figures to: {OUT_DIR}")
    print(f"[DONE] Saved slope summary: {out_txt}")


if __name__ == "__main__":
    main()
