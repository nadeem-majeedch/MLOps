# Concepts · Watching a model after it ships

## 1. Four layers, four questions

A model in production can fail at four levels. Monitoring each answers a different question:

| Layer | Question | Example signal |
|---|---|---|
| **Service** | Is it up and fast? | Error rate, p95 latency, 5xx count |
| **Data** | Is the input what we trained on? | Feature distributions, null rate, unseen categories |
| **Model** | Are the predictions still accurate? | MAE on labelled outcomes, error by slice |
| **Business** | Is the product still working? | Cancellations, manual overrides, support tickets |

The layers fail in order: data changes first, predictions degrade later, the business notices last. Monitoring only the service tells you the process is alive while it confidently returns worse numbers.

## 2. Prediction logging: the raw material

You cannot monitor what you did not record. A prediction log is one row per prediction (or per sampled prediction):

```json
{"logged_at":"2026-10-24T03:27:52+00:00","batch":"storm","trip_id":"T000095",
 "prediction":15.05,"model_version":"1"}
```

A production log usually also contains the input features, a request ID, latency, and enough context to join with the eventual outcome. Four decisions shape it:

**What to log.** The features used, the prediction, the model version, and a join key. Logging the *raw request* is often better than logging engineered features: you can recompute features later if the code changes, whereas a stored derived value freezes one interpretation.

**How much.** Full logging is expensive at scale; sampling (1–10%) is common, but sampling must be unbiased and the sample rate must be recorded, or slice metrics become nonsense.

**How long.** Long enough to cover the label delay and the review cycle. If outcomes arrive after 30 days, a 7-day retention makes performance monitoring impossible.

**What not to log.** Personal data that is not needed, full request bodies with free text, credentials, or anything that turns the log into a privacy liability. Module 15 covers the obligations; the design decision belongs here.

The join key is the part teams forget. If `trip_id` is not stored with the prediction, the eventual `duration_min` cannot be attached to it, and performance monitoring becomes impossible without re-running the model.

## 3. Reference data and reference windows

Every drift metric compares **current** data with a **reference**. The choice of reference determines what the metric means:

| Reference | Answers | Risk |
|---|---|---|
| Training set | "Is production like training?" | Drifts slowly into meaninglessness as the world moves |
| Last N days | "Did anything change recently?" | A gradual shift is invisible; a seasonal cycle alerts twice a year |
| Same period last year | "Is this season unusual?" | Needs a year of history; misses structural change |
| A fixed "golden" batch | "Is production like the batch we validated on?" | Stale by design |

The reference project uses the training features (896 rows) because the question is "is this batch like what the model learned from?". That is the right default immediately after deployment. After a year, the more useful question is usually "is this week like last week", with the training reference kept for a slower sanity check.

Whatever you choose, write it down, version it, and record its row count. A PSI value without a reference is a number without a meaning.

## 4. Three kinds of drift

**Covariate shift** — the distribution of inputs changes, but the input→output relationship does not. More trips in central zones, longer distances, a new weather mix. The model may still be accurate; it is being asked different questions from the same syllabus.

**Label shift** — the distribution of the target changes while the inputs' relationship stays similar. Average trip duration rises because the city is busier. A model predicting the old average is biased, and the fix is often recalibration or retraining on recent data.

**Concept drift** — the relationship itself changes. A new ring road makes the same distance take less time; a pricing change alters driver behaviour. This is the drift that most reliably degrades a model, and the hardest to detect without labels.

**Schema drift** is not statistical at all: a column renamed, a unit changed, a category added. It usually appears as a pipeline failure or an unseen-category spike, not as a gradual shift, and it is the one to catch first because it is a defect rather than a change in the world.

## 5. Metrics, and what they do not say

**Population Stability Index (PSI)** compares two distributions over bins:

```text
PSI = Σ (P_current(bin) − P_reference(bin)) × ln(P_current(bin) / P_reference(bin))
```

Rules of thumb from credit-risk practice: below 0.10 stable, 0.10–0.25 moderate, above 0.25 significant. They are conventions, not laws — the right threshold depends on the feature, the sample size, and the cost of a false alarm.

Practical caveats:

- **Bin edges come from the reference.** Quantile bins of a 896-row reference are coarse; on a 300-row batch, each decile holds 30 rows and the estimate is noisy.
- **PSI is sensitive to bin count.** Ten bins is conventional; five and twenty tell different stories.
- **Categorical PSI** works the same way over categories, but a new category with one occurrence can produce a large value. Require a minimum count before alerting.
- **PSI says "different", not "worse".** It has no access to the target.

Alternatives: the **Kolmogorov–Smirnov** statistic for numeric features (more sensitive to location/shape, needs a library), **chi-square** for categorical, and **Jensen–Shannon divergence** (symmetric, bounded). They disagree at the edges; pick one, document it, and use it consistently.

The reference implementation computes PSI only, so the module's numbers are reproducible with NumPy and pandas alone.

## 6. Performance with delayed labels

Accuracy needs the truth, and the truth arrives late: a trip ends, the fare settles, a cancellation is confirmed, a label is adjudicated. Until then:

- **Drift metrics work immediately** because they need only the inputs.
- **Performance metrics work only on the labelled subset**, which may be biased (labels arrive faster for some slices).
- **Proxy signals** fill the gap: prediction distribution, override rate, the share of predictions outside a plausible band, downstream conversion.

A performance report must state:

- the window,
- the number of predictions,
- the number labelled,
- the label delay,
- the metric computed on the labelled subset.

"MAE is 3.1" without "on 18% of the traffic, labels from 12 October" is a number that invites the wrong decision.

## 7. Slicing is not optional

