# Detailed Syllabus

This is the authoritative specification of the course. Every module states the same twelve things: what you will be able to do, what you need first, the vocabulary, the tools and why they are used, how long it takes, the guided lab, the independent challenge, how it is assessed, what it depends on, the evidence you produce, and the free or local route if the primary tool is inconvenient.

Module prose, lessons, and lab sheets are written later. This document fixes scope, sequence, and assessment so those lessons cannot quietly contradict each other.

**Reading conventions**

- **Effort** is guided hours: reading plus the guided lab. Independent challenges and revision add roughly 10-20 percent.
- **Tier** is `Essential`, `Recommended`, or `Advanced / optional`. Skipping an Essential module breaks later work.
- **Evidence** is what you keep. It is not "I understood it"; it is a file, log, report, or recorded result that another person could inspect.
- Every lab uses the running `raviride-eta` system described in [course project map](course-project-map.md), except where a module says otherwise.

---

## 01. Introduction to MLOps and the ML lifecycle

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Foundation | 8 hours | Essential | None |

**Learning outcomes**
- Define MLOps and distinguish it from machine learning engineering, data engineering, and DevOps.
- Describe the ML lifecycle end to end and name the artefact each stage produces.
- Place a given failure at the correct lifecycle stage, and explain which control would have caught it.
- Explain what "hidden technical debt" means in ML systems and give three concrete examples.
- Describe the difference between model deployment and model release.

**Required background** — One introductory ML course. No operations experience.

**Key concepts and vocabulary** — model; training versus serving; lifecycle (framing, data, training, evaluation, deployment, monitoring, retraining); artifact; training/serving skew; reproducibility; deployment versus release; feedback loop; hidden technical debt; glue code; pipeline jungle; maturity (manual, automated, continuous).

**Tools and why they are used** — None required. Mermaid for the lifecycle diagram, because diagrams that live in text can be reviewed and versioned. A short Python snippet reproduces "identical code, different result" to make non-determinism tangible before any tooling appears.

**Guided laboratory scenario** — You join RaviRide after an incident: the ETA estimate drifted from 6 minutes to 14 minutes over three weeks and nobody noticed until riders complained. You are given a synthetic timeline (commits, data changes, a holiday, a model retrain, a library upgrade) and must classify each event, build the system's lifecycle diagram, and write a one-page postmortem naming the missing controls.

**Independent practical challenge** — Take any public incident write-up involving a deployed model and map it to the same taxonomy. Identify three controls that were absent and state which module in this course would have supplied each one.

**Assessment** — Knowledge check (10 questions, self-marked) plus the postmortem artefact against a four-criterion rubric: correctness of classification, causal reasoning, named controls, and clarity. This is the first portfolio piece.

**Dependencies** — None. Unlocks Modules 02 and 03.

**Evidence to produce** — Lifecycle diagram (Mermaid source), failure classification table, one-page postmortem, and five glossary entries for terms that were new to you.

**Free or local alternative** — Not applicable; the module requires no software.

---

## 02. Python, Git, CLI, and reproducible environments

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Foundation | 14 hours | Essential | 01 |

**Learning outcomes**
- Create and activate an isolated Python environment, and diagnose the three common reasons activation fails.
- Declare dependencies in a project file, pin them, and explain the difference between a loose and a locked dependency set.
- Explain why "works on my machine" is an environment problem, and prove reproducibility by rebuilding from scratch.
- Use branches, commits, and diffs as a working habit rather than an emergency measure.
- Navigate a project from the command line and read a traceback to its first useful line.

**Required background** — Basic Python and basic Git. This module converts both into reliable habits.

**Key concepts and vocabulary** — interpreter; virtual environment; PATH; dependency resolution; lock file; transitive dependency; `pyproject.toml`; source layout; entry point; branch; merge; diff; `.gitignore`; commit hygiene; deterministic seed.

**Tools and why they are used** — Python 3.11 or 3.12 with the standard `venv` and `pip`, because they exist on every student machine and teach what a lock file is doing. Git for version control; PowerShell 7 as the primary shell; VS Code as an editor, never as a requirement. `uv` is introduced only as an optional faster installer once the standard workflow is understood.

**Guided laboratory scenario** — You create the `raviride-eta` repository skeleton: source layout, project file, pinned environment, test folder, ignore rules, and a first branch. You then receive a colleague's environment that installs cleanly on their machine and fails on yours, and must locate the conflicting pin.

**Independent practical challenge** — Delete your environment, rebuild it from the repository alone, and run the code. Then deliberately break the lock file in two different ways and document the exact error each produces.

**Assessment** — Knowledge check plus a reproducibility checklist review of your own repository: ten binary criteria, each inspectable (for example, "a clean clone installs with one documented command").

**Dependencies** — Module 01. Unlocks everything; no later module can be completed without this one.

