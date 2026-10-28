# Question bank 03 · Experiment tracking and evaluation

| | |
|---|---|
| **Covers** | [Module 06](../../modules/06-experiment-tracking/index.md), [Module 09](../../modules/09-model-registry/index.md) |
| **Level** | Intermediate |
| **Questions** | 10 |
| **Marks** | 30 |
| **Time** | 40 minutes |
| **Answer key** | [03 · Answers](../solutions/question-bank/03-experiment-tracking-evaluation-answers.md) |

---

## Section A · Multiple choice (4 marks)

**A1.** In MLflow, which belongs in **params** rather than **metrics**?

- a) Validation loss
- b) `max_depth`
- c) Training duration
- d) Per-slice accuracy

**A2.** A team evaluates twenty variants on the test set, chooses the best, and
reports its test score. What is wrong?

- a) Nothing; the test set is there to compare models
- b) The reported score is optimistically biased, because the test set informed
  the choice
- c) The score should be the mean of all twenty
- d) The test set should have been larger

**A3.** Positive cases are 3% of the data. Which pair of metrics is most useful?

- a) Accuracy and ROC AUC
- b) PR AUC and recall at a fixed precision
- c) Accuracy and log loss
- d) R² and MAE

**A4.** Which statement about a registry alias is correct?

- a) An alias is a mutable pointer to a version; the version itself is immutable
- b) An alias renames the artifact on disk
- c) An alias is a copy of the model for backup
- d) An alias is the same as a run ID

---

## Section B · Short answer (9 marks)

**B1.** *(3 marks)* Give three things a run record must contain for someone else
to trust its metric, and say why each matters.

**B2.** *(3 marks)* Why should the selection rule be written down before the
results are seen? Illustrate with a plausible outcome.

**B3.** *(3 marks)* A model improves aggregate MAE by 8% but is worse for trips
over 15 km. What should the report say, and what decision would you recommend?

---

## Section C · Debugging and diagnosis (8 marks)

**C1.** *(4 marks)* Two MLflow runs claim identical parameters and metrics, but
their artifacts differ. The data file changed between runs. Which record should
have caught this, and what would you add?

**C2.** *(4 marks)* A model's test ROC AUC is 0.94 in the experiment and 0.71 in
production. The serving code is correct. Give three likely causes and the check
that distinguishes them.

---

## Section D · Architecture and scenario (9 marks)

**D1.** You inherit a project with 40 notebooks, a spreadsheet of results, and no
tracking server. Design the minimum tracking and evaluation setup that would let
a new colleague answer, in ten minutes: which model is deployed, why it was
chosen, and whether a proposed change is better. *(9 marks)*
