# Independent challenge · The smallest test that would have caught it

**Time:** 2 hours. **Deliverable:** `docs/smallest-test.md` plus the test itself, merged into your suite.

Big test suites are easy to write and hard to maintain. The skill this challenge builds is the opposite: given a real failure, find the cheapest test that would have caught it, and justify why a broader test would have been worse.

## The incident

> After a serving refactor, the ETA API began returning `duration_min` in **seconds** while clients expected minutes. Unit tests passed: the response was a positive float of the expected type. Integration tests passed: the endpoint returned 200. The regression gate passed: it read metrics from training, not from the API. Riders saw "arriving in 1,140 minutes".
>
> The defect was found by a rider complaining on social media.

## The task

1. Write **one** test that would have failed before the incident and passes after the fix. It must be short enough to read in one screen.
2. Justify in a paragraph:
   - why this test is the smallest sufficient one;
   - what it asserts that the existing unit, integration, and gate tests did not;
   - why a broader test (an end-to-end latency and contract suite, for example) would have been worse *for this defect* - even if it is worth having for others.
3. Add the test to your suite and show it failing against a deliberately broken implementation, then passing.
4. Add a second test only if the first is insufficient. If you add one, explain why the pair is still minimal.

## What counts as "smallest"

| Not smallest | Smallest |
|---|---|
| Spin up the API, a database, and 1,000 requests | Call the response-building function with one record and assert the unit |
| Assert every field of the response | Assert the one property that carries meaning: plausible magnitude or explicit unit |
| A golden-file comparison of the whole payload | A bound: duration between 1 and 240 minutes for a 5 km trip |

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Minimality | The test touches one unit of behaviour and runs in milliseconds |
| Discrimination | It fails on the broken version and passes on the fixed one, demonstrated |
| Reasoning | The paragraph explains the gap in the existing layers, not just the new test |
| Placement | The test lives in the layer where the defect was introduced |

## Hints

- The failure is a **unit mismatch**, so the assertion should reference a physical magnitude or a declared unit, not a type.
- An API contract test at the boundary is the right layer here, because the bug was introduced at the boundary. A model test could not see it.
- If your test would also fail for a legitimately long trip, your bound is too tight; choose a bound from the product's promise, not from one example.

## Extension

Write a short "missing layer" memo: which test layer had no coverage for units at any boundary in this project, and what one test per boundary would cost to maintain. Add the highest-value one to the suite and note the change in the strategy note.
