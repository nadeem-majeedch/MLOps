"""Lab 13: the tests that were supposed to catch this.

Run them before your first change. Two pass and one fails, which tells you the
problem is in the code path, not in the environment: if a package were missing,
the import at the top of the module would fail instead.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

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
