# Before You Start: Prerequisites and Readiness

This page tells you whether you are ready for the course, what you need on your machine, and what the course will teach you from scratch. Read it before Module 01. It takes about ten minutes.

If you find a gap, that is normal. Section 5 names the bridge for each one, and every bridge is inside the course.

---

## 1. Who this course is for

You will get the most from this course if you have completed one introductory machine learning course and can already:

- load a dataset, split it, train a scikit-learn model, and report a metric;
- write and run a Python script that imports a package;
- use a terminal to move between folders and run a command;
- make a commit and push it to a GitHub repository.

You do **not** need prior experience with Docker, cloud platforms, CI/CD, monitoring, Linux administration, or software packaging. Those are taught here, starting from what they are for.

You do **not** need a powerful computer, a cloud account, or paid software. A laptop that can run a Jupyter notebook can complete the core course.

For the full picture of what the course contains, see the [course overview](../syllabus/course-overview.md); for the order you will study it, see the [learning roadmap](../learning-roadmap/index.md).

---

## 2. Knowledge you should already have

| Area | What "ready" looks like | If you are not ready |
|---|---|---|
| Python | Functions, dictionaries, list comprehensions, imports, exceptions, reading a traceback | Any introductory Python course; you will struggle silently otherwise |
| Machine learning | Train/test split, overfitting, a classifier and a regressor, one metric you can interpret | A first ML course or the first half of one |
| Statistics | Mean, standard deviation, distribution, sampling bias, correlation vs causation | Enough to read a histogram and explain why a sample may not represent a population |
| Git | `clone`, `add`, `commit`, `push`, resolving a simple merge | Git's own "Getting Started" chapter, about two hours |
| Command line | `cd`, listing files, running a program, reading `--help` | One hour of practice; the course uses the terminal constantly |
| English | Reading technical text of moderate length | The glossary is written for non-native readers, but the course is in English |

You do **not** need calculus, linear algebra beyond matrix shapes, or the ability to derive a gradient. MLOps is mostly about systems, evidence, and decisions, not model mathematics.

---

## 3. What you need on your machine

These are *requirements*, not installation instructions. Installation is Module 02's job and lives in the setup guide, so that versions, paths, and Windows-specific details are handled once, correctly, in one place.

### 3.1 Hardware

| | Minimum | Recommended | Why |
|---|---|---|---|
| RAM | 8 GB | 16 GB | Docker, a database, and an editor together are heavy |
| Free disk | 20 GB | 40 GB | Container images and Python environments are large |
| CPU | Dual-core, 64-bit | Quad-core | Training is small; the tooling is what needs headroom |
| Virtualisation | Enabled in UEFI/BIOS | Enabled | Required for WSL 2, which Docker Desktop uses on Windows 11 |
| Network | Needed for setup and downloads | Broadband | Course activities run offline once set up |

If you have 8 GB of RAM, you can still complete every core activity, but run one service at a time and expect slower lab starts. Modules that need more state clearly when they do.

### 3.2 Software

| Tool | Version guidance | Cost | Needed by |
|---|---|---|---|
| Windows 11 (or Linux/macOS) | Current, updated | Included | Module 01 |
| PowerShell 7 | 7.4 or later | Free | Module 02 |
| Git | 2.40 or later | Free | Module 02 |
| Python | 3.11 or 3.12 recommended | Free | Module 02 |
| A code editor (VS Code suggested) | Current | Free | Module 02 |
| Docker Desktop with WSL 2 backend | Current | Free for personal use and education; paid subscription required in large organisations | Module 11 |
| A web browser | Current Chrome, Edge, or Firefox | Free | Module 01 |

Notes that save students hours later:

- **Windows 11 and Docker:** Docker Desktop needs WSL 2, which needs virtualisation enabled in firmware. If virtualisation is off, Docker installation succeeds but containers will not start. Check this before Module 11, not during it.
- **PowerShell version matters.** Windows PowerShell 5.1 ships with Windows 11 and is not the same as PowerShell 7. This course writes PowerShell 7 commands. Where a command behaves differently in 5.1, the lesson says so.
- **Python version matters more than you expect.** Several MLOps libraries lag the newest Python release. Use 3.11 or 3.12 unless a module says otherwise.
- **Long paths on Windows:** deep Python environments can exceed the legacy path limit. Module 02 covers the setting if you hit it.
- **macOS on Apple silicon** is supported; a few container images may need an explicit architecture flag, and those labs say so.

### 3.3 Accounts

| Account | Required? | What for | Cost |
|---|---|---|---|
| GitHub | Required for Modules 02 and 12 | Version control practice, CI pipelines, submission of work | Free |
| Docker Hub | Optional | Pulling images; anonymous pulls are rate-limited but usually sufficient | Free |
| Any cloud provider | Optional only | Modules 15 and 16 extension labs | Free tier or paid; never required |

No lab in the core path requires a credit card, a paid subscription, or a university licence. If an activity does, it is marked `Paid - optional` or `Institution only` and an alternative is provided.

---

## 4. Gaps this course fills for you

These are the prerequisites students most often *lack* without knowing it. They are not entry requirements; they are taught, and each one has a named home.

