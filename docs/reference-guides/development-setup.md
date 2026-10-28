# Development setup

This page sets up a machine to **edit and build the course website**. It is for
maintainers, not students. A student only needs the [prerequisites](../prerequisites/index.md)
and a terminal; nothing here is required to study the course.

The site is static HTML generated from Markdown by MkDocs. There is no Node
toolchain, no bundler, no database, and no service to run. Setup is one Python
environment and one install command.

---

## 1. Three different deployments

The word "deployment" means three unrelated things in this repository. Confusing
them leads to the wrong credentials, the wrong workflow, and the wrong advice.

| | **A. Course website** | **B. Student model service** | **C. ML infrastructure** |
|---|---|---|---|
| **What is deployed** | Static HTML, CSS, and search index | A trained model behind FastAPI, usually in a container | Training pipelines, schedules, monitoring jobs |
| **Where** | GitHub Pages, from this repository | The student's machine, a container host, or a cluster | A runner, a scheduler, or a cloud account |
| **Who does it** | Repository owner, through GitHub Actions | The student, as part of Modules 10–12 | The student, as part of Modules 13–16 |
| **Credentials** | None beyond the per-run `GITHUB_TOKEN` | None; the service has no auth in the course | Optional cloud account, never required |
| **Documented in** | This page set, especially [deployment](github-pages-deployment.md) | [Module 10](../modules/10-model-serving/index.md), [Module 11](../modules/11-docker-containers/index.md) | [Module 13](../modules/13-orchestration/index.md), [Module 16](../modules/16-cloud-kubernetes/index.md) |
| **Paid service** | No | No | No for the core route |

Everything below concerns **A only**. Building the site does not touch the
student's model, and deploying a student model does not publish the site.

---

## 2. Required software

| Requirement | Version used here | Why |
|---|---|---|
| **Python** | 3.12.10 | Matches the version in the documented build and on the CI runner |
| **pip** | Ships with Python | Installs the two documentation packages |
| A terminal | PowerShell 7, bash, or zsh | Commands are given for both families |
| A text editor | Any | UTF-8 and LF line endings are the only requirements |
| Git | Optional | Only needed if you are cloning or inspecting history; the build does not use it |

Not required: Node, npm, Docker, Kubernetes, a cloud account, a GitHub token, or
administrator rights. The site has no build-time network access beyond `pip`
installing the pinned packages.

Python 3.11 is within MkDocs's supported range, but this repository's verification
uses 3.12 only. If you build with 3.11, say so when reporting the result; a
difference that appears on one interpreter is worth knowing about.

### Disk and time

| Item | Size or time |
|---|---|
| Documentation virtual environment | About 45 MB |
| Installed site output (`site/`) | About 40 MB with the full 244-page course |
| First install | 30–60 seconds on a normal connection |
| Full strict build | 3–5 seconds |

---

## 3. Get the repository

If you already have the folder, skip this. Otherwise clone it with the method
your host provides:

```bash
git clone https://github.com/nadeem-majeedch/MLOps.git
cd MLOps
```

```powershell
git clone https://github.com/nadeem-majeedch/MLOps.git
Set-Location MLOps
```

Do not run `git commit`, `git push`, or `mkdocs gh-deploy` while following these
guides. The documentation below builds locally only; publishing is the owner's
decision and happens through the Pages workflow.

---

## 4. Create the documentation environment

Use a dedicated environment at the repository root. Do not reuse the environment
you use for the course labs: the labs install scikit-learn, FastAPI, and MLflow,
and none of those belong in the documentation build.

**Windows 11 · PowerShell 7**

```powershell
python -m venv .venv-docs
.\.venv-docs\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-docs.txt
```

**Linux / macOS**

```bash
python3 -m venv .venv-docs
source .venv-docs/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-docs.txt
```

Expected: the prompt is prefixed with `(.venv-docs)`. If PowerShell refuses to run
the activation script, allow scripts for this terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then confirm the versions:

```bash
python -m mkdocs --version
python -c "import material; print(material.__version__)"
```

```text
python -m mkdocs, version 1.6.1 from .../site-packages/mkdocs (Python 3.12)
9.8.0
```

If the numbers differ, the build still works within the pins, but record the
difference in your report. `requirements-docs.txt` deliberately caps MkDocs below
2.0, because Material for MkDocs 9.x targets the 1.x plugin and theme system.

---

## 5. What is installed and why

`requirements-docs.txt` has two direct dependencies:

| Package | Role | Constraint |
|---|---|---|
| `mkdocs` | Static site generator, navigation, search index | `>=1.6,<2.0` |
| `mkdocs-material` | Theme, extensions bundle, icons | `>=9.7,<10.0` |

The extensions used by the site (`admonition`, `pymdownx.*`, `tables`, `toc`)
ship with MkDocs or Material; there are no third-party plugins. That is
deliberate: fewer moving parts, no build-time fetching, and a site that works
offline.

