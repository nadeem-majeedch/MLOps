<!--
LAB TEMPLATE - copy to modules/NN-slug/lab-NN-kebab-title.md and fill it in.
Delete every HTML comment before publishing.
Rules: docs/course-standards.md. Student-facing, Windows 11 + PowerShell 7 first.
A lab is not a tutorial. The student does the work; the text removes ambiguity,
not thinking. Every step ends in something the student can observe.
-->

# Lab NN: Verb-First Title

`Course home > Module NN > Lab NN`   ·   **Lesson:** [related lesson](NN-title.md)

| | |
|---|---|
| **Module** | NN - Module title |
| **Level** | Foundation / Intermediate / Advanced / Production |
| **Time** | NN-NN minutes |
| **Prerequisites** | Module NN, lab NN |
| **Tools** | Tool and version bracket |
| **Cost** | `Free - local` |
| **Resources** | `Light` / `Moderate` / `Heavy` |
| **Last verified** | YYYY-MM-DD, Windows 11, PowerShell 7.x |

## Scenario

<!--
A realistic, ethical workplace situation in 4-8 sentences. Name the organisation
(fictional), the role the student is playing, the system, and the pressure.
Include why it matters to a person, not just to a metric.

Good: "You are the second data scientist at Sahar Clinic, a four-branch clinic in
Lahore. The no-show model was trained in March. In July, reception changed how
appointments are booked and the reminder SMS stopped being sent. Nobody
re-trained the model. The clinic manager wants to know whether to trust this
week's predictions."
-->

## Your task

<!-- One sentence: what the student will produce or decide by the end. -->

## Learning outcomes

By the end of this lab you will be able to:

1. ...
2. ...
3. ...

## Before you start

- [ ] Environment from Module 00 is working (`python --version` prints 3.11+).
- [ ] Repository is up to date and you are on your own branch.
- [ ] You have about NN minutes and NN GB of free disk space.
- [ ] You have read [the related lesson](NN-title.md).

> **Safety note:** state anything that is destructive, slows the machine, downloads a
> large file, or touches a service outside the laptop. If nothing applies, delete this.

---

## Part 1: Name of the first stage

<!--
Each part has a goal, the commands, the expected observation, and a checkpoint.
Do not exceed 5-8 numbered steps per part.
-->

**Goal:** what this part achieves and why it comes first.

1. Step, with the working directory stated.

   ```powershell
   # Windows 11 - PowerShell 7 - run from the repository root
   command
   ```

   Expected result:

   ```text
   <real output>
   ```

2. Next step.

<details>
<summary>Linux / macOS alternative</summary>

```bash
command
```

</details>

> **Checkpoint 1** - you should now see `X`. If you see `Y` instead, go to
> [Troubleshooting](#troubleshooting) entry T1 before continuing.

---

## Part 2: Name of the second stage

**Goal:**

<!-- Repeat the structure. -->

> **Checkpoint 2** - 

---

## Part 3: Break it on purpose

<!--
Required. The student introduces a realistic fault and diagnoses it. This is
where MLOps skill actually forms: the ability to recognise a failure signature.
Examples: delete a column the model expects, serve a model trained on different
feature scaling, corrupt one row, stop a service mid-run, point at an empty data
directory.
-->

**Goal:** meet the failure you will meet in production, in a safe place.

1. Cause the fault.
2. Observe the symptom. Record the exact message.
3. Diagnose using a specific check, not guesswork.
4. Repair, and confirm the original behaviour returns.

**What you should have learned:** the symptom for this failure is `<signature>`, and
the first diagnostic step is `<action>`.

---

## Expected end state

<!-- A concrete, checkable description of "done". -->

When you finish, you should have:

- a file at `path/to/artefact` containing ...
- output resembling ...
- a one-paragraph written answer to the decision question.

## Verify your work

<!--
Give the student a command or check that distinguishes success from near-success.
Ideally include one automated check, e.g. a pytest test or a script that exits
non-zero on failure.
-->

```powershell
# Windows 11 - PowerShell 7
python scripts/check_lab_NN.py
```

Expected:

```text
<real output; exit code 0>
```

---

## Troubleshooting

<!--
Real failures, written from real runs. Ordered by how often students hit them.
The symptom column must quote the actual message text.
-->

| ID | Symptom | Likely cause | Fix |
|---|---|---|---|
| T1 | Exact error text | Underlying reason | Smallest correct action |
| T2 | Exact error text | Underlying reason | Smallest correct action |
| T3 | Command not found in PowerShell | Virtual environment not activated or PATH not refreshed | Activate `.venv`; reopen the shell |
| T4 | Permission denied writing files | Running from a protected folder or a file open in another program | Work inside the repository; close the file |

---

## Cleanup

<!--
Stop services, remove large temporary artefacts, keep what the next lab needs.
State exactly what to delete and what to keep, with commands.
-->

Keep: `<path>` (needed for lab NN+1).
Remove:

```powershell
# Windows 11 - PowerShell 7
Remove-Item -Recurse -Force .\path\to\temp
```

---

## Reflect

<!--
Three questions that require judgement, not recall. These are the seed of the
graded write-up.
-->

1. What evidence would have told you this system was degrading a month earlier?
2. Which choice in this lab would you defend to a reviewer, and which would you change?
3. What would break first if this ran at 100 times the data volume?

## Self-check

- [ ] I can explain what each command changed, without reading the lab.
- [ ] My output matches the expected end state.
- [ ] I caused the failure in Part 3 and can describe its signature from memory.
- [ ] I can answer the reflect questions in writing, in my own words.
- [ ] I cleaned up temporary files and stopped all services.

## Optional extensions

<!--
Clearly optional, labelled with cost/resource impact. Never required for the
module outcome; never the only way to learn something assessed.
-->

- `Free - local` / `Moderate`: extension that deepens the same idea.
- `Paid - optional`: a cloud variant, with a warning about cost and accounts.

---

## Verification status

- [ ] Executed end-to-end on Windows 11 (build), PowerShell 7.x, YYYY-MM-DD
- [ ] Executed on macOS
- [ ] Executed on Ubuntu

## Related material

- Lesson: [link](NN-title.md)
- Next lab: [link](lab-NN-title.md)
- Glossary terms introduced: term, term
