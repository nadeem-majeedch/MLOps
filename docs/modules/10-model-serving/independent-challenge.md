# Independent challenge · A batch endpoint with a budget you can defend

## The brief

The dispatch app can send one trip at a time, but the nightly planner sends 5,000. Add `POST /predict/batch`, keep a single model load, and show that latency stays inside a budget you stated **before** you measured.

The budget is the point. "It felt fast" is not a result; "p95 180 ms for 500 rows, against a 250 ms budget derived from the planner's 30-second cycle" is a result, because it can be wrong.

## Requirements

1. **Bounded input.** Reject batches above a stated size with `422` and a message that names the limit. Do not accept an unbounded array.
2. **One model call per batch.** Loop over rows calling the model 500 times and you will pass the tests and fail the point.
3. **Per-row errors, or none.** Decide between all-or-nothing and partial results, implement it, and document it. If all-or-nothing, the error must identify the offending row index. If partial, every response row must say whether it is a prediction or an error — never a bare `null`.
4. **Same contract as single prediction.** Batch results must equal single-request results for the same records, within rounding. Prove it with a test.
5. **A stated budget**, with where it came from, and a measurement that includes p50/p95/p99 and the batch size.
6. **A 500 is still a 500.** A batch that triggers a model failure must not return `200` with empty predictions.

## What to submit

- The endpoint, its schema, and its tests (at least: valid batch, oversized batch, one invalid row, equivalence with single predictions).
- `docs/batch-budget.md`: the budget, its derivation, the measurement table, and one sentence on what you would do if the p95 exceeded it.
- A measurement at two sizes — for example 100 and 500 rows — because latency per row usually improves with size while total latency grows.

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Budget | Written before measurement, with a derivation from a real constraint |
| Batching | One model call for the batch; you can show where the loop is |
| Limits | Oversized payloads rejected with a specific message |
| Equivalence | Batch and single predictions agree for every fixed record |
| Failure semantics | The chosen strategy is documented and tested, including its edge case |
| Honesty | The report states what the measurement does not cover (concurrency, network, cold start) |

## Questions to answer in the report

1. At what batch size does per-row latency stop improving? What limits it?
2. If one row in 500 is invalid, what does your endpoint return, and why is that the right trade-off for this caller?
3. What happens to p95 when two batch requests arrive at once, given one worker process?
4. Would a queue with asynchronous results be better than a synchronous batch endpoint for the planner? Defend either answer.

## Stretch

Add a `request_id` to the batch request and return it in the response, then make a retried request idempotent: the same `request_id` returns the stored result instead of recomputing. Explain what you had to store, and what happens when the store is unavailable.
