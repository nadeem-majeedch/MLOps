"""Tests for the data rules. Each one names the defect it defends against."""

from __future__ import annotations

import pandas as pd
import pytest

from make_data import COLUMNS, build_rows
from support_risk.data import DataError, feature_frame, load_frame, validate


def frame(rows: int = 120) -> pd.DataFrame:
    return pd.DataFrame(build_rows(rows, seed=7), columns=COLUMNS)


def test_a_generated_frame_passes_validation():
    frame().pipe(validate)


def test_missing_target_column_is_named_in_the_error():
    broken = frame().drop(columns=["needs_support"])
    with pytest.raises(DataError, match="missing columns.*needs_support"):
        validate(broken)


def test_extra_column_is_rejected_rather_than_ignored():
    broken = frame().assign(attendance_rate_pct=99.0)
    with pytest.raises(DataError, match="unexpected columns.*attendance_rate_pct"):
        validate(broken)


def test_duplicate_identifier_is_rejected():
    broken = frame()
    broken.loc[1, "student_ref"] = broken.loc[0, "student_ref"]
    with pytest.raises(DataError, match="duplicate student_ref"):
        validate(broken)


def test_unknown_band_is_rejected():
    broken = frame()
    broken.loc[0, "prior_gpa_band"] = "very-low"
    with pytest.raises(DataError, match="unknown prior_gpa_band"):
        validate(broken)


def test_out_of_range_attendance_is_rejected():
    broken = frame()
    broken.loc[0, "attendance_rate"] = 1.4
    with pytest.raises(DataError, match="outside the documented range.*attendance_rate"):
        validate(broken)


def test_single_class_target_is_rejected():
    broken = frame()
    broken["needs_support"] = 0
    with pytest.raises(DataError, match="single class"):
        validate(broken)


def test_feature_frame_never_contains_the_identifier_or_target():
    features = feature_frame(frame())
    assert "student_ref" not in features.columns
    assert "needs_support" not in features.columns


def test_missing_file_message_tells_you_the_fix(tmp_path):
    with pytest.raises(DataError, match="make_data.py"):
        load_frame(tmp_path / "absent.csv")
