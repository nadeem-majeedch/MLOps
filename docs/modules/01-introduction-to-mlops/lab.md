# Guided lab · The ETA drift postmortem

**Estimated time:** 3 hours, in five parts. **Tools:** a text editor and Git. No software installation, no accounts, no data downloads.

## Scenario and business problem

You have joined RaviRide as its first MLOps engineer. The ETA model has been in production for a year. Over three weeks the median estimate for central pickups rose from about 6 minutes to about 14, and rider complaints followed. Nobody noticed until the complaints arrived.

You are given a timeline of what changed. Your job is to produce the artefact the company should already have had: a postmortem that classifies the failure, names the missing controls, and recommends fixes in priority order.

> **The timeline is a teaching scenario, not a logged incident.** It is constructed so that each event illustrates a different lifecycle stage. Do not treat its dates or numbers as measurements.

### Skills practised

- Reading a chronology and separating trigger from contributing factors.
- Mapping events to lifecycle stages and to the controls that belong there.
- Drawing a lifecycle diagram whose arrows carry artefacts.
- Writing a postmortem a manager can act on.

### Prerequisites

Module 01 [Concepts](concepts.md), especially sections 2, 3, and 6. No prior MLOps experience.

### Input: the scenario packet

| # | Date | What happened | Where it lives in the system |
|---|---|---|---|
| 1 | 14 Sep | Monsoon season starts; average trip duration rises 18% for rain days | Upstream weather, no code change |
| 2 | 16 Sep | City boundary change: zone Z08 is split, and Z09 is introduced in the trip feed | `dim_zone` upstream table |
| 3 | 18 Sep | Model retrained on the last 30 days of trips, including rainy days | `train.py`, run on an analyst's laptop |
| 4 | 18 Sep | scikit-learn upgraded 1.4 → 1.5 in that laptop's environment | `requirements.txt`, unpinned |
| 5 | 21 Sep | Training image rebuilt for a separate project and redeployed to serving | Container registry |
| 6 | 23 Sep | Median ETA in central zones rises from 6 to 9 minutes | Serving logs |
| 7 | 27 Sep | Complaints and cancellations rise; support escalates | Support queue |
| 8 | 2 Oct | Investigation finds training used a random split, so rainy September trips appeared in both train and test; validation never ran on the new feed | `train.py`, `validate.py` (does not exist) |

You also know these facts, which are the sort of thing an investigation turns up:

- The retrained model scored *better* on its test set than the previous model.
- Serving and training used different library versions after 21 Sep.
- No alert existed for ETA distribution; the dashboard showed request latency only.
- Z09 rows were dropped by the serving code's zone lookup, which fails silently.

### Directory layout

Work inside your course repository:

```text
raviride-eta/
├── docs/
│   └── postmortems/
│       ├── 2026-10-eta-drift.md      # your postmortem
│       └── eta-lifecycle.mmd         # your diagram source
└── glossary.md                       # your five new terms
```

## Part 1 · Timeline and stages (40 minutes)

1. Copy the packet into a Markdown table in `docs/postmortems/2026-10-eta-drift.md` under a heading `## Timeline`.
2. Add two columns: `Lifecycle stage` and `Artefact`.
3. Fill them in. Use only these stage names: framing, data, training, evaluation, deployment, monitoring, retraining.
4. **Checkpoint 1:** every row has a stage, and no row says "unknown". If a row feels ambiguous, write the two candidate stages and one sentence choosing between them. Ambiguity documented is better than ambiguity hidden.

*Recovery:* if you are stuck on a row, ask "what would have had to exist for this event to be harmless?" The stage that produces that thing is the stage.

## Part 2 · Trigger versus contributing factors (30 minutes)

5. Under `## Contributing factors`, write a table with columns `Factor`, `Role (trigger/contributing)`, `Why`.
6. Mark exactly one row as the trigger. Defend the choice in one sentence.

*Watch for:* the trigger is usually a normal business event (weather, expansion, a dependency upgrade). If your trigger is "the engineer made a mistake", you have stopped analysing too early.

## Part 3 · Missing controls (45 minutes)

7. Add a `## Missing controls` table: `Factor`, `Control that was missing`, `Preventive or detective`, `Module that teaches it`.
8. For each factor, name one control. Controls must be specific enough to become a ticket: "add validation" is not a control, "fail the pipeline when a zone in the feed is absent from `dim_zone`" is.
9. **Checkpoint 2:** at least one control is preventive and at least one is detective. If everything is preventive, you are probably describing intentions rather than systems.

