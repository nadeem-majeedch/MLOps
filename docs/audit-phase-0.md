# Phase 0 Audit: Repository State and Foundation Plan

**Course:** Machine Learning Operations (MLOps) - self-study textbook and laboratory manual
**Instructor:** Engr. Dr. Muhammad Nadeem Majeed, Professor, Department of Data Science (PUCIT), University of the Punjab, Lahore
**Repository:** <https://github.com/nadeem-majeedch/MLOps>
**Audit date:** 23 October 2026
**Audit scope:** Repository contents, history, documentation, configuration, workflows, and readiness for course authoring.

---

## 1. How this audit was performed

| Check | Method | Result |
|---|---|---|
| Repository metadata | Read-only GitHub REST API (`/repos/...`) | Public repository, created 23 Oct 2026, `size: 0` |
| Branches | Read-only API (`/branches`) | Empty list |
| Commits | Read-only API (`/commits`) | `409` - "Git Repository is empty" |
| File tree | Read-only API (`/git/trees/HEAD`) | `409` - no tree exists |
| Default branch | Repository metadata | `main` (no commits on it) |
| Licence | Repository metadata | `null` |
| Topics / description | Repository metadata | Description "Machine Learning Operations"; no topics |
| Local working folder | Directory listing | Contains only `.freebuff/` tool metadata; **not** a Git checkout |

No `git` command that writes to history was run. No clone, no `git init`, no remote changes.

> **Superseded in part (Phase 1, 23 October 2026).** The provisional 13-module spine in Section 5.2 and the folder tree in Section 5 have been replaced by the 17-module syllabus in [syllabus/detailed-syllabus.md](syllabus/detailed-syllabus.md). `docs/prerequisites.md` moved to [prerequisites/index.md](prerequisites/index.md), and `docs/syllabus/` and `docs/learning-roadmap/` were added. The repository-state findings, risks, and decisions below remain a record of what was true at Phase 0 and have not been rewritten; Section 7's phase plan still applies, with module numbers shifted.

---

## 2. Repository state found

**The repository is empty.** There is no README, no course content, no documentation, no configuration, no workflow, no licence, and no contributor history. The remote has a repository shell and nothing else.

Local environment note: the folder used for this work (`/e/ML-Ops`) is empty apart from `.freebuff/`, and it has no `.git` directory. It is therefore *not* a clone of the GitHub repository. Files written in this phase exist only in that folder and must be placed into a real clone before they can be committed. This is recorded as Issue I-1 in Section 6.

### 2.1 Inventory

