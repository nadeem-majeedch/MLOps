"""Pure feature transforms: same input, same output, no mutation."""

from __future__ import annotations

import pandas as pd

from .config import FEATURES


def add_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    # Hours studied per point of prior score; guards a zero denominator.
    out["study_ratio"] = out["hours"] / out["prior_score"].clip(lower=1)
    return out


def feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame if "study_ratio" in frame.columns else add_features(frame)
    return out[FEATURES]