| Missing skill | Why MLOps needs it | Taught in |
|---|---|---|
| Python packaging and virtual environments | "Works on my machine" is the most common production failure | Module 02 |
| Automated testing | A model that is not tested is a model nobody can safely change | Module 07, introduced in 02 |
| Git branching and review | Production changes need review, not commits to `main` | Module 02 |
| YAML and configuration files | Almost every pipeline and CI tool is configured in YAML | Modules 03 and 12 |
| HTTP APIs and JSON | A served model is an HTTP endpoint with a contract | Module 10 |
| Containers | Reproducible runtime, not just reproducible code | Module 11 |
| Shell scripting basics | Pipelines are commands, environment variables, and exit codes | Modules 02, 03, 08 |
| Reading logs | Diagnosis starts with a log line, not a guess | Module 14, practised in every lab |
| Basic statistics for monitoring | Drift detection is a statistical claim, not a dashboard colour | Module 14 |
| Access control and secrets handling | Leaked credentials are the most common real-world incident | Module 15 |

If several rows above describe you, that is the expected starting point. The course is designed for exactly this profile.

---

## 5. Readiness self-check

Answer without looking anything up; this is a map of your gaps, not a test.

1. What is the difference between a virtual environment and a Docker container?
2. Your model scores 0.91 in a notebook and 0.72 behind an API. Name two plausible causes.
3. What does `git diff` show that `git status` does not?
4. What is the difference between a data scientist retraining a model and a pipeline retraining a model?
5. In one sentence, what is a model registry for?
6. Why can a model with unchanged code produce worse predictions six months later?
7. What is the difference between a unit test and a data validation check?
8. What does an HTTP 422 response usually mean for a prediction endpoint?
9. Name one thing that should never be committed to a Git repository.
10. If a dashboard shows accuracy dropped from 0.88 to 0.81 overnight, what are the first two things you would check?

### How to read your result

<details>
<summary>Suggested answers and what each gap means</summary>

1. A virtual environment isolates Python packages on one machine. A container isolates the whole runtime, including the operating system libraries, so it behaves the same on another machine. *Gap → Modules 02 and 11.*
2. Different preprocessing between training and serving, a different feature order or scaling, a different data distribution, a stale model artefact, or a unit mismatch (for example currency or timestamps). *Gap → Module 10.*
3. `git status` lists changed files; `git diff` shows the actual line changes. *Gap → Module 02.*
4. A person remembers and decides; a pipeline is triggered, repeatable, and records what it did. The second is auditable. *Gap → Modules 05 and 13.*
5. A registry stores model versions with their metadata and lifecycle state, so a team can identify, compare, and promote a specific model rather than a filename. *Gap → Module 09.*
6. The world changed: input distribution shifted, the relationship between inputs and target changed, or an upstream data source changed. Code stability does not imply behaviour stability. *Gap → Module 14.*
7. A unit test checks code behaviour on fixed inputs. A data validation check tests whether incoming data still satisfies expectations about schema, ranges, and distributions. *Gap → Modules 07 and 04.*
8. The request was syntactically valid JSON but failed validation: a missing field, wrong type, or out-of-range value. I.e. the client broke the contract. *Gap → Module 10.*
9. Credentials, API keys, tokens, personal data, large datasets, or generated artefacts such as model binaries. *Gap → Modules 02 and 15.*
10. Whether the input data changed (schema, volume, source), and whether the evaluation labels or the evaluation set changed. Only then look at the model itself. *Gap → Module 14.*

</details>

Scoring is not the point. If three or more answers were unfamiliar, skim the modules in the right-hand column when you reach them rather than skipping them.

---

## 6. Time and study pattern

| Level | Modules | Study time per module |
|---|---|---|
| Foundation | 01-03 | 8-14 hours, including labs |
| Intermediate | 04-11 | 10-16 hours |
| Advanced | 12-16 | 14-22 hours |
| Production capstone | 17 | 35-48 hours, over several weeks |

**Total: approximately 284 guided hours.** Three routes are laid out in the [learning roadmap](../learning-roadmap/index.md): 16 weeks intensive, 30 weeks standard, 40 weeks part-time.

A sustainable pattern for self-study is three sessions per week of 60-90 minutes: one reading session, one lab session, one review-and-write session. Labs assume you will stop and resume, so they are written in parts with checkpoints.

Do the labs in order. From Module 04 onward, modules reuse artefacts created earlier; skipping a lab means recreating it later under time pressure.

---

## 7. If you are missing a prerequisite

- **No ML background:** complete a short introductory course first. You need to fit one model and interpret one metric, not more.
- **No Git experience:** spend two hours on branching and merging. Module 02 assumes you have typed `git switch -c` before.
- **No terminal confidence:** practise for an hour with `cd`, `ls`, `python --version`. Every lab depends on it.
- **Old or low-spec laptop:** skip Docker-based extension labs first, not core labs. Every core outcome has a local, non-container path until Module 11, and Module 11 states the minimum it needs.
- **No GitHub account:** Modules 02 and 12 need one. Create it before Module 02; it is free and takes two minutes.
- **Unstable internet:** do the setup downloads in one sitting, then work offline. Labs state which steps need a network.

When in doubt, start Module 01. It needs no tooling and no setup, and it will show you immediately which foundation to revisit before the technical modules begin.
