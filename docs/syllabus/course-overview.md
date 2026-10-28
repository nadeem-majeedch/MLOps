# Course Overview

**Machine Learning Operations (MLOps)** is a self-study course for university students who have trained a model in a notebook and now need to make it survive contact with real users.

This page is the map. It tells you what the course is, who it is for, how it is sequenced, how long it takes, and where each part of the material lives. The per-module specifications are in the [detailed syllabus](detailed-syllabus.md); this page does not repeat them.

---

## 1. The problem this course solves

A notebook that trains a model answers the question "can a model learn this pattern?" It does not answer the questions an organisation actually asks:

- Which version of the model is serving users right now, and what data trained it?
- Why did its predictions get worse last Tuesday, and who noticed?
- Can a colleague reproduce your reported accuracy from a clean copy of the repository?
- If the new model is worse, how do we go back, and how long does that take?

Most failures in machine learning systems are not modelling failures. They are version, data, environment, testing, and operational failures. This course is about those.

---

## 2. What you build

The course follows one system from a blank folder to a monitored deployment. The organisation is fictional and the data is synthetic, so you can make mistakes without consequence.

> **RaviRide** is a ride-hailing company in Lahore. Riders see an estimated arrival time before they book. The estimate comes from a model trained on past trips. Operations wants it to stay accurate as traffic, weather, and city boundaries change.

You build `raviride-eta` incrementally. Module 02 creates the repository; Module 04 validates its data; Module 05 makes training reproducible; Module 06 tracks experiments; Module 09 promotes a model into a registry; Module 10 serves it; Module 11 containerises it; Module 12 gates it in CI; Module 14 monitors it; Module 17 proves the whole chain can be operated by someone else.

The [course project map](course-project-map.md) shows exactly which artefact each module adds and which modules reuse it.

---

## 3. Who this course is for

**It is for you if** you have completed one introductory machine learning course, can fit a scikit-learn model and read a metric, can use a terminal and Git at a basic level, and have no industry experience or budget.

**It is not for you if** you are looking for deep learning research, a vendor certification, a tour of every MLOps product on the market, or a course that requires a cloud account on day one.

**It is also for you if** you already work with models and have been doing MLOps by improvisation. The early modules will be quick; the later ones will name the practices you have been missing.

Full readiness detail, including hardware and account requirements, is in [Prerequisites and readiness](../prerequisites/index.md).

---

## 4. Design principles

These are the rules that shaped the module list. They are worth knowing, because they explain what the course leaves out.

1. **Concepts before tooling.** Every tool appears because a problem has already been described and felt. Nothing is introduced with "install this and run that".
2. **One major new tool per module.** You should always be able to name the tool you learned this week and the problem it solved.
3. **Alternatives are explained, not hidden.** When a choice is made (Prefect rather than Airflow, MLflow rather than a managed registry), the guide says what the other options are and why a beginner should not start there.
4. **No enterprise complexity for its own sake.** No service mesh, no multi-cluster, no feature store on day one. Complexity is added only when a realistic failure demands it.
5. **Advanced means advanced.** The last third of the course is not "more of the same"; it is drift analysis, access control, rollout strategy, and incident response.
6. **Every claim is checkable.** Labs end in observable output. Assessment asks you to produce evidence, not to assert understanding.
7. **Local and free by default.** No core outcome requires payment, a credit card, or a cloud account.

---

## 5. Levels and tiers

**Level** describes intellectual difficulty. **Tier** describes whether you may skip it.

| Level | Meaning |
|---|---|
| Foundation | No MLOps background; concepts and first hands-on use |
| Intermediate | Assumes earlier modules; multiple interacting components |
| Advanced | Design trade-offs, failure handling, observability, security |
| Production | Operate and defend a running system end to end |

| Tier | Meaning |
|---|---|
| **Essential** | Skipping this breaks later modules or the capstone |
| **Recommended** | Deepens practice; a core capstone can pass without it |
| **Advanced / optional** | For production realism or specialisation; explicitly optional |

The essential path is about 200 hours and produces a working, tested, monitored service. The full path is about 285 hours and adds automation depth, orchestration, cloud concepts, and a full capstone.

---

## 6. Module sequence

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
| 16 | Cloud deployment concepts, Kubernetes, scaling, and reliability | Advanced | 22 | Advanced |
| 17 | Advanced MLOps capstone integrating the entire lifecycle | Production | 48 | Capstone |

**Total: approximately 284 guided hours**, including reading, labs, and the capstone. Self-study beyond the guided material, such as revision and your own experimentation, typically adds 10-20 percent.

