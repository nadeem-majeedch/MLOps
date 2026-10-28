# MP4 · Monitored lifecycle with retraining

| | |
|---|---|
| **After** | [Module 14](../../modules/14-monitoring-drift/index.md) |
| **Integrates** | Modules 13–14, with MP1–MP3 |
| **Effort** | About 12 hours |
| **Weight** | 10% (illustrative) |
| **Assumes MP3** | A gated service is running |

---

## Brief

The system notices its own degradation and proposes a retrain, with evidence.
"Notices" is the hard word: drift is easy to compute and hard to interpret, and
the common failure is not a missing metric but an alert that fires constantly and
teaches everyone to ignore it.

You will replay four weeks of batches. One of them is shifted. Your job is to
detect the shift, decide what it does and does not license you to claim, and make
the retraining decision conditional on evidence.

---

## Deliverables

1. **Drift reports** per batch across four replayed weeks.
2. **Thresholds with justification**, including a minimum batch size and a
   rationale tied to the cost of action.
3. **One alert** with an owner, a first diagnostic step, and a closing condition.
4. **Conditional retraining trigger**: the code path that opens a retrain, and the
   guardrail that prevents auto-promotion.
5. **Before/after comparison** showing improvement on the affected slice and no
   regression elsewhere.
6. **Decision memo** of one page for a non-technical manager, stating the cost of
   retraining and the cost of not retraining.

---

## Acceptance criteria

- [ ] Data drift and prediction drift are reported separately.
- [ ] The alert fires on the injected batch and not on the three control batches.
- [ ] The report does not claim accuracy fell without labels that show it.
- [ ] Retraining is justified by evidence, and a worse candidate is blocked by the
      existing gate.
- [ ] The memo names both costs and one uncertainty.
- [ ] The alert has a named owner and a first diagnostic step, not only a
      threshold.

---

## Evidence

| Claim | Weak | Strong |
|---|---|---|
| Drift detected | One PSI value | Per-feature values across four batches, with a control batch |
| Alert is usable | "It fires" | The firing batch, the non-firing controls, the owner, and the first step |
| Retraining helps | A better aggregate | Slice improvement, no regression elsewhere, and the gate output |
| Decision is sound | "We recommend retraining" | Costs on both sides, uncertainty named, and a trigger for reversal |

---

## Rubric

| Criterion | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Detection** | No reports | One batch, one metric | Four batches, per-feature, controls included | As level 2, plus data vs prediction drift separated |
| **Thresholds** | Arbitrary | Copied from a blog | Justified against cost and batch size | As level 2, plus sensitivity to sample size shown |
| **Alert design** | None | Threshold only | Owner, first step, closing condition | As level 2, plus tested against a control batch |
| **Decision quality** | Retrain reflex | Evidence on one side | Evidence and cost on both sides | As level 2, plus a guardrail and a stated uncertainty |

---

## Build order

1. Log predictions and inputs from the service, with a batch identifier.
2. Build the reference from the training window; freeze and hash it.
3. Compute per-feature drift for three control batches.
4. Inject the shift; compute again; compare.
5. Write the alert and test it against controls.
6. Retrain, gate, and compare slices.
7. Write the memo last, from the numbers.

---

## Common failures

| Failure | Signature | Fix |
|---|---|---|
| Reference overwritten nightly | PSI trend always small | Freeze the training-window reference |
| Alert on every batch | Threshold set to look strict | Set from the control distribution, not from fear |
| Claiming accuracy drop from drift | Report says "performance fell" with no labels | Separate the two claims explicitly |
| Retraining on the same shifted batch | Improvement that does not generalise | Hold out part of the shifted period |
| No guardrail | Retrain auto-promotes a worse model | Route through the MP2 gate |
| Memo full of PSI | Manager cannot act | Lead with the decision and the cost |

---

## Extension

Add a delayed-label evaluation: simulate outcomes arriving two weeks after
prediction and compute the metric on matured labels. Report what the alert would
have said in the meantime, and whether it was right.

See also: [Lab 17 · Drift analysis](../../labs/lab-17-drift-analysis.md),
[Lab 18 · Regression and rollback](../../labs/lab-18-regression-rollback.md), and
the [advanced starter](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/starters/advanced-monitoring-pipeline)
for a working drift and gate implementation.