**Evidence to produce** — Working repository, `pyproject.toml`, lock file, captured environment listing, repository tree, and a short troubleshooting log of every error you hit and how you fixed it.

**Free or local alternative** — Everything here is free and local. `uv` is optional; if unavailable, `venv` and `pip` are sufficient.

---

## 03. Organizing an ML project and understanding technical debt

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Foundation | 10 hours | Essential | 02 |

**Learning outcomes**
- Lay out an ML project so that data, code, configuration, and outputs are separable.
- Move logic out of notebooks into importable, testable modules without changing behaviour.
- Distinguish configuration from code, and explain why hard-coded paths and parameters become debt.
- Identify technical debt categories in an existing repository and rank them by remediation cost.
- Write a short architecture decision record (ADR) that a reviewer can act on.

**Required background** — Module 02; comfort reading a few hundred lines of Python.

**Key concepts and vocabulary** — repository layout; notebook versus module; coupling; configuration layer; environment variable; secret versus setting; dead code path; glue code; pipeline jungle; ADR; code review; refactoring without behaviour change.

**Tools and why they are used** — Git and Python; `ruff` for fast linting so style stops consuming review attention; `pre-commit` to run checks before a commit exists. No framework is introduced, because a project layout is a convention, not a product.

**Guided laboratory scenario** — RaviRide hands you a 300-line notebook that trains the ETA model, with paths hard-coded to one analyst's laptop. You refactor it into a package (`data`, `features`, `train`, `config`), preserve the original metric exactly, write two ADRs, and produce a debt register of at least five items with severity and estimated fix cost.

**Independent practical challenge** — Take a supplied "before" snapshot of the repository and write a debt register a manager could budget from: each item with symptom, risk, fix, and cost.

**Assessment** — Rubric on the refactor (behaviour preserved, structure justified, no dead code) plus the ADRs and debt register. Marks reward reasoning over volume.

**Dependencies** — Module 02. Unlocks Modules 04 and 05.

**Evidence to produce** — Refactored package, configuration files, two ADRs, debt register, and proof that the refactor preserved the original metric.

**Free or local alternative** — All tools free and local; `pre-commit` is optional if installation is restricted, in which case the checks are run manually and logged.

---

## 04. Data quality, validation, and data versioning

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Intermediate | 14 hours | Essential | 02, 03 |

**Learning outcomes**
- Write explicit expectations for schema, ranges, uniqueness, and cross-field consistency.
- Implement those expectations as executable validation that fails loudly on a corrupt batch.
- Version datasets so that a specific training run can be tied to a specific data state.
- Detect temporal leakage in a feature set and explain why a random split hides it.
- Document dataset provenance, licence, and known limitations.

**Required background** — Modules 02 and 03; pandas basics.

**Key concepts and vocabulary** — data contract; schema; nullability; range and domain checks; referential integrity; distribution expectation; outlier versus error; leakage; temporal split; point-in-time join; content-addressed storage; data lineage; provenance; dataset version.

**Tools and why they are used** — `pandas` for manipulation; `pandera` for declarative dataframe schemas, because validation written as data is easier to read and extend than a wall of `if` statements; DVC for data versioning, because Git should not store binary datasets and DVC records content hashes and lineage instead. Great Expectations is named as the heavier alternative and deliberately not required.

**Guided laboratory scenario** — RaviRide's trip extract gains three defects overnight: negative distances, duplicated trip identifiers, and a pickup zone that no longer exists after a city boundary change. You write eight validation checks, watch the pipeline refuse the batch with a useful message, fix the data, and then track the dataset with DVC so a "clean clone" can retrieve the exact version used for training. Finally you add one check that catches a feature computed from future data.

**Independent practical challenge** — Add a leakage test that fails on a deliberately contaminated feature, and write a two-paragraph provenance note explaining, to a new colleague, which data produced the current model and what would invalidate it.

**Assessment** — Validation module reviewed against a criterion list (specificity of messages, coverage, failure behaviour), plus a failure report showing the bad batch rejected and the good batch accepted.

**Dependencies** — Modules 02 and 03. Unlocks Module 05.

**Evidence to produce** — Validation code, pass and fail logs, `.dvc` files and data checksum, dataset `README` with licence and limitations, leakage note.

**Free or local alternative** — All primary tools are free and local. DVC can use a local directory as its remote, so no cloud storage is needed; the lab documents exactly that setup.

---

## 05. Reproducible model training and pipeline design

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Intermediate | 16 hours | Essential | 04 |

**Learning outcomes**
- Write a deterministic training entry point that produces the same metrics twice from the same inputs.
- Separate feature engineering into a reusable transformer that can also run at serving time.
- Express training as a pipeline of stages with declared inputs, outputs, and parameters.
- Explain cache invalidation: why changing one parameter reruns only the affected stages.
- Measure and record runtime and resource use for each stage.

