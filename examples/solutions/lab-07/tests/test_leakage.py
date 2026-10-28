"""Reference solution for Lab 07: three tests with three different causes."""

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


def test_no_target_derived_feature(result):
    # `score_band` is a bucket of the target: any model given it is reading
    # the answer sheet, and its error is meaningless.
    leaked = [name for name in result["features"] if "score" in name and name != "prior_score"]
    assert leaked == [], f"target-derived features in use: {leaked}"


def test_students_do_not_cross_the_split(result):
    overlap = set(result["train_groups"]) & set(result["test_groups"])
    assert overlap == set(), f"{len(overlap)} students appear in both splits, e.g. {sorted(overlap)[:3]}"


def test_imputer_is_fitted_on_training_rows_only(result):
    assert result["imputer_fit_rows"] == result["rows_train"], (
        f"imputer saw {result['imputer_fit_rows']} rows but only {result['rows_train']} are training rows"
    )
