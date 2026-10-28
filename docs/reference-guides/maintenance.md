# Maintenance

The site is static, but it is not maintenance-free: dependencies move, links rot,
GitHub changes action runtimes, and content drifts out of sync with the labs. This
page is the routine that keeps those from becoming surprises.

Nothing here publishes changes. Every step ends with a local verification, and
the owner decides what to commit.

---

## 1. Maintenance calendar

| When | Task | Time |
|---|---|---|
| Every content change | Run the [validation commands](build-and-validation.md) | 1 min |
| Monthly | Review open build warnings, broken external links, and stale "not yet" statements | 30 min |
| Quarterly | Review documentation dependencies and action versions | 1 h |
| Each Python/MkDocs/Material major release | Read the release notes, test in a fresh environment, update pins deliberately | 2–3 h |
| Each semester | Check module counts, lab catalogue links, and assessment dates against the syllabus | 1 h |
| Annually | Re-read the licence and About page; confirm the repository owner and contact | 30 min |

A maintenance task that is not on a calendar does not happen. Put the quarterly
review in the owner's calendar, not in a note.

---

## 2. Dependency policy

`requirements-docs.txt` uses **bounded ranges**, not exact pins:

```text
mkdocs>=1.6,<2.0
mkdocs-material>=9.7,<10.0
```

The reason is the theme and plugin contract. Material 9.x targets MkDocs 1.x; a
surprise MkDocs 2.0 would break extensions and the theme. The upper bound is a
compatibility statement, not caution for its own sake.

For reproducible builds, the CI runner installs the newest version allowed by the
range. That means a new patch release can change rendering between two runs. If
that becomes a problem, record the resolved versions in the build log and tighten
the range; do not pin a single version without a review date, because an exact pin
quietly becomes an unpatched dependency.

### Updating documentation dependencies

1. **Read the release notes** for MkDocs and Material. Look for renamed
   configuration keys, removed extensions, and theme changes.
2. **Create a fresh environment.** Do not upgrade inside the environment you use
   for editing; a half-upgraded environment produces misleading results.

   ```bash
   python -m venv .venv-docs-next
   source .venv-docs-next/bin/activate
   python -m pip install -r requirements-docs.txt
   ```

   ```powershell
   python -m venv .venv-docs-next
   .\.venv-docs-next\Scripts\Activate.ps1
   python -m pip install -r requirements-docs.txt
   ```

3. **Record the resolved versions.**

   ```bash
   python -m pip freeze
   ```

4. **Build and validate.**

   ```bash
   python scripts/validate_course.py --verbose
   python -m mkdocs build --strict
   ```

5. **Inspect the rendered site**, not only the exit code. Search, navigation,
   tables, admonitions, code highlighting, and the light/dark toggle are the parts
   that break silently.
6. **If the range itself must change**, edit `requirements-docs.txt`, explain why
   in the change description, and update the version record below.
7. **Delete the trial environment** after merging, or keep it for the next
   review.

Never install a documentation plugin into an environment that also runs the
course labs. The lab pins (scikit-learn 1.5.2, NumPy 2.5.4, FastAPI 0.115.6) are
unrelated, and mixing them makes both harder to diagnose.

### If an upgrade breaks the site

| Symptom | First check |
|---|---|
| Theme colours or fonts change | Material release notes; `theme` block in `mkdocs.yml` |
| An extension is unknown | MkDocs release notes; extension may have moved into Material |
| Search returns nothing | Search plugin configuration; rebuild without `--dirty` |
| A page renders raw Markdown | Indentation or an unclosed fence; run the validator |
| `--strict` reports new anchor warnings | Heading slug rules may have changed; check a sample page |

Revert the `requirements-docs.txt` change and rebuild before debugging further.
A dependency upgrade is not the moment to redesign the theme.

---

## 3. Action version policy

The workflows pin current release tags:

| Workflow | Actions |
|---|---|
| `pages.yml` | `checkout@v7.0.1`, `setup-python@v7.1.0`, `upload-pages-artifact@v5.0.0`, `deploy-pages@v5.0.1` |
| `validate.yml` | `checkout@v7.0.1`, `setup-python@v7.1.0`, `upload-artifact@v7.0.2` |

Review them quarterly:

1. Open each action's **Releases** page.
2. Note the latest stable major and whether the runtime changed (Node 20 → 24 was
   a breaking transition for older majors).
3. Read the release notes for input or output changes.
4. Update the tag in both workflows, in one change.
5. Run the validation workflow on a branch or pull request before merging.
6. Update the table above and the deployment guide's version table.

Do not use `@main` or `@master`. The validator fails an unpinned reference, and a
branch reference means the code that runs can change without a commit in this
repository.

The current majors run on Node 24. GitHub-hosted runners are updated
automatically; a self-hosted runner must be version 2.327.1 or later before these
versions will run. GitHub removed the Node 20 runtime in September 2026, which is
why older action majors are not an option here.

Pinning to a full commit SHA is stricter than a version tag: a tag can be moved,
a SHA cannot. If the repository adopts a security policy that requires SHA
pinning, update the validator to accept SHA references (it already does) and
replace the tags with the SHAs from the release pages.

