# Learning objectives · Module 10

| # | Objective | Evidence |
|---|---|---|
| 1 | Serve a model over HTTP with one load at start-up | A service whose `/model-info` reports the loaded version |
| 2 | Declare and enforce a request contract | Schema plus tests for missing, extra, and out-of-range fields |
| 3 | Return meaningful errors | A 422 body naming the field and the rule that failed |
| 4 | Choose status codes deliberately | A table of endpoint → 2xx/4xx/5xx and the reason for each |
| 5 | Separate liveness from readiness | `/health` that does not touch the model; `/ready` that does |
| 6 | Measure latency in percentiles | p50/p95/p99 over at least 100 requests, with a stated budget |
| 7 | Detect train/serve skew | A single-record comparison against the training path |
| 8 | Read generated documentation critically | A list of what OpenAPI documents and what it does not |

## Service-review criteria

A service is reviewable when a caller can use it from the documentation alone, and an operator can diagnose it from the endpoints alone:

- [ ] Every request field has a type, a range or enum, and a description in the schema.
- [ ] Invalid input returns `4xx`, never a `200` with an error inside the body.
- [ ] A server-side failure returns `5xx` and does not leak a stack trace to the caller.
- [ ] The response says which model version produced it.
- [ ] `/health` answers "is the process alive?" without loading anything heavy.
- [ ] `/ready` answers "can it serve?" and fails when the model is missing.
- [ ] The model is loaded once, not per request.
- [ ] There is a test that would fail if the serving feature assembly diverged from training.
- [ ] Latency is reported as percentiles, with the measurement method and the machine.

## Why a contract is not documentation

Documentation describes what the service intends; a schema enforces what it accepts. They diverge the moment someone changes a field. FastAPI generates the documentation *from* the schema, so there is one source of truth for structure — but not for meaning. `distance_km: float` says nothing about the unit, and a schema cannot tell you that `traffic_index` was inverted in the caller's system.

## Self-check before you start

You should have a registered model from Module 09 and be able to run a Python module from the command line. You do not need prior web-framework experience, but you should know what an HTTP status code is.

After the module, you can answer:

1. Why does loading the model inside the request handler produce correct but unacceptable behaviour?
2. What is the difference between `422` and `500` here, and who fixes each?
3. Why is `/health` returning `200` compatible with the service being unable to predict anything?
4. What does p95 latency tell you that the mean does not?
5. Why can a service with a perfect schema still return wrong predictions?
