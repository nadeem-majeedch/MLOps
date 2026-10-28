# Course Standards and Authoring Guide

**Applies to:** every lesson, lab, assessment, diagram, dataset description, and README in this repository.
**Audience for this document:** course authors and contributors. Students do not need to read it, though nothing in it is secret.

If a rule here conflicts with convenience, the rule wins. If a rule is wrong, change the rule deliberately in a separate commit rather than quietly breaking it in one file.

---

## 1. What this course is

A self-study course that takes a university student from "I can train a model in a notebook" to "I can operate a model in production, explain its behaviour, and diagnose it when it fails."

Two consequences follow from "self-study":

1. **The text must teach, not prompt.** A student reading alone cannot ask what a term meant. Every new term is defined before it is used.
2. **The student must be able to tell whether they succeeded.** Every lab ends in an observable result, a comparison against expected output, and a self-check. "It seemed to work" is not a result.

### 1.1 Audience

| Assumed | Not assumed |
|---|---|
| One introductory machine learning course (can fit a model with scikit-learn) | Any industry experience |
| Basic Python: functions, lists, dictionaries, imports, virtual environments | Packaging, testing, or type hints |
| Basic command line: change directory, run a command | Shell scripting, `grep`/`sed` fluency, Linux administration |
| Basic Git: `add`, `commit`, `push` | Branching strategy, review workflow, large-file handling |
| Comfort reading English technical text | Prior exposure to Docker, cloud, CI, or monitoring |

Everything beyond the left column is taught in Modules 00-03 before the course relies on it.

---

## 2. Non-negotiable rules

1. **Define before use.** A term appears in a definition callout the first time it is used, and is added to the glossary. No acronym survives its first appearance unexplained.
2. **Windows 11 first.** The primary command block is PowerShell 7 (`pwsh`). A bash/zsh version follows only where the commands genuinely differ. Never publish bash-only instructions without a Windows path.
3. **Local and free by default.** Every learning outcome is achievable with free and open-source tools on a student laptop. Cloud, paid tiers, and account requirements are labelled and optional.
4. **No unverified instructions.** A command block is verified only if its output was captured from a real run. Otherwise it must be marked `> **Unverified:**`. Never present a plausible command as tested.
5. **No secrets, ever.** No API keys, tokens, passwords, connection strings, or personal data in the repository, including examples and screenshots.
6. **No personal data.** Core datasets are synthetic or openly licensed with a stated licence. No scraping of people's data.
7. **Ethical scenarios.** Every lab scenario is plausible, non-exploitative, and framed around a defensible purpose. No surveillance, scoring of individuals' rights, or medical diagnosis.
8. **Explanations before instructions.** Say what a tool is for and what problem it solves before listing how to run it.
9. **Failure is part of the curriculum.** Each lab names at least one realistic failure, how to recognise it, and how to fix it.
10. **Root `README.md` stays a front door.** No installation steps, package commands, build instructions, or deployment procedures there; those live under `docs/setup/` and in module material.
11. **Do not overwrite another author's work to make a point.** Improve in place and keep the reasoning visible in the commit message.
12. **State the resource cost.** Time, disk, RAM, network, and money are stated before the student starts.

---

## 3. Voice and tone

- Address the student as **you**. Refer to the course as **we** when describing what the material does.
- Explain the *why* before the *how*, and the *what happens if it goes wrong* after it.
- Be direct. "Run the following command" is better than "you may wish to consider running".
- No hype, no fear. Do not call a tool "revolutionary"; do not claim a model "will fail in production" without a mechanism.
- Do not use "simply", "just", "obviously", or "of course". If it were obvious, the section would not be needed.
- Prefer concrete numbers and named examples over abstractions: "a model retrained weekly on 40,000 rows" beats "a model at scale".
- Write in complete sentences, except inside tables and checklists.
- Avoid idioms and culturally specific humour; the course is read internationally and often in a second language.

---

## 4. Terminology policy

MLOps borrows from software engineering, data engineering, and machine learning, and the same word often means three things. To keep the course learnable:

1. **First-use definition callout.** Use this exact block:

   ```markdown
   > **Drift** - a change over time in the data the model receives, or in the relationship
   > between that data and the target, that makes the model's learned patterns less valid.
   > Drift is not the same as a bug: the code is unchanged, but the world moved.
   ```

2. **One canonical definition.** The full definition lives in `docs/glossary.md` (planned, Phase 1). Lessons give the short version and link to the glossary entry, so the definitions cannot drift apart.
3. **Expand every acronym on first use** in each file: "continuous integration (CI)". Files are read out of order.
4. **Distinguish near-synonyms explicitly** when both are used: data drift vs concept drift; reproducibility vs replicability; deployment vs release; monitoring vs observability.
5. **Do not invent vocabulary.** If the field uses "model registry", do not rename it "model catalogue" for elegance. Students must recognise the term outside this course.

