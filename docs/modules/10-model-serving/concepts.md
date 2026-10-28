# Concepts · From a model file to a service

## 1. What serving adds

Training code runs once, on data you control, and its output is a number you read. A service runs many times, on input you do not control, and its output is consumed by another program that will not notice a plausible wrong answer.

Four things appear that training never had to handle:

| Requirement | What it means |
|---|---|
| **Contract** | Callers need to know what to send and what they will get back |
| **Failure semantics** | Bad input must fail the caller's request, not the server's process |
| **Latency** | The answer has a deadline, measured in milliseconds |
| **Concurrency** | Several requests arrive at once, sharing one process |

A notebook model answers none of these. A service answers all four explicitly, which is why "just wrap it in Flask" produces something that works in a demo and fails in an incident.

## 2. Load once, at start-up

The model is data, not a per-request computation. Loading a scikit-learn artifact costs tens to hundreds of milliseconds; doing it inside the handler adds that to every request and multiplies it under concurrency.

FastAPI's **lifespan** hook is the right place:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    state["model"], state["info"] = load_model()
    yield
    state.clear()
```

`yield` separates start-up from shutdown: everything before it runs once when the server starts, everything after it runs when the server stops. Long-lived resources belong here — model, database pool, HTTP client.

The **cold start** is the time from process launch to the first successful request. In the reference service it is 2.96 s, almost all of it importing MLflow and reading the artifact. That number matters for autoscaling and for deploys: a container that takes three seconds to become ready cannot absorb traffic instantly.

**Reloading** is the consequence. If the registry alias moves, a running process keeps serving the model it loaded. Options, in increasing complexity: restart the process (simple, brief unavailability), expose a reload endpoint (fast, needs authorisation), or run a sidecar that watches the alias (production-grade). A service that claims to "follow the alias" without one of these is describing a restart policy, not a feature.

## 3. HTTP in one page

- **Method**: `GET` reads, `POST` creates or computes. Prediction is a `POST` because it carries a body and is not a resource lookup.
- **Status code**: the first digit is the category. `2xx` success, `4xx` the caller's fault, `5xx` the server's.
- **Idempotency**: repeating a request has the same effect as sending it once. `GET` is idempotent; a pure prediction `POST` is effectively idempotent (same input, same output, no state change), which is why retries are safe.
- **Body**: JSON for both directions, with `Content-Type: application/json`.
- **Statelessness**: each request carries everything needed. The server may cache, but must not require a previous request.

A prediction endpoint has no side effects, so the interesting decisions are the status codes for "you sent nonsense" (`422`), "you sent too much" (`429`), and "I could not answer" (`500`/`503`).

## 4. The request schema is the contract

The reference schema is a pydantic model. Each field carries a type, a constraint, and a description:

```python
class TripRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requested_at: datetime
    pickup_zone: str
    dropoff_zone: str
    distance_km: float = Field(gt=0, le=60, description="Route distance in kilometres")
    passengers: int = Field(ge=1, le=6)
    traffic_index: float = Field(ge=0, le=1)
    driver_supply: int = Field(ge=1, le=100)
    weather: Literal["clear", "cloud", "rain"]
```

Four decisions are embedded there, and each is arguable:

1. **`extra="forbid"`** rejects unknown fields. Default pydantic behaviour is to ignore them. Forbidding is stricter and catches a caller sending `fare_amount` or `duration_min` — often a sign that the caller is using the wrong schema. The cost: adding a field to the request is a breaking change for nobody, but *sending* one before the server knows it is now an error. Choose deliberately; document the choice.
2. **Ranges live in the schema**, not in a separate validation function. A negative distance is structurally invalid, so it should fail before reaching model code.
3. **`Literal` for weather** turns a typo into a clear error instead of an unseen category the encoder ignores.
4. **`datetime` for `requested_at`** parses ISO 8601. A record that arrives as `"2026-09-23 18:20"` works; `"23/09/2026"` does not, which is the correct outcome for an ambiguous format.

A field validator adds domain knowledge the type system cannot express:

```python
@field_validator("pickup_zone", "dropoff_zone")
@classmethod
def known_zone(cls, value: str) -> str:
    if value not in ZONES:
        raise ValueError(f"unknown zone {value!r}; expected one of {sorted(ZONES)}")
    return value
```

The resulting error is specific, which is the entire point:

```json
{"detail":[{"type":"value_error","loc":["body","pickup_zone"],
  "msg":"Value error, unknown zone 'Z99'; expected one of ['Z01', ..., 'Z08']",
  "input":"Z99"}]}
