# 06 · Experiment tracking and model evaluation using MLflow

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Intermediate | 14 hours | [05](../05-reproducible-training/index.md) | Essential |

The pipeline produces a model and a metrics file. It cannot answer the question the team actually asks: *which of these six attempts should we ship, and what is wrong with it?* Answering that needs records that survive the terminal, and an evaluation that looks inside the aggregate.

This module adds both: MLflow for run records, and slice-level evaluation for decisions.

## What you will be able to do

- Record parameters, metrics, artefacts, and the dataset version for every run.
- Compare runs and justify a choice on evidence rather than one number.
- Design an evaluation that includes slice metrics, not only an aggregate.
- Recognise when a model has been selected by overfitting the evaluation set.
- Establish a baseline that candidates must beat.

## Start here

1. Read [Concepts](concepts.md) sections 1–3.
2. Run the six tracked experiments from the [worked example](worked-example.md) and read the comparison table before reading the commentary.
3. Do the [lab](lab.md), then write the evaluation report in the [independent challenge](independent-challenge.md).

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives and the evaluation evidence list |
| [Concepts](concepts.md) | Runs, comparison, slices, baselines, metric choice |
| [Worked example](worked-example.md) | Six real runs, compared and interpreted |
| [Guided lab](lab.md) | Track six experiments, then analyse the winner's weaknesses |
| [Independent challenge](independent-challenge.md) | An evaluation report that would stop a plausible model shipping |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Tracking store, UI, and artefact problems |
| [References](references.md) | MLflow documentation and evaluation sources |

## What you produce

- An MLflow experiment with six runs, each with parameters, metrics, tags, and a model artefact.
- A comparison table exported from `mlflow.search_runs`.
- A slice analysis covering zones and peak hours.
- A recorded baseline (`baseline.json`) and a written justification for it.
- An evaluation report with an explicit recommendation.

## Next

[Module 07 · Testing ML systems](../07-testing-ml-systems/index.md) turns the evaluation criteria into tests that run without a human reading a table.
