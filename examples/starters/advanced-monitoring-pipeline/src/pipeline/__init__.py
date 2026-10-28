"""Advanced starter: validated training, a gated registry, and drift monitoring."""

from .data import FEATURES, GROUP, TARGET, DataError, load, split_by_machine, validate
from .drift import population_stability_index, report
from .model import build_model, evaluate, train
from .registry import Registry

__all__ = [
    "FEATURES", "GROUP", "TARGET", "DataError", "load", "split_by_machine",
    "validate", "population_stability_index", "report", "build_model", "evaluate",
    "train", "Registry",
]
