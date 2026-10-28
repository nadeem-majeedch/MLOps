<!--
ASSESSMENT TEMPLATE - three reusable shapes in one file:
  A. Knowledge check (low stakes, inside a module)
  B. Graded assignment (judgement + artefact)
  C. Project / capstone rubric
Copy only the shape you need into assessments/NN-kebab-title.md and delete the rest.
Answers go to assessments/solutions/ and are never published above the questions.
Rules: docs/course-standards.md, Section 13.

NOTE: this container file deliberately holds three documents (Shapes A, B, C) and so has
more than one H1. The one-H1 rule in the standards applies to the copy you publish.
-->

# Assessment Title

| | |
|---|---|
| **Assesses** | Module NN, lessons NN/NN-NN |
| **Level** | Foundation / Intermediate / Advanced / Production |
| **Weight** | NN% of the course, or "not graded" |
| **Time allowed** | NN minutes / NN hours / take-home, NN days |
| **Format** | Knowledge check / written + artefact / project |
| **Submission** | What is handed in, and where (state "see your instructor's submission channel") |
| **Allowed resources** | Open book and notes, own code, course repository; no shared answers |
| **Due** | Set by the instructor |

## Purpose

<!-- Two or three sentences: what this assessment proves that reading cannot. -->

## Outcomes assessed

By completing this assessment you demonstrate that you can:

1. Observable capability, phrased as a verb.
2. Observable capability.
3. Observable capability.

<!-- If an outcome is listed, some criterion below must measure it. Remove outcomes
you are not actually assessing. -->

## Before you begin

- Environment: state the exact setup expected.
- Starting point: branch, dataset, or provided files.
- Deliverables: numbered list of files, each with a required name and format.
- Integrity: individual work unless stated; cite any external code, data, or text.

> **Academic integrity:** the work must be yours. Using documentation, libraries, and
> course material is expected and should be acknowledged. Submitting another person's
> analysis, or a generated artefact you cannot explain, is a breach. You may be asked to
> walk through any part of your submission.

---

# Shape A - Knowledge check

<!-- 5-12 questions. Mix: definition recall, prediction, diagnosis, short reasoning.
No question should be answerable by pattern-matching a single sentence. -->

**Time:** 10-15 minutes. **Marks:** 10. **Closed book is not required.**

1. *(2 marks)* Question testing a core definition in the student's own words.
2. *(2 marks)* "A pipeline produces X on Monday and Y on Tuesday with no code change. Give the two most likely causes and one check that separates them."
3. *(2 marks)* Given a log excerpt, identify the failure.
4. *(3 marks)* Short scenario: choose an approach and justify it in two sentences.
5. *(1 mark)* True/false with a required one-line justification.

**Marking notes:** each question's answer, the acceptable variants, and what earns partial credit. Kept in `assessments/solutions/`.

---

# Shape B - Graded assignment

## Brief

<!-- The workplace framing, in 5-8 sentences. Same rules as a lab scenario:
realistic, ethical, no personal data. -->

## Tasks

| # | Task | Deliverable | Marks |
|---|---|---|---|
| 1 | Reproduce the baseline and record the metric with the environment details | `report.md`, section 1 | 20 |
| 2 | Introduce a controlled change and justify it | commit/PR description | 25 |
| 3 | Demonstrate the failure mode and its diagnosis | `report.md`, section 3, plus logs | 30 |
| 4 | Written recommendation for the decision-maker | `report.md`, section 4, max 400 words | 25 |
| | **Total** | | **100** |

## Marking scheme

<!-- Bands must sum to 100 and must be checkable by a second marker. -->

### Task 1 - Reproduce the baseline (20)

| Band | Descriptor |
|---|---|
| 18-20 | Reproduces the reported metric within the stated tolerance; records versions, seeds, and data checksum; another student could repeat it from the write-up alone |
| 14-17 | Reproduces the metric; environment details partly missing |
| 8-13 | Reproduces something, but the result cannot be attributed to the stated setup |
| 0-7 | Not reproducible, or no metric reported |

### Task 2 - Controlled change (25)

| Band | Descriptor |
|---|---|
| 22-25 | Single change isolated; hypothesis stated before the result; effect measured against the same baseline; limitations acknowledged |
| 16-21 | Change made and measured, but confounded with another change or missing a hypothesis |
| 9-15 | Change made without measurement or justification |
| 0-8 | No meaningful change, or an unexplained rewrite |

### Task 3 - Failure handling (30)

| Band | Descriptor |
|---|---|
| 27-30 | Failure is realistic, symptom is documented from a real run, diagnosis uses evidence, fix is verified, and the detection lesson is stated |
| 20-26 | Failure reproduced and fixed, but diagnosis is partly guesswork or the fix is unverified |
| 11-19 | Failure described conceptually, not demonstrated |
| 0-10 | No failure analysis |

### Task 4 - Recommendation (25)

| Band | Descriptor |
|---|---|
| 22-25 | Decision stated first; evidence cited; risks and cost named; a non-specialist could act on it; within the word limit |
| 16-21 | Sound recommendation, but vague on risk or cost |
| 9-15 | Describes the work rather than recommending an action |
| 0-8 | Missing, or contradicts the evidence |

## Feedback

<!-- What the student receives and when. Written feedback should name one thing
done well and one specific next improvement. -->

## Resubmission

<!-- Allowed or not, once or unlimited, what may change, and the mark cap. -->

---

# Shape C - Project / capstone rubric

## Brief

<!-- 8-12 sentences. The system to build, the constraints, the operating context,
and the decision the student must defend. Include what is explicitly out of scope
so the project does not expand without limit. -->

## Required artefacts

| # | Artefact | Why it is required | Marks |
|---|---|---|---|
| 1 | Working pipeline that reruns from a clean clone | Proves reproducibility, not a one-off notebook | 20 |
| 2 | Versioned data and model with provenance | Proves traceability | 15 |
| 3 | Automated tests and a CI run that fails on a bad model | Proves the quality gate is real | 20 |
| 4 | Served prediction endpoint with input validation | Proves the model is usable by another system | 15 |
| 5 | Monitoring view plus an alert rule | Proves the system is observable | 15 |
| 6 | Runbook: deploy, roll back, respond to the top three alerts | Proves operability by someone else | 10 |
| 7 | Model card and written defence | Proves judgement and honesty about limits | 5 |
| | **Total** | | **100** |

## Cross-cutting criteria

<!-- Applied to the whole submission, not to one artefact. State the top band only;
lower bands are "partly", "weakly", "not". -->

| Criterion | What the top band looks like |
|---|---|
| Reproducibility | A fresh clone, one documented command, and the reported metric returns within tolerance |
| Correctness | Tested behaviour matches the claims in the report; no silent exception handling |
| Operability | A competent peer can deploy and roll back using the runbook without asking the author |
| Honesty | Limitations, failure modes, and untested assumptions are stated explicitly |
| Ethics and privacy | No personal data or secrets; risks to affected people named and addressed |
| Clarity | Diagrams and prose explain the system to a reader who has not seen the code |

## Defence

<!-- Optional oral or written defence. If used, specify duration, what is asked,
and that the student may be asked to modify the system live. -->

## Late work and extensions

<!-- State the policy or defer to the instructor's course policy. -->

---

## Marking checklist for the assessor

- [ ] Every mark awarded maps to a written band descriptor.
- [ ] Total is 100 and the arithmetic is checked.
- [ ] Feedback names one strength and one specific improvement.
- [ ] Any suspicion of undisclosed assistance is handled by the institution's policy, not informally.
- [ ] The student can explain every artefact they submitted.
