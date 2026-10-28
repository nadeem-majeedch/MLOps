# Troubleshooting builds

Start with the local commands, not with GitHub:

```bash
python scripts/validate_course.py --verbose
python -m mkdocs build --strict
```

Most failures are one of: a link, a missing nav entry, a missing dependency, or a
filename whose case differs from its link. The tables below go from the most
common to the most specific.

---

## 1. The environment

| Symptom | Cause | Fix |
|---|---|---|
| `No module named mkdocs` | Environment not active, or dependencies installed elsewhere | Activate `.venv-docs`; `python -m pip install -r requirements-docs.txt` |
| `pip` installs into the wrong Python | `python` and `pip` resolve to different installations | Use `python -m pip`, never bare `pip` |
| `python: command not found` (Linux) | Only `python3` is on the path | `python3 -m venv .venv-docs`; use `python3` consistently |
| Activation blocked on Windows | Execution policy | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| Install succeeds but the theme is missing | Only `mkdocs` was installed, not `mkdocs-material` | Install from `requirements-docs.txt` |
| Wrong MkDocs major version | A global install or a stale environment | `python -m mkdocs --version`; recreate the environment |

Check what is actually running:

```bash
python -c "import sys, mkdocs; print(sys.executable); print(mkdocs.__version__)"
```

```powershell
python -c "import sys, mkdocs; print(sys.executable); print(mkdocs.__version__)"
```

The executable path must be inside `.venv-docs`.

---

## 2. Configuration

| Error | Cause | Fix |
|---|---|---|
| `Config file 'mkdocs.yml' does not exist` | Wrong working directory | `cd` to the repository root |
| `Config value 'docs_dir': The path ... isn't an existing directory` | `docs_dir` changed or the folder is missing | Keep `docs_dir: docs`; check the folder exists |
| `Error parsing 'mkdocs.yml': ...` | YAML indentation, a tab, or an unquoted `:` | Use spaces; quote labels containing `:` |
| `The following pages exist ... but are not included in the 'nav'` | A published page is missing from nav | Add it, or exclude it in `mkdocs.yml` and the validator |
| `A relative path to '...' is included in the 'nav' ... not found` | Renamed or deleted page still listed | Update the nav path |
| `Unrecognised theme name: 'material'` | Material not installed in the active environment | Install `-r requirements-docs.txt` |
| A nav label shows as `!!python/name:...` | YAML tag typo in an extension | Copy the extension block from a working version |

`mkdocs.yml` is the only configuration file that affects the published site.
`requirements-docs.txt` affects which versions render it. Nothing else is read at
build time.

---

## 3. Links and anchors

`--strict` makes these fatal. That is intended.

### `contains a link to '...' which is not found`

The target path does not exist relative to the page. Check:

1. The spelling and extension (`.md`, not `.html`).
2. The relative depth: from `docs/labs/lab-01.md`, a module is
   `../modules/...`, not `../../modules/...`.
3. The filename case. Windows is case-insensitive; the Linux CI runner is not.

```bash
grep -rn "the-missing-target" docs --include="*.md"
```

### `contains a link to '...' which does not contain an anchor`

The page exists, but the heading slug does not. A heading `## 4. Debugging and
diagnosis` becomes `#4-debugging-and-diagnosis`: lowercase, punctuation removed,
spaces to hyphens.

1. Open the target page and copy the heading.
2. Recompute the slug; do not guess.
3. Search for inbound links before renaming a heading:

   ```bash
   grep -rn "old-slug" docs --include="*.md"
   ```

4. Update every link, or add the old slug as an explicit anchor if the heading
   must change.

### A link works locally but fails in CI

Almost always case. `Lab-01.md` and `lab-01.md` are the same file on Windows and
different files on Linux. Rename to lowercase, hyphenated names and update links.

A second cause is a link to a path outside `docs/`. MkDocs can only resolve pages
inside `docs_dir`. Link to repository files with a full GitHub URL, or mention the
path in code formatting instead of a Markdown link.

### The validator reports an anchor the build accepts

The validator approximates Python-Markdown's slug rules. If the rendered page
shows the anchor working, trust the build, and report the discrepancy so the
validator's slug function can be improved. Do not disable the check.

---

## 4. Navigation

