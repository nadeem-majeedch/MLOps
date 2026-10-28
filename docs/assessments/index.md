# How Assessment Works

> **This is a suggested self-study framework, not an official university grading scheme.** No institution has authorised these weights. They exist so you can judge your own work honestly, and so an instructor who adopts the course has a defensible starting point.

Self-study has one specific failure mode: reading feels like progress. Assessment exists to make the difference between "I have seen this" and "I can do this" visible to you before an employer or an examiner does.

---

## The practice package

| Material | What it is for | Start when |
|---|---|---|
| [Module practice exercises](module-practice.md) | Two short tasks per module | After reading a lesson, before its lab |
| [Question banks](question-bank/index.md) | 90 questions across nine topics, with separate keys | During revision, or after a module check |
| [Mini-projects](../projects/mini-projects/index.md) | Five progressive specifications | After Modules 05, 09, 12, 14 |
| [Capstone assessment](capstone-assessment.md) | Rubric, checklists, and defence protocol | When the capstone is built |
| [Revision guide](revision-guide.md) | A 14-day plan and exam technique | Two weeks before an assessment |
| [Submission templates](../submissions/index.md) | Seven documents a project needs | Before you start writing |
| [Reference solutions](solutions/index.md) | Answers and design notes, kept separate | After a first attempt |

Everything in the package is self-contained: synthetic data, no paid service, no
account. The exercises assume the `raviride-eta` project from the course, and the
[starter projects](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/starters) give you a working shape if
you do not have one yet.

---

## What is assessed

| Component | Weight | Purpose |
|---|---|---|
| Knowledge checks | 0% (diagnostic) | Expose vocabulary and reasoning gaps early |
| Guided labs | 20% | Prove you can execute and verify the core practices |
| Four core mini-projects | 40% (10 each) | Prove you can integrate several modules into one working artefact; MP5 is optional and unweighted |
| Capstone | 40% | Prove you can operate and hand over a complete system |

Knowledge checks carry no marks deliberately. If you optimise for them, you have misunderstood the subject: the course is about what your system does, not what you can recite.

Mini-projects are described in [Projects](../projects/index.md), with separate
specifications for [MP1](../projects/mini-projects/mp-01-reproducible-training-package.md)
to [MP5](../projects/mini-projects/mp-05-operate-and-hand-over.md); the capstone
brief is [here](../projects/capstone.md) and its rubric is in the
[capstone assessment](capstone-assessment.md).

---

## Four gates that are not worth marks

These are pass/fail preconditions. Failing one caps the affected component at half marks regardless of polish, because a system that leaks a secret or cannot be reproduced is not a working system.

| Gate | Requirement |
|---|---|
| **Reproducibility** | A clean copy installs and runs using only documented commands, reproducing the reported metric within tolerance |
| **Secrets** | No credential, token, or key in the repository or its history; scans clean or every finding explained |
| **Rollback** | A previous model version can be restored and demonstrated, with elapsed time recorded |
| **Honesty** | Limitations and untested claims are stated; no result is reported that you cannot show |

The gates are the part students most often try to negotiate, and the part that best predicts whether a system survives contact with reality.

---

## What good evidence looks like

| Weak | Strong |
|---|---|
| "Tests pass" | The test file, plus a log showing a deliberately broken behaviour failing the right test |
| "CI is green" | A red run from a degraded model, the gate's error message, and the green run after the fix |
| "Docker image is smaller" | Two build logs with sizes and durations, and the change that caused the difference |
| "Model is better" | Baseline, candidate, slice-level comparison, and the selection rule applied before results |

If an artefact could have been produced without understanding, it is not good evidence.

---

## Self-marking protocol

1. **Open the rubric before your report.** Score the criteria, then read your narrative. This reduces the tendency to reward effort.
2. **Re-run the verification** for the marking session. Do not score reproducibility from memory.
3. **Write one sentence of justification per score.** A score without a reason is a guess.
4. **Name the weakest criterion.** That is your next study target.
5. **Wait a day, then re-read the rubric with the artefact closed.** If you cannot recall the evidence, it is not strong enough.
6. **Record the result** with the date and artefact version.

Once per mini-project, ask a peer to mark one criterion blind. A difference of more than one band means the rubric is being read differently, and that is worth discussing.

---

## Integrity and AI use

- **Individual work** unless a project brief says otherwise. Discussing ideas is encouraged; sharing artefacts is not.
- **Cite** external code, data, and text, including generated text you have substantially used.
- **You must be able to explain and modify every artefact you submit.**
- **Never report a result you did not produce.** If a metric came from an earlier run, say so and say when.

These are not policing rules. The assessment only measures what you can do; anything that hides a gap wastes the only feedback you were going to get.

---

## Full detail

The complete framework - weights, band descriptors, the worked rubric for MP3, the capstone rubric, and guidance for instructors adapting it - is in [Rubrics and quality gates](../syllabus/assessment-framework.md).

The outcomes these assessments evidence are mapped in [Learning outcomes](../syllabus/learning-outcomes.md).

---

## Suggested study loop

```text
read a module  ->  module practice exercise  ->  guided lab
      ->  knowledge check  ->  question bank (later)
      ->  mini-project at the integration boundary
      ->  capstone, marked against the rubric
```

The loop matters more than the order of individual pages. A module you have read
but not practised will not survive the mini-project that assumes it.
