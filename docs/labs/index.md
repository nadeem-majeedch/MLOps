# Lab catalogue

Two kinds of lab material live on this site, and they are numbered differently on
purpose:

- **Module labs (G01–G17)** are the guided lab and independent challenge attached
  to each module. They are written from that module's material and are the
  exercises referred to by "the lab" on a module page.
- **The lab collection (Lab 01–Lab 20)** is a standalone sequence of realistic
  scenarios. Each one has a starter kit, synthetic data, an objective acceptance
  checker, and a reference solution kept separate from the instructions.

A module lab assumes you have just read its module. A lab from the collection
assumes only the stated prerequisites, so you can use the collection for revision,
for a course unit with its own schedule, or to rebuild a skill you learned months
ago.

---

## Command conventions

Commands are given for a shell on Linux or macOS, in blocks marked `bash`. Where
the PowerShell form differs, the page gives it directly under the block, or as a
`powershell` block. The same interpreter and the same files are used on every
platform; only these forms change:

| Task | bash | PowerShell 7 |
|---|---|---|
| Activate the environment | `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` |
| Set a variable for one command | `VAR=1 python run.py` | `$env:VAR="1"; python run.py` |
| Read a file | `cat file.json` | `Get-Content file.json` |
| Read the first lines | `head -20 file.log` | `Get-Content file.log -TotalCount 20` |
| Compare two outputs | `diff a.txt b.txt` | `Compare-Object (Get-Content a.txt) (Get-Content b.txt)` |
| Delete generated files | `rm -rf data artifacts` | `Remove-Item data, artifacts -Recurse -Force -ErrorAction SilentlyContinue` |
| Stop a server | ++ctrl+c++ | ++ctrl+c++ |

Paths are written with `/` throughout; PowerShell accepts them. A single `cd`
into the lab directory is assumed in every Steps section, and every command is
run from there unless the page says otherwise.

---

## The lab collection

Every lab runs locally, offline, with synthetic data. Each page states a time
estimate that includes reading, not only typing.

### Foundation

| Lab | Title | Topic | Time | Prerequisite module |
|---|---|---|---|---|
| [01](lab-01-nondeterministic-analysis.md) | Diagnose a notebook that will not reproduce | Reproducibility | 2 h | [02](../modules/02-python-git-cli-environments/index.md), [05](../modules/05-reproducible-training/index.md) |
| [02](lab-02-refactor-notebook.md) | Turn a working script into a project | Structure | 3 h | [03](../modules/03-project-organization/index.md) |

### Intermediate

| Lab | Title | Topic | Time | Prerequisite module |
|---|---|---|---|---|
| [03](lab-03-data-defects.md) | Find every defect in a supplier drop | Data quality | 3 h | [04](../modules/04-data-quality-versioning/index.md) |
| [04](lab-04-version-and-reproduce.md) | Version a dataset and reproduce last month's run | Data versioning | 3 h | [04](../modules/04-data-quality-versioning/index.md), [05](../modules/05-reproducible-training/index.md) |
| [05](lab-05-deterministic-pipeline.md) | Make a pipeline deterministic, then lazy | Pipelines | 4 h | [05](../modules/05-reproducible-training/index.md), [08](../modules/08-pipeline-automation/index.md) |
| [06](lab-06-experiment-comparison.md) | Compare four experiments without trusting memory | Tracking | 3 h | [06](../modules/06-experiment-tracking/index.md) |
| [07](lab-07-leakage-tests.md) | Write the tests that catch leakage | Testing | 4 h | [07](../modules/07-testing-ml-systems/index.md) |
| [08](lab-08-quality-gate.md) | Reject a model that fails the quality policy | Release gates | 3 h | [07](../modules/07-testing-ml-systems/index.md), [09](../modules/09-model-registry/index.md) |
| [09](lab-09-release-candidates.md) | Track artefacts, promote, roll back | Registry | 3 h | [09](../modules/09-model-registry/index.md) |
| [10](lab-10-serving-contract.md) | Build and test a prediction service | Serving | 4 h | [10](../modules/10-model-serving/index.md) |
| [11](lab-11-request-triage.md) | Triage ten requests and five tickets | API diagnosis | 2 h | [10](../modules/10-model-serving/index.md) |
| [12](lab-12-docker-image.md) | Package the service into an image | Containers | 3 h | [11](../modules/11-docker-containers/index.md) |
| [13](lab-13-dependency-conflict.md) | Diagnose a dependency incompatibility | Environments | 2 h | [02](../modules/02-python-git-cli-environments/index.md), [11](../modules/11-docker-containers/index.md) |

### Advanced

