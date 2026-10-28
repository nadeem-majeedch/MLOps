"""Reference solution for Lab 10: a service with a contract."""

from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

MODEL_PATH = Path(os.environ.get("MODEL_PATH", "models/model.joblib"))
META_PATH = MODEL_PATH.with_name("meta.json")


class SessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hours: float = Field(ge=0.25, le=16, description="Study hours for the session")
    prior_score: float = Field(ge=0, le=100, description="Most recent assessment, 0-100")
    sleep_hours: float = Field(ge=3, le=12, description="Sleep the night before")


class Prediction(BaseModel):
    prediction: float
    model_version: str


class Readiness(BaseModel):
    status: str
    model_version: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = None
    app.state.meta = {}
    if MODEL_PATH.exists():
        app.state.model = joblib.load(MODEL_PATH)
        meta_path = META_PATH if META_PATH.exists() else Path("models/meta.json")
        app.state.meta = json.loads(meta_path.read_text(encoding="utf-8"))
    yield


app = FastAPI(title="Session Score Service", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    """Liveness: the process can answer. Never touches the model."""
    return {"status": "ok"}


@app.get("/ready", response_model=Readiness, responses={503: {"description": "Model not loaded"}})
def ready() -> Readiness:
    if app.state.model is None:
        raise HTTPException(status_code=503, detail="model artifact not loaded")
    return Readiness(status="ready", model_version=str(app.state.meta.get("version", "unknown")))


@app.get("/model-info")
def model_info() -> dict:
    if not app.state.meta:
        raise HTTPException(status_code=503, detail="model metadata not loaded")
    return app.state.meta


@app.post("/predict", response_model=Prediction, responses={503: {"description": "Model not loaded"}})
def predict(request: SessionRequest) -> Prediction:
    if app.state.model is None:
        raise HTTPException(status_code=503, detail="model artifact not loaded; predictions unavailable")
    features = [[request.hours, request.prior_score, request.sleep_hours]]
    value = float(app.state.model.predict(features)[0])
    return Prediction(prediction=round(value, 2), model_version=str(app.state.meta.get("version", "unknown")))
