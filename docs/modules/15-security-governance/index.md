# 15 · Security, privacy, governance, fairness, and responsible deployment

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Advanced | 14 hours | [09](../09-model-registry/index.md), [10](../10-model-serving/index.md), [11](../11-docker-containers/index.md) | Recommended |

A prediction service is an attack surface, a repository is a place where credentials leak, and a model that is accurate on average can be systematically worse for the people with the least power to complain.

None of this is exotic. The most common real incidents are a committed token, an unpatched dependency, and a subgroup the evaluation never separated out. This module teaches you to find those three before someone else does, and to write down what you cannot fix.

## What you will be able to do

- Threat-model a prediction service and rank findings by exploitability and impact.
- Keep secrets out of code and history, detect a leak, and rotate a credential.
- Scan dependencies for known vulnerabilities and interpret the result without panic.
- Measure error and selection rates across meaningful groups, and explain what the metric does not prove.
- Write a model card a non-specialist can use to judge whether to trust the system.
- Describe the governance evidence an auditor would ask for, and the data you should never collect.

## Start here

1. Read [Concepts](concepts.md) sections 1–6: threat modelling, secrets, least privilege, supply chain, privacy, and lineage.
2. Read the [worked example](worked-example.md): a review that finds six problems in a working service, and a fairness table where the aggregate looks acceptable and one group does not.
3. Do the [lab](lab.md): threat-model the ETA API, measure disparity, and write a model card that states a limitation plainly.

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives, evidence, and the release-review checklist |
| [Concepts](concepts.md) | Threats, secrets, privilege, supply chain, privacy, fairness, governance |
| [Worked example](worked-example.md) | A six-finding review and a measured disparity analysis |
| [Guided lab](lab.md) | Threat model, fairness audit, model card, and a rotation rehearsal |
| [Independent challenge](independent-challenge.md) | Three mitigations, one recommendation, with residual risk |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Leaked keys, noisy scanners, unstable group metrics |
| [References](references.md) | Threat modelling, privacy, fairness, and governance sources |

## What you produce

- A STRIDE table for the ETA service with trust boundaries, assets, and ranked mitigations.
- A secret-scanning result with the finding redacted, plus a rotation and verification procedure.
- A dependency report that distinguishes exploitable findings from noise.
- A fairness table with row counts, selection rate, TPR, FPR, and an explicit caveat.
- A model card with intended use, limitations, prohibited use, and monitoring.
- A one-page incident-response note for a leaked credential.

## The reference result

The fairness audit in [fairness.py](https://github.com/nadeem-majeedch/MLOps/blob/main/examples/modules/15-security-governance/fairness.py) trains the support-risk model on the synthetic 400-row dataset and evaluates the 100-row test split at a 0.50 threshold. The aggregate looks reasonable:

```text
overall         selection 0.250  TPR 0.643  FPR 0.097  precision 0.720
```

Split by prior GPA band, the same model is not uniform:

| Group | Rows | Positives | Selection rate | TPR | FPR |
|---|---|---|---|---|---|
| high | 24 | 0 | 0.000 | — | 0.000 |
| low | 24 | 18 | 0.917 | 0.944 | 0.833 |
| mid | 52 | 10 | 0.058 | 0.100 | 0.048 |

The high band has no positive labels in this test split, so TPR is undefined, not zero. The low band is selected almost every time. Before concluding anything about fairness, you have to ask whether the grouping attribute is a legitimate need variable or a proxy for it — here the generator uses the band to produce the label, so the model has learned a near-deterministic relationship. That is a property of the synthetic data, and exactly the kind of thing an analyst must notice before quoting a ratio.

## What this module is not

It is not a law course, a compliance certification, or a guarantee that a checklist makes a system ethical. It teaches the engineering evidence that a review needs: what data you hold, who can reach it, what the model does to different groups, and what you would do at 2 a.m. if a key leaked.

## Next

Module 16 scales the system, which multiplies both the attack surface and the cost of a poor access model. The capstone requires these artefacts, and Module 17's incident simulation includes a credential and a schema failure as possible faults.
