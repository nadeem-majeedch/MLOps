"""Feature transforms shared by training and serving.

Both paths import these functions rather than reimplementing them. That is the
only structural defence against training/serving skew that costs nothing at run
time: one function, two callers.

Every function here is pure and row-wise. Nothing computes a mean over the batch,
because serving receives one row and a batch statistic would silently differ.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

PEAK_HOURS = (8, 9, 17, 18, 19)

NUMERIC = [
    "distance_km", "passengers", "traffic_index", "driver_supply",
    "hour", "weekday", "is_weekend", "is_peak", "log_distance",
]
CATEGORICAL = ["pickup_zone", "dropoff_zone", "weather"]

TARGET = "duration_min"


def add_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add calendar and distance features. Returns a copy; never mutates input."""
    out = frame.copy()
    requested = pd.to_datetime(out["requested_at"])
    out["hour"] = requested.dt.hour
    out["weekday"] = requested.dt.dayofweek
    out["is_weekend"] = (out["weekday"] >= 5).astype(int)
    out["is_peak"] = out["hour"].isin(PEAK_HOURS).astype(int)
    out["log_distance"] = np.log(out["distance_km"].clip(lower=0.1))
    return out


def feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Return exactly the declared columns, in a fixed order.

    The order is a contract: a model trained on one order and served another
    produces plausible but wrong predictions, with no error to warn you.
    """
    if "hour" not in frame.columns:
        frame = add_features(frame)
    return frame[[*NUMERIC, *CATEGORICAL]].copy()