## Part 4 · The diagram (30 minutes)

10. Create `docs/postmortems/eta-lifecycle.mmd` containing a Mermaid `flowchart LR`.
11. Draw the seven stages. Label every arrow with the artefact that crosses it (for example `data -->|train.csv + checksum| training`).
12. Mark the two stages where this incident's defects were introduced, and the stage where it became visible, using different node styles.
13. Preview it by running `mkdocs serve` in your repository and opening the postmortem page, or paste the source into the Mermaid Live Editor.

*Expected result:* seven nodes, six labelled forward arrows plus a retraining loop, and three highlighted nodes. If your arrows are unlabelled, the diagram is decoration rather than documentation.

## Part 5 · Write the postmortem (45 minutes)

14. Under `## Summary`, write one paragraph in the causal-chain style of the [worked example](worked-example.md): neutral trigger, then the absent controls, then the visible symptom. No names, no blame.
15. Under `## Impact`, state what was affected and for how long, using the packet. Say plainly which numbers you do **not** have.
16. Under `## What went well`, list two things. A postmortem with no positives is usually an incomplete investigation.
17. Under `## Actions`, produce a table: `Action`, `Type (prevent/detect/mitigate)`, `Owner role`, `Cost (S/M/L)`, `Would it have caught this?`.
18. Order the actions by (risk reduced ÷ cost). Put the top three in a `## Priority` list.
19. Add five glossary entries for terms that were new to you, each with a one-sentence definition and an example from this incident. Append them to `glossary.md` in your repository; they will be merged into the site glossary as you progress.

## Expected outputs

| File | What a reviewer should see |
|---|---|
| `2026-10-eta-drift.md` | Timeline with stages and artefacts; one trigger; contributing factors; controls; impact; actions; priorities |
| `eta-lifecycle.mmd` | Valid Mermaid, labelled arrows, three highlighted nodes |
| `glossary.md` | Five new entries, each tied to the incident |

## Verification

Run these checks yourself before declaring the lab done:

- [ ] Every timeline row has a stage from the allowed list.
- [ ] Exactly one factor is marked as the trigger.
- [ ] Every missing control is specific enough to be a ticket.
- [ ] At least one preventive and one detective control.
- [ ] The diagram renders without a Mermaid syntax error.
- [ ] The summary paragraph contains no personal names.
- [ ] Every action has a cost estimate and an answer to "would it have caught this?".

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Classification correctness | At least six of eight events are placed at a defensible stage, with justification |
| Causal reasoning | The summary distinguishes trigger from contributing factors, and explains the *better test score* rather than ignoring it |
| Named controls | At least five controls, each specific, typed, and mapped to a module |
| Clarity | A manager who was not involved can read the summary and the priority list and know what to approve |

The "better test score" is the trap in this lab. A random split let rainy trips appear in both train and test, so the model's measured quality improved while real-world quality fell. If your postmortem does not mention it, revisit [Module 04](../04-data-quality-versioning/concepts.md)'s leakage section after you finish.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Every event maps to "deployment" | You are classifying *where it was noticed* | Ask which stage could have prevented it; notice is usually monitoring |
| The postmortem reads like a list of fixes | No causal chain | Write the one-paragraph summary first, then derive actions from it |
| Diagram arrows are unlabelled | You drew boxes, not a data flow | Each arrow should answer "what file or record moves here?" |
| You cannot decide between two stages | The event has two effects | Split the row into two events; one row per effect |
| Mermaid will not render | Missing `flowchart LR` header or unquoted special characters | Compare against the snippet in [Concepts](concepts.md) |

## Cleanup

No services were started. Keep both files: they are portfolio artefacts. If you ran `mkdocs serve`, stop it with ++ctrl+c++.

## Optional extensions

1. **Earliest-catch analysis.** For each action, state the earliest date it would have prevented or detected the incident. Rank actions by how much earlier they act, not by cost.
2. **Detection budget.** Assume you can afford one alert only. Which metric do you alert on, what threshold, and what is the false-positive cost? Justify with the packet's numbers.
3. **Second incident.** Repeat parts 1–5 for the promo-eligibility scenario in the [worked example](worked-example.md), then compare which controls appear in both. The repeated controls are your organisation's real gaps.
