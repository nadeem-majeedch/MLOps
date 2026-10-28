# All Modules

Seventeen modules, studied in order. Each page is the module brief: why it exists, what you will be able to do, the tools it uses, the lab you will run, and the evidence you keep.

!!! info "Where the course is up to"
    All **17 modules** have the full page set: concepts, worked example, guided lab, independent
    challenge, knowledge check, troubleshooting, and references. Modules 01–14 were run end to
    end against the RaviRide reference project.

    Modules 15–17 state their verification limits on the page. The fairness audit and the
    Kubernetes manifest checker were executed; the optional cluster deployment and hosted CI
    runs were not, and are marked as not run. Nothing is marked verified unless it was.

## Modules 01–17: complete materials

| # | Module | Start | Lab | Check |
|---|---|---|---|---|
| 01 | MLOps foundations | [Overview](01-introduction-to-mlops/index.md) | [Lab](01-introduction-to-mlops/lab.md) | [Knowledge check](01-introduction-to-mlops/knowledge-check.md) |
| 02 | Python, Git, CLI, environments | [Overview](02-python-git-cli-environments/index.md) | [Lab](02-python-git-cli-environments/lab.md) | [Knowledge check](02-python-git-cli-environments/knowledge-check.md) |
| 03 | Project organization and debt | [Overview](03-project-organization/index.md) | [Lab](03-project-organization/lab.md) | [Knowledge check](03-project-organization/knowledge-check.md) |
| 04 | Data quality and versioning | [Overview](04-data-quality-versioning/index.md) | [Lab](04-data-quality-versioning/lab.md) | [Knowledge check](04-data-quality-versioning/knowledge-check.md) |
| 05 | Reproducible training | [Overview](05-reproducible-training/index.md) | [Lab](05-reproducible-training/lab.md) | [Knowledge check](05-reproducible-training/knowledge-check.md) |
| 06 | Experiment tracking | [Overview](06-experiment-tracking/index.md) | [Lab](06-experiment-tracking/lab.md) | [Knowledge check](06-experiment-tracking/knowledge-check.md) |
| 07 | Testing ML systems | [Overview](07-testing-ml-systems/index.md) | [Lab](07-testing-ml-systems/lab.md) | [Knowledge check](07-testing-ml-systems/knowledge-check.md) |
| 08 | Pipeline automation | [Overview](08-pipeline-automation/index.md) | [Lab](08-pipeline-automation/lab.md) | [Knowledge check](08-pipeline-automation/knowledge-check.md) |
| 09 | Model registry and lifecycle | [Overview](09-model-registry/index.md) | [Lab](09-model-registry/lab.md) | [Knowledge check](09-model-registry/knowledge-check.md) |
| 10 | Serving with FastAPI | [Overview](10-model-serving/index.md) | [Lab](10-model-serving/lab.md) | [Knowledge check](10-model-serving/knowledge-check.md) |
| 11 | Docker and containers | [Overview](11-docker-containers/index.md) | [Lab](11-docker-containers/lab.md) | [Knowledge check](11-docker-containers/knowledge-check.md) |
| 12 | CI/CD for ML | [Overview](12-ci-cd/index.md) | [Lab](12-ci-cd/lab.md) | [Knowledge check](12-ci-cd/knowledge-check.md) |
| 13 | Workflow orchestration | [Overview](13-orchestration/index.md) | [Lab](13-orchestration/lab.md) | [Knowledge check](13-orchestration/knowledge-check.md) |
| 14 | Monitoring and drift | [Overview](14-monitoring-drift/index.md) | [Lab](14-monitoring-drift/lab.md) | [Knowledge check](14-monitoring-drift/knowledge-check.md) |
| 15 | Security and governance | [Overview](15-security-governance/index.md) | [Lab](15-security-governance/lab.md) | [Knowledge check](15-security-governance/knowledge-check.md) |
| 16 | Cloud and Kubernetes | [Overview](16-cloud-kubernetes/index.md) | [Lab](16-cloud-kubernetes/lab.md) | [Knowledge check](16-cloud-kubernetes/knowledge-check.md) |
| 17 | Capstone | [Overview](17-capstone/index.md) | [Lab](17-capstone/lab.md) | [Knowledge check](17-capstone/knowledge-check.md) |

