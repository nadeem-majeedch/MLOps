# 12 · CI/CD with GitHub Actions

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Intermediate | 16 hours | [07](../07-testing-ml-systems/index.md), [09](../09-model-registry/index.md), [11](../11-docker-containers/index.md) | Essential |

Every check in this course so far depends on someone remembering to run it. The test suite passes because a person typed `pytest`. The model gate blocks a regression because a person compared two JSON files. That is a process, not a control.

Continuous integration turns those checks into conditions of merging. Continuous delivery turns a passing build into a deployable artifact. Neither makes the checks better; both make them unavoidable.

## What you will be able to do

- Write a workflow with a minimal trigger, least-privilege permissions, and a pinned toolchain.
- Split fast feedback (lint, tests) from slower evidence (pipeline, model gate) and explain the ordering.
- Cache dependencies without caching the result you are trying to verify.
- Pass secrets to a step without putting them in source, logs, or artifacts.
- Make a model regression block a pull request rather than appear in a comment.
- Explain what a green check does *not* prove.

## Start here

1. Read [Concepts](concepts.md) sections 1–6: workflows, triggers, permissions, secrets, artifacts.
2. Read the [worked example](worked-example.md): the two workflows, the lint failure, the gate that blocked a degraded model — and what was not executed.
3. Do the [lab](lab.md): make a pull request that cannot merge with a worse model.

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives and the workflow-review criteria |
| [Concepts](concepts.md) | Triggers, jobs, permissions, secrets, caching, gates, supply chain |
| [Worked example](worked-example.md) | Real local runs of every CI step, plus schema validation |
| [Guided lab](lab.md) | Two workflows protecting `main` |
| [Independent challenge](independent-challenge.md) | A gate that cannot be talked around |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Failing jobs that pass locally, cache traps, secret leaks |
| [References](references.md) | GitHub Actions, security hardening, and CI-for-ML guidance |

## What you produce

- `.github/workflows/ci.yml` with lint and a Python-version matrix.
- `.github/workflows/model-validation.yml` with a data check, a pipeline run, and a regression gate.
- A failing run and a passing run, with the gate's exact message.
- A branch protection rule requiring the checks.
- A short note on what the green build does not prove.

## Honest verification note

The course repository has no GitHub remote, so **no workflow was executed by GitHub Actions** while writing this module. Two things were verified instead: both workflow files validate against the official GitHub workflow JSON schema (`ok -- validation done`), and every command inside them was executed locally in the project environment — lint passed after fixing 16 findings, 10 tests passed, the pipeline reproduced MAE 2.7686, and the gate failed a deliberately degraded model with exit code 1 before passing again. Runner-specific behaviour (caching, matrix, permissions, branch protection) remains unverified here and is marked as such in the lab.

## Next

[Module 13](../13-orchestration/index.md) moves from "run on every push" to "run on a schedule, with retries and dependencies" — a different problem from CI, often confused with it.
