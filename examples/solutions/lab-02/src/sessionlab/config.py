"""One place for the decisions the old script hid."""

from __future__ import annotations

from dataclasses import dataclass

FEATURES = ["hours", "prior_score", "sleep_hours", "study_ratio"]
TARGET = "score"


@dataclass(frozen=True)
class Settings:
    test_size: float = 0.25
    seed: int = 42
    n_estimators: int = 120
    max_depth: int = 8
