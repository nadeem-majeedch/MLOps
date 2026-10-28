# Pre-publication checklist

Last reviewed: 2026-10-28.

For the repository owner. The audit does not commit, push, deploy, or change
GitHub settings; these are the actions only you can take.

Work through the sections in order. A box is ticked only when the evidence exists,
not when the intention does.

---

## 1. Decide what you are publishing

- [ ] I have read the distinction between the **course website**, the **student
      model service**, and the **ML training/monitoring infrastructure** in
      [Development setup](development-setup.md#1-three-different-deployments).
- [ ] I am publishing the static course site only. No student model or training
      job is being deployed by the Pages workflow.
- [ ] I have read [Known limitations](known-limitations.md) and accept what this
      repository does not prove.

---

## 2. Licence and attribution

- [ ] I have chosen a licence for the **prose** and a licence for the **code**
      (they may differ). A common pair is CC BY 4.0 for prose and MIT for code;
      either is a decision, not a default.
- [ ] I have added a `LICENSE` file (or `LICENSE-CODE` and `LICENSE-CONTENT`) and
      named it in `README.md` and `docs/about/index.md`.
- [ ] I have checked that the licence is compatible with every third-party
      dataset, image, and code excerpt referenced by the course.
- [ ] The generated datasets remain CC0-1.0 as stated in `datasets/README.md`.
- [ ] The instructor details are correct and limited to what I intend to publish:
      **Engr. Dr. Muhammad Nadeem Majeed**, Professor, Department of Data Science
      (PUCIT), University of the Punjab, Lahore, Pakistan.
- [ ] I have not invented a contact address, qualification, accreditation, or
      institutional approval.

!!! warning "Do not publish without a licence decision"
    “All rights reserved” is a valid choice, but it must be deliberate and stated.
    The current pages say a licence has not been declared; update them when you
    add one.

---

## 3. Repository state

A `.git` directory was initialized externally during the audit. It is on branch
`main`, has no commits, and has 493 files staged; nine audit edits are unstaged.
The audit read the index and found no generated paths and no credential patterns.
The owner must review that staged tree before the first commit.

- [ ] `git status --short` shows only intended changes; the nine `AM` files are
      reviewed and staged deliberately, not with a blanket `git add -A`.
- [ ] `git ls-files` contains no `site/`, `.venv*`, `datasets/generated/`,
      `examples/starters/*/data/`, `examples/starters/*/artifacts/`, `mlruns/`,
      `models/`, `__pycache__/`, `.pytest_cache/`, or `.ruff_cache/`.
- [ ] Generated data and model artifacts that are already tracked have been
      removed from the index **and** the ignore rule is in the same change.
- [ ] No credential, token, private key, real student record, or customer data is
      tracked. The fabricated fixtures in Lab 19 are clearly marked as
      non-functional teaching material.
- [ ] The six `examples/raviride/candidates/*.json` example records are either
      intentionally tracked or removed from the index; the new `candidates/`
      ignore rule applies only to records generated in future runs.
- [ ] The default branch is `main`, matching `mkdocs.yml`, the Pages workflow
      guard, and the deployment docs.
- [ ] The repository URL and owner in `mkdocs.yml`, the workflows, and the About
      page match the real repository.

Useful checks:

```bash
git status --short
git ls-files | grep -E "(^site/|\.venv|__pycache__|datasets/generated|mlruns|/models/)" || true
git grep -nE "ghp_|github_pat_|AKIA[0-9A-Z]{16}|BEGIN (RSA |OPENSSH )?PRIVATE KEY" || true
```

```powershell
git status --short
git ls-files | Select-String -Pattern "(^site/|\.venv|__pycache__|datasets/generated|mlruns|/models/)"
```

---

## 4. Local verification

Run from the repository root, with the documentation and lab environments
described in [Development setup](development-setup.md).

- [ ] `python scripts/validate_course.py --verbose` → `0 failed`.
- [ ] `python -m mkdocs build --strict` → exit 0, no warnings.
- [ ] `python examples/labs/verify_all.py` → `20/20 labs verified`.
- [ ] `python examples/starters/verify_starters.py` → `12/12 checks passed`.
- [ ] `python datasets/generate.py --check` → three `OK` lines.
- [ ] `python -m ruff check datasets/generate.py examples/starters` → all checks
      passed (the same command the validation workflow runs).
- [ ] `cd examples/raviride && python -m ruff check .` → all checks passed.
- [ ] `cd examples/raviride && python -m pytest` → 10 passed, after the pipeline
      and a promoted champion.
- [ ] `python examples/modules/16-kubernetes/check_manifests.py --dir solution`
      → 35/35.
- [ ] `python examples/modules/15-security-governance/fairness.py` → the
      documented table (selection 0.250, TPR 0.643, FPR 0.097).

Record the date, OS, Python version, and any count that differs. A green result
without a version is not reproducible.

---

## 5. Optional environment checks

Do these only if the software is available; otherwise record “not run” and keep
the limitation visible.

- [ ] **Docker:** `docker build -t raviride-eta:1.0.0 examples/raviride` succeeds;
      the image runs and answers `/health`, `/ready`, `/predict`.
- [ ] **Docker:** the image does not contain `mlruns/`, credentials, or a writable
      application log.
- [ ] **Kubernetes:** `kind create cluster --name raviride`, load the image,
      `kubectl apply -f examples/modules/16-kubernetes/solution/`, and the
      deployment reaches two ready pods.
- [ ] **Kubernetes:** a rollout to a missing tag does not replace the ready pods;
      `kubectl rollout undo` restores the previous version; record the time.
- [ ] **Kubernetes:** delete the cluster with `kind delete cluster --name
      raviride` and confirm `kind get clusters` is empty.
- [ ] **actionlint:** `actionlint` passes on both workflows. The final audit ran
      v1.7.12 with no findings; it is not installed by `requirements-docs.txt`.
- [ ] **External links:** a manual or scheduled link check finds no dead GitHub or
      third-party URL.

---

## 6. GitHub Pages settings

- [ ] **Settings → Pages → Build and deployment → Source** is set to **GitHub
      Actions**. The workflow cannot set this.
- [ ] The `github-pages` environment exists.
- [ ] If environment protection rules are used, `main` is allowed to deploy and
      the rules do not block the workflow's own `GITHUB_TOKEN`.
- [ ] Actions are enabled for the repository, with permission to run the
      `validate.yml` and `pages.yml` workflows.
- [ ] No repository secret or personal access token is required. The workflows use
      `GITHUB_TOKEN` and OIDC only.
- [ ] The repository guard in `pages.yml` matches the real repository name.
- [ ] I understand that a pull request never deploys (there is no
      `pull_request` trigger), and a fork's push cannot deploy because of the
      repository/ref guard.

---

## 7. First CI run

- [ ] The validation workflow runs on a pull request and both jobs pass.
- [ ] A deliberately broken link or anchor makes the strict build fail; revert it.
- [ ] The Pages workflow runs on `main` and the build job succeeds.
- [ ] The deploy job succeeds, or its failure is diagnosed from the log and the
      Pages settings.
- [ ] The published URL is `https://nadeem-majeedch.github.io/MLOps/` (or the
      custom domain you configured).
- [ ] The landing page, a module page, a lab page, search, code highlighting, and
      the light/dark toggle render on the **deployed** site.
- [ ] A deep link with a `#fragment` resolves on the deployed site.

A successful local build does not prove the deployed site works. Check the
deployed origin separately.

---

## 8. Content spot checks

- [ ] The root `README.md` is student-facing: overview, outcomes, audience,
      syllabus summary, roadmap, links. It contains no install, virtual
      environment, MkDocs, Pages, CI, or developer-troubleshooting commands.
- [ ] `docs/index.md` and `docs/modules/index.md` say all 17 modules have the full
      page set, and name the Module 16 and hosted-CI limitations.
- [ ] Module 15–17 pages open from the navigation and from the lab catalogue.
- [ ] The 20 lab pages each have scenario, setup, data, steps, expected output,
      acceptance criteria, troubleshooting, reflection, extension, cleanup, and
      checklist.
- [ ] Reference solutions remain separate from the student instructions.
- [ ] Assessment weights and rubrics are labelled illustrative, not official.
- [ ] No page claims Docker, Kubernetes, a hosted CI run, or a cloud deployment
      was executed when it was not.

---

## 9. Handover

- [ ] The owner knows the commands in [Build and validation](build-and-validation.md)
      and the failure table in [Troubleshooting builds](troubleshooting-builds.md).
- [ ] The maintenance calendar in [Maintenance](maintenance.md) is in a calendar,
      not only in the document.
- [ ] A second person can build the site from a clean clone by following
      [Development setup](development-setup.md).
- [ ] The repository has an issue-reporting route, and the About page says what
      to include in a report.

---

## 10. Final statement

- [ ] I have read [Final quality report](final-quality-report.md).
- [ ] I accept the verdict and the warnings, or I have closed them.
- [ ] I understand that this audit did **not** commit, push, deploy, or change any
      GitHub setting.
- [ ] The decision to publish is mine, and I can state the evidence behind it.
