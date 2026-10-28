"""Drift and performance monitoring with plain NumPy: PSI and slice errors."""

from __future__ import annotations

import numpy as np
import pandas as pd

PSI_WARN = 0.10
PSI_ALERT = 0.25
MAE_ALERT = 0.15  # relative increase against the reference


def psi(reference: pd.Series, current: pd.Series, bins: int = 10) -> float:
    """Population Stability Index over quantile bins of the reference."""
    ref = pd.to_numeric(reference, errors="coerce").dropna()
    cur = pd.to_numeric(current, errors="coerce").dropna()
    if ref.empty or cur.empty:
        return float("nan")
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    if len(edges) < 2:
        return 0.0
    edges[0], edges[-1] = -np.inf, np.inf
    ref_pct = pd.cut(ref, edges).value_counts(normalize=True).sort_index()
    cur_pct = pd.cut(cur, edges).value_counts(normalize=True).sort_index()
    ref_pct = ref_pct.replace(0, 1e-6)
    cur_pct = cur_pct.replace(0, 1e-6)
    return float(((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)).sum())


def categorical_psi(reference: pd.Series, current: pd.Series) -> float:
    ref = reference.value_counts(normalize=True)
    cur = current.value_counts(normalize=True)
    categories = ref.index.union(cur.index)
    ref = ref.reindex(categories, fill_value=1e-6)
    cur = cur.reindex(categories, fill_value=1e-6)
    return float(((cur - ref) * np.log(cur / ref)).sum())


def severity(value: float) -> str:
    if np.isnan(value):
        return "unknown"
    if value >= PSI_ALERT:
        return "alert"
    if value >= PSI_WARN:
        return "warn"
    return "stable"


def evaluate(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    predictions: np.ndarray,
    baseline_mae: float,
    features: list[str],
) -> dict:
    report: dict = {"features": {}, "performance": {}, "alerts": []}
    for name in features:
        if name not in current or name not in reference:
            continue
        if pd.api.types.is_numeric_dtype(reference[name]):
            value = psi(reference[name], current[name])
        else:
            value = categorical_psi(reference[name].astype(str), current[name].astype(str))
        report["features"][name] = {"psi": round(value, 4), "severity": severity(value)}
        if value >= PSI_ALERT:
            report["alerts"].append(f"drift: {name} psi {value:.3f} >= {PSI_ALERT}")

    truth = current["duration_min"].to_numpy()
    errors = np.abs(predictions - truth)
    mae = float(errors.mean())
    overall = {
        "mae": round(mae, 4),
        "baseline_mae": round(baseline_mae, 4),
        "relative_change": round((mae - baseline_mae) / baseline_mae, 4),
        "rows": int(len(current)),
        "p95_abs_error": round(float(np.percentile(errors, 95)), 4),
    }
    report["performance"]["overall"] = overall
    if overall["relative_change"] >= MAE_ALERT:
        report["alerts"].append(
            f"performance: mae {mae:.3f} is {overall['relative_change']:.1%} "
            f"above baseline {baseline_mae:.3f}"
        )

    zones = {}
    for zone in sorted(current["pickup_zone"].unique()):
        mask = current["pickup_zone"] == zone
        if mask.sum() < 10:
            continue
        zones[zone] = {"mae": round(float(errors[mask].mean()), 3), "rows": int(mask.sum())}
    report["performance"]["zones"] = zones

    if report["alerts"]:
        decision = "retrain_review" if overall["relative_change"] >= MAE_ALERT else "investigate_drift"
    else:
        decision = "no_action"
    report["decision"] = decision
    return report
