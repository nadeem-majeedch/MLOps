# 05 · Reproducible training and pipeline design

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Intermediate | 16 hours | [04](../04-data-quality-versioning/index.md) | Essential |

A model you cannot rebuild is a model you cannot debug, compare, or trust. This module turns the four scripts from Module 03 into a **pipeline**: stages with declared inputs, outputs, and parameters, executed by DVC in dependency order and cached by content.

The immediate payoff is speed - a second run does no work - and the long-term payoff is evidence: every metric can be traced to a stage graph, a dataset hash, and a parameter file.

## What you will be able to do

- Write a deterministic training entry point that produces the same artefact twice.
- Separate feature engineering into a reusable transformer used by both training and serving.
- Express training as stages with declared inputs, outputs, and parameters.
- Explain cache invalidation: why one parameter change reruns only two stages.
- Record runtime and resource use per stage.

## Start here

1. Read [Concepts](concepts.md) sections 1–3. Determinism first; pipelines are worthless on top of randomness you cannot control.
2. Copy the `dvc.yaml` from the [worked example](worked-example.md) and run `dvc repro` on your own project.
3. Do the [lab](lab.md), including the parameter change and the DAG.

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives and the reproducibility evidence list |
| [Concepts](concepts.md) | Determinism, stages, cache keys, invalidation, artefacts |
| [Worked example](worked-example.md) | A four-stage pipeline, run fresh, cached, and invalidated |
| [Guided lab](lab.md) | Build the pipeline, prove determinism, add a feature |
| [Independent challenge](independent-challenge.md) | A two-run reproducibility report, including what remains non-deterministic |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Caching surprises, stage failures, hash mismatches |
| [References](references.md) | DVC pipeline reference and scikit-learn pipeline docs |

## What you produce

- `dvc.yaml` with four stages and `dvc.lock` committed.
- `params.yaml` covering every human-chosen value, including the feature set.
- A metrics file with overall and slice metrics.
- A recorded fresh run, cached run, and invalidation run.
- A two-run comparison proving identical metrics and artefact hashes.
- An exported DAG.

## Next

[Module 06 · Experiment tracking](../06-experiment-tracking/index.md) records the runs this pipeline produces, so comparisons survive beyond a terminal scrollback.
