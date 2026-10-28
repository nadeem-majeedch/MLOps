# Tool Selection Guide

Every tool in this course is a decision. This page records those decisions, the alternatives that were rejected, and the conditions under which a student should choose differently.

Two rules govern everything here:

1. **A tool is introduced only when a problem has already been felt.** No module begins with installation.
2. **Free, local, and maintainable beats impressive.** If a tool cannot run on a student laptop without an account, it is optional by definition.

---

## 1. Selection principles

| Principle | What it means in practice |
|---|---|
| Boring and widely used | Prefer tools a student will meet again in a job over tools that are merely modern |
| One new tool per module | You should be able to name what you learned this week and the problem it solved |
| Local-first | Works offline after setup, without a cloud account, credit card, or institutional licence |
| Windows-first | Tested on Windows 11 with PowerShell 7; POSIX-only tooling is rejected or given a documented bridge |
| Observable behaviour | The tool produces output you can inspect, compare, and put in a portfolio |
| Reversible | Removing the tool does not invalidate earlier learning; concepts survive the product |
| Honest licensing | Where a licence is not open source, or a paid tier exists, the guide says so plainly |

---

## 2. The two tool stacks

**Minimum viable stack** (essential path, roughly 200 hours): Python and `venv`, Git, DVC, MLflow, pytest, pandera, FastAPI, Docker, GitHub Actions.

**Advanced stack** (full path, roughly 285 hours): the above plus Prefect, Evidently, Prometheus and Grafana (optional), `kind` and `kubectl`, Terraform, `gitleaks`, `pip-audit`, `fairlearn`.

A student who completes only the minimum stack has still met every essential outcome; the advanced stack adds operational realism, not new fundamentals.

---

## 3. Tools by job

### 3.1 Language and environment

| Job | Chosen | Why | Alternatives and when to choose them | Cost |
|---|---|---|---|---|
| Language | Python 3.11 or 3.12 | Dominant in ML; every tool in the course supports it; students already know it | R 4.x if your ML background is statistical; the operational concepts transfer, the tooling does not | Free |
| Environment isolation | `venv` + `pip` | Ships with Python; teaches what a lock file and a dependency graph actually are | `uv` for speed once the concept is understood; conda only if a dependency needs non-Python binaries | Free |
| Dependency declaration | `pyproject.toml` | The current standard, understood by every modern tool | `requirements.txt` only for legacy projects; the course explains both | Free |
| Editor | VS Code | Free, cross-platform, good Python and Docker support, not required by any lab | Any editor; labs only assume a terminal | Free |

### 3.2 Version control and collaboration

| Job | Chosen | Why | Alternatives | Cost |
|---|---|---|---|---|
| Version control | Git | Universal; branching and review are the actual skill | None worth naming | Free |
| Hosting and CI | GitHub | Free for public repositories; Actions included; students likely to meet it | GitLab CI is mapped as an equivalent; the workflow concepts transfer | Free (public); 2,000 minutes/month on private free tier |
| Local hooks | `pre-commit` | Runs checks before a bad commit exists, which is the cheapest possible gate | Manual checks, logged; weaker but workable | Free |
| Linting | `ruff` | Fast, single tool for lint and format, minimal configuration | `flake8` + `black`; equivalent outcomes, more configuration | Free |

### 3.3 Data

| Job | Chosen | Why | Alternatives | Cost |
|---|---|---|---|---|
| Dataframes | pandas | Ubiquitous; students already know it | Polars for large data; not needed at course scale | Free |
| Data validation | pandera | Schemas declared as data, so checks are readable and extensible; small footprint | Great Expectations (more capable, much heavier); plain assertions (what most teams start with) | Free |
| Data and pipeline versioning | DVC | Content-addressed data versioning plus stage graphs; works with a local remote, so no cloud needed | Git LFS (no lineage or pipelines); lakeFS (server); cloud storage versions (paid, account) | Free |
| Experiment tracking | MLflow | Runs locally with a file store; industry-recognised; registry included | Weights & Biases (free tier, account, hosted); Neptune (paid); spreadsheets (fails at scale, and the course shows why) | Free |
| Model registry | MLflow Model Registry | Same install as tracking; versions and aliases without a cloud account | Cloud registries (paid); file-based manifest (reduced lab path) | Free |

