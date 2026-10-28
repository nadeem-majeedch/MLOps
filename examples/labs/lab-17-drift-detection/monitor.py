"""Lab 17 starter: a weekly report that reports the wrong thing.

    python monitor.py --reference week0 --batches week0 week1 week2 week3 \
                      --json artifacts/monitor.json

It prints the change in the mean of each feature and the week's MAE. Both are
real numbers and neither is a monitoring decision:

* A mean can stay put while the shape of a distribution changes completely.
* MAE needs labels, which arrive late, so it cannot be the only signal.
* Drift is not accuracy loss. One week below has a large shift and no
  regression; another has a regression and no shift.

Implement:

    psi(reference, current, bins=10)   population stability index
    severity(value)                    stable / warn / alert
    decide(feature_alerts, mae_relative) -> "ok" | "investigate" | "retrain"

Thresholds: PSI 0.10 warn, 0.25 alert; relative MAE change 0.15 alert.

Decision rule to implement (and to be able to defend):

    no alerts                      -> ok
    performance alert              -> retrain
    feature alert without one      -> investigate

Report contract:

    {"reference": "week0",
     "batches": [{"batch": "week1", "rows": 220,
                  "features": {"hours": {"psi": 1.23, "severity": "alert"}, ...},
                  "performance": {"mae": 4.5, "baseline_mae": 4.4,
                                  "relative_change": 0.02},
                  "decision": "investigate", "reasons": [str]}],
     "alerts": [str]}
"""

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
    """Population stability index over reference quantile bins."""
    raise NotImplementedError("psi")


def severity(value: float) -> str:
    if np.isnan(value):
        return "unknown"
    if value >= PSI_ALERT:
        return "alert"
    if value >= PSI_WARN:
        return "warn"
    return "stable"


def decide(feature_severities: list[str], relative_change: float) -> tuple[str, list[str]]:
    """Turn signals into an action. Drift alone is not a reason to retrain."""
    raise NotImplementedError("decide")


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

        # A mean comparison, which is not a drift measure.
        for feature in FEATURES:
            print(f"{name} {feature}: mean {reference[feature].mean():.2f} -> {current[feature].mean():.2f}")
        print(f"{name}: mae {errors.mean():.3f} (baseline {baseline_mae:.3f}, relative {relative:+.1%})")

        decision, reasons = decide([row["severity"] for row in features.values()], relative)
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

    report["alerts"] = [f"{row['batch']}: {row['decision']}" for row in report["batches"] if row["decision"] != "ok"]
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
