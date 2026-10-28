# Answer key · Question bank 01

[Back to the questions](../../question-bank/01-mlops-fundamentals.md)

Marks: 30. Award partial credit for a correct mechanism with imprecise
vocabulary; award nothing for a definition that is not applied to the question.

---

## Section A (1 mark each)

**A1 — b.** Evaluation should have compared performance by city. A single
aggregate can improve while one slice collapses. Data collection (a) may be the
*origin*, but the stage that should have *caught* it is evaluation. Deployment
(c) only propagates the problem; retraining (d) may repeat it.

**A2 — b.** Validation produces evidence, not an artefact that predicts. The hash
matters because a report without one cannot say which data it describes.

**A3 — b.** The model's own output shapes the next training set: a feedback loop.
Concept drift (a) is a change in the input-to-output relationship; the loop can
cause it, but the named mechanism here is the loop. Skew (c) is a difference
between training and serving pipelines. Imbalance (d) is a property of labels.

**A4 — b.** The undeclared dependency is the classic ML-specific form: data,
environment, and glue code that only exist on one machine. Options (a), (c), and
(d) are real debt, but not specific to ML.

## Section B (3 marks each)

**B1.** *Model decay* is performance loss from any cause, including changes the
model never sees. *Concept drift* is a change in the relationship between inputs
and the target: the same input now implies a different outcome. Signal for decay:
a monitored metric on labelled outcomes falls (or complaint rate rises). Signal
for concept drift: the relationship itself changes, which you can only establish
with fresh labels — input drift alone is not evidence of it. Full marks require
both the distinction and the admission that labels are needed.

**B2.** The serving/integration stage, with an **input-validation check** at the
API boundary and a **contract test** that compares the serving feature path with
the training path. Input validation rejects a value the model cannot interpret
(here, a zone code where a number is expected); the contract test catches a
feature-order or dtype mismatch that validation permits. One mark for the stage,
two for naming both checks and what each catches.

**B3.** Production is a location, not a result. You would want: (i) evidence that
the deployed artifact is the evaluated one, by hash or version; (ii) evidence
from live traffic — prediction distribution, error rates, and eventually labelled
outcomes — rather than offline metrics. Other acceptable answers: rollback
timing, alert coverage, a named owner. Deduct one mark if the answer only says
"monitor it" without naming what would count as working.

## Section C (4 marks each)

**C1.** Most likely cause: a **schema or dtype change on the request path** — for
example, a caller started sending a zone as a string where the model expects a
numeric feature, or the feature assembly reordered columns and a categorical
value landed in a numeric slot. "The same code" is the clue: the code did not
change, so the input or the environment did. A library upgrade that changed an
encoder's output dtype is the second candidate.

Marks: 1 for naming a request-schema or feature-assembly cause; 1 for the
reasoning that unchanged code implies changed input or environment; 1 for the
input-validation check at the boundary; 1 for the contract test comparing serving
and training paths. "Add a try/except" earns nothing: it hides the failure.

**C2.** Three explanations, with the evidence that separates them:

| Explanation | Evidence |
|---|---|
| The metric is computed on a stale or incomplete label set | Compare label coverage and cutoff dates; recompute on the same rows |
| The complaint definition changed (users complain about something new) | Ticket taxonomy and volume per category; sample tickets |
| Performance fell on a subgroup that the aggregate hides | Slice accuracy by segment, region, or device; confusion counts |

Accept any three plausible mechanisms with a discriminating test. A response
that says "retrain" without a diagnostic earns at most one mark.

## Section D (9 marks)

A strong memo is explicit about the decision boundary. Model answers:

**1. Decision boundary (2).** The model *prioritises* calls; it does not decide
who receives care, and a low score must not remove anyone from the call list. The
human team makes the contact decision. One mark for the boundary, one for saying
what the model must not do.

**2. Failure modes (3).** Any three, each with a design response:

- *Historical bias*: the records reflect who was offered follow-up before.
  Response: report performance by group, exclude the prior intervention as a
  feature, and state the limitation.
- *Distribution shift*: discharge policy or population changes. Response:
  monitor inputs and outcomes, with a review trigger.
- *Silent label delay*: readmissions appear weeks later. Response: define the
  evaluation window and do not claim live accuracy before it closes.
- *Automation bias*: staff stop exercising judgement. Response: present reasons,
  not only a score, and sample audits.

One mark per failure mode with a response; cap at three.

**3. Monitoring and honesty (2).** Monitor input completeness, score
distribution, contact outcomes, and performance on matured labels; alert on
shifts in the flagged population. Refuse to report "accuracy" as success in
month one, because labels have not matured; report coverage and process measures
instead. One mark each.

**4. Question for the hospital (2).** Any question that could invalidate the
project, asked before accepting data. Strong examples: what was the follow-up
policy during the historical period, and who was *not* offered a call? Is the
data complete for patients who moved away or died? What consent covers secondary
use? One mark for relevance, one for saying why the answer could change the
design.

---

## What a weak answer looks like

| Weak | Why it loses marks |
|---|---|
| "Monitor accuracy and retrain when it drops" | Accuracy is not available live; retraining is not a diagnosis |
| "The model is biased, so remove the sensitive attribute" | Removing the attribute does not remove the disparity, and loses the ability to measure it |
| "Add validation" without saying what is validated | Names a category, not a check |
| "The code did not change, so the data must have" | Half the reasoning: the environment can change too, and the log points at a dtype |