| Symptom | Cause | Fix |
|---|---|---|
| A new page is published but not in the menu | Not listed in `nav` | Add it in the right section |
| A page appears in the menu but 404s | Nav path typo or missing file | Fix the path |
| Sections appear in the wrong order | YAML list order | `nav` is ordered; move the entry |
| A page is listed twice | Duplicate entry | Remove one |
| The validator demands a nav entry for `templates/` | Exclusion lists are out of sync | Add the path to `EXCLUDED` in `scripts/validate_course.py` |
| A page is intentionally unpublished but MkDocs warns | Missing `exclude_docs` entry | Add it to `mkdocs.yml` `exclude_docs` and the validator |

Navigation is a contract with the reader. A page that exists but cannot be reached
from the menu is effectively unpublished, even if its URL works.

---

## 5. Rendering

| Symptom | Cause | Fix |
|---|---|---|
| Page is unstyled | Opened `site/index.html` from disk | Serve it: `python -m http.server 8001 --directory site`, then `/MLOps/` |
| Raw Markdown appears in the page | Unclosed code fence or wrong indentation | Balance fences; run the validator |
| An admonition renders as text | Missing `!!!` indentation (four spaces for the body) | Indent the body four spaces |
| A table renders as text | No blank line before the table | Add a blank line |
| Icons show as `:octicons-...:` | Material not loaded, or the icon name is wrong | Check the theme install and the icon name |
| Search finds nothing | Build was served from the wrong root, or `--dirty` skipped the index | Rebuild clean; serve through a server |
| Code highlighting is missing | Fence has no language | Add `powershell`, `bash`, `python`, `yaml`, or `text` |
| A wide table overflows | Too many columns for the viewport | Split the table or shorten cells |

`--dirty` is the usual cause of "the page looks stale". Do a clean build before
concluding that something is broken.

---

## 6. Base path and Pages URL

| Symptom | Cause | Fix |
|---|---|---|
| Site loads at `/MLOps/` but CSS 404s | The artifact root is wrong: `site/` was not the uploaded directory | Upload `site/`; do not upload the repository root |
| Canonical or sitemap URLs point at the old path | `site_url` lacks the repository name or the trailing slash | Set `site_url: https://<owner>.github.io/MLOps/`; rebuild |
| Landing page 404s but a deep page works | Pages is serving a branch with an old index, or the artifact root is wrong | Set Pages source to GitHub Actions; check the artifact is `site/` |
| Everything works at `github.io` but canonical URLs use `github.io` on a custom domain | `site_url` still points at `github.io` | Update `site_url` and rebuild |
| The site appears at the account root instead of `/MLOps/` | Repository is named `<owner>.github.io`, or Pages is serving a user site | Confirm the repository name and the environment's URL |

The project path itself comes from the repository name, not from `site_url`.
MkDocs emits relative links, so navigation continues to work under `/MLOps/` even
when `site_url` is wrong. A wrong `site_url` shows up in the canonical tag, the
sitemap, and the preview mount point rather than in a broken stylesheet.

---

## 7. The deployment workflow

These errors appear in the **Actions** tab, not in a local build.

| Error | Meaning | Owner action |
|---|---|---|
| `Get Pages site failed` / `Failed to create deployment (status: 404)` | Pages is not enabled, or the source is not GitHub Actions | Settings > Pages > Source: GitHub Actions |
| `Resource not accessible by integration` | The job lacks `pages: write` | Check job permissions in `pages.yml` |
| `id-token: write` error, or OIDC failure | The deploy job is missing `id-token: write` | Restore the job-level permission |
| `Branch "main" is not allowed to deploy to github-pages due to environment protection rules` | The environment allows a different branch | Adjust the environment rule, or deploy from `main` |
| `Artifact not found for name: github-pages` | The upload step failed or used a different name | Check the build job; `upload-pages-artifact` uses `github-pages` by default |
| `Multiple artifacts named "github-pages"` | Two uploads in one run | Upload once, in one job |
| Deploy job is skipped | The repository/ref guard did not match | Confirm `github.repository` and the branch in `pages.yml` |
| Deploy job waits indefinitely | Environment requires manual approval | Owner approves in the run, or removes the rule |
| Workflow does not start on a docs change | Path filters exclude the changed file | Add the path to `on.push.paths` |
| Fork's run skips deploy | The repository guard deliberately prevents it | Expected; forks publish to their own Pages, if enabled |

