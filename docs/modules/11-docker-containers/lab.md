# Guided lab · Build it, run it, prove what is inside

**Time:** 4 hours. **Tools:** Docker 24+ (Docker Desktop on Windows/macOS, Docker Engine on Linux), the service from Module 10, Git. No cloud registry required; everything is local.

## Scenario and business problem

The ETA service works on the ML engineer's laptop and fails on the deployment host with a scikit-learn version mismatch. The fix that was proposed — "install the same version there too" — has already failed twice, because "there" is now three machines.

You will package the service so the environment is defined once, verify what the container actually is (not what the Dockerfile intends), and record the one thing that is easiest to get wrong: which model is inside the image.

### Skills practised

- Writing a Dockerfile with a cache-friendly layer order.
- Keeping the build context small and free of data and secrets.
- Publishing a port and understanding the bind address.
- Configuring at run time with environment variables.
- Reading logs from stdout and persisting a file in a volume.
- Verifying the non-root user, the health check, and the image contents.

### Prerequisites

- Module 10 complete: `serving/app.py` runs locally and answers `/predict`.
- A model artifact on disk (`models/model.joblib`) — or a registry alias if you keep MLflow in the image.
- Docker installed and running: `docker run --rm hello-world` succeeds.

### Input data

No dataset is needed at run time. The fixed trip from Module 10 is the test input. The model artifact is copied into the image; record its hash.

### Directory layout

```text
raviride-eta/
├── Dockerfile
├── .dockerignore
├── requirements-serve.txt
├── serving/app.py
├── src/raviride_eta/
├── models/model.joblib
└── docs/image-evidence.md
```

## Part 1: the definition (45 minutes)

1. Write `requirements-serve.txt` with pins for FastAPI, Uvicorn, pydantic, pandas, scikit-learn, NumPy, and joblib. Reuse the versions that work in your environment; do not invent pins you have not installed.
2. Write the Dockerfile: slim Python base, `WORKDIR`, non-root user, dependency layer before source, model copied last, `EXPOSE`, `HEALTHCHECK`, `CMD` binding `0.0.0.0`.
3. Write `.dockerignore` excluding at least: `.git`, `.venv`, `mlruns`, `data`, `tests`, `docs`, `logs`, `**/__pycache__`.
   **Checkpoint 1:** `COPY` instructions reference only files that exist and are not excluded. List them explicitly in your evidence file.

*Why the order matters:* dependencies change rarely, code changes often, the model changes on promotion. Put the most volatile thing last.

## Part 2: build and read the output (45 minutes)

4. Build with a version tag:
   ```powershell
   docker build -t raviride-eta:1.0.0 .
   ```
5. Record: total build time, the context size reported by the builder, the final image size (`docker image ls`), and the image ID/digest.
   **Checkpoint 2:** the build succeeds, and your evidence file contains the actual numbers, not estimates.
6. Change one line in `serving/app.py` and rebuild. Record which steps ran again.
   **Checkpoint 3:** the dependency install is cached; the source copy and everything after it rerun. If the install reruns, your `COPY` order is wrong.
7. Demonstrate the context problem: temporarily remove `.dockerignore`, create a 50 MB file under `data/`, and rebuild. Record the context size difference. Restore `.dockerignore` and delete the file.
   **Checkpoint 4:** you can state how many megabytes the context grew and why the Dockerfile did not need that file.

## Part 3: run and exercise (45 minutes)

8. Run detached with a published port and a name:
   ```powershell
   docker run --rm -d --name eta -p 8000:8000 raviride-eta:1.0.0
   ```
9. Check the endpoints with the fixed trip. Record the response, including `model_version`.
10. Read the logs:
    ```powershell
    docker logs eta
    ```
    **Checkpoint 5:** you can see the start-up lines and the access log for your request in `docker logs`, without opening a file inside the container.

11. Confirm the process is not root:
    ```powershell
    docker exec eta id
    ```
    **Checkpoint 6:** the uid is not 0, and the model file is readable by that user.

12. Confirm health:
    ```powershell
    docker inspect --format "{{.State.Health.Status}}" eta
    ```
    **Checkpoint 7:** the status becomes `healthy` after the start period. If it stays `starting` and then turns `unhealthy`, the health check URL or port is wrong.

13. Break the bind address on purpose: rebuild with `--host 127.0.0.1`, run, and observe the connection failure from the host. Restore `0.0.0.0`.
    **Checkpoint 8:** you can explain why the container appears healthy while the host cannot connect.

## Part 4: runtime configuration and persistence (30 minutes)

14. Override an environment variable without rebuilding:
    ```powershell
    docker run --rm -d --name eta-alt -e MODEL_URI=/app/models/model.joblib -p 8001:8000 raviride-eta:1.0.0
    ```
    **Checkpoint 9:** `/model-info` on port 8001 reflects the variable, and no rebuild was needed.

