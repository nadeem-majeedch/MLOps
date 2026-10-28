# Assessment Framework

> **Status: suggested self-study framework.** This is not an official university grading scheme, and it is not authorised by any institution. It is a structure for assessing your own work honestly, built so that an instructor who adopts this course can use it as a starting point and adjust weights to local regulations. Nothing here overrides your university's assessment policy.

The framework exists because self-study has a specific failure mode: reading feels like progress, and there is no one to tell you that your pipeline only works because of a leftover file. The assessment is designed to make that visible to you.

---

## 1. What is assessed, and why

| Component | Weight | Purpose | Marked by |
|---|---|---|---|
| Knowledge checks | Formative, 0% | Expose gaps in vocabulary and reasoning before they compound | You, against published answers |
| Guided labs | 20% | Prove you can execute and verify the core practices | You, against lab acceptance criteria |
| Progressive mini-projects | 40% (4 × 10%) | Prove you can integrate several modules into one working artefact | You, against rubrics; optionally a peer |
| Integrated capstone | 40% | Prove you can operate and hand over a complete system | You, against the capstone rubric and a defence |

Total: 100. The capstone and mini-projects carry 80% because integration and judgement are the point of the course. Knowledge checks carry no marks because they are diagnostic: a student who optimises for them has misunderstood the subject.

!!! note "The optional fifth mini-project"
    [MP5 · Operate and hand over](../projects/mini-projects/mp-05-operate-and-hand-over.md)
    is an optional extension for students who take Modules 13–16. It is not part
    of the illustrative 40% above and does not change the total. If an instructor
    adopts it, reduce the capstone or another component rather than adding to 100.

### 1.1 Non-negotiable quality gates

These are pass/fail and are not worth marks. Failing one caps the affected component at half marks regardless of polish, because a system that leaks a secret or cannot be reproduced is not a working system.

| Gate | Requirement |
|---|---|
| **Reproducibility gate** | A clean copy installs and runs using only documented commands, and reproduces the reported metric within the stated tolerance |
| **Secrets gate** | No credential, token, or key in the repository or its history; scans come back clean or every finding is explained |
| **Rollback gate** | A previous model version can be restored and demonstrated, with elapsed time recorded |
| **Honesty gate** | Limitations and untested claims are stated; no result is reported that was not produced by a run you can show |

---

## 2. Component 1: Knowledge checks

**Where:** at the end of each module, in `modules/NN-slug/`. **Length:** 8-12 questions, 10-15 minutes. **Answers:** in `assessments/solutions/`, never inline.

A good knowledge check asks you to *use* a concept, not recognise a phrase:

| Weak question | Better question |
|---|---|
| "What is data drift?" | "A model's inputs shift but its accuracy is unchanged for two weeks. Name the drift type that is *not* ruled out, and the data you would need to rule it out." |
| "List the stages of MLOps." | "A team's model trains reproducibly but serves wrong predictions. Which lifecycle stage is at fault, and which test would have caught it?" |
| "What does DVC do?" | "Your colleague sends you a `.dvc` file with no data. Describe exactly what you must run to train, and what could still be missing." |

**Marking:** 1-2 marks per question, total 10. Award partial credit for a correct mechanism with an imprecise term. Do not award credit for a definition copied from the lesson; the check is for understanding, and the answers are open.

**Use:** if you score below 7/10, re-read the lesson before starting the lab, not after. The lab will not fix a missing concept.

---

## 3. Component 2: Guided labs (20%)

Labs are assessed on **completion and verification**, not elegance. Each lab ends with a self-check list; you mark each item only if you have the evidence.

| Level | Credit for the lab |
|---|---|
| Complete | All checkpoints observed, verification command passes, fault in the "break it" section reproduced and repaired, cleanup done |
| Partial | Core path completed but the failure section or verification skipped |
| Incomplete | Steps performed but no verification, or expected output not matched |

**Marks:** each lab is worth equal credit; the component is the proportion of Essential-module labs completed at "complete" level. Recommended-module labs are recorded but do not lower the mark.

**Evidence standard:** a screenshot of a terminal is acceptable only if it shows the command and the result in the same frame. A copied expected-output block from the lesson is not evidence.

---

## 4. Component 3: Progressive mini-projects (40%)

Four mini-projects, each at a natural integration boundary. They are described in the [course project map](course-project-map.md); this section defines how they are marked.

| # | Mini-project | After modules | Integrates |
|---|---|---|---|
| MP1 | Reproducible training package | 05 | 02-05 |
| MP2 | Evaluated and registered model | 09 | 06-09 |
| MP3 | Served, containerised, gated service | 12 | 10-12 |
| MP4 | Monitored lifecycle with retraining | 14 | 13-14 |

Each is worth 10 marks.

### 4.1 Rubric structure

Four criteria per mini-project, each marked 0-3, doubled to give a total out of 24, then scaled to 10. The scale exists so that partial competence is visible rather than rounded away.

| Score | Meaning |
|---|---|
| 0 | Absent or does not run |
| 1 | Present but does not achieve the stated behaviour; or works only by accident |
| 2 | Achieves the behaviour; one significant gap in evidence or robustness |
| 3 | Achieves the behaviour, is robust to a stated perturbation, and the evidence would convince a sceptical reviewer |

### 4.2 Worked example: MP3, "Served, containerised, gated service"

| Criterion | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Service contract** | No endpoint | Endpoint returns predictions for well-formed input only | Validates input and returns a specific error for malformed payloads | As level 2, plus a contract test that fails if the feature order or schema diverges from training |
| **Container** | No Dockerfile | Image builds but runs as root, unpinned base, or includes build tools | Builds reproducibly, pinned base, non-root, ignore file present | As level 2, plus measured size or start-time improvement and a note on what was not optimised and why |
| **CI gate** | No workflow | Workflow runs but does not fail on a regression | Tests, data validation, and a metric gate all run; the gate blocks a degraded model | As level 2, plus a log proving the gate failed for the *stated* reason, and a demonstration that a fix passes it |
| **Evidence** | Claims only | Commands shown but outputs missing | Logs and measurements for every claim | Reproducible by a peer from the submitted repository without asking questions |

