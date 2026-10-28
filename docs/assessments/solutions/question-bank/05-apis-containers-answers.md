# Answer key · Question bank 05

[Back to the questions](../../question-bank/05-apis-containers.md)

---

## Section A (1 mark each)

**A1 — b.** The payload is syntactically valid JSON but violates the schema, so
422 with a `loc` and message. A default (a) silently changes the meaning of the
request; a 500 (c) makes a client error look like a server fault.

**A2 — b.** Liveness proves the process runs; readiness proves it can serve. A
load balancer should send traffic only to ready instances, which is why the
distinction matters during model load and warm-up.

**A3 — b.** Layer caching. Source edits then rebuild only the copy and later
layers, which is the difference between a two-second and a two-minute build.

**A4 — b.** Binding to loopback inside the container accepts connections only from
inside it. Non-root (d) does not prevent publishing, and the health check (c)
does not affect reachability.

## Section B (3 marks each)

**B1.** Ignoring unknown fields returns a prediction that the caller believes used
data it did not use. Example: a caller sends `distance` while the schema expects
`distance_km`; a default fills in a plausible distance and the response looks
fine. Rejecting makes the mistake visible at the boundary.

**B2.** Feature names and order, data hash, training rows, parameters, library
versions, metric values, and the model hash; exposed at `/model-info` (and
reported in `/predict`). Operationally, during an incident the first question is
"which model is answering?", and the answer must not depend on reading a log from
deployment day.

**B3.** The base image tag moved, a dependency resolved differently, the build
context differed (a file was excluded by `.dockerignore`), the platform differs
(arm64 vs amd64), or the container depends on a host-mounted path or environment
variable. Reduce it with a pinned digest, a lock file, an explicit `.dockerignore`,
and a test that runs the built image, not only the code.

## Section C (4 marks each)

**C1.** The schema validates types and ranges but not the relationship that makes
the computation defined — a denominator that can be zero, or a category that maps
to an empty group. The defect is trusting validation to guarantee arithmetic
safety. Fix: guard the computation and return a specific 4xx if the input cannot
be scored, or exclude the value in the schema (e.g. `gt=0`), and add a test for
the zero case. A 500 is acceptable only for genuinely unexpected states.

**C2.** The image does not contain the artifact: either it was never copied
(excluded by `.dockerignore`, or built from the wrong context), or it was
generated after the build. Build-time fix: ensure `COPY artifacts/` runs after
training and that `.dockerignore` does not exclude it. Run-time fix: mount it,
`docker run -v "$PWD/artifacts:/app/artifacts" ...`, or point `MODEL_PATH` at a
mounted path — while stating that a mounted artifact is no longer reproducible
from the image alone.

## Section D (9 marks)

| Element | Marks | What it looks like |
|---|---|---|
| Serving shape | 2 | Stateless FastAPI/Uvicorn workers behind a load balancer, model loaded at start-up, no per-request training or disk scan |
| Latency budget | 2 | p95 measured under a realistic concurrency, a stated payload size, model load kept out of the request path, and a documented measurement method |
| Failure behaviour | 2 | Invalid input → 422; model unavailable → 503 with retry semantics; timeouts and bounded concurrency; no partial or defaulted predictions |
| Measurements | 2 | p95/p99 latency, error rate by status class, and prediction distribution or feature freshness — not only CPU |
| Rollback and capacity | 1 | Two versions deployable, a rollback procedure, and a capacity estimate (workers × requests per second) with headroom |

A strong answer computes the concurrency implied by 20 rps × 0.1 s ≈ 2 in-flight
requests and notes that one worker may suffice, so the architecture should be
simple. Claiming a p95 budget without saying how it was measured loses a mark.
