from __future__ import annotations

import pandas as pd

from sessionlab.features import add_features, feature_frame


def test_add_features_does_not_mutate_the_input():
    frame = pd.DataFrame({"hours": [2.0], "prior_score": [50.0]})
    add_features(frame)
    assert "study_ratio" not in frame.columns


def test_study_ratio_is_hours_per_prior_point():
    frame = pd.DataFrame({"hours": [3.0], "prior_score": [60.0]})
    assert add_features(frame)["study_ratio"].iloc[0] == 0.05


def test_zero_prior_score_does_not_divide_by_zero():
    frame = pd.DataFrame({"hours": [4.0], "prior_score": [0.0]})
    value = add_features(frame)["study_ratio"].iloc[0]
    assert value == 4.0


def test_feature_frame_is_idempotent():
    frame = pd.DataFrame({"hours": [2.0, 5.0], "prior_score": [50.0, 80.0], "sleep_hours": [7.0, 6.5]})
    once = feature_frame(frame)
    twice = feature_frame(once)
    pd.testing.assert_frame_equal(once, twice)
