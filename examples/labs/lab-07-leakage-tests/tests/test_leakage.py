"""Lab 07: tests that catch leakage.

Run the suite against the fixed pipeline:

    python -m pytest tests -q

Run it against the frozen production copy by naming the module:

    LAB07_PIPELINE=leaky_pipeline python -m pytest tests -q      # bash
    $env:LAB07_PIPELINE="leaky_pipeline"; python -m pytest tests -q   # PowerShell

The three tests marked TODO must be written so that they fail on
`leaky_pipeline` and pass on the fixed pipeline. A test that fails on both is
not a leak test, it is a broken test.
"""

from __future__ import annotations

import importlib
import os

import pytest

MODULE = os.environ.get("LAB07_PIPELINE", "pipeline")


@pytest.fixture(scope="module")
def result() -> dict:
    return importlib.import_module(MODULE).run(seed=42)


def test_pipeline_reports_a_score(result):
    assert 0 <= result["mae"] <= 20


def test_pipeline_sees_the_expected_columns(result):
    assert {"hours", "prior_score", "sleep_hours"} <= set(result["features"])


def test_no_target_derived_feature(result):
    """TODO 1: no feature may be computed from the target."""
    raise AssertionError("not implemented: assert score_band is not a feature")


def test_students_do_not_cross_the_split(result):
    """TODO 2: the same student must not be in train and test."""
    raise AssertionError("not implemented: compare train_groups and test_groups")


def test_imputer_is_fitted_on_training_rows_only(result):
    """TODO 3: preprocessing must not see the test rows."""
    raise AssertionError("not implemented: compare imputer_fit_rows with rows_train")
