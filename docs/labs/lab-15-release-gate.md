# Lab 15 · Stop a defective model from passing release validation

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L15 | Advanced | 3 hours | [09 · Model registry](../modules/09-model-registry/index.md), [12 · CI/CD](../modules/12-ci-cd/index.md) | Yes, locally; hosted workflow not executed |

**Starter kit:** [`examples/labs/lab-15-release-validation/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-15-release-validation) — starter files, data generator, and acceptance checker.

## Scenario

A release bundle arrives with a good MAE: 2.74, better than the champion. It also
has 34 skipped tests, no named owner, and an artefact whose checksum no longer
matches the file. The existing validation script prints `PASS` because it only
reads the headline metric.

This is the failure mode that a metrics-only gate creates: it does not just miss
the problem, it certifies it. A green tick from a weak gate is worse than no
tick, because someone will trust it.

## What you will be able to do

- Validate a release bundle: metrics, artefact integrity, test evidence and
  metadata.
- Treat missing evidence as a failure rather than as compliance.
- Order a release workflow so nothing is published before validation.
- Distinguish "the model is bad" from "the bundle is not trustworthy".

## Prerequisites and setup

```bash
cd examples/labs/lab-15-release-validation
python make_bundles.py
python validate_release.py --bundle release/tempting
```

Expected: `PASS release/tempting`. That is the defect.

## Your task

Implement the five missing rules in `validate_release.py`, then fix the release
workflow so publishing happens after validation.

## Data and starter files

| File | Purpose |
|---|---|
| `make_bundles.py` | Builds an honest bundle and a tempting one |
| `release/clean/` | candidate.json, model.joblib, tests.json, checksums.txt |
| `release/tempting/` | Same, with three defects |
| `validate_release.py` | Metrics-only starter |
| `.github/workflows/release.yml` | Publishes before validating |

The tempting bundle:

| Property | Value | Why it matters |
|---|---|---|
| MAE | 2.74 | Passes every metric rule |
| Tests | 34 skipped, 0 passed | "Passed" and "did not run" are different |
| Metadata | no `owner` | Nobody to ask |
| Checksum | manifest written before the file changed | The artefact is not the one that was evaluated |

## Steps

### 1. Read the bundle

```bash
cat release/tempting/candidate.json
cat release/tempting/tests.json
cat release/tempting/checksums.txt
```

PowerShell:

```powershell
Get-Content release/tempting/candidate.json
Get-Content release/tempting/tests.json
Get-Content release/tempting/checksums.txt
```

Then recompute one hash by hand:

```bash
python -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('release/tempting/model.joblib').read_bytes()).hexdigest())"
```

It will not match the manifest. That mismatch is what the checksum file is for.

### 2. Verify integrity

Recompute every file listed in `checksums.txt`. A missing manifest is a block,
not a warning; without it, nothing in the bundle can be verified.

### 3. Load the artefact and predict

`joblib.load` and one prediction on `[[4.0, 60.0, 7.0]]`. A non-finite result is
a failure: a NaN prediction is worse than an exception because it travels.

### 4. Require test evidence

`tests.json` must exist, report at least 20 passing tests, and report zero
failures. Skipped tests are not passes. The threshold is arbitrary; the rule that
missing evidence fails is not.

### 5. Require metadata

`candidate`, `git_commit`, `data_hash`, `trained_at`, `owner` — all non-empty.
The bundle you cannot attribute is the bundle you cannot roll back or investigate.

### 6. Fix the workflow order

Validation before `upload-artifact`, with a timeout, and no `continue-on-error`.
The current file publishes first, so a later failure leaves a released artefact
behind.

### 7. Run the checker

```bash
python check_lab15.py
```

Expected: `17/17 checks passed`.

## Expected output

On the tempting bundle:

```text
BLOCK release/tempting
  - artifact_hash: model.joblib hash is 3f6a1c2e9d41..., manifest says 8c02b7d1f0a9...
  - tests_evidence: only 0 tests passed (need 20); 34 skipped
  - missing_metadata: absent or empty: owner
```

On the clean bundle: `PASS release/clean` with exit 0.

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Clean bundle passes | Exit 0, no reasons |
| 2 | Tempting bundle blocked | Exit 1 |
| 3 | Hash mismatch named | `artifact_hash` |
| 4 | Skipped tests named | `tests_evidence` |
| 5 | Missing owner named | `missing_metadata` |
| 6 | Good MAE does not buy a pass | `metric_ceiling` absent |
| 7 | Missing `tests.json` blocked | `tests_evidence` |
| 8 | Missing `checksums.txt` blocked | `artifact_hash` |
| 9 | Validation before publishing | Step order in workflow |
| 10 | Release job has a timeout | Job key present |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Clean bundle fails on `artifact_hash` | You edited a file after generating | Re-run `make_bundles.py` |
| Tempting bundle passes | Checksum comparison skipped when parsing fails | Fail closed on a parse error |
| `artifact_loads` fails on the clean bundle | Prediction input shape wrong | Use the same three features the bundle was fitted on |
| Workflow lint-style check fails | Upload step still first | Move validation above publishing |
| `FileNotFoundError` for a bundle | Relative path from the wrong directory | Run from the lab root |

## Reflection questions

1. Why is a skipped test more dangerous than a failed one in a release bundle?
2. What does the checksum protect against that a signature would protect better?
3. The gate blocks on a missing owner. Is that a technical control or a
   governance control, and does the distinction matter?
4. What would you add to this bundle so that a reviewer could reproduce the MAE
   without asking for a second artefact?

## Optional extension

Add a rule that requires the bundle's `data_hash` to match the dataset recorded
in the training run's metadata, and explain what an attacker with repository
write access could still do after this rule exists.

## Cleanup

```bash
rm -rf release artifacts
```

PowerShell: `Remove-Item release, artifacts -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] I saw the metrics-only gate accept a defective bundle
- [ ] All five rules are implemented and fail closed
- [ ] Missing evidence blocks, not warns
- [ ] The workflow publishes only after validation
- [ ] `check_lab15.py` reports `ACCEPTED`
- [ ] I noted that the hosted workflow was not executed here
