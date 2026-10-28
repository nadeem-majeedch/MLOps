# Independent challenge · Analyse an incident you did not cause

**Time:** 2–3 hours. **Deliverable:** a one-page analysis in `docs/postmortems/external-incident.md`.

The guided lab gave you a packet with the facts already collected. Real analysis starts with a messy account written for a different purpose, usually by a company explaining itself to its users.

## The task

1. Choose **one** published incident write-up that involves a deployed model or an automated decision system. Good places to look:
   - the postmortem collection in the *Site Reliability Engineering* book's [postmortem culture chapter](https://sre.google/sre-book/postmortem-culture/), which explains what a useful one contains;
   - engineering blogs of companies that publish incident reviews (search for "postmortem" on their blog index);
   - a regulator's or auditor's report on an automated decision system, if you prefer a non-corporate source.
2. Write a one-page analysis with these sections, in this order:
   - **What the system did**, in two sentences, for a reader who has never heard of the company.
   - **The timeline**, at most eight rows, each with a date and an artefact if the source names one.
   - **Classification table**: event, lifecycle stage, and one sentence of justification.
   - **Three absent controls**, each with the type (preventive or detective) and the module of this course that teaches it.
   - **What the source does not tell you**, at least three items. This section is marked.
3. Add a final paragraph answering: *would the controls you named have prevented the incident, or only detected it sooner?* Be specific about which.

## What "good" looks like

| Criterion | Weak | Strong |
|---|---|---|
| Sourcing | A news article summarising the event | A technical account that names components, versions, or data |
| Classification | Every event labelled "model" | Stages distinguished, with justification |
| Controls | "Better testing" | A named check at a named seam, with the failure it would produce |
| Gaps | "Not enough information" | Specific missing facts and why each would change the conclusion |

## Rules

- Do not invent dates, metrics, or quotes. If the source does not say, write "not stated".
- If the source is about a non-ML system (a database outage, say), you may still use it, but add a paragraph on what changes when the deployed artefact is a model rather than code.
- Keep it to one page. The discipline is in the selection, not the volume.

## Self-check before you submit

- [ ] A reader who knows nothing about the company can follow the timeline.
- [ ] At least one event is placed at a stage *before* deployment.
- [ ] At least one control is preventive.
- [ ] The "what the source does not tell you" section has three concrete items.
- [ ] No sentence assigns blame to an individual.

## Extension

Compare your three controls with the five you proposed in the guided lab. Any control that appears in both is a gap your own project is likely to have. Add it to your project's debt register now, while you remember why.
