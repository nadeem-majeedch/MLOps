# Lab 11 · Triage ten requests and five support tickets

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L11 | Intermediate | 2 hours | [10 · Serving with FastAPI](../modules/10-model-serving/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-11-request-triage/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-11-request-triage) — starter files, data generator, and acceptance checker.

## Scenario

Support forwards four complaints and one question about the prediction service.
The tickets describe symptoms; none of them names a cause. Your job is to
reproduce each report, read the actual response, and classify it: the caller's
mistake, the service's defect, or a contract that answers 200 while doing the
wrong thing.

The most expensive item is not the 500. It is the 200 that looks fine.

## What you will be able to do

- Turn a support ticket into a reproducible request.
- Classify a failure by who must act: client, service, or contract.
- Read a 422 body well enough to name the field and the rule.
- Recognise a 200 that is semantically wrong.

## Prerequisites and setup

```bash
cd examples/labs/lab-11-request-triage
python ../_shared/make_sessions.py --out data/sessions.csv
python make_model.py
python probes.py
```

Expected: a ten-row table with status codes, and `artifacts/probes.json`. Some
probes return 500; they are supposed to.

## Your task

Fill in `triage.yaml`: one classification and cause per probe, plus the single
change that would have prevented the 500. Then run `check_lab11.py`.

## Data and starter files

| File | Purpose |
|---|---|
| `service.py` | Frozen service with the defects (do not edit) |
| `probes.py` | Sends ten requests and records status, excerpt and evidence |
| `triage.yaml` | Your worksheet: class and cause per probe |
| `check_lab11.py` | Compares the evidence and your triage with the truth |

Classes:

| Class | Meaning | Who acts |
|---|---|---|
| `ok` | Correct behaviour | Nobody |
| `client` | Bad request, correctly rejected | Caller |
| `service` | Well-formed request, service failed | You |
| `contract` | 200, but not what the caller believes | You and the caller |

## Steps

### 1. Run the probes, then read them

```bash
python probes.py
```

Do not open `service.py` first. The evidence is the request and the response;
reading the code first turns diagnosis into confirmation.

### 2. Explain the 500

Probe `p06` sends `prior_score: 0`, which is inside the declared range. The
handler divides by it. The client sees an empty 500 because the exception escapes
the framework's error handling strategy.

Note in your triage that this is a service defect triggered by a *valid* request.

### 3. Explain the 200 that should not be a 200

Probe `p05` sends `score: 90` as an extra field. The model ignores it and answers
normally. Nothing in the response tells the caller the field was dropped. The
caller's mental model is now wrong, and the next decision they make inherits it.

### 4. Classify the remaining probes

`p02`, `p03`, `p04`, `p09` and `p10` are validation failures with different
causes (range, range, missing, all missing, wrong type). `p07` and `p08` are
method and route errors. `p01` is the only clean success.

### 5. Write the first fix

`first_fix` should name the failing operation, not a file. "Guard the division in
the prediction path, or remove it" is actionable; "fix service.py" is not.

### 6. Run the checker

```bash
python check_lab11.py
```

Expected: `36/36 checks passed`.

## Expected output

```text
p01  POST /predict         200    {"prediction": 84.9, "model_version": "2026.10.1"}
p02  POST /predict         422    greater_than_equal: ['body', 'hours']
p03  POST /predict         422    less_than_equal: ['body', 'prior_score']
p04  POST /predict         422    missing: ['body', 'sleep_hours']
p05  POST /predict         200    {"prediction": 84.9, "model_version": "2026.10.1"}
p06  POST /predict         500    Internal Server Error
p07  GET /predict          405    Method Not Allowed
p08  GET /prediction       404    Not Found
p09  POST /predict         422    missing: ['body', 'hours']
p10  POST /predict         422    float_type: ['body', 'hours']
```

Your prediction value may differ with your artefact; the statuses must not.

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | All ten probes executed | Statuses match the table |
| 2 | Every ticket classified | Correct class per probe |
| 3 | Every cause explains the behaviour | Contains the relevant field or mechanism |
| 4 | `first_fix` names the failing operation | No `TODO`, longer than a file name |
| 5 | Evidence file exists | `artifacts/probes.json` |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| All probes return 500 | Model artefact missing | Run `make_model.py` first |
| `p05` returns 422 | You edited the service's `extra` policy | Restore the frozen service; this lab diagnoses it |
| Probe crash instead of a status | `TestClient` re-raises exceptions | `raise_server_exceptions=False` is already set; do not remove it |
| Triage rejected on wording | Cause must contain the mechanism keyword | Say "zero" or "division", not "bug" |
| `p06` returns 422 | Your service copy is the Lab 10 solution | Use the frozen service in this lab |

## Reflection questions

1. Which ticket would a dashboard built on status codes alone have missed, and
   why?
2. The 500 is triggered by a request the schema accepts. Whose responsibility is
   the boundary: the schema author or the handler author?
3. What would you add to the API so a caller can tell that an extra field was
   ignored, without reading the docs?
4. Why is `first_fix` more useful phrased as an operation than as a file?

## Optional extension

Add a `--base-url` run against a live Uvicorn instance and compare the probe
results with the in-process ones. Note any difference in the 500 body, and explain
why the two paths differ.

## Cleanup

```bash
rm -rf data models artifacts
```

PowerShell: `Remove-Item data, models, artifacts -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] I ran the probes before reading the service code
- [ ] All ten requests are classified
- [ ] I distinguished the 500 from the contract problem
- [ ] The first fix names an operation
- [ ] `check_lab11.py` reports `ACCEPTED`
