# Mini-projects

Five project specifications, each at a natural integration boundary. They use the
same `raviride-eta` repository as the labs, so nothing is rebuilt from scratch:
each one adds a layer and makes the previous layer prove itself.

| # | Mini-project | After | Effort | Illustrative weight | Core? |
|---|---|---|---|---|---|
| [MP1](mp-01-reproducible-training-package.md) | Reproducible training package | Module 05 | 8 h | 10% | Yes |
| [MP2](mp-02-evaluated-registered-model.md) | Evaluated and registered model | Module 09 | 8 h | 10% | Yes |
| [MP3](mp-03-served-containerised-gated-service.md) | Served, containerised, gated service | Module 12 | 12 h | 10% | Yes |
| [MP4](mp-04-monitored-lifecycle.md) | Monitored lifecycle with retraining | Module 14 | 12 h | 10% | Yes |
| [MP5](mp-05-operate-and-hand-over.md) | Operate and hand over | Modules 13–16 | 14 h | optional | Extension |

!!! warning "Weights are illustrative"
    The percentages describe a suggested self-study structure, not an official
    university grading scheme. No institution has approved them. An instructor
    adopting the course should set weights against local regulations; the
    [assessment framework](../../syllabus/assessment-framework.md) explains the
    reasoning. MP5 is an optional extension and is not part of the default total.

Why five when the course describes four? MP1–MP4 reach every core outcome. MP5
exists for students who take Modules 13, 15, and 16 and want the operational half
of the job — handover, incident response, and scale reasoning — assessed rather
than only read. It is the closest rehearsal for the capstone.

---

## The progression

| Stage | The system can... | The new failure it exposes |
|---|---|---|
| MP1 | rebuild its data and model from a clean clone | a result that only exists on your machine |
| MP2 | say which model is champion, and why | a plausible model that is worse on a slice |
| MP3 | answer a validated request from a container, gated by CI | a contract that drifts, a gate that checks nothing |
| MP4 | notice its inputs moved and propose a retrain | an alert nobody can act on, a retrain that helps nothing |
| MP5 | be operated by someone else under time pressure | a runbook that was never tested |

Each stage assumes the previous one exists. Skipping MP1 makes MP2 unverifiable;
skipping MP3 makes MP4's alerts impossible to interpret.

---

## How each specification is written

| Section | What it gives you |
|---|---|
| Header | Prerequisite modules, effort, weight, what it integrates |
| Brief | The workplace situation, in a few sentences |
| Deliverables | Numbered artefacts with required names |
| Acceptance criteria | Observable facts a stranger can check |
| Evidence | What to keep, and what weak evidence looks like |
| Rubric | Four criteria, four bands, with the behaviour that earns each |
| Build order | A sequence that survives interruption |
| Common failures | The ones that actually happen, and their signature |

The rubric bands are the same scale used across the course: 0 absent, 1 present
but not achieving the behaviour, 2 achieves it with one significant gap, 3
achieves it and survives a stated perturbation.

---

## Working rules

- **One repository.** New folders are not new projects. `src/raviride_eta/`,
  `dvc.yaml`, `Dockerfile`, and `.github/workflows/ci.yml` stay where they are.
- **Evidence over narrative.** A claim without a log, a metric, or a run ID is
  not evidence.
- **State the tolerance before the run.** A metric that matches "closely enough"
  after the fact is not reproduced.
- **Keep the failing runs.** They are the most convincing artefacts you will
  produce, and the ones students delete first.

Reference solutions are kept separate, under
[reference solutions](../../assessments/solutions/mini-projects.md). Read them
after a first attempt, not before.

---

## Choosing an order if you are short of time

Do MP1 and MP3. They cover reproducibility and delivery, the two failures that
end projects. MP2's registry discipline can be learned from the module lab; MP4's
monitoring can be read and practised in [Lab 17](../../labs/lab-17-drift-analysis.md).
MP5 should not be attempted before MP3 is complete.

The [capstone](../capstone.md) requires all four core mini-projects' outcomes in
one system, so the shortest honest route to it is MP1 → MP2 → MP3 → MP4, with the
labs filling the gaps.
