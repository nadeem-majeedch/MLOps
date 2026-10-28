"""The service with the support tickets. Frozen: diagnose it, do not edit it.

Support has forwarded four complaints and one question:

* "One client gets a 500 for a learner with no prior score. It works for
  everyone else." (ticket 4412)
* "We send `score` with the request and the number never changes." (ticket 4418)
* "A negative number of hours is accepted by the app but rejected here."
  (ticket 4421)
* "Calling the endpoint from a browser address bar fails." (ticket 4423)
* Question: "Is a 200 always a correct answer?" (ticket 4430)

Start the service:

    uvicorn service:app --port 8010
"""

from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

MODEL_PATH = Path(os.environ.get("MODEL_PATH", "models/model.joblib"))
META_PATH = MODEL_PATH.with_name("meta.json")


class SessionRequest(BaseModel):
    # Unknown fields are allowed and dropped: ticket 4418.
    model_config = ConfigDict(extra="allow")

    hours: float = Field(ge=0.25, le=16)
    prior_score: float = Field(ge=0, le=100)
    sleep_hours: float = Field(ge=3, le=12)


class Prediction(BaseModel):
    prediction: float
    model_version: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
    app.state.meta = json.loads(META_PATH.read_text(encoding="utf-8")) if META_PATH.exists() else {}
    yield


app = FastAPI(title="Session Score Service", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict", response_model=Prediction)
def predict(request: SessionRequest) -> Prediction:
    # Ticket 4412: prior_score 0 passes validation and divides by zero here.
    pace = request.hours / request.prior_score
    features = [[request.hours, request.prior_score, request.sleep_hours]]
    value = float(app.state.model.predict(features)[0]) * (1 + 0.02 * pace)
    return Prediction(prediction=round(value, 2), model_version=str(app.state.meta.get("version", "unknown")))
