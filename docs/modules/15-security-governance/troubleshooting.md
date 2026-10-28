# Troubleshooting · Module 15

## Diagnose in this order

1. **What is the asset?** A credential, personal data, model integrity, availability, or a decision about people.
2. **Who can reach it?** Trace the boundary; do not assume the diagram is current.
3. **What is the evidence?** A scanner line, a log entry, a permission, a metric — not a suspicion.
4. **What is the impact if it happens?** Access, disclosure, wrong decision, downtime.
5. **What would prove the fix works?** A test, a revoked value, a closed permission, a measured rate.

## Failure table

| Symptom | Likely cause | Fix |
|---|---|---|
| Scanner reports nothing | Wrong root, ignored file type, or a clean tree | Run from the repository root with the documented `--root`; confirm the rule set; check `.gitignore` does not hide the file from the scan |
| Scanner reports dozens of hits in a fixture | Test data is being treated as live | Triage by file and purpose; exclude fixtures explicitly, with a comment; never suppress a live finding |
| Secret still valid after "removal" | History, forks, CI cache, or a deployed copy | Revoke first; enumerate copies; rotate; verify the old value fails |
| Rotation causes downtime | The service reads the secret once at start-up and has no reload | Add a reload path or a rolling restart; rehearse it before the incident |
| `pip-audit` fails on every package | Using a different environment or no lock file | Audit the lock file that built the image; pin and re-run |
| Fairness table has `NaN` | Group has no positives or no rows in the split | Report undefined with row counts; do not substitute zero |
| Fairness numbers change every run | Unseeded split or a different library version | Fix the seed, record versions, and compare on the same split |
| Every group looks the same | Group column is constant, or the split leaked | Check value counts; verify the group is not in the features |
| Model card is rejected as vague | Limitations are labels, not consequences | Name population, rows, metric, and what a reader should do |
| Audit chain stops at `unknown` | Commit or data hash not recorded | Record it at training time; document how to reconstruct; do not invent |

## Case 1: the key that will not die

You removed the line, committed, and pushed. A scanner still finds the value in an old commit, and the service still accepts it.

The order is wrong. The live credential is the emergency; the history is a separate problem.

1. Revoke the credential at the issuer. Confirm a request using it fails.
2. Issue a replacement, store it in the secret manager, and deploy.
3. Verify the service with the new value.
4. Enumerate copies: forks, clones, CI logs, container layers, notebooks, screenshots, tickets.
5. Decide whether history rewriting is necessary, who has clones, and whether the repository was public. Record the decision.
6. Add a pre-commit hook and a CI scan; test both with a fake key.

If the key was a signing key, revoke the signer and re-sign the artifacts. A password change does not invalidate signatures.

## Case 2: "the model is fair, the selection rates match"

Equal selection rates are one definition of fairness (demographic parity), and they can coexist with very different error rates. Check TPR and FPR, group sizes, base rates, and the threshold.

A model can select 25% of every group and still miss twice as many positive cases in one group. If the intervention is supportive, that is a serious harm. If the intervention is punitive, a high false-positive rate is the serious harm. The metric follows the decision.

Do not respond by removing the group attribute from the model and declaring the problem solved. The attribute may be a proxy for need, and removing it can make the disparity harder to see. Measure with and without it, and document the choice.

## Case 3: the dependency finding you cannot fix today

A critical vulnerability has no fixed version. You cannot patch, and the service needs the package.

Record:

- the package, version, and advisory;
- whether the vulnerable code is reachable and whether input is attacker-controlled;
- the compensating control (a WAF rule, a restricted network path, a feature flag that disables the path);
- the owner and the review date;
- the trigger that would force an emergency change.

An accepted risk with an owner and a date is governance. An unexamined risk is a future incident with no paper trail.

## Case 4: the review that finds nothing

A review with no findings is usually a review with no scope. Check:

- Did you review the deployed configuration, or only the source?
- Did you include the CI workflow, the container image, and the secret store?
- Did you look at logs, backups, and analytics, or only the API?
- Did you test an unauthorized request, or only read the authorization code?
- Did you measure a slice, or only the aggregate?

Add one deliberate negative test: a request without a token, a request with a token for the wrong audience, a query for another user's record. If all three fail closed, you have evidence. If not, you have a finding.

## Case 5: the model card nobody reads

A card that repeats the README is not a model card. Shorten it and make every sentence actionable:

- "Intended for adviser review within two weeks; not for automatic disciplinary action."
- "Trained on 400 synthetic records; do not infer performance on real students."
- "FPR is 0.033 in fall and 0.143 in spring on 45/55 test rows; review the threshold before a spring rollout."
- "Owner: ...; review date: ...; monitoring: weekly TPR and selection rate."

If a sentence would survive unchanged in a different project, delete it.

## When to stop and escalate

Escalate rather than improvise when:

- a credential may have been used by someone else;
- personal data has been exposed beyond its intended audience;
- the model is making decisions about people without a human review that the policy requires;
- a fix would require deleting evidence or rewriting shared history;
- the legal basis for processing is unclear.

The engineering response is to contain, document, and hand over with evidence. It is not to decide the institution's legal position.
