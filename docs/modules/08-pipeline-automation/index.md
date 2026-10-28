# 08 · Pipeline automation and workflow dependencies

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Intermediate | 12 hours | [05](../05-reproducible-training/index.md), [07](../07-testing-ml-systems/index.md) | Recommended |

A pipeline that needs six remembered commands is not a pipeline. It is a set of six commands that happen to work when the person who wrote them is present.

This module turns the stage graph from Module 05 into an operation: one command, declared inputs, visible failure, and a rerun that does the minimum correct work. The hard part is not running stages. It is knowing what a rerun should do before you run it, and what state you are in when a stage dies halfway.

## What you will be able to do

- Run the whole pipeline with one documented command, from any working directory.
- Declare dependencies so a partial rerun is correct, not merely faster.
- Read a failure: which stage failed, what it left behind, and what a rerun will reuse.
- Design failures that stop the pipeline instead of warning and continuing.
- Use commit-time hooks to reject oversized or malformed changes before they exist.
- Measure stage cost and say where the wall-clock time actually goes.

## Start here

1. Read [Concepts](concepts.md) sections 1–5, which define stages, cache keys, and failure propagation.
2. Read the [worked example](worked-example.md): one fresh run, one cached run, one parameter change, one failure, one recovery — all with real output.
3. Do the [lab](lab.md): you build the single command, break the pipeline on purpose, and write the recovery log.

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives and the evidence review criteria |
| [Concepts](concepts.md) | Stage graphs, cache keys, exit codes, failure modes, resumability |
| [Worked example](worked-example.md) | The reference pipeline's real runs, including a failed stage |
| [Guided lab](lab.md) | One command, a deliberate failure, and a measured rerun |
| [Independent challenge](independent-challenge.md) | Cut the runtime in half without changing the outputs |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Cache misses, wrong working directories, stuck locks |
| [References](references.md) | DVC, pre-commit, and exit-code documentation |

## What you produce

- `dvc.yaml` and `dvc.lock` covering at least four stages.
- `run_pipeline.py` (or an equivalent entry point) with preflight checks, logging, and meaningful exit codes.
- A failure-recovery log: what failed, what the rerun reused, and how you knew.
- A timing table measured on your machine.
- `.pre-commit-config.yaml` with at least three hooks, and one recorded rejection.

## The reference run

Every number in this module comes from the course project, `raviride-eta`, on the dataset from Module 04 (1,200 rows, 896 training / 304 test). The reference pipeline completes a forced full run in about 11 seconds on a laptop CPU; the cached run takes about 1.5 seconds, almost all of it DVC's own start-up. Your timings will differ; the ordering of stages and the reuse behaviour will not.

## Next

[Module 09](../09-model-registry/index.md) takes the artefact this pipeline produces and gives it a version, an alias, and a promotion gate.
