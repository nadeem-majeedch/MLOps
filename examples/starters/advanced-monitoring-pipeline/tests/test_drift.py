"""Drift: zero when nothing moved, an alert when something did, and no accuracy claim."""

from __future__ import annotations

import pandas as pd
import pytest

from pipeline.data import FEATURES
from pipeline.drift import classify, population_stability_index, report


def test_identical_distribution_has_zero_psi(frame):
    assert population_stability_index(frame["vibration_mm_s"], frame["vibration_mm_s"]) == pytest.approx(0.0, abs=1e-9)


def test_a_shifted_feature_crosses_the_threshold(frame):
    shifted = frame.copy()
    shifted["vibration_mm_s"] = shifted["vibration_mm_s"] + 1.0
    psi = population_stability_index(frame["vibration_mm_s"], shifted["vibration_mm_s"])
    assert psi > 0.25


def test_report_names_only_the_features_that_moved(frame):
    shifted = frame.copy()
    shifted["vibration_mm_s"] = shifted["vibration_mm_s"] + 1.2
    result = report(frame, shifted, FEATURES, threshold=0.25)
    assert result["verdict"] == "drift"
    assert result["drifted"] == ["vibration_mm_s"]
    assert result["features"]["pressure_bar"]["status"] == "stable"


def test_report_is_stable_when_the_batch_is_a_sample_of_reference(frame, generated_dir):
    batch = pd.read_csv(generated_dir / "current_batch.csv").drop(columns=["failure_within_7d"], errors="ignore")
    # The generated batch *is* shifted; a same-distribution sample is the control.
    control = frame.sample(120, random_state=3).drop(columns=["failure_within_7d"])
    result = report(frame, control, FEATURES, threshold=0.25)
    assert result["verdict"] in {"stable", "watch"}
    assert len(batch) == 80


def test_report_says_out_loud_that_drift_is_not_accuracy(frame):
    result = report(frame, frame.copy(), FEATURES)
    assert "not accuracy" in result["note"]


def test_classification_bands():
    assert classify(0.05, 0.25) == "stable"
    assert classify(0.15, 0.25) == "watch"
    assert classify(0.60, 0.25) == "drift"


def test_empty_series_is_a_clear_error(frame):
    with pytest.raises(ValueError, match="at least one non-null"):
        population_stability_index(frame["vibration_mm_s"], pd.Series([], dtype=float))
