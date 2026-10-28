"""The feature contract: order, completeness, purity, and leakage."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from eta_service.features import CATEGORICAL, NUMERIC, add_features, feature_frame

ROW = {
    "requested_at": "2026-03-02T18:10:00",
    "pickup_zone": "Z01",
    "dropoff_zone": "Z04",
    "distance_km": 8.0,
    "passengers": 2,
    "traffic_index": 0.6,
    "driver_supply": 30,
    "weather": "rain",
    "duration_min": 26.0,
}


def test_feature_order_is_fixed_and_complete():
    frame = feature_frame(pd.DataFrame([ROW]))
    assert list(frame.columns) == [*NUMERIC, *CATEGORICAL]


def test_calendar_features_are_derived_from_the_request_time():
    frame = add_features(pd.DataFrame([ROW]))
    assert frame.loc[0, "hour"] == 18
    assert frame.loc[0, "is_peak"] == 1
    assert frame.loc[0, "weekday"] == 0  # 2026-03-02 is a Monday
    assert frame.loc[0, "is_weekend"] == 0


def test_add_features_does_not_mutate_its_input():
    original = pd.DataFrame([ROW])
    add_features(original)
    assert "hour" not in original.columns


def test_target_is_not_a_feature():
    frame = feature_frame(pd.DataFrame([ROW]))
    assert "duration_min" not in frame.columns
    assert "trip_id" not in frame.columns


def test_single_row_and_batch_paths_agree():
    """Serving sends one row; training sends many. The values must match."""
    batch = add_features(pd.DataFrame([ROW, dict(ROW, distance_km=3.0)]))
    single = add_features(pd.DataFrame([ROW]))
    pd.testing.assert_frame_equal(
        feature_frame(batch).iloc[[0]].reset_index(drop=True),
        feature_frame(single).reset_index(drop=True),
    )


def test_unknown_category_survives_to_the_encoder():
    frame = feature_frame(pd.DataFrame([dict(ROW, weather="snow")]))
    assert frame.loc[0, "weather"] == "snow"


def test_zero_distance_does_not_produce_a_nan_or_an_exception():
    """The transform clips so the pipeline stays defined; the schema still rejects 0.

    Clipping is a last line of defence, not permission: `TripRequest.distance_km`
    requires a value greater than zero, and the API test proves the 422.
    """
    bad = pd.DataFrame([dict(ROW, distance_km=0.0)])
    value = add_features(bad).loc[0, "log_distance"]
    assert np.isfinite(value)
    assert value == pytest.approx(np.log(0.1), abs=1e-9)