| Lab | Title | Topic | Time | Prerequisite module |
|---|---|---|---|---|
| [14](lab-14-actions-workflow.md) | Build a CI workflow that can fail | CI/CD | 3 h | [12](../modules/12-ci-cd/index.md) |
| [15](lab-15-release-gate.md) | Stop a defective model from passing release validation | Release integrity | 3 h | [09](../modules/09-model-registry/index.md), [12](../modules/12-ci-cd/index.md) |
| [16](lab-16-scheduled-training.md) | Schedule, retry, and backfill a workflow | Orchestration | 4 h | [13](../modules/13-orchestration/index.md) |
| [17](lab-17-drift-analysis.md) | Detect a shift and decide whether to retrain | Monitoring | 4 h | [14](../modules/14-monitoring-drift/index.md) |
| [18](lab-18-regression-rollback.md) | Investigate a regression and decide to roll back | Incident response | 3 h | [14](../modules/14-monitoring-drift/index.md), [09](../modules/09-model-registry/index.md) |
| [19](lab-19-security-review.md) | Review a deployment for security and privacy risk | Governance | 4 h | [15](../modules/15-security-governance/index.md) |

### Integration

| Lab | Title | Topic | Time | Prerequisite module |
|---|---|---|---|---|
| [20](lab-20-incident-review.md) | Run the operational incident review | Whole lifecycle | 4 h | [17](../modules/17-capstone/index.md), Labs 08–19 |

---

## By topic

| Topic | Labs | What you practise |
|---|---|---|
| Reproducibility | 01, 04, 05, 13 | Seeding, content hashing, cache keys, version boundaries |
| Data | 03, 04, 17 | Validation, versioning, drift measurement |
| Code and tests | 02, 07, 13 | Structure, leakage tests, API contracts |
| Experimentation | 06 | Parameters, slices, comparison from a store |
| Release engineering | 08, 09, 14, 15 | Gates, aliases, CI, bundle integrity |
| Serving | 10, 11, 12 | HTTP contracts, triage, containers |
| Operations | 16, 17, 18 | Scheduling, monitoring, rollback |
| Governance | 19, 20 | Security, privacy, model cards, incident review |

## What each lab gives you

| Element | Where it is |
|---|---|
| Scenario and task | The lab page, first two sections |
| Starter files and data generator | `examples/labs/lab-NN-.../` in the repository |
| Commands with expected results | The lab page, Steps and Expected output |
| Acceptance criteria | A table on the page, enforced by `check_labNN.py` |
| Reference solution | `examples/solutions/lab-NN/` — separate from the instructions |

The acceptance checkers are the same standard the page describes. They print a
table and exit `0` only when every check passes. Run one before you start to see
what "not yet" looks like.

To check the whole collection at once — for example after editing a kit — run the
runner from the repository root:

```bash
python examples/labs/verify_all.py              # all 20
python examples/labs/verify_all.py --only 09 15 # two of them
```

It copies each kit to a scratch directory, overlays the reference solution,
generates the data, and runs the checker, so the lab directories are untouched.

---

## Module labs

Each module has one guided lab and one independent challenge. These are the
exercises that build directly on that module's reading.

| # | Module lab | Module | Level | Time | You produce |
|---|---|---|---|---|---|
| G01 | Incident postmortem for a degraded model | [01](../modules/01-introduction-to-mlops/lab.md) | Foundation | 3 h | Lifecycle diagram, failure table, postmortem |
| G02 | Build and rebuild a reproducible environment | [02](../modules/02-python-git-cli-environments/lab.md) | Foundation | 4 h | Skeleton, pinned environment, troubleshooting log |
| G03 | Refactor a notebook into a project | [03](../modules/03-project-organization/lab.md) | Foundation | 4 h | Package, two ADRs, debt register |
| G04 | Validate a corrupt batch and version the dataset | [04](../modules/04-data-quality-versioning/lab.md) | Intermediate | 5 h | Eight checks, fail/pass logs, `.dvc` files |
| G05 | Build a four-stage training pipeline | [05](../modules/05-reproducible-training/lab.md) | Intermediate | 5 h | Stage graph, DAG image, two-run comparison |
| G06 | Track six experiments and find the weak slice | [06](../modules/06-experiment-tracking/lab.md) | Intermediate | 5 h | Run history, comparison, evaluation report |
| G07 | Add four layers of tests | [07](../modules/07-testing-ml-systems/lab.md) | Intermediate | 6 h | Test suite, coverage report, gate definition |
| G08 | One command, one pipeline | [08](../modules/08-pipeline-automation/lab.md) | Intermediate | 4 h | Entry script, manifest, failure log, timing table |
| G09 | Register, promote, and roll back a model | [09](../modules/09-model-registry/lab.md) | Intermediate | 5 h | Version table, alias history, rollback log |
| G10 | Serve a model with a validated contract | [10](../modules/10-model-serving/lab.md) | Intermediate | 6 h | API, OpenAPI schema, latency table, skew report |
| G11 | Containerise the service | [11](../modules/11-docker-containers/lab.md) | Intermediate | 5 h | Dockerfile, Compose file, size comparison |
| G12 | Gate a model in CI | [12](../modules/12-ci-cd/lab.md) | Advanced | 7 h | Workflow, red/green runs, gate evidence |
| G13 | Orchestrate a nightly retrain | [13](../modules/13-orchestration/lab.md) | Advanced | 6 h | Flow, run history, retry and backfill logs |
| G14 | Detect drift across four weeks | [14](../modules/14-monitoring-drift/lab.md) | Advanced | 7 h | Drift reports, alert rule, retraining memo |
| G15 | Threat-model, scan, and write a model card | [15](../modules/15-security-governance/lab.md) | Advanced | 5 h | STRIDE table, scan reports, model card |
| G16 | Deploy to a local cluster and roll back | [16](../modules/16-cloud-kubernetes/lab.md) | Advanced | 9 h | Manifests, rollout log, Terraform plan, cost sheet |
| G17 | Capstone and incident simulation | [17](../modules/17-capstone/lab.md) | Production | 30+ h | Handover package, postmortem, defence |

