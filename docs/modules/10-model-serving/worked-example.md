# Worked example · Serve the champion, then try to break it

The service is `serving/app.py`, about 150 lines. It loads `models:/raviride-eta@champion` — registry version 2, a 300-tree forest — once at start-up and answers four paths: `/health`, `/ready`, `/model-info`, `/predict`.

## The contract, in one table

| Field | Type | Rule | Why the rule exists |
|---|---|---|---|
| `requested_at` | ISO 8601 datetime | parseable | Hour and peak features depend on it |
| `pickup_zone`, `dropoff_zone` | string | one of `Z01`–`Z08` | An unknown zone hits the encoder's ignore path |
| `distance_km` | float | `0 < d <= 60` | Negative or zero distance is a data defect, not a trip |
| `passengers` | int | 1–6 | Outside the observed range |
| `traffic_index` | float | 0–1 | Observed congestion scale |
| `driver_supply` | int | 1–100 | Observed supply scale |
| `weather` | enum | `clear`, `cloud`, `rain` | Anything else is a caller typo |

`extra="forbid"` is set on the request model, so a caller sending `fare_amount` or `duration_min` gets a `422` rather than a silently ignored field.

## Running it locally

```powershell
python -m pip install "fastapi==0.115.6" "uvicorn==0.32.1" "httpx==0.28.1"
uvicorn serving.app:app --host 127.0.0.1 --port 8010
```

```text
INFO:     Started server process [8832]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8010 (Press CTRL+C to quit)
```

The three lines between process start and the listening message are the lifespan hook: MLflow resolves the alias, loads the artifact, and stores it in `state`. From then on, every request reuses it.

```powershell
curl http://127.0.0.1:8010/health
curl http://127.0.0.1:8010/model-info
```

```json
{"status":"ok"}
{"alias":"champion","version":"2","source":"models:/raviride-eta@champion","feature_set":"full"}
```

```powershell
curl -X POST http://127.0.0.1:8010/predict -H "Content-Type: application/json" -d '{
  "requested_at":"2026-09-23T18:20:00","pickup_zone":"Z08","dropoff_zone":"Z01",
  "distance_km":11.4,"passengers":2,"traffic_index":0.72,"driver_supply":41,"weather":"clear"}'
```

```json
{"duration_min":43.0,"model_alias":"champion","model_version":"2"}
```

Forty-three minutes for 11.4 km in Z08 at the evening peak. It is a plausible number: Z08 is the slowest zone in the dataset, and the test rows with similar distance and hour range from 18.7 to 50.0 minutes.

## What a bad request looks like

Unknown zone:

```text
POST /predict HTTP/1.1" 422 Unprocessable Entity
```

```json
{"detail":[{"type":"value_error","loc":["body","pickup_zone"],
  "msg":"Value error, unknown zone 'Z99'; expected one of ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06', 'Z07', 'Z08']",
  "input":"Z99","ctx":{"error":{}}}]}
```

The body answers three questions without a log search: which field, which value, and which values are allowed. Negative distance produces `"greater_than"` in the error type; an unknown extra field produces `"extra_forbidden"`.

## The ten tests

```text
$ python -m pytest tests/test_api.py -q
10 passed in 2.67s
```

| Test | What it protects |
|---|---|
| `test_health` | The liveness contract |
| `test_ready_reports_model` | Readiness includes a named model |
| `test_model_info_names_the_alias` | Which model is answering |
| `test_valid_prediction` | The happy path stays inside the physical range |
| `test_prediction_is_deterministic` | Two identical requests, two identical answers |
| `test_unknown_zone_is_client_error` | 422 with a domain-specific message |
| `test_negative_distance_is_rejected` | Range constraint reaches the client |
| `test_missing_field_is_rejected` | Missing required field names the field |
| `test_extra_field_is_rejected` | `extra="forbid"` actually forbids |
| `test_api_matches_training_path` | Serving assembly equals training assembly |

The suite runs with `TestClient`, which executes the lifespan hook when used as a context manager — so the tests exercise the real load path, not a stub.

## The contract test that failed for the wrong reason

The first version of `test_api_matches_training_path` compared the API's answer with a prediction from `models/model.joblib`. It failed:

```text
assert 43.0 == 41.165 ± 0.06
```

The tempting diagnosis is train/serve skew. The actual cause was simpler: `models/model.joblib` is the **baseline** (version 1, 200 trees) written by the pipeline, while the service loads **version 2** (300 trees) from the registry. Two different models, compared as if they were two paths through one model.

The fix was to compare against the artifact the service actually loaded:

```python
from app import state
expected = float(state["model"].predict(feature_frame(add_features(record), "full"))[0])
```

The lesson generalises: **before investigating a discrepancy, confirm both sides are the same model.** A contract test that loads its own artifact silently stops testing the service the day the registry moves.

## The skew experiment

With the same artifact, the same trip, assembled three ways:

```text
correct                       43.00 min
distance sent in miles        22.64 min
traffic_index defaulted to 0  21.13 min
```

Both wrong versions are valid JSON, pass every schema rule, and return a plausible number. The miles bug is the classic: the caller's system reports miles, the field is named `distance_km`, and nobody validates the unit because both are positive floats below 60.

Two findings worth recording:

1. **Column order is not a risk in this design.** Sorting the numeric columns alphabetically produced exactly 43.00, because `ColumnTransformer` selects columns by name. A model fed a positional NumPy array would have produced a different prediction. Tool-specific behaviour, not a general law — know which one you rely on.
2. **A missing field is a bigger risk than a wrong one**, because defaults are invisible. `traffic_index = 0.0` looks like free-flowing traffic; here it changed the estimate by 22 minutes.

The single-record test catches assembly drift only if it uses the same artifact and the same code path. It does not catch a caller sending miles — that needs range validation, unit documentation, or distribution monitoring (Module 14).

## Latency

Two hundred sequential requests from one client on the same machine, after a warm-up request:

| Metric | Value |
|---|---|
| p50 | 9.55 ms |
| p95 | 10.27 ms |
| p99 | 30.60 ms |
| Max | 41.69 ms |

Cold start, measured from process launch to `{"ready":true}`: **2.96 s**.

The honest reading: the handler is not the bottleneck at this scale, and the tail is 3× the median, which is worth watching but not yet a problem. Sequential single-client measurement says nothing about throughput under concurrency; that needs a load generator and a stated arrival rate.

## The generated documentation

```text
GET /openapi.json -> ['/health', '/model-info', '/predict', '/ready']
```

`/docs` renders the same information interactively, including the field constraints and the response model. It documents structure, not meaning: nothing in the schema says that `distance_km` must be road distance, that Z08 is the weakest slice, or that a `500` means the model returned an implausible value. Those belong in the README and the model card.

## What the service establishes

| Claim | Evidence |
|---|---|
| The artifact loads without training code | Start-up resolves `@champion` and reports v2 |
| The contract is enforced, not documented | 422 bodies name the field and the allowed values |
| Failures are attributed correctly | Caller errors are 422; implausible model output raises 500 |
| Health and readiness answer different questions | `/health` never touches the model; `/ready` names it |
| Latency is measured, not assumed | p50/p95/p99 over 200 requests |
| Skew is detectable | One record, one artifact, two assemblies, a 20-minute difference |

The service still runs as a single process on a laptop, with the model on local disk. Module 11 makes it portable; Module 14 makes its predictions observable.