| Area | Found | Notes |
|---|---|---|
| Root README | None | Nothing to preserve |
| Documentation (`docs/`, `wiki`) | None | None |
| Course modules, lessons, labs | None | None |
| Assessments, projects, rubrics | None | None |
| Sample data, notebooks | None | None |
| Configuration (`.gitignore`, `.editorconfig`, linters, `pyproject.toml`) | None | None |
| CI/CD workflows (`.github/workflows`) | None | None |
| Issue/PR templates, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` | None | None |
| Licence, citation metadata (`CITATION.cff`) | None | No licence selected |
| GitHub Pages / site config | None observed | No branch content, so no site build |
| Releases, tags, packages | None | None |

---

## 3. Existing assets worth preserving

**None.** There is no prior content to migrate, repair, style-match, or avoid overwriting. Every future file is a first version, which means the conventions created in this phase will set the pattern for the whole course. They should be treated as binding rather than aspirational.

### 3.1 Incomplete work

None. There are no half-finished modules, stubs, or TODOs to carry forward.

### 3.2 Broken references

None can exist yet; there are no documents, links, images, or code samples. Link integrity becomes a live risk only from Phase 1 onward, and the standards in [course-standards.md](course-standards.md) include a link-check requirement for exactly that reason.

---

## 4. Risks and issues requiring attention

| ID | Risk | Impact | Likelihood | Mitigation in this phase |
|---|---|---|---|---|
| R-1 | **No licence.** A public repository without a licence is legally "all rights reserved"; students and other universities may not legally reuse the material. | High | Certain (already true) | README states reuse terms plainly and flags that a licence must be chosen before wide release. Instructor decision required (Issue I-2). |
| R-2 | **No `.gitignore`.** The first lab a student runs will produce `.venv/`, `mlruns/`, `data/raw/`, and Docker artefacts. Without ignore rules these enter history and bloat the repository permanently. | High | High (inevitable in Phase 1) | Recorded as a Phase 1 blocker; ignore rules are specified before any executable content is added. |
| R-3 | **Windows-first audience vs. Linux-oriented tooling.** Most MLOps tutorials assume bash. Half-written instructions will strand Windows 11 students. | High | High | Standards mandate PowerShell 7 as the primary command, with bash/zsh alternatives, and a reproducible command-block format. |
| R-4 | **Docker Desktop requirement.** Container labs need Docker Desktop with WSL 2, which has hardware, BIOS-virtualisation, and licensing implications on Windows 11. | Medium | High | Prerequisites document states disk, RAM, virtualisation, and licence conditions up front instead of at the first container lab. |
| R-5 | **Tool drift.** MLOps tooling changes faster than a course edition. Unpinned examples silently rot. | Medium | High | Standards require pinned versions, a "last verified" date on every lab, and a documented re-verification policy. |
| R-6 | **Cost ambiguity.** Cloud-deployed MLOps examples can generate charges; student accounts can be misused. | Medium | Medium | Fixed cost labels and a rule that every activity must be completable locally for free; cloud paths labelled optional and paid. |
| R-7 | **Resource-heavy labs on student laptops.** Airflow, Kafka, or full observability stacks can exceed 8 GB RAM. | Medium | Medium | Resource labels plus an explicit lightweight alternative for each heavy lab. |
| R-8 | **Unverified content.** AI-assisted authoring makes it easy to publish commands that were never run. | High | Medium | Rule: a command block is only "verified" if its output was captured from a real run; otherwise it must be marked unverified. |
| R-9 | **Ethics and privacy drift.** Real datasets with personal data create consent, licensing, and privacy problems. | High | Medium | Standards restrict core labs to synthetic or openly licensed data, with no personally identifying information. |
| R-10 | **Breadth without depth.** "Complete MLOps" can become a list of 40 tools with no transferable understanding. | Medium | Medium | A 12-module spine with named outcomes per module, and a capstone that reuses earlier artefacts rather than introducing new tools. |
| R-11 | **Single-author maintenance load.** Every module added increases review and re-verification burden. | Medium | Medium | Templates plus a definition-of-done checklist keep quality consistent without re-deciding structure each time. |
| R-12 | **Assessment integrity.** Publishing solutions next to problems undermines self-assessment. | Low | Medium | Separate `solutions/` location and a solutions-handling rule in the assessment template. |

---

## 5. Target repository structure

The structure below is the target for the completed course. Only the bolded files exist after Phase 0; everything else is planned and is not yet written.

```text
MLOps/
├── README.md                        # course landing page (exists)
├── LICENSE                          # planned, instructor decision
├── CITATION.cff                     # planned
├── .gitignore                       # planned, Phase 1 blocker
├── .editorconfig                    # planned
├── CONTRIBUTING.md                  # planned
├── CODE_OF_CONDUCT.md               # planned
│
├── docs/
│   ├── course-standards.md          # exists - authoring rules
│   ├── prerequisites.md             # exists - student readiness
│   ├── audit-phase-0.md             # exists - this report
│   ├── templates/
│   │   ├── lesson-template.md       # exists
│   │   ├── lab-template.md          # exists
│   │   └── assessment-template.md   # exists
│   ├── setup/                       # planned - environment setup guide (Windows-first)
│   ├── glossary.md                  # planned - single source of term definitions
│   ├── faq.md                       # planned
│   └── instructor-notes/            # planned - delivery guidance, kept separate from student text
│
├── modules/                         # planned - the textbook, in teaching order
│   ├── 00-orientation/              # course mechanics, environment, GitHub account
│   ├── 01-foundations/              # ML lifecycle, roles, maturity, why models fail
│   ├── 02-reproducible-projects/    # Python environments, packaging, config, seeds, tests
│   ├── 03-version-control/          # Git for ML teams, review, commits, large files
│   ├── 04-data-versioning/          # data versioning, contracts, validation, leakage
│   ├── 05-experiment-tracking/      # tracking, comparison, model registry
│   ├── 06-packaging-serving/        # refactor to package, API, validation, containers
│   ├── 07-ci-cd/                    # automated tests, quality gates, build and release
│   ├── 08-deployment/               # batch vs online, rollout, rollback
│   ├── 09-monitoring/               # logs, metrics, drift, alerting, dashboards
│   ├── 10-orchestration/            # pipelines, scheduling, retries, idempotency
│   ├── 11-security-governance/      # secrets, access, privacy, fairness, model cards
│   └── 12-capstone/                 # end-to-end system, runbooks, incident response
│
├── projects/                        # planned - milestone and capstone briefs, datasets
├── assessments/                     # planned - quizzes, assignments, rubrics, answer keys
│   └── solutions/                   # planned - worked solutions, kept out of lesson flow
├── assets/                          # planned - diagrams, screenshots, shared figures
├── data/                            # planned - small synthetic or openly licensed datasets
│   └── README.md                    # planned - provenance and licence per dataset
└── .github/
    ├── workflows/                   # planned - link check, Markdown lint, Python tests
    ├── ISSUE_TEMPLATE/              # planned
    └── pull_request_template.md     # planned
