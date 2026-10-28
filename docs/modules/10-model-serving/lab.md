# Guided lab · Serve it, then find the bug the schema cannot see

**Time:** 5 hours. **Tools:** Python 3.11/3.12, FastAPI 0.115, Uvicorn, httpx, pytest. CPU only; no cloud account and no GPU.

## Scenario and business problem

The dispatch app needs an ETA for a trip before it is assigned. Today the app calls a spreadsheet export and a colleague's script; the number arrives late and nobody can say which model produced it.

You will expose the champion model as an HTTP service with a contract the app team can rely on, prove it behaves under bad input, and then investigate a class of failure that no schema catches: the same valid request producing a materially different answer because the serving code assembles features differently from training.

### Skills practised

- Loading an artifact once and serving it through a typed endpoint.
- Writing a request schema that encodes domain rules, not just types.
- Choosing 4xx versus 5xx deliberately.
- Separating liveness from readiness.
- Measuring latency as percentiles against a stated budget.
- Detecting and fixing train/serve skew with a single-record equivalence test.

### Prerequisites

Module 09 complete: a registered model with a `champion` alias, or `models/model.joblib` as a fallback. FastAPI and Uvicorn installed in the project environment.

### Input data

No dataset is served. The service takes one trip per request. Use these two fixed records throughout; the second is the one that exposes unit drift.

```json
{"requested_at":"2026-09-23T18:20:00","pickup_zone":"Z08","dropoff_zone":"Z01",
 "distance_km":11.4,"passengers":2,"traffic_index":0.72,"driver_supply":41,"weather":"clear"}
```

```json
{"requested_at":"2026-09-24T09:05:00","pickup_zone":"Z03","dropoff_zone":"Z06",
 "distance_km":9.2,"passengers":1,"traffic_index":0.55,"driver_supply":60,"weather":"rain"}
```

### Directory layout

```text
raviride-eta/
├── serving/
│   ├── app.py
│   └── skew_demo.py
├── tests/
│   └── test_api.py
└── docs/serving-evidence.md
```

## Part 1: load once, answer four questions (45 minutes)

1. Create the app with a lifespan hook that loads the artifact and stores it in module state. Record which URI and version were loaded.
2. Implement:
   - `GET /health` → `{"status":"ok"}`, no model access;
   - `GET /ready` → readiness plus the loaded version;
   - `GET /model-info` → alias, version, feature set;
   - `POST /predict` → response model with the prediction and the model version.
3. Start it:

   ```powershell
   uvicorn serving.app:app --host 127.0.0.1 --port 8010
   ```

   **Checkpoint 1:** `/health` and `/ready` both answer; `/model-info` names the version you expect from Module 09. If it reports `local-file`, the registry alias was not found and the fallback was used — acceptable, but say so in your evidence.

*Recovery:* if start-up fails with `RESOURCE_DOES_NOT_EXIST`, the tracking URI inside the service differs from the one used to register. Use an absolute `file:` URI derived from the project root.

## Part 2: make the contract strict (60 minutes)

4. Add `extra="forbid"`, ranges for distance, passengers, traffic, and supply, and a `Literal` for weather.
5. Add a validator for the zone fields that names the allowed values in the error.
6. Send a valid request, then each of these, and record the status code and the message:

   | Request | Expected |
   |---|---|
   | valid | `200` |
   | `pickup_zone: "Z99"` | `422`, message names the zone |
   | `distance_km: -3` | `422`, range violation |
   | missing `passengers` | `422`, field named |
   | extra `fare_amount` | `422`, extra field forbidden |
   | `weather: "snow"` | `422`, allowed values listed |

   **Checkpoint 2:** all six status codes match, and every message would let a caller fix the request without asking you.

7. Add the output plausibility check: if the model returns a value outside 1–240 minutes, raise rather than clamp.
   **Checkpoint 3:** you can explain to a reviewer why clamping would be worse than a `500`.

## Part 3: tests (60 minutes)

8. Write at least ten tests using `TestClient` inside a `with` block so the lifespan runs.
9. Include the two fixed records, determinism, every failure path from Part 2, and one equivalence test:

   ```python
   expected = state["model"].predict(feature_frame(add_features(record), "full"))[0]
   assert served == pytest.approx(expected, abs=0.06)
   ```

   **Checkpoint 4:** `pytest tests/test_api.py -q` passes, and the suite runs in under five seconds.

