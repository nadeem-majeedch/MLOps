"""Reference solution for Lab 17: measure shape, then decide with two signals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

BATCHES = Path("data/batches")
FEATURES = ["hours", "prior_score", "sleep_hours"]
TARGET = "score"
PSI_WARN = 0.10
PSI_ALERT = 0.25
MAE_ALERT = 0.15


def psi(reference: pd.Series, current: pd.Series, bins: int = 10) -> float:
    ref = pd.to_numeric(reference, errors="coerce").dropna()
    cur = pd.to_numeric(current, errors="coerce").dropna()
    if ref.empty or cur.empty:
        return float("nan")
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    if len(edges) < 2:
        return 0.0
    edges[0], edges[-1] = -np.inf, np.inf
    ref_pct = pd.cut(ref, edges).value_counts(normalize=True).sort_index().replace(0, 1e-6)
    cur_pct = pd.cut(cur, edges).value_counts(normalize=True).sort_index().replace(0, 1e-6)
    return float(((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)).sum())


def severity(value: float) -> str:
    if np.isnan(value):
        return "unknown"
    if value >= PSI_ALERT:
        return "alert"
    if value >= PSI_WARN:
        return "warn"
    return "stable"


def decide(feature_severities: list[str], relative_change: float) -> tuple[str, list[str]]:
    # Performance first: it is the signal that costs money.
    if relative_change >= MAE_ALERT:
        return "retrain", [f"relative mae change {relative_change:+.1%} exceeds {MAE_ALERT:.0%}"]
    if any(value in {"warn", "alert"} for value in feature_severities):
        # Inputs moved but accuracy held. Look before spending a training run.
        return "investigate", ["feature distribution moved, performance within tolerance"]
    return "ok", []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", default="week0")
    parser.add_argument("--batches", nargs="+", default=["week0", "week1", "week2", "week3"])
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    reference = pd.read_csv(BATCHES / f"{args.reference}.csv")
    model = LinearRegression().fit(reference[FEATURES], reference[TARGET])
    baseline_mae = float(np.abs(model.predict(reference[FEATURES]) - reference[TARGET]).mean())

    report = {"reference": args.reference, "batches": [], "alerts": []}
    for name in args.batches:
        current = pd.read_csv(BATCHES / f"{name}.csv")
        errors = np.abs(model.predict(current[FEATURES]) - current[TARGET])
        relative = (float(errors.mean()) - baseline_mae) / baseline_mae

        features = {}
        for feature in FEATURES:
            drift = psi(reference[feature], current[feature])
            features[feature] = {"psi": round(float(drift), 4), "severity": severity(drift)}

        decision, reasons = decide([row["severity"] for row in features.values()], relative)
        drifted = [f for f, row in features.items() if row["severity"] in {"warn", "alert"}]
        if drifted:
            reasons.append("drifted features: " + ", ".join(drifted))

        report["batches"].append({
            "batch": name,
            "rows": int(len(current)),
            "features": features,
            "performance": {"mae": round(float(errors.mean()), 4),
                            "baseline_mae": round(baseline_mae, 4),
                            "relative_change": round(relative, 4)},
            "decision": decision,
            "reasons": reasons,
        })
        print(f"{name}: mae {errors.mean():.3f} ({relative:+.1%}), "
              f"max psi {max(row['psi'] for row in features.values()):.3f} -> {decision}")

    report["alerts"] = [f"{row['batch']}: {row['decision']}" for row in report["batches"] if row["decision"] != "ok"]
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"alerts: {report['alerts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