**Required background** — Modules 03 and 04; scikit-learn `Pipeline` and `ColumnTransformer`.

**Key concepts and vocabulary** — determinism; seed control; reproducibility versus replicability; feature transformer; train/serve consistency; stage; dependency; directed acyclic graph; cache key; invalidation; idempotency; artefact; model signature; baseline model.

**Tools and why they are used** — scikit-learn for the model and transformers, chosen because the operational lesson does not need a complex model; DVC pipelines (`dvc.yaml`, `dvc repro`, `dvc dag`) for stage graphs, because they encode dependencies in a file that Git versions and they cache aggressively, which makes the concept of invalidation visible. `joblib` for artefact serialisation.

**Guided laboratory scenario** — You turn the refactored training code into four stages: prepare, featurise, train, evaluate. First run builds everything; second run is a full cache hit; changing one hyperparameter reruns only training and evaluation. You then add a derived feature and show, from the DAG and timings, exactly which stages were invalidated.

**Independent practical challenge** — Prove reproducibility rather than assert it: run the pipeline twice from a clean state, record metrics and hashes, and demonstrate byte-identical metrics. Then explain one source of remaining non-determinism you could not remove and why.

**Assessment** — Pipeline runs from a clean state on another machine or fresh clone; assessment of the DAG, the invalidation explanation, and the reproducibility report.

**Dependencies** — Module 04. Unlocks Modules 06 and 08.

**Evidence to produce** — `dvc.yaml`, `dvc.lock`, metrics file, exported DAG image, two-run comparison table, runtime log.

**Free or local alternative** — Entirely local and free. If DVC cannot be installed, the lab documents a reduced fallback: a Python driver script plus recorded file hashes, which preserves the learning outcome but loses caching.

---

## 06. Experiment tracking and model evaluation using MLflow

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Intermediate | 14 hours | Essential | 05 |

**Learning outcomes**
- Record parameters, metrics, artefacts, and dataset version for every training run.
- Compare runs and justify a selection on evidence rather than the best single number.
- Design an evaluation suite that includes slice-level metrics, not only an aggregate.
- Recognise when a model has been selected by overfitting the evaluation set.
- Establish and record a baseline that future candidates must beat.

**Required background** — Module 05; scikit-learn metrics and basic model evaluation.

**Key concepts and vocabulary** — run; experiment; parameter versus metric versus artefact; tag; nested run; baseline; hold-out versus temporal evaluation; slice or segment metric; error distribution; percentile latency of error (p95); metric selection (MAE versus RMSE); evaluation leakage.

**Tools and why they are used** — MLflow with a local tracking store, because it is open source, runs on a laptop without a server, and is widely used in industry, so the concepts transfer. Alternatives are named honestly: Weights & Biases (free tier, account required) and Neptune (paid). The lesson explains why a spreadsheet is not tracking and where it actually fails.

**Guided laboratory scenario** — Six runs, varying feature sets and hyperparameters, are tracked against RaviRide data. You compare them, notice the aggregate winner is worse in two peripheral zones and at peak hours, and record that finding as part of the evaluation rather than a footnote. You log the dataset version with each run and register the chosen model as a baseline.

**Independent practical challenge** — Produce an evaluation report that would stop a plausible-looking model from shipping: find the slice where it regresses, quantify the business consequence, and state the decision you would defend.

**Assessment** — Knowledge check plus an evaluation report assessed on evidence quality, slice analysis, and honesty about limitations. The report becomes a capstone appendix.

**Dependencies** — Module 05. Unlocks Modules 07 and 09.

**Evidence to produce** — MLflow run table or export, comparison view, evaluation report with slice metrics, baseline record.

**Free or local alternative** — MLflow is free and local by default. No account, server, or database is required; the lab uses a local store and documents the trade-offs of that choice.

---

## 07. Unit, data, model, integration, and regression testing

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Intermediate | 16 hours | Essential | 05, 06 |

**Learning outcomes**
- Choose the right test type for a given risk, and explain what each type cannot catch.
- Write unit tests for feature transformations, including edge cases such as missing values.
- Write data tests that run against fixtures rather than the live dataset.
- Write behavioural model tests: invariance, directional expectation, and minimum performance.
- Add a regression gate that fails when a metric degrades beyond a stated tolerance.

**Required background** — Modules 05 and 06; ability to read a traceback and run `pytest` once.

**Key concepts and vocabulary** — test pyramid for ML; fixture; parametrisation; assertion; tolerance; flaky test; behavioural test; invariance or metamorphic test; directional test; golden dataset; regression gate; coverage and its limits; test that proves nothing.

