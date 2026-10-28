# Troubleshooting · Module 10

## Diagnose in this order

1. **Does it start?** Read the traceback from the lifespan hook before anything else.
2. **Which model?** `/model-info` — alias, version, source. Most "wrong prediction" reports end here.
3. **Is the request valid?** A `422` body names the field and the rule; do not guess.
4. **Is the answer plausible?** Compare against the training path for the same record.
5. **Is it slow or broken?** Latency is a different investigation from correctness; do not mix them.

## Failure table

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: serving` | Wrong working directory | Run from the project root or set `PYTHONPATH` |
| `RuntimeError: could not load models:/...` at start-up | No alias, wrong tracking URI, or MLflow not installed | Check the alias in the registry; use an absolute `file:` URI |
| Start-up hangs | Registry on a network path that is slow or unreachable | Load a local artifact, or add a timeout and a clear error |
| 422 on a request from the app team | Extra field, wrong type, or a date format the schema rejects | Send the `detail` array; it names the field |
| 500 with `implausible duration` | Feature assembly drift, wrong artifact, or genuinely extreme input | Compare one record against the training path |
| All requests slow, first one very slow | Model loaded per request, or no warm-up | Load in the lifespan hook |
| `TestClient` never runs start-up | Client used outside a `with` block | `with TestClient(app) as client:` |
| Port already in use | Previous server still running | Stop the recorded PID; do not silently switch ports |
| `/health` fails but `/predict` works | Health check is doing too much | Make health a constant response |
| Prediction differs between two runs | Nondeterministic model or random preprocessing | Fix the seed; scikit-learn inference is deterministic |
| 413 or connection reset on a large batch | Body size limit at the proxy | Reduce batch size or raise the limit deliberately |

## Case 1: "the API returns a different number from my notebook"

Do not adjust the model. Compare in this order:

```python
# 1. same artifact?
service_version = client.get("/model-info").json()["version"]
# 2. same features?
frame = feature_frame(add_features(pd.DataFrame([record])), "full")
# 3. same prediction?
model.predict(frame)
```

If step 3 matches the notebook and the API differs, the serving path assembles features differently. If step 3 differs from the notebook, the artifact or feature set differs. The two causes have different fixes; guessing wastes an afternoon.

## Case 2: a valid request returns an absurd value

Check, in order:

1. **Unknown category.** `handle_unknown="ignore"` silently produces a zero vector for an unseen zone or weather value. Look at the request's categories against the training vocabulary.
2. **Defaulted field.** A caller omitted or defaulted `traffic_index`; 0.0 means free-flowing and changes the estimate substantially.
3. **Unit drift.** Distance in miles, speed in km/h, duration in seconds. The schema cannot see it.
4. **Wrong feature set.** The service uses `full` while the artifact was trained on `core`; the `ColumnTransformer` will raise, but a hand-built array might not.

The reference experiment is the template: 43.00 correct, 22.64 with miles, 21.13 with defaulted traffic.

## Case 3: tests pass locally, fail in CI

- **Different artifact.** CI has no registry alias, so the app falls back to `models/model.joblib`, which may not exist. Seed the artifact or make the test skip with a reason.
- **Different Python or library version.** Pickle compatibility is real; Module 11 pins it.
- **Port or state leakage.** Module-scoped `TestClient` fixtures can share state between tests; prefer per-test clients unless start-up is expensive.

## Case 4: p99 is much worse than p95

Common causes, in order of likelihood for a small service:

- **Garbage collection** from allocating a large feature frame per request.
- **First request after idle** paying lazy imports or page faults.
- **Logging** that flushes synchronously.
- **A slow client** on one connection, if the client is included in the measurement.

Measure with the client's own timing excluded from server logs, and repeat with a warm-up. A single 40 ms outlier in 200 requests is not a defect; a p99 that grows with request count is.

## Case 5: the model is stale after a promotion

An in-process model is a snapshot. After promoting a new version, a running service keeps serving the old one until it reloads. Confirm with `/model-info`, then restart or call the reload endpoint. If the service "follows the alias", prove it with a test: promote in the test, call the reload, assert the version changed.

## When to stop debugging the model

If the same request produces the same wrong number consistently, the service is behaving as designed and the defect is in the artifact, the features, or the training data. Chasing the HTTP layer further will only add noise. Move the investigation to a single-record comparison and, if that matches, to Module 09's lineage.
