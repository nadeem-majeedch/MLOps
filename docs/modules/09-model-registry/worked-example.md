# Worked example · Six candidates, two refusals, one rollback

The registry is MLflow's local file store at `mlruns/`, with the model name `raviride-eta`. Every line below is real output from the reference project; run names are shortened.

## The candidates

Six versions were trained against the same 896/304 split. The variants were chosen to make different failure modes visible, not to find the best model.

| Version | Candidate | What changed | MAE | p95 abs error | Z07 MAE (16 rows) | Z08 MAE (22 rows) |
|---|---|---|---|---|---|---|
| 1 | `baseline` | 200 trees, depth 12, leaf 3 | 2.7686 | 8.254 | 5.1749 | 5.5812 |
| 2 | `deep` | 300 trees, depth 16, leaf 1 | **2.7557** | 8.551 | 5.1792 | 5.6103 |
| 3 | `shallow` | 60 trees, depth 2, leaf 40 | 3.4416 | 9.497 | 5.8903 | 7.3065 |
| 4 | `core` | four-feature set instead of nine | **2.7275** | 8.473 | 5.5116 | 5.2873 |
| 5 | `noz08` | Z08 rows dropped from training | 2.7574 | 8.045 | 5.2205 | 5.9600 |
| 6 | `noz08b` | same as v5, re-run after the policy change | 2.7574 | 8.045 | 5.2205 | 5.9600 |

Two rows deserve attention before any gate runs. Version 4 has the **lowest MAE of all six** and the **worst Z07 error of any candidate that is not obviously broken**. Version 5 has a worse overall MAE than the champion and an 8% worse Z08 error, and it trained on **849 rows instead of 896**.

## Registering

```text
Successfully registered model 'raviride-eta'.
Created version '1' of model 'raviride-eta'.
baseline: version 1 run 6f6e36b0 MAE 2.7686
```

Each `train` call logs parameters, tags (`data_hash=285bbf8406f483a9`, `git_commit=ac4246f`), metrics including per-zone MAE, the metrics document, and the model with a signature and input example. The model is saved as a scikit-learn pipeline, so preprocessing travels with it.

## Gate 1: the first champion

There is no champion yet, so only the absolute ceiling applies:

```text
$ python registry/registry.py promote 1
champion -> v1 (was vNone)
```

Versions 1 and 2 both clear the ceiling of 3.20; the alias exists so that future candidates have something to be compared against.

## Gate 2: an obviously bad candidate

```text
$ python registry/registry.py gate 3
FAIL
  - overall_mae 3.442 exceeds ceiling 3.2
  - overall_mae 3.442 exceeds champion v1 by more than 3% (allowed 2.8517)
  - zone Z01 mae 2.545 exceeds champion 1.890 by more than 5% (allowed 1.9843)
  - zone Z05 mae 3.889 exceeds champion 3.113 by more than 5% (allowed 3.2685)
  - zone Z07 mae 5.890 exceeds champion 5.175 by more than 5% (allowed 5.4336)
  - zone Z08 mae 7.306 exceeds champion 5.581 by more than 8% (allowed 6.0277)
```

Six reasons, each naming a value and a limit. This is what a gate should look like when it fails: a reader can reproduce the comparison without opening the code. Note that it does not stop at the first failure — a candidate that is bad everywhere should be reported as bad everywhere, because the pattern is diagnostic.

## Gate 3: the better candidate wins

```text
$ python registry/registry.py gate 2
PASS
$ python registry/registry.py promote 2
champion -> v2 (was v1)
```

Version 2 improves MAE by 0.5% and every zone stays inside tolerance. Its p95 absolute error is *worse* (8.551 vs 8.254, +3.6%). The policy does not gate p95, which is a decision someone should defend: for an ETA product, the tail matters for the worst journeys, and a 3.6% tail regression may be worth a 0.5% average gain — or not. The point is that the policy states what is tolerated; the reviewer can disagree and change it.

## Gate 4: the best aggregate is refused

```text
$ python registry/registry.py gate 4
FAIL
  - zone Z07 mae 5.512 exceeds champion 5.179 by more than 5% (allowed 5.4382)
```

One reason. Version 4 is 1% better overall than the champion and 6.4% worse for pickups in Z07, the second-sparsest zone with 16 test rows. Two defensible responses:

