"""Training: determinism, a threshold chosen before test, and honest metrics."""

from __future__ import annotations

import json

import joblib

from pipeline.data import FEATURES, TARGET, split_by_machine
from pipeline.model import build_model, choose_threshold, evaluate, train


def test_same_seed_same_metrics(frame, tmp_path):
    first = train(frame, tmp_path / "a", seed=42)
    second = train(frame, tmp_path / "b", seed=42)
    assert first["metrics"] == second["metrics"]


def test_threshold_reaches_target_recall_on_training_data(frame):
    train_frame, _ = split_by_machine(frame)
    model = build_model(seed=42).fit(train_frame[FEATURES], train_frame[TARGET])
    threshold = choose_threshold(model, train_frame, target_recall=0.8)
    predicted = (model.predict_proba(train_frame[FEATURES])[:, 1] >= threshold).astype(int)
    recall = predicted[train_frame[TARGET] == 1].mean()
    assert recall >= 0.8 - 1e-9


def test_metrics_beat_a_majority_class_baseline(frame):
    meta = train(frame, output_dir="artifacts/test-run")
    metrics = meta["metrics"]
    assert metrics["roc_auc"] > 0.65
    # A 92%-accurate "never fails" model has zero recall; this one must not.
    assert metrics["recall"] > 0.5


def test_training_writes_artifact_and_provenance(frame, tmp_path):
    meta = train(frame, tmp_path, seed=42)
    assert (tmp_path / "model.joblib").exists()
    assert (tmp_path / "metrics.json").exists()
    saved = json.loads((tmp_path / "metrics.json").read_text(encoding="utf-8"))
    assert saved["roc_auc"] == meta["metrics"]["roc_auc"]
    assert meta["test_machines"]
    assert set(meta["train_machines"]).isdisjoint(meta["test_machines"])

    model = joblib.load(tmp_path / "model.joblib")
    assert model.predict_proba(frame[FEATURES].head(3)).shape == (3, 2)


def test_evaluate_reports_the_confusion_counts(frame):
    _, test_frame = split_by_machine(frame)
    model = build_model(seed=42).fit(frame[FEATURES], frame[TARGET])
    metrics = evaluate(model, test_frame, threshold=0.5)
    assert metrics["true_positives"] + metrics["false_negatives"] == int(test_frame[TARGET].sum())
    assert metrics["threshold"] == 0.5


def test_a_single_class_cannot_produce_a_threshold(frame):
    """The threshold is a quantile of positive scores; with no positives there is none.

    Fitting would already fail, and `validate()` rejects the table before that.
    The guard here is the second line of defence, not the first.
    """
    import pytest

    train_frame, _ = split_by_machine(frame)
    model = build_model(seed=42).fit(train_frame[FEATURES], train_frame[TARGET])
    broken = train_frame.copy()
    broken[TARGET] = 0
    with pytest.raises(ValueError, match="no positive rows"):
        choose_threshold(model, broken, target_recall=0.8)
