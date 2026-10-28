# Lab 20 · Run the operational incident review

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L20 | Integration | 4 hours | [17 · Capstone](../modules/17-capstone/index.md); Labs 08–19 | Yes |

**Starter kit:** [`examples/labs/lab-20-incident/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-20-incident) — starter files, data generator, and acceptance checker.

## Scenario

At 02:00 on 18 October, release v5 replaced v4 outside the normal gate. It
expected a feature the service does not send. Every prediction raised
`KeyError: 'traffic_index'` and returned 500. The first page fired at 02:12; the
service was restored at 04:20.

Nobody needs an explanation of what happened to the model. They need an incident
record that agrees with the evidence, and a set of changes that would make the
next occurrence shorter. You are the reviewer, not the on-call engineer.

## What you will be able to do

- Reconstruct an incident timeline from logs, alerts and deployment records.
- Compute impact from metrics instead of estimating it.
- Separate the root cause from the conditions that made it reach production.
- Write a blameless postmortem with verifiable prevention items.

## Prerequisites and setup

```bash
cd examples/labs/lab-20-incident
python incident.py
cat incident/alerts.json
cat incident/deploys.json
head -20 incident/app.log
```

PowerShell:

```powershell
Get-Content incident/alerts.json
Get-Content incident/deploys.json
Get-Content incident/app.log -TotalCount 20
```

Expected: 660 failed requests, first alert 02:12, rollback 04:20, error rate back
to baseline at 04:24.

## Your task

Complete `incident.json` and `postmortem.md` so that every claim matches the
evidence pack. `check_lab20.py` recomputes the impact figure and the MTTR.

## Data and starter files

| File | Purpose |
|---|---|
| `incident.py` | Generates the evidence pack (deterministic) |
| `incident/metrics_hourly.csv` | Requests, errors, p95 latency, delayed MAE |
| `incident/alerts.json` | Four alerts, two of them resolved |
| `incident/deploys.json` | Version windows, release type, gate status |
| `incident/app.log` | Service log from 01:58 to 04:24 |
| `incident/tickets.json` | Three user reports |
| `incident.json` | Your record |
| `postmortem.md` | Your blameless write-up |

## Steps

### 1. Build the timeline from evidence, not memory

Start with the earliest signal, not the first page:

- 01:58:42 — v5 starts and logs a schema warning.
- 02:00:04 — first 500.
- 02:12:00 — latency alert pages.
- 02:18:00 — 5xx alert fires.
- 02:22:51 — acknowledgement, eleven minutes after the page.
- 02:58:30 — mismatch hypothesised.
- 03:20:44 — rollback blocked on approval.
- 03:52:10 — approval granted.
- 04:20:00 — alias moved to v4.
- 04:24:00 — alert resolved.

A timeline that starts at 02:12 hides the 14 minutes between cause and page, and
the 21 minutes between the 5xx alert and acknowledgement. Those are the
actionable gaps.

### 2. Compute impact

Sum the `errors` column for the incident window: 240 + 300 + 120 = 660. Do not
count the hours after recovery. State the window as 02:00–04:20, not "most of the
morning".

### 3. Name the root cause and the conditions

Root cause: the artefact required `traffic_index`; the request schema did not
provide it; nothing compared the two before traffic arrived.

Contributing conditions — at least three:

1. The gate was overridden for the hotfix, so the contract test never ran.
2. The rollout went to 100% with no canary.
3. Rollback required a release-owner approval with no out-of-hours route, which
   accounts for 87 of the 128 minutes.

"The engineer was careless" is not a contributing factor and not welcome here.

### 4. Write the immediate action and its verification

Rollback to v4, verified by the 5xx rate returning to 0.001 and p95 to 190ms.
Verification is part of the action; "rolled back" without a signal is a claim.

### 5. Write prevention items you could check

Each item needs an owner role and a way to prove it works: a contract test in the
gate, a 5% canary with automatic rollback, pre-approved out-of-hours rollback with
a monthly drill, and alerting on the startup schema warning.

### 6. Write the postmortem

Eight sections: Summary, Impact, Timeline, Root cause, Detection, Response,
Prevention, Lessons. Blameless language, no individual named as the cause, at
least eight timestamps in the Timeline.

### 7. Run the checker

```bash
python check_lab20.py
```

Expected: `34/34 checks passed`.

## Expected output

```text
  [PASS] detection time is the first page -- got '2026-10-18T02:12'
  [PASS] mitigation time is the alias change -- got '2026-10-18T04:20'
  [PASS] the reported mttr matches its own timestamps -- got 128, expected 128
  [PASS] failed requests match the metrics -- got 660, expected 660
  [PASS] the gate override is a contributing factor -- ...
  [PASS] the timeline has at least eight entries -- 10 entries
  [PASS] the postmortem is explicitly blameless -- stated
  [PASS] the written timeline carries at least eight timestamps -- 10 timestamps
```

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Severity stated | SEV1–SEV3 or equivalent |
| 2 | Detection time | `2026-10-18T02:12` |
| 3 | Mitigation time | `2026-10-18T04:20` |
| 4 | MTTR consistent with timestamps | 128 minutes |
| 5 | Failed requests | 660 |
| 6 | Root cause names the missing feature | `traffic_index` or schema/feature |
| 7 | Three contributing factors | ≥ 3, including the gate override |
| 8 | Rollback to v4, verified | Present with a signal |
| 9 | Timeline | ≥ 8 entries, ordered |
| 10 | Prevention | ≥ 3 verifiable items |
| 11 | Postmortem sections | All eight filled |
| 12 | Blameless language | No individual blamed |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Failed requests 1,200 | Counting requests instead of errors | Sum the `errors` column |
| MTTR 132 | Using 04:24 (alert resolved) as mitigation | Mitigation is the alias change at 04:20 |
| Checker rejects a contributing factor | Too short or missing the override | Name the gate and the approval delay |
| Timeline out of order | Entries appended by thought, not time | Sort by `at` |
| Postmortem flagged for blaming | "The engineer should have…" | Rewrite as a system condition |

## Reflection questions

1. Rollback took 87 minutes because of an approval. Is that a process failure or
   a control working as designed? Defend one position.
2. The 5xx alert fired six minutes after the latency alert. Which one would you
   keep if you could only keep one?
3. What would a canary at 5% have changed about the impact figure, and what would
   it not have changed?
4. Which prevention item would you fund first if only one were approved?

## Optional extension

Write the follow-up: a 30-minute tabletop exercise for this incident, with three
inject messages and the expected action at each. Then explain how you would score
whether the team passed, without scoring the individual on call.

## Cleanup

```bash
rm -rf incident artifacts
```

PowerShell: `Remove-Item incident, artifacts -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] My timeline starts before the first page and ends after recovery is verified
- [ ] Impact is computed from metrics, not estimated
- [ ] The root cause and the contributing conditions are separate
- [ ] Prevention items are verifiable
- [ ] The postmortem is blameless and complete
- [ ] `check_lab20.py` reports `ACCEPTED`