### 3.4 Testing and quality

| Job | Chosen | Why | Alternatives | Cost |
|---|---|---|---|---|
| Test runner | pytest | One runner for unit, data, model, and integration tests | `unittest` (stdlib, more verbose) | Free |
| Coverage | pytest-cov | Shows which branches are never executed, including the ones that matter | None needed | Free |
| Model behaviour testing | Hand-written pytest | Most useful ML tests are small invariants and directional checks; a heavy suite hides that | `deepchecks`, `checklist`; introduced only as optional reading | Free |
| Secret scanning | gitleaks | Fast, local, produces a concrete finding you can act on | GitHub secret scanning (repository setting, may require enabling) | Free |

### 3.5 Serving and packaging

| Job | Chosen | Why | Alternatives | Cost |
|---|---|---|---|---|
| API framework | FastAPI | Schema validation and OpenAPI docs are built in, so the contract is executable | Flask (simpler, hand-written validation); Django (too much for one endpoint) | Free |
| ASGI server | Uvicorn | The standard companion to FastAPI; one command to run | Gunicorn with workers (POSIX-oriented; mentioned, not required) | Free |
| Serialisation | joblib / MLflow model format | Preserves the preprocessing pipeline, not just weights | Pickle alone (fragile; the course explains why) | Free |
| Containers | Docker Desktop (WSL 2) | Industry standard; one runtime for local labs and Compose | Podman (free, daemonless); no-container path with reduced outcomes | Free for personal/education; paid subscription required in large organisations |

### 3.6 Automation, orchestration, and operations

| Job | Chosen | Why | Alternatives | Cost |
|---|---|---|---|---|
| CI/CD | GitHub Actions | No infrastructure; free for public repos; YAML that students can read | GitLab CI, Jenkins (self-hosted, heavy) | Free tier |
| Orchestration | Prefect 3 | Python-native, no cluster, retries and schedules visible in a UI | Airflow (industry standard, heavy: scheduler, metadata DB, webserver); Dagster (asset-oriented, steeper); Windows Task Scheduler (minimal, no retry UI) | Free |
| Drift detection | Evidently | One call produces a report and metrics; runs offline | WhyLabs, Arize (paid platforms); hand-written PSI/KS (good exercise, more code) | Free |
| Metrics and dashboards | Prometheus + Grafana (optional) | The standard open-source pairing; taught only as an optional heavy path | Log-based reports (default path); cloud monitoring (paid) | Free; heavy |
| Infrastructure as code | Terraform with a local provider | Teaches plan/apply/state without provisioning anything billable | OpenTofu (open-source fork, drop-in for this lab); Pulumi; cloud console clicking (not reproducible) | Free for individual use; Terraform is source-available, not OSI open source |
| Local Kubernetes | `kind` | A real cluster inside Docker; no cloud account | minikube, k3d; managed clusters (paid) | Free; heavy |
| Fairness measurement | fairlearn | Standard disparity metrics with clear documentation | Hand-written group metrics; commercial fairness tools | Free |
| Dependency scanning | pip-audit | Reports known vulnerabilities from the Python packaging database | `safety` (free tier); Dependabot (GitHub setting) | Free |

---

## 4. Tools deliberately excluded, and why

These appear in lessons as named concepts, never as required labs. Each exclusion is a scope decision, not a judgement that the tool is bad.