```

### 5.1 Why this shape

- **`modules/NN-slug/`** puts the reading path in the folder names, so the course reads in order on GitHub, in an editor, and in any future site generator. Modules hold `README.md`, numbered lessons, and their own labs, which keeps a lesson and its practice together.
- **`projects/` and `assessments/` at the top level** separate graded and integrative work from explanatory text, so students can find "what am I assessed on" without knowing the module number.
- **`assessments/solutions/`** keeps answers out of the reading path.
- **`docs/`** holds the rules of the course rather than the course itself: standards, setup, glossary, FAQ, and instructor-only notes.
- **`assets/`** is shared because the same lifecycle diagram appears in several modules; per-module duplication would drift.
- **`data/`** holds small, redistributable datasets only; anything larger is fetched by a script and documented by provenance.

### 5.2 Module spine and levels

| Module | Title | Level | Central question |
|---|---|---|---|
| 00 | Orientation and Setup | Foundation | How do I work through this course on my own machine? |
| 01 | Foundations of MLOps | Foundation | What breaks between a notebook and production, and why? |
| 02 | Reproducible Python Projects | Foundation | Why does it work on my machine and not yours? |
| 03 | Version Control for ML Teams | Foundation | How do a team and its data change together safely? |
| 04 | Data Versioning and Quality | Intermediate | Which data produced this model, and is it still valid? |
| 05 | Experiment Tracking and Model Registry | Intermediate | Which experiment is the model we ship? |
| 06 | From Notebook to Service | Intermediate | How does a model become something another program can call? |
| 07 | CI/CD for Machine Learning | Intermediate | How do we stop a bad model from reaching users automatically? |
| 08 | Deployment Patterns and Serving | Advanced | How do we release, roll back, and scale without panic? |
| 09 | Monitoring, Observability, and Drift | Advanced | How do we know the model is wrong before users tell us? |
| 10 | Orchestration and Automation | Advanced | How does the whole pipeline run unattended and safely? |
| 11 | Security, Privacy, and Responsible MLOps | Advanced | Who can do what, with whose data, and can we prove it? |
| 12 | Capstone: Production-Grade ML System | Production | Can I run this system, explain it, and fix it at 2 a.m.? |

Each module is expected to contain: overview, 3-6 lessons, 1-3 labs, a knowledge check, at least one graded artefact, and a troubleshooting section drawn from real failures.

---

## 6. Issues requiring instructor decisions

| ID | Issue | Why it needs the instructor | Suggested default |
|---|---|---|---|
| I-1 | The working folder is not a Git checkout of the remote. | Files produced here are not in the repository and cannot be committed until they are inside a clone. | Copy this folder's contents into a fresh clone of the repository, then commit from there. Do not `git init` this folder and force-push it over the remote. |
| I-2 | No licence has been chosen. | Licensing is a legal decision for the author and institution. | A permissive documentation-friendly licence (for example CC BY 4.0 for prose, MIT for code) chosen before public announcement. |
| I-3 | Course credit hours, semester length, and assessment weights are unknown. | They determine the number of graded items and the pacing of modules. | Author a modular course that can be trimmed to 12 or 16 weeks; state the assumption in the course guide. |
| I-4 | Whether student work is submitted through GitHub, an LMS, or both is unknown. | It changes the submission sections in assessments. | Write assessments to be submission-system neutral. |
| I-5 | Localisation and language policy are unknown (English only?). | Affects glossary depth and phrasing. | English only, with plain-language definitions and a glossary. |
| I-6 | Whether any cloud account is permitted at all. | Cloud labs are optional, but even optional paths need a policy on student accounts and spend. | No cloud account required; every core outcome achievable locally and free. |

---

## 7. Phase plan

| Phase | Scope | Status |
|---|---|---|
| 0 | Audit, standards, templates, prerequisites, root README | **Complete in this phase** |
| 1 | Repository hygiene (`.gitignore`, licence, citation, `.editorconfig`, link/Markdown CI), Module 01 orientation, and the Module 02 environment setup guide | Superseded by Phase 1 (syllabus and architecture) |
| 2 | Modules 01-04 with labs and knowledge checks | Not started |
| 3 | Modules 05-08 with labs and assessments | Not started |
| 4 | Modules 09-12, capstone brief, runbooks | Not started |
| 5 | Full link check, command re-verification pass, glossary completion, accessibility review | Not started |

**Phase 1 acceptance criteria (proposed):** ignore rules proven against a real lab run; setup guide executed start-to-finish on Windows 11 and once on macOS or Linux; the orientation module's knowledge check passes with no unverified commands; CI rejects broken internal links.

---

## 8. Decisions and assumptions recorded in this phase

1. **Windows 11 with PowerShell 7 is the primary platform**, with Linux/macOS given as labelled alternatives. Rationale: the stated student population, and the fact that most MLOps material silently assumes a POSIX shell.
2. **Free and open-source, local-first.** Every core outcome must be achievable offline after setup, without paid services or accounts beyond a free GitHub account.
3. **No course content is written in this phase**, per the brief. Only the rules, templates, readiness material, and landing page.
4. **The root README is a course front door, not an operations manual.** Installation, environment setup, and deployment guidance live in `docs/setup/` and module material.
5. **Every executable instruction is treated as a claim that must be verified** by running it and capturing the output.
6. **Datasets are synthetic or openly licensed**, and no lab requires personal data.
7. **The instructor's name and affiliation appear in the README About section and in `CITATION.cff` once created**, not repeated in every lesson.

---

## 9. Verification log for this phase

| Claim | How verified |
|---|---|
| Remote repository exists and is public | GitHub REST API returned `200` with `"private": false` |
| Remote has no content | `/commits` returned `409` "Git Repository is empty"; `/branches` returned `[]` |
| No licence declared | API field `license: null` |
| Local folder had no prior course files | Directory listing showed only `.freebuff/` |
| Local folder is not a Git checkout | `git status` returned "not a git repository" |
| Documents created in this phase exist and links resolve | Re-checked by filesystem listing and link extraction after writing (Section 10 of the final report) |

---

*This audit is a working document. It will be superseded once Phase 1 adds repository hygiene and the setup guide.*
