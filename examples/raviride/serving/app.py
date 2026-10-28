"""RaviRide ETA service.

One model load at start-up; every request is a validated JSON body; every
response says which model answered.
"""

from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raviride_eta.features import add_features, feature_frame  # noqa: E402

MODEL_URI = os.environ.get("MODEL_URI", "models:/raviride-eta@champion")
FALLBACK_PATH = ROOT / "models" / "model.joblib"
FEATURE_SET = os.environ.get("FEATURE_SET", "full")
ZONES = {"Z01", "Z02", "Z03", "Z04", "Z05", "Z06", "Z07", "Z08"}
WEATHER = {"clear", "cloud", "rain"}

state: dict = {}


class TripRequest(BaseModel):
    """One trip for which the caller wants an ETA."""

    model_config = ConfigDict(extra="forbid")

    requested_at: datetime = Field(
        description="Pickup time, ISO 8601. Used for hour, weekday, and peak features."
    )
    pickup_zone: str = Field(description="One of Z01..Z08")
    dropoff_zone: str = Field(description="One of Z01..Z08")
    distance_km: float = Field(gt=0, le=60, description="Route distance in kilometres, greater than 0")
    passengers: int = Field(ge=1, le=6, description="Number of passengers, 1 to 6")
    traffic_index: float = Field(ge=0, le=1, description="Observed congestion, 0 free-flowing to 1 gridlocked")
    driver_supply: int = Field(ge=1, le=100, description="Available drivers near the pickup zone")
    weather: Literal["clear", "cloud", "rain"] = Field(description="Current conditions")

    @field_validator("pickup_zone", "dropoff_zone")
    @classmethod
    def known_zone(cls, value: str) -> str:
        if value not in ZONES:
            raise ValueError(f"unknown zone {value!r}; expected one of {sorted(ZONES)}")
        return value


class PredictionResponse(BaseModel):
    duration_min: float = Field(description="Predicted trip duration in minutes")
    model_alias: str
    model_version: str


def load_model() -> tuple[object, dict]:
    """Load from a registry alias, or from a file path inside the image.

    A container bakes the artifact and sets MODEL_URI=/app/models/model.joblib,
    so it needs no registry at run time. mlflow is imported lazily for that
    reason: the serving image does not have to carry it.
    """
    if MODEL_URI.startswith("models:/"):
        import mlflow

        mlflow.set_tracking_uri((ROOT / "mlruns").as_uri())
        try:
            model = mlflow.pyfunc.load_model(MODEL_URI)
            client = mlflow.MlflowClient()
            version = client.get_model_version_by_alias("raviride-eta", "champion").version
            return model, {"alias": "champion", "version": str(version), "source": MODEL_URI}
        except Exception as exc:  # noqa: BLE001 - fall back, but say so
            if not FALLBACK_PATH.exists():
                raise RuntimeError(f"could not load {MODEL_URI} and no fallback at {FALLBACK_PATH}: {exc}") from exc
            model = joblib.load(FALLBACK_PATH)
            return model, {"alias": "none", "version": "local-file", "source": str(FALLBACK_PATH)}

    path = Path(MODEL_URI)
    if not path.exists():
        raise RuntimeError(f"MODEL_URI points at {path}, which does not exist")
    return joblib.load(path), {"alias": "none", "version": path.stem, "source": str(path)}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["model"], state["info"] = load_model()
    yield
    state.clear()


app = FastAPI(
    title="RaviRide ETA",
    version="1.0.0",
    description="Predicts trip duration for one trip. See /docs for the interactive schema.",
    lifespan=lifespan,
)


@app.get("/health", tags=["ops"], summary="Liveness: the process is running")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready", tags=["ops"], summary="Readiness: the model is loaded")
def ready() -> dict:
    return {"ready": bool(state.get("model")), "model": state.get("info", {})}


@app.get("/model-info", tags=["ops"], summary="Which model is answering")
def model_info() -> dict:
    info = dict(state.get("info", {}))
    info["feature_set"] = FEATURE_SET
    return info


@app.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(trip: TripRequest, request: Request) -> PredictionResponse:
    frame = add_features(pd.DataFrame([trip.model_dump()]))
    prediction = float(state["model"].predict(feature_frame(frame, FEATURE_SET))[0])
    if not 1.0 <= prediction <= 240.0:
        raise ValueError(f"model produced an implausible duration: {prediction:.2f}")
    return PredictionResponse(
        duration_min=round(prediction, 1),
        model_alias=state["info"]["alias"],
        model_version=state["info"]["version"],
    )