**Tools and why they are used** — `pytest` for all test layers, so one runner and one mental model; `pytest-cov` to expose untested branches; `pandera` reused from Module 04 for data tests. Heavier model-testing suites are named but not required, because they obscure the fact that most useful ML tests are small and hand-written.

**Guided laboratory scenario** — You add four layers of tests to the ETA pipeline. A deliberately introduced unit conversion bug (kilometres treated as miles) passes every unit test but fails an invariance test, which is the lesson: tests that only check shapes and types do not check meaning. You then set a regression gate at a stated tolerance and watch a degraded model fail it.

**Independent practical challenge** — Write the smallest test that would have caught a described production bug, and justify why a broader test would have been worse.

**Assessment** — Test suite reviewed for meaningfulness (would each test fail if the behaviour broke?), plus a short strategy note on the limits of testing.

**Dependencies** — Modules 05 and 06. Unlocks Modules 08 and 12.

**Evidence to produce** — Test files, coverage report, before/after failure logs, regression gate definition, test strategy note.

**Free or local alternative** — Fully free and local; no service involved.

---

## 08. Pipeline automation and workflow dependencies

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Intermediate | 12 hours | Recommended | 05, 07 |

**Learning outcomes**
- Run the entire pipeline with one documented command.
- Encode dependencies so a partial rerun is correct, not merely faster.
- Use commit-time hooks to stop broken or oversized changes early.
- Interpret exit codes and design failures that stop the pipeline rather than warn and continue.
- Recover from a mid-pipeline failure without corrupting artefacts.

**Required background** — Modules 05 and 07.

**Key concepts and vocabulary** — automation; task graph; fan-out and fan-in; cache; failure propagation; fail-fast versus fail-safe; exit code; hook; dry run; resumability; runbook; non-interactive execution.

**Tools and why they are used** — The DVC stage graph from Module 05 as the automation backbone, because it already encodes dependencies; `pre-commit` for local hooks; a small PowerShell entry script as the single documented command. `make` is discussed and not used: it is not installed by default on Windows 11 and would add a platform dependency for no pedagogical gain.

**Guided laboratory scenario** — You reduce the project to one command that prepares data, validates it, trains, evaluates, and writes metrics. Then you kill the process mid-training, restart, and show what is reused and what is rebuilt. You add hooks that reject a file over 5 MB and a trailing-whitespace change, and record which hook caught which mistake.

**Independent practical challenge** — Halve the pipeline runtime without changing its outputs, and prove the outputs are unchanged. Document the measurement, not the intuition.

**Assessment** — Automation evidence (single command, logs, exit codes), failure-recovery log, and the measured runtime comparison.

**Dependencies** — Modules 05 and 07. Unlocks Modules 09, 12, and 13.

**Evidence to produce** — Entry script, hook configuration, timing table before and after, recovery log, one-page runbook.

**Free or local alternative** — Free and local. If hooks cannot be installed, the checks are run manually and the difference is documented.

---

## 09. Model artifacts, registries, promotion, and lifecycle management

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Intermediate | 14 hours | Essential | 06, 08 |

**Learning outcomes**
- Package a model with its signature, preprocessing, and metadata so it can be loaded without the training code.
- Register model versions and distinguish versions from aliases.
- Define promotion gates that a candidate must pass before serving traffic.
- Perform a rollback to a previous version and measure how long it takes.
- Explain model lineage from dataset hash to deployed version.

**Required background** — Modules 06 and 08.

**Key concepts and vocabulary** — artefact versus model; model signature; registry; version; alias; stage (deprecated concept); promotion; approval gate; champion and challenger; immutability; rollback; lineage; compatibility; model card stub.

**Tools and why they are used** — MLflow Model Registry locally, because it demonstrates versions, aliases, and lineage without a cloud account. The module teaches aliases rather than stages, since stage labels are deprecated in current MLflow. Alternatives named: cloud registries (paid, account required) and plain artefact directories (what most teams actually start with, and why that fails at scale).

**Guided laboratory scenario** — Three candidate versions are registered. One passes all gates and is aliased `champion`; one fails a slice-level gate and is blocked; the third is promoted then rolled back after an injected defect. You record the rollback procedure and its elapsed time, and trace the champion back to a dataset hash and a commit.

**Independent practical challenge** — Write a promotion policy with at least three measurable gates, implement it, and prove a failing model cannot reach `champion` even when a human asks nicely.

**Assessment** — Registry evidence, promotion policy, rollback rehearsal log, and a lineage trace. Rubric rewards gates that are automatic and measurable, not prose promises.

**Dependencies** — Modules 06 and 08. Unlocks Modules 10, 12, and 16.

**Evidence to produce** — Version table, alias history, blocked-promotion log, rollback timing, promotion policy document, lineage diagram.

**Free or local alternative** — MLflow registry is local and free. If unavailable, a documented file-based registry with a JSON manifest preserves the concepts but not the tooling experience; the lab labels this as reduced.

