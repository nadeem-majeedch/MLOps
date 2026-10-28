# Glossary

MLOps reuses words from software engineering, data engineering, and machine learning, and often means three different things by the same word. This glossary gives one definition per term, written for someone meeting it for the first time.

**How to use it:**

- Terms are grouped alphabetically. Use your browser's find function (++ctrl+f++) or the site search for a specific word.
- The *modules* column in each definition tells you where the term is taught properly, so you can go from a definition to the reasoning.
- If two terms are commonly confused, the entry says what the term is *not*.

Definitions here are deliberately short. A definition is not an explanation; the lessons do the explaining.

---

## A-C

**Alias (model alias)** - A movable label in a model registry, such as `champion`, that points at exactly one model version. Promotion means repointing the alias, not renaming a file. This replaces the older idea of fixed "stages". *Module 09.*

**API contract** - The agreed shape of a request and response: which fields exist, their types, which are required, and what happens when they are wrong. In this course the contract is executable, not a document that drifts. *Module 10.*

**Artefact (also spelled artifact)** - Any file a process produces that must be kept: trained model weights, metrics, plots, reports, a container image. An artefact is evidence; a log line is not. *Modules 01, 05.*

**Attestation (build provenance)** - A signed statement describing how an artefact was built: which source revision, which builder, which inputs. It lets a consumer verify origin instead of trusting a filename. *Module 15.*

**Audit trail** - The append-only record of who did what and when: an approval, a promotion, a rollback, a data export. Reconstructing a decision months later is the test of whether one exists. *Module 15.*

**Baseline** - The reference result a new candidate must beat. It is usually the current production model or a trivial heuristic, and it is recorded before candidates are compared, not chosen afterwards. *Module 06.*

**Batch inference** - Predictions computed for many records at once, on a schedule, and written to storage for later use. Contrast with *online inference*. *Modules 01, 14.*

**Blast radius** - How much breaks when a change fails: one request, one zone, one region, or everything. Reducing blast radius is why rollout strategies exist. *Module 16.*

**Blue-green deployment** - Running two complete environments, one live and one idle, and switching traffic between them. Rollback is a switch back, which is fast but doubles the infrastructure. *Module 16.*

**Canary deployment** - Releasing to a small fraction of traffic first, watching for harm, then widening. Named after the bird in the coal mine. *Module 16.*

**Champion / challenger** - A pattern where the live model (champion) is compared against a candidate (challenger) on real or replayed traffic before promotion. *Module 09.*

**CI/CD** - Continuous integration automatically tests every change; continuous delivery keeps the system always releasable; continuous deployment releases automatically. They are three different levels of automation, often conflated. *Module 12.*

**Cold start** - The first request after a service starts, which is slower because the model and libraries must load. Reported separately from steady-state latency, never averaged into it. *Module 10.*

**Concept drift** - The relationship between inputs and the target changes, so the same inputs should now produce a different answer. The world moved, not the data schema. *Module 14.*

**ConfigMap** - Non-secret configuration held as key-value data and mounted into containers or exposed as environment variables. Keeping it outside the image lets one image run in two environments. *Module 16.*

**Configuration drift** - The running system gradually stops matching the files that describe it, because someone changed something by hand. The reason infrastructure as code exists. *Module 16.*

## D-F

**Data contract** - Testable expectations about data: schema, types, allowed ranges, uniqueness, and semantics. A contract that is not executable is a wish. *Module 04.*

**Data drift (covariate shift)** - The distribution of inputs changes while the input-to-output relationship may not. Detectable without labels, which is why it is the earliest warning signal. *Module 14.*

**Data leakage** - Information that would not be available at prediction time sneaks into training, usually through the target or the future. It produces excellent offline metrics and useless production models. *Module 04.*

**Data minimisation** - Collecting and retaining only the fields the stated purpose needs. It reduces breach impact and is a legal expectation in many jurisdictions, not merely good manners. *Module 15.*

**Demographic parity** - A fairness criterion requiring equal positive-prediction rates across groups. It can conflict with equal error rates, so choosing one is a policy decision that must be stated, not a technical default. *Module 15.*

**Dependency lock file** - A record of the exact versions actually installed, including transitive dependencies. It is what makes "works on my machine" reproducible elsewhere. *Module 02.*

**Deployment versus release** - Deployment is putting code or a model into an environment; release is exposing it to users. A model can be deployed for a week before it is released to anyone. *Module 01.*

**Determinism** - Same inputs, same outputs, every time. In ML this usually means fixed seeds, fixed splits, and fixed library versions; without it, comparisons between runs are noise. *Module 05.*

