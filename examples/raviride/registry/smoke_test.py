"""Post-promotion smoke test: load the champion alias and check a known trip.

Run after every promotion. Exit 0 means the alias resolves and the prediction is
inside the tolerance recorded from the accepted model.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import mlflow
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raviride_eta.features import add_features, feature_frame  # noqa: E402

MODEL_URI = "models:/raviride-eta@champion"
EXPECTED_MIN = 25.0
EXPECTED_MAX = 50.0
TRIP = {
    "requested_at": "2026-09-23 18:20:00",
    "pickup_zone": "Z08",
    "dropoff_zone": "Z01",
    "distance_km": 11.4,
    "passengers": 2,
    "traffic_index": 0.72,
    "driver_supply": 41,
    "weather": "clear",
}


def main() -> int:
    mlflow.set_tracking_uri((ROOT / "mlruns").as_uri())
    model = mlflow.pyfunc.load_model(MODEL_URI)
    frame = add_features(pd.DataFrame([TRIP]))
    prediction = float(model.predict(feature_frame(frame))[0])
    version = mlflow.MlflowClient().get_model_version_by_alias("raviride-eta", "champion").version
    status = "PASS" if EXPECTED_MIN <= prediction <= EXPECTED_MAX else "FAIL"
    print(f"{status} champion v{version}: predicted {prediction:.2f} min "
          f"(expected {EXPECTED_MIN:.0f}-{EXPECTED_MAX:.0f} for an 11.4 km Z08->Z01 trip at 18:20)")
    print(json.dumps({"version": version, "prediction": round(prediction, 3), "status": status}))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
