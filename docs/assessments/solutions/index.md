# Reference solutions

Answers and reference material, kept separate from the questions and briefs so you
can attempt the work first. That separation is deliberate: reading a solution
produces recognition, and the course assesses capability.

| Material | What it contains | Use it |
|---|---|---|
| [Question bank keys](question-bank/index.md) | Model answers, marking notes, weak-answer examples for all nine banks | After attempting a bank |
| [Mini-project notes](mini-projects.md) | Design decisions, common wrong turns, evidence standards | After a first attempt |
| [Capstone notes](capstone.md) | What a strong submission contains, with pointers to working code | During self-marking |
| [Lab solutions](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/solutions) | Reference implementations for Labs 01–20 | After the lab's diagnosis attempt |

---

## How to use a reference solution

1. **Attempt first**, and write down where you got stuck. The stuck point is the
   useful information.
2. **Compare mechanisms, not text.** Your file names and structure can differ; if
   the mechanism is right and the evidence exists, it is a valid solution.
3. **Mark your own work before reading the notes.** Reading the reference sets an
   anchor that makes self-assessment generous.
4. **Re-attempt the weakest part** a day later, without the reference open.

---

## What these are not

- **Not the only correct answer.** Several designs meet the same criteria. The
  notes describe one that was executed and verified, and say why.
- **Not a marking scheme.** The rubrics are in the briefs and the
  [capstone assessment](../capstone-assessment.md). Weights are illustrative.
- **Not a substitute for the labs.** Running the code teaches things reading it
  does not, particularly the failure signatures.

---

## Status of the reference material

| Item | Verified how |
|---|---|
| Lab solutions | Each lab's `check_labNN.py` was run against its kit and solution |
| Starter projects | `examples/starters/verify_starters.py`, 12 checks, all passing |
| Code quoted in notes | Executed in the authoring environment (Python 3.12.10, Windows 11) |
| Docker and hosted CI | Not executed; commands documented, limitation stated |

Where something was not executed, the note says so. A reference that quietly
skips verification is worse than no reference, because it teaches a false
confidence.
