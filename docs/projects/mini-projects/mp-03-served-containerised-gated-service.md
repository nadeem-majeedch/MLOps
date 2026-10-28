# MP3 · Served, containerised, gated service

| | |
|---|---|
| **After** | [Module 12](../../modules/12-ci-cd/index.md) |
| **Integrates** | Modules 10–12 |
| **Effort** | About 12 hours |
| **Weight** | 10% (illustrative) |
| **Assumes MP2** | A registered champion with a policy |

---

## Brief

A caller can get a validated prediction from a container, and CI refuses a
regression. Three systems have to agree: the training path, the serving path, and
the gate. Each one can be correct alone while the combination is wrong — which is
the failure this project is designed to expose.

You are also asked to measure something and then decide not to optimise it. That
decision, explained, is worth more than a faster image.

---

## Deliverables

1. **API**: `/health`, `/predict`, `/model-info` with schema validation on every
   request.
2. **Contract test** comparing serving features with training features on the same
   row.
3. **Dockerfile** with a pinned base, non-root user, and `.dockerignore`; a size
   and start-time comparison with and without optimisation.
4. **Compose file** running the API beside the tracking store (or a documented
   reason it is unnecessary).
5. **CI workflow**: lint, tests, data validation, smoke train, metric gate, and
   artifact upload.
6. **Five malformed payloads** with their 422 responses and the field each names.
7. **Latency measurement** against a budget you defined before measuring.

---

## Acceptance criteria

- [ ] Five malformed payloads each return 422 with a specific message.
- [ ] The contract test fails when the feature order changes, and the API still
      returns 200 — proving the test catches what a smoke test cannot.
- [ ] p95 latency is measured against a budget defined beforehand, with the method
      stated.
- [ ] The image builds from scratch and runs as a non-root user.
- [ ] CI fails on a data-schema break, a unit regression, and a metric regression,
      each for the stated reason.
- [ ] The image contains the artifact, or the run-time mount is documented as a
      deliberate trade.
- [ ] `/model-info` reports the same hash as the artifact metadata.

---

## Evidence

| Claim | Weak | Strong |
|---|---|---|
| Validation works | "It validates" | Five payloads, five responses, five named fields |
| Contract test is real | "Tests pass" | The test, plus a deliberate reorder and the failure output |
| CI gate works | A green badge | The red run for each of three injected defects, with the failing step |
| Container is reproducible | "Docker builds" | Clean build, image digest, non-root user, artifact hash inside |
| Latency is acceptable | "It feels fast" | Method, request size, concurrency, p50/p95, and the budget |

---

## Rubric

| Criterion | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Service contract** | No endpoint | Predicts well-formed input only | Validates and returns specific errors | As level 2, plus a contract test that catches path divergence |
| **Container** | No Dockerfile | Builds but root, unpinned, or includes build tools | Pinned, non-root, ignore file, artifact inside | As level 2, plus measured size or start-time change and a stated non-optimisation |
| **CI gate** | No workflow | Runs but does not fail on regression | Tests, data, and metric gate run and block | As level 2, plus a log proving the gate failed for the stated reason and passed after a fix |
| **Evidence** | Claims | Commands only | Logs and measurements for every claim | A peer reproduces from the repository without questions |

---

## Build order

1. Serve the champion with a thin API; add `/health`.
2. Add the request schema and one rejection test.
3. Write the contract test; break the order; restore it.
4. Dockerise; build; run; compare size and start time.
5. Add tests and the metric gate to CI.
6. Inject the three defects, one at a time, and keep the logs.
7. Measure latency; write down what you chose not to optimise.

Steps 1–3 are a working service. Steps 4–6 are the assessment. If Docker is
unavailable, complete steps 1–3 and 5, and document the container as unbuilt with
the exact commands you would have run — the honesty criterion covers this.

---

## Common failures

| Failure | Signature | Fix |
|---|---|---|
| Feature order drifts | Predictions plausible but worse | Share one feature function; contract test |
| Artifact missing from image | `RuntimeError: no model at /app/...` | Copy artifacts, check `.dockerignore` |
| Container bound to loopback | Host gets connection refused | `--host 0.0.0.0` |
| Gate compares to itself | CI green on a bad model | Pin the baseline artifact and hash |
| Latency measured once | A number with no method | State payload, concurrency, and percentile |
| Tests run against a stale artifact | Suite passes for the wrong reason | Build a throwaway artifact in a fixture |

---

## Extension

Add a batch endpoint with a bounded payload and a documented partial-failure
policy. Then measure the p95 for a batch of 100 and explain why it is not 100×
the single-row latency.

See also: [Lab 10 · Serving contract](../../labs/lab-10-serving-contract.md),
[Lab 12 · Container image](../../labs/lab-12-docker-image.md),
[Lab 14 · CI workflow](../../labs/lab-14-actions-workflow.md), and the
[intermediate starter](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/starters/intermediate-eta-service).
