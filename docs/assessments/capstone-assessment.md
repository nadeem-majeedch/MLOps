# Capstone assessment

> **Illustrative self-study framework.** The weights and bands below are a
> suggested structure for marking your own work, not an official university
> grading scheme. No institution has approved them. The
> [assessment framework](../syllabus/assessment-framework.md) explains the design;
> an instructor adopting the course should adjust weights to local regulations.

The [capstone brief](../projects/capstone.md) says what to build. This page says
how it is judged, what evidence earns each band, and how to mark yourself without
rewarding effort.

---

## 1. What is assessed

| Artefact | Marks | Rubric section |
|---|---|---|
| Rerunnable pipeline from a clean clone | 8 | [2.1](#21-rerunnable-pipeline-8) |
| Versioned data and model with provenance | 6 | [2.2](#22-versioned-data-and-model-6) |
| Automated tests and a CI gate that genuinely fails | 8 | [2.3](#23-tests-and-a-gate-that-fails-8) |
| Served endpoint with validation | 6 | [2.4](#24-served-endpoint-6) |
| Monitoring with an actionable alert | 6 | [2.5](#25-monitoring-and-an-alert-6) |
| Runbook covering deploy, rollback, and top three alerts | 4 | [2.6](#26-runbook-4) |
| Model card and defence document | 2 | [2.7](#27-model-card-and-defence-2) |
| **Total** | **40** | |

Cross-cutting criteria — reproducibility, correctness, operability, honesty,
ethics, clarity — are scored separately, 0–4 each, and a capstone with 0–1 on
**honesty** or **operability** is not a pass regardless of the artefact total.
Those two describe whether the system can be trusted in someone else's hands.

The Core and Full variants are assessed against the same seven artefacts. The
Full variant's extra work shows up in the cross-cutting criteria, especially
operability and honesty about scale — not in extra artefact marks.

---

## 2. Artefact rubrics

Each artefact is scored in bands. A band is earned by observable evidence, not by
the presence of a file.

### 2.1 Rerunnable pipeline (8)

| Band | Descriptor |
|---|---|
| 7–8 | A clean clone installs and trains using only the README; the reported metric returns within a tolerance stated before the run; a second run agrees; a peer reproduces it without questions |
| 5–6 | Reproduces on the author's machine and a clean clone with one undocumented step that the author explains on request |
| 3–4 | Runs, but requires an untracked file, an absolute path, or a manual step; metric not comparable |
| 0–2 | Does not run from a clean clone |

**Evidence required:** the clone command, the install command, the metric, the
tolerance, and the second run. A screenshot of a terminal is acceptable only if
the command and result are in the same frame.

### 2.2 Versioned data and model (6)

| Band | Descriptor |
|---|---|
| 5–6 | Data and model are versioned with hashes; a manifest ties source, date, rows, columns, and hash; an earlier version resolves and trains |
| 3–4 | Versioned, but retrieval is undocumented or the model's data lineage is missing |
| 1–2 | A file path and a date only |
| 0 | No provenance |

### 2.3 Tests and a gate that fails (8)

| Band | Descriptor |
|---|---|
| 7–8 | Schema, unit, data, model, and contract tests; CI blocks a degraded model; three injected regressions each fail the correct step with the stated reason; the failing runs are kept |
| 5–6 | Tests exist and the gate blocks, but one layer is missing or a failure names the wrong step |
| 3–4 | Tests pass but the gate has never blocked anything, or blocks for the wrong reason |
| 0–2 | No automated gate, or a gate that cannot fail |

**Evidence required:** the three red runs and one green run after a fix. A green
badge alone is worth nothing here.

### 2.4 Served endpoint (6)

| Band | Descriptor |
|---|---|
| 5–6 | Health, readiness, prediction, and model-info; five malformed payloads each return 422 naming the field; contract test ties serving to training; served version identifiable |
| 3–4 | Predicts and validates, but no contract test or no version visibility |
| 1–2 | Returns predictions for well-formed input only |
| 0 | No endpoint |

### 2.5 Monitoring and an alert (6)

| Band | Descriptor |
|---|---|
| 5–6 | Input and prediction monitoring, a frozen reference, an alert that fires on the injected batch and not on controls, with owner and first diagnostic step; data drift and accuracy claims separated |
| 3–4 | Monitoring exists; the alert fires for everything or for nothing useful |
| 1–2 | A dashboard with no alert |
| 0 | No monitoring |

### 2.6 Runbook (4)

| Band | Descriptor |
|---|---|
| 4 | Deploy, rollback, and the top three alerts; a peer completes deploy and rollback in under 30 minutes; rollback timed under five |
| 3 | Complete but untested by another person |
| 2 | Covers deploy only, or omits rollback |
| 0–1 | Notes, not a procedure |

### 2.7 Model card and defence (2)

| Band | Descriptor |
|---|---|
| 2 | Intended use, limitations with evidence, measured disparity, monitoring plan; the defence answers "why not simpler?" and "what breaks at 10× load?" with specifics |
| 1 | Card present but generic; defence describes effort |
| 0 | Neither |

---

## 3. Cross-cutting criteria (0–4 each)

| Criterion | 0 | 2 | 4 |
|---|---|---|---|
| **Reproducibility** | Cannot rebuild | Rebuilds with help | A stranger rebuilds from the repository alone |
| **Correctness** | Claims contradicted by behaviour | Mostly correct, one silent gap | Tested behaviour matches every claim; no swallowed errors |
| **Operability** | Only the author can run it | Documented, partly tested | A peer deploys, rolls back, and diagnoses using the runbook |
| **Honesty** | Overclaims, hides failures | States some limits | Limitations, untested claims, and failure modes stated with evidence |
| **Ethics and privacy** | Ignores affected people | Mentions risks | Names who is affected, the disparity measured, and the mitigation |
| **Clarity** | Unreadable | Understandable with effort | A reader who has not seen the code can follow the architecture and decisions |

A 4 is not "excellent prose". It means a sceptical reviewer would be convinced by
the evidence.

---

## 4. Self-assessment checklist

Mark only what you can show. Each line maps to a rubric band.

### Reproducibility

- [ ] `git clone` into a new directory, install, train: metric within tolerance.
- [ ] The tolerance was written before the run, and you can say where.
- [ ] Two runs agree; both `metrics.json` files are kept.
- [ ] No absolute paths, secrets, or untracked files are required.
- [ ] The dataset resolves from its version record.

### Tests and release

- [ ] Schema, unit, data, model, and contract tests exist.
- [ ] Three injected regressions each fail the correct CI step.
- [ ] A degraded model is blocked by the gate, and the message names the metric.
- [ ] The failing runs are in `evidence/ci/`.
- [ ] The fixed run passes, and its log is kept.

### Serving

- [ ] `/health`, `/ready`, `/predict`, `/model-info` exist.
- [ ] Five malformed payloads return 422 with a named field.
- [ ] The contract test fails when the feature order changes.
- [ ] The served model version is visible from the API.
- [ ] p95 latency is measured against a budget defined beforehand.

### Operations

- [ ] Rollback is demonstrated and timed under five minutes.
- [ ] The alert fires on the injected batch and not on a control batch.
- [ ] The alert names an owner and a first diagnostic step.
- [ ] The runbook was followed by someone else, or after 48 hours away.
- [ ] The postmortem names the detection gap, not only the cause.

### Governance

- [ ] Secret scan is clean or every finding is explained.
- [ ] The model card states at least two limitations with evidence.
- [ ] Disparity between two meaningful groups is measured.
- [ ] Data provenance and licence are recorded.
- [ ] Who is affected by a false positive and a false negative is stated.

### Defence

- [ ] "Why not simpler?" answered with a specific cost you avoided.
- [ ] "What breaks at 10× load?" answered with a measured or estimated limit.
- [ ] The top residual risk is named with a monitoring plan.
- [ ] One decision you would make differently is described with the evidence.

Score: count checked lines per group, compare with the band descriptors. A group
with unchecked lines cannot earn the top band for that artefact.

---

## 5. Evidence inventory

Your submission should contain these files. If one is missing, say why rather
than leaving the folder empty.

```text
evidence/
├── clean-clone/       # commands and metric from a fresh clone
├── ci/                # three red runs, one green run, the gate output
├── serving/           # five 422 responses, latency measurement
├── rollback/          # timed log, served version before and after
├── drift/             # reports, control batches, the alert
├── security/          # secret scan, dependency scan, threat model
└── handover/          # peer timings, questions they had to answer
```

Name files with the date and the claim they support:
`2026-10-26-clean-clone-mae.txt`, `2026-10-27-gate-blocks-noz08.log`. A folder of
screenshots named `IMG_0421.png` is not evidence a marker can use.

---

## 6. Defence

Fifteen minutes, written or oral, with these time boxes:

| Time | Question | What earns the top band |
|---|---|---|
| 2 min | What does the system do, and what does it not do? | A boundary, not a feature list |
| 5 min | Which decision would you make differently now, and what changed your mind? | A specific decision, the evidence, and the alternative |
| 5 min | Why not simpler? What breaks at 10× load? | A cost avoided and a measured or estimated limit |
| 3 min | Top residual risk, and what you would monitor | A named risk with a signal and a response |

If you are studying alone, record the answers in writing and keep them. The
purpose is articulation: a system you cannot explain without the code open is not
one you understand.

---

## 7. Mark sheet

Copy this into your portfolio and fill it in before reading your own report.

| Component | Max | Awarded | Justification (one sentence) |
|---|---|---|---|
| Rerunnable pipeline | 8 | | |
| Versioned data and model | 6 | | |
| Tests and gate | 8 | | |
| Served endpoint | 6 | | |
| Monitoring and alert | 6 | | |
| Runbook | 4 | | |
| Model card and defence | 2 | | |
| **Artefacts total** | **40** | | |
| Reproducibility | 4 | | |
| Correctness | 4 | | |
| Operability | 4 | | |
| Honesty | 4 | | |
| Ethics and privacy | 4 | | |
| Clarity | 4 | | |

Rules:

1. **Score the artefact before reading your narrative.** Reading first rewards the
   story you told yourself.
2. **One sentence of justification per score.** A score without a reason is a
   guess.
3. **Apply the gates.** Honesty or operability at 0–1 caps the result at "not yet
   a pass", whatever the total.
4. **Name the weakest criterion.** That is the next study target, and it goes at
   the top of your notes.
5. **Wait a day and re-read with the artefact closed.** If you cannot recall the
   evidence, it is not strong enough.

---

## 8. Resubmission and integrity

- The capstone has **one** submission in a taught course, because handover is the
  point and a second attempt changes the conditions. In self-study, you may
  iterate freely, but keep the first marked version so you can see what changed.
- Cite external code, data, and text, including generated text you have
  substantially used. You must be able to explain and modify every artefact.
- Never report a result you did not produce. If a metric came from an earlier run,
  say so and say when.
- If a component could not be executed in your environment (Docker, a cluster, a
  cloud service), label it **untested**, give the procedure, and take the honesty
  band that reflects the gap. That is a legitimate outcome; claiming it works is
  not.

---

## 9. What a strong submission looks like

It is usually smaller than students expect. One model, one service, one gate, one
alert, one runbook, and evidence for each. The distinguishing features are:

- the failing runs are kept, and the postmortem is about the system rather than
  about the author;
- the README says what the system does not do before it says what it does;
- every number has a command behind it;
- the runbook was tested on a person, and the awkward questions are written down;
- the defence admits one thing that does not work.

None of those require more technology. All of them require decisions made before
the deadline.
