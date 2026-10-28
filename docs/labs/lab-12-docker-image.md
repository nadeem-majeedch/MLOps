# Lab 12 · Package the service into an image

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L12 | Intermediate | 3 hours | [11 · Docker and containers](../modules/11-docker-containers/index.md) | Partly: static audit executed; image build requires Docker |

**Starter kit:** [`examples/labs/lab-12-docker-image/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-12-docker-image) — starter files, data generator, and acceptance checker.

## Scenario

The service runs on your machine because your machine has the right Python, the
right packages, a model file at a relative path and a shell where `uvicorn` is on
`PATH`. The deployment target has none of that.

The starter Dockerfile "works": it builds, and it produces a 1.4 GB image running
as root, reinstalling every dependency when one line of Python changes, answering
on `127.0.0.1` inside the container where nothing outside can reach it.

## What you will be able to do

- Write a multi-stage Dockerfile that separates dependency installation from
  code.
- Explain what belongs in `.dockerignore` and why a blanket copy is a defect.
- Make the container non-root, health-checked, and reachable.
- Audit an image definition without Docker installed, and verify with Docker when
  it is.

## Prerequisites and setup

The static part of this lab needs only Python:

```bash
cd examples/labs/lab-12-docker-image
python ../_shared/make_sessions.py --out data/sessions.csv
python make_model.py
python audit_image.py
```

Expected: `4/11 image checks passed` on the starter.

!!! note "Docker is not installed in the authoring environment"
    The image was **not** built during authoring. The Dockerfile audit, the
    Compose file and the application code were executed; `docker build` and the
    container run were not. Part 3 gives the exact procedure and what to record,
    so the lab can be completed honestly on a machine with Docker.

## Your task

Rewrite `Dockerfile` and `.dockerignore` so the audit passes, then build, run and
probe the container if Docker is available.

## Data and starter files

| File | Purpose |
|---|---|
| `Dockerfile` | Deliberately flawed single-stage image |
| `.dockerignore` | Almost empty |
| `compose.yaml` | Builds the service and publishes port 8000 |
| `audit_image.py` | Eleven structural checks, no Docker required |
| `app.py`, `make_model.py`, `requirements.txt` | The service and its pinned dependencies |

## Steps

### 1. Read the audit output

```bash
python audit_image.py
```

Seven failures. Each is a decision, not a style preference: mutable base image,
one stage, dependencies copied with the code, root user, no health check, blanket
copy, and no address for the server to bind.

### 2. Separate the stages

Build dependencies in one stage, copy the virtual environment into the runtime
stage with the code. A Python change then rebuilds only the second stage.

### 3. Pin and order

`python:3.12-slim-bookworm`, not `python:3.12`; `COPY requirements.txt` and
`RUN pip install` before copying the application; explicit `COPY` for each file
the runtime needs.

### 4. Make it a service, not a script

`USER app`, a `HEALTHCHECK` against `/health`, `EXPOSE 8000`, and
`--host 0.0.0.0` in the command. The last one is the difference between a
container that runs and a container that is reachable.

### 5. Fix `.dockerignore`

At minimum: `.git`, `mlruns`, `data`, `__pycache__`, `.venv`. The model file must
stay included — it is part of the runtime artefact.

### 6. Audit again

Expected: `11/11 image checks passed`.

### 7. Build and run, if Docker is available

```bash
docker build -t session-score:local .
docker run --rm -p 8000:8000 session-score:local
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
```

```powershell
docker build -t session-score:local .
docker run --rm -p 8000:8000 session-score:local
Invoke-RestMethod http://127.0.0.1:8000/health
```

Record: build time, image size (`docker image ls session-score`), and the output
of both endpoints. Then change one line in `app.py` and rebuild. The dependency
layer must be cached; record the second build time.

### 8. Prove the environment is external

```bash
docker run --rm -e MODEL_PATH=/app/models/missing.joblib -p 8001:8000 session-score:local
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8001/ready
```

Expect 200 for health and 503 for readiness. No rebuild required, which is the
point of configuration through the environment.

### 9. Run the checker

```bash
python check_lab12.py            # static audit + Compose
python check_lab12.py --build    # also builds, when Docker is installed
```

## Expected output

Starter audit:

```text
  [PASS] base image is pinned -- FROM python:3.12
  [FAIL] build stage is separate from runtime -- 1 FROM instruction(s)
  [FAIL] dependencies install before application code -- requirements COPY at None, app COPY at 2
  [FAIL] container runs as a non-root user -- no USER instruction
  [FAIL] healthcheck is defined -- missing
  [FAIL] no blanket copy of the build context -- COPY . . sends everything not ignored
  [FAIL] build context excludes generated and private files -- .git, mlruns, data, .venv
  [PASS] runtime requirements are pinned -- requirements.txt
  [FAIL] the server binds all interfaces -- CMD [...]
```

Solution audit: `11/11 image checks passed`.

## Acceptance criteria

| # | Criterion | How it is checked |
|---|---|---|
| 1 | Base image pinned to a tag | `FROM` scan |
| 2 | Two stages | `FROM` count |
| 3 | Dependencies before application code | Instruction order |
| 4 | Non-root user | Last `USER` is not root |
| 5 | Health check defined | `HEALTHCHECK` present |
| 6 | No blanket copy | No `COPY . .` |
| 7 | Build context excludes generated files | `.dockerignore` contents |
| 8 | Requirements pinned | `==` on every line |
| 9 | Server binds `0.0.0.0` | `CMD` scan |
| 10 | `EXPOSE` matches the command's port | Parsed comparison |
| 11 | No credentials in `ENV`/`ARG` | Keyword scan |
| 12 | Compose builds, publishes 8000, passes `MODEL_PATH` | YAML parsed |
| 13 | Image builds and answers (Docker only) | `--build` run |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `COPY failed: models/model.joblib` | Artefact not generated | `python make_model.py` before building |
| Container starts, connection refused | Bound to `127.0.0.1` | `--host 0.0.0.0` |
| `/ready` 503 in the container | `MODEL_PATH` points at a missing file | Check the path inside the image: `/app/models/model.joblib` |
| Rebuild reinstalls everything | Code copied before dependencies | Reorder `COPY`/`RUN` |
| `docker build` cannot reach the index | No network | Build once with network, or use a base image with wheels preinstalled |
| Health check never becomes healthy | `start-period` shorter than the model load | Increase `--start-period` |

## Reflection questions

1. Why does copying the code after installing dependencies make rebuilds faster,
   and what breaks that benefit?
2. The image runs as a non-root user. What could now fail that worked before, and
   how would you diagnose it?
3. `.dockerignore` excludes `data`. What would happen if the service needed a
   lookup table from that directory?
4. If you could keep only three of the eleven audit rules, which three prevent the
   most severe failures?

## Optional extension

Add a second Compose service that runs the MLflow tracking server with a named
volume, and have the API receive its tracking URI from the environment. Record
what changes in the image and what does not.

## Cleanup

```bash
docker compose down --rmi local
docker image rm session-score:local
rm -rf models data
```

PowerShell: `Remove-Item models, data -Recurse -Force -ErrorAction SilentlyContinue`.

Without Docker: `rm -rf models data`.

## Checklist

- [ ] The audit reports 11/11
- [ ] The image uses two stages and a pinned base
- [ ] The container runs as a non-root user with a health check
- [ ] `.dockerignore` excludes generated and private files
- [ ] Compose builds and publishes port 8000
- [ ] If Docker was available: build, run, health, readiness and rebuild timing recorded
- [ ] If Docker was not available: the limitation is recorded in my evidence file
