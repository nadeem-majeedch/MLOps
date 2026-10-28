# Machine Learning Operations (MLOps)

**A self-study course that takes you from a working notebook to a system you can run, monitor, and defend in production.**

This repository is a textbook and a laboratory manual in one. Every idea is explained in plain language, practised in a realistic lab on your own machine, checked against an observable result, and then assessed. It is written for university students studying alone, not for an instructor reading slides aloud.

The material is also organised as a documentation website. Start at [docs/index.md](docs/index.md) if you prefer to read it with navigation, search, and a table of contents on every page.

> **Course status:** all 17 modules are written, with concepts, worked examples, guided labs, independent challenges, knowledge checks, troubleshooting, and references. Modules 01–14 are backed by the executable RaviRide project, whose pipeline, registry, API, and tests were re-run in the final audit; not every command printed in every lesson was re-executed. Modules 15–17 state their verification limits on the page: the fairness and manifest checks were executed, while the optional Kubernetes cluster exercise and hosted CI runs are marked as not executed here. Nothing is marked verified unless it was.

---

## What this course is

A notebook that trains a model answers one question: can a model learn this pattern? It does not answer the questions an organisation actually asks. Which model is serving users right now, and what data trained it? Why did it get worse last Tuesday, and who noticed? Can a colleague reproduce your reported accuracy from a clean copy? If the new model is worse, how do we go back, and how long does that take?

Most failures in machine learning systems are not modelling failures. They are version, data, environment, testing, and operational failures. This course is about those, taught in the order you meet them.

---

## What you will be able to do

By the end of the course you will be able to:

- explain the ML lifecycle, name the artefact each stage produces, and place a failure at the stage that should have caught it;
- make a project reproducible, so another person can rebuild your environment, data, and results from a clean copy;
- specify and enforce data quality with executable checks, version datasets, and detect leakage;
- track experiments, evaluate beyond a single aggregate number, and justify a model choice on evidence;
- verify a system with unit, data, model, integration, and regression tests, and explain what each cannot catch;
- deliver a model as a validated service, packaged in a container, with CI that refuses a regression;
- operate the service: schedule and retry pipelines, detect drift before users report it, retrain, and roll back;
- assess risk - threat-model the service, manage secrets, measure disparity, and publish an honest model card;
- reason about deployment at scale: infrastructure as code, probes, SLOs, rollout strategy, and cost;
- hand over a running system with documentation a peer can operate, and defend the design when asked "why not simpler?".

The full outcome map, including where each is taught and assessed, is in [Learning outcomes](docs/syllabus/learning-outcomes.md).

---

## Who this course is for

You should have completed one introductory machine learning course and be comfortable with basic Python, Git, and a terminal. You do **not** need experience with Docker, cloud platforms, CI/CD, or Linux administration; those are taught here from first principles.

A laptop that can run a Jupyter notebook can complete the core course. No paid software, cloud account, or credit card is required.

**Start here:** [Prerequisites and readiness](docs/prerequisites/index.md) - a ten-minute check of what you need and what this course will teach you from scratch.

---

## How the course is organised

Seventeen modules, in four levels. Every module states its level, hours, and prerequisites at the top, so you always know what you are committing to.

| Level | What changes |
|---|---|
| **Foundation** | Concepts and first hands-on use. No MLOps background assumed. |
| **Intermediate** | Multi-component workflows: data, experiments, services, automation. |
| **Advanced** | Design trade-offs, failure handling, observability, security, scale. |
| **Production** | Operate and defend a complete system end to end. |

### Module map

