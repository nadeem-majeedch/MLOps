# 17 · Advanced MLOps capstone

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Production | 48 hours over several weeks | Modules 01–07, 09–12, 14; Modules 13, 15, 16 strengthen it | Capstone |

Every previous module taught one part of the lifecycle with the scaffolding provided. The capstone removes the scaffolding. You integrate the parts, hand the system to someone else, and then diagnose a fault you did not choose.

This is the module where the course stops being a sequence of exercises and becomes evidence that you can operate something.

## What you will be able to do

- Operate a complete lifecycle: validation, reproducible training, tracking, registration, serving, containerisation, CI, orchestration, monitoring.
- Hand the system to another person using documentation alone.
- Diagnose an injected production incident using evidence, then write a postmortem.
- Defend design trade-offs against "why not simpler?" and "what breaks at ten times the load?".
- State honestly what the system does not protect against.

## Choose a variant

| | Core capstone | Full capstone |
|---|---|---|
| **Requires** | Essential modules (01–07, 09–12, 14) | All modules, including 13, 15, 16 |
| **Orchestration** | Script plus Task Scheduler is acceptable | Prefect flow with retries and schedule |
| **Deployment** | Local process or Compose | Local cluster with probes and limits |
| **Security artefacts** | Threat model and secret scan | Plus dependency scan, fairness analysis, access sketch |
| **Effort** | About 35 hours | About 48 hours |

Both variants are assessed against the same seven artefacts. The Full variant earns its extra marks in the cross-cutting criteria, especially operability and honesty about scale.

If you are short of time, take Core and do it well. A smaller system you can operate is worth more than a larger one you cannot hand over — and that judgement is itself part of the assessment.

## Start here

1. Read the [capstone brief](../../projects/capstone.md): the seven artefacts, acceptance criteria, handover layout, incident simulation, and defence.
2. Read [Concepts](concepts.md) sections 1–5: system boundary, clean-clone reproducibility, gates, observability, and incident command.
3. Read the [worked example](worked-example.md): a reference starter's measured artefacts and a timed incident, with the evidence each claim needs.
4. Do the [lab](lab.md): build, hand over, inject a fault, diagnose it, and write the postmortem.

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives, evidence, and the capstone readiness gate |
| [Concepts](concepts.md) | Integration, reproducibility, release gates, observability, incident command, handover, defence |
| [Worked example](worked-example.md) | A reference lifecycle with measured numbers and an incident timeline |
| [Guided lab](lab.md) | The six-week build, handover, and incident simulation |
| [Independent challenge](independent-challenge.md) | Extension requirements for the Full variant |
| [Knowledge check](knowledge-check.md) | Ten scenario questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Clean-clone failures, stalled gates, incidents, handover gaps |
| [References](references.md) | MLOps, reliability, and capstone sources |

## What you produce

The handover package in the [capstone brief](../../projects/capstone.md#5-handover-package):

```text
capstone/
├── README.md              # what it is, how to run it, what it does not do
├── docs/
│   ├── architecture.md
│   ├── runbook.md
│   ├── model-card.md
│   └── postmortem.md
├── evidence/
│   ├── ci/                # green and correctly-red runs
│   ├── drift/             # reports and the alert
│   └── rollback/          # timed log
└── <the working system>
```

The `evidence/` directory is the difference between claiming a gate works and showing it. Keep the failing runs; they are the most convincing artefacts you will produce.

## The standard

A capstone passes when someone else can check these in under ten minutes each:

- a clean clone reaches the reported metric, following only the README;
- CI fails for the correct reason on three injected regressions: schema, unit, and metric;
- rollback is demonstrated in under five minutes;
- five malformed requests return 422 with specific messages;
- the alert fires on the injected drift batch and names an owner and a first step;
- a peer deploys from the runbook in under 30 minutes;
- the secret scan has no unaddressed findings;
- the model card states two limitations and the measured disparity;
- the incident is diagnosed within 30 minutes with the evidence path recorded;
- the defence answers "why not simpler?" and "what breaks at ten times the load?".

"I understand the lifecycle" cannot be marked. "A peer deployed it in 22 minutes" can.

## The reference implementation

The advanced starter in [`examples/starters/advanced-monitoring-pipeline/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/starters/advanced-monitoring-pipeline) is the closest template to the capstone and was executed as part of the course verification. It reports 29 passing tests, ROC AUC 0.8382, recall 0.875 at a threshold chosen for 80% training recall, a promotion gate, a champion alias, a rollback, and a drift monitor that exits 2 on the supplied shifted batch.

It is a template, not a submitted capstone. It does not include authentication, a real registry service, concurrency, or the handover package. Those are your work.

## Next

The capstone is the end of the guided course, not the end of the subject. The [portfolio narrative](../../projects/capstone.md#10-portfolio-narrative) and the [revision guide](../../assessments/revision-guide.md) are the bridge to interviews and to operating a real system.
