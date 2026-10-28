from __future__ import annotations

import pytest

from sessionlab.scores import mean_score, normalise


def test_mean_score_is_rounded():
    assert mean_score([60, 70, 80]) == 70.0


def test_mean_score_rejects_empty_input():
    with pytest.raises(ValueError):
        mean_score([])


def test_normalise_clamps():
    assert normalise(140) == 1.0
    assert normalise(-5) == 0.0


def test_normalise_rejects_bad_bounds():
    with pytest.raises(ValueError):
        normalise(50, low=100, high=0)
