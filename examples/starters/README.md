# Starter projects

Three reusable project templates, one per level. Each is a real, runnable
project: pinned dependencies, generated data, tests, and a README you can follow
without the rest of the course.

| Template | Level | Task | You get | Time |
|---|---|---|---|---|
| [beginner-support-risk](beginner-support-risk/README.md) | Beginner | Binary classification | Validation, one pipeline, metric floor, 13 tests | ~2 min |
| [intermediate-eta-service](intermediate-eta-service/README.md) | Intermediate | Regression + API | Artifact metadata, FastAPI, contract tests, Dockerfile | ~3 min |
| [advanced-monitoring-pipeline](advanced-monitoring-pipeline/README.md) | Advanced | Imbalanced classification | Group split, gated registry, rollback, PSI drift, CI example | ~3 min |

All three generate their own data, so none needs a download. None requires an
account, a cloud service, or Docker (the intermediate Dockerfile is optional and
was not built in the authoring environment; its README says so).

---

## Which one to copy

| Your situation | Start from | Then |
|---|---|---|
| First project; the model is the easy part | Beginner | Add tests before adding features |
| You have a model and need an API | Intermediate | Add the contract test first, then the container |
| You need release control and monitoring | Advanced | Read the registry limitation before trusting the gate |
| You are starting the capstone | Advanced | Replace the model and data, keep the shape |

Copy the folder rather than working in place:

```bash
cp -r examples/starters/intermediate-eta-service ~/projects/my-service
cd ~/projects/my-service
```

```powershell
Copy-Item examples\starters\intermediate-eta-service $HOME\projects\my-service -Recurse
Set-Location $HOME\projects\my-service
```

Then change the package name, the data, and the README. Leave the test structure
and the pinned requirements until you have something working; both are load-
bearing.

---

## Shared conventions

- **`src/<package>/`** for importable code, a thin entry point at the root.
- **`config.yaml`** (or `configs/pipeline.yaml`) for paths, seeds, and thresholds.
  No magic numbers in the code that decides pass or fail.
- **`artifacts/`** for generated models and metrics; **`data/`** for generated
  data. Both ignored by version control.
- **`pytest.ini`** with `pythonpath`, so `python -m pytest` works from the project
  directory without installing the package.
- **Exit codes** carry the gate: 0 pass, non-zero fail, with a printed reason.
- **Honest READMEs**: expected output, tolerance, and what was not tested.

---

## Verify all three

From the repository root, with the course environment active:

```bash
python examples/starters/verify_starters.py
```

```powershell
python examples\starters\verify_starters.py
```

The script runs each project in its own directory: generate, train, test, and for
the advanced project validate, promote, and monitor. It treats the advanced
monitor's exit code 2 as the expected result, because drift is the finding.

Observed in the authoring environment (Python 3.12.10, Windows 11, Git Bash):

```text
PASS  advanced: generate data             exit 0
PASS  advanced: tests                     exit 0: 29 passed
PASS  advanced: validate                  exit 0
PASS  advanced: train                     exit 0
PASS  advanced: promote                   exit 0
PASS  advanced: monitor (drift expected)  exit 2
PASS  beginner: generate data             exit 0
PASS  beginner: train                     exit 0
PASS  beginner: tests                     exit 0: 13 passed
PASS  intermediate: generate data         exit 0
PASS  intermediate: train                 exit 0: PASS: MAE 2.182 <= ceiling 3.500
PASS  intermediate: tests                 exit 0: 23 passed

12/12 checks passed
```

Run it after changing a template. A template that no longer runs is worse than no
template, because it teaches a false shape.

---

## What the templates deliberately leave out

| Missing | Why | Where it is taught |
|---|---|---|
| Experiment tracking | Changes the shape of the code; belongs after the basics | [Module 06](../../docs/modules/06-experiment-tracking/index.md) |
| Real registry service | A local JSON registry shows the rule without hiding it | [Module 09](../../docs/modules/09-model-registry/index.md) |
| Authentication | Teaching auth badly is worse than not teaching it | [Module 15](../../docs/modules/15-security-governance/index.md) |
| Kubernetes manifests | Nothing here needs a cluster | [Module 16](../../docs/modules/16-cloud-kubernetes/index.md) |
| Real data | Privacy and licence; synthetic data lets you break things | [datasets/README.md](../../datasets/README.md) |

The graduation route is the [capstone brief](../../docs/projects/capstone.md): it
requires the pieces these templates omit, in one system.
