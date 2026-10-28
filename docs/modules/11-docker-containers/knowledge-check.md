# Knowledge check · Module 11

## Questions

**1.** `docker build .` transfers the whole project directory, but the Dockerfile copies only `src/`, `serving/`, and the model. Why does the unused data directory still matter?

**2.** A container's service listens on `127.0.0.1:8000` inside the container, and it was started with `-p 8000:8000`. Requests from the host fail. Why?

**3.** `EXPOSE 8000` is in the Dockerfile. Does that make the port reachable? What does it actually do?

**4.** You put a database password in `ENV` so the app can read it. Name two ways it leaks.

**5.** The service writes logs to `logs/app.log` inside the container. After a crash and `docker rm`, the log is gone. What is the standard fix, and what does it change about how logs are collected?

**6.** A rebuild after changing one line of application code reinstalls pandas. What is wrong with the Dockerfile, and what is the fix?

**7.** The image was built a week ago. The registry's `champion` alias has moved twice since. A request to the container returns a prediction from the old model. Is this a bug? What would you change?

**8.** Why does `PYTHONUNBUFFERED=1` matter in a container more than on a laptop?

**9.** `docker history` shows an `ARG` containing an API token. You deleted the `ARG` line and rebuilt. Is the secret gone? Explain.

**10.** Your image is 1.9 GB and starts in 12 seconds. Name three changes you would try, in order, and what you would measure after each.

---

## Answers and reasoning

**1.** Because the context is transferred and hashed before the build starts. A large context makes every build slow, even when the files are never copied, and it creates a leakage surface: a broad `COPY . .` (or a mistaken pattern) can put any context file into a layer. `.dockerignore` addresses both.

**2.** The published port forwards to the container's network interface, not its loopback. A server bound to `127.0.0.1` accepts only connections originating inside the container. Bind `0.0.0.0` inside the container and keep the host-side restriction to localhost if desired.

**3.** No. `EXPOSE` is documentation and metadata for tooling; it does not publish anything. Reachability requires `-p` (or a compose `ports` entry, or an orchestrator's service definition).

**4.** It is stored in the image configuration, visible via `docker inspect` and to anyone who can pull the image; and if the value came through an `ARG`, it is also in the image history. Environment variables are also commonly captured in crash dumps and logs. Use a runtime secret mount or the orchestrator's secret store.

**5.** Write logs to stdout/stderr and let the platform collect them (`docker logs`, or a log driver shipping to a central store). The change is operational: rotation, retention, and search move from your code to the platform, and you can no longer rely on a file path inside the container.

**6.** The source copy appears before the dependency install, so a code change invalidates the install layer. Copy `requirements.txt` first, install, then copy the source. Layer order should go from least to most volatile.

**7.** Not a bug in the image: the image contains a snapshot, and snapshots do not follow aliases. It becomes a defect if the team believes the container follows `@champion`. Either rebuild on promotion (and record the model version in the image), or resolve the alias at start-up (and handle registry unavailability and reloads).

**8.** Without it, Python buffers stdout when it is not attached to a terminal. In a container, output can appear late or be lost on a crash — precisely when the logs matter. On a laptop the terminal usually makes stdout line-buffered, hiding the problem.

**9.** No. The layer that contained the `ARG` still exists in the image if it was built into a layer, and in the build cache. Deleting the instruction in a later build does not rewrite history. Rotate the token; treat it as compromised.

**10.** First measure where the size is (`docker history`, `docker image ls`): likely the base image and packages. Then, in order: switch to a slim base (measure size and whether wheels still install), remove unused heavy dependencies such as MLflow if the model is baked (measure size and whether any endpoint changes), and use a multi-stage build to keep build tools out of the final image (measure size and build time). After each change, re-measure cold start and re-run the prediction tests; a smaller image that starts slower or predicts differently is not an improvement.
