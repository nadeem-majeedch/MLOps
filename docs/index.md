# Machine Learning Operations

**A self-study course that takes you from a working notebook to a system you can run, monitor, and defend in production.**

Most machine learning courses stop when the model trains. This one starts there. You will learn what happens to a model after the notebook closes: how it is versioned, packaged, served, tested, released, watched, and eventually retired.

You do not need a job in the field, a cloud account, or a credit card. You need a laptop, one introductory machine learning course behind you, and the willingness to type commands rather than copy them.

<div class="grid cards" markdown>

-   **New here?**
    Start with the ten-minute readiness check, then your first day.

    [:octicons-arrow-right-24: Check your readiness](prerequisites/index.md)

-   **Ready to begin?**
    Module 01 explains the problem before any tool appears.

    [:octicons-arrow-right-24: Begin Module 01](modules/01-introduction-to-mlops/index.md)

-   **Planning your term?**
    Three routes, from a 16-week intensive to a 40-week part-time pace.

    [:octicons-arrow-right-24: See the roadmap](learning-roadmap/index.md)

-   **Ready to test yourself?**
    Question banks, module exercises, five mini-projects, and the capstone rubric.

    [:octicons-arrow-right-24: Open the practice package](assessments/index.md)

</div>

---

## What you will be able to do

By the end of the course you will be able to:

- **explain** the ML lifecycle, name the artefact each stage produces, and place a failure at the stage that should have caught it;
- **make a project reproducible**, so a stranger can rebuild your environment, data, and results from a clean copy;
- **enforce data quality** with executable checks, versioned datasets, and leakage tests that actually fail;
- **evaluate honestly**, looking past one aggregate number to the slices where a model quietly loses;
- **verify** a system with unit, data, model, integration, and regression tests and say what each cannot catch;
- **deliver** a validated API in a container, gated by CI that refuses a regression;
- **operate**: schedule and retry pipelines, detect drift before users report it, retrain on evidence, roll back safely;
- **assess risk**: threat-model the service, keep secrets out of history, measure disparity, publish an honest model card;
- **hand over** a running system with documentation a colleague can operate, and defend the design when asked "why not simpler?".

The [full outcome map](syllabus/learning-outcomes.md) shows where each is taught and what evidence proves it.

---

## What you build

The course follows one system from an empty folder to a monitored deployment.

**RaviRide** is a fictional ride-hailing company in Lahore. Before a rider books, the app shows an estimated arrival time, produced by a model trained on completed trips. Operations wants that estimate to stay accurate as traffic, weather, and the city change.

The data is synthetic, so mistakes are free. You build `raviride-eta` step by step: repository, validated data, reproducible training, tracked experiments, a model registry, an API, a container, a CI gate, monitoring, and finally a handover package someone else can operate.

[See every artefact and which module produces it](syllabus/course-project-map.md){ .md-button }

---

## The course at a glance

| | |
|---|---|
| **Modules** | 17, from foundations to a production capstone |
| **Guided time** | About 284 hours, including labs and the capstone |
| **Levels** | Foundation, Intermediate, Advanced, Production |
| **Platforms** | Windows 11 with PowerShell 7 first; Linux and macOS alternatives throughout |
| **Cost** | Free and local by default. No paid service is required for any core outcome |
| **Tools** | Python, Git, DVC, MLflow, pytest, FastAPI, Docker, GitHub Actions, Prefect, Evidently |
| **Assessment** | Knowledge checks, guided labs, four mini-projects, one capstone - a suggested self-study framework |

!!! info "Course status: complete"
    **All 17 modules have the full page set**: concepts, worked example, guided lab, independent
    challenge, knowledge check, troubleshooting, and references. Modules 01–14 are backed by the
    RaviRide reference project, whose pipeline, registry, API, and tests were re-run in the final
    audit; not every printed command was re-executed.

    Modules 15–17 state their verification limits on the page. The fairness audit and the
    Kubernetes manifest checker were executed; the optional cluster deployment and hosted CI
    runs were not, because those tools were unavailable in the authoring environment. Nothing is
    marked verified unless it was. Start with the [module index](modules/index.md) or the
    [first-day guide](start-here/index.md).

---

## How the course is organised

Four levels, three tiers. **Level** describes difficulty; **tier** tells you whether you may skip it.

| Level | Modules | What changes |
|---|---|---|
| Foundation | 01-03 | Concepts and first hands-on use; no MLOps background assumed |
| Intermediate | 04-11 | Multi-component workflows: data, experiments, services, automation |
| Advanced | 12-16 | Trade-offs, failure handling, observability, security, scale |
| Production | 17 | Operate and defend a complete system |

Modules marked **Essential** cannot be skipped without breaking later work. **Recommended** modules deepen practice. **Advanced / optional** modules add production realism and can be deferred.

[Browse all 17 modules](modules/index.md){ .md-button .md-button--primary }

---

## How to study

1. **Read a lesson.** Definitions come before use; a new term is explained where it appears.
2. **Do its lab.** Type the commands. Labs are built in parts, so they survive interruption.
3. **Compare with the expected result.** Every lab ends in a check that separates success from near-success.
4. **Break something on purpose.** Each lab includes a realistic fault, so you learn the failure signature.
5. **Answer the knowledge check**, then compare with the key.
6. **Write two sentences** on what you would change, and keep them. The capstone draws on these notes.

Do the labs in order. From Module 04 onward, modules reuse artefacts you built earlier.

---

## Honest about cost and difficulty

- **Free and local by default.** Every core outcome is achievable with open-source tools on your own machine.
- **No account required** beyond a free GitHub account, introduced in Module 02 and used again in Module 12.
- **Cloud is optional and labelled.** Where a cloud service adds realism, it is marked `Paid - optional`, with a local alternative that reaches the same outcome.
- **Heavy labs are labelled** with RAM, disk, and time, and name a lighter route. Module 16 is the heaviest; nothing essential depends on it.

---

## Where this course comes from

It was written for students who will be asked, often in their first job, to keep a model alive rather than to train a new one. It assumes no industry experience and no budget, and it treats operational competence, honesty about limitations, and care for the people affected by a system as part of the subject.

[:octicons-person-24: About the instructor and the course](about/index.md)
