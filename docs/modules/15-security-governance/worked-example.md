# Worked example · Six findings and a number that looks fine

This example combines two reviews of the same fictional organisation. The first is a security and privacy review of a small session-scoring service, using the fixture in [`examples/labs/lab-19-security-review/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-19-security-review). The second is a fairness check of the support-risk model on the synthetic course dataset.

Both are deliberately small enough to reproduce. Neither concludes "the system is secure" or "the model is fair".

## Part 1: the review that starts with sixteen rows

The scanner reports sixteen candidate lines across six rule classes:

```text
$ python scan.py
rule                  file                        line  excerpt
hardcoded_secret      app/config.py               8     API_KEY="<redacted>"
hardcoded_secret      app/config.py               9     DB_PASSWORD="<redacted>"
pii_email             app/logs/service.log        4     ... <email> ...
pii_date_of_birth     app/logs/service.log        4     ... <date> ...
secret_in_ci          app/.github/workflows/deploy.yml 9   ... ${{ secrets.DEPLOY_KEY }} ...
...
16 candidates: broad_permissions=1, hardcoded_secret=2, pii_date_of_birth=3,
pii_email=5, secret_in_ci=1, unpinned_action=1, unpinned_dependency=2
```

Sixteen lines are not sixteen problems. Grouping by cause produces six findings:

| ID | Finding | Severity | Impact | Mitigation and verification |
|---|---|---|---|---|
| F1 | Two live-looking credentials in `config.py` | High | Anyone with repository access can use the API and database; the values are also in history | Revoke both, issue new values into the platform secret store, add a pre-commit scan, re-run the scanner on a fresh clone and confirm zero live matches |
| F2 | Full request payloads and the API key are logged | High | Names, emails, dates of birth, and a credential are duplicated into a log with different access controls and retention | Remove the key from the log line; log a request ID and a redacted field set; delete existing log data; verify by searching the new log for the fixture values |
| F3 | CI echoes a deployment secret | High | The value appears in build logs visible to anyone with log access, on every push | Remove the echo, rotate the secret, restrict log visibility, add a workflow lint that fails on `${{ secrets.* }}` inside `run:` |
| F4 | Workflow grants `write-all` | Medium | A compromised action or a malicious pull request step can write to the repository | Declare per-job permissions, read-only by default; use `contents: read` for the test job; verify with a dry run and a review of the workflow |
| F5 | Actions and dependencies are unpinned | Medium | A moved tag or a compromised release changes what runs without a code change | Pin actions to a commit SHA and dependencies to exact versions with hashes; enable update PRs; verify by resolving each reference |
| F6 | A CSV of names, emails, and dates of birth is committed | Medium | Personal data in a repository is copied to every clone and fork, and retention is unenforceable | Remove it, replace with synthetic or aggregated data, restrict history access, record the retention decision; verify no copy remains in the current tree |

The ranking is not the same as the scanner's order. F1 is first because it is exploitable now. F6 is last because the data is already exposed, but removing it from the working tree does not remove it from clones — that is why the mitigation includes a decision about history and access, not just `git rm`.

### The redaction rule

The scanner prints `API_KEY="<redacted>"`, not the value. A finding that quotes the secret has copied it into a second system: the ticket, the report, the chat, the screenshot. Redact at the source, and never paste a live value into a review document. If you need to prove which value it was, use a fingerprint (the last four characters of a hash), not the value.

### The rotation rehearsal

A rotation is not complete when the new key works. It is complete when the old key fails:

```text
1. Create the new credential in the secret store.        T+0
2. Deploy a configuration that reads the new value.      T+4 min
3. Verify /health, /ready, and one authenticated call.   T+6 min
4. Revoke the old credential.                            T+8 min
5. Confirm a call with the old value returns 401.       T+9 min
6. Record the timestamps and the operator.               T+10 min
```

The reference incident does not exist; this is a rehearsal. The point is that step 5 is the one teams skip, and it is the only step that proves the old credential is dead.

## Part 2: the fairness table that needs a second look

The support-risk model is trained on 300 rows and evaluated on 100, at a threshold of 0.50. The aggregate is:

```text
overall         selection 0.250  TPR 0.643  FPR 0.097  precision 0.720
```

That reads as a reasonable model: it flags a quarter of students, identifies about two-thirds of those who need support, and has a false-positive rate under 10%. Now split by prior GPA band:

| Group | Rows | Positives | Selection rate | TPR | FPR |
|---|---|---|---|---|---|
| high | 24 | 0 | 0.000 | — | 0.000 |
| low | 24 | 18 | 0.917 | 0.944 | 0.833 |
| mid | 52 | 10 | 0.058 | 0.100 | 0.048 |

Three things must be said before any conclusion:

1. **The high band has no positive labels in this test split.** Its TPR is undefined, not zero. A table that prints `0.000` there would be wrong; the script prints `NaN`.
2. **The bands are tiny.** Twenty-four rows per band means one student moves the selection rate by four percentage points. The confidence interval is wide.
3. **The band is not a neutral attribute.** The synthetic generator uses the band in the logit that produces `needs_support`. The model has learned a near-deterministic relationship, and the disparity reflects the generator, not a claim about real students.

The term split is more stable and more interesting:

| Group | Rows | Positives | Selection rate | TPR | FPR |
|---|---|---|---|---|---|
| 2025-Fall | 45 | 15 | 0.244 | 0.667 | 0.033 |
| 2026-Spring | 55 | 13 | 0.255 | 0.615 | 0.143 |

Selection rates are nearly equal (ratio 0.96), TPRs are close (0.92), and false-positive rates differ by a factor of four (0.033 vs 0.143). Which disparity matters depends on the intervention. If a flag triggers a supportive tutoring invitation, a false positive costs an invitation; if it triggers a mandatory meeting or a hold on registration, a false positive is a burden, and the 14% rate in spring deserves attention.

### What the numbers do not say

- They do not say the model is discriminatory. They say the measured error and selection rates differ on this split.
- They do not say the model causes the difference. The base rates differ, and the features are correlated with the group.
- They do not say the model is fair if the numbers are equal. A model can be equally wrong for everyone.
- They do not survive a change of threshold. At 0.30, every rate moves; the ranking of groups may not.

The fair thing to write in the report is the table, the row counts, the threshold, the caveat, and the decision the team is making about the trade-off. That is more useful than a single "fairness score".

## Part 3: the model card, in the form a reader can use

```text
Intended use: identify students who may benefit from a support conversation in
the next two weeks. Adviser-facing; not student-facing.

Not for: disciplinary action, admission decisions, fee collection, or any
automated decision without a human review.

Data: 400 synthetic student-term records generated for this course. No real
student data. The generator uses prior GPA band, attendance, LMS logins,
submissions, and support contacts.

Evaluation: 100-row holdout, threshold 0.50. Overall selection 0.250, TPR 0.643,
FPR 0.097, precision 0.720. By term, FPR is 0.033 (2025-Fall) and 0.143
(2026-Spring); by GPA band the test groups are too small to support a stable
estimate.

Limitations: synthetic data; small holdout; no measurement of whether support
actually helps; prior GPA band is a proxy for need and may encode disadvantage;
no monitoring of label quality; the threshold was chosen for the exercise, not
by an adviser.

Monitoring: weekly selection rate and TPR by term; alert on a shift greater than
10 percentage points; review any change with an adviser.

Owner: module author. Review date: before any use with real students.
```

Two sentences do the most work: "not for disciplinary action" and "prior GPA band is a proxy". The first prevents a misuse that the model cannot prevent itself. The second tells a reviewer where to look.

## What the review establishes

| Claim | Evidence |
|---|---|
| The service has exploitable credentials in source | Two scanner matches, both redacted, both confirmed by reading the file |
| Personal data is duplicated into logs | Three date-of-birth and five email candidates in one log file |
| The CI workflow can write to the repository | `permissions: write-all` in the workflow |
| The model's aggregate metric hides a group difference | Selection 0.250 overall; 0.917 vs 0.058 across GPA bands |
| The difference is not proof of unfairness | Group sizes, proxy relationship, synthetic generator, one threshold |
| The rotation is verifiable | Old credential returns 401 after revocation |

## What the review does not establish

- It does not prove the service is secure after the six fixes; it removes six known classes of failure.
- It does not prove the model is fair; it measures one split and states the caveats.
- It does not test the deployed system; it reviews source and artifacts.
- It does not assess legal compliance; that depends on jurisdiction, purpose, and the institution's rules.

The last point is the one to say out loud in a real review. An engineer can provide evidence; a data protection officer or legal adviser decides what the law requires.