| Excluded | Why not in the core path | Where it is mentioned |
|---|---|---|
| Apache Airflow (as a required lab) | Scheduler, metadata database, and webserver teach infrastructure before orchestration concepts; too heavy for an 8 GB laptop | Module 13 comparison; optional extension |
| Kubeflow | A platform, not a lesson; requires a cluster to be useful, and hides the pipeline concepts students need first | Module 16 reading |
| Managed cloud ML platforms (SageMaker, Vertex AI, Azure ML) | Account, billing, and IAM complexity dominate the learning; vendor-specific interfaces do not transfer | Modules 09, 16 as `Paid - optional` |
| Feature store products (Feast and commercial equivalents) | Solve a multi-team problem; at course scale they add a service without adding understanding | Module 09 concept, Module 16 optional |
| Service mesh, multi-cluster orchestration | Operate problems a single-service system does not have | Module 16 reading only |
| Commercial observability platforms | Paid, account-bound; the signals matter more than the vendor | Module 14 |
| Deep learning frameworks at scale | The course's subject is operations, not architecture; GPU provisioning would dominate | Module 01 scope note |
| Jenkins | Heavy to host, and the concepts are already covered by Actions | Module 12 comparison |
| Notebook-only workflows (Jupyter as the primary artefact) | Notebooks are useful for exploration and poor as the unit of production; the course teaches the transition | Module 03 |

---

## 5. Version policy

- **Pin in one place.** The setup guide owns versions; lessons reference it rather than repeating numbers that will drift apart.
- **Bracket in prose.** "Python 3.11 or 3.12" is acceptable; "the latest Python" is not.
- **Record what was tested.** Every lab carries `Last verified` with a date, OS, and shell. A lab whose tools have had a major release is re-verified, not assumed.
- **Upgrade deliberately.** When a tool's interface changes, the lesson and its lab change in the same commit, and the change is noted for returning students.
- **Do not chase releases mid-course.** A student who started on a pinned set should finish on it.

---

## 6. Resource profile

So you can plan before you install:

| Component | Disk | RAM when running | Notes |
|---|---|---|---|
| Python environment per project | 0.3-1.5 GB | 200-500 MB | Depends on whether scientific wheels are included |
| MLflow local tracking store | Under 100 MB | 200 MB | File-based; grows with artefacts |
| DVC cache | Roughly dataset size | Negligible | A local remote doubles it |
| Docker Desktop + WSL 2 | 5-10 GB | 1-2 GB idle | Images add several GB |
| Local Kubernetes (`kind`) cluster | 3-6 GB | 2-4 GB | Optional module only |
| Prometheus + Grafana stack | 1-2 GB | 500 MB-1 GB | Optional; the default monitoring path needs neither |
| Full stack running together | 15-20 GB | 6-8 GB | This is why 16 GB RAM is recommended |

If you have 8 GB of RAM, run one heavy component at a time. Every heavy lab names a lighter path that reaches the same assessed outcome.

---

## 7. If you cannot install a tool

No module is blocked by one unavailable product. Each lab specifies a reduced path:

| Unavailable | Reduced path | What is lost |
|---|---|---|
| Docker | Pinned environment plus a documented parity checklist; Compose replaced by two local processes | Image reproducibility, isolation, the container mental model |
| GitHub Actions | Workflow authored and validated with `act` where possible, or reviewed against a checklist | Real runner evidence, caching behaviour |
| Prefect | Windows Task Scheduler plus a Python entry point | Retry UI, run history visualisation |
| DVC | Python driver script plus recorded file hashes | Caching, stage-graph invalidation |
| `kind` | Compose-based deployment plus a manifest mapping exercise | Real cluster behaviour, probes, rolling updates |
| Terraform | A written plan/apply exercise against the local Docker provider's documentation | State handling, plan review |

The lab must state which outcome is reduced. A reduced path is honest; a simulated success is not.

---

## 8. Choosing a tool not in this guide

You will meet new tools after the course. Use the same criteria the course used:

1. **What problem does it solve, and do I have that problem now?**
2. **Can I run it locally and free, and does it work on my platform?**
3. **What does it replace, and what would I have to give up?**
4. **Is it maintained, documented, and used by more than its vendor?**
5. **If it disappears, what of my work survives?** Prefer tools where the answer is "the data and the process".
6. **Can I explain it to a colleague in two sentences?** If not, you probably do not need it yet.

A tool that fails question 1 or 5 is a tool you are learning for its own sake.
