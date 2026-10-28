# Known limitations

This page states what the repository does **not** prove, and what a reader should
not infer from a green local build. It is deliberately blunt: a limitation that is
not written down becomes a false claim in a student's evidence.

Last reviewed: 2026-10-28.

---

## 1. Environment limitations of this audit

| Tool or service | Available? | Consequence |
|---|---|---|
| Git repository history | **No commits** — a `.git` directory was initialized externally during the audit, on branch `main` | `git status` and `git ls-files` were inspected: 493 files staged, 9 audit edits unstaged, no generated paths or credential patterns staged. There is no commit history or diff against a commit to review. |
| Docker | **No** | No image was built or run. Lab 12 and the container steps in Modules 11 and 17 use a static Dockerfile audit and application tests, not a real build. |
| `kind`, `kubectl`, Kubernetes | **No** | Module 16's live cluster exercise was not executed. The manifests were checked offline (35 checks); rollout and rollback behaviour is unverified. |
| `actionlint` | **Not installed by default; v1.7.12 was downloaded for this audit** | Both workflows were linted with no findings. A contributor without the binary still gets only the PyYAML parse and pinning checks from `validate_course.py`. |
| GitHub-hosted runner | **No** | Neither workflow has run on GitHub. Permissions, Pages settings, environment rules, and artifact upload are unverified. |
| Cloud account / Terraform | **No** | No cloud deployment, Terraform plan, or cost quote was produced. All cloud paths are optional and labelled. |
| A second operating system | **No** | Commands were executed on Windows 11 with Git Bash. Linux/macOS and PowerShell variants are documented but were not run here. |
| A browser visual check | **No** | The site was built and served over HTTP; page HTML, links, assets, and the project subpath were checked, but no screenshot or visual design review was performed. |
| External HTTP links | **No** | `mkdocs build` and the validator check relative links only. GitHub URLs and third-party references were not fetched, so a dead external link would not fail the build. |

These are limitations of the audit environment, not necessarily of the
repository. A machine with Docker, `kind`, and a GitHub remote can close most of
them; the procedures are in the module pages and in
[Pre-publication checklist](pre-publication-checklist.md).

---

## 2. Course-content limitations

### Module claims versus independent re-verification

Modules 01–14 were verified in earlier phases against the RaviRide reference
project. This audit re-ran the shared executable suites (20 lab checkers, three
starter projects, the reference pipeline, the API tests, the fairness audit, and
the manifest checker) but did **not** re-execute every command printed in every
lesson of Modules 01–14. A command can drift from the code without a link or a
syntax check noticing. The module pages state their own verification basis; treat
“measured on Windows 11, Python 3.12.10” as a record from that run, not a
guarantee for a different library patch version.

### Module 15 tools

The module names `gitleaks`, `pip-audit`, and `fairlearn`, but the executable lab
uses the supplied Python scanner and fairness script so it can run offline without
those packages. The tools are described, not installed by the course. Their
absence is not a failure of the lab, but a student who claims to have run
`gitleaks` must actually run it.

### Module 16 live path

The 35-check manifest review is real and reproducible. The cluster rollout,
probe behaviour, HPA, PDB drain, and rollback are **not** verified here. The module
says so in its overview, worked example, and lab. Do not cite the 35/35 result as
evidence that the service deploys.

### Module 17 capstone

The capstone is a specification and a guided process, not a pre-built submission.
The advanced starter and the incident fixture are references; neither is a
completed capstone. The rubric's peer-handover and timed-incident criteria
require a person and a clock, which cannot be automated.

### Synthetic data

All datasets are generated from rules and contain no real people. That makes them
safe, and it also makes them simpler than reality:

- the relationships are the ones the generator encodes;
- drift happens in the columns the generator shifts;
- the GPA band in the support dataset is a near-deterministic driver of the
  label, which is useful for teaching proxy variables and misleading as a claim
  about real students;
- absolute metrics are not benchmarks.

### Lab fixtures that look like secrets

`examples/labs/lab-19-security-review/` contains fabricated API keys, passwords,
emails at `example.edu`, and dates of birth. They are intentional teaching
fixtures, not live credentials. The scanner redacts them. Do not copy them into a
report, and do not treat their presence as a leak.

---

## 3. Assessment and institutional limitations

- The assessment framework is a **suggested self-study structure**, not an
  official university grading policy. Weights, rubrics, and pass marks are
  illustrative.
- The course does not claim accreditation, credit, or institutional approval.
- The instructor details are limited to the name, title, department, and
  university published on the About page. No contact address, qualification, or
  approval is invented.
- Legal and regulatory references in Module 15 are starting points, not legal
  advice. Data-protection obligations depend on jurisdiction, purpose, and the
  institution's rules.

---

## 4. Repository and publication limitations

### No licence

There is no `LICENSE` file. The README and About page say so, and the default
applies: the author retains all rights, and reuse beyond viewing requires
permission. A public course should declare a licence for the prose and the code,
and separately respect the licences of third-party tools and datasets. That is an
owner decision; this audit did not choose one.

### Uncommitted Git repository

A `.git` directory was initialized externally during the audit; `main` has no
commits. At the end of the audit, 493 files were staged and nine files (the README,
three content pages, four reference guides, and the RaviRide ignore file) had
unstaged audit edits. `git ls-files` contained no `site/`, virtual environment,
generated dataset, model, MLflow, or cache paths, and `git grep --cached` found no
credential patterns. The staged tree is still uncommitted, so the owner must
review it and create the first commit. Nothing in this audit altered the index or
history.

### External links and repository URLs

The site links to GitHub paths under `nadeem-majeedch/MLOps`. If the repository is
renamed, moved, or made private, those links and the Pages workflow's repository
guard will be wrong. The build cannot detect this.

### Site size

The full site is about 40 MB because every module page is rendered and the search
index is substantial. It is generated output and is ignored; it is not a reason
to commit `site/`.

### Environment drift in a reused virtual environment

A long-lived verification environment in this workspace once had `packaging 26.3`,
which conflicts with MLflow 2.17's `packaging<25` requirement. It was aligned to
the documented `packaging==24.2`, and `pip check` now reports no broken
requirements. A separate environment built from `examples/requirements-labs.txt`
also passes `pip check` and all 20 labs. The repository pins are compatible; a
stale local environment may not be. Recreate it rather than debugging the conflict.

---

## 5. Operational limitations students must state

Any student evidence that claims one of these without doing it is not credible:

- a Docker image built and run, when Docker was unavailable;
- a Kubernetes deployment, when no cluster was used;
- a hosted CI run, when the workflow was only linted locally;
- a cloud deployment or cost figure, when no account or price source was used;
- a peer handover, when the author performed both roles;
- a model card disparity claim, when the group rows were too few to support it;
- a fairness conclusion, when only one threshold and one split were measured.

The course's honesty criterion is not “everything worked”. It is “the evidence
matches the claim”.
