# Question bank 07 · Monitoring and drift

| | |
|---|---|
| **Covers** | [Module 14](../../modules/14-monitoring-drift/index.md) |
| **Level** | Advanced |
| **Questions** | 10 |
| **Marks** | 30 |
| **Time** | 40 minutes |
| **Answer key** | [07 · Answers](../solutions/question-bank/07-monitoring-drift-answers.md) |

---

## Section A · Multiple choice (4 marks)

**A1.** PSI on a feature rises from 0.04 to 0.31. What do you know?

- a) Model accuracy has fallen
- b) The feature's distribution has moved substantially relative to the reference
- c) The labels have changed
- d) The model should be retrained immediately

**A2.** A model predicts loan default. The economy changes and the same applicants
now default at a different rate. This is:

- a) Data drift
- b) Concept drift
- c) Training/serving skew
- d) Label noise

**A3.** Why is a label-delayed system harder to monitor than one with immediate
outcomes?

- a) Labels are always noisier
- b) Performance metrics arrive late, so input and proxy signals must carry the
  early warning
- c) The model cannot be retrained
- d) Drift does not occur

**A4.** An alert fires every night and is correct every time, but nobody acts.
What is the design error?

- a) The threshold is too sensitive for anyone's capacity, or the alert has no
  owner and no first action
- b) The metric is wrong
- c) Alerts should be weekly
- d) The model is fine

---

## Section B · Short answer (9 marks)

**B1.** *(3 marks)* Explain, in two or three sentences, why drift is not proof of
declining accuracy, and what evidence would prove it.

**B2.** *(3 marks)* Name three monitoring signals available *without* labels, and
what each can and cannot tell you.

**B3.** *(3 marks)* Give three conditions that justify retraining, and one that
does not.

---

## Section C · Debugging and diagnosis (8 marks)

**C1.** *(4 marks)* A drift report shows `distance_km` PSI = 0.42. The model's
accuracy on the same batch, measured a week later, is unchanged. What are two
plausible explanations, and what would you do next?

**C2.** *(4 marks)* A monitoring job computed PSI against a reference file that is
overwritten nightly with the previous day's data. What is wrong with the resulting
trend, and how would you fix it?

---

## Section D · Architecture and scenario (9 marks)

**D1.** Design monitoring for a model that predicts equipment failure within seven
days. Outcomes are known only after the window closes, and maintenance crews act
on the alerts. Specify the signals, the thresholds and their justification, human
review, and the retraining and rollback triggers. *(9 marks)*