### Why this order

Modules 01-03 establish vocabulary and a working environment, because every later failure ("it works on my laptop") is an environment or project-structure problem in disguise. Modules 04-07 cover the data and training substrate: nothing downstream is trustworthy if the data and the training run are not reproducible. Modules 08-09 introduce automation and lifecycle, which is where a collection of scripts becomes a system. Modules 10-12 make the system callable, portable, and gated. Modules 13-16 make it operable, observable, safe, and scalable. Module 17 integrates everything and removes the scaffolding.

The [learning roadmap](../learning-roadmap/index.md) shows the dependency graph and two concrete week-by-week schedules.

---

## 7. Time commitment and pacing

| Route | Weekly effort | Duration | Notes |
|---|---|---|---|
| Intensive | ~18 hours | 16 weeks | One semester with MLOps as a main subject |
| Standard | 9-10 hours | 30 weeks | The default recommendation while studying other courses |
| Part-time | ~7 hours | 40 weeks | Working professionals; capstone stretches over several weeks |

A 10-hour week is three 3-hour sessions, or four 2.5-hour sessions. The course is written in parts with checkpoints, so an interrupted session does not cost you the lab. Week-by-week schedules for all three routes are in the [learning roadmap](../learning-roadmap/index.md).

Do not compress the capstone. It is where the course's outcomes are actually demonstrated, and it needs calendar time for CI runs, drift windows, and rollback rehearsal, not just hours.

---

## 8. Assessment

Assessment is practical and self-administered. It is a **suggested self-study framework**, not an official university grading scheme: you mark your own work against published rubrics, and an instructor who adopts the course may weight it differently.

The structure is knowledge checks (ungraded, in-module), guided labs (completion and verification), four progressive mini-projects, and one integrated capstone. Acceptance criteria are written as observable evidence. Full detail, including rubrics and self-marking protocol, is in the [assessment framework](assessment-framework.md).

---

## 9. Tooling

The course uses a deliberately small set of free and open-source tools, each introduced at the moment its problem appears: Python and `venv`, Git, DVC, MLflow, pytest and pandera, FastAPI, Docker, GitHub Actions, Prefect, Evidently, and a local Kubernetes cluster for concepts only.

Every module states what its tool is for, what the alternatives are, and what to do if you cannot or will not use it. The [tool selection guide](tool-selection-guide.md) is the single place where those choices are justified, including which paid services are optional and which enterprise tools are deliberately excluded.

---

## 10. Platform, cost, and honesty

- **Windows 11 with PowerShell 7 is the primary platform.** Linux and macOS alternatives are given wherever commands differ. This is stated once here and enforced throughout.
- **Core path: free and local.** No credit card, no cloud account, no paid licence.
- **Optional cloud paths are labelled** `Paid - optional` and always have a local alternative that reaches the same outcome.
- **Heavy labs are labelled** with RAM, disk, and time, and name a lighter route.
- **Nothing is claimed as tested that was not run.** Every lab states whether it was verified and names any step that could not be run here.

---

## 11. Where to start

1. Read [Prerequisites and readiness](../prerequisites/index.md) and take the ten-minute self-check. Do this before anything else; it is diagnostic.
2. Read [The learning roadmap](../learning-roadmap/index.md) and pick a route.
3. Begin Module 01. It needs no tooling and no setup.
4. Keep the [project map](course-project-map.md) open while you work; it shows what you are accumulating and why.

---

## 12. What this course is not

- **Not a deep learning course.** Models are deliberately simple so that the operational machinery is the subject, not the architecture.
- **Not a certification guide.** It teaches judgement, not exam answers.
- **Not a product tour.** Several popular platforms are named and deliberately not taught; the guide says why.
- **Not a reference manual.** It is a teaching text: it explains before it instructs, and it expects you to do the labs.

---

## Related documents

| Document | What it answers |
|---|---|
| [Detailed syllabus](detailed-syllabus.md) | The full specification of every module |
| [Learning outcomes](learning-outcomes.md) | What you can do at the end, and where each outcome is taught and assessed |
| [Tool selection guide](tool-selection-guide.md) | Why these tools, what the alternatives are, what to avoid |
| [Assessment framework](assessment-framework.md) | How self-assessment and rubrics work |
| [Course project map](course-project-map.md) | The artefact ladder and capstone requirements |
| [Learning roadmap](../learning-roadmap/index.md) | Dependency graph, schedules, milestones |
| [Prerequisites](../prerequisites/index.md) | Readiness, hardware, accounts, self-check |