---

## 4. Content integrity

The validator catches structural drift, not semantic drift. These need a human:

| Drift | How to find it | Fix |
|---|---|---|
| A module is described as "in progress" after it is complete | Search for "being written", "brief", "not yet" | Update the module page, `modules/index.md`, and the landing page status |
| Counts disagree | Compare `docs/index.md`, `modules/index.md`, and the syllabus | Make the syllabus the source of truth |
| A lab's expected output no longer matches | Run the lab's checker | Update the page or the kit, and say which |
| External links 404 | Monthly link check or a reader report | Replace or remove; do not leave a dead link |
| Page numbers, dates, or instructor details change | Semester review | Update About and syllabus |
| Assessment weights are presented as official | Search for "weight" | Keep the "illustrative" label |

External links are not checked by `mkdocs build` or by the validator, because
checking them requires network access and produces flaky failures. Check them
manually each month, or add a scheduled link checker as a separate, non-blocking
workflow.

### Regenerating data

If `datasets/generate.py` changes intentionally:

```bash
python datasets/generate.py
python datasets/generate.py --check
python scripts/validate_course.py
```

If the numbers in a lab page change as a result, update the page in the same
commit, with the new output. A generator change that leaves the documentation
quoting old hashes or counts is worse than no change.

---

## 5. Repository hygiene

Keep generated output out of version control:

| Path | Status | Why |
|---|---|---|
| `site/` | Ignored | Build output, reproducible in seconds |
| `.venv-docs/`, `.venv-verify/` | Ignored | Local environments |
| `datasets/generated/` | Ignored | Regenerate with one command |
| `examples/starters/*/data`, `artifacts/` | Ignored | Generated by each starter |
| `__pycache__/`, `.pytest_cache/`, `.ruff_cache/` | Ignored | Tool caches |

Before a handover, check:

```bash
git status --short
git ls-files | grep -E "(^site/|\.venv|__pycache__|datasets/generated)" || true
```

```powershell
git status --short
```

If a generated file is already tracked, remove it from the index and add the
ignore rule in the same change. Deleting it from disk only fixes the symptom.

---

## 6. Change record

Keep a short log of maintenance that affects the build. A table in the change
description is enough; a separate document becomes stale.

| Date | Change | Verification |
|---|---|---|
| 2026-10-26 | Added validation and Pages workflows; validator script | `validate_course.py` 9/9 passed; strict build clean; workflow YAML parsed |
| 2026-10-27 | Completed Module 15–17 page sets; added the fairness audit and Kubernetes manifest kit; strengthened the validator; pinned `pathspec` for DVC | 12/12 validator; strict build clean; 20/20 labs; 12/12 starter checks; 10 API tests |
| 2026-10-26 | Pinned actions to current releases | Versions read from official release pages |
| 2026-10-28 | Final release audit; corrected overclaimed verification wording, added the `candidates/` ignore rule, refreshed the release reports | 12/12 validator; strict build; 20/20 labs in a fresh environment; 12/12 starters; 10 API tests; `actionlint` 1.7.12 clean |
| _(next)_ | | |

The record answers "when did we last look at this?" without archaeology in the
commit history.

---

## 7. Version record

Update this table when the documented build changes.

| Component | Version | Checked |
|---|---|---|
| Python | 3.12.10 | 2026-10-28 |
| MkDocs | 1.6.1 | 2026-10-28 |
| Material for MkDocs | 9.8.0 | 2026-10-28 |
| `actions/checkout` | v7.0.1 | 2026-10-28 |
| `actions/setup-python` | v7.1.0 | 2026-10-28 |
| `actions/upload-pages-artifact` | v5.0.0 | 2026-10-28 |
| `actions/deploy-pages` | v5.0.1 | 2026-10-28 |
| `actions/upload-artifact` | v7.0.2 | 2026-10-28 |

---

## 8. Ownership and handover

| Responsibility | Owner |
|---|---|
| Approving and publishing changes | Repository owner |
| Repository and Pages settings | Repository owner |
| Dependency and action review | Maintainer, with owner approval |
| Content accuracy | Module author, reviewed by the owner |
| Security reports | Owner, through the repository's private reporting route |

If ownership changes, update:

- the About page and the repository's contact details;
- `site_url`, `repo_url`, and `edit_uri` in `mkdocs.yml`;
- the repository guard in `pages.yml` (`github.repository == ...`);
- the workflow badge or links, if any.

A handover that leaves a hard-coded old owner in the deploy guard produces a
workflow that silently skips deployment. Check the guard.

---

## 9. What not to do

| Don't | Why |
|---|---|
| Run `mkdocs gh-deploy` | It commits and pushes generated files |
| Commit `site/` | Generated output, large diffs, merge conflicts |
| Loosen `--strict` to fix a red build | It hides the defect the build found |
| Pin an exact dependency with no review date | Becomes unpatched and forgotten |
| Use `@main` for an action | The code can change without a commit here |
| Add a token to a workflow | `GITHUB_TOKEN` and OIDC are sufficient |
| Change Pages settings from a script | Settings are the owner's decision |
| Edit generated data or model files by hand | The generator and manifest are the provenance |
