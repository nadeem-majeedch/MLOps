# Concepts · Writing the environment down

## 1. The problem containers solve, stated precisely

A Python service depends on things that are not in its source tree:

- the interpreter version and build (3.12.10 versus 3.12.4 behave differently in edge cases);
- the installed packages and their transitive dependencies;
- system libraries that wheels link against;
- environment variables and file paths that exist on one machine;
- the model artifact itself.

`requirements.txt` pins some of this. It does not pin the interpreter, the system libraries, or the paths. A **container image** is a filesystem plus a start command: everything the process needs, defined once, built the same way everywhere.

The useful definition is not "a lightweight VM". A container is a process (or a few) isolated by the kernel, running from an image. The image is the portable part.

## 2. Image, container, tag, digest

| Term | Meaning |
|---|---|
| **Image** | An immutable, layered filesystem plus metadata (command, env, ports) |
| **Container** | A running instance of an image, with its own writable layer |
| **Tag** | A human-readable pointer, `raviride-eta:1.0.0` |
| **Digest** | A content hash, `sha256:...`, identifying exact bytes |
| **Registry** | Where images are stored and pulled from |

Tags are mutable. `raviride-eta:latest` today and next month can be different images, which is why production deployments should record the **digest**, not just the tag. The tag is for humans; the digest is for reproducibility.

A container's writable layer disappears when the container is removed. Anything that must survive belongs in a volume or outside the container entirely.

## 3. Layers and the build cache

Every `RUN`, `COPY`, and `ADD` creates a layer. Docker caches each layer keyed by the instruction and the content it touches. When one layer changes, that layer and everything after it are rebuilt.

This is why instruction order is a design decision:

```dockerfile
COPY requirements-serve.txt ./
RUN pip install --no-cache-dir -r requirements-serve.txt
COPY src ./src
COPY serving ./serving
```

Editing `serving/app.py` invalidates the `COPY serving` layer and the two after it, but not the dependency install. Reverse the order — copy the source first — and every code change reinstalls every package.

Two rules follow:

1. **Least volatile first.** Base image, system packages, Python dependencies, then application code, then the model.
2. **One `RUN` per logical unit.** Installing packages plus cleaning caches in the same `RUN` keeps the cleanup in the same layer; cleaning in a later layer removes nothing from the image size.

## 4. The Dockerfile, instruction by instruction