---

## 10. Model serving and REST APIs using FastAPI

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Intermediate | 16 hours | Essential | 09 |

**Learning outcomes**
- Load a model once at start-up and serve predictions over HTTP.
- Define and validate a request and response contract, rejecting bad input with a useful error.
- Distinguish client errors from server errors and choose status codes deliberately.
- Measure latency and report percentiles rather than an average.
- Detect and fix train/serve skew using a contract test.

**Required background** — Module 09; basic HTTP and JSON.

**Key concepts and vocabulary** — endpoint; request and response schema; payload; pydantic model; 4xx versus 5xx; validation error; contract; cold start; latency percentile (p50, p95, p99); health versus readiness; API versioning; idempotency; feature order; train/serve skew.

**Tools and why they are used** — FastAPI with Uvicorn, because schema validation and generated OpenAPI documentation are built in, so the contract is executable rather than a document; pydantic for the schema; `pytest` with `TestClient` for integration tests. Flask is discussed as the simpler alternative and rejected for this course because validation would become hand-written. BentoML and KServe are named as production serving frameworks and deferred to Module 16.

**Guided laboratory scenario** — You serve the champion ETA model with `/health`, `/predict`, and `/model-info`. Invalid payloads return 422 with a specific message. Then a contract test reveals that the API assembles features in a different order from training and scales distance differently, producing plausible but wrong estimates; you locate it with a single-record comparison against the training pipeline and fix it.

**Independent practical challenge** — Add a second prediction endpoint for a batch of trips, keep one model load, and show that p95 latency stays within a stated budget. Document where the budget came from.

**Assessment** — Running service with tests, contract documentation, error examples, latency table, and the skew investigation report.

**Dependencies** — Module 09. Unlocks Modules 11, 12, and 14.

**Evidence to produce** — Application code, OpenAPI schema, sample requests and responses including failures, latency measurements, skew report.

**Free or local alternative** — Entirely free and local; no hosting service is required.

---

## 11. Docker images, containers, and deployment environments

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Intermediate | 14 hours | Essential | 10 |

**Learning outcomes**
- Write a Dockerfile that installs dependencies reproducibly and runs as a non-root user.
- Explain image layers and use build cache deliberately.
- Reduce image size with a multi-stage build and measure the difference.
- Run the API and the tracking server together with Docker Compose.
- Explain why a container is not a virtual machine, and what it does and does not guarantee.

**Required background** — Module 10; comfort running commands in a terminal.

**Key concepts and vocabulary** — image; container; layer; build cache; tag; base image; entrypoint versus command; volume; bind mount; registry; `.dockerignore`; environment parity; image size; non-root user; reproducibility of runtime.

**Tools and why they are used** — Docker Desktop with the WSL 2 backend on Windows 11, because it is the standard local container runtime and integrates with the rest of the course. Podman is the documented free alternative. The module is explicit about licensing: Docker Desktop is free for personal use and education and requires a paid subscription in large organisations.

**Guided laboratory scenario** — You containerise the ETA API. The first build is 1.2 GB and takes minutes; after a multi-stage rebuild with a slim base and no build tools in the final image, you compare size and start time. You add Compose to run the API beside the MLflow tracking store, then run the test suite inside the container to prove the environment travels.

**Independent practical challenge** — Make the image build reproducibly pinned and as small as you reasonably can, then document the one thing you chose not to optimise and why.

**Assessment** — Dockerfile review against a checklist (pinned base, non-root, ignore file, layer order, health check), build logs, size and start-time comparison, and a short environment-parity note.

**Dependencies** — Module 10. Unlocks Modules 12 and 16.

**Evidence to produce** — Dockerfile, `.dockerignore`, Compose file, build and run logs, image size table, parity note.

**Free or local alternative** — Docker Desktop is free for personal and educational use; Podman is a drop-in alternative. If containerisation is impossible on a given machine, a reduced path uses a pinned environment plus a documented parity checklist, and the lab states plainly which outcome is lost.

---

## 12. CI/CD and ML validation workflows using GitHub Actions

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Advanced | 18 hours | Essential | 07, 08, 11 |

**Learning outcomes**
- Write a workflow that runs on pull requests and on merges to the main branch.
- Run lint, unit tests, data validation, and a training smoke test as separate, diagnosable steps.
- Cache dependencies and measure the runtime improvement.
- Enforce a model quality gate that blocks a regression before merge.
- Handle secrets correctly and explain why a token in a log is an incident.

**Required background** — Modules 07, 08, and 11; a GitHub account.

**Key concepts and vocabulary** — continuous integration; continuous delivery versus deployment; workflow; job; step; runner; trigger; matrix; cache; artefact; required status check; branch protection; quality gate; secret versus variable; least-privilege token; flaky pipeline; reproducibility on a clean runner.

