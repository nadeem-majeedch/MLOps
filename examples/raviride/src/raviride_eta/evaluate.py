"""Stage 4: score the artefact on the held-out period and write metrics.json."""

from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .config import load_params, project_path
from .features import feature_frame


def main() -> int:
    params = load_params()
    set_name = params["features"]["set"]
    model = joblib.load(project_path("models", "model.joblib"))
    test = pd.read_csv(project_path("data", "features", "test.csv"), parse_dates=["requested_at"])

    pred = model.predict(feature_frame(test, set_name))
    truth = test["duration_min"].to_numpy()
    error = np.abs(pred - truth)
    metrics = {
        "overall": {
            "mae": round(float(mean_absolute_error(truth, pred)), 4),
            "rmse": round(float(mean_squared_error(truth, pred) ** 0.5), 4),
            "r2": round(float(r2_score(truth, pred)), 4),
            "p95_abs_error": round(float(np.percentile(error, 95)), 4),
            "test_rows": int(len(test)),
        },
        "slices": {
            "peak": round(float(mean_absolute_error(truth[test["is_peak"] == 1], pred[test["is_peak"] == 1])), 4),
            "off_peak": round(float(mean_absolute_error(truth[test["is_peak"] == 0], pred[test["is_peak"] == 0])), 4),
            "zones": {},
        },
    }
    for zone in sorted(test["pickup_zone"].unique()):
        mask = test["pickup_zone"] == zone
        metrics["slices"]["zones"][zone] = {
            "mae": round(float(mean_absolute_error(truth[mask], pred[mask])), 4),
            "rows": int(mask.sum()),
        }
    metrics["model_sha256"] = json.loads(project_path("models", "run_meta.json").read_text())["model_sha256"]

    project_path("metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(f"test rows: {len(test)}")
    m = metrics["overall"]
    print(f"MAE {m['mae']} min | RMSE {m['rmse']} | R2 {m['r2']} | p95 {m['p95_abs_error']} min")
    print("wrote metrics.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
