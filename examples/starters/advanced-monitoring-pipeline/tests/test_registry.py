"""The registry's only job that matters: promotion follows policy, not memory."""

from __future__ import annotations

import pytest

from pipeline.registry import Registry

META = {
    "metrics": {"roc_auc": 0.84, "recall": 0.88, "precision": 0.17},
    "model_sha256": "abc123",
    "train_machines": ["M01", "M02"],
    "params": {"seed": 42},
}
POLICY = {"min_roc_auc": 0.75, "min_recall": 0.60, "min_precision": 0.10}


def test_a_model_that_meets_policy_is_promoted(tmp_path):
    registry = Registry(tmp_path)
    entry = registry.register(META, "artifacts/model.joblib", "baseline")
    registry.promote(entry["version"])
    assert registry.champion()["version"] == 1


def test_a_model_below_policy_is_blocked_with_every_reason(tmp_path):
    registry = Registry(tmp_path)
    weak = {"metrics": {"roc_auc": 0.62, "recall": 0.30, "precision": 0.05}}
    ok, reasons = registry.decision(weak, POLICY)
    assert not ok
    assert len(reasons) == 3
    assert any("roc_auc 0.6200" in reason for reason in reasons)


def test_rollback_moves_to_the_previous_version(tmp_path):
    registry = Registry(tmp_path)
    for version in range(2):
        entry = registry.register(META, "artifacts/model.joblib")
        registry.promote(entry["version"])
    assert registry.champion()["version"] == 2
    previous = registry.rollback()
    assert previous["version"] == 1
    assert registry.champion()["version"] == 1


def test_rollback_with_nothing_older_is_refused(tmp_path):
    registry = Registry(tmp_path)
    registry.promote(registry.register(META, "artifacts/model.joblib")["version"])
    with pytest.raises(ValueError, match="oldest"):
        registry.rollback()


def test_promoting_a_version_that_does_not_exist_is_refused(tmp_path):
    registry = Registry(tmp_path)
    registry.register(META, "artifacts/model.joblib")
    with pytest.raises(ValueError, match="does not exist"):
        registry.promote(version=9)


def test_registry_survives_a_reload(tmp_path):
    first = Registry(tmp_path)
    first.promote(first.register(META, "artifacts/model.joblib")["version"])
    again = Registry(tmp_path)
    assert again.champion()["version"] == 1
    assert again.champion()["model_sha256"] == "abc123"