**Tools and why they are used** — GitHub Actions, because it is free for public repositories, requires no infrastructure, and is the most common CI system students will meet. The module distinguishes what the *file* can do from what a *repository setting* can do (branch protection is configured in GitHub, not in YAML), and notes that an instructor or repository owner must enable it. `act` is optional for local runs.

**Guided laboratory scenario** — You build a pull-request pipeline: lint, unit and data tests, a fast training smoke run, a metric gate against the recorded baseline, and artefact upload. You then submit a deliberately degraded model and watch the gate block it, reading the failure from the log rather than from a dashboard. Finally you cache the environment and compare runtimes.

**Independent practical challenge** — Make the pipeline fail for the right reason three times in a row: a data schema break, a unit regression, and a metric regression. Each failure must name the offending artefact in its log.

**Assessment** — Workflow file review, evidence of one green and three correctly red runs, runtime comparison, and a written explanation of which checks must be required before merge.

**Dependencies** — Modules 07, 08, and 11. Unlocks Modules 13, 14, and 16.

**Evidence to produce** — Workflow YAML, run logs or screenshots, gate-failure evidence, timing table, branch-protection recommendation.

**Free or local alternative** — Free for public repositories, with generous free minutes for private ones. GitLab CI is described as an equivalent alternative. If a student cannot use GitHub, the workflow is written and validated locally with `act` where possible, and the limitation is stated.

---

## 13. Workflow orchestration and scheduled pipelines

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Advanced | 16 hours | Recommended | 08, 09, 12 |

**Learning outcomes**
- Explain when CI is the wrong tool and an orchestrator is required.
- Build a flow with explicit dependencies, a schedule, and retry policy.
- Make tasks idempotent so a retry cannot corrupt state.
- Diagnose a partial failure and backfill three missed days correctly.
- Set a concurrency limit and explain why unbounded parallelism is a production incident.

**Required background** — Modules 08, 09, and 12.

**Key concepts and vocabulary** — orchestrator; flow; task; DAG versus imperative flow; scheduler; trigger; retry; exponential backoff; idempotency; backfill; concurrency limit; SLA; dead-letter or failure notification; observability of runs.

**Tools and why they are used** — Prefect 3 locally, because it is Python-native, installs without a cluster, and makes retries and scheduling visible in a UI. Airflow is discussed as the industry standard and deliberately deferred: its scheduler, metadata database, and webserver are heavy for a laptop and teach infrastructure before concepts. Windows Task Scheduler plus a Python entry point is the minimal fallback.

**Guided laboratory scenario** — You orchestrate the nightly retrain: fetch, validate, featurise, train, evaluate, register, notify. You schedule it, force a failure in featurisation, watch retries with backoff, then backfill three missed days without duplicating registered versions. You add a concurrency limit after deliberately triggering two runs at once.

**Independent practical challenge** — Add a conditional branch that retrains only when new data or drift exceeds a threshold, and prove both branches execute under the right conditions.

**Assessment** — Flow code, run history, retry and backfill evidence, schedule documentation, and a written justification of retry counts and limits.

**Dependencies** — Modules 08, 09, and 12. Unlocks Modules 14 and 17.

**Evidence to produce** — Flow definitions, run history export, failure and retry logs, backfill record, scheduling note, concurrency configuration.

**Free or local alternative** — Prefect is free and local; no Prefect Cloud account is required. If it cannot be installed, the Task Scheduler path preserves scheduling and idempotency lessons but not the retry UI; the lab labels this as reduced.

---

## 14. Prediction monitoring, data drift, model drift, and retraining

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Advanced | 18 hours | Essential | 10, 12, 13 |

**Learning outcomes**
- Define the signals that indicate a model is failing before labels arrive.
- Distinguish data drift, prediction drift, and concept drift, with an example of each.
- Compute drift between reference and current batches and choose thresholds deliberately.
- Design a retraining trigger with guardrails that prevent a bad automatic release.
- Write an alert with an owner, a threshold, and a first diagnostic step.

**Required background** — Modules 10, 12, and 13; basic statistics (distributions, percentiles).

**Key concepts and vocabulary** — observability (logs, metrics, traces); SLI and SLO; input drift; prediction drift; concept drift; label delay; population stability index; KS test; alert fatigue; threshold; shadow deployment; retraining cadence versus trigger; feedback loop poisoning; rollback criterion.

**Tools and why they are used** — Evidently for drift reports, because it produces both a machine-readable result and a human-readable report from the same call; scikit-learn and pandas for reference statistics. Prometheus and Grafana are offered as an optional heavy path using Compose, and a log-based metrics report is the default so no extra services are required. Commercial observability platforms are named as optional and paid.