**Drift threshold** - The value at which a drift measure triggers an alert or a retrain. It must be justified by consequence, not chosen because it looks strict. *Module 14.*

**DVC (Data Version Control)** - A tool that versions datasets by content hash and defines pipeline stages with declared inputs and outputs. It keeps large files out of Git while recording lineage. *Modules 04, 05.*

**Error budget** - The amount of unreliability an SLO allows. If the objective is 99.5% availability, the budget is 0.5%; spending it on risk becomes a decision rather than an accident. *Module 16.*

**Evaluation slice** - A subgroup of the evaluation data - a zone, an hour, a customer type - scored separately. Aggregate metrics hide slices where a model is worse. *Module 06.*

**Explainability** - Producing a reason a human can inspect for an individual prediction, such as the features that moved the score. An explanation is evidence about the model, not proof that the decision was right. *Module 15.*

**Experiment tracking** - Recording the parameters, metrics, artefacts, and data version of every training run so that a result can be explained and repeated. *Module 06.*

**Feature store** - A service that computes features once and serves them consistently to training and to online prediction. It solves a multi-team problem; a single project usually does not have it yet. *Module 09, concepts only.*

**Feedback loop** - When a model's predictions influence the data used to retrain it. It can quietly poison training data, for example if predicted demand changes where drivers go. *Modules 01, 14.*

## G-L

**Ground truth** - The true outcome used to measure error. In production it often arrives late, or never, which is why *label delay* matters. *Module 14.*

**Health check** - An endpoint that reports whether a service is alive; a *readiness* check reports whether it can serve traffic. They fail differently and should not be the same endpoint. *Module 10.*

**Horizontal Pod Autoscaler (HPA)** - A controller that adds or removes replicas based on a measured signal such as CPU or a custom metric. It scales capacity, not correctness: a broken model stays broken at ten replicas. *Module 16.*

**Idempotency** - Repeating an operation has the same effect as doing it once. Essential for retries: without it, a retried pipeline registers the same model twice. *Modules 08, 13.*

**Incident** - An unplanned event that degrades a service for users. Incidents are handled with a runbook and reviewed with a blameless postmortem. *Module 17.*

**Inference** - Using a trained model to produce predictions. *Batch* and *online* are the two common modes. *Module 10.*

**Infrastructure as code (IaC)** - Describing servers, clusters, and networks in versioned files that a tool applies, so the environment is reviewable and repeatable. Terraform is the example used here. *Module 16.*

**Label delay** - The gap between a prediction and the true outcome that proves it right or wrong. Models predicting next month's churn cannot be evaluated on accuracy today. *Module 14.*

**Latency percentile** - The value below which a given share of requests fall: p95 means 95% were faster. Averages hide the slow tail users actually notice. *Module 10.*

**Least privilege** - Granting each identity only the permissions its task needs, for only as long as it needs them. A service that can read every table because it once needed one is a finding. *Module 15.*

**Lineage** - The traceable chain from dataset version to code commit to model version to deployment. If you cannot answer "what trained this?", you do not have lineage. *Modules 04, 09.*

## M-O

**MLOps** - The set of practices that keep machine learning systems working: versioning, testing, automation, deployment, monitoring, and governance. Not a tool, and not a synonym for "putting a model in Docker". *Module 01.*

**MLOps maturity** - How much of the lifecycle is automated and observable, commonly described in levels from manual and script-driven to fully automated retraining. Useful for describing a team, dangerous as a scoreboard. *Module 01.*

**Model card** - A short document describing a model's intended use, training data, measured performance, limitations, and risks, written so a non-specialist can judge whether to trust it. *Module 15.*

**Model registry** - A versioned store of models with their metadata, lineage, and lifecycle labels, so "which model is live?" has one answer. *Module 09.*

**Model signature** - The declared input and output schema of a model, including types and column order. Mismatches between signature and serving code are a common silent failure. *Modules 09, 10.*

**Monitoring** - Watching known signals - error rate, latency, drift - against thresholds you defined in advance. Contrast with *observability*. *Module 14.*

**Observability** - Being able to answer new questions about a running system from its telemetry, not just the questions you anticipated. Logs, metrics, and traces are its raw material. *Module 14.*

**Online inference** - Producing a prediction per request, within a latency budget, usually behind an API. Contrast with *batch inference*. *Module 10.*

**Orchestrator** - A system that runs tasks on a schedule or trigger, respecting dependencies, retries, and concurrency limits. Prefect is the example used here; Airflow is the industry standard. *Module 13.*

## P-R

