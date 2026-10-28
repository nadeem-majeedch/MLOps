# Knowledge check · Module 10

## Questions

**1.** A service loads its model inside the request handler. It returns correct predictions. Name two costs that appear under load.

**2.** A client sends `{"distance_km": 11.4}` where the number is miles. The request is valid and returns `200`. Which layer should have caught it, and what would you change?

**3.** What is the difference between `/health` and `/ready`, and why should `/health` not load the model?

**4.** Your API returns `422` for a missing field and `500` when the model produces 900 minutes. Who is responsible for each, and what should each of them do next?

**5.** Why is p95 more useful than the mean when reporting prediction latency?

**6.** A contract test compares the API's prediction with `models/model.joblib` and fails by 1.8 minutes. What is the first thing to check, and why is "train/serve skew" a premature conclusion?

**7.** The service accepts a valid request for a zone that exists but was absent from training, and returns a prediction. Is this a bug? What should happen instead?

**8.** You clamp predictions to the range 1–240. Give one reason this is worse than raising an error.

**9.** The API's response includes `model_version`. Give two incident questions this answers that a log search might not, quickly enough to matter.

**10.** Adding an optional field to the request schema is usually backward compatible. Why does `extra="forbid"` complicate that claim?

---

## Answers and reasoning

**1.** Every request pays the artifact load cost (tens to hundreds of milliseconds), so latency is inflated and grows with concurrency; and memory/IO churn increases because each load allocates a new object that the garbage collector must reclaim. Correctness is unaffected, which is why this survives code review and fails in production.

**2.** The schema did its job: `11.4` is a valid float in range. The unit is a **semantic** contract, not a type constraint. Catch it with documentation and field naming (`distance_km`), range validation informed by the product (an 11 km trip in Z08 cannot be 4 minutes), and monitoring of the distance distribution against the reference. Assuming the caller's unit is unvalidated is the actual defect.

**3.** `/health` answers "is the process alive?"; `/ready` answers "can it serve traffic now?" — the model is loaded and named. If `/health` loads the model, a registry outage or a slow artifact turns a healthy process into a restart loop, and orchestration kills the thing that was working.

**4.** `422` belongs to the caller: fix the request. `500` belongs to the service owner: the caller sent something valid and the server could not answer, so investigate the artifact, the feature assembly, or the plausibility rule. Returning `500` for a caller mistake hides a client bug; returning `422` for a server bug blames the caller.

**5.** The mean is dominated by the bulk of fast requests and hides the tail, which is where timeouts and user complaints live. p95 says "one request in twenty is at least this slow", which is the number an SLA can be written against.

**6.** First check that both sides use the same artifact. In the reference case the API loaded registry version 2 while the test loaded the local baseline version 1; the 1.8-minute gap was two models, not two paths. Concluding "skew" would have sent you to rewrite feature code that was already correct.

**7.** It is a defect in the training data or the encoder policy, not necessarily in the service. The model has no information about that zone and falls back to whatever the encoder's ignore path implies, producing a confident-looking number. The right behaviour is to prevent it upstream: a provenance gate on training data (Module 09), an explicit unknown-category policy, and a monitoring alert when the unseen-category rate rises (Module 14).

**8.** Clamping turns an impossible answer into a plausible one, so the defect becomes invisible: dashboards look normal, the caller ships a wrong ETA, and nobody investigates. An error surfaces the problem at the moment it occurs, with the input attached. If a fallback is genuinely needed, make it explicit in the response (`"fallback": true`), not silent.

**9.** "Which model produced this specific bad prediction?" — answered directly from the response instead of correlating timestamps across a log store. And "did the answer change when we promoted?" — because the caller's captured responses show the version transition. Both matter during the first ten minutes of an incident.

**10.** `extra="forbid"` means a client that sends the new optional field *before* the server is upgraded gets a `422`. The schema change is additive from the server's perspective but breaking for early adopters, so rollout order matters: deploy the server first, or relax to `extra="ignore"` during the transition.

## Scoring yourself

- 8–10: you can defend a service contract in review.
- 5–7: reread Concepts §4–§9; the gaps are usually validation layering or skew detection.
- Below 5: rebuild the lab's error table from memory before moving on. Module 11 assumes you can explain what the service promises.