An aggregate metric can hide a collapse in one population. The storm batch in the reference run had overall MAE 3.683 (+33%) and a Z07 slice at 10.384 minutes against a baseline of 5.17 — the zone where users were most affected.

Monitor slices that correspond to:

- **product populations** (zones, customer tiers),
- **known weak spots** from Module 06's analysis,
- **high-volume segments** where a small regression touches many people,
- **small segments** with a lower alert threshold and a higher minimum sample size, because noise is larger.

Report row counts beside every slice metric. A slice with 19 rows and a 10-minute MAE is a signal to look, not a certainty.

## 8. Thresholds, alert fatigue, and the cost of a page

A threshold encodes a trade-off between missing a problem and waking someone up. Both have costs, and neither is zero.

Three practices that keep alerts useful:

1. **Multiple signals for a page.** Drift alone opens a ticket; drift plus a performance breach (or a business KPI drop) pages. In the reference run, `rainy_peak` had a severe weather PSI and only a 6.7% error increase — a ticket, not a page. `storm` had drift and +33% error — a page.
2. **Minimum sample sizes.** Do not alert on 12 rows. State the minimum, and suppress (with a visible "insufficient data" state) rather than computing a noisy value.
3. **A review cadence.** Every quarter, count alerts, how many led to action, and how many were false. A channel with a 5% action rate is a channel people mute.

The reference thresholds are deliberately simple: PSI ≥ 0.25 alerts per feature, MAE ≥ 15% above baseline alerts on performance. The lab asks you to justify them for your product, not to copy them.

## 9. The decision: investigate, retrain, or roll back

A monitor exists to support a decision. The reference implementation returns one of three values:

| Decision | When | First action |
|---|---|---|
| `no_action` | No alert; metrics inside bands | Record and continue |
| `investigate_drift` | Drift without a performance breach | Check data quality, slice metrics, and recent deploys |
| `retrain_review` | Performance breach beyond tolerance | Confirm labels, quantify the slice, prepare a candidate, run the gate |

Notice what is missing: "retrain automatically". Automatic retraining on a drift signal is a common and expensive mistake, because drift can accompany **better** performance. The reference `zone_shift` batch had distance PSI 0.598 and zone PSI 0.622 — both far above the alert band — and MAE **1.821, 34% better than baseline**. A pipeline that retrained on that alert would have replaced a model that was doing well with one trained on a different population.

Before retraining, answer four questions:

1. **Is the metric real?** Check label coverage, label delay, and whether the batch is representative.
2. **Is the model at fault?** Rule out a pipeline defect, a stale artifact, or a unit bug. Retraining a broken feature pipeline reproduces the bug with fresher data.
3. **Is the population the one we serve?** A batch dominated by an unusual event (a storm, a holiday) may not justify a new model.
4. **Will the candidate be evaluated on the right data?** Training on the storm and testing on the storm proves nothing. Keep a hold-out from a normal period, and add a slice for the event if it matters.

## 10. Retraining is a release, not a refresh

A retrained model goes through the same path as any other candidate:

- it is registered with a version, a data hash, and a commit;
- it passes the promotion gates (Module 09), including slice and provenance checks;
- it is validated on recent labelled data, not only on the old test split;
- it is deployed gradually where possible (shadow, canary), with the previous version retained for rollback.

The gate matters more here than anywhere else. A retrain triggered by degraded performance will often *look* better on the data that triggered it, because that data is now in the training set. Evaluation on a fresh, later window is the only honest test.

## 11. Rollback versus retrain

| Situation | Rollback | Retrain |
|---|---|---|
| A new model version degraded after release | Yes, immediately | Later, after the cause is understood |
| Data drift with a working model | No; the old model is the problem | Candidate, gated |
| Pipeline or feature bug | Yes, to the last good artifact | No; fix the pipeline first |
| Registry alias points at a bad version | Yes, one command (Module 09) | Irrelevant until rollback is done |
| Schema change broke the input | No; both versions fail | No; fix the contract |

Rollback restores service; retraining changes the model. Doing the second while the first is needed wastes the incident window.

## 12. Monitoring the monitor

A monitor that has never been tested is a dashboard with good intentions. Two cheap tests:

- **Inject a known shift.** Generate a batch with 80% rain and confirm the weather PSI alerts, the performance metric moves, and the decision changes. The reference implementation does exactly this with four synthetic batches.
- **Replay history.** Take last month's batches, compute the metrics, and ask whether the alerts correspond to problems someone remembers. If the monitor fires constantly on normal weeks, the thresholds are wrong; if it never fires, the reference or the metric is wrong.

Record both tests in the runbook. They are the evidence that the alert means something.

## 13. Feedback loops

Monitoring data can change the system it measures:

- **Retraining on served traffic** teaches the model its own biases: if it under-predicts long trips, those trips get fewer drivers, and the next dataset contains fewer long trips.
- **Acting on alerts** changes behaviour: blocking a zone after an alert removes the zone from the data, and the next model never learns it.
- **Label collection** is selective: only some outcomes are observed, and the missing ones are rarely random.

These are not reasons to stop monitoring; they are reasons to keep a stable evaluation set outside the production loop and to audit which populations are disappearing from the data.

## 14. What belongs in the runbook

One page, written for someone who is not you:

1. What the service does and which model is live (alias and version).
2. The dashboard links and the meaning of each panel.
3. The alert thresholds and which ones page.
4. The first five checks: model version, input schema, null rate, slice metrics, recent deploys.
5. How to roll back (the exact command, from Module 09).
6. Who can approve a retrain, and the link to the gate.
7. The known limitations: label delay, unmonitored slices, seasonal effects.

If the runbook cannot be followed at 3 a.m. by a tired person, it is documentation for the author, not for the team.
