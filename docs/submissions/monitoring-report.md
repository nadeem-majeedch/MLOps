# Monitoring report template

> Copy this for a weekly report or a replayed batch. One or two pages. The
> discipline is to separate what you observed from what you concluded.

---

# Monitoring report: *week or batch identifier*

| | |
|---|---|
| **Period** | YYYY-MM-DD to YYYY-MM-DD |
| **Model version** | *v7, alias `champion`* |
| **Predictions served** | *12,480* |
| **Labels matured** | *9,120 (73%)* |
| **Reference window** | *training period, hash a1b2…* |
| **Report owner** | *name* |

---

## 1. What moved (observations)

### Inputs

| Feature | Reference mean | Period mean | PSI | Status |
|---|---|---|---|---|
| distance_km | 7.8 | 8.1 | 0.06 | stable |
| hour | 13.2 | 13.0 | 0.03 | stable |
| zone_Z08 share | 0.12 | 0.19 | 0.31 | drift |

### Predictions

| Signal | Reference | Period | Change |
|---|---|---|---|
| Mean prediction | 18.4 min | 20.1 min | +9% |
| Share > 40 min | 4.1% | 6.8% | +2.7 pts |
| Fallback responses | 0 | 34 | new |

### Outcomes, where labels exist

| Metric | Baseline | Period | Difference | Sample |
|---|---|---|---|---|
| MAE | 3.42 | 3.51 | +0.09 | 9,120 |
| MAE, long trips | 5.80 | 6.40 | +0.60 | 1,930 |
| p95 abs error | 8.4 | 9.1 | +0.7 | 9,120 |

---

## 2. What it means (interpretation)

*Three short paragraphs. Keep observation and inference apart.*

**Inputs.** Zone Z08's share nearly doubled. That is consistent with the new
promotion in that district; it is not evidence that the model is wrong.

**Predictions.** The mean prediction rose with the input mix. The rise in
long-prediction share is partly explained by the mix, not by a model change.

**Outcomes.** MAE rose by 0.09 overall, within the ±0.15 week-to-week range we
recorded before this period. The long-trip slice rose by 0.60, which is larger
than its usual variation (±0.25) and worth investigating.

---

## 3. Alerts

| Alert | Fired? | Threshold | Owner | First action | Closed |
|---|---|---|---|---|---|
| Input drift, any feature | Yes, Z08 | PSI > 0.25 | Data team | Confirm the district promotion | Yes, explained |
| Long-trip MAE | Yes | > 6.0 | ML team | Compare error by zone within long trips | No |
| Error rate | No | > 2% | Service team | Check `/model-info` and logs | — |

*An alert that fired and was closed needs a reason. "Looked fine" is not one.*

---

## 4. Decision

- [ ] No action; continue monitoring.
- [ ] Investigate the long-trip slice by zone; report next week.
- [ ] Open a release candidate; gate against the current champion.
- [ ] Roll back; reason below.

**Reason and evidence:** the long-trip regression is concentrated in Z08, where
the new promotion changed the trip mix. Before retraining, confirm whether the
degradation is a mix effect or a genuine error increase by comparing within-zone
error.

**What would change this decision:** if within-zone long-trip error is flat, this
is composition, not degradation, and retraining is premature.

---

## 5. Data quality and operations

| Check | Result |
|---|---|
| Prediction log completeness | 99.8% of requests |
| Missing features at serving | 0 |
| Label maturity | 73%; long trips mature slower |
| Latency p95 | 84 ms (budget 150) |
| Incidents | None |

---

## 6. Next period

| Watch | Why | Trigger |
|---|---|---|
| Z08 within-zone MAE | Separate mix from degradation | > 6.0 for two weeks |
| Label maturity | Conclusions weaken if it falls | < 60% |
| New zones in requests | Unknown categories are ignored by the encoder | Any new category |

---

## Checklist

- [ ] Observations and interpretations are separate sections.
- [ ] Every metric has a sample size.
- [ ] Data drift and accuracy are not conflated.
- [ ] Every alert has an owner, a first action, and a closing reason.
- [ ] The decision names what evidence would reverse it.
- [ ] At least one limitation of this report is stated.

---

## Limitation to state explicitly

This report cannot say whether accuracy *will* fall. It describes what moved and
what the matured labels show. A claim about the future needs a monitoring plan and
a threshold, not a correlation.
