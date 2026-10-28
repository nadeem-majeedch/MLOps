# 14 · Model monitoring, drift detection, and retraining

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Advanced | 18 hours | [06](../06-experiment-tracking/index.md), [09](../09-model-registry/index.md), [13](../13-orchestration/index.md) | Essential |

Everything up to this point happens before the model meets the world. This module is about what happens afterwards: the world changes, and the model does not.

The central discipline is telling three different situations apart — the inputs changed, the relationship changed, the service broke — because they call for different responses, and because the most common mistake is to retrain on the first one.

## What you will be able to do

- Log predictions in a form that supports joining to delayed labels.
- Choose a reference window and compute feature drift against it.
- Explain why a drift alert is not evidence that accuracy fell.
- Measure performance when labels arrive late, and say what to do before they do.
- Set thresholds that produce a manageable number of alerts, and justify them.
- Decide between investigating, retraining, and rolling back, with evidence.
- Write a runbook that someone else can follow at 3 a.m.

## Start here

1. Read [Concepts](concepts.md) sections 1–6: logging, reference windows, drift types, metrics.
2. Read the [worked example](worked-example.md): four batches, one with severe drift and *better* accuracy, one with a 33% error increase.
3. Do the [lab](lab.md): instrument the service, backtest four batches, and write the decision.

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives and the monitoring-review criteria |
| [Concepts](concepts.md) | Logging, drift, metrics, thresholds, decisions, rollback |
| [Worked example](worked-example.md) | PSI values, performance changes, and four decisions |
| [Guided lab](lab.md) | Log predictions, backtest batches, tune thresholds |
| [Independent challenge](independent-challenge.md) | A monitor that survives a false alarm |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Noisy alerts, missing labels, silent failures |
| [References](references.md) | Drift detection, monitoring, and retraining literature |

## What you produce

- A prediction log with a schema, a retention rule, and no personal data.
- A drift report per batch: per-feature PSI, severity, and the reference window used.
- A performance report that states when labels arrived and how many rows were labelled.
- A thresholds table with the false-positive cost stated.
- A decision record: investigate, retrain, or roll back — with the evidence.

## The reference run

Four 300-row batches were compared with the 896-row training reference. The results are the module's central lesson:

| Batch | Drift | MAE vs 2.7686 | Decision |
|---|---|---|---|
| Normal | none | 2.553 (−7.8%) | no action |
| Zone mix shifted | distance PSI 0.598, zone PSI 0.622 | **1.821 (−34.2%)** | investigate drift, no retrain |
| Rainy peak | weather PSI 1.379 | 2.955 (+6.7%) | investigate |
| Storm | weather PSI 2.880, traffic PSI 0.311 | 3.683 (+33.0%) | retrain review |

The second row is why this module exists: severe drift, better accuracy. Retraining on a drift alert alone would have replaced a model that was doing well.

## Next

Module 15 covers security and governance, including the data-protection obligations that constrain what you may log in the first place.
