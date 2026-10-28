"""Compare incoming batches with the training reference and decide what to do.

Scenarios are generated with the course generator so labels are known. In
production the labels arrive late; the drift metrics do not need them.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raviride_eta.features import add_features, feature_frame  # noqa: E402

spec = importlib.util.spec_from_file_location("gen", ROOT / "scripts" / "generate_trips.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

FEATURES = [
    "distance_km",
    "passengers",
    "traffic_index",
    "driver_supply",
    "weather",
    "pickup_zone",
]
SCENARIOS = {
    "normal": {},
    "zone_shift": {
        "zone_weights": [0.40, 0.25, 0.18, 0.10, 0.03, 0.02, 0.01, 0.01],
    },
    "rainy_peak": {
        "weather_p": [0.15, 0.25, 0.60],
        "traffic_delta": 0.18,
    },
    "storm": {
        "weather_p": [0.05, 0.15, 0.80],
        "traffic_delta": 0.30,
        "distance_scale": 1.15,
    },
}


def main() -> int:
    model = joblib.load(ROOT / "models" / "model.joblib")
    reference = pd.read_csv(ROOT / "data" / "features" / "train.csv", parse_dates=["requested_at"])
    metrics = json.loads((ROOT / "metrics.json").read_text(encoding="utf-8"))
    baseline_mae = metrics["overall"]["mae"]

    reports = ROOT / "monitoring" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    log_path = ROOT / "monitoring" / "predictions.jsonl"
    log_path.write_text("", encoding="utf-8")

    for name, options in SCENARIOS.items():
        batch = gen.generate(300, seed=101, **options)
        featured = add_features(batch)
        predictions = model.predict(feature_frame(featured))

        with log_path.open("a", encoding="utf-8") as handle:
            for row, prediction in zip(featured.itertuples(), predictions, strict=False):
                handle.write(json.dumps({
                    "logged_at": datetime.now(UTC).isoformat(timespec="seconds"),
                    "batch": name,
                    "trip_id": row.trip_id,
                    "prediction": round(float(prediction), 2),
                    "model_version": "1",
                }) + "\n")

        report = drift_report(reference, featured, predictions, baseline_mae)
        report["scenario"] = name
        (reports / f"{name}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print_report(name, report)
    return 0


def drift_report(reference, current, predictions, baseline_mae):
    from drift import evaluate  # local import: script runs from the project root

    return evaluate(reference, current, predictions, baseline_mae, FEATURES)


def print_report(name: str, report: dict) -> None:
    overall = report["performance"]["overall"]
    print(f"\n=== {name} ===")
    print(f"{'feature':<16}{'psi':>8}  severity")
    for feature, values in report["features"].items():
        print(f"{feature:<16}{values['psi']:>8.3f}  {values['severity']}")
    print(
        f"mae {overall['mae']:.3f} vs baseline {overall['baseline_mae']:.3f} "
        f"({overall['relative_change']:+.1%})"
    )
    for alert in report["alerts"]:
        print(f"  ALERT {alert}")
    print(f"decision: {report['decision']}")


if __name__ == "__main__":
    raise SystemExit(main())
