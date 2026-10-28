# RaviRide ETA · course reference project

The project Modules 04–14 build in stages: a validated trip extract, a DVC
pipeline, a registered model with a champion alias, a FastAPI service, a
container, a CI gate, a scheduler, and a drift monitor.

It is deliberately small (about 900 lines of Python) and runs offline. The data
is synthetic; no real trip or personal record is used.

## Requirements

- Python 3.11 or 3.12
- Git (optional, for the commit tag; the project works without a repository)
- No Docker, cloud account, or paid service for the pipeline, registry, API, or
  tests. Docker is used only by the container module.

## Setup from a clean copy

```bash
cd examples/raviride
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,serve]"
```

PowerShell:

```powershell
cd examples\raviride
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,serve]"
```

`.[dev,serve]` installs the pinned training, tracking, API, and test
dependencies. If you only need the pipeline, `pip install -e .` is enough.

## Generate data and run the pipeline

```bash
python scripts/generate_trips.py --out data/raw/trips.csv
dvc init --no-scm
python run_pipeline.py
```

`--no-scm` is only because this directory is not its own Git repository. In your
own project, `dvc init` is correct.

Expected output (measured on Windows 11, Python 3.12.10, with the pins in
`pyproject.toml`):

```text
wrote 1200 rows -> data/raw/trips.csv
PASS data/raw/trips.csv: 1200 rows, 8 checks
train: 896 rows 2026-09-01 02:56:00 .. 2026-09-21 23:36:00
test:  304 rows 2026-09-22 02:04:00 .. 2026-09-28 23:23:00
trained full model on 896 rows -> model.joblib
summary['exit_code']=0 summary['elapsed_s']=12.66s
```

The pipeline is a four-stage DVC graph: `prepare` → `featurise` → `train` →
`evaluate`. Re-running without changes is a cache hit; change a parameter in
`params.yaml` and only the dependent stages rerun.

## Register and promote a baseline

The API prefers `models:/raviride-eta@champion`. Train and promote one version so
the registry path is exercised:

```bash
python registry/registry.py train baseline --set-json '{}'
python registry/registry.py promote 1
python registry/registry.py show
```

Expected:

```text
baseline: version 1 run <id> MAE 2.7686
champion -> v1 (was vNone)
```

`mlruns/` and `candidates/` are generated and ignored by Git. If you skip this
step, the service falls back to `models/model.joblib`, reports
`"alias": "none"`, and the tests still exercise the API — but they do not
exercise the registry load path. Say which path you tested in your evidence.

## Test

```bash
python -m pytest
```

Expected: `10 passed`. The suite covers health, readiness, model info, a valid
prediction, determinism, unknown zone, negative distance, missing field, extra
field, and serving/training feature equivalence.

## Serve

```bash
uvicorn serving.app:app --host 127.0.0.1 --port 8010
```

```bash
curl http://127.0.0.1:8010/health
curl http://127.0.0.1:8010/ready
curl -X POST http://127.0.0.1:8010/predict \
  -H "Content-Type: application/json" \
  -d '{"requested_at":"2026-09-23T18:20:00","pickup_zone":"Z08","dropoff_zone":"Z01","distance_km":11.4,"passengers":2,"traffic_index":0.72,"driver_supply":41,"weather":"clear"}'
```

Verified responses with the baseline champion:

```json
{"status":"ok"}
{"ready":true,"model":{"alias":"champion","version":"1","source":"models:/raviride-eta@champion"}}
{"duration_min":41.2,"model_alias":"champion","model_version":"1"}
```

An unknown zone returns `422` with a message naming `Z99` and the allowed zones.
Module 10's worked example reports `43.0` for a different registered version
(v2); the difference is the artifact, not the request.

Stop the server with `Ctrl+C`, then confirm `/health` no longer answers.

## What is not verified here

- Docker is not used by the pipeline or tests. The container is audited in
  Module 11; an image build requires Docker.
- A hosted CI run requires a GitHub repository and a push. The workflow is
  linted and its commands are executed locally.
- The scheduler and drift monitor are module exercises; see
  `orchestration/scheduler.py` and `monitoring/run_monitor.py`.

## Cleanup

```bash
rm -rf data/processed data/features models mlruns logs .pipeline .dvc
```

PowerShell:

```powershell
Remove-Item data\processed, data\features, models, mlruns, logs, .pipeline, .dvc -Recurse -Force -ErrorAction SilentlyContinue
```

Keep `data/raw/trips.csv` if you want to rerun without regenerating; delete it
for a true clean-clone test.
