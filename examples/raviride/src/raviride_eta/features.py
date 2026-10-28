"""Pure feature transforms and the declared feature sets."""

from __future__ import annotations

import numpy as np
import pandas as pd

PEAK_HOURS = (7, 8, 9, 17, 18, 19)

LEAKY_COLUMNS = {
    "fare_amount": "written by the meter after the trip ends",
    "duration_min": "the target",
}

FEATURE_SETS = {
    "core": {
        "numeric": ["distance_km", "passengers", "log_distance", "traffic_index"],
        "categorical": ["pickup_zone", "weather"],
    },
    "full": {
        "numeric": [
            "distance_km", "passengers", "hour", "day_of_week", "is_weekend",
            "is_peak", "log_distance", "traffic_index", "driver_supply",
        ],
        "categorical": ["pickup_zone", "dropoff_zone", "weather"],
    },
}


def add_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add calendar and distance features. Does not mutate the input."""
    out = frame.copy()
    requested = pd.to_datetime(out["requested_at"])
    out["hour"] = requested.dt.hour
    out["day_of_week"] = requested.dt.dayofweek
    out["is_weekend"] = (out["day_of_week"] >= 5).astype(int)
    out["is_peak"] = out["hour"].isin(PEAK_HOURS).astype(int)
    out["log_distance"] = np.log(out["distance_km"].clip(lower=0.1))
    return out


def feature_columns(name: str = "full") -> tuple[list[str], list[str]]:
    if name not in FEATURE_SETS:
        raise ValueError(f"unknown feature set {name!r}; choose from {sorted(FEATURE_SETS)}")
    spec = FEATURE_SETS[name]
    leaked = sorted(set(spec["numeric"] + spec["categorical"]) & set(LEAKY_COLUMNS))
    if leaked:
        reasons = "; ".join(f"{c}: {LEAKY_COLUMNS[c]}" for c in leaked)
        raise ValueError(f"feature set {name!r} contains leaky columns -- {reasons}")
    return list(spec["numeric"]), list(spec["categorical"])


def feature_frame(frame: pd.DataFrame, name: str = "full") -> pd.DataFrame:
    numeric, categorical = feature_columns(name)
    if "hour" not in frame.columns:
        frame = add_features(frame)
    return frame[numeric + categorical]