```dockerfile
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
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

- **`FROM`** chooses the base. `python:3.12-slim-bookworm` is a Debian bookworm image with Python 3.12 and no build tools. `slim` saves hundreds of megabytes; the cost is that packages without wheels cannot compile.
- **`ENV`** sets values visible to the process at runtime and to later build steps. `PYTHONUNBUFFERED=1` is not cosmetic: without it, stdout is block-buffered when not attached to a terminal, and `docker logs` lags behind reality.
- **`WORKDIR`** creates and changes into a directory. All relative `COPY`, `RUN`, and `CMD` paths are relative to it.
- **`RUN`** executes at build time. The user creation is one layer; the install is another.
- **`COPY`** takes files from the **build context**, not from arbitrary host paths.
- **`USER app`** switches to a non-root user for the rest of the build and for the container. Running as root inside a container is not "isolated enough"; it turns a file-write bug into a host-volume permission problem and increases blast radius.
- **`EXPOSE 8000`** documents the intended port. It does not publish it.
- **`HEALTHCHECK`** tells Docker how to test the container. Orchestrators have their own probes; this one is useful locally and for `docker ps`.
- **`CMD`** is the default command. `ENTRYPOINT` is the fixed executable; use `CMD` for a service you may want to override (`docker run image bash`).

`CMD` in JSON array form does not invoke a shell, so environment variables are not expanded. `CMD ["uvicorn", ..., "--port", "$PORT"]` passes the literal string `$PORT`. Use shell form or a small entry script when you need expansion.

## 5. The build context

`docker build .` sends the directory to the daemon — the **build context**. `COPY` can only see files inside it. Two consequences:

- **Size.** A 2 GB `data/` directory makes every build slow even if the Dockerfile never copies it, because the context is transferred and hashed first.
- **Leakage.** Anything in the context can end up in a layer. A `.env` file copied by a broad `COPY . .` is in the image history, even if a later layer deletes it.

`.dockerignore` excludes paths from the context:

```text
.git
.venv
mlruns
data
tests
docs
logs
**/__pycache__
```

The reference project's copied content is small — `src` 74 KB, `serving` 20 KB, the model 4.3 MB — while the excluded `mlruns/` and `data/` directories are orders of magnitude larger and change constantly. Excluding them is both a size decision and a cache decision.

**Do not copy secrets.** Not into the context, not with `COPY`, not with `ARG`. Build arguments are recorded in image history and visible via `docker history`. Runtime secrets belong in the orchestrator's secret store, mounted as files or environment variables at run time.

## 6. Ports, and why `localhost` is a trap

`EXPOSE 8000` is metadata. Reachability comes from publishing at run time:

```powershell
docker run --rm -p 8000:8000 raviride-eta:1.0.0
```

`-p host:container` maps a host port to a container port. Without it, the service is reachable only from inside the container's network namespace.

The second trap is the bind address. A server listening on `127.0.0.1` inside the container is unreachable from the host even with `-p`, because the published port forwards to the container's network interface, not its loopback. Uvicorn must bind `0.0.0.0`:

```text
uvicorn serving.app:app --host 0.0.0.0 --port 8000
```

This is a common first failure: the container starts, logs look healthy, and every request is refused. The app is fine; the socket is on the wrong interface.

## 7. Environment variables: build time, run time, and secrets

Three mechanisms, often confused:

| Mechanism | When it applies | Visible where |
|---|---|---|
| `ARG` | Build only | Image history (`docker history`) |
| `ENV` | Build and run, baked into the image | `docker inspect`, image config |
| `-e` / compose `environment` | Run only | Container config, `docker inspect` |

Use `ENV` for non-secret defaults (`MODEL_URI=/app/models/model.joblib`), `-e` for values that differ per deployment (log level, feature flag), and never either for credentials. A secret in `ENV` is readable by anyone who can inspect the image or the container.

The reference service reads `MODEL_URI` at start-up. That single variable decides whether it loads a baked file or resolves a registry alias — a runtime decision, so changing it does not require a rebuild.

## 8. Logs, and the twelve-factor expectation

A container's filesystem is disposable and its log file is invisible to `docker logs`. The convention is to write to **stdout and stderr** and let the platform collect, rotate, and ship them.

This conflicts with a common habit:

```python
logging.basicConfig(filename="logs/app.log")   # invisible in a container
```

In a container, log to stderr:

```python
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
```

Uvicorn already writes access logs to stderr. `docker logs <container>` shows them; `docker logs -f` follows. If you must keep files, mount a volume and accept that you now own rotation.

`PYTHONUNBUFFERED=1` matters here: buffered output appears in bursts or not at all before a crash, which is exactly when you need it.

## 9. Volumes: what must outlive the container

| Kind | Syntax | Use |
|---|---|---|
| Named volume | `-v eta-logs:/app/logs` | Data Docker manages; survives container removal |
| Bind mount | `-v ${PWD}/logs:/app/logs` | Development, or host-owned files you want to inspect |
| tmpfs | `--tmpfs /tmp` | Scratch space, never persisted |

A named volume is the portable choice for prediction logs or a local cache. A bind mount is convenient on a laptop and fragile in production because it depends on a host path.

Permissions matter once you run as non-root: a host directory owned by your user may not be writable by uid 999 inside the container. Either `chown` the host directory to the container uid, or use a named volume that Docker initialises with the image's ownership.

Read-only mounts (`-v ...:ro`) are a cheap safety measure for model files: the service should never need to write to its artifact.

## 10. Reproducibility: pins, digests, and the word "latest"

An image is reproducible when rebuilding it produces the same behaviour. In practice:

- **Pin the base by tag at least**, ideally by digest: `python:3.12-slim-bookworm@sha256:...`. Tags like `3.12-slim` move when the upstream image is rebuilt; `latest` moves unpredictably.
- **Pin every Python dependency.** `scikit-learn>=1.5` means a different model runtime next month, and possibly a different prediction from the same pickle.
- **Pin the model.** A baked artifact has a hash; record it.
- **Record the image digest** after the build. That is what was deployed, and it is what a rollback should name.

A rebuild months later will still differ if the registry's base digest has changed, which is why the built image is itself an artifact to keep, not a recipe to re-run.

## 11. Image size: where it goes and why it matters

Size affects pull time (cold starts, autoscaling), registry storage, and the attack surface. The reference recipe installs FastAPI, Uvicorn, pandas, scikit-learn, NumPy, and joblib on a slim base. In a fresh virtual environment the same package set occupies about **346 MB** on disk — a proxy for the Python portion of the image, not the image size, which also includes the base OS and layer overhead.

Levers, in order of effect:

1. **Do not install what you do not serve.** The reference image omits MLflow by loading a baked artifact instead of resolving an alias; that is a real trade-off, not a free win.
2. **Use a slim base**, and avoid build tools in the final image.
3. **Multi-stage builds**: compile in one stage, copy only the result into the final image.
4. **Clean caches in the same layer** (`--no-cache-dir`, `rm -rf /root/.cache`).
5. **Exclude tests, docs, and data** via `.dockerignore`.

A smaller image is not automatically better: `distroless` images have no shell, which makes debugging harder. Choose deliberately and write down why.

## 12. The model inside the image

Two designs, both legitimate:

| Design | Build | Runtime dependency | Rollback |
|---|---|---|---|
| **Baked artifact** | Image contains `models/model.joblib` | None beyond the filesystem | Rebuild and redeploy the previous image |
| **Registry at run time** | Image contains only code | Registry must be reachable and the alias resolvable | Move the alias, restart or reload |

The reference image bakes the artifact, which is simpler to run and needs no MLflow in the image. Its cost is visible in a real measurement: the baked artifact was the **baseline** model (prediction 41.2 minutes for the fixed trip), while the registry's champion at the time was version 2 (43.0 minutes). Same code, same request, different model — because the image was built from a file that had not been refreshed from the promoted version.

That is not a bug in Docker; it is a property of snapshots. If you bake, build the image from the promoted artifact and record which version it contains. If you resolve at run time, you must handle the registry being unavailable and the alias moving under a running process.

## 13. What containers do not solve

- **Data drift.** The container is identical; the world is not (Module 14).
- **Model quality.** A reproducible bad model is still bad.
- **Configuration errors.** A wrong `MODEL_URI` fails the same way everywhere, consistently.
- **State.** Anything the service must remember needs a volume, a database, or a queue.
- **Orchestration.** One container is not high availability; Module 13 and 16 deal with scheduling and multiple replicas.

What containers do solve is the class of failure where two people run the same code and get different results because their machines differ. That class is larger than it looks, and it is where most "it worked yesterday" incidents begin.