```

FastAPI maps pydantic validation failures to **422 Unprocessable Entity** automatically. Some teams argue for `400 Bad Request`; both are defensible, and consistency matters more than the choice. What is not defensible is returning `200` with `{"error": ...}` in the body: every client, retry library, and dashboard will treat it as success.

## 5. The response schema

```python
class PredictionResponse(BaseModel):
    duration_min: float
    model_alias: str
    model_version: str
```

Three choices worth noticing:

- **The unit is in the name.** `duration_min` cannot be confused with seconds the way `duration` can.
- **The version travels with the answer.** When a caller reports a strange prediction, the first question is "which model?", and the response can answer it without a log search.
- **The response is narrow.** Returning the full feature frame, the model's internal state, or a confidence interval you cannot justify invites dependence on details you will change.

Rounding is a contract decision too. The reference rounds to one decimal. That is honest about precision — the model's MAE is 2.77 minutes, so four decimal places would be false precision — and it makes responses byte-comparable in tests.

## 6. Three layers of validation

| Layer | Example | Who fixes the failure |
|---|---|---|
| Schema | `distance_km` missing, string where a number belongs | The caller |
| Domain rule | zone `Z99`, distance `-3`, 9 passengers | The caller, with a better message |
| Plausibility | model returns 900 minutes for an 11 km trip | You |

The third layer is the one teams forget. A model can accept a valid request and produce an absurd answer — because an unseen category hit the encoder's ignore path, because a feature was defaulted to zero, or because the artifact is not the one you think. The reference service checks the output range and raises:

```python
if not 1.0 <= prediction <= 240.0:
    raise ValueError(f"model produced an implausible duration: {prediction:.2f}")