---

## 5. Module and lesson anatomy

A module is a folder `modules/NN-slug/`. A lesson is a Markdown file inside it.

Module numbers, titles, levels, and hours are fixed by the [detailed syllabus](syllabus/detailed-syllabus.md). Do not renumber a module or rename it in one file only; the numbering appears in the README, the roadmap, the project map, and every prerequisite chain.

### 5.1 Module README (`modules/NN-slug/README.md`)

1. Title and one-paragraph purpose
2. Level, estimated study time, prerequisites
3. Learning outcomes (3-6, each measurable)
4. Lesson list with links and one-line descriptions
5. Labs in this module, with time and cost labels
6. What you should be able to do when finished
7. Common misconceptions for this module
8. Where this module is used later in the course

### 5.2 Lesson file

Follow `docs/templates/lesson-template.md`. The required order is:

1. Front matter block (module, level, time, prerequisites, tools, cost)
2. **Why this matters** - a concrete failure this lesson prevents
3. **What you need to know first** - links, not repetition
4. **Core concepts** - definitions, diagrams, worked reasoning
5. **Worked example** - one small, complete, runnable example
6. **Common mistakes** - symptoms, causes, fixes
7. **Check your understanding** - 3-5 questions, answers elsewhere
8. **Next step** - one link forward, one back

Lessons target **15-25 minutes of reading**. If a lesson exceeds that, split it rather than hiding the length.

### 5.3 Section length

Aim for sections of 80-250 words with a heading every one to three screens. Long unbroken prose is where self-study students stop reading.

---

## 6. File and path conventions

| Artefact | Pattern | Example |
|---|---|---|
| Module folder | `modules/NN-kebab-title/` | `modules/06-experiment-tracking/` |
| Module overview | `README.md` | `modules/06-experiment-tracking/README.md` |
| Lesson | `NN-kebab-title.md` | `03-comparing-runs.md` |
| Lab | `lab-NN-kebab-title.md` | `lab-02-registry-promotion.md` |
| Module knowledge check | `check-NN-kebab-title.md` | `check-01-tracking-basics.md` |
| Assessment | `assessments/NN-kebab-title.md` | `assessments/04-data-quality-assignment.md` |
| Solutions | `assessments/solutions/NN-kebab-title-solutions.md` | `assessments/solutions/04-data-quality-assignment-solutions.md` |
| Project brief | `projects/NN-kebab-title.md` | `projects/02-capstone-brief.md` |
| Figure | `assets/NN-module-slug/descriptive-name.png` | `assets/06-experiment-tracking/run-comparison-view.png` |
| Dataset description | `data/NN-kebab-title/README.md` | `data/01-transit-ridership/README.md` |

Rules:

- Lowercase kebab-case only. No spaces, no uppercase, no underscores in filenames.
- Numbers are zero-padded two digits (`05`, not `5`), so sorting is stable.
- One H1 per file, matching the title. Never skip heading levels.
- Links are **relative** (`../04-data-versioning/02-dvc-basics.md`), never absolute GitHub URLs, so the repository works offline and after a rename.
- Anchor links use GitHub's slug rules; prefer a stable heading over a fragile deep anchor.
- Images: PNG or SVG, under 300 KB where possible, with descriptive filenames and alt text.
- No `.ipynb` files as the sole version of an explanation. Notebooks may appear as optional companions; the lesson text must stand alone.

---

## 7. Labels

Use these exact strings so students can scan and filter.

### 7.1 Level

| Label | Meaning |
|---|---|
| `Foundation` | No MLOps background assumed; concepts and first hands-on use |
| `Intermediate` | Assumes earlier modules; introduces multi-component workflows |
| `Advanced` | Assumes the full toolchain; design trade-offs and failure handling |
| `Production` | Operate and defend a running system; integration and incident work |

### 7.2 Cost and access

| Label | Meaning |
|---|---|
| `Free - local` | No account, no payment, no network after setup |
| `Free - account` | Requires a free account (for example GitHub) |
| `Free tier` | A paid service's free allowance; may expire or rate-limit; never required |
| `Paid - optional` | Requires payment or a card; alternative provided |
| `Institution only` | Requires a university licence or lab machine |

### 7.3 Resources

| Label | Meaning |
|---|---|
| `Light` | Under 2 GB disk, under 4 GB RAM, under 10 minutes |
| `Moderate` | 2-5 GB disk, 4-8 GB RAM |
| `Heavy` | Over 5 GB disk or over 8 GB RAM, or over 30 minutes |

