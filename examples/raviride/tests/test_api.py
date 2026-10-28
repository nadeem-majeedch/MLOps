"""Contract tests for the ETA service. They use the real champion artifact."""

from __future__ import annotations

import json

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app import app
from raviride_eta.features import add_features, feature_frame

TRIP = {
    "requested_at": "2026-09-23T18:20:00",
    "pickup_zone": "Z08",
    "dropoff_zone": "Z01",
    "distance_km": 11.4,
    "passengers": 2,
    "traffic_index": 0.72,
    "driver_supply": 41,
    "weather": "clear",
}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_ready_reports_model(client):
    body = client.get("/ready").json()
    assert body["ready"] is True
    assert body["model"]["version"] != ""


def test_model_info_names_the_alias(client):
    body = client.get("/model-info").json()
    assert body["alias"] in {"champion", "none"}
    assert "feature_set" in body


def test_valid_prediction(client):
    response = client.post("/predict", json=TRIP)
    assert response.status_code == 200
    body = response.json()
    assert 1 <= body["duration_min"] <= 240
    assert body["model_version"] != ""


def test_prediction_is_deterministic(client):
    first = client.post("/predict", json=TRIP).json()["duration_min"]
    second = client.post("/predict", json=TRIP).json()["duration_min"]
    assert first == second


def test_unknown_zone_is_client_error(client):
    bad = dict(TRIP, pickup_zone="Z99")
    response = client.post("/predict", json=bad)
    assert response.status_code == 422
    assert "unknown zone" in json.dumps(response.json()).lower()


def test_negative_distance_is_rejected(client):
    response = client.post("/predict", json=dict(TRIP, distance_km=-3))
    assert response.status_code == 422
    assert "greater_than" in json.dumps(response.json())


def test_missing_field_is_rejected(client):
    bad = {k: v for k, v in TRIP.items() if k != "distance_km"}
    response = client.post("/predict", json=bad)
    assert response.status_code == 422
    assert "distance_km" in json.dumps(response.json())


def test_extra_field_is_rejected(client):
    response = client.post("/predict", json=dict(TRIP, fare_amount=99))
    assert response.status_code == 422
    assert "extra_forbidden" in response.text or "fare_amount" in response.text


def test_api_matches_training_path(client):
    """The serving path must assemble features exactly as training does.

    Compare against the artifact the app actually loaded: comparing with
    models/model.joblib would compare two different models, not two paths.
    """
    from app import state

    record = pd.DataFrame([TRIP])
    record["requested_at"] = pd.to_datetime(record["requested_at"])
    expected = float(state["model"].predict(feature_frame(add_features(record), "full"))[0])
    served = client.post("/predict", json=TRIP).json()["duration_min"]
    assert served == pytest.approx(expected, abs=0.06)
