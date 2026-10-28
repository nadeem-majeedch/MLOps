# Question bank 05 · APIs and containers

| | |
|---|---|
| **Covers** | [Module 10](../../modules/10-model-serving/index.md), [Module 11](../../modules/11-docker-containers/index.md) |
| **Level** | Intermediate |
| **Questions** | 10 |
| **Marks** | 30 |
| **Time** | 40 minutes |
| **Answer key** | [05 · Answers](../solutions/question-bank/05-apis-containers-answers.md) |

---

## Section A · Multiple choice (4 marks)

**A1.** A client sends a valid JSON body with `"passengers": "two"`. What should
the service return?

- a) 200 with a default of 1 passenger
- b) 422 with the field and reason
- c) 500, because the model raised
- d) 400 with an empty body

**A2.** What is the difference between `/health` and `/ready`?

- a) None; both are aliases
- b) `/health` says the process is alive; `/ready` says it can serve, e.g. the
  model is loaded
- c) `/health` checks the model; `/ready` checks the database
- d) `/ready` is only for Kubernetes

**A3.** Why should a Dockerfile copy `requirements.txt` and install dependencies
*before* copying the source?

- a) It reduces the image size
- b) It lets the dependency layer be reused when only source changes
- c) Python requires that order
- d) It prevents secrets from being copied

**A4.** A container starts, logs `Application startup complete`, but the host
cannot reach it. Which is the most likely cause?

- a) The model is too large
- b) The server binds `127.0.0.1` inside the container instead of `0.0.0.0`
- c) The health check is missing
- d) The image runs as a non-root user

---

## Section B · Short answer (9 marks)

**B1.** *(3 marks)* Why reject unknown fields in a prediction request instead of
ignoring them? Give a concrete failure the rejection prevents.

**B2.** *(3 marks)* What belongs in a model artifact's metadata, and which
endpoint should expose it? Explain the operational reason.

**B3.** *(3 marks)* Explain why a container that works on your machine can fail on
a colleague's, even with the same Dockerfile, and how to reduce the chance.

---

## Section C · Debugging and diagnosis (8 marks)

**C1.** *(4 marks)* The service returns 500 for a subset of valid-looking
requests. The log shows:

```text
ZeroDivisionError: division by zero
```

The schema accepts the payload. What is the design defect, and what would you
change?

**C2.** *(4 marks)* `docker run -p 8000:8000 service:1` exits immediately with
`RuntimeError: no model at /app/artifacts/model.joblib`. The file exists locally
in `artifacts/`. Diagnose and give two fixes, one build-time and one run-time.

---

## Section D · Architecture and scenario (9 marks)

**D1.** A team wants to serve a model to an internal application at 20 requests
per second, with a 100 ms p95 budget. Describe the serving architecture you would
build, the failure behaviour you would specify, and the three measurements that
would tell you it is working. *(9 marks)*