A `Heavy` activity must state a lighter alternative that reaches the same learning outcome, even if less realistic.

### 7.4 Platform

`Windows 11 (PowerShell 7)` · `Linux` · `macOS` · `WSL 2` · `Docker`

### 7.5 Front matter block

Every lesson and lab begins with this block, filled in:

```markdown
| | |
|---|---|
| **Module** | 06 - Experiment tracking and model evaluation using MLflow |
| **Level** | Intermediate |
| **Time** | 40-55 minutes |
| **Prerequisites** | Module 05, lesson 05/02 |
| **Tools** | Python 3.11+, MLflow (pinned in setup guide) |
| **Cost** | `Free - local` |
| **Resources** | `Light` |
| **Last verified** | 2026-10-23, Windows 11 23H2, PowerShell 7.4 |
```

The `Last verified` row is mandatory. It records the date and platform of the last successful end-to-end run, not the date of editing.

---

## 8. Command block conventions

Commands are where self-study material fails most often. The format is fixed.

### 8.1 Format

````markdown
**Step 3 - Create and activate a virtual environment**

Run this from the repository root. The parentheses in the prompt show that the
environment is active; if you do not see them, activation failed.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Expected result: your prompt is prefixed with `(.venv)`.

<details>
<summary>Linux / macOS alternative</summary>

```bash
python3 -m venv .venv
source .venv/bin/activate
```

</details>
````

### 8.2 Requirements

- **State the working directory** before the block, or as a comment on the first line.
- **One idea per block.** A block that both installs and runs is a block that hides which step failed.
- **Show expected output** for anything whose success is not obvious. Copy it from a real run; do not paraphrase error messages.
- **Name the failure mode.** For risky steps, add one line: "If you see `X`, the cause is usually `Y`; fix it with `Z`."
- **Never require administrator rights.** If a step needs elevation, it does not belong in a student lab; find another route or mark the lab `Institution only`.
- **Never use `sudo`** in a student-facing block. It teaches a habit that hides ownership problems and is unavailable on the primary platform.
- **Do not chain with `&&`** in PowerShell 5.1 material. If a chain is used, it must be in a PowerShell 7 block, which is the stated baseline.
- **Quote paths containing spaces**, and prefer relative paths inside the repository.
- **Pin or bracket every version.** Write "Python 3.11 or 3.12" or a version pinned by the setup guide; never "the latest version".
- **`curl` on Windows** is an alias for `Invoke-WebRequest` in Windows PowerShell. Use `curl.exe` explicitly when a real curl is intended, or use `Invoke-RestMethod`.
- **Time-box downloads.** Say roughly how large a download is before the student starts it.

### 8.3 Verification status

Every lab file ends with:

```markdown
## Verification status

- [x] Executed end-to-end on Windows 11 23H2, PowerShell 7.4, 2026-10-23
- [ ] Executed on macOS 14
- [ ] Executed on Ubuntu 24.04
```

Unticked platforms must be described as untested in the lab itself. Do not imply cross-platform verification that did not happen.

---

## 9. Reproducibility requirements

A lab is reproducible when a different student, on a different day, gets a result close enough to compare.

