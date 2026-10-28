# Answer key · Question bank 03

[Back to the questions](../../question-bank/03-experiment-tracking-evaluation.md)

---

## Section A (1 mark each)

**A1 — b.** `max_depth` is an input to the run. Metrics are outputs, and training
duration is an observation about the run rather than a property of the model.
Per-slice accuracy is a metric, and belongs in metrics with the slice in its name.

**A2 — b.** Choosing on the test set turns it into a validation set; the reported
score is the maximum of twenty noisy estimates. The fix is a held-out set touched
once, or nested selection.

**A3 — b.** With 3% positives, accuracy is dominated by the majority class and ROC
AUC flatters a model at the operating point you care about. PR AUC and recall at
a precision floor describe the trade you actually make.

**A4 — a.** An alias is a named pointer (`champion`); promoting moves the pointer.
The version and its artifact do not change, which is what makes rollback possible.

## Section B (3 marks each)

**B1.** Any three with a reason: data version/hash (the metric describes *that*
data); code commit or image digest (the metric describes *that* implementation);
parameters and seed (the metric is a draw from that configuration); environment
versions (BLAS and library versions move results); evaluation split definition
(a metric on a different split is not comparable). One mark each.

**B2.** Writing the rule first prevents the result from choosing the criterion.
Example: "promote if ROC AUC improves and no slice drops more than 2 points."
Without it, a team that sees a 3-point slice drop invents a reason it does not
matter. The rule is not sacred — it can be revised — but the revision must be
visible and justified, not silent.

**B3.** Report both numbers: aggregate improvement and the long-trip regression,
with the slice size and the decision rule. Recommendation depends on exposure: if
long trips are a small share but high-value, the 8% may not be worth it. A strong
answer refuses to average the two into one number without stating the weighting.

## Section C (4 marks each)

**C1.** The run record should contain a **data version or hash**; without it,
"identical parameters" is not comparable. Add the dataset hash and the split
definition to every run, and make the training entry point compute them rather
than accept them as free text. Two marks for the missing field, two for the
mechanism that prevents recurrence.

**C2.** Candidates:

| Cause | Check |
|---|---|
| Leakage in training (target-derived feature, duplicate rows across splits) | Recompute the metric on a time-based or group split |
| Split mismatch: test rows come from the same period as training | Compare date ranges and group overlap |
| Population difference: production is a different segment | Compare feature distributions, then score a labelled production sample |
| Label definition changed between experiment and production | Compare the label query and positive rate |

Accept any three with a check. "The model overfit" is not an answer without
evidence of *how*.

## Section D (9 marks)

| Element | Marks | What it looks like |
|---|---|---|
| One tracking store | 2 | MLflow (local file store is enough) with runs named by purpose, params, metrics, and the data hash logged automatically |
| One evaluation protocol | 2 | Fixed split or time-based folds, a written selection rule, and slices defined before results |
| Registry with aliases | 2 | Versions immutable; `champion` points at the deployed one; the promotion decision cites run IDs |
| Reproducible entry point | 2 | One command trains and logs, so a run record cannot be created by hand |
| Answerable questions | 1 | A short README that shows how to find the deployed version, its run, and the comparison |

Lose marks for a plan that only renames the spreadsheet, stores metrics in Git
commit messages, or logs results without the data version. The ten-minute test is
the criterion: a colleague should not need to ask which notebook was last run.
