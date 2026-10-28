# Question bank 04 · Testing and automation

| | |
|---|---|
| **Covers** | [Module 07](../../modules/07-testing-ml-systems/index.md), [Module 08](../../modules/08-pipeline-automation/index.md) |
| **Level** | Intermediate |
| **Questions** | 10 |
| **Marks** | 30 |
| **Time** | 40 minutes |
| **Answer key** | [04 · Answers](../solutions/question-bank/04-testing-automation-answers.md) |

---

## Section A · Multiple choice (4 marks)

**A1.** Which test catches a feature computed differently at serving time?

- a) A unit test of the feature function
- b) A contract test comparing the training and serving feature paths on the same row
- c) A smoke test that the API returns 200
- d) A test that the model file loads

**A2.** A test asserts `model.predict(X)` returns a DataFrame with 10 rows. What
does it *not* establish?

- a) The function runs without raising
- b) The output shape is stable
- c) The predictions are correct or plausible
- d) The model object is callable

**A3.** A pipeline stage writes `latest.csv` with a timestamp in its name. What
does this break first?

- a) The cache key, because the output name changes on every run
- b) The Python import path
- c) The model's accuracy
- d) The container's health check

**A4.** Which failure should a data test catch before training starts?

- a) A feature with a shifted mean
- b) A required column arriving with 30% nulls
- c) A model with lower ROC AUC than last week
- d) A slow API response

---

## Section B · Short answer (9 marks)

**B1.** *(3 marks)* Explain why a test that passes on every run, including when
the behaviour is broken, is worse than no test.

**B2.** *(3 marks)* Name the four layers of an ML test suite and one defect only
that layer catches.

**B3.** *(3 marks)* A pipeline takes 40 minutes because every stage reruns. Give
three checks you would make before optimising anything.

---

## Section C · Debugging and diagnosis (8 marks)

**C1.** *(4 marks)* A test passes locally and fails in CI with:

```text
AssertionError: assert 1700000000.0 == 1700000001.0
```

The values are timestamps. What is the most likely cause, and how would you make
the test independent of it?

**C2.** *(4 marks)* A metric gate in CI has passed for six weeks. A model with a
known regression also passes. List three reasons a gate can be green while
checking nothing, and the check for each.

---

## Section D · Architecture and scenario (9 marks)

**D1.** Design the test and automation strategy for a daily batch pipeline that
scores loan applications and writes results to a database. Include what is tested
at each layer, what is deliberately not automated, and how a failure stops the
run. *(9 marks)*