15. Add one line to the service that appends a JSON line to `/app/logs/predictions.jsonl`, then run with a named volume:
    ```powershell
    docker run --rm -d --name eta-logs -v eta-logs:/app/logs -p 8002:8000 raviride-eta:1.0.0
    ```
16. Send a request, remove the container, start a new one with the same volume, and confirm the file is still there.

    **Checkpoint 10:** the file survives container removal. Without the volume, the same procedure loses it — demonstrate that too.

## Part 5: which model is inside (20 minutes)

17. Record the SHA-256 of `models/model.joblib` before the build.
18. From inside the running container, compute the hash of `/app/models/model.joblib` and compare.
19. Ask the registry which version is champion and whether its artifact hash matches. If it does not, you have found artifact drift; write it down as a finding rather than fixing it silently.
    **Checkpoint 11:** your evidence file states the model hash in the image, the champion's hash, and whether they agree.

## Part 6: rebuild, clean up, and write it down (20 minutes)

20. Rebuild from a clean cache at least once (`docker build --no-cache`) and record the time. This is your real build time.
21. Stop and remove the containers, the image, and the volume. Confirm `docker ps -a` and `docker volume ls` are clean for this project.
22. Write `docs/image-evidence.md`: base image and tag, package pins, copied files, image size, build times, run command, health status, non-root uid, model hash comparison, and the one thing you would change before production.

## Expected outputs

| Output | What to record |
|---|---|
| Build | Success, context size, image size, image ID |
| Rebuild after code change | Dependency layer reused; source layers rerun |
| `/predict` | `200`, a plausible duration, a `model_version`/source |
| `docker logs` | Start-up lines plus one access log line per request |
| `docker exec id` | uid ≠ 0 |
| Health | `healthy` |
| Volume | File present after container removal |
| Model hash | Image hash vs champion hash, and whether they agree |

The reference recipe was executed outside Docker on the authoring machine (no daemon available): dependencies installed from the pins, the service started, `/ready` took 4.85 s, and `/predict` returned 41.2 minutes from the baked artifact. Image size, layer caching, and health status were **not** verified there and must come from your build.

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Definition | Pinned base tag, pinned dependencies, non-root user, explicit `CMD` |
| Context | `.dockerignore` excludes data, VCS, environment, and generated state |
| Cache | A source-only change does not reinstall dependencies |
| Runtime | Port published, `0.0.0.0` bind, env override works without rebuild |
| Logs | Visible through `docker logs`, no reliance on a file inside the container |
| Persistence | A volume survives container removal; the same file without one does not |
| Contents | The model hash inside the image is recorded and compared with the champion |
| Cleanup | No stray containers, images, or volumes left behind |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Build sends gigabytes | Missing or ineffective `.dockerignore` | Add the paths; confirm the reported context size |
| `COPY failed: file not found` | File excluded by `.dockerignore`, or wrong path relative to context | Check the pattern; remember `COPY` sees only the context |
| Container exits immediately | `CMD` references a missing module or wrong working directory | `docker logs` shows the traceback; run `docker run --rm image python -c "import serving.app"` |
| Host cannot connect | Server bound to `127.0.0.1`, or `-p` missing | Bind `0.0.0.0`; publish the port |
| `permission denied` writing a mounted directory | Host directory owned by a different uid than the container user | Use a named volume, or `chown` the host directory |
| Health check always unhealthy | Wrong port, wrong path, or the app needs longer than `start-period` | Test the URL with `docker exec`; increase `start-period` |
| `exec format error` | Image built for another CPU architecture | Build with `--platform` matching the host |
| Build fails resolving NumPy/scikit-learn | No wheel for the base image's Python or platform | Pin versions with wheels, or use a different base |
| Image is unexpectedly huge | Build tools or caches left in the final layer | Clean in the same `RUN`; consider multi-stage |

## Cleanup

```powershell
docker stop eta eta-alt eta-logs 2>$null
docker rm eta eta-alt eta-logs 2>$null
docker rmi raviride-eta:1.0.0
docker volume rm eta-logs
docker ps -a
docker volume ls
```

Remove the 50 MB scratch file if you created one. Keep the Dockerfile, `.dockerignore`, `requirements-serve.txt`, and the evidence file in Git.

## Optional extensions

1. **Multi-stage.** Build wheels in a builder stage, copy only the installed packages into a slim runtime stage. Record the size difference and one thing that became harder to debug.
2. **Compose.** Add a `docker-compose.yml` that runs the service with an environment file and a named volume. Explain what Compose adds over `docker run` and what it does not (it is not an orchestrator).
3. **Read-only filesystem.** Run with `--read-only --tmpfs /tmp` and fix whatever breaks. Record what the service actually needed to write, and whether that belongs in a volume.
