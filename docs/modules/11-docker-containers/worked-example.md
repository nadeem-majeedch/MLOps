# Worked example · The image, and what could be checked without Docker

This page separates three things that are easy to blur: the definition, what was verified on the machine that wrote it, and what only a Docker daemon can confirm.

## The definition

```dockerfile
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MODEL_URI=/app/models/model.joblib

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --home /app app

COPY requirements-serve.txt ./
RUN pip install --no-cache-dir -r requirements-serve.txt

COPY src ./src
COPY serving ./serving
COPY models/model.joblib ./models/model.joblib

RUN chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["uvicorn", "serving.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

The dependency install sits above the source copy so that editing `serving/app.py` does not reinstall pandas. The model is copied last because it changes least often than code but more often than dependencies — and, as the last section shows, it is the part most likely to be stale.

`requirements-serve.txt` pins seven packages:

```text
fastapi==0.115.6
uvicorn==0.32.1
pydantic==2.14.1
pandas==2.2.3
scikit-learn==1.5.2
numpy==2.5.4
joblib==1.4.2
```

MLflow is absent on purpose: this image loads a baked artifact, and the application imports MLflow lazily only when `MODEL_URI` starts with `models:/`.

## What was verified here

The authoring machine has no Docker daemon:

```text
$ docker --version
bash: docker: command not found
```

So the image was not built and no container ran. Two things were checked instead.

**1. The Dockerfile parses and its metadata is what it looks like.** Using `dockerfile-parse` (syntax and instruction structure, not a build):

```text
base: python:3.12-slim-bookworm
cmd: ["uvicorn", "serving.app:app", "--host", "0.0.0.0", "--port", "8000"]
instructions: 14 (FROM, ENV, WORKDIR, RUN, COPY, RUN, COPY, COPY, COPY, RUN, USER, EXPOSE, HEALTHCHECK, CMD)
env: PYTHONDONTWRITEBYTECODE=1, PYTHONUNBUFFERED=1, PIP_NO_CACHE_DIR=1,
     PIP_DISABLE_PIP_VERSION_CHECK=1, MODEL_URI=/app/models/model.joblib
```

This proves the file is well-formed and that the command, environment, and base image are the intended ones. It proves nothing about whether the build succeeds.

**2. The runtime recipe, executed outside Docker.** A clean directory was populated with exactly the files the Dockerfile copies (`src/`, `serving/`, `models/model.joblib`, `requirements-serve.txt`), a fresh virtual environment was created, and the requirements were installed from scratch:

```text
$ python -m venv venv
$ ./venv/Scripts/python -m pip install -r requirements-serve.txt
(success)
$ ./venv/Scripts/python -c "import fastapi, pandas, sklearn, numpy; print(...)"
fastapi 0.115.6 pandas 2.2.3 sklearn 1.5.2 numpy 2.5.4
```

Then the same command the container runs, with the same environment variable:

```text
$ MODEL_URI=/tmp/imagesim/models/model.joblib uvicorn serving.app:app --port 8012
INFO:     Started server process [9140]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8012

$ curl /ready       -> time to {"ready":true}: 4847 ms
$ curl /model-info  -> {"alias":"none","version":"model","source":".../models/model.joblib"}
$ curl /predict     -> {"duration_min":41.2,"model_alias":"none","model_version":"model"}
$ curl /health      -> {"status":"ok"}
```

This is a real verification of dependency resolution, the import path, the lazy-MLflow change, the file-based `MODEL_URI` branch, and the start-up sequence. It is **not** a verification of the base image, layer caching, the non-root user, the health check, or port publishing — all of which depend on Docker.

The same package set occupies **346 MB** in that virtual environment. That is a proxy for the Python portion of the image, not the image size: the base OS and layer overhead are additional, and the real number must be measured with `docker image ls`.

## The finding that matters: the baked model was stale

The fixed trip used throughout Modules 10 and 11 — 11.4 km, Z08 → Z01, 18:20, traffic 0.72 — produced:

| Where the model came from | Prediction |
|---|---|
| Registry alias `@champion` (version 2, 300 trees) | **43.0 min** |
| `models/model.joblib` baked into the image (version 1, 200 trees) | **41.2 min** |

Same code, same request, different answer. The image was built from a local file written by the pipeline, while the registry's champion had moved on. Neither artifact is "wrong"; the image simply contains a snapshot that no longer matches what the registry says is live.

This is the container version of a stale cache, and it is easy to ship because everything looks healthy: the container starts, `/health` returns `ok`, `/predict` returns a plausible number.

Three defences, in increasing strength:

1. **Tag the image with the model version** and record the artifact hash in a label or a manifest file. "Which model is in this image?" becomes a lookup.
2. **Build the image from the promoted artifact**, not from a working-tree file: copy the artifact out of the registry version into the build context as part of the build pipeline.
3. **Check the agreement in CI**: compare the model hash inside the image (or a `/model-info` response from the built container) with the champion's hash, and fail the build when they differ. Module 12 implements the simpler form.

## What still needs Docker

Run these on a machine with Docker, and record the real output. Do not accept the parenthetical expectations as evidence; they are what the definition is designed to produce.

```powershell
# Build (expect a multi-minute first build, fast rebuild after a source-only change)
docker build -t raviride-eta:1.0.0 .

# Inspect (expect a size in the hundreds of MB, and a non-root user)
docker image ls raviride-eta
docker image inspect raviride-eta:1.0.0 --format "{{.Config.User}}"
docker history raviride-eta:1.0.0

# Run (expect the service on localhost:8000)
docker run --rm -d --name eta -p 8000:8000 raviride-eta:1.0.0
docker logs eta
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{...}"

# Non-root, inside the container
docker exec eta id

# Runtime configuration without a rebuild
docker run --rm -e MODEL_URI=/app/models/model.joblib -p 8001:8000 raviride-eta:1.0.0

# Persistence
docker run --rm -v eta-logs:/app/logs -p 8002:8000 raviride-eta:1.0.0
docker volume ls

# Cleanup
docker stop eta
docker rm eta
docker rmi raviride-eta:1.0.0
docker volume rm eta-logs
```

| Check | Verified here | Requires Docker |
|---|---|---|
| Dockerfile parses | Yes | — |
| Requirements resolve from a clean environment | Yes | — |
| Service starts and predicts | Yes (outside Docker) | — |
| Build succeeds | No | Yes |
| Image size and layer cache | No | Yes |
| Runs as non-root | No | Yes (`docker exec id`) |
| Port publishing | No | Yes |
| Named volume persistence | No | Yes |
| Health check transitions to healthy | No | Yes |

## The honest summary

The definition is small, and the parts that usually go wrong are not in the Dockerfile: they are the build context (what gets copied), the artifact (which model is inside), and the runtime configuration (which port, which env, which volume). The verification above covers the third only partially and the second not at all.

A reader who runs the lab with Docker will learn more from the build output than from this page. That is the correct relationship: the page explains what to look for; the daemon provides the evidence.