**Why these criteria:** they test the three things that actually fail in delivery - a contract that drifts from training, a container that only works on the author's machine, and a CI gate that reports success without checking anything. Polish is deliberately not a criterion.

### 4.3 What weak evidence looks like

| Weak | Strong |
|---|---|
| "Tests pass" | The test file, plus a log showing a deliberately broken behaviour failing the right test |
| "CI is green" | A red run from a degraded model, the gate's error message, and the subsequent green run after a fix |
| "Docker image is smaller" | Two build logs with sizes and build durations, and the Dockerfile diff that caused it |
| "Model is better" | Baseline metric, candidate metric, slice-level comparison, and the selection rule applied before seeing results |

---

## 5. Component 4: Capstone (40%)

The capstone is assessed against seven artefacts and six cross-cutting criteria, defined in full in the [course project map](course-project-map.md#5-capstone-requirements-what-is-assessed) and summarised here.

| Artefact | Marks |
|---|---|
| Rerunnable pipeline from a clean clone | 8 |
| Versioned data and model with provenance | 6 |
| Automated tests and a CI gate that genuinely fails | 8 |
| Served endpoint with validation | 6 |
| Monitoring with an actionable alert | 6 |
| Runbook covering deploy, rollback, and the top three alerts | 4 |
| Model card and defence document | 2 |
| **Total** | **40** |

Cross-cutting criteria - reproducibility, correctness, operability, honesty, ethics, clarity - each 0-4. A capstone that scores well on artefacts but 0-1 on honesty or operability is not a pass, regardless of total: those criteria describe whether the system can be trusted in someone else's hands.

### 5.1 Defence

A 15-minute written or oral defence, structured as:

1. **Two minutes:** what the system does and what it does not do.
2. **Five minutes:** walk through one decision you would make differently now, with evidence.
3. **Five minutes:** answer "why not simpler?" and "what breaks at ten times the load?".
4. **Three minutes:** state the top residual risk and what you would monitor for it.

If you are studying alone, record this as a written document and answer the four questions in writing. The purpose is to force articulation, which is why the questions are asked out loud in a taught setting.

---

## 6. Self-marking protocol

Marking your own work is only useful if it is structured. Follow the same sequence every time:

1. **Assess against criteria before reading your own narrative.** Open the rubric first; score each criterion; then read your report. This reduces the tendency to reward your own effort.
2. **Re-run the verification.** Score reproducibility from an actual clean run performed for the marking session, not from memory.
3. **Write the score and one sentence of justification per criterion.** A score without a reason is a guess.
4. **Name the weakest criterion.** That is your next study target, and it goes at the top of your notes.
5. **Wait a day before finalising.** Re-read the rubric with the artefact closed. If you cannot recall the evidence, the evidence is not strong enough.
6. **Record the result** in your portfolio, with the date and the artefact version.

### 6.1 Calibration check

Once per mini-project, ask a peer (or an instructor) to mark one criterion blind. Compare scores. A difference of more than one band means the criterion is being read differently, and the rubric wording - not your work - is the likely cause. Adjust your reading, not your score.

---

## 7. Feedback and revision

- **Self-feedback:** each rubric asks for one strength and one specific improvement. "Improve testing" is not feedback; "add a test that fails when the distance unit changes" is.
- **Peer feedback:** exchange mini-project repositories with one classmate. The reviewer must be able to follow the README to a running system without asking a question. Where they cannot is the finding.
- **Instructor feedback:** where a course is taught, feedback should reference the rubric criterion, not the effort.
- **Revision:** one resubmission per mini-project is encouraged; the mark recorded is the revised one, and the revision must state what changed and why. The capstone has no resubmission, because handover is the point.

---

## 8. Academic integrity and AI use

- **Individual work** unless a project brief says otherwise. Collaboration on understanding is encouraged; sharing artefacts is not.
- **Cite** external code, data, and text, including generated text you have substantially used.
- **You must be able to explain and modify every artefact you submit.** If you used a generative tool, you own the result: a pipeline you cannot debug is not your work in any meaningful sense, and the defence will expose it.
- **Never submit a result you did not produce.** If a metric came from a previous run, say so and say when.

These rules are about capability, not policing. The assessment only measures what you can actually do; anything that hides a gap wastes the only feedback you were going to get.

---

## 9. Mapping to course outcomes

| Component | Outcomes evidenced |
|---|---|
| Knowledge checks | CO1, CO2, CO3, CO4 (recognition and reasoning) |
| Guided labs | CO2-CO8, one or two per lab |
| MP1 | CO2, CO3 |
| MP2 | CO4, CO1 |
| MP3 | CO5, CO6 |
| MP4 | CO7, CO4 |
| Capstone | All ten, with CO10 as the distinguishing outcome |

Full definitions are in [learning outcomes](learning-outcomes.md).

---

## 10. If an instructor adopts this framework

- Weights are a suggestion. A 12-week course may reduce mini-projects to two and raise the capstone to 50%.
- **Do not** turn the knowledge checks into a high-stakes exam; they are designed for retrieval practice, and making them summative encourages memorisation over judgement.
- **Do** keep the quality gates. They are the part students most often try to negotiate, and the part that most predicts whether the system survives contact with reality.
- **Do** require the defence, in some form. Without it, a strong written report can mask a system nobody can operate.
- The framework is self-contained; it does not require the course repository to be adopted as-is.