Do not add a plugin that fetches data during a build. A build that needs the
network is a build that fails on a locked-down runner and cannot be reproduced
later.

---

## 6. Repository layout for maintainers

```text
mkdocs.yml                  site configuration and navigation
requirements-docs.txt      documentation dependencies
README.md                  student-facing course introduction
scripts/
└── validate_course.py     links, nav, module structure, syntax, datasets
.github/workflows/
├── validate.yml            pull-request and push validation (no deployment)
└── pages.yml               build and deploy to GitHub Pages
docs/                      everything published
├── reference-guides/       these maintainer pages
├── templates/              authoring templates (excluded from the site)
└── audit-phase-0.md        historical audit (excluded from the site)
examples/                  lab kits, starter projects, reference project
datasets/                  synthetic data generator and documentation
site/                      generated output; ignored by version control
```

`docs/templates/` and `docs/audit-phase-0.md` are excluded in `mkdocs.yml`. They
contain placeholder links and historical detail; publishing them would create
navigation noise. They stay readable on GitHub.

The validator's exclusions must match `mkdocs.yml`. If you add an exclusion,
update both, or the validator will demand a nav entry for a page that is not
published.

---

## 7. First verification

Run both commands before editing anything. A clean baseline makes later failures
attributable to your change.

```bash
python scripts/validate_course.py --verbose
python -m mkdocs build --strict
```

Expected, on an unmodified checkout:

```text
PASS  navigation        241 nav targets exist
PASS  navigation        all 241 published pages are in nav
PASS  links             767 relative links and images resolve
PASS  modules           17 modules have the full 9-page set
PASS  labs              20 lab pages have the required student sections
PASS  readme            student-facing policy satisfied; no build commands
PASS  instructor        name, title, department, and university present
PASS  markdown          code fences are balanced on every page
PASS  python            142 Python files compile
PASS  dataset manifest  3 files match their hashes
PASS  secrets           no credential patterns in docs, scripts, or workflows
PASS  workflows         2 workflow file(s) parse and pin actions

12 passed, 0 failed, 0 skipped
```

The exact counts change as pages are added. What matters is `0 failed` and a
strict build that ends with `Documentation built in ... seconds` and no
`WARNING` lines.

MkDocs 1.6 prints a notice about a future 2.0 release. It is informational, not a
build warning, and it does not fail `--strict`. Set `NO_MKDOCS_2_WARNING=1` to
silence it if it distracts you.

---

## 8. Editor settings

| Setting | Value | Why |
|---|---|---|
| Encoding | UTF-8, no BOM | A BOM appears as a stray character in the first heading |
| Line endings | LF | CI runs on Linux; CRLF causes noisy diffs, not build failures |
| Indent | 4 spaces for Python, 2 for YAML | Matches the existing files |
| Wrap | Soft, 88–100 columns | Prose is wrapped; tables and code are not |
| Trailing whitespace | Strip, except two spaces for a Markdown line break | Invisible whitespace is a diff hazard |

No formatter is enforced for Markdown. Keep the shape of the surrounding page.

---

## 9. Environment variables

None are required. The build reads `mkdocs.yml` and `docs/`.

| Variable | Effect | When to use |
|---|---|---|
| `NO_MKDOCS_2_WARNING=1` | Hides the MkDocs 2.0 notice | Optional, cosmetic |
| `PYTHONUTF8=1` | Forces UTF-8 I/O on Windows | If a build fails with a `UnicodeDecodeError` |
| `SOURCE_DATE_EPOCH` | Not used here | — |

Never put a token, personal access token, or repository secret in a local file for
this build. None is needed; the Pages workflow uses the per-run `GITHUB_TOKEN` and
OIDC.

---

## 10. Windows notes

- **Activation policy.** Use `Set-ExecutionPolicy -Scope Process` as above. Do not
  change the machine-wide policy to build documentation.
- **Case sensitivity.** Windows is case-insensitive; the Linux CI runner is not.
  A link to `Lab-01.md` that works locally fails in CI. Use exact filenames.
- **Paths in examples.** Documentation commands use forward slashes; PowerShell
  accepts them. Backslashes in code blocks are for `powershell` blocks only.
- **Long paths.** The repository is shallow enough that the 260-character limit is
  not normally reached; if it is, enable long paths rather than moving the
  repository into a deeply nested folder.

---

## 11. Next steps

| I want to... | Read |
|---|---|
| See the site while editing | [Local preview](local-preview.md) |
| Understand `--strict`, links, and validation | [Build and validation](build-and-validation.md) |
| Edit pages and follow content conventions | [Website development](website-development.md) |
| Publish, or understand the Pages settings | [GitHub Pages deployment](github-pages-deployment.md) |
| Update a dependency or an action | [Maintenance](maintenance.md) |
| Fix a failing build | [Troubleshooting builds](troubleshooting-builds.md) |
