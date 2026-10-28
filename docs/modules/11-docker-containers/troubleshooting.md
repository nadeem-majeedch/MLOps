# Troubleshooting · Module 11

## Diagnose in this order

1. **Did the build finish?** A failing `RUN` is a build problem; a container that exits is a runtime problem.
2. **What does the container say?** `docker logs <name>` before anything else.
3. **Is it the network or the app?** `docker exec <name> curl localhost:8000/health` separates the two.
4. **Is the image what you think?** `docker image inspect`, `docker history`, and the model hash.

## Build failures

| Symptom | Cause | Fix |
|---|---|---|
| Build context is hundreds of MB | `.dockerignore` missing or not matching | Add patterns; confirm the reported context size |
| `COPY failed: file not found` | File excluded, or path outside the context | Fix the path; remember `COPY` sees only the context |
| `No matching distribution found` | No wheel for the base image's Python/platform | Pin a version with wheels; avoid Alpine for scientific packages |
| `error: command 'gcc' failed` | Package needs compilation and the slim base has no compiler | Use a multi-stage build with a builder image, or a wheel-only package set |
| `failed to solve: failed to compute cache key` | A `COPY` source does not exist at that point | Check the build order and the `.dockerignore` |
| Build works locally, fails in CI | Different platform or missing build args | Pin `--platform`; make args explicit |

## Runtime failures

| Symptom | Cause | Fix |
|---|---|---|
| Container exits immediately | `CMD` error, missing module, wrong working directory | `docker logs`; then `docker run --rm image python -c "import serving.app"` |
| `exec format error` | Architecture mismatch | Build with `--platform linux/amd64` (or the host's) |
| Host cannot connect | Bound to `127.0.0.1`, or no `-p` | Bind `0.0.0.0`; publish the port |
| Connection refused only from another container | Services are on different networks, or `localhost` used instead of the service name | Put them on one network; use the container name as hostname |
| `permission denied` on a mounted path | uid mismatch between host directory and container user | Named volume, or `chown` to the container uid |
| Health status `unhealthy` | Wrong port/path, or start-up longer than `start-period` | Test inside the container; raise `start-period` |
| App writes to `/app/logs` and crashes | Directory not present or not writable by the non-root user | Create and `chown` it in the image, or mount a writable volume |
| Predictions differ from local | Different artifact or feature code inside the image | Compare model hashes and the image's commit |

## Case 1: the image is much larger than expected

```powershell
docker history --no-trunc raviride-eta:1.0.0
```

Look for:

- a large `RUN pip install` layer (expected; check what was installed);
- a `COPY . .` that brought data, notebooks, or a virtual environment;
- build tools that stayed because cleanup happened in a later layer;
- an unexpected base image tag.

Fixing the third requires cleaning in the same `RUN`:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y build-essential && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
```

Better: use a multi-stage build so the tools never reach the final image.

## Case 2: the container is healthy but predictions are stale

This is the artifact-drift case from the worked example. Check three hashes:

```powershell
(Get-FileHash models/model.joblib -Algorithm SHA256).Hash      # what you built with
docker exec eta sha256sum /app/models/model.joblib             # what is inside
# and the champion's artifact hash from the registry
```

If the image hash differs from the champion's, the image is a valid snapshot of an older model. Rebuild from the promoted artifact, and add a CI check (Module 12) so this cannot ship silently.

## Case 3: logs are empty

- The app logs to a file inside the container, not to stdout.
- `PYTHONUNBUFFERED` is not set and the process died before flushing.
- The container was started with a logging driver that discards output.
- You are looking at a different container with the same name (after `docker rm`, names are reused).

## Case 4: works locally, fails on the server

Compare, in order:

1. **Image digest** on both sides (`docker image inspect --format "{{.Id}}"`).
2. **Platform** (`docker version --format "{{.Server.Arch}}"`).
3. **Environment variables** actually set (`docker exec env`).
4. **Mounted volumes** and their permissions.
5. **Network reachability** to the registry or database.

The first mismatch usually explains the rest.

## When to stop debugging the container

If the same image produces the same wrong prediction on two machines, the container is doing its job and the defect is in the artifact or the data. Move the investigation to Module 09's lineage and Module 14's monitoring; changing the Dockerfile will not help.