| # | Module | Level | Hours | Tier |
|---|---|---|---|---|
| 01 | Introduction to MLOps and the ML lifecycle | Foundation | 8 | Essential |
| 02 | Python, Git, CLI, and reproducible environments | Foundation | 14 | Essential |
| 03 | Organizing an ML project and understanding technical debt | Foundation | 10 | Essential |
| 04 | Data quality, validation, and data versioning | Intermediate | 14 | Essential |
| 05 | Reproducible model training and pipeline design | Intermediate | 16 | Essential |
| 06 | Experiment tracking and model evaluation using MLflow | Intermediate | 14 | Essential |
| 07 | Unit, data, model, integration, and regression testing | Intermediate | 16 | Essential |
| 08 | Pipeline automation and workflow dependencies | Intermediate | 12 | Recommended |
| 09 | Model artifacts, registries, promotion, and lifecycle management | Intermediate | 14 | Essential |
| 10 | Model serving and REST APIs using FastAPI | Intermediate | 16 | Essential |
| 11 | Docker images, containers, and deployment environments | Intermediate | 14 | Essential |
| 12 | CI/CD and ML validation workflows using GitHub Actions | Advanced | 18 | Essential |
| 13 | Workflow orchestration and scheduled pipelines | Advanced | 16 | Recommended |
| 14 | Prediction monitoring, data drift, model drift, and retraining | Advanced | 18 | Essential |
| 15 | Security, privacy, governance, fairness, and responsible deployment | Advanced | 14 | Recommended |
| 16 | Cloud deployment concepts, Kubernetes, scaling, and reliability | Advanced | 22 | Advanced / optional |
| 17 | Advanced MLOps capstone integrating the entire lifecycle | Production | 48 | Capstone |

**About 284 guided hours** in total. The essential path is roughly 200 hours and still produces a working, tested, monitored service; Modules 08, 13, 15, and 16 deepen it.

`Essential` means skipping it breaks later work. `Recommended` and `Advanced` modules can be deferred; each names the outcome it strengthens.

### What a module contains

Every module follows the same shape, so you spend your attention on the subject rather than the layout:

- an overview that states its outcomes, required background, and common misconceptions;
- short lessons of 15-25 minutes each;
- a guided lab in a realistic organisation, with checkpoints, expected output, a deliberately induced failure, troubleshooting, and cleanup;
- an independent challenge that is not step-by-step;
- a knowledge check with answers kept separate;
- at least one graded artefact with a rubric stated in advance.

---

## What you build

The course follows one system from an empty folder to a monitored deployment. **RaviRide** is a fictional ride-hailing company in Lahore whose app shows an estimated arrival time. The data is synthetic, so mistakes are free.

You build `raviride-eta` incrementally: repository in Module 02, validated data in 04, reproducible training in 05, tracked experiments in 06, a registry in 09, an API in 10, a container in 11, a CI gate in 12, monitoring in 14, and a handover package in 17. Four progressive mini-projects and one capstone bring the pieces together.

The [course project map](docs/syllabus/course-project-map.md) shows which module contributes which artefact, and exactly what the capstone is assessed on.

---

## How to study

1. **Read a lesson.** Definitions come before use; if a term is new, it is explained where it appears.
2. **Do its lab.** Type the commands rather than copying them. Labs are built in parts, so they survive interruption.
3. **Compare against the expected result.** Every lab ends with a check that distinguishes success from near-success.
4. **Break something on purpose.** Each lab includes a realistic fault so you learn the failure signature, not just the happy path.
5. **Answer the knowledge check**, then compare with the key.
6. **Write two sentences** on what you would change in the design, and keep them. The capstone draws on these notes.

Do the labs in order. From Module 04 onward, modules reuse artefacts you built earlier; skipping a lab means rebuilding it later under time pressure.

### Pacing

| Route | Weekly effort | Duration |
|---|---|---|
| Intensive | ~18 hours | 16 weeks |
| Standard | 9-10 hours | 30 weeks |
| Part-time | ~7 hours | 40 weeks |

Each route reaches the same outcomes. The [learning roadmap](docs/learning-roadmap/index.md) has week-by-week schedules, a dependency graph, and the milestone gates that tell you when you are ready to move on.

---

## Assessment

Assessment is practical and self-administered against published rubrics. It is a **suggested self-study framework**, not an official university grading scheme: you mark your own work, and an instructor who adopts the course may weight it differently.

The structure is knowledge checks (diagnostic, unmarked), guided labs, four core mini-projects plus an optional fifth, and one integrated capstone. Acceptance criteria are stated as observable evidence - a clean clone reproduces the metric, CI fails for the right reason, rollback is demonstrated and timed - because "understand MLOps" cannot be marked.

A [practice package](docs/assessments/index.md) supports it: [module practice exercises](docs/assessments/module-practice.md), [nine question banks](docs/assessments/question-bank/index.md) with separate answer keys, five [mini-project specifications](docs/projects/mini-projects/index.md), the [capstone rubric](docs/assessments/capstone-assessment.md), a [revision guide](docs/assessments/revision-guide.md), and seven [submission templates](docs/submissions/index.md).

