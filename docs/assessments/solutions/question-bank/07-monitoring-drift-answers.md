# Answer key · Question bank 07

[Back to the questions](../../question-bank/07-monitoring-drift.md)

---

## Section A (1 mark each)

**A1 — b.** PSI is a statement about the input distribution. Accuracy (a) needs
labels; nothing here implies a retrain (d) — the inputs may have moved into a
region the model handles well.

**A2 — b.** The relationship between the same input and the outcome changed.
Data drift (a) would be a change in the applicant mix, not in default behaviour
for a given applicant.

**A3 — b.** With delayed labels, the metric that matters is unavailable exactly
when you need it. Early warning has to come from inputs, proxies, and process
signals, each with its own uncertainty.

**A4 — a.** Either the threshold exceeds the team's capacity to act, or the alert
lacks an owner and a first diagnostic step. A correct alert that nobody can act on
is a design failure, not an accuracy problem.

## Section B (3 marks each)

**B1.** Drift is a change in *inputs*; accuracy is a change in *outcomes*. The
model may be robust to the new inputs, or degrade. To prove decline you need
labels for the shifted period, a metric computed on them, and the same operating
threshold as the baseline — otherwise you have a hypothesis, not a finding.

**B2.** Input distribution (detects movement, cannot say whether predictions are
right); prediction distribution (detects a change in outputs, cannot distinguish
a model change from an input change); operational signals — latency, error rate,
fallback counts, missing features (detect process failures, not model quality);
proxy outcomes such as downstream conversion or override rate (correlate with
quality, can be confounded). Two marks for three signals, one for the limits.

**B3.** Justified: a labelled slice shows a material drop; a data defect is found
and corrected; the population changed in a way the model was not trained for and
you have labels proving the gap. Not justified: input drift alone, a competitor
announcing a new model, or a metric that moved within its known noise band.

## Section C (4 marks each)

**C1.** The shift may be benign — for example a route-length mix change the model
handles because it learned distance effects — or accuracy may have been measured
on a different sample, or the labels may have matured for an easier subset. Next:
score the shifted batch, compare predictions and errors by segment with labels,
and check whether the shift is inside the training range. Do not retrain on the
strength of PSI alone.

**C2.** With a rolling reference, each comparison is against yesterday, so slow
drift accumulates invisibly and the PSI value never looks large. Fix: keep a
frozen reference from the training period (hashed), and add a second view against
a rolling window if you want short-term movement. Record which reference was used
in every report.

## Section D (9 marks)

| Element | Marks | What it looks like |
|---|---|---|
| Signals | 2 | Input drift per sensor feature; prediction rate and score distribution; alert-to-inspection outcome; matured 7-day failure labels; data freshness |
| Thresholds | 2 | PSI reference frozen at training time, threshold justified by the cost of inspection vs missed failure; a minimum batch size; an alert only when two consecutive windows breach |
| Human review | 2 | Every alert reviewed by the maintenance lead; false alarms recorded with a reason; a weekly review of the alert list and its precision |
| Retraining trigger | 2 | Matured-label recall or precision below the agreed floor on a sufficient sample, or a confirmed new operating regime — not input drift alone |
| Rollback | 1 | Previous model version kept, with a comparison on the same matured window and a named decision owner |

A strong answer notes that acting on an alert changes the outcome data (crews
inspect flagged machines), so the monitoring report must say the observed failure
rate is affected by intervention. That selection effect is the difference between
a good answer and a textbook one.
