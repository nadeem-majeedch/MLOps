# Guided lab · Threat-model it, measure it, write it down

**Time:** 5 hours. **Tools:** Python 3.11/3.12, pandas, scikit-learn, PyYAML. Optional: `gitleaks`, `pip-audit`, Docker. CPU only; no account and no cloud service.

## Scenario and business problem

RaviRide wants to open the ETA API to a partner's dispatch console. The partner will send real trip requests, and the security team has asked three questions before access is granted:

1. What can an attacker reach, and what would they gain?
2. What personal data does the service hold, where does it go, and how long does it stay?
3. The model is accurate overall, but is it accurate for everyone it will affect?

You have a working service and a registry. You do not have a security product, a lawyer, or a budget. You have the repository, a scanner, and the ability to measure.

### Skills practised

- Drawing a data-flow diagram with trust boundaries and ranking threats.
- Reading a secret scan and grouping candidates into findings.
- Rehearsing a credential rotation and proving the old value is dead.
- Measuring selection rate, TPR, and FPR across groups.
- Writing a model card that states a limitation a reader can act on.
- Separating an accepted risk from an unexamined one.

### Prerequisites

Modules 09–11 complete: a registered model, a served API, and a container build. The lab's fairness step uses the synthetic dataset in `datasets/generated/study_support.csv`; run `python datasets/generate.py` if it is absent. The ETA service is in `examples/raviride/`; you do not need it running for Parts 1–4.

### Input data

| Data | Rows | Sensitive? | Use |
|---|---|---|---|
| `datasets/generated/study_support.csv` | 400 | No: synthetic, no real students | Fairness audit |
| `examples/labs/lab-19-security-review/app/` | small fixture | Fabricated secrets and PII | Optional secret-scan practice |
| ETA service source | — | No personal data | Threat model |

The `student_ref` column is a sequence number, not a real identifier. The GPA band is synthetic and used as an example grouping attribute, not as a claim about real students.

### Directory layout

```text
module-15/
├── examples/modules/15-security-governance/
│   └── fairness.py
├── docs/
│   ├── threat-model.md          # you write
│   ├── security-review.md       # you write
│   └── model-card.md            # you write
└── evidence/
    ├── fairness.txt             # captured output
    └── rotation.md              # rehearsal record
```

Create `docs/` and `evidence/` next to your project, or inside it. Keep them out of the service's runtime image.

## Part 1: threat model the ETA API (60 minutes)

1. Draw the data flow. Start at the partner console, cross into the API, then to the model store, the prediction log, and the registry. Mark each boundary where the trust level changes.
2. List assets: the model artifact, the alias that names the champion, the prediction log, the partner credential, the registry credentials, the container image, and the service's availability.
3. Fill a STRIDE table with at least eight rows. For each row, name the boundary, the threat, the asset, the likelihood (low/medium/high), the impact, and one control.
4. Rank the rows by likelihood × impact. Put the top three in `docs/threat-model.md` with a sentence explaining why each is ranked there.
5. For each top-three threat, name the evidence that would show the control works. "Use authentication" is not evidence; "a request without a token returns 401, and the token is scoped to `/predict`" is.

**Checkpoint 1:** the diagram has at least four trust boundaries, the table has at least eight threats, and every top-three threat has a verifiable control.

*Recovery:* if every row feels equally likely, choose a concrete attacker (an unauthenticated internet user, a compromised dependency, a departing contractor) and rank from that actor's position. A threat model without an actor is a list of worries.

## Part 2: scan, group, and rank (60 minutes)

6. Run the scanner on the supplied fixture:

   ```bash
   cd examples/labs/lab-19-security-review
   python scan.py --json artifacts/scan.json
   ```

   PowerShell:

   ```powershell
   cd examples/labs/lab-19-security-review
   python scan.py --json artifacts/scan.json
   ```

   Expected: 16 candidates across six rule classes, with credentials redacted.

7. Group the candidates by cause. Aim for six findings, not sixteen. Record the file, the line range, the severity, the impact, and a mitigation with a verification step.
8. Re-read `app/config.py`, `app/service.py`, and `app/.github/workflows/deploy.yml` yourself. The scanner cannot tell you whether a key is live, whether an email is a test fixture, or whether a log is retained for a week or five years.
9. Write `docs/security-review.md` with the six findings, the ranking rationale, and a "not checked" section.

