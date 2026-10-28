# Problem statement template

> Copy this into `docs/problem-statement.md` in your project. Delete the guidance
> in italics. One page. Write it before the first model.

---

## Title

*Name the system and the decision it supports, not the algorithm. "Trip duration
estimate for RaviRide dispatch", not "Random forest regression".*

## 1. The situation

*Three or four sentences. Who has the problem, what happens today, and what it
costs. No technology.*

> Example: RaviRide shows riders an arrival estimate before booking. Today the
> estimate comes from a fixed formula based on distance. Riders abandon bookings
> when the shown time is more than five minutes short, and dispatch cannot tell
> which estimates are unreliable.

## 2. The decision this system supports

| | |
|---|---|
| **Who acts** | *The rider, or the dispatcher, or the support agent* |
| **What they do differently** | *Book, re-route, call a driver, offer a voucher* |
| **What the system must never decide** | *Price, driver assignment, whether a rider is served* |
| **Cost of a false positive** | *In this system: an over-optimistic ETA* |
| **Cost of a false negative** | *An over-pessimistic ETA* |

*If you cannot name both costs, you cannot choose a threshold, and the evaluation
section will be arbitrary.*

## 3. Success criteria

Write these before building. At least one must be measurable from data you will
actually have.

| Criterion | Metric | Threshold | Measured on | When |
|---|---|---|---|---|
| Accuracy | MAE | ≤ 3.0 min | Held-out trips, last 20% by date | Before release |
| Slice safety | MAE for trips > 15 km | ≤ 4.0 min | Same split | Before release |
| Service | p95 latency | ≤ 150 ms | 20 rps, 30 minutes | Before release |
| Operation | Rollback time | ≤ 5 min | Timed drill | Before release |
| Adoption | Predictions served per day | ≥ 1,000 | Service logs | Week 4 |

*"Improve accuracy" is not a criterion. A number, a population, and a date are.*

## 4. What is out of scope

*List three things a reader might reasonably expect and you are not doing. This
protects you from scope creep and is assessed as judgement.*

- Real-time traffic feeds; the model uses historical patterns only.
- Driver assignment or pricing.
- Multi-city generalisation.

## 5. Data

| | |
|---|---|
| **Source** | *Synthetic generator in this repository, seed 20260101* |
| **Licence** | *CC0 for generated data; no source data* |
| **Rows and period** | *600 trips, January–February 2026 (synthetic)* |
| **Target** | *`eta_minutes`, realised duration* |
| **Sensitive fields** | *None; identifiers are sequence numbers* |
| **Known limitation** | *Synthetic relationships are simpler than real traffic* |

## 6. Constraints and assumptions

*Time, hardware, no paid services, single developer, no access to production
traffic. State the assumptions that could invalidate the project.*

## 7. What would make you stop

*One or two conditions. A project without a stop condition has no boundary.*

> If the model cannot beat the distance-only formula by 20% on held-out data, the
> project does not proceed; the formula stays.

---

## Checklist

- [ ] The decision and the person making it are named.
- [ ] Both error costs are stated, not only the one that is easy to measure.
- [ ] Every success criterion has a metric, a threshold, and a measurement plan.
- [ ] Out-of-scope items are listed.
- [ ] Data provenance and licence are recorded.
- [ ] A stop condition exists.
- [ ] No technology appears before section 5.