### Independent challenges

| # | Challenge | Module | What makes it independent |
|---|---|---|---|
| C01 | Map a real incident to the lifecycle | [01](../modules/01-introduction-to-mlops/independent-challenge.md) | You choose and analyse the case |
| C02 | Break the lock file two ways | [02](../modules/02-python-git-cli-environments/independent-challenge.md) | You design the failure |
| C03 | Write a budgetable debt register | [03](../modules/03-project-organization/independent-challenge.md) | No checklist provided |
| C04 | Add a leakage test | [04](../modules/04-data-quality-versioning/independent-challenge.md) | You decide what counts as leakage |
| C05 | Prove reproducibility | [05](../modules/05-reproducible-training/independent-challenge.md) | You defend the claim with evidence |
| C06 | Stop a plausible bad model | [06](../modules/06-experiment-tracking/independent-challenge.md) | You must find the slice |
| C07 | Write the smallest sufficient test | [07](../modules/07-testing-ml-systems/independent-challenge.md) | Judgement, not coverage |
| C08 | Halve the runtime | [08](../modules/08-pipeline-automation/independent-challenge.md) | Optimisation with proof |
| C09 | Implement a promotion policy | [09](../modules/09-model-registry/independent-challenge.md) | You design the gates |
| C10 | Add batch prediction within budget | [10](../modules/10-model-serving/independent-challenge.md) | You define the budget |
| C11 | Justify what you did not optimise | [11](../modules/11-docker-containers/independent-challenge.md) | Trade-off reasoning |
| C12 | Three correct CI failures | [12](../modules/12-ci-cd/independent-challenge.md) | Each must name the artefact |
| C13 | Conditional retraining | [13](../modules/13-orchestration/independent-challenge.md) | Branch design |
| C14 | Monitoring plan for a foreign model | [14](../modules/14-monitoring-drift/independent-challenge.md) | No access to the code |
| C15 | Three mitigations, one recommendation | [15](../modules/15-security-governance/independent-challenge.md) | Cost and residual risk |
| C16 | Rollout plan with abort criteria | [16](../modules/16-cloud-kubernetes/independent-challenge.md) | Operational judgement |
| C17 | Core or Full capstone | [17](../modules/17-capstone/independent-challenge.md) | Whole-system integration |

---

## How the collection was verified

Every command, expected output and numeric value on these pages was produced by
running the kits in the authoring environment: Windows 11 with Git Bash, Python
3.12.10, and the pins in `examples/requirements-labs.txt`. Where a step could not
be executed, the page says so and gives the procedure to complete it:

| Lab | Limitation | What was verified instead |
|---|---|---|
| 12 · Container | Docker is not installed in the authoring environment | Dockerfile and `.dockerignore` audits (11 checks), Compose parsing, application tests. Image build and run are left to the reader with exact commands |
| 14 · CI workflow | No hosted runner or repository remote | Workflow lint (12 checks), local execution of the workflow's `run:` commands, injected-defect failure |
| 15 · Release workflow | No hosted runner | Validator executed against three bundles; workflow step order linted |

Nothing in the collection requires a cloud account, a paid service, a GPU, or
administrator rights.

A full pass of `examples/labs/verify_all.py` confirms the kits still agree with
the solutions they were written against: **20 of 20 labs accepted** on the last
run, alongside the eight checks each module page keeps for itself.

## Lab safety

- All data is synthetic and generated locally. No real student or customer records
  appear anywhere in the repository.
- The credentials in Lab 19 are fabricated and clearly marked; the scanner redacts
  them, and the page tells you to keep them redacted.
- Every lab that starts a server names how to stop it.
- Cleanup is a numbered section on every page, not an afterthought.

## When a lab goes wrong

Each page has its own troubleshooting table, written from failures that actually
occurred while building the kits. If an expected value differs slightly, compare
against the stated tolerance before assuming you are wrong: versions of
scikit-learn change tree construction, and therefore MAE, by a few hundredths.
Structural differences — a missing key, a wrong status code, a non-zero exit code
— are not tolerance.