Full detail, including rubrics and self-marking protocol, is in the [assessment framework](docs/syllabus/assessment-framework.md).

---

## Windows 11, Linux, and macOS

Windows 11 with **PowerShell 7** is the primary platform, and instructions are written for it explicitly. Every command block names its shell. Where Linux or macOS genuinely differs, an alternative is given in a clearly marked, collapsed section.

This is a deliberate choice: most MLOps material silently assumes a Unix shell, and Windows students then spend their evenings translating instead of learning. If you use Linux or macOS, nothing is lost; you will simply take the alternative path more often.

---

## Cost, resources, and honesty about both

- **Free and local by default.** Every core learning outcome is achievable with free and open-source tools on your own machine.
- **No accounts required** beyond a free GitHub account for version control and CI practice.
- **Cloud is optional and labelled.** Where a cloud service adds realism, it is marked `Paid - optional` with a local alternative that reaches the same outcome.
- **Heavy activities are labelled.** Anything needing substantial RAM, disk, or time says so before you start, and offers a lighter route.
- **Licensing is stated where it matters.** Docker Desktop, for example, is free for personal use and education but requires a paid subscription in large organisations.

You will never reach a graded outcome and discover it requires a credit card.

---

## Course materials

| Document | What it answers |
|---|---|
| [Course overview](docs/syllabus/course-overview.md) | What the course is, who it is for, how it is sequenced |
| [Detailed syllabus](docs/syllabus/detailed-syllabus.md) | Every module: outcomes, vocabulary, tools, labs, assessment, evidence |
| [Learning roadmap](docs/learning-roadmap/index.md) | Dependencies, schedules, milestones, recovery when you fall behind |
| [Learning outcomes](docs/syllabus/learning-outcomes.md) | What you can do at the end, and the evidence that proves it |
| [Tool selection guide](docs/syllabus/tool-selection-guide.md) | Why these tools, what the alternatives are, what is deliberately excluded |
| [Assessment framework](docs/syllabus/assessment-framework.md) | Rubrics, quality gates, self-marking protocol |
| [Course project map](docs/syllabus/course-project-map.md) | The artefact ladder, mini-projects, and capstone requirements |
| [Datasets](datasets/README.md) | Provenance, licences, schemas, and the generator for all practice data |
| [Starter projects](examples/starters/README.md) | Beginner, intermediate, and advanced templates with tests |
| [Lab collection](docs/labs/index.md) | Twenty scenario labs with kits, checkers, and solutions |
| [Question banks](docs/assessments/question-bank/index.md) | Ninety questions across nine topics, with answer keys |
| [Submission templates](docs/submissions/index.md) | Seven documents a project needs, with evidence fields |
| [Prerequisites](docs/prerequisites/index.md) | Readiness, hardware, accounts, self-check |
| [Course standards](docs/course-standards.md) | The authoring rules every lesson and lab follows |
| [Phase 0 audit](docs/audit-phase-0.md) | The repository's starting state and the plan for each phase |

Every module now has the full page set. Where an activity needs software that is not available on every machine — Docker, a Kubernetes cluster, a hosted CI runner — the page names the limitation and the static or local check that was used instead. The [site](docs/index.md) is the authoritative version.

---

## About

**Engr. Dr. Muhammad Nadeem Majeed**
Professor, Department of Data Science (PUCIT)
University of the Punjab, Lahore, Pakistan

This course was written for students of data science who will be asked, often in their first job, to keep a model alive rather than to train a new one. It assumes no industry experience and no budget, and it treats operational competence, honesty about limitations, and care for the people affected by a system as part of the subject rather than an afterthought.

Corrections, clarifications, and reports of instructions that no longer work are welcome through the repository's issue tracker. Please include your operating system, the tool version, and the exact message you saw.

---

## Licence and reuse

A licence has not yet been declared for this repository. Until one is added, the default applies: the author retains all rights, and reuse beyond viewing on GitHub requires permission. A licence suitable for both the prose and the code will be chosen before the course is announced publicly; see [the audit's open issues](docs/audit-phase-0.md#6-issues-requiring-instructor-decisions).

Third-party tools, datasets, and figures referenced by the course remain under their own licences, which are credited where they are used.