**Point-in-time correctness** - Computing features using only information available at the moment of prediction. Violating it is the most common form of leakage. *Module 04.*

**Population stability index (PSI)** - A numeric measure of how much a distribution has shifted between a reference batch and a current one. Convenient, widely used, and only as meaningful as the reference you chose. *Module 14.*

**Promotion** - Moving a model version into service after it passes defined gates. Promotion should be a decision with evidence, not a rename. *Module 09.*

**Promotion gate** - An automated, measurable condition a candidate must satisfy, such as "no slice regresses by more than 2%". Gates that require a human to remember them are not gates. *Modules 09, 12.*

**Provenance** - The origin and history of a dataset or artefact: where it came from, who changed it, and under what licence. *Module 04.*

**Readiness probe** - A check that tells an orchestrator whether an instance can serve traffic yet. It fails while the model is still loading, which is why it is separate from a liveness check. *Module 16.*

**Regression gate** - A check that fails when a measured behaviour gets worse than a stated tolerance. It is the difference between testing and hoping. *Module 07.*

**Replicability** - A different team, with a different setup, reaches the same conclusion. Stronger and rarer than reproducibility. *Module 05.*

**Reproducibility** - The same team, with the same artefacts and environment, gets the same result again. The minimum professional standard, and the one most projects fail. *Modules 02, 05.*

**Resource requests and limits** - A request is what the scheduler reserves for a container; a limit is what it may not exceed. Without a memory limit one leaking pod can take down its node. *Module 16.*

**Retraining** - Fitting a model again on newer data. The interesting questions are what triggers it, what guards it, and how you know it helped. *Module 14.*

**Rollback** - Restoring the previous working version. A rollback you have never rehearsed is a plan, not a capability. *Modules 09, 16.*

**Rolling update** - Replacing instances of a deployment a few at a time, waiting for each new one to become ready before removing an old one. It keeps capacity available, provided the probes are honest. *Module 16.*

## S-U

**Secrets management** - Storing and rotating credentials outside code and history, and limiting who can read them. A secret in Git is compromised even after deletion. *Module 15.*

**Serving skew (train/serve skew)** - Differences between how features are computed in training and at prediction time, such as a different order, unit, or aggregation. Produces plausible but wrong predictions. *Module 10.*

**Shadow deployment** - Running a new model alongside the live one on mirrored traffic, without letting it affect users, to compare behaviour. *Module 16.*

**SLI, SLO, SLA** - An indicator is what you measure (p95 latency); an objective is the target over a window (under 250 ms, 99% of the time); an agreement is the contractual consequence of missing it. *Module 16.*

**Smoke test** - A minimal end-to-end run that proves the pipeline works at all, before slower and deeper tests. *Module 12.*

**Supply chain (software)** - Everything that goes into a built artefact: base images, packages, build tools, and the accounts that can publish them. Most of it is code you did not write and cannot see. *Module 15.*

**Technical debt (in ML)** - The accumulated cost of shortcuts that make a system hard to change: glue code, pipeline jungles, undeclared consumers, and configuration spread across notebooks. It compounds silently. *Module 03.*

**Temporal split** - Training on earlier data and evaluating on later data, mirroring how the model will actually be used. A random split on time-ordered data leaks the future. *Module 04.*

**Threat model** - A structured list of what you are protecting, who might attack it, how, and what you would notice. It is a design document, not a scanner report. *Module 15.*

**Threshold** - The value at which a system raises an alert or takes an action. Thresholds are decisions about consequences, not statistical facts. *Module 14.*

**Trace** - The recorded path of one request through multiple services, used to find where latency or failure originates. *Module 14.*

## V-Z

**Version (data, model, code)** - An identifiable, immutable state of an artefact. "Latest" is not a version, because it changes. *Modules 02, 04, 09.*

**Warm start** - A service that has already loaded its model and can answer at steady-state speed. The opposite of *cold start*. *Module 10.*

---

## Commonly confused pairs

| Pair | The difference in one line |
|---|---|
| Data drift vs concept drift | Inputs changed vs the input-output relationship changed. |
| Reproducibility vs replicability | Same setup repeats vs a different setup agrees. |
| Monitoring vs observability | Checking known signals vs answering new questions. |
| Deployment vs release | Made available vs made visible to users. |
| Artefact vs model | Any produced file vs the specific file that predicts. |
| Alias vs version | A movable pointer vs the immutable thing it points at. |
| Exception vs error rate | One failure vs the proportion of failures over a window. |

---

*This glossary grows with the course. If a term is missing or a definition is wrong, report it through the repository's issue tracker.*
