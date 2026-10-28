# Question banks

Nine banks, ninety questions, one answer key per bank. They exist for retrieval
practice: answering from memory, then checking, is the study method with the
best evidence behind it. Reading the answers first feels productive and is not.

| Bank | Covers | Level | Questions | Time |
|---|---|---|---|---|
| [01 · MLOps fundamentals](01-mlops-fundamentals.md) | Module 01 | Foundation | 10 | 35 min |
| [02 · Reproducibility and data versioning](02-reproducibility-data-versioning.md) | Modules 02, 04, 05 | Foundation | 10 | 40 min |
| [03 · Tracking and evaluation](03-experiment-tracking-evaluation.md) | Modules 06, 09 | Intermediate | 10 | 40 min |
| [04 · Testing and automation](04-testing-automation.md) | Modules 07, 08 | Intermediate | 10 | 40 min |
| [05 · APIs and containers](05-apis-containers.md) | Modules 10, 11 | Intermediate | 10 | 40 min |
| [06 · CI/CD and orchestration](06-cicd-orchestration.md) | Modules 12, 13 | Advanced | 10 | 45 min |
| [07 · Monitoring and drift](07-monitoring-drift.md) | Module 14 | Advanced | 10 | 40 min |
| [08 · Security and governance](08-security-governance.md) | Module 15 | Advanced | 10 | 45 min |
| [09 · Cloud and advanced operations](09-cloud-advanced-operations.md) | Module 16 | Advanced | 10 | 40 min |

Every bank has the same four sections:

| Section | Type | Marks | What it tests |
|---|---|---|---|
| A | Multiple choice (4) | 1 each | Recognition of the *right mechanism*, not the familiar phrase |
| B | Short answer (3) | 3 each | Ability to explain a trade-off in your own words |
| C | Debugging (2) | 4 each | Reading evidence and naming the cause |
| D | Architecture or scenario (1) | 9 | Judgement across several modules |

Total: 30 marks. The marks are illustrative, in the same sense as the rest of the
assessment framework: they weight the scenario more heavily because that is where
the course's outcomes live.

---

## How to use a bank

1. **Answer without notes**, in writing. Guessing is fine; a blank is not.
2. **Mark against the key**, awarding partial credit for a correct mechanism with
   an imprecise term.
3. **Write one line per wrong answer** describing what you thought and why. This
   is the part that makes the practice stick.
4. **Re-attempt the wrong ones after two days**, not after ten minutes.
5. **Below 18/30** means reread the module before starting its lab. The lab will
   not repair a missing concept.

Answer keys are separate pages, linked at the top of each bank and grouped under
[Reference solutions](../solutions/index.md). Do not open one while answering.

---

## Coverage

The banks are not a substitute for the labs. A student can score well here and
still be unable to make a pipeline reproducible, because knowing the words
"cache key" is not the same as finding the undeclared file that broke one. The
practical work is in the [lab collection](../../labs/index.md); these questions
check whether you understand what you did there.

| If you are revising for... | Start with | Then |
|---|---|---|
| A module knowledge check | That module's page | The matching bank |
| A viva or interview | Banks 01, 03, 07 | Practise the scenario answers aloud |
| The capstone defence | Banks 06–09 | [Revision guide](../revision-guide.md) |
| A resit after a weak lab | The bank for that topic | Redo the lab's diagnosis section |

---

## Marking your own answers

The keys give a model answer, not the only acceptable one. Award full marks when
the answer contains the mechanism the key names, even if the wording differs.
Award nothing for a definition copied from a module without application: the
question asked what you would *do*, or which of four mechanisms explains the
evidence.

For the scenario question, the key lists the elements a strong answer contains
and the marks for each. Mark element by element. A polished answer that misses
the central risk should score lower than a plain answer that names it.
