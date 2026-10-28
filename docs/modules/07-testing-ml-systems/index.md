# 07 · Unit, data, model, integration, and regression testing

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Intermediate | 16 hours | [05](../05-reproducible-training/index.md), [06](../06-experiment-tracking/index.md) | Essential |

A model can improve its measured error and still be unsafe to change. What is missing is not more evaluation; it is tests that fail when behaviour breaks, in seconds, without a human reading a table.

This module adds four layers to the pipeline: unit tests for feature logic, data tests for contracts, behavioural tests for the model, and a regression gate for the metric itself.

## What you will be able to do

- Choose the right test type for a risk, and say what each type cannot catch.
- Write unit tests for feature transformations including edge cases.
- Write data tests that use fixtures rather than the live dataset.
- Write behavioural tests: invariance, directional expectation, minimum performance.
- Add a regression gate that fails when a metric degrades beyond a stated tolerance.

## Start here

1. Read [Concepts](concepts.md) sections 1–4.
2. Run the [worked example](worked-example.md): it introduces a unit bug that most tests miss, and shows which test catches it.
3. Do the [lab](lab.md): 25 tests, a coverage report, and a gate that fails on a degraded model.

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives and the test-strategy review criteria |
| [Concepts](concepts.md) | Test layers, fixtures, behavioural tests, gates, coverage limits |
| [Worked example](worked-example.md) | A unit bug, five tests, and the one that catches it |
| [Guided lab](lab.md) | Four test layers plus a regression gate, with real failures |
| [Independent challenge](independent-challenge.md) | The smallest test that would have caught a production bug |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Fixtures, imports, flaky tests, and slow suites |
| [References](references.md) | pytest, pandera, and ML test-score sources |

## What you produce

- `tests/` with four layers and at least 20 tests.
- A coverage report, with an explanation of what the uncovered lines are.
- A recorded failure for each layer, and a passing run afterwards.
- `baseline.json` plus a gate at a stated tolerance.
- A one-page test-strategy note on what the suite cannot catch.

## Next

[Module 08 · Pipeline automation](../08-pipeline-automation/index.md) runs these tests and the pipeline on a trigger, so nobody has to remember the order.