```

An uncaught `ValueError` becomes a `500`, which is the correct signal: the caller did nothing wrong, the server cannot answer. Do not clamp the value to the valid range; a clamped nonsense answer is worse than an error, because it hides the defect.

## 7. Health, readiness, and the trap

Three different questions, often conflated:

- **Liveness** — is the process running and not deadlocked? `/health` returns `{"status":"ok"}` without touching the model. A liveness probe that loads a model will restart a healthy pod when the registry is briefly unavailable.
- **Readiness** — can this instance serve traffic right now? `/ready` checks that the model is loaded and reports which one.
- **Startup** — has initialisation finished? In Kubernetes this is a separate probe with a longer grace period, which prevents a slow cold start from being mistaken for a crash loop.

The reference service separates them. `/health` answers in microseconds and never fails because of the model; `/ready` fails when the model failed to load. A load balancer should use readiness, a supervisor should use liveness.

## 8. Latency: measure percentiles, state a budget

An average hides the requests that ruin an experience. Two services with the same mean can differ completely: one answers every request in 10 ms, the other answers 95% in 5 ms and 5% in 100 ms.

Report **p50** (typical), **p95** (bad but common), **p99** (the tail users complain about), and the maximum. The reference measurement:

| Metric | Value |
|---|---|
| Requests | 200, sequential, one client, warm server |
| p50 | 9.55 ms |
| p95 | 10.27 ms |
| p99 | 30.60 ms |
| Max | 41.69 ms |

Read that table honestly. Sequential requests from one client on the same machine measure the handler plus localhost overhead; they say nothing about throughput, contention, or network. p99 at three times the median suggests occasional garbage collection, logging, or scheduler noise — worth investigating, not yet a problem. A **budget** turns this into a requirement: "p95 must stay under 50 ms at 20 requests per second", stated before measuring, tested in CI (Module 12).

Cold start is a separate latency: 2.96 s to the first ready response. It belongs in the deployment discussion (Module 11), not in the request latency table.

## 9. Train/serve skew, the silent failure

**Skew** means the features used at serving differ from the features used at training, in a way that changes predictions. It is silent because both sides run without errors.

The reference demonstration sends the same trip through the same model, assembled three ways:

```text
correct                       43.00 min
distance sent in miles        22.64 min
traffic_index defaulted to 0  21.13 min
```

Both wrong versions are plausible. A 22-minute estimate for an 11 km trip is not obviously absurd; it is simply wrong by half. Nothing in the schema objects: `distance_km: 11.4` is valid whether the caller meant kilometres or miles.

Common sources:

| Source | Mechanism | Detection |
|---|---|---|
| Units | Caller sends miles; field name says km | Document units; validate range; compare distributions |
| Missing default | A field is unavailable and silently set to 0 | Make required fields required; log defaults |
| Timezone | `hour` computed in UTC, trained in local time | Store timezone with the timestamp; test a known hour |
| Encoding drift | A category unseen at training hits `handle_unknown="ignore"` | Log unknown categories; alert on rate |
| Feature order | Positional assembly instead of named selection | Single-record equivalence test |
| Different artifact | Serving loads `models/model.joblib`, test loads `@champion` | Compare against the artifact the service actually loaded |

The last row is not hypothetical: the first version of the reference contract test failed with 43.0 against 41.165, and the cause was not skew at all — the test loaded the local joblib baseline while the service loaded registry version 2. A test that compares two different models proves nothing about either path. Fix the comparison before investigating the difference.

The reliable detection is a **single-record equivalence test**: one fixed record, assembled by the serving code, predicted by the same artifact the service loaded, compared with the training path's result to within rounding. It catches assembly drift that a schema cannot see, and it fails loudly the day someone "simplifies" the feature code.

A useful negative result from the reference implementation: reordering the numeric columns alphabetically produced **exactly the same prediction** (43.00). That is not luck; `ColumnTransformer` selects columns by name, so order does not matter. A model that consumed a positional NumPy array would have produced a different answer. Knowing which of these your pipeline does is the difference between a real safeguard and a superstition.

## 10. Versioning and compatibility

Two versions exist and they are often confused:

- **The API version** (`/v1/predict`) is about the contract: field names, types, semantics.
- **The model version** (`model_version: "2"`) is about the artifact behind the contract.

Adding an optional field is backward compatible; making a required field optional is usually safe; renaming, removing, tightening a range, or changing a unit is breaking. `extra="forbid"` makes *adding* a request field a breaking change for clients that already send it — a real trade-off, not an accident.

The practical rule: version the URL when you must break the contract, run both versions during a migration, and put the sunset date in the deprecation response header. Model versions change far more often than API versions and must not require a client change; that is why the model version is in the body, not the path.

## 11. Idempotency, retries, and duplicates

A prediction is a pure function of its input, so retrying after a timeout is safe: the worst case is a duplicate computation, not a duplicate charge. That is worth stating in the documentation, because it licenses the client's retry policy.

This stops being true the moment the endpoint logs a row per request (Module 14). Then a retry writes a duplicate prediction record, and your monitoring counts phantom traffic. The fix is a client-supplied `request_id` with de-duplication on write, not a ban on retries.

## 12. Documentation that is generated, and what it does not say

FastAPI publishes OpenAPI at `/openapi.json` and an interactive UI at `/docs`. The reference service exposes four paths:

```text
['/health', '/model-info', '/predict', '/ready']
```

The schema documents types, constraints, defaults, and response shapes. It does **not** document:

- units and their assumptions (`distance_km` is kilometres *as driven*, not straight-line);
- the model's accuracy or its known weak slices;
- the meaning of a `500` in this deployment;
- rate limits, authentication, or the retention of request logs.

Those belong in the service README and in a model card. A caller who reads only Swagger will send a valid request and misinterpret a valid answer, which is the failure mode documentation is supposed to prevent.

## 13. Concurrency and batching

Uvicorn runs an event loop. A synchronous handler is executed in a thread pool, so a CPU-bound scikit-learn prediction does not block the loop but does consume a worker. One process is therefore limited by the GIL for CPU-bound work; scale with multiple workers or processes, and measure rather than assume.

Batching helps when callers have many rows and per-request overhead dominates: one model call for 500 rows is much cheaper than 500 calls. It hurts when callers have one row and expect an immediate answer. The reference service keeps `/predict` single-row and leaves batch as the independent challenge, where the latency budget makes the trade-off explicit.

Reading 500 rows and predicting them in one call also raises a new failure mode: one bad row rejects the whole batch. Decide whether the batch endpoint is all-or-nothing (fail with the row index) or partial (return per-row results). Both are defensible; silently dropping bad rows is not.

## 14. Security in one paragraph

The service accepts JSON from anyone who can reach it. At minimum: do not return stack traces, do not accept unbounded payloads, do not log full request bodies containing personal data, and put authentication in front of anything that is not a public demo. Modules 11 and 15 cover the container and governance sides; this module's responsibility is to not invent a new leak.

## 15. Local versus deployed

`uvicorn app:app --reload` is a development server: one process, automatic reload, verbose errors. It is not a production server. A deployment adds workers, a reverse proxy for TLS and timeouts, resource limits, and a restart policy — which is exactly what Module 11 packages and Module 12 automates.

The contract you build here does not change between the two. That is the point of writing it down.
