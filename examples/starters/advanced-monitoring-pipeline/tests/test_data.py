"""The data contract and the split rule."""

from __future__ import annotations

import pytest

from pipeline.data import DataError, split_by_machine, validate


def test_generated_table_passes(frame):
    validate(frame)


def test_missing_feature_is_named(frame):
    with pytest.raises(DataError, match="missing columns.*vibration_mm_s"):
        validate(frame.drop(columns=["vibration_mm_s"]))


def test_duplicate_reading_id_is_rejected(frame):
    broken = frame.copy()
    broken.loc[1, "reading_id"] = broken.loc[0, "reading_id"]
    with pytest.raises(DataError, match="duplicate reading_id"):
        validate(broken)


def test_null_measurement_is_rejected(frame):
    broken = frame.copy()
    broken.loc[3, "temperature_c"] = None
    with pytest.raises(DataError, match="null values.*temperature_c"):
        validate(broken)


def test_impossible_vibration_is_rejected_with_examples(frame):
    broken = frame.copy()
    broken.loc[2, "vibration_mm_s"] = 41.0
    with pytest.raises(DataError, match="vibration_mm_s: 1 value"):
        validate(broken)


def test_target_must_be_binary(frame):
    broken = frame.copy()
    broken.loc[0, "failure_within_7d"] = 2
    with pytest.raises(DataError, match="only 0 and 1"):
        validate(broken)


def test_unlabelled_batch_skips_target_rules(frame):
    batch = frame.drop(columns=["failure_within_7d"]).head(40)
    validate(batch, require_target=False)


def test_split_keeps_machines_whole_and_both_sides_learnable(frame):
    train, test = split_by_machine(frame, holdout_machines=2)
    assert set(train.machine_id).isdisjoint(set(test.machine_id))
    assert train.failure_within_7d.nunique() == 2
    assert test.failure_within_7d.nunique() == 2
    assert len(train) + len(test) == len(frame)


def test_holding_out_every_machine_is_an_error(frame):
    with pytest.raises(DataError, match="cannot hold out"):
        split_by_machine(frame, holdout_machines=frame.machine_id.nunique())


def test_a_single_class_on_the_test_side_is_an_error(frame):
    """A split that leaves no positives cannot produce a meaningful recall."""
    broken = frame.copy()
    held_out = sorted(broken.machine_id.unique())[-2:]
    broken.loc[broken.machine_id.isin(held_out), "failure_within_7d"] = 0
    with pytest.raises(DataError, match="single class"):
        split_by_machine(broken, holdout_machines=2)
