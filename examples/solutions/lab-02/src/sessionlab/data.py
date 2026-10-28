"""Loading and splitting. No I/O at import time."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from .config import Settings


def load(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"session_id", "section", "hours", "prior_score", "sleep_hours", "score"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{path} is missing columns: {missing}")
    return frame


def split(frame: pd.DataFrame, settings: Settings) -> tuple[pd.DataFrame, pd.DataFrame]:
    return train_test_split(frame, test_size=settings.test_size, random_state=settings.seed)
