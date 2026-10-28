# Intermediate starter — ETA model behind a validated API

A trained model, its metadata, a FastAPI service, contract tests, and a
Dockerfile. This is the smallest system that another application could actually
call.

| | |
|---|---|
| **Level** | Intermediate |
| **Task** | Regression (trip duration in minutes) |
| **Data** | Synthetic, generated locally |
| **Time to run** | About two minutes |
| **Needs** | Python 3.11+; Docker optional |

---

## What it demonstrates

- **One feature path** imported by both training and serving. The contract test
  compares the two paths on the same row.
- **An artifact plus metadata**: hash of the data, hash of the model, feature
  order, versions, metrics. The service reports them at `/model-info`.
- **A schema at the boundary**: unknown fields rejected, zones checked against a
  known set, ranges enforced, and a plain-language message for each.
- **Fail-fast start-up**: a missing artifact stops the process instead of
  answering half the requests with 500s.
- **A metric ceiling** enforced by `train.py`'s exit code, ready for CI.

It deliberately omits a registry, monitoring, CI, and a model card. The advanced
starter adds the first two; the course labs add the rest.

---

## Layout

```text
intermediate-eta-service/
├── config.yaml
├── make_data.py                 # deterministic trip generator
├── train.py                     # entry point; exits non-zero above max_mae
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── pytest.ini
├── data/                        # generated
├── artifacts/                   # generated: model.joblib, metrics.json, run_meta.json
├── src/eta_service/
│   ├── __init__.py
│   ├── features.py              # add_features, feature_frame, column order
│   └── train.py                 # build_pipeline, train, hashes
├── service/app.py               # FastAPI application
└── tests/
    ├── conftest.py              # data + throwaway model + client
    ├── test_features.py
    └── test_api.py
```

---

## Run it

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python make_data.py
python train.py
python -m pytest
```

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

python make_data.py
python train.py
python -m pytest
```

### Expected output

```text
$ python make_data.py
wrote data/trips.csv  360 rows

$ python train.py
trained on   270 rows
MAE          2.182 min
baseline MAE 13.602 min
RMSE         2.709 min
artifact     .../artifacts/model.joblib
data sha256  4afafc1cd932f8ef...
PASS: MAE 2.182 <= ceiling 3.500

$ python -m pytest
23 passed
```

### Start the service

```bash
python -m uvicorn service.app:app --port 8000
```

Then, in a second terminal:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
curl -X POST http://127.0.0.1:8000/predict \
  -H "content-type: application/json" \
  -d '{"requested_at":"2026-03-02T18:10:00","pickup_zone":"Z01","dropoff_zone":"Z04",
       "distance_km":8.0,"passengers":2,"traffic_index":0.6,"driver_supply":30,"weather":"rain"}'
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health

$body = @{
  requested_at = "2026-03-02T18:10:00"; pickup_zone = "Z01"; dropoff_zone = "Z04"
  distance_km = 8.0; passengers = 2; traffic_index = 0.6; driver_supply = 30; weather = "rain"
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/predict -ContentType "application/json" -Body $body
```

Observed against the running service:

```text
health=200
{"ready":true}
{"duration_min":26.5,"model_file":"model.joblib","model_sha256":"f2e87e13..."}
bad-payload=422         # pickup_zone "Z99"
```

Open <http://127.0.0.1:8000/docs> for the generated schema. Stop the server with
++ctrl+c++.

---

## Docker

The image pins the base, installs dependencies as a separate layer, runs as an
unprivileged user, and bakes the artifact in:

```bash
docker build -t eta-service:0.1 .
docker run --rm -p 8000:8000 eta-service:0.1
curl -s http://127.0.0.1:8000/health
docker image ls eta-service
```

```powershell
docker build -t eta-service:0.1 .
docker run --rm -p 8000:8000 eta-service:0.1
Invoke-RestMethod http://127.0.0.1:8000/health
docker image ls eta-service
```

!!! warning "Not built in the authoring environment"
    Docker was not installed on the machine where this template was written, so
    the image build and run were **not** executed. What was verified: the
    application starts and answers over HTTP, the tests pass, the Dockerfile's
    paths match the copied tree, and `.dockerignore` excludes the tests, data,
    and virtual environment. Build it yourself and report what you see rather
    than treating the commands above as tested.

A reasonable first check after `docker run`: `/health` returns 200, `/model-info`
reports the same `model_sha256` as your local `artifacts/run_meta.json`, and a
bad payload returns 422 with the field named.

---

## Read the code in this order

1. `src/eta_service/features.py` — the feature contract, and why order matters.
2. `src/eta_service/train.py` — what goes into `run_meta.json`.
3. `service/app.py` — the request schema and the plausibility guard.
4. `tests/test_api.py` — especially `test_service_and_training_paths_agree`.
5. `Dockerfile` — layer order, non-root user, health check.

---

## Exercises

1. **Add a field to the request** (`passenger_count` is a common alias). Update
   the schema, the feature code, and the tests. Which test catches you if you
   forget one of the three?
2. **Break the contract deliberately.** Change `feature_frame()` to sort the
   columns alphabetically. Run the tests. The predictions still come back in
   range; explain why the contract test fails and a smoke test would not.
3. **Serve an old artifact.** Train with `n_estimators: 5`, keep `metrics.json`,
   and start the service. Does anything stop you? Add a start-up check that
   refuses an artifact whose `mae` exceeds the config ceiling.
4. **Add a `/batch` endpoint** accepting a list of up to 100 trips and returning
   a list of predictions. What is the right status code when one item is invalid,
   and why is rejecting the whole batch usually better than a partial response?
5. **Measure start-up time** with `time` (bash) or `Measure-Command` (PowerShell),
   then compare a container start. What dominates?

---

## Common problems

| Symptom | Cause | Fix |
|---|---|---|
| `RuntimeError: no model at ...` on start-up | Artifact not trained | `python train.py` |
| 422 on a payload that looks right | Extra field, or a zone outside `Z01`–`Z06` | Read the `loc` in the response; it names the field |
| `Address already in use` | Another server holds port 8000 | `--port 8010` |
| Tests fail at import with `ModuleNotFoundError: service` | Running pytest from the parent directory | `cd` here; `pytest.ini` sets `pythonpath` |
| Predictions differ from the README by ~1 min | Different data seed, or a different scikit-learn version | Compare `data_sha256` and `versions` in `run_meta.json` |
| Docker build fails at `COPY artifacts/` | Artifact excluded or never trained | Train first; check `.dockerignore` does not exclude `artifacts/` |

---

## Cleanup

```bash
# stop the server first with Ctrl+C
rm -rf data artifacts .pytest_cache .venv
docker image rm eta-service:0.1 2>/dev/null || true
```

```powershell
Remove-Item data, artifacts, .pytest_cache -Recurse -Force -ErrorAction SilentlyContinue
docker image rm eta-service:0.1
```

---

## Where this sits in the course

| Before this | This starter | Next |
|---|---|---|
| [Beginner starter](../beginner-support-risk/README.md) | A model another system can call | [Advanced starter](../advanced-monitoring-pipeline/README.md) |
| [Module 10 · Serving](../../../docs/modules/10-model-serving/index.md) | The serving contract in full | [Lab 11 · Request triage](../../../docs/labs/lab-11-request-triage.md) |
| [Lab 10 · Serving contract](../../../docs/labs/lab-10-serving-contract.md) | The same idea, with a diagnosis task | [Lab 12 · Container image](../../../docs/labs/lab-12-docker-image.md) |