**Guided laboratory scenario** — RaviRide's monsoon season begins. You replay four weeks of batches: week one is stable, week two shows input drift in road-speed features, week three shows prediction drift without label drift, week four brings delayed labels confirming error growth. You compute drift reports, set a threshold, wire an alert, trigger a retrain, and verify the retrained model improves the affected slice without regressing another.

**Independent practical challenge** — Write a monitoring plan for a model you did not build, given only its inputs, outputs, and refresh cadence: four signals, thresholds with justification, and an on-call first action for each.

**Assessment** — Drift reports, threshold justification table, alert configuration, retraining decision memo, and a post-retrain comparison. Rubric rewards precision of thresholds and honesty about label delay.

**Dependencies** — Modules 10, 12, and 13. Unlocks Module 17.

**Evidence to produce** — Drift report files, monitoring plan, alert rule, retraining memo, before/after metric comparison.

**Free or local alternative** — Evidently is free and local. The Prometheus/Grafana path is optional and heavy; the default path uses files and a small plotting script, which is sufficient for every assessed outcome.

---

## 15. Security, privacy, governance, fairness, and responsible deployment

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Advanced | 14 hours | Recommended | 09, 10, 11 |

**Learning outcomes**
- Threat-model a prediction service and rank findings by exploitability and impact.
- Keep secrets out of code and history, detect a leak, and rotate a credential.
- Scan dependencies for known vulnerabilities and interpret the result without panic.
- Measure error disparity across meaningful groups and explain what the metric does not prove.
- Write a model card that a non-specialist can use to judge whether to trust the system.

**Required background** — Modules 09, 10, and 11. No security background assumed.

**Key concepts and vocabulary** — threat model; STRIDE; attack surface; authentication versus authorisation; least privilege; secret rotation; dependency vulnerability; software supply chain; personal data; data minimisation; purpose limitation; consent; proxy variable; fairness metric (demographic parity, equal opportunity); disparate error; model card; data card; audit trail; retention.

**Tools and why they are used** — `gitleaks` to detect committed secrets, because seeing a real finding is more instructive than a lecture; `pip-audit` for dependency vulnerabilities; GitHub encrypted secrets for storage; `fairlearn` for disparity metrics. Commercial scanners are named as options, not requirements.

**Guided laboratory scenario** — You threat-model the ETA API, then scan a supplied repository that contains a committed token, confirm the finding, rotate the credential, and rewrite history guidance without actually rewriting shared history. You measure ETA error across central and peripheral zones, discover a systematic gap, and write a model card that states it plainly alongside the aggregate metric.

**Independent practical challenge** — Propose three mitigations for the worst disparity, with cost, expected effect, and residual risk, and recommend one. The recommendation must be defensible to both an engineer and a manager.

**Assessment** — Threat model, scan evidence, model card against a published checklist, fairness analysis, and the mitigation memo. Rubric rewards specificity and honesty; vague statements such as "improve fairness" score zero.

**Dependencies** — Modules 09, 10, and 11. Unlocks Module 17.

**Evidence to produce** — STRIDE table with mitigations, scan reports, model card, fairness metrics table, mitigation memo, access-control sketch.

**Free or local alternative** — All primary tools are free and local. No cloud key-management service is required; local environment variables and GitHub secrets cover every assessed outcome.

---

## 16. Cloud deployment concepts, Kubernetes, scaling, and reliability

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Advanced | 22 hours | Advanced / optional | 11, 12, 14 |

**Learning outcomes**
- Explain the trade-offs between virtual machines, managed platforms, and orchestrators, with cost and control implications.
- Read and write Kubernetes manifests for a stateless prediction service.
- Deploy locally to a real cluster, configure probes and resource limits, and explain what each prevents.
- Provision infrastructure as code and explain why state files are both necessary and dangerous.
- Plan a rollout with abort criteria, perform a rollback, and estimate monthly cost.

**Required background** — Modules 11, 12, and 14.

**Key concepts and vocabulary** — cluster; node; pod; deployment; service; ingress; config map; secret; resource request and limit; liveness and readiness probe; horizontal scaling; blue-green; canary; infrastructure as code; state; blast radius; SLO; error budget; cost attribution; managed versus self-hosted.

**Tools and why they are used** — `kind` for a local Kubernetes cluster, because it runs inside Docker and needs no cloud account; `kubectl`; Terraform with a local provider, so infrastructure as code is practised without provisioning anything billable. Managed Kubernetes and cloud runtimes are described and marked `Paid - optional`. The module is explicit that this is the heaviest part of the course.

**Guided laboratory scenario** — You deploy the containerised API to a local cluster with readiness and liveness probes, resource limits, and two replicas. You scale manually, observe a rolling update, then perform a rollback after a deliberately broken image. You provision the same local service with Terraform, inspect the plan, and apply it. Finally you complete a cost worksheet for the equivalent managed deployment.

