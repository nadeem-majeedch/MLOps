"""ETA prediction service.

    uvicorn service.app:app --port 8000
    curl http://127.0.0.1:8000/health

The model is loaded once, during start-up, so a broken artifact fails the
container instead of half the requests. Every request is validated against an
explicit schema; unknown fields are rejected rather than ignored, because a
client that sends `distance` instead of `distance_km` should be told.
"""

from __future__ import annotations

import json
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eta_service.features import add_features, feature_frame  # noqa: E402

ZONES = {f"Z{i:02d}" for i in range(1, 7)}

state: dict = {}


def model_path() -> Path:
    """Read the environment at call time, not import time.

    Tests point MODEL_PATH at a temporary artifact; a module-level constant
    would freeze whatever was set when the test process imported this file.
    """
    return Path(os.environ.get("MODEL_PATH", ROOT / "artifacts" / "model.joblib"))


def meta_path() -> Path:
    return Path(os.environ.get("META_PATH", model_path().parent / "run_meta.json"))


class TripRequest(BaseModel):
    """One trip. Field descriptions appear in /docs and in validation errors."""

    model_config = ConfigDict(extra="forbid")

    requested_at: datetime = Field(
        description="Pickup time, ISO 8601. Hour and weekday are derived from it."
    )
    pickup_zone: str = Field(description="One of Z01..Z06")
    dropoff_zone: str = Field(description="One of Z01..Z06")
    distance_km: float = Field(gt=0, le=60, description="Route distance, greater than 0, up to 60")
    passengers: int = Field(ge=1, le=6, description="Passengers, 1 to 6")
    traffic_index: float = Field(ge=0, le=1, description="0 free-flowing, 1 gridlocked")
    driver_supply: int = Field(ge=1, le=200, description="Available drivers nearby")
    weather: Literal["clear", "cloud", "rain"] = Field(description="Current conditions")

    @field_validator("pickup_zone", "dropoff_zone")
    @classmethod
    def known_zone(cls, value: str) -> str:
        if value not in ZONES:
            raise ValueError(f"unknown zone {value!r}; expected one of {sorted(ZONES)}")
        return value


class Prediction(BaseModel):
    duration_min: float = Field(description="Predicted trip duration in minutes")
    model_file: str
    model_sha256: str | None = None


def load_model() -> tuple[object, dict]:
    path = model_path()
    if not path.exists():
        raise RuntimeError(
            f"no model at {path}. Run `python train.py` before starting the service."
        )
    model = joblib.load(path)
    meta = {}
    if meta_path().exists():
        meta = json.loads(meta_path().read_text(encoding="utf-8"))
    return model, meta


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["model"], state["meta"] = load_model()
    yield
    state.clear()


app = FastAPI(
    title="ETA service",
    version="1.0.0",
    description=(
        "Predicts trip duration for one trip. "
        "This is a teaching service, not a production system: it has no authentication."
    ),
    lifespan=lifespan,
)


@app.get("/health", tags=["ops"], summary="Liveness")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready", tags=["ops"], summary="Readiness: the artifact is loaded")
def ready() -> dict:
    loaded = state.get("model") is not None
    if not loaded:
        raise HTTPException(status_code=503, detail="model not loaded")
    return {"ready": True}


@app.get("/model-info", tags=["ops"], summary="Which artifact is answering")
def model_info() -> dict:
    meta = state.get("meta", {})
    return {
        "model_file": model_path().name,
        "model_sha256": meta.get("model_sha256"),
        "data_sha256": meta.get("data_sha256"),
        "trained_rows": meta.get("train_rows"),
        "features": meta.get("features"),
        "metrics": meta.get("metrics"),
    }


@app.post("/predict", response_model=Prediction, tags=["prediction"])
def predict(trip: TripRequest) -> Prediction:
    frame = add_features(pd.DataFrame([trip.model_dump()]))
    prediction = float(state["model"].predict(feature_frame(frame))[0])

    # A model that returns 900 minutes is not "a bit off"; it is answering a
    # question the inputs do not support. Fail visibly rather than serve it.
    if not 1.0 <= prediction <= 240.0:
        raise HTTPException(
            status_code=500,
            detail=f"implausible prediction {prediction:.1f} min for the given inputs",
        )
    meta = state.get("meta", {})
    return Prediction(
        duration_min=round(prediction, 1),
        model_file=model_path().name,
        model_sha256=meta.get("model_sha256"),
    )
