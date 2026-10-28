# Learning Outcomes

This page states what the course as a whole promises, where each promise is taught, and what evidence proves it. Module-level outcomes (the finer-grained statements) live in the [detailed syllabus](detailed-syllabus.md) for each module.

Read this page in two ways:

- **As a student:** it is the contract. If you cannot produce the evidence in the right-hand column, the outcome is not yet yours, regardless of how much you have read.
- **As an instructor adopting the course:** it is the alignment map. Every outcome is taught somewhere, practised somewhere, and assessed somewhere, and you can see where to trim if your semester is shorter.

---

## 1. Course-level outcomes

By the end of the course you will be able to:

| ID | Outcome | Cognitive level | Primary modules |
|---|---|---|---|
| **CO1** | Explain the machine learning lifecycle, name the artefact each stage produces, and locate a failure at the stage and control that should have caught it. | Understand, Analyse | 01, 17 |
| **CO2** | Make a project reproducible: environment, dependencies, data, configuration, seeds, and results, such that another person can rebuild it from a clean copy. | Apply, Analyse | 02, 05, 12 |
| **CO3** | Specify and enforce data quality with executable checks, version datasets, and detect leakage before it reaches a model. | Apply, Analyse | 04, 05 |
| **CO4** | Track experiments, evaluate beyond a single aggregate metric, select a model on evidence, and record a defensible baseline. | Analyse, Evaluate | 06, 09 |
| **CO5** | Verify an ML system with unit, data, model, integration, and regression tests, and explain what each layer cannot catch. | Apply, Evaluate | 07, 12 |
| **CO6** | Deliver a model as a validated service: packaged artefact, documented API contract, container image, and an automated pipeline that gates regressions. | Apply, Create | 09, 10, 11, 12 |
| **CO7** | Operate the service: schedule and retry pipelines, monitor for drift and degradation, retrain on evidence, and roll back safely. | Analyse, Evaluate | 13, 14, 09 |
| **CO8** | Assess and reduce risk: threat-model the service, manage secrets and dependencies, measure disparity, and publish an honest model card. | Evaluate, Create | 15 |
| **CO9** | Reason about deployment at scale: choose between hosting models, write infrastructure as code, define SLOs, plan a rollout, and estimate cost. | Understand, Apply, Evaluate | 16 |
| **CO10** | Hand over and defend a running system: documentation sufficient for a peer, an incident postmortem, and a justified answer to "why not simpler?". | Evaluate, Create | 17 |

Cognitive levels use Bloom's revised taxonomy. They describe the highest level the assessment demands, not the highest level mentioned in the text: a lesson may explain, but if the assessment only asks you to recall, the outcome is not achieved at that level.

---

## 2. What counts as evidence

Every outcome is assessed through an artefact you keep, not through self-report. The evidence column is the answer to "how would anyone know?".

| ID | Evidence that demonstrates the outcome | Assessed in |
|---|---|---|
| CO1 | A lifecycle diagram plus a postmortem that classifies real failure events and names the missing controls | Module 01 postmortem; capstone incident report |
| CO2 | A clean clone installs, trains, and reports the same metric within a stated tolerance, using documented commands only | Module 02 checklist; Module 05 two-run proof; CI run on a fresh runner |
| CO3 | Validation code that rejects a corrupt batch with a specific message, a versioned dataset with checksum, and a leakage test that fails on contaminated features | Module 04 lab and challenge |
| CO4 | A tracked run history, a comparison table, and an evaluation report identifying a slice where the aggregate winner loses | Module 06 report; registry candidate review in 09 |
| CO5 | A test suite in which deliberately breaking behaviour makes a specific test fail, plus a regression gate that blocks a degraded model | Module 07; CI gate evidence in 12 |
| CO6 | A served endpoint with schema validation, a container image with a documented build, and a pipeline that refuses a worse model | Modules 10, 11, 12 artefacts |
| CO7 | Drift reports across successive batches, an alert with a threshold and owner, a retrain decision memo, and a timed rollback log | Modules 14, 09 |
| CO8 | A STRIDE table with mitigations, secret-scan and dependency-scan output, a fairness table, and a model card with limitations | Module 15 |
| CO9 | Kubernetes manifests with probes and limits, a Terraform plan, a rollout plan with abort criteria, and a cost worksheet | Module 16 |
| CO10 | A handover package a peer can operate from, an incident postmortem under time pressure, and a defence document | Capstone |

If an artefact could have been produced without understanding, it is not good evidence. A screenshot of a green CI badge is weak; a log showing the gate failing for the stated reason, and the fix, is strong.

---

## 3. Module alignment matrix

`P` = primary teaching and assessment. `r` = reinforced, practised again. Blank = not addressed.

| Module | CO1 | CO2 | CO3 | CO4 | CO5 | CO6 | CO7 | CO8 | CO9 | CO10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 Introduction to MLOps | P | | | | | | | | | |
| 02 Python, Git, CLI, environments | r | P | | | | | | | | |
| 03 Project organization and debt | r | r | | | | | | | | P |
| 04 Data quality and versioning | | r | P | | | | | | | |
| 05 Reproducible training | | P | r | r | | | | | | |
| 06 Experiment tracking and evaluation | | r | | P | | | | | | |
| 07 Testing ML systems | | | | r | P | | | | | |
| 08 Pipeline automation | | r | | | r | r | | | | P |
| 09 Registry and lifecycle | | | | P | | r | r | | | |
| 10 Serving with FastAPI | | | | | r | P | | | | |
| 11 Docker and containers | | r | | | | P | | | r | |
| 12 CI/CD and validation workflows | | P | r | | P | P | | | | |
| 13 Orchestration and scheduling | | | | | | r | P | | | r |
| 14 Monitoring, drift, retraining | | | r | r | | | P | | | |
| 15 Security, privacy, fairness | | | | | | | | P | | r |
| 16 Cloud, Kubernetes, reliability | | | | | | r | r | r | P | |
| 17 Capstone | P | P | r | r | r | P | P | r | r | P |