**Independent practical challenge** — Write a rollout plan with measurable abort criteria, rehearse the rollback, record elapsed time, and estimate the monthly cost of running the service with realistic traffic assumptions.

**Assessment** — Manifests reviewed for correctness and safety, rollout and rollback logs with timings, Terraform plan output, reliability memo defining at least two SLOs.

**Dependencies** — Modules 11, 12, and 14. Unlocks Module 17 (for the production variant of the capstone).

**Evidence to produce** — Kubernetes manifests, `kubectl` output, Terraform configuration and plan, rollback log, SLO definitions, cost worksheet.

**Free or local alternative** — Entire local path is free: `kind` plus the Terraform Docker provider. This module is `Heavy` (8 GB RAM or more, 10 GB disk). Cloud is strictly optional; without a cluster, the conceptual path uses Compose plus a written mapping exercise, and the lab states which outcomes are reduced.

---

## 17. Advanced MLOps capstone integrating the entire lifecycle

| Level | Effort | Tier | Prerequisites |
|---|---|---|---|
| Production | 48 hours | Capstone | All essential modules; recommended modules strengthen it |

**Learning outcomes**
- Operate a complete lifecycle: data validation, reproducible training, tracking, registration, serving, containerisation, CI, orchestration, and monitoring.
- Hand the system to another person using documentation alone.
- Diagnose an injected production incident using evidence, then write a postmortem.
- Defend design trade-offs against a reviewer who asks "why not simpler?" and "what breaks at ten times the load?".
- State honestly what the system does not protect against.

**Required background** — Modules 01-14 at minimum; 15 and 16 for the full variant.

**Key concepts and vocabulary** — integration; operational readiness; runbook; incident; severity; postmortem; handover; service ownership; trade-off; residual risk; technical debt repayment; cost of operation.

**Tools and why they are used** — No new tool. The capstone is deliberately tool-free so that integration, judgement, and communication are the subject. Reusing the existing stack is part of the assessment.

**Guided laboratory scenario** — Two supervised sessions: a scoping workshop that forces the capstone into a defined system boundary, and an incident simulation in which an instructor or a supplied script injects a fault (stale model, corrupted feature, failed rollback) and you diagnose it under time pressure using your own monitoring and runbook.

**Independent practical challenge** — Build and hand over the system. The full brief, artefact list, and rubric are in the [course project map](course-project-map.md) and [assessment framework](assessment-framework.md). Two variants exist: a **Core capstone** using only essential modules, and a **Full capstone** adding orchestration, security, and deployment depth.

**Assessment** — Weighted rubric out of 100 across seven artefacts and six cross-cutting criteria, plus a written or oral defence. Acceptance criteria are measurable: reproducible from a clean clone, gate demonstrably blocks a regression, rollback demonstrated and timed, runbook sufficient for a peer.

**Dependencies** — All essential modules; recommended modules strengthen it.

**Evidence to produce** — A repository, a rerunnable pipeline, a registry with promotion history, a served and containerised API, a CI pipeline with a real gate, a monitoring view with alerts, security and fairness artefacts, runbooks, a model card, an incident postmortem, and a defence document.

**Free or local alternative** — The Core capstone is entirely local and free. The Full capstone's cloud extension is optional; its local equivalent uses the Module 16 local cluster path.

---

## Cross-cutting topics

These are required by the course but do not each own a module. Each is introduced where it first becomes necessary and revisited where it is used again.

| Topic | First taught | Reused in |
|---|---|---|
| Feature engineering | 05 | 06, 10 (train/serve consistency), 17 |
| Feature stores | 09, conceptually | 13, 16 (optional lab only) |
| Infrastructure as code | 16 | 17 |
| Secrets management | 15 | 12, 16, 17 |
| Model and data lineage | 04 | 09, 13, 17 |
| Rollback | 09 | 12, 16, 17 |
| Reproducibility | 02 | 05, 07, 12, 17 |
| Cost management | 01 (concept) | 16, 17 |
| Configuration management | 03 | 05, 12, 16 |
| Documentation and handover | 03 | every module; assessed in 17 |

## Deliberate exclusions

Stated so that scope does not creep, and so students know what they are not being taught here:

- **Deep learning training at scale.** GPUs, distributed training, and model parallelism are out of scope; the operational principles transfer, but the infrastructure does not.
- **Feature store products, service meshes, and multi-cluster orchestration.** Introduced as concepts only, because they solve problems a single-team system does not yet have.
- **Vendor certifications and product-specific administration.** The course teaches transferable practice, not exam objectives.
- **Data engineering at scale.** Batch and stream processing frameworks are named, not taught; the course assumes a dataset, not a data platform.
- **Model research and architecture selection.** Models stay simple on purpose.