**Checkpoint 2:** every finding names an impact and a mitigation that can be verified; no unredacted credential appears anywhere in your notes.

*Recovery:* if the scanner reports a different count, run it from the lab root with `--root app`, and check the PyYAML version. If you paste a secret into your notes, replace it with `<redacted>` and rotate anything real; a fixture value is still a bad habit.

## Part 3: rehearse the rotation (45 minutes)

10. Pick the API key finding. Write the six-step rotation sequence from Concepts §10 with timestamps and an owner role.
11. If you have a local service with an API key, perform the rotation against a copy: issue a new value, deploy it, verify `/health` and one authenticated call, revoke the old value, and confirm the old value returns `401`.
12. If you do not have a local service, rehearse with a small script: read the key from an environment variable, accept a request only when it matches, change the variable, and prove the old value fails.
13. Record the elapsed time and the verification output in `evidence/rotation.md`.

**Checkpoint 3:** the record shows the old credential failing after rotation, not just the new one working.

*Recovery:* if the old value still works, the service is caching it or reading a different source. Find the actual read path before declaring the rotation complete.

## Part 4: measure disparity (75 minutes)

14. Run the fairness audit:

    ```bash
    cd examples/modules/15-security-governance
    python fairness.py
    ```

    PowerShell is identical. The script reads `datasets/generated/study_support.csv` from the repository root.

15. Capture the output in `evidence/fairness.txt`. You should see:

    ```text
    overall         selection 0.250  TPR 0.643  FPR 0.097  precision 0.720

    group  rows  positives  selection_rate   tpr   fpr  precision
     high    24          0           0.000   NaN 0.000        NaN
      low    24         18           0.917 0.944 0.833      0.773
      mid    52         10           0.058 0.100 0.048      0.333
    ```

16. Run the term split:

    ```bash
    python fairness.py --group term
    ```

    Expected: selection 0.244 vs 0.255, TPR 0.667 vs 0.615, FPR 0.033 vs 0.143.

17. Answer these in `docs/model-card.md` or a separate analysis:

    - Which group has the largest gap, and how many rows support it?
    - Is the grouping attribute a legitimate need variable, a proxy, or both?
    - Which error matters more for the intervention: a missed student or a false flag? Why?
    - What would you change first: the threshold, the features, the labels, or the intervention?

18. Change the threshold to 0.30 and rerun. Record how every group's selection rate and TPR move. Explain why "the model is fair at 0.50" is an incomplete sentence.

**Checkpoint 4:** the table includes row counts and a caveat; the analysis distinguishes a measured disparity from proof of discrimination.

*Recovery:* if TPR is `NaN`, the group has no positive labels in the test split. Do not replace it with zero; report `undefined` and the row count. If every group looks identical, check that the group column is actually varying and that the test split is not accidentally the training split.

## Part 5: write the model card (45 minutes)

19. Fill every section: intended use, users, out-of-scope and prohibited use, data provenance and licence, evaluation (with the threshold and split), limitations, fairness, privacy, monitoring, owner, review date.
20. The limitations section needs at least three specific statements. "The model may be biased" is not one. Use the measured numbers and name the populations that are missing or too small.
21. Add a "what we would do before real use" section: a privacy review, an adviser review of the intervention, a larger labelled sample, and a monitoring plan.

**Checkpoint 5:** a reader who has not seen the code can decide whether the system is appropriate for their use, and can name one thing it must not be used for.

## Part 6: the release memo (15 minutes)

22. Write a one-page memo to the partner: what you reviewed, what you fixed, what remains, and the conditions of access. Include the residual risks and the review date.

**Checkpoint 6:** the memo does not say "secure" or "fair" without a qualifier and a scope.

## Expected outputs

