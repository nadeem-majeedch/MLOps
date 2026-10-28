# Build and validation

Two commands decide whether a documentation change is acceptable:

```bash
python scripts/validate_course.py --verbose
python -m mkdocs build --strict
```

They check different things, and neither is a substitute for the other. The
validator checks repository integrity — links, navigation, module structure,
syntax, datasets, and workflows. MkDocs checks that the site it is about to
generate is internally consistent and renders. Run both before you ask the owner
to commit.

Neither command publishes anything.

---

## 1. Build the site

```bash
python -m mkdocs build
```

```text
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: .../site
INFO    -  Documentation built in 3.28 seconds
```

The output is a self-contained static site in `site/`: HTML, CSS, JavaScript for
search and theme behaviour, and copied assets. There is no server-side component.
`site/` is generated output and is ignored by version control; never edit it and
never commit it.

Open it through a local server, not by double-clicking a file. `site/` contains the
files at its root, so serving it directly puts the site at `/`; to reproduce the
project subpath, put the output inside a folder named `MLOps`:

```bash
rm -rf .preview && mkdir -p .preview
cp -r site .preview/MLOps
python -m http.server 8001 --directory .preview
```

```powershell
Remove-Item .preview -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory .preview | Out-Null
Copy-Item site .preview\MLOps -Recurse
python -m http.server 8001 --directory .preview
```

Then visit <http://127.0.0.1:8001/MLOps/>. Opening `site/index.html` directly
usually renders an unstyled page, because the generated links and assets assume a
web server and the project base path.

---

## 2. What `--strict` changes

```bash
python -m mkdocs build --strict
```

MkDocs normally logs a warning and continues. `--strict` makes **any warning abort
the build with a non-zero exit code**. In this repository that turns these into
failures:

| Warning | Meaning | Usual fix |
|---|---|---|
| `contains a link to '...' which is not found` | Relative link to a missing file | Correct the path or create the page |
| `contains a link to '...' which does not contain an anchor` | `#fragment` points at a heading that no longer exists | Update the fragment to the new slug |
| `is included in the 'nav' configuration, which is not found` | A nav entry names a missing file | Fix the path or remove the entry |
| `exists in the docs directory, but is not included in the nav` | A published page is unreachable from the menu | Add it to `nav`, or exclude it deliberately |
| `The following pages exist in the docs directory, but are not included...` | Same issue, reported as a group | Same fix |

A clean build ends with `Documentation built in ... seconds` and no `WARNING`
lines. If you cannot reach zero warnings, report the remaining ones. Do not
remove `--strict` from CI to make a red run green.

MkDocs defaults some of these checks to `info`, which means `--strict` would not
fail on them. `mkdocs.yml` sets them to `warn` explicitly:

```yaml
validation:
  nav:
    omitted_files: warn
    not_found: warn
    absolute_links: warn
  links:
    not_found: warn
    absolute_links: warn
    unrecognized_links: warn
    anchors: warn
```

If those settings are removed, a broken anchor or an unlisted page can publish
without a warning. The validator still catches both, but keep the build strict as
well: the two tools use different parsers, and a defect that one misses is often
caught by the other.

### The MkDocs 2.0 notice

MkDocs 1.6 prints a notice that a 2.0 release exists and that Zensical is its
successor. It is informational, not a warning, and does not fail `--strict`. Set
`NO_MKDOCS_2_WARNING=1` to hide it. Do not upgrade to 2.x without checking the
Material compatibility and updating the pins deliberately; see
[Maintenance](maintenance.md).

---

## 3. Check links and navigation

`scripts/validate_course.py` is a standard-library script that runs without
MkDocs installed. It exists because MkDocs only reports what it can resolve; the
validator also checks anchors against heading slugs, module completeness, Python
syntax, and workflow pinning.

```bash
python scripts/validate_course.py
```

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

Counts change as pages are added. The requirement is `0 failed`, not a specific
number. Exit codes: `0` for success (skips are allowed), `1` for at least one
failure.

### What each check does

| Check | Rule | Failure means |
|---|---|---|
| **Navigation targets** | Every `.md` path named in `nav` exists under `docs/` | A page was renamed or deleted without updating `mkdocs.yml` |
| **Navigation completeness** | Every published page appears in `nav` | A page is published but unreachable |
| **Links** | Every relative link and image resolves; `#anchor` exists in the target page | A typo, a renamed heading, or a page moved |
| **Modules** | All 17 modules have the nine page types, at least 2,500 words total, and no page under 120 words | A module is a stub or a file was misplaced |
| **Labs** | All 20 lab pages carry the scenario, setup, task, data, steps, output, acceptance, troubleshooting, reflection, extension, cleanup, and checklist sections | A lab is missing a student-facing section |
| **README** | The root README has the required student sections and no build/environment commands or code fences | Technical instructions leaked into the student overview |
| **Instructor** | Name, title, department, and university appear in the README and About page | Missing or inconsistent attribution |
| **Markdown** | Code fences are balanced | An unclosed fence swallows the rest of the page |
| **Python** | Every `.py` under `scripts/`, `datasets/`, and `examples/` compiles | A syntax error, often in a lab kit |
| **Dataset manifest** | If generated data exists, its SHA-256 matches the manifest | The generator changed without regenerating, or a file was edited by hand |
| **Secrets** | No obvious token or private-key pattern in docs, scripts, or workflows | A credential was pasted into content |
| **Workflows** | YAML parses; every action is pinned to a version tag or commit SHA | A workflow typo, or an action referenced by branch |

