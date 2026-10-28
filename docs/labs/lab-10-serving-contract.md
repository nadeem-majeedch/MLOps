# Lab 10 · Build and test a prediction service

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L10 | Intermediate | 4 hours | [10 · Serving with FastAPI](../modules/10-model-serving/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-10-fastapi-service/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-10-fastapi-service) — starter files, data generator, and acceptance checker.

## Scenario

The dispatch app needs a score per request. Today it calls a script that reads a
CSV and prints a number; it also accepts anything you send it and returns a
number anyway, which is how a client came to believe that sending `score` changed
the prediction.

You will expose the model over HTTP with a contract the app team can rely on:
validated inputs, a documented schema, a meaningful error for each failure, and a
health endpoint that does not depend on the model.

## What you will be able to do

- Serve an artefact loaded once, with readiness separated from liveness.
- Encode domain rules in the request schema, not only types.
- Choose 4xx and 5xx deliberately, and make each message actionable.
- Test a real server over HTTP rather than calling functions directly.

## Prerequisites and setup

```bash
cd examples/labs/lab-10-fastapi-service
python ../_shared/make_sessions.py --out data/sessions.csv
python make_model.py
uvicorn app:app --port 8010
```

Expected: `wrote model 2026.10.1 held-out mae ...`, and the server listening on
`http://127.0.0.1:8010`. Open `/docs` for the generated API documentation.

## Your task

Complete `app.py`: strict schema, the two missing endpoints, and a controlled 503
when the artefact is absent. `check_lab10.py` starts the server twice — once with
a model and once without.

## Data and starter files

| File | Purpose |
|---|---|
| `make_model.py` | Trains and writes `models/model.joblib` plus `meta.json` |
| `app.py` | Starter: `/health` and an unvalidated `/predict` |
| `check_lab10.py` | Starts Uvicorn, exercises HTTP, restarts without an artefact |

The accepted request body:

| Field | Type | Rule |
|---|---|---|
| `hours` | number | 0.25 to 16 |
| `prior_score` | number | 0 to 100 |
| `sleep_hours` | number | 3 to 12 |
| anything else | — | forbidden |

## Steps

### 1. Load once

Use a lifespan handler to load the artefact and its metadata into application
state. Loading per request is the most common performance defect in these
services and it is invisible in a functional test.

### 2. Make the schema strict

Use `Field(ge=..., le=...)` and `ConfigDict(extra="forbid")`. Extra fields must be
rejected, not ignored: silent acceptance is how a caller comes to believe a field
was used.

### 3. Add readiness and metadata

- `GET /ready` → 200 with the loaded version, or 503.
- `GET /model-info` → version, features, held-out MAE.
- `GET /health` → 200 without touching the model.

### 4. Return 503, not 500, when the artefact is missing

The service is alive but cannot predict. That is a capacity/configuration problem,
not a bug in the request, and the status code should say so.

### 5. Start it and send the five bad requests

```bash
curl -X POST http://127.0.0.1:8010/predict -H "content-type: application/json" -d "{\"hours\": 40, \"prior_score\": 62, \"sleep_hours\": 7}"
```

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8010/predict -ContentType application/json -Body '{"hours": 40, "prior_score": 62, "sleep_hours": 7}'
```

Record the status code and the field named in each response. The checker expects
`hours`, `prior_score`, `sleep_hours`, `hours` again (type error) and the extra
field name.

### 6. Run the checker

Stop your server first; the checker starts its own on a free port.

```bash
python check_lab10.py
```

Expected: `24/24 checks passed`.

## Expected output

```text
  [PASS] /ready returns 200 with the loaded version -- got (200, '2026.10.1')
  [PASS] a valid request returns 200 -- status 200
  [PASS] the response carries a prediction and a version -- {'prediction': 84.93, 'model_version': '2026.10.1'}
  [PASS] the same request returns the same answer -- [84.93, 84.93, 84.93]
  [PASS] hours above the range is rejected with 422 -- got 422, expected 422
  [PASS] extra field is rejected with 422 -- {"type": "extra_forbidden", "loc": ["body", "score"], ...}
  [PASS] the service still starts without an artifact -- liveness must not depend on the model
  [PASS] /predict reports 503 without an artifact -- got 503, expected 503
```

The exact prediction depends on your trained artefact; the shape and status codes
do not.

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | `/health` answers without the model | 200 |
| 2 | `/ready` reports the loaded version | 200, version matches `meta.json` |
| 3 | `/model-info` returns metadata | Version, features, MAE |
| 4 | Valid request | 200 with `prediction` and `model_version` |
| 5 | Five malformed requests | 422 each, field named |
| 6 | Missing artefact | Service starts, `/health` 200, `/ready` and `/predict` 503 |
| 7 | `/docs` and `/openapi.json` | Served, three endpoints listed |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Address already in use` | An earlier Uvicorn still running | Stop it, or use another `--port` |
| `/predict` returns 500 on a valid body | Feature order differs from training | Keep `FEATURES` in one place and import it |
| 422 on the valid record | Bounds too tight for your artefact | Compare with `meta.json` features |
| `/ready` 200 but `/predict` 503 | Model loaded but metadata missing | Load both from the same directory |
| Checker times out | Uvicorn not importable in the same interpreter | Run the checker with the venv's Python |

## Reflection questions

1. Why is a 503 more useful to the caller than a 500 when the model is missing?
2. The response includes `model_version`. What does the client do with it, and
   what breaks if it is absent?
3. Which failure in the five malformed requests would the old service have
   returned as a confident 200, and what would the caller have concluded?
4. What would you add to this service before it handles 50 requests per second?

## Optional extension

Add a `/predict-batch` endpoint that accepts up to 100 records and returns one
result per record with its index. Decide what happens when one record is invalid
and defend the choice in two sentences.

## Cleanup

Stop the server with `Ctrl+C`. Then:

```bash
rm -rf models data artifacts
```

PowerShell: `Remove-Item models, data, artifacts -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] The model is loaded once, not per request
- [ ] The schema rejects ranges, types, missing and extra fields
- [ ] Readiness is separate from liveness
- [ ] A missing artefact produces 503, not a traceback
- [ ] `/docs` documents every endpoint
- [ ] `check_lab10.py` reports `ACCEPTED`
