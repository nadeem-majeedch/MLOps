# Progress Tracker

A course this long is completed in small, dated steps, not by enthusiasm. This page is the step list.

!!! warning "Ticks on this site do not save"
    A documentation page cannot remember your progress. Copy this page into your own notes,
    a fork of the repository, or a plain text file, and tick items there. The act of copying
    it is itself useful: it forces you to look at what the whole course asks of you.

---

## How to use it

1. **Copy** the sections you are working on into your own file.
2. **Date** each completed line. Undated ticks turn into optimistic fiction.
3. **Do not tick "evidence" until the artefact exists** somewhere you could show a stranger.
4. **Read the gate** before moving to the next stage. The gates are in [Milestones](#milestones) below.

A module is done when its evidence exists and its knowledge check was answered before you looked at the key.

---

## Stage 1: Beginner (Modules 01-03)

### Module 01 - Introduction to MLOps and the ML lifecycle

- [ ] Read the module brief and lesson
- [ ] Complete the guided lab (incident postmortem)
- [ ] Attempt the independent challenge
- [ ] Answer the knowledge check, then compare with the key (target 7/10)
- [ ] Evidence saved: lifecycle diagram, failure table, one-page postmortem

### Module 02 - Python, Git, CLI, and reproducible environments

- [ ] Read the module brief and lessons
- [ ] Create the `raviride-eta` repository skeleton
- [ ] Rebuild the environment from scratch and run the code
- [ ] Break the lock file two ways and document each error
- [ ] Evidence saved: project file, lock file, environment listing, troubleshooting log

### Module 03 - Organizing an ML project and understanding technical debt

- [ ] Read the module brief and lessons
- [ ] Refactor the supplied notebook into a package, preserving the metric
- [ ] Write two architecture decision records
- [ ] Build a debt register of at least five items
- [ ] Evidence saved: package, ADRs, debt register, before/after metric

---

## Stage 2: Intermediate (Modules 04-11)

### Module 04 - Data quality, validation, and data versioning

- [ ] Write eight validation checks and watch a corrupt batch fail
- [ ] Track the dataset with DVC and retrieve it from a clean clone
- [ ] Add a leakage test that fails on contaminated features
- [ ] Evidence saved: validation code, fail/pass logs, `.dvc` files, data README

### Module 05 - Reproducible model training and pipeline design

- [ ] Build the four-stage pipeline and observe a full cache hit
- [ ] Change one parameter and confirm only affected stages rerun
- [ ] Prove two clean runs produce the same metrics
- [ ] Evidence saved: stage file, DAG image, metrics, two-run comparison

### Module 06 - Experiment tracking and model evaluation using MLflow

- [ ] Track six runs with parameters, metrics, and dataset version
- [ ] Compare runs and identify a slice where the aggregate winner loses
- [ ] Record a baseline
- [ ] Evidence saved: run table, comparison view, evaluation report

### Module 07 - Unit, data, model, integration, and regression testing

- [ ] Write the four test layers
- [ ] Introduce the unit-conversion bug and watch the invariance test catch it
- [ ] Add a regression gate at a stated tolerance
- [ ] Evidence saved: test suite, coverage report, failure logs, strategy note

### Module 08 - Pipeline automation and workflow dependencies

- [ ] Reduce the pipeline to one documented command
- [ ] Kill it mid-run and resume, noting what was reused from cache
- [ ] Add pre-commit hooks and record one rejection
- [ ] Evidence saved: entry script, `dvc.lock`, timing table, recovery log

### Module 09 - Model artifacts, registries, promotion, and lifecycle management

- [ ] Register three versions and promote one to `champion`
- [ ] Block a failing candidate automatically
- [ ] Roll back and time it
- [ ] Trace one alias back to its dataset hash
- [ ] Evidence saved: version table, alias history, rollback log, promotion policy

### Module 10 - Model serving and REST APIs using FastAPI

- [ ] Serve `/health`, `/ready`, `/model-info`, and `/predict`
- [ ] Reject five malformed payloads with specific errors
- [ ] Break the feature assembler and see the contract tests catch it
- [ ] Evidence saved: app code, OpenAPI schema, latency table, skew report

### Module 11 - Docker images, containers, and deployment environments

- [ ] Containerise the API and run it on a published port
- [ ] Prove a source-only change does not reinstall dependencies
- [ ] Show an environment variable and a volume changing behaviour without a rebuild
- [ ] Record the model hash inside the image and compare it with the champion
- [ ] Evidence saved: Dockerfile, ignore file, build logs, size and timing table

---

## Stage 3: Advanced (Modules 12-17)

### Module 12 - CI/CD and ML validation workflows using GitHub Actions

- [ ] Build two workflows: fast checks and model validation with a metric gate
- [ ] Make lint fail, then pass, through a hook that also passes locally
- [ ] Block a deliberately degraded model with a non-zero exit, then restore it
- [ ] Require the check through branch protection
- [ ] Evidence saved: workflow files, red/green run logs, gate message, secrets note

### Module 13 - Workflow orchestration and scheduled pipelines

- [ ] Run the five-task workflow and read its state file
- [ ] Force a transient failure and observe the retry with backoff
- [ ] Exhaust the retries on a permanent failure and resume the run
- [ ] Backfill missed dates without duplicating an output
- [ ] Evidence saved: workflow code, run logs, retry log, decision memo

### Module 14 - Prediction monitoring, data drift, model drift, and retraining

- [ ] Log predictions with a schema and no personal data
- [ ] Compute per-feature drift and performance for four batches
- [ ] Set two-signal thresholds and show a false alarm that should not page
- [ ] Write a decision record: investigate, retrain, or roll back
- [ ] Evidence saved: drift reports, threshold table, decision records, runbook

### Module 15 - Security, privacy, governance, fairness, and responsible deployment

- [ ] Threat-model the API with STRIDE and mitigations
- [ ] Find the committed secret, rotate it, and document the response
- [ ] Measure disparity across the groups in the fairness audit
- [ ] Write a model card that states limitations
- [ ] Evidence saved: threat model, scan reports, fairness table, model card

### Module 16 - Cloud deployment concepts, Kubernetes, scaling, and reliability

- [ ] Repair the manifests until the offline checker passes 35/35
- [ ] Deploy to a local cluster with probes and limits, if Docker and kind are available
- [ ] Perform a rolling update and a rollback, and time the rollback (or write the plan)
- [ ] Estimate monthly cost for realistic traffic
- [ ] Evidence saved: manifests and checker output; cluster output if run; rollout log or plan; cost worksheet

### Module 17 - Capstone

- [ ] Choose Core or Full variant and write the system boundary
- [ ] Assemble all seven required artefacts
- [ ] Pass every measurable acceptance criterion
- [ ] Complete the incident simulation within 30 minutes
- [ ] Have a peer deploy from your runbook in under 30 minutes
- [ ] Write the 400-600 word portfolio narrative
- [ ] Evidence saved: handover package, postmortem, defence document

---

## Milestones

### M0 - Ready to start

- [ ] I can run a Python script, use `cd` and `ls`, and make a Git commit
- [ ] My machine meets the minimum hardware in [Prerequisites](../prerequisites/index.md)
- [ ] I have a free GitHub account
- [ ] I completed the readiness self-check

### M1 - Environment reproducible (after Module 02)

- [ ] A fresh folder installs my project with one documented command
- [ ] I can explain why a global install breaks another project

### M2 - Data trustworthy (after Module 04)

- [ ] A corrupt batch is rejected with a useful message
- [ ] I can name the exact dataset version behind my model

### M3 - Training reproducible (after Module 05)

- [ ] Two clean runs agree within my stated tolerance
- [ ] A colleague could repeat it without asking me anything

### M4 - Model selected and registered (after Module 09)

- [ ] My report names a slice where the aggregate winner loses
- [ ] A failing candidate cannot be promoted by convention alone
- [ ] Rollback is demonstrated and timed

### M5 - Service gated (after Module 12)

- [ ] Malformed input returns specific errors
- [ ] The image builds from scratch and runs as non-root
- [ ] CI fails on data, code, and metric regressions - each for the stated reason

### M6 - Operated (after Module 14)

- [ ] Drift is detected a batch before the error is obvious
- [ ] The alert has a threshold, an owner, and a first action
- [ ] Retraining improves the affected slice without regressing another

### M7 - Handover (after Module 17)

- [ ] A peer deploys from my runbook in under 30 minutes
- [ ] Rollback takes under five minutes
- [ ] The incident is diagnosed within 30 minutes
- [ ] The model card states limitations honestly

---

## My record

| Item | Date |
|---|---|
| Course started | |
| Stage 1 complete | |
| Stage 2 complete | |
| Stage 3 complete | |
| Capstone submitted | |
| Portfolio narrative written | |
