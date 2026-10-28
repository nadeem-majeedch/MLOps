# Question bank 01 · MLOps fundamentals

| | |
|---|---|
| **Covers** | [Module 01 · MLOps foundations](../../modules/01-introduction-to-mlops/index.md) |
| **Level** | Foundation |
| **Questions** | 10 |
| **Marks** | 30 |
| **Time** | 35 minutes |
| **Answer key** | [01 · Answers](../solutions/question-bank/01-mlops-fundamentals-answers.md) |

Answer in writing before opening the key. Partial credit is for a correct
mechanism, not for a correct-sounding sentence.

---

## Section A · Multiple choice (4 marks)

**A1.** A model's offline metric is unchanged, but users report bad predictions
for one city. Which lifecycle stage should have caught this first?

- a) Data collection
- b) Evaluation, using slices rather than one aggregate metric
- c) Deployment
- d) The next scheduled retraining

**A2.** Which artefact should a data-validation stage produce?

- a) A trained model
- b) A pass/fail report with per-check counts and the input's hash
- c) A Docker image
- d) A feature store

**A3.** A team ships a recommendation model. Users click what it shows them, so
the training data next quarter contains only items the model already displayed.
What is this called?

- a) Concept drift
- b) A feedback loop
- c) Training/serving skew
- d) Class imbalance

**A4.** Which of these is *technical debt specific to ML systems*, rather than
ordinary software debt?

- a) A function with no tests
- b) An undeclared dependency between a training script and a file on one
  engineer's laptop
- c) A deprecated library version
- d) A missing docstring

---

## Section B · Short answer (9 marks)

**B1.** *(3 marks)* Explain the difference between **model decay** and **concept
drift**, and give one monitoring signal for each.

**B2.** *(3 marks)* A model is trained reproducibly, tested, and deployed. Six
weeks later it produces a confidence of 0.99 for an input that is clearly
nonsense. Name the stage that should have prevented this and the check it would
have run.

**B3.** *(3 marks)* Why is "the model is in production" not evidence that the
system works? Give two things you would need to see instead.

---

## Section C · Debugging and diagnosis (8 marks)

**C1.** *(4 marks)* A service was deployed this morning. Since then, about 4% of
requests return a 500 with this log line:

```text
ValueError: could not convert string to float: 'Z02'
```

The service worked yesterday with the same code. What changed, what is the most
likely cause, and which test would have caught it before deployment?

**C2.** *(4 marks)* Weekly accuracy is flat at 0.91, but the support team reports
more complaints. The input distribution is unchanged. List three explanations and
the evidence that would separate them.

---

## Section D · Architecture and scenario (9 marks)

**D1.** A hospital asks you to build a model that flags patients who may need
follow-up after discharge. You have twelve months of historical records, and the
hospital intends to use the flag to prioritise phone calls from a small team.

Answer as a short memo (no more than 350 words):

1. What the system should and should not decide. *(2 marks)*
2. The three most serious failure modes, and how the design reduces each.
   *(3 marks)*
3. What you would monitor in the first month, and what you would refuse to report
   as success. *(2 marks)*
4. One question you must ask the hospital before accepting the data.
   *(2 marks)*

---

*Marks: 4 + 9 + 8 + 9 = 30. The key explains what each distractor in Section A
represents, because recognising a wrong mechanism is part of knowing the right
one.*
