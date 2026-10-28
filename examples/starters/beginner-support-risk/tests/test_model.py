"""Tests for training. The claim being tested is reproducibility, not accuracy."""

from __future__ import annotations

import json

import joblib
import pandas as pd

from make_data import COLUMNS, build_rows
from support_risk import feature_frame, split, train
from support_risk.data import TARGET


def frame(rows: int = 200) -> pd.DataFrame:
    return pd.DataFrame(build_rows(rows, seed=7), columns=COLUMNS)


def test_split_is_stratified_and_disjoint():
    train_frame, test_frame = split(frame(), test_size=0.25, seed=42)
    assert len(train_frame) + len(test_frame) == 200
    # The positive rate must survive the split; that is what stratified means.
    assert abs(train_frame[TARGET].mean() - test_frame[TARGET].mean()) < 0.06
    overlap = set(train_frame.student_ref) & set(test_frame.student_ref)
    assert overlap == set()


def test_same_seed_produces_the_same_metrics():
    first = train(frame(), output_dir="artifacts/seed-a", seed=42)
    second = train(frame(), output_dir="artifacts/seed-b", seed=42)
    assert first["metrics"] == second["metrics"]


def test_metrics_beat_a_constant_predictor():
    """A real signal exists: ROC AUC must clear 0.5 by a clear margin."""
    metrics = train(frame(), output_dir="artifacts/floor")["metrics"]
    assert metrics["roc_auc"] > 0.65


def test_training_writes_an_artifact_and_its_metadata(tmp_path):
    meta = train(frame(), output_dir=tmp_path, kind="logistic", seed=42)
    assert (tmp_path / "model.joblib").exists()
    saved = json.loads((tmp_path / "run_meta.json").read_text(encoding="utf-8"))
    assert saved["metrics"]["roc_auc"] == meta["metrics"]["roc_auc"]
    assert saved["features"]["categorical"] == ["term", "prior_gpa_band"]

    model = joblib.load(tmp_path / "model.joblib")
    sample = feature_frame(frame().head(2))
    assert model.predict_proba(sample).shape == (2, 2)