How to read it: every outcome has at least one `P`, and every module has at least one `P`. That is the alignment guarantee. If you remove a module, check that no outcome loses its only `P`.

---

## 4. Outcome progression by stage

The same outcome looks different at the beginning and the end of the course. This is the difference between "has heard of it" and "can do it".

| Stage | Modules | What you can do by the end |
|---|---|---|
| Foundations | 01-03 | Explain the lifecycle and its failure modes; set up a reproducible project that a stranger could install; identify debt in a repository and justify a structure. |
| Data and training | 04-06 | Validate and version data; build a cached, deterministic pipeline; evaluate candidates on slices and defend a selection. |
| Engineering | 07-09 | Test at four layers; automate the pipeline; register, promote, and roll back a model with automatic gates. |
| Delivery | 10-12 | Serve the model with a validated contract; containerise it; gate every change in CI with tests and a metric threshold. |
| Operations | 13-14 | Schedule and retry pipelines; detect drift before users report it; retrain on evidence and prove no regression. |
| Governance and scale | 15-16 | Threat-model and scan the system; measure disparity; write a model card; deploy with IaC, probes, SLOs, and a cost estimate. |
| Integration | 17 | Operate and hand over the whole system, diagnose an injected incident, and defend the design. |

---

## 5. Self-audit

Use this before starting (to see the gap) and after the capstone (to see the distance). Mark each statement **can do**, **can do with reference**, or **cannot do yet**.

### Foundations
- [ ] I can draw the ML lifecycle and say what artefact each stage produces.
- [ ] I can rebuild a project environment from its repository alone.
- [ ] I can explain why a notebook that works locally may fail elsewhere.

### Data and training
- [ ] I can write validation that fails on a corrupt batch, with a message a colleague can act on.
- [ ] I can prove a dataset version is the one that trained a model.
- [ ] I can show that my pipeline produces identical metrics twice.
- [ ] I can find the slice where a "better" model is actually worse.

### Engineering
- [ ] I can name which test layer would have caught a given bug, and which would not.
- [ ] I can run the entire pipeline with one command, and resume it after a failure.
- [ ] I can block a failing model from promotion without relying on human discipline.

### Delivery
- [ ] I can serve a model with input validation and a documented contract.
- [ ] I can rebuild the runtime from a Dockerfile and explain what the container guarantees.
- [ ] I can make CI fail for the right reason on a data, code, and metric regression.

### Operations
- [ ] I can distinguish data drift, prediction drift, and concept drift in a real batch.
- [ ] I can set a threshold I can justify, not one that merely looks strict.
- [ ] I can retrain on evidence and show it did not regress elsewhere.
- [ ] I can roll back and state how long it took.

### Governance and scale
- [ ] I can threat-model a service and rank findings by impact.
- [ ] I can detect a committed secret and state what to do next.
- [ ] I can measure disparity and explain what the number does not prove.
- [ ] I can write a model card a non-specialist could use to decide whether to trust the system.

### Integration
- [ ] Someone else can operate my system from my documentation.
- [ ] I can diagnose an incident using evidence, not guesswork.
- [ ] I can defend my design against "why not simpler?" and "what breaks at ten times the load?".
- [ ] I can state what my system does not protect against.

---

## 6. Outcomes and employability

The outcomes map onto the work that junior MLOps, ML platform, and production data science roles actually assign in the first year: making training reproducible, getting a model behind an API, adding tests and CI, and answering "is the model still good?" with evidence.

| Typical early-career task | Outcomes exercised |
|---|---|
| "Our retrain gives different numbers each week. Fix it." | CO2, CO3 |
| "Put this model behind an endpoint by Friday." | CO6 |
| "Why did accuracy drop?" | CO1, CO7 |
| "We need to prove which model is live." | CO4, CO6 |
| "Can we ship this automatically?" | CO5, CO6 |
| "Security review flagged our repo." | CO8 |
| "We are moving to Kubernetes. What changes?" | CO9 |
| "Write the handover doc before you leave." | CO10 |

The course does not claim these outcomes make anyone job-ready on their own. They make a graduate able to do the first six months of such work with supervision, which is a different and more honest claim.

---

## 7. For instructors adapting this course

- **Shorter semester:** keep every `P` for CO1-CO6 and CO7, and use the Core capstone. Modules 13 and 16 can be reduced to guided reading without losing an outcome's only `P`.
- **Longer semester or a second course:** add the Full capstone and the Module 16 local cluster path; these extend CO9 and CO10 without adding new tools.
- **Assessment-only adoption:** the rubrics in the [assessment framework](assessment-framework.md) can be used with your own teaching material; the outcome statements remain valid because they are stated as capabilities, not as content coverage.
- **Do not** assess an outcome only by recall. If a quiz is the sole evidence for CO5, the outcome is not met at the stated cognitive level.