### Exclusions

The validator skips `docs/templates/` and `docs/audit-phase-0.md`, matching
`exclude_docs` in `mkdocs.yml`. Templates contain placeholder paths such as
`NN-title.md` and would fail every link check. If you add an exclusion to
`mkdocs.yml`, add it to `EXCLUDED` in the script as well.

### Anchors

The anchor check approximates Python-Markdown's slug rules: lowercase, punctuation
removed, spaces to hyphens, duplicates suffixed `_1`, `_2`. It also reads explicit
`<a id="...">` anchors. If a heading contains unusual Unicode, verify the link in
the rendered page rather than trusting the approximation.

An anchor check cannot prove the destination *discusses* the right thing. It only
proves the heading exists. When you rename a section, search for links to its old
slug:

```bash
grep -rn "old-heading-slug" docs --include="*.md"
```

```powershell
Select-String -Path docs\*.md,docs\**\*.md -Pattern "old-heading-slug"
```

---

## 4. Validate Python

The validator compiles each Python file without importing it:

```bash
python scripts/validate_course.py --skip-python   # skip the syntax check
```

Syntax is the minimum. For behaviour, run the starter projects:

```bash
python -m pip install -r examples/requirements-labs.txt
python examples/starters/verify_starters.py
```

Expected: `12/12 checks passed`. That script generates data, trains, tests, and
runs the advanced pipeline's gate and monitor; the monitor exits `2` on drift by
design, and the verifier treats that as success.

Run `ruff` on the same code if it is installed:

```bash
python -m ruff check datasets/generate.py examples/starters
```

The lab dependencies are large (scikit-learn, FastAPI, MLflow). Install them in a
separate environment, not in `.venv-docs`. The validation workflow does exactly
this, in a separate job.

---

## 5. Rebuild the dataset manifest

The generated data is optional, but if it exists the validator checks it:

```bash
python datasets/generate.py
python datasets/generate.py --check
```

Expected:

```text
OK       raviride_trips.csv  600 rows
OK       study_support.csv   400 rows
OK       equipment_sensors.csv  500 rows
```

`generated/` is ignored by version control. A hash mismatch usually means the
generator changed; regenerate and commit the generator, not the data.

---

## 6. Validate the workflows

The validator parses every `.github/workflows/*.yml` with PyYAML and checks that
each `uses:` reference is pinned to a version tag (`@v7.0.1`) or a full commit
SHA. It does not execute the workflows, and it is not a full linter.

For deeper checks, install [actionlint](https://github.com/rhysd/actionlint) and
run it from the repository root:

```bash
actionlint
```

```powershell
actionlint
```

`actionlint` is not installed by `requirements-docs.txt`. It was run at version
1.7.12 against both workflows during the final documentation audit and reported no
findings. If you adopt it in CI, add it as a separate step and pin its version.

The validator cannot prove that an action version exists, that a permission is
sufficient, or that the repository's Pages settings are correct. A one-time audit
confirmed that the current pins exist in their upstream repositories, but no local
check repeats that. A real deployment is the only proof of permissions and Pages
settings; the checklist in
[Troubleshooting builds](troubleshooting-builds.md) covers them.

---

## 7. Reproduce CI locally

The validation workflow runs these commands in order. Running them locally in the
same order is the closest you can get without pushing.

| CI step | Local equivalent |
|---|---|
| Checkout | Your working directory |
| `pip install -r requirements-docs.txt` | Same, in `.venv-docs` |
| `python scripts/validate_course.py --verbose` | Same |
| `python -m mkdocs build --strict` | Same |
| `pip install -r examples/requirements-labs.txt` | Same, in a separate environment |
| `python -m ruff check ...` | Same |
| `python examples/starters/verify_starters.py` | Same |

The CI runner is Linux, so two things differ:

- **Case sensitivity.** A link that resolves on Windows may fail on Linux.
- **Line endings and encoding.** CRLF is tolerated, a BOM is not.

If you are on Windows, the case difference is the one that catches people. Rename
files to the exact case used in links, and prefer lowercase, hyphenated names.

---

## 8. What these checks do not prove

| Not checked | Why it matters | Where it is covered |
|---|---|---|
| That the deployed site is reachable | A successful build can still fail to publish | [Deployment](github-pages-deployment.md), owner action |
| That GitHub Pages is set to "GitHub Actions" | The workflow cannot configure repository settings | Owner, Settings > Pages |
| That an action version exists | The validator only checks the reference shape | First workflow run |
| That a permission is sufficient | OIDC and Pages permissions are evaluated by GitHub | First deployment |
| That prose is correct | Spelling and sense are not machine-checkable | Review, [Website development](website-development.md) |
| That a lab kit runs | The starter job covers three templates, not twenty labs | Lab checkers, [Lab catalogue](../labs/index.md) |
| That anchors discuss the right topic | Only that the heading exists | Human review |

---

## 9. Before you hand the change over

- [ ] `python scripts/validate_course.py --verbose` reports `0 failed`.
- [ ] `python -m mkdocs build --strict` ends without warnings.
- [ ] Every new page is in `nav` and linked from an existing page.
- [ ] Renamed headings have their inbound anchors updated.
- [ ] New Python files compile; changed starter code still passes its tests.
- [ ] No `site/`, generated data, or virtual environment is staged.
- [ ] No secret, token, personal path, or real personal data appears.
- [ ] You did **not** run `mkdocs gh-deploy`, `git commit`, or `git push`.

The owner decides when to commit and push. A local green build is the evidence
they need to make that decision.