*Recovery:* if the equivalence test fails, first check that both sides use the **same artifact**. Comparing the API against `models/model.joblib` compares two models and proves nothing.

## Part 4: break the assembler (45 minutes)

10. Write `serving/skew_demo.py` that predicts the fixed Z08 record three ways: correct, distance converted to miles, and `traffic_index` defaulted to `0.0`.
11. Record the three numbers. Convert the differences into a business statement: how many minutes of error, and in which direction.
12. Comment out the plausibility check and send a request that triggers the miles path through the API. Does it return `200`? Why is that worse than a crash?

    **Checkpoint 5:** you have a table of three predictions and a one-paragraph explanation of why the schema could not catch two of them.

13. Restore the check. Fix the bug by making the unit explicit in the field name and documentation, and add a test that would catch a caller sending an implausible distance for the zone.

## Part 5: measure (45 minutes)

14. State a budget before measuring, for example: "p95 under 50 ms for sequential requests on this machine".
15. Warm up with one request, then measure at least 100 requests with `httpx` and report p50, p95, p99, max.
16. Measure cold start separately: start the server, poll `/ready` every 250 ms, record the time to first ready response.
    **Checkpoint 6:** the budget is written down before the measurement, and both numbers are reported with the method (sequential, one client, warm server).

## Part 6: documentation and evidence (30 minutes)

17. Fetch `/openapi.json` and list the paths. Compare the schema's descriptions with what a caller actually needs to know.
18. Write `docs/serving-evidence.md`: the contract table, the six error cases, the test list, the skew table, the latency table, and three things the OpenAPI document does not say.
19. Stop the server (record how), and confirm the port is free.

## Expected outputs

| Output | Reference value |
|---|---|
| Valid prediction | `{"duration_min":43.0,"model_alias":"champion","model_version":"2"}` |
| Unknown zone | `422`, `unknown zone 'Z99'; expected one of ['Z01', ...]` |
| Tests | 10 passed in ~2.7 s |
| Skew | correct 43.00, miles 22.64, defaulted traffic 21.13 |
| Latency (200 requests) | p50 9.55 ms, p95 10.27 ms, p99 30.60 ms |
| Cold start | 2.96 s to `{"ready":true}` |
| OpenAPI paths | `/health`, `/model-info`, `/predict`, `/ready` |

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Contract | Every field has a type, a rule, and a description; unknown fields are rejected |
| Errors | Caller mistakes return 4xx with a message that names the field and the rule |
| Model loading | One load at start-up; `/model-info` reports the version |
| Tests | At least ten, including an equivalence test against the loaded artifact |
| Skew | A measured difference between correct and drifted assembly, with the mechanism named |
| Latency | Percentiles with a stated method and a budget that predates the measurement |
| Ops | `/health` does not depend on the model; `/ready` does |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: serving` | Running from the wrong directory | Start from the project root, or set `PYTHONPATH` |
| `RuntimeError: could not load ...` at start-up | No champion alias and no fallback file | Promote a version, or train and save the joblib |
| 422 on a request you believe is valid | Extra field, wrong type, or a datetime without a time component | Read `detail[0].loc` and `.msg` |
| Every request is slow | Model loaded inside the handler | Move it into the lifespan hook |
| `TestClient` returns 500 on first request | Using the client outside a `with` block, so lifespan never ran | `with TestClient(app) as client:` |
| Predicted value differs from the notebook | Different artifact, or a feature assembled differently | Compare against `state["model"]` first |
| Port already in use | A previous server is still running | Find the PID and stop it; do not start a second server on another port and forget it |

## Cleanup

- Stop the server process you started; confirm `/health` no longer answers.
- Remove any scratch scripts that duplicate `skew_demo.py`.
- Keep `tests/test_api.py` and the evidence file.
- No containers or external services were started.

## Optional extensions

1. **Model reload.** Add an authenticated `/admin/reload` endpoint that re-resolves the alias without restarting. Test it by promoting a different version and observing the change. Explain the race with in-flight requests.
2. **Request logging.** Log one JSON line per prediction (timestamp, model version, latency, hashed trip id) to a file. Do not log personal data. This becomes the input to Module 14.
3. **Concurrency.** Run 10 concurrent clients with `httpx.AsyncClient` and compare p95 with the sequential number. Explain the difference using worker count and the GIL.