| Output | Reference value |
|---|---|
| Scanner candidates | 16 across six rule classes |
| Grouped findings | 6, with 3 rated high |
| Fairness overall | selection 0.250, TPR 0.643, FPR 0.097, precision 0.720 |
| GPA-band split | low selection 0.917, mid 0.058, high 0.000 (0 positives, TPR undefined) |
| Term split | selection 0.244/0.255, TPR 0.667/0.615, FPR 0.033/0.143 |
| Rotation record | old credential rejected after revocation |
| Model card | every section filled; ≥ 3 specific limitations; one prohibited use |

## Acceptance criteria

| # | Criterion | Passes when |
|---|---|---|
| 1 | Threat model | ≥ 4 trust boundaries, ≥ 8 STRIDE rows, top 3 ranked with reasons |
| 2 | Controls | Each top-3 threat has a control and a verification |
| 3 | Findings | ≥ 5 distinct findings, grouped by cause, with impact and mitigation |
| 4 | Redaction | No unredacted credential in any submitted file |
| 5 | Rotation | Old credential fails after revocation, with evidence |
| 6 | Fairness | Group table includes rows, positives, selection rate, TPR, FPR |
| 7 | Interpretation | States that disparity is measured, not proof of discrimination |
| 8 | Threshold | Reports the threshold and shows one alternative |
| 9 | Model card | Intended use, prohibited use, ≥ 3 limitations, monitoring, owner |
| 10 | Residual risk | At least two accepted risks with owner and review date |
| 11 | Honesty | A "not checked" section names what the review did not cover |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: sklearn` | Wrong environment | Activate the course environment; install `requirements-labs.txt` |
| `FileNotFoundError: study_support.csv` | Dataset not generated | `python datasets/generate.py` from the repository root |
| `NaN` TPR for a group | No positive labels in that group | Report undefined; do not substitute zero |
| Fairness numbers differ slightly | Different scikit-learn version or split | Record versions and the seed; use the same environment |
| Scanner finds nothing | Wrong root or wrong working directory | Run `python scan.py --root app` from the lab root |
| Secret appears in a report | Copied from the fixture | Replace with `<redacted>`; rotate anything real |
| Rotation "passes" but old key works | Service cached the old value | Find the read path; restart or reload, then re-test |
| Model card rejected as vague | Limitations are labels, not statements | Name the population, the row count, and the consequence |

## Reflection questions

1. Which finding would you fix first with one hour, and which would you accept for a month? What makes the difference?
2. The scanner produces sixteen candidates and your review has six findings. What did grouping decide, and could it hide a problem?
3. The high GPA band has no positive test labels. What can you legitimately say about the model's TPR for that group?
4. The term split has nearly equal selection rates but a fourfold FPR difference. Which metric would you put in the partner memo, and why?
5. What is the difference between a model card and a README, and who reads each?
6. If the partner asked for a "fairness certificate", what would you give them instead?

## Optional extension

Add a **privacy data-flow** to the threat model: for every field in the request and the prediction log, record purpose, retention, access role, and whether it is necessary. Then remove one field and measure the effect on the model. If the effect is negligible, argue for not collecting it. If it is large, argue for a documented justification and a stricter retention rule.

A second extension: add a scanner rule for personal data in *model inputs* (an `email` field in a request schema). Explain why that is a different risk from PII in logs: the model may memorise it, and the model store's retention policy is usually not the one you documented.

## Cleanup

```bash
rm -rf docs/threat-model.md docs/security-review.md docs/model-card.md evidence
rm -rf examples/labs/lab-19-security-review/artifacts
```

PowerShell:

```powershell
Remove-Item docs, evidence -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item examples/labs/lab-19-security-review/artifacts -Recurse -Force -ErrorAction SilentlyContinue
```

Keep the fairness output if you are using it as portfolio evidence. Do not keep any real credential, even in a scratch file.

## Checklist

- [ ] The threat model names assets, actors, boundaries, and ranked threats
- [ ] Every top threat has a control and a verification
- [ ] The review has six grouped findings and a "not checked" section
- [ ] No secret appears unredacted in my notes
- [ ] The rotation record proves the old credential fails
- [ ] The fairness table includes row counts and a caveat
- [ ] I reported an undefined TPR as undefined, not zero
- [ ] The model card states intended use and at least one prohibited use
- [ ] The residual risks have owners and review dates
- [ ] The release memo does not overclaim
