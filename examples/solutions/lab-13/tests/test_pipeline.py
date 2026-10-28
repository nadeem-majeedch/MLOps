"""Reference solution for Lab 13: tests that notice an API change."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from packaging.version import Version

import pipeline


def test_data_files_exist():
    assert Path("data/sessions.csv").exists()
    assert Path("data/extra_sessions.csv").exists()


def test_both_extracts_are_loaded():
    frame = pipeline.load()
    assert len(frame) == 600
    assert frame["session_id"].is_unique


def test_summary_is_written():
    frame = pipeline.load()
    summary = pipeline.summarise(frame)
    assert summary["rows"] == 600
    assert 0 < summary["mean_score"] < 100


def test_pandas_is_new_enough_for_the_code():
    # The code calls concat and drop_duplicates; both behave differently before
    # 2.0. This test fails at the source of the problem, not at line 40 of a run.
    assert Version(pd.__version__) >= Version("2.0"), f"pandas {pd.__version__} is too old for this module"


def test_requirements_pin_the_supported_major():
    text = Path("requirements.txt").read_text(encoding="utf-8")
    assert "pandas==2." in text, "requirements.txt must pin pandas to the major the tests exercise"
