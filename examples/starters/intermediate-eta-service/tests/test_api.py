"""API contract tests. Every rejection test names the client mistake it models."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from eta_service.features import add_features, feature_frame

TRIP = {
    "requested_at": "2026-03-02T18:10:00",
    "pickup_zone": "Z01",
    "dropoff_zone": "Z04",
    "distance_km": 8.0,
    "passengers": 2,
    "traffic_index": 0.6,
    "driver_supply": 30,
    "weather": "rain",
}


def test_health_is_independent_of_the_model(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_ready_requires_a_loaded_model(client):
    assert client.get("/ready").json() == {"ready": True}


def test_model_info_exposes_provenance(client):
    body = client.get("/model-info").json()
    assert body["model_sha256"]
    assert body["features"]["numeric"]
    assert body["metrics"]["mae"] > 0


def test_valid_request_returns_a_plausible_prediction(client):
    response = client.post("/predict", json=TRIP)
    assert response.status_code == 200
    body = response.json()
    assert 1 <= body["duration_min"] <= 240
    assert body["model_sha256"]


def test_repeated_requests_are_identical(client):
    first = client.post("/predict", json=TRIP).json()
    second = client.post("/predict", json=TRIP).json()
    assert first == second


@pytest.mark.parametrize(
    "field,value",
    [
        ("distance_km", 0),
        ("passengers", 9),
        ("traffic_index", 1.4),
        ("weather", "snow"),
        ("pickup_zone", "Z99"),
        ("requested_at", "yesterday afternoon"),
    ],
)
def test_invalid_field_is_a_422_with_the_field_named(client, field, value):
    response = client.post("/predict", json=dict(TRIP, **{field: value}))
    assert response.status_code == 422
    assert field in response.text


def test_missing_field_is_rejected(client):
    body = {k: v for k, v in TRIP.items() if k != "distance_km"}
    response = client.post("/predict", json=body)
    assert response.status_code == 422
    assert "distance_km" in response.text


def test_unknown_field_is_rejected_not_ignored(client):
    """A caller sending `distance` believes it predicted something. Say no."""
    response = client.post("/predict", json=dict(TRIP, distance=8.0))
    assert response.status_code == 422
    assert "extra_forbidden" in response.text or "distance" in response.text


def test_non_json_body_is_rejected(client):
    response = client.post(
        "/predict", content="distance_km=8", headers={"content-type": "text/plain"}
    )
    assert response.status_code == 422


def test_service_and_training_paths_agree(client, model_dir):
    """The contract test: same row, two code paths, one answer."""
    import joblib

    model = joblib.load(model_dir / "model.joblib")
    record = add_features(pd.DataFrame([TRIP]))
    expected = float(model.predict(feature_frame(record))[0])
    served = client.post("/predict", json=TRIP).json()["duration_min"]
    assert served == pytest.approx(expected, abs=0.06)


def test_openapi_schema_documents_the_contract(client):
    schema = client.get("/openapi.json").json()
    assert "/predict" in schema["paths"]
    props = schema["components"]["schemas"]["TripRequest"]["properties"]
    assert {"distance_km", "pickup_zone", "weather"} <= set(props)
    assert json.dumps(schema).count("One of Z01..Z06") >= 1