### Permissions, in one place

```yaml
permissions:
  contents: read          # workflow default, enough to check out and build
jobs:
  deploy:
    permissions:
      pages: write        # create the Pages deployment
      id-token: write     # request the OIDC token that proves the source
```

The build job must not have `pages: write`. The deploy job must not check out and
run repository code. Keeping those separate is what makes the deployment path
reviewable.

### It deployed but the site is old

1. Check the run's commit SHA against the commit you expected.
2. Hard-refresh, or open a private window; Pages caches aggressively at the edge.
3. Confirm the `deploy` job, not only `build`, is green.
4. Check that Pages source is GitHub Actions, not a branch.
5. If a custom domain is configured, confirm DNS still resolves to Pages.

Propagation is usually under a minute but can take longer after a configuration
change.

---

## 8. Validator failures

The script's output names the check and the file. Common cases:

| Output | Meaning | Fix |
|---|---|---|
| `links ... -> path (anchor not found)` | Heading slug mismatch | Update the link or add the heading |
| `page is not in nav: ...` | Published page without a menu entry | Add it |
| `module ...: missing concepts.md` | Module folder incomplete | Restore the page or correct the folder name |
| `unbalanced code fence: ...` | Odd number of fence lines | Close the fence |
| `python ... SyntaxError` | A lab or script does not compile | Fix the syntax; the file is not imported, so this is a real parse error |
| `dataset manifest ... hash differs` | Generator changed, or data edited | Regenerate; commit the generator, not the data |
| `possible GitHub personal token` | A credential-shaped string in content | Remove it; if it is a deliberate fake, rewrite it so it cannot be mistaken for a live token |
| `workflow ... unpinned action reference` | `uses: owner/action@main` | Pin a version tag or commit SHA |
| `workflow ... YAML does not parse` | Indentation or a duplicate key | Fix the YAML; `python -c "import yaml; yaml.safe_load(open(...))"` |

The validator is intentionally conservative. A false positive is a signal to
improve the check or the content, not to delete the check.

---

## 9. Reproducing CI on your machine

```bash
python -m venv .venv-docs
source .venv-docs/bin/activate
python -m pip install -r requirements-docs.txt
python scripts/validate_course.py --verbose
python -m mkdocs build --strict
```

```powershell
python -m venv .venv-docs
.\.venv-docs\Scripts\Activate.ps1
python -m pip install -r requirements-docs.txt
python scripts/validate_course.py --verbose
python -m mkdocs build --strict
```

For the starter job, use a separate environment:

```bash
python -m venv .venv-verify
source .venv-verify/bin/activate
python -m pip install -r examples/requirements-labs.txt
python -m ruff check datasets/generate.py examples/starters
python examples/starters/verify_starters.py
```

The last command prints `12/12 checks passed`. The advanced project's monitor
exits `2` on drift; that is expected and the verifier treats it as success.

What still differs: the runner is Linux, its Python patch version may move within
3.12, and GitHub evaluates permissions and Pages settings that cannot be tested
locally.

---

## 10. When to stop and report

Stop, and report rather than work around, when:

- the failure needs a repository setting, a token, or a deployment you are not
  authorised to perform;
- the only fix you can see is disabling `--strict`, deleting a test, or adding a
  credential;
- a dependency upgrade requires a theme or configuration redesign;
- the deployed site is broken in a way that a local build cannot reproduce.

A good report contains: the command, the full error, the local result, the CI run
URL if one exists, and what you already ruled out. "The build is broken" costs a
round trip; the four lines above usually do not.

---

## 11. Quick diagnostic sequence

```text
wrong Python?        python -c "import sys; print(sys.executable)"
deps missing?        python -m pip show mkdocs mkdocs-material
config broken?       python -c "import yaml; yaml.safe_load(open('mkdocs.yml'))"
links broken?        python scripts/validate_course.py --verbose
build warnings?      python -m mkdocs build --strict
page unstyled?       serve site/ over HTTP, not file://
CI-only failure?     check case, then permissions, then Pages settings
deploy skipped?      check the repository and branch guard
deploy failed?       read the deploy job log, not the build log
```

If none of these identifies the cause, open
[Build and validation](build-and-validation.md), confirm the documented versions,
and report the difference. A reproducible environment is the first thing to rule
out.
