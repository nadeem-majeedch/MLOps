# Experiment record template

> Copy one per experiment into `docs/experiments/YYYY-MM-DD-slug.md`. A record
> written after the result is a story; a record written before it is evidence.

---

# Experiment: *short name*

| | |
|---|---|
| **Date** | YYYY-MM-DD |
| **Run ID** | *from the tracker, never "local"* |
| **Owner** | *your name* |
| **Code version** | *commit hash* |
| **Data version** | *hash or DVC tag* |
| **Environment** | *Python, key library versions, or image digest* |
| **Related** | *previous run, issue, or hypothesis* |

---

## 1. Hypothesis

*One sentence, written before the run, that could be wrong.*

> Adding a log-distance feature will reduce MAE for long trips without changing
> short-trip error, because the current model under-weights distance above 15 km.

## 2. Change

*Exactly one change relative to the named baseline. If you changed two things, you
have two experiments and one confound.*

| | Baseline | This run |
|---|---|---|
| Features | distance, zone | distance, zone, **log_distance** |
| Model | random forest, 200 trees | same |
| Seed | 42 | 42 |
| Data | `trips@v3` | `trips@v3` |

## 3. Result

| Metric | Baseline | This run | Difference | Meaningful? |
|---|---|---|---|---|
| MAE (all) | 3.42 | 3.11 | −0.31 | Yes; outside the ±0.08 seed range |
| MAE (> 15 km) | 5.80 | 4.65 | −1.15 | Yes |
| MAE (≤ 5 km) | 1.90 | 1.93 | +0.03 | Within noise |
| p95 abs error | 8.4 | 7.9 | −0.5 | Yes |

*State how you know what "meaningful" means: a seed sweep, a confidence interval,
or a stated tolerance. A difference with no noise estimate is a guess.*

## 4. Slices

| Slice | Rows | Baseline MAE | This run MAE | Note |
|---|---|---|---|---|
| Peak hours | 180 | 3.9 | 3.4 | |
| Rain | 96 | 4.4 | 4.1 | |
| Zone Z08 | 74 | 4.8 | 3.9 | |

*At least two slices, with row counts. A slice under 30 rows is reported but not
used to decide.*

## 5. Interpretation

*What the result supports, and what it does not. Two short paragraphs.*

Supported: the feature helps long trips, as hypothesised, and does not harm short
ones beyond noise.

Not supported: that the model is better for rain; the slice moved but the interval
overlaps the baseline. Do not claim it.

## 6. Decision

- [ ] Promote to candidate
- [ ] Keep as a variant, revisit
- [ ] Reject

**Reason:** *one sentence, citing the numbers above and the selection rule.*

## 7. Artifacts

| Item | Location |
|---|---|
| Model | `runs/<run-id>/model.joblib` |
| Metrics | `runs/<run-id>/metrics.json` |
| Plot | `runs/<run-id>/residuals.png` |
| Log | `runs/<run-id>/train.log` |

## 8. What surprised you

*One honest sentence. This is the part that makes a record useful six months
later, and the part most often omitted.*

---

## Checklist

- [ ] The hypothesis was written before the run.
- [ ] Exactly one change from a named baseline.
- [ ] Every metric has a data version and a run ID.
- [ ] At least two slices with row counts.
- [ ] Noise or tolerance is stated, not assumed.
- [ ] The decision cites the numbers, not the effort.
- [ ] Anything not supported is listed under interpretation.
