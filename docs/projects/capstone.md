# Capstone Brief

**Module 17 · Production · 48 hours over several weeks · Free and local**

The capstone is where the course stops giving you scaffolding. You integrate the lifecycle on the `raviride-eta` system you have been extending since Module 02, hand it to someone else, and then diagnose a fault you did not choose.

There is no new tool. If you find yourself installing something in this module, the scope has slipped.

---

## 1. Choose a variant

| | Core capstone | Full capstone |
|---|---|---|
| **Requires** | Essential modules (01-07, 09-12, 14) | All modules, including 13, 15, 16 |
| **Orchestration** | Script plus Task Scheduler is acceptable | Prefect flow with retries and schedule |
| **Deployment** | Local process or Compose | Local cluster with probes and limits |
| **Security artefacts** | Threat model and secret scan | Plus dependency scan, fairness analysis, access sketch |
| **Effort** | About 35 hours | About 48 hours |

Both variants are assessed against the same seven artefacts. The Full variant earns its extra marks in the cross-cutting criteria, especially operability and honesty about scale.

!!! tip "Choosing"
    If you are short of time, take Core and do it well. A smaller system you can operate is worth
    more than a larger one you cannot hand over - and that judgement is itself part of the assessment.

---

## 2. What you build

A prediction service for RaviRide's arrival-time estimate that:

- validates its input data and rejects bad batches;
- trains reproducibly from a versioned dataset;
- tracks experiments and registers versions with lineage;
- serves predictions with a validated contract;
- runs in a container, gated by CI;
- detects when its predictions are degrading;
- documents its own limitations.

You do not need new data. You need the system you already built to work together, from a clean clone, without you in the room.

---

## 3. Required artefacts

| # | Artefact | Marks |
|---|---|---|
| 1 | Rerunnable pipeline from a clean clone | 8 |
| 2 | Versioned data and model with provenance | 6 |
| 3 | Automated tests and a CI gate that genuinely fails | 8 |
| 4 | Served endpoint with validation | 6 |
| 5 | Monitoring with an actionable alert | 6 |
| 6 | Runbook covering deploy, rollback, and the top three alerts | 4 |
| 7 | Model card and defence document | 2 |
| | **Total** | **40** |

---

## 4. Acceptance criteria

A capstone passes when all of these are true. Each is checkable by someone else in under ten minutes.

- [ ] A clean clone reaches the reported metric within the stated tolerance, following only the `README`.
- [ ] CI fails for the correct stated reason on three injected regressions: schema, unit, and metric.
- [ ] Rollback from the current champion to the previous version is demonstrated and takes under five minutes.
- [ ] At least five malformed prediction requests return 422 with specific messages.
- [ ] The alert fires on the injected drift batch and includes an owner and a first diagnostic step.
- [ ] A peer who has not seen the project deploys it from the runbook in under 30 minutes.
- [ ] `gitleaks` (or equivalent) reports no unaddressed findings.
- [ ] The model card states at least two limitations and the measured disparity between central and peripheral zones.
- [ ] The incident simulation is diagnosed within 30 minutes, with the evidence path recorded.
- [ ] The defence answers "why not simpler?" and "what breaks at ten times the load?" with specifics.

These are deliberately written as observable facts. "I understand the lifecycle" cannot be marked; "a peer deployed it in 22 minutes" can.

---

## 5. Handover package

```text
capstone/
├── README.md              # what it is, how to run it, what it does not do
├── docs/
│   ├── architecture.md    # diagram plus the two decisions that shaped it
│   ├── runbook.md         # deploy, rollback, top three alerts
│   ├── model-card.md      # intended use, limitations, disparity, monitoring
│   └── postmortem.md      # injected incident: timeline, cause, controls
├── evidence/
│   ├── ci/                # green and correctly-red run logs
│   ├── drift/             # reports and the alert that fired
│   └── rollback/          # timed log
└── <the working system>
```

The `evidence/` directory is the difference between claiming a gate works and showing it. Keep the failing runs; they are the most convincing artefacts you will produce.

---

## 6. The incident simulation

At the end of the capstone, a fault is injected without warning: a stale model alias, a corrupted feature, a missing dependency, or a failed rollback. You must:

1. **Detect** it from your own monitoring or a reported symptom.
2. **State a hypothesis** and your first diagnostic step *before* touching anything.
3. **Gather evidence** that confirms or rejects the hypothesis.
4. **Restore service**, using the runbook where possible.
5. **Write a postmortem**: timeline, cause, why detection took as long as it did, and one control to add.

If you are studying alone, use the supplied fault-injection script and a timer. The clock is the point: with unlimited time, everything is diagnosable, and the skill you need is diagnosis under pressure.

---

## 7. Defence

A 15-minute written or oral defence:

| Time | Question |
|---|---|
| 2 min | What does the system do, and what does it not do? |
| 5 min | Which decision would you make differently now, and what evidence changed your mind? |
| 5 min | Why not simpler? What breaks at ten times the load? |
| 3 min | What is the top residual risk, and what would you monitor for it? |

The defence is not a presentation of effort. It is a test of whether you can explain and defend the system without the code in front of you.

---

## 8. Timeline

| Week | Work |
|---|---|
| 1 | Scoping: system boundary, out-of-scope list, artefact inventory |
| 2 | Pipeline, data versioning, and provenance to the clean-clone standard |
| 3 | Tests, CI gate, serving, container |
| 4 | Monitoring, alert, retraining guardrail |
| 5 | Runbook, model card, peer handover, incident simulation |
| 6 | Postmortem, defence document, portfolio narrative |

Add a week if your deployment includes Module 16. Do not compress the handover or the incident; they are the parts that cannot be faked.

---

## 9. Assessment

The rubric, cross-cutting criteria, and self-marking protocol are in the [assessment framework](../syllabus/assessment-framework.md#5-component-4-capstone-40). The design rationale and the artefact ladder are in the [project map](../syllabus/course-project-map.md#5-capstone-requirements-what-is-assessed).

A capstone that scores well on artefacts but 0-1 on **honesty** or **operability** is not a pass, regardless of total. Those two criteria describe whether the system can be trusted in someone else's hands.

---

## 10. Portfolio narrative

Finish with 400-600 words:

1. What does the system do, and for whom?
2. What would have gone wrong if you had skipped Modules 04, 07, and 14?
3. Which decision are you least confident about, and what evidence would change your mind?
4. What would you do first if this had real users next week?

This is the document you would attach to an application, and the one worth rereading before an interview.
