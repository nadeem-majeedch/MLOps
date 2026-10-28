# Independent challenge · Stop a plausible model from shipping

**Time:** 3 hours. **Deliverable:** a two-page decision memo, `docs/ship-decision.md`.

A model with a good aggregate score and a broken slice is the most common way an ML feature ships and then embarrasses its team. Your job is to be the reviewer who catches it before the riders do.

## The task

1. Pick the best aggregate model from your tracked runs. Treat it as a proposal from a colleague who wants to ship next week.
2. Build the case *for* it in one table: aggregate metrics, improvement over the previous baseline, training cost, inference cost if you can measure it.
3. Then look for the case against, in this order:
   - **the worst slice**, with its sample size and an estimate of how many riders per day it affects;
   - **the tail**: p95 and p99 error, and what a 95th-percentile error means for a rider deciding whether to walk;
   - **bias**: mean signed error. Is the model systematically optimistic at peak? Optimistic ETAs cause cancellations, pessimistic ones cause complaints - they are not symmetric costs;
   - **stability**: retrain with three different seeds and report the spread of MAE. If the improvement is smaller than the spread, it may not exist.
4. Write the memo with a clear recommendation: ship, ship behind a flag to one zone, or do not ship. Justify with numbers, not adjectives.
5. Add a "what would change my mind" line: the specific measurement that would reverse your decision.

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Honesty | The case for the model is presented fairly before it is criticised |
| Quantification | The worst slice is expressed in affected trips per day, not only in minutes |
| Statistical care | Seed-spread or interval evidence is used before claiming an improvement |
| Decision | A clear recommendation, a named risk owner, and a reversal condition |

## Rules

- Do not tune the model to fix the slice in this exercise. The point is the decision, not another experiment.
- Every number must come from a run you can point to.
- If the slice with the worst error has fewer than 30 rows, say so and treat it as a hypothesis.

## Hints

- Convert error to impact: a 4-minute error at peak on a 6-minute promise changes behaviour; a 4-minute error on a 30-minute trip does not.
- p95 is easier to explain to a product manager than RMSE: "one trip in twenty is off by more than X minutes".
- If seed spread is large relative to the improvement, the honest recommendation is often "not yet", with a plan to collect more test data.

## Extension

Take the memo to someone who does not work on the model and ask them to restate the recommendation and its main risk. If they cannot, rewrite the summary. This is the only reliable test of a decision document.
