# Independent challenge · A rollout you would approve

## The brief

The platform team will approve one release window for the ETA service. You must write the rollout plan they will approve, including the evidence that would make them stop it.

The plan is judged on whether a different engineer could execute it at 02:00 without asking you a question. It must cover the release, the observation window, the abort criteria, the rollback, and the cost.

## Requirements

1. **Release description.** Image tag or digest, the change, and the expected effect on latency, error rate, and model quality.
2. **Strategy.** Rolling, blue-green, or canary, with the reason. If canary, state the traffic split and the promotion rule.
3. **Pre-flight checks.** At least six: image exists and scans clean, model artifact loads, readiness passes locally, database schema is compatible, capacity is available, rollback target is pullable.
4. **Abort criteria.** At least four signals with a threshold, a window, and an owner. Include one business signal and one model-quality signal.
5. **Rollback.** Exact command, verification command, expected time, and what rollback does *not* fix (for example, a destructive migration).
6. **Observation window.** How long, what is watched, and who declares success.
7. **Cost.** Monthly and per-release incremental cost, with assumptions and a range.
8. **Communication.** Who is told before, during, and after; what happens if the release is aborted.

## The scenario

- Two replicas, HPA 2–5, 100m CPU / 256Mi memory requests.
- Peak 20 requests/second, p95 latency 40 ms.
- The new image changes the feature assembly and is 3% slower.
- The previous image digest is known and still in the registry.
- The database has no migration in this release.
- The error budget has 40% remaining for the 30-day window.

## What to submit

A four-page release plan with the eight sections, plus a filled table:

| Signal | Baseline | Abort threshold | Window | Owner | Action |
|---|---|---|---|---|---|
| 5xx rate | 0.2% | > 1% | 2 min | on-call | undo |
| p95 latency | 40 ms | > 120 ms | 5 min | on-call | pause |
| Readiness failures | 0 | any new pod > 60 s | 1 min | release lead | undo |
| Prediction MAE (delayed) | 2.77 | > 3.20 | next labelled batch | model owner | review |
| Error budget burn | 40% left | > 10% consumed | 1 h | SRE | freeze |

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Executable | Another engineer can run it without asking a question |
| Pre-flight | Six checks, each with a command or artifact |
| Abort | Four signals, each with threshold, window, owner, action |
| Rollback | Command, verification, time, and limitations |
| Model quality | A delayed-label signal, not only 5xx and latency |
| Cost | Assumptions, range, and the sensitive driver |
| Communication | Before/during/after, with an abort message |
| Honesty | Names one thing the plan cannot detect |

## Questions to answer

1. Which abort signal would you trust least, and why keep it?
2. If the canary is at 5% and the error rate doubles, how many users are affected before the abort fires? Show the arithmetic.
3. What would you do differently if the release included a destructive migration?
4. If the error budget were exhausted, would you still release? Defend the answer.
5. Which cost line would you challenge first, and what evidence would you ask for?

## Stretch

Write the **post-release review** for a rollout that was aborted at 5%. Include the timeline, the signal that fired, the false-positive cost, and one change to the abort criteria. Do not blame the engineer who pressed the button.
