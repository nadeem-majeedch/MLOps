# Independent challenge · Halve the image without changing the answer

## The brief

Reduce the image size by at least 40% and prove the service still behaves identically. Then explain what got worse.

The second sentence is the exercise. Almost anything can be made smaller by removing things; the engineering question is which removals are free and which move the cost somewhere else — debuggability, build time, reproducibility, or the ability to resolve a registry alias.

## Constraints

- The same `/predict` response for the fixed trip, to the same rounding.
- The same endpoints and status codes, including the 422 cases.
- The container must still run as non-root and still report healthy.
- No new paid service; no cloud registry required.
- The build must be reproducible from a clean cache.

## Levers, with their costs

| Lever | Typical effect | Cost |
|---|---|---|
| `python:3.12-slim` instead of the full image | Large | No compilers; some packages fail without wheels |
| Remove MLflow (baked model) | Large | Cannot resolve `@champion` at run time |
| Multi-stage build | Moderate | More complex Dockerfile; harder to debug a failed stage |
| `--no-cache-dir` and cleaning in the same layer | Small–moderate | None, if done correctly |
| Remove tests and docs from the context | Small | Cannot run tests inside the image |
| Distroless or Alpine base | Large | No shell; musl vs glibc wheel issues |
| Prune unused dependencies | Varies | Risk of removing something imported lazily |

Pick two or three and know why you did not pick the others.

## What to submit

1. **Before and after measurements**: `docker image ls` size, build time from clean cache, cold start to `/ready`.
2. **A behavioural equivalence check**: the fixed trip's response before and after; the six error cases from the lab still returning the same status codes.
3. **The new Dockerfile** with a comment on each changed line explaining the trade-off.
4. **A "what got worse" section**: at least two concrete costs, with evidence (for example, "no shell, so `docker exec` cannot be used for diagnosis; we added a `/debug/config` endpoint instead").
5. **A reproducibility note**: the base image tag or digest, and whether a rebuild produced the same digest.

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Reduction | At least 40%, measured, with the before/after numbers |
| Behaviour | Same predictions and same error semantics |
| Operations | Non-root, healthy, logs still visible |
| Trade-offs | At least two costs named, with evidence |
| Reproducibility | Clean-cache rebuild works; base image and digest recorded |
| Honesty | No claim of size reduction that came from deleting the model or tests silently |

## Questions to answer

1. Which lever gave the largest reduction per unit of risk?
2. If you removed MLflow, how would a rollback to a previous model now work? How long would it take?
3. If you moved to a distroless base, how would you diagnose a container that fails to start?
4. What does the image size actually cost in your deployment: pull time, storage, or nothing measurable?

## Stretch

Build two variants — one with a baked model, one that resolves the registry alias at start-up — and compare size, cold start, rollback time, and failure behaviour when the registry is unreachable. Write a one-page recommendation for a team that deploys twice a week.
