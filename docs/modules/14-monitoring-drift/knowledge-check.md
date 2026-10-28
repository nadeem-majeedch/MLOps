# Knowledge check · Module 14

## Questions

**1.** A batch has PSI 0.6 on `pickup_zone` and its MAE is 34% better than baseline. What do you do, and why is "retrain" wrong?

**2.** What is the difference between covariate shift, label shift, and concept drift? Which one most reliably degrades a model without labels?

**3.** Why does a prediction log need a join key, and what happens to performance monitoring without one?

**4.** Your monitor compares production with the training set. Two years later, what has gone wrong with that reference, and what would you use instead?

**5.** Labels arrive 14 days late. What can you alert on today, and what must wait? Give one proxy signal for the waiting period.

**6.** PSI is 0.31 for `traffic_index` on a batch of 40 rows. Why should that not page anyone, and what would you change?

**7.** A storm causes a +33% MAE increase for one week, then conditions return to normal. The model is unchanged. Do you retrain? Defend either answer.

**8.** You retrain on data from the storm week and evaluate on a held-out sample from the same week. Why is the resulting metric misleading?

**9.** When is rollback the right response, and when is retraining the right response? Give one example of each.

**10.** What does it mean to "monitor the monitor", and name one test that would reveal a useless drift alert.

---

## Answers and reasoning

**1.** Investigate the change in population; do not retrain. The model is performing better on this batch, so replacing it would trade a working model for one trained on a different mix. Check whether the zone mix change is persistent and whether it reflects a product change (new service area, campaign); if it persists, the *evaluation* set should be updated, not necessarily the model.

**2.** **Covariate shift**: input distribution changes, relationship unchanged (more central-zone trips). **Label shift**: target distribution changes (longer trips overall) while the relationship is roughly stable. **Concept drift**: the input→output relationship changes (a new road makes the same distance faster). Concept drift most reliably degrades a model, and it is the hardest to detect without labels because the inputs may look normal.

**3.** The join key links each prediction to the outcome that eventually arrives. Without it, you cannot compute error on production traffic — only on a re-scored dataset, which is not the same thing — and slice analysis by real population becomes impossible.

**4.** The world has moved; production no longer resembles the training distribution for legitimate reasons, so every PSI is large and the signal is useless. Use a rolling reference (last 30–90 days) for "what changed recently", keep the training reference for a slow sanity check, and document both.

**5.** Today you can monitor feature distributions, prediction distributions, schema violations, unseen categories, latency, and business proxies (overrides, cancellations). Performance must wait for labels. A proxy: the share of predictions outside a plausible band, or the override rate by zone.

**6.** Forty rows cannot support a stable PSI estimate on a 10-bin reference; a single row moves a bin by 2.5 percentage points. Apply a minimum sample size and report `insufficient_data`, or use fewer bins and a coarser threshold. Paging on it trains people to ignore the channel.

**7.** Either is defensible if argued. Not retraining: the event was transient, the model returns to baseline, and a storm-trained model may be worse in normal conditions. Retraining: storms are becoming frequent, the error during them is unacceptable for users, and a candidate can include storm-like data while still being evaluated on normal and storm windows. What is not defensible is retraining silently and evaluating only on storm data.

**8.** The evaluation measures how well the model fits the conditions it was just trained on. It cannot show whether the model generalises to the next normal week or the next storm. Use a later window, or hold out entire days/events, and keep the old test set as a regression check.

**9.** Rollback: a newly promoted version degrades service, or the artifact is wrong; restore the previous version immediately (Module 09), then investigate. Retrain: the data relationship has changed and the current model is systematically wrong in a way a new model can fix, with a candidate that passes the gates. Rollback is incident response; retraining is a release.

**10.** It means testing the alerting system itself. Inject a known shift (80% rain, high traffic) and confirm the expected alert fires and the decision changes; or replay a month of history and check that alerts correspond to problems people remember. A monitor that never fires, or fires every day, fails this test.
