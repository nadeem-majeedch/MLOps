# 10 · Model serving and REST APIs using FastAPI

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Intermediate | 16 hours | [09](../09-model-registry/index.md) | Essential |

A model that only exists in a notebook cannot be used by the product it was built for. Serving is where machine learning becomes a service with a contract: specific inputs, specific outputs, and specific behaviour when a caller gets it wrong.

It is also where the most expensive silent bug lives. Units, feature assembly, and defaults can differ between training and serving while every component behaves exactly as written. The result is not a crash; it is a plausible number that is wrong.

## What you will be able to do

- Load the champion artifact once at start-up and serve predictions over HTTP.
- Define a request and response contract that rejects bad input with a useful message.
- Choose status codes deliberately: what is the client's fault, what is the server's.
- Separate liveness from readiness, and explain why a health check that loads the model is a bad health check.
- Measure latency as percentiles, with a budget stated before measuring.
- Detect train/serve skew with a single-record comparison against the training path.
- Read the generated API documentation and know what it does not promise.

## Start here

1. Read [Concepts](concepts.md) sections 1–6: contract, validation, status codes, health, latency.
2. Read the [worked example](worked-example.md): ten tests, one deliberately broken assembler, and a contract test that first failed for the wrong reason.
3. Do the [lab](lab.md): serve the champion, break the contract, and find the skew.

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives and the service-review criteria |
| [Concepts](concepts.md) | HTTP contracts, pydantic, status codes, health, latency, skew |
| [Worked example](worked-example.md) | The reference service, its tests, and the skew investigation |
| [Guided lab](lab.md) | Build, run, test, and break the service |
| [Independent challenge](independent-challenge.md) | A batch endpoint with a latency budget |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | 422s, import errors, model loading, slow first requests |
| [References](references.md) | FastAPI, pydantic, HTTP semantics, and serving guidance |

## What you produce

- A running FastAPI service with `/health`, `/ready`, `/model-info`, and `/predict`.
- A request schema that rejects unknown zones, negative distances, and extra fields.
- Tests for the happy path and at least five failure paths.
- A latency table with p50, p95, and p99, measured over at least 100 requests.
- A skew report comparing one record through the API and through the training pipeline.

## The reference run

The service loads `models:/raviride-eta@champion` (version 2) once at start-up. A valid request for an 11.4 km Z08→Z01 trip at 18:20 returns **43.0 minutes** in a median of **9.55 ms**; p95 is **10.27 ms** and p99 **30.60 ms** over 200 sequential requests on the same machine. Cold start to readiness is **2.96 s**. All figures are local and sequential; a load test with concurrency will look different.

## Next

[Module 11](../11-docker-containers/index.md) puts this service in a container, so "it works on my machine" stops being part of the deployment procedure.