Each module's pages are also in the navigation under its own section, so you can move between
concepts, lab, and reference without returning here.

---

## How to read a module page

| Section | What it tells you |
|---|---|
| Meta table | Level, effort in hours, tier, prerequisites, tools, cost |
| Why this module exists | The failure it prevents, in plain language |
| What you will be able to do | Outcomes you can check yourself against |
| Key concepts | Vocabulary to watch for; definitions in the [glossary](../glossary/index.md) |
| Guided lab | The scenario and what you will build, with a stable page anchor for the lab catalogue |
| Independent challenge | The task that is not step-by-step |
| Assessment and evidence | What is marked, and what you keep |
| Where this leads | The next dependency |

**Tier** matters more than level when you are short of time: `Essential` cannot be skipped, `Recommended` deepens practice, `Advanced / optional` adds realism.

---

## Stage 1 - Beginner

| # | Module | Level | Hours | Tier |
|---|---|---|---|---|
| 01 | [Introduction to MLOps and the ML lifecycle](01-introduction-to-mlops/index.md) | Foundation | 8 | Essential |
| 02 | [Python, Git, CLI, and reproducible environments](02-python-git-cli-environments/index.md) | Foundation | 14 | Essential |
| 03 | [Organizing an ML project and understanding technical debt](03-project-organization/index.md) | Foundation | 10 | Essential |

**At the end of this stage** you can explain how models fail in production, and you have a project that a stranger could install and run.

## Stage 2 - Intermediate

| # | Module | Level | Hours | Tier |
|---|---|---|---|---|
| 04 | [Data quality, validation, and data versioning](04-data-quality-versioning/index.md) | Intermediate | 14 | Essential |
| 05 | [Reproducible model training and pipeline design](05-reproducible-training/index.md) | Intermediate | 16 | Essential |
| 06 | [Experiment tracking and model evaluation using MLflow](06-experiment-tracking/index.md) | Intermediate | 14 | Essential |
| 07 | [Unit, data, model, integration, and regression testing](07-testing-ml-systems/index.md) | Intermediate | 16 | Essential |
| 08 | [Pipeline automation and workflow dependencies](08-pipeline-automation/index.md) | Intermediate | 12 | Recommended |
| 09 | [Model artifacts, registries, promotion, and lifecycle management](09-model-registry/index.md) | Intermediate | 14 | Essential |
| 10 | [Model serving and REST APIs using FastAPI](10-model-serving/index.md) | Intermediate | 16 | Essential |
| 11 | [Docker images, containers, and deployment environments](11-docker-containers/index.md) | Intermediate | 14 | Essential |

**At the end of this stage** a model is registered, served in a container, and blocked from promotion when it fails a gate.

## Stage 3 - Advanced and production

| # | Module | Level | Hours | Tier |
|---|---|---|---|---|
| 12 | [CI/CD and ML validation workflows using GitHub Actions](12-ci-cd/index.md) | Advanced | 18 | Essential |
| 13 | [Workflow orchestration and scheduled pipelines](13-orchestration/index.md) | Advanced | 16 | Recommended |
| 14 | [Prediction monitoring, data drift, model drift, and retraining](14-monitoring-drift/index.md) | Advanced | 18 | Essential |
| 15 | [Security, privacy, governance, fairness, and responsible deployment](15-security-governance/index.md) | Advanced | 14 | Recommended |
| 16 | [Cloud deployment concepts, Kubernetes, scaling, and reliability](16-cloud-kubernetes/index.md) | Advanced | 22 | Advanced / optional |
| 17 | [Advanced MLOps capstone](17-capstone/index.md) | Production | 48 | Capstone |

**Total: about 284 guided hours.**

---

## If you are short of time

Take the essential path: Modules 01-07, 09-12, 14, and the Core capstone. That is about 200 hours and still reaches every core outcome except the scaling and governance depth added by 15 and 16.

Do not drop Modules 04, 07, or 14. Each is the only place its outcome is taught properly, and the capstone assumes all three.

[See the routes and schedules](../learning-roadmap/index.md){ .md-button }
