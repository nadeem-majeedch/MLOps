# Independent challenge · Extend the capstone without breaking it

## The brief

The Core capstone is complete and handed over. You have one more sprint to make it production-grade — or to prove that a particular production feature is not worth its cost.

Choose **two** extensions from the list below. For each, add the feature, the evidence that it works, and the evidence that it fails safely. Then write a one-page decision record: what you added, what it cost, what it replaced, and what you deliberately did not add.

The extensions are not a checklist to collect. A well-argued refusal is a valid result if it names the failure the feature would prevent and the cost it would add.

## Extension options

### A. Orchestration with retries and backfill (Module 13)

Add a scheduled flow with:

- a retry policy that distinguishes transient from permanent failures;
- an idempotent task, demonstrated by running it twice;
- a backfill for a missed day, with the same output as the original run;
- a run history that shows a failure, a retry, and a success.

Evidence: a run log, a duplicate-safe output, and a backfill comparison.

### B. Security and privacy hardening (Module 15)

Add:

- a threat model with ranked findings and one implemented control;
- a secret scan with no unaddressed findings;
- a dependency scan with a triage table;
- a model card with measured disparity and a prohibited use;
- a rotation rehearsal.

Evidence: the threat model, scan outputs, the model card, and a timed rotation.

### C. Kubernetes deployment (Module 16)

Add:

- the corrected manifests from the module lab;
- a local `kind` deployment, if available;
- a rollout and a rollback, timed;
- a cost worksheet with assumptions.

Evidence: the 35/35 checker, cluster output if run, the rollout log, and the cost sheet. If no cluster is available, say so and provide the static review plus a written rollout plan.

### D. Performance and load (Module 10 / 14)

Add:

- a load test at the expected peak and at 2× peak;
- p50/p95/p99 and error rate, with the method stated;
- the first bottleneck, measured;
- one optimisation and its effect, with a regression check.

Evidence: the load-test output, before/after numbers, and the bottleneck analysis.

### E. Fairness and human review (Module 15)

Add:

- a group-level evaluation with row counts and confidence intervals;
- a human-review step for the highest-risk decisions;
- a measurement of how often the reviewer overrides the model;
- a policy for what the reviewer may and may not see.

Evidence: the evaluation table, the review log, and the policy.

## Requirements for each extension

1. **Failure mode.** What does the extension prevent, and what new failure does it introduce?
2. **Evidence.** A command or artifact that proves it works, and one that proves it fails safely.
3. **Cost.** Engineer time, runtime cost, and operational burden.
4. **Rollback.** How to remove the extension without breaking the Core system.
5. **Decision record.** Why this extension, why not the others, and what would change your mind.

## What to submit

- The two extensions, implemented.
- An evidence index with paths and commands.
- A one-page decision record per extension.
- An updated runbook covering the new failure modes.
- A 200-word statement of what you deliberately did not add.

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Core intact | The original clean-clone metric and tests still pass |
| Failure mode | Each extension names what it prevents and what it risks |
| Evidence | Both success and safe-failure evidence exist |
| Cost | Time and runtime cost are stated |
| Rollback | Removing the extension is documented and tested |
| Runbook | The new failure modes are covered |
| Decision | At least one rejected option is argued, not ignored |
| Honesty | Anything not run is marked not run |

## Questions to answer

1. Which extension had the best evidence-to-effort ratio, and which was the most disappointing?
2. Did any extension make the Core system harder to hand over? How would you mitigate that?
3. If you could keep only one extension for a real deployment, which would it be, and why?
4. What did you deliberately not add, and what would have to be true to add it later?

## Stretch

Write the **production readiness review** for the extended system as if you were a different engineer: what you would approve, what you would block, and what you would ask for before the next release. Then answer the review as the author. The gap between the two documents is the most useful feedback you will get.