- **Refuse**, because 16 rows is enough to see a consistent direction and Z07 users are a real population.
- **Widen the Z07 tolerance**, because 16 rows cannot support 5%, and record that decision.

What is not defensible is promoting it while the policy says no, and then describing the result as "the model improved".

## Gate 5: the candidate that passes everything it is measured on

```text
$ python registry/registry.py gate 5
PASS
$ python registry/registry.py promote 5
champion -> v5 (was v2)
$ python registry/smoke_test.py
PASS champion v5: predicted 44.29 min (expected 25-50 for an 11.4 km Z08->Z01 trip at 18:20)
```

Version 5 is slightly worse overall than v2 (+0.06%, inside the 3% allowance) and 6.2% worse in Z08 (inside the 8% allowance). Every gate passes; the smoke test confirms the artifact loads and produces a plausible number for a fixed trip.

The defect is not in the numbers. It is in the training data: 849 rows, 47 fewer than every other candidate. Z08's training rows were dropped by a "remove outliers" filter that treated a whole zone as noise. The numeric gates could not see it because Z08's test error moved only 6.2%, inside a tolerance that exists precisely because 22 rows are noisy.

## The incident and the rollback

The Z08 error was noticed the next morning on a per-zone chart, not by the registry. The reviewer opened the version and found `train_rows: 849` against `896` for every other version — a signal that had been recorded and not checked.

```text
$ python registry/registry.py rollback
rolled back: v5 -> v2
```

Measured end to end: **2.1 s** for the command, of which **25 ms** is the alias write and 1.5 ms the alias read; the rest is Python and MLflow import time. The artifact already existed, so nothing was rebuilt.

What the rollback did:

- `models:/raviride-eta@champion` resolved to v2 again;
- the smoke test passed on v2 (43.00 min for the same trip);
- an audit tag recorded `rollback_at` on v2 and `promoted_from: 1` on v2's promotion record.

What it did not do:

- fix the missing provenance gate;
- fix v5's training data;
- tell anyone that Z08 had been absent for a day.

Those became follow-up actions.

## The gate that would have caught it

The policy gained one line, and the training code gained a `dropped_zones` tag:

```yaml
forbid_dropped_zones: true
```

Re-running the same candidate under the new policy:

```text
$ python registry/registry.py gate 6
FAIL
  - training data excludes production zones: Z08
$ python registry/registry.py promote 6
BLOCKED v6:
  - training data excludes production zones: Z08
```

`promote` exits `1` and the alias does not move. Version 6 is byte-for-byte the same kind of candidate that was promoted as v5 an hour earlier; only the policy changed. That is the correct relationship: **the registry records, the policy decides, and the decision can be re-evaluated later** — a promotion is not a property of the model, it is a judgement made under a policy at a time.

## Lineage of the restored champion

```text
champion version: 2  aliases: ['champion']
version tags: candidate=deep, data_hash=285bbf8406f483a9, git_commit=ac4246f,
              run_id=cf6b16d6..., promoted_at=2026-10-24T02:46:41+00:00,
              promoted_from=1
run params: feature_set=full, max_depth=16, min_samples_leaf=1,
            n_estimators=300, random_state=42, train_rows=896
artifact uri: file:///.../mlruns/185804069013446306/cf6b16d6.../artifacts
```

Reading outward: the alias names v2; v2 names a run; the run names its parameters, its dataset hash, and its commit; the artifact directory holds the model with its signature. In six months, `285bbf8406f483a9` is the only link that can prove *which data*, and `ac4246f` the only one that proves *which code*.

## What the sequence establishes

| Claim | Evidence |
|---|---|
| A version is immutable; an alias is not | Versions 1–6 kept their metrics while `champion` moved |
| Gates must be machine-evaluable | Every refusal is a printed comparison with values |
| An aggregate can hide a regression | v4: best MAE, blocked on Z07 |
| Numeric gates cannot see provenance | v5 passed and was still wrong |
| Rollback is cheap; recovery is not | 2.1 s to move the alias; the gate took a day to add |
| Policies are temporal | v6 fails the policy that v5 passed |

The next module makes the registry's promise testable: build a service that loads `@champion` and rejects a request the artifact cannot honestly answer.
