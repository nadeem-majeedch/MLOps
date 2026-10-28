"""Three ways to assemble the same request, one of which is correct."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "serving"))

from app import load_model  # noqa: E402

from raviride_eta.features import add_features, feature_columns, feature_frame  # noqa: E402

TRIP = {
    "requested_at": "2026-09-23T18:20:00",
    "pickup_zone": "Z08",
    "dropoff_zone": "Z01",
    "distance_km": 11.4,
    "passengers": 2,
    "traffic_index": 0.72,
    "driver_supply": 41,
    "weather": "clear",
}


def main() -> None:
    model, info = load_model()
    base = add_features(pd.DataFrame([TRIP]))
    base["requested_at"] = pd.to_datetime(base["requested_at"])
    numeric, categorical = feature_columns("full")

    correct = feature_frame(base)
    miles = base.copy()
    miles["distance_km"] = miles["distance_km"] * 0.621
    miles["log_distance"] = np.log(miles["distance_km"].clip(lower=0.1))
    miles_frame = miles[numeric + categorical]
    no_traffic = base.copy()
    no_traffic["traffic_index"] = 0.0
    no_traffic_frame = no_traffic[numeric + categorical]

    print(f"model: {info}")
    rows = (
        ("correct", correct),
        ("distance sent in miles", miles_frame),
        ("traffic_index defaulted to 0", no_traffic_frame),
    )
    for label, frame in rows:
        prediction = float(model.predict(frame)[0])
        print(f"{label:28s} {prediction:6.2f} min")
    print("expected for this trip: 43.00 min (registry champion v2)")


if __name__ == "__main__":
    main()
