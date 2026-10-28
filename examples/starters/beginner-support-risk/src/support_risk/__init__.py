"""Beginner starter: reproducible support-risk classification."""

from .data import CATEGORICAL, NUMERIC, TARGET, DataError, feature_frame, load_frame, split
from .model import build_pipeline, evaluate, train

__all__ = [
    "CATEGORICAL", "NUMERIC", "TARGET", "DataError", "feature_frame",
    "load_frame", "split", "build_pipeline", "evaluate", "train",
]
