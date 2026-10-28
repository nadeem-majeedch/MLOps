# Worked example · A promo-eligibility incident, analysed

> **Teaching scenario.** RaviRide is fictional and the timeline below was written for this course. No real users, metrics, or companies are involved. The reasoning method is the same one you apply to a real incident in the lab.

## The situation

RaviRide's growth team uses a small model that scores riders for a discount campaign. The model outputs a probability; riders above a threshold receive a promo code by SMS. The campaign ran in Lahore and Karachi only.

On 3 May the service expanded to Hyderabad. On 4 May, 1,900 riders in Hyderabad received discount codes for a campaign that had no budget there. Support handled the complaints; the campaign was paused. Nobody was hurt, and the total cost was small. The interesting question is not "who typed the city list" but "which controls were absent".

## Step 1: Build the timeline, with artefacts

A timeline without artefacts is a story. Each row should say what changed and what file, table, or setting carried the change.

| # | Date | Event | Artefact affected |
|---|---|---|---|
| 1 | 2 May | Hyderabad added to the service-area table | `dim_city` table, new row |
| 2 | 3 May | Campaign job runs, scores all riders with a completed trip in 30 days | `promo_scores.csv` |
| 3 | 3 May | Job filters to Lahore and Karachi using a list inside the job script | `run_campaign.py`, lines 44–51 |
| 4 | 4 May | 1,900 Hyderabad riders receive codes | SMS provider log |
| 5 | 4 May | Support tickets spike; campaign paused by a marketing manager | Ticket queue |
| 6 | 6 May | Engineering finds the hard-coded list | Code review |
| 7 | 12 May | Postmortem written; list moved to configuration | Pull request |

## Step 2: Separate trigger from contributing factors

The **trigger** is the event that started the failure. The **contributing factors** are the conditions that turned a small trigger into a customer-visible defect. An analysis that stops at the trigger produces a fix that does not hold.

| Role | Item | Why it is classified this way |
|---|---|---|
| Trigger | Event 1: a new city appeared in an upstream table | Normal business change; it should be safe by construction |
| Contributing | Event 3: the campaign filter was code, not configuration | A list that changes with the business lived in a file that requires a developer |
| Contributing | No validation compared campaign scope with known cities | Nothing checked that the filter matched the service area |
| Contributing | No pre-send check on recipient count or city distribution | A 1,900-recipient jump in a new city was visible but unlooked-for |
| Contributing | The campaign job had no owner outside marketing | Nobody who saw the anomaly had the authority to stop it |

## Step 3: Place each factor at a lifecycle stage

| Factor | Stage that could have caught it | Control that was missing | Taught in |
|---|---|---|---|
| New city in the table | Data | Schema/domain validation on the city list used by the model | [Module 04](../04-data-quality-versioning/index.md) |
| Hard-coded city list | Framing / configuration | Configuration layer, reviewed like code | [Module 03](../03-project-organization/index.md) |
| Filter not derived from service area | Framing | Output contract: the job declares which cities it may target | Module 03, revisited in [09](../09-model-registry/index.md) |
| No recipient sanity check | Evaluation | Pre-send validation of expected volume and distribution | Module 04 |
| Silent send | Deployment | Release gate: a human approves the first send to a new city | [Module 12](../12-ci-cd/index.md) |
| Nobody monitored the campaign | Monitoring | Alert on unexpected segment of recipients | [Module 14](../14-monitoring-drift/index.md) |

The classification is not unique, and that is normal. What matters is that each factor gets *a* stage whose owner could plausibly have stopped it, plus a named control. "Human error" is not a stage.

## Step 4: Write the causal chain in one paragraph

> A routine service-area expansion added Hyderabad to the city table. The campaign job, written months earlier, filtered recipients using a hard-coded list of two cities inside the script. Because the list was code rather than configuration, the expansion required a code change that nobody made. No validation compared the job's target list with the current service area, and no pre-send check looked at the city distribution of the 1,900 recipients. The codes were sent, and the defect became visible only through support tickets.

Note the shape: a neutral trigger, then a chain of absent controls. This paragraph can be reviewed, argued with, and turned into tickets. "The marketer made a mistake" cannot.

## Step 5: Derive the fixes, and rank them

| Fix | Type | Cost | Would it have caught this? |
|---|---|---|---|
| Move the city list into configuration, validated against `dim_city` | Preventive | Small | Yes, at run time |
| Fail the job if a target city has no active campaign budget | Preventive | Small | Yes, before send |
| Require approval for any send whose recipient count differs from the previous run by more than 20% | Detective | Medium | Yes, before send |
| Alert on recipients per city after send | Detective | Small | It would have detected it *after* the send; useful as a second layer |
| Add the campaign job to the on-call rotation | Organisational | Ongoing | Maybe; depends on whether anyone acts |

Two habits worth carrying forward:

- **Prefer preventive controls at the seam where the change enters.** Validation of the city list beats an alert after 1,900 messages.
- **Two layers beat one.** Prevention fails eventually; detection limits the damage when it does.

## What this example does not show

It does not show a monitoring dashboard catching the problem, because none existed. It does not claim the model was wrong: the model scored riders exactly as designed. The defect was entirely in the surrounding system, which is the ordinary case. Most ML incidents are not modelling failures.
