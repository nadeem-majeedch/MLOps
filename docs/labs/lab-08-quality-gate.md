# Lab 08 · Reject a model that fails the quality policy

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L08 | Intermediate | 3 hours | [07 · Testing ML systems](../modules/07-testing-ml-systems/index.md), [09 · Model registry](../modules/09-model-registry/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-08-quality-gate/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-08-quality-gate) — starter files, data generator, and acceptance checker.

## Scenario

Six candidate models are waiting. One is better overall and safe. One is
underfitted. One was trained without a production zone. One improves the average
while making a small zone much worse. One has no evaluation for the zone with the
highest error.

The promotion decision is currently made in a meeting, from a table, by whoever
is most confident. You will replace the meeting with a policy file and a script
that returns an exit code.

## What you will be able to do

- Encode a quality policy as data, separate from the gate that applies it.
- Compare a candidate with a champion rather than with an abstract threshold.
- Block a candidate whose average improved but whose slice degraded.
- Make a gate's refusal specific enough to act on.

## Prerequisites and setup

```bash
cd examples/labs/lab-08-quality-gate
python gate.py --candidate candidates/deeper_v2.json --champion candidates/baseline_v1.json
```

Expected on the starter: `PASS deeper_v2`. Run the shallow candidate next and
notice that it is also accepted, which is the defect.

## Your task

Implement the four missing rules in `gate.py` so that five of six candidates are
blocked for five different reasons. `check_lab08.py` runs every candidate.

## Data and starter files

| File | Purpose |
|---|---|
| `policy.yaml` | Ceilings, tolerances and required slices |
| `candidates/*.json` | Champion plus five candidates with real metric layouts |
| `gate.py` | Implements absolute ceiling and overall regression only |
| `check_lab08.py` | Runs six candidates and checks the reason codes |

Candidate summary:

| Candidate | MAE | Notable property |
|---|---|---|
| `baseline_v1` | 2.7686 | The champion |
| `deeper_v2` | 2.7557 | Better everywhere within tolerance |
| `shallow_v3` | 3.4416 | Underfitted |
| `no_z08_v5` | 2.7574 | Trained without zone Z08 |
| `zone_regression_v6` | 2.7401 | Best average; Z01 up 16% |
| `missing_slice_v7` | 2.7503 | No Z07 in the report |

## Steps

### 1. Read the policy

Open `policy.yaml`. Every number is a decision someone made: absolute ceiling,
relative tolerance against the champion, p95 ceiling, per-zone tolerances,
required slices, and a rule forbidding a model that never saw a production zone.

### 2. Implement the p95 rule

The tail matters more than the mean for an ETA: a model that is usually right and
occasionally 20 minutes wrong is worse than one that is consistently 4 minutes
off. Fail when `p95_abs_error` exceeds its ceiling.

### 3. Implement per-zone limits

For each zone with a tolerance, compare against the champion's zone MAE and fail
when the candidate is worse by more than the tolerance. Report the zone, both
values and the allowance.

### 4. Implement the dropped-zone rule

A candidate that lists `dropped_zones` never saw those rows. Its Z08 MAE is
computed on a distribution it was not trained for, and the number is not
evidence. Fail before reading the number.

### 5. Implement the missing-slice rule

An absent evaluation is not a pass. Every zone in `required_slices` must appear
in the candidate's report.

### 6. Run the checker

```bash
python check_lab08.py
```

Expected: `21/21 checks passed`.

## Expected output

```text
  [PASS] deeper_v2 decision -- got 'pass', expected 'pass'
  [PASS] shallow_v3 names absolute_ceiling -- reasons: ['absolute_ceiling', 'overall_regression', 'zone_limit']
  [PASS] no_z08_v5 names dropped_zone -- reasons: ['dropped_zone']
  [PASS] zone_regression_v6 names zone_limit -- reasons: ['zone_limit']
  [PASS] zone_regression_v6 ... Z01 mae 2.190 vs champion 1.890 by more than 5% (allowed 1.984)
  [PASS] missing_slice_v7 names missing_slice -- reasons: ['missing_slice']
  [PASS] zone_regression improves overall MAE but is still blocked
```

## Acceptance criteria

| # | Candidate | Decision | Rules that must appear |
|---|---|---|---|
| 1 | `deeper_v2` | pass | none |
| 2 | `shallow_v3` | block | `absolute_ceiling`, `overall_regression` |
| 3 | `no_z08_v5` | block | `dropped_zone` |
| 4 | `zone_regression_v6` | block | `zone_limit` |
| 5 | `missing_slice_v7` | block | `missing_slice` |
| 6 | Every block | — | A reason containing a number |
| 7 | Exit codes | — | 0 for pass, 1 for block |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `deeper_v2` blocked | Comparing zone MAE without the tolerance multiplier | Allow `champion * (1 + limit)` |
| `no_z08_v5` passes | Rule reads the zone metric instead of the metadata | Read `dropped_zones` |
| `zone_regression_v6` passes | Only overall MAE checked | Add the per-zone loop |
| `missing_slice_v7` passes | `dict.get` returns 0 for absent zones | Check membership, not the value |
| All candidates blocked | Policy path resolved from the wrong directory | Run from the lab directory or pass `--policy` |

## Reflection questions

1. Why compare with the champion as well as with an absolute ceiling? Give a case
   where each rule alone gives the wrong answer.
2. `zone_regression_v6` has the best MAE of all candidates. What argument would you
   make to its author?
3. Which rule in this policy would you expect to change most often, and why
   should it live in a file rather than in code?
4. What is missing from this gate that a human reviewer would still catch?

## Optional extension

Add a rule that blocks a candidate whose training data hash differs from the
champion's without an accompanying data-change note, and explain in your notes
why "different data" is not automatically a defect.

## Cleanup

```bash
rm -rf artifacts
```

PowerShell: `Remove-Item artifacts -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] I read the policy before writing code
- [ ] Five candidates are blocked for five distinct reasons
- [ ] The passing candidate still passes
- [ ] Every refusal contains a number I can act on
- [ ] `check_lab08.py` reports `ACCEPTED`