- **Pin dependencies** in a committed requirements or lock file; the setup guide owns the versions.
- **Set seeds** for every random operation and say which ones matter (`random`, `numpy`, and the estimator's `random_state`).
- **Record dataset provenance**: source, licence, retrieval date, row count, checksum. Hash large files rather than committing them.
- **Fix split boundaries explicitly** (by row index or a stable key), never by an unseeded shuffle.
- **State tolerance.** "Accuracy within 0.01 of 0.84" is a test; "accuracy should be good" is not.
- **Report environment-sensitive numbers as ranges** for timings; wall-clock times differ by machine.
- **Avoid absolute paths.** Everything is relative to the repository root or an environment variable introduced in setup.

---

## 10. Data and ethics rules

1. **Synthetic or openly licensed data only** for core labs, with the licence named in `data/NN-slug/README.md`.
2. **No personally identifying information**, even fake-but-realistic names tied to sensitive attributes. Synthetic records use clearly fictional identifiers.
3. **No credentials in datasets**, including sample configuration files that look real.
4. **Scenarios pass the public-interest test.** A churn model for a subscription service is fine; predicting individual criminality is not.
5. **Name the harmed party.** When a lesson discusses model failure, say who bears the cost: the user, the operator, or a group of people.
6. **Document known limitations** of any dataset used: sampling bias, missing groups, label noise, and time period.
7. **Do not require students to upload their own data** to any service. Optional extensions may mention it, with a privacy warning.

---

## 11. Figures, tables, and citations

- Every figure has alt text that conveys the information, not the filename.
- Diagrams are editable sources where practical (`.svg` or Mermaid), not only screenshots. Screenshots age badly; caption them with the tool version.
- Tables are real Markdown tables, never images of tables.
- Cite claims that are not self-evident: link the official documentation page, not a blog summary, and include the access date for anything version-sensitive:

  ```markdown
  According to the [MLflow tracking documentation](https://mlflow.org/docs/latest/tracking.html)
  (accessed 2026-10-23), ...
  ```

- Do not cite tools as authorities on their own weaknesses. Use an independent source, or reason from first principles.

---

## 12. Navigation and cross-linking

- Every lesson begins with a breadcrumb line: `Course home > Module 06 > Lesson 03`.
- Every lesson ends with **Previous** and **Next** links; the first and last lesson of a module link to the module README instead.
- A module README links every lesson and lab in order.
- Cross-module references name the module and lesson, not just a path, so a printed excerpt is still useful.
- Before finishing any file, click every link. From Phase 1, CI checks internal links on every pull request.
- `docs/templates/` is the one exception to the link check: template files contain `NN` placeholders on purpose. The checker skips that directory, and authors replace placeholders when copying a template out of it.

---

## 13. Assessment and solutions

- Knowledge checks inside lessons test recall and reasoning, not trivia, and never reveal answers inline. Answers live in the assessment key.
- Graded work uses `docs/templates/assessment-template.md` and states its rubric before the student starts.
- Solutions live under `assessments/solutions/` and are linked from the assessment only as "solution and marking notes", never embedded above the question.
- Every graded criterion must be observable in the submitted artefact. "Understands MLOps" is not a criterion; "the pipeline reruns from a clean clone and reproduces the reported metric" is.
- Marks total 100 per graded item, with bands that sum correctly. Verify the arithmetic.

---

## 14. Accessibility checklist

- [ ] Heading levels are sequential; the page is navigable by headings alone.
- [ ] Colour is never the only carrier of meaning (use labels and text).
- [ ] All images have meaningful alt text; decorative images have empty alt text.
- [ ] Code blocks specify a language for syntax highlighting.
- [ ] Tables have header rows.
- [ ] Link text describes the destination; no "click here".
- [ ] No ASCII art that depends on a fixed-width font to be understood.
- [ ] Instructions do not depend on a mouse, a specific screen reader, or a specific colour vision.
- [ ] Abbreviations are expanded; sentence length is reasonable for non-native readers.

---

## 15. Attribution

- The instructor's name, title, department, and university appear once in the root `README.md` **About** section, and once in `CITATION.cff` when that file is added.
- Do not repeat the instructor's biography in module READMEs, lesson footers, or lab headers. Students already know whose course they are reading.
- A module may credit a *contributor* or *reviewer* of that module where the contribution is substantial.
- Third-party text, datasets, diagrams, and code are credited at the point of use, with a licence reference, even when the licence does not require it.

---

## 16. Definition of done for a module

A module is complete only when all of these are true:

- [ ] Module README follows Section 5.1 and links every child file.
- [ ] Outcomes are measurable and each is taught, practised, and assessed.
- [ ] Every lesson follows the template and stays within its time target.
- [ ] Every lab has a scenario, checkpoints, expected output, a troubleshooting table, cleanup, and a self-check.
- [ ] Every command block has been run on Windows 11 with PowerShell 7; the verification-status section reflects reality.
- [ ] At least one deliberately broken state is included, with diagnosis guidance.
- [ ] A knowledge check exists, with answers in the solutions location.
- [ ] The module glossary terms are proposed for `docs/glossary.md`.
- [ ] All internal links resolve; no placeholder text such as `TODO`, `TBD`, or `lorem` remains.
- [ ] Cost, resource, and platform labels are present and accurate.
- [ ] No secrets, personal data, or absolute local paths are present.
- [ ] A reader who has completed only the listed prerequisites can finish it unaided; ideally one such reader has tried.

---

## 17. Maintenance and tool drift

- Each lab carries `Last verified`. Re-verify any lab whose tools have had a major release, at least once per academic year.
- When a tool's interface changes, update the lesson and the lab in the same change, and note the version in the commit message.
- If a technique becomes obsolete, do not delete the lesson silently. Replace it and state what changed and why in the lesson's "What changed" note, so returning students are not confused.
- Prefer a smaller set of tools taught deeply over a catalogue. A new tool is added only when an existing module cannot meet its outcome without it.
