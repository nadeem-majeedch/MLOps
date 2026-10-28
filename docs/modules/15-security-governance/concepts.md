# Concepts · Building a system you can defend

## 1. Start with a threat model, not a checklist

A threat model is a short, structured argument about what can go wrong. It has four parts:

1. **Assets** — what is worth stealing, breaking, or lying about. A model artifact, a signing key, a database of student records, the reputation of the service.
2. **Actors** — who might act. An unauthenticated internet user, a compromised dependency, a careless insider, a legitimate user who sends malformed input.
3. **Trust boundaries** — where data or authority crosses from one zone to another. Browser → API, API → model store, CI → production, developer laptop → repository.
4. **Attack paths** — how an actor crosses a boundary to reach an asset.

**STRIDE** is a prompt for the fourth part: **S**poofing, **T**ampering, **R**epudiation, **I**nformation disclosure, **D**enial of service, **E**levation of privilege. Use it to generate candidates, then rank them by **likelihood × impact**. A table with twenty "possible" rows and no ranking is not a review; it is a word search.

For the ETA service, a useful first pass:

| Boundary | Threat | Example | First control |
|---|---|---|---|
| Internet → API | Spoofing | No authentication on `/predict` | Require a caller identity; rate-limit per identity |
| API → model store | Tampering | Anyone can overwrite the `champion` alias | Restrict promotion to a role; audit alias changes |
| CI → production | Elevation | Workflow has `write-all` and unpinned actions | Minimal permissions; pin actions by commit |
| Logs → support staff | Information disclosure | Full request bodies with names and emails | Redact at the logger; restrict log access |
| Repository → internet | Information disclosure | A token committed in a notebook | Secret scanning; rotate; history rewrite is a decision, not a reflex |

The ETA service's contract deliberately rejects unknown fields and unknown zones. That is a safety control, not a security boundary: it reduces malformed input, but it does not authenticate anyone and it does not stop an attacker who sends valid requests.

## 2. Secrets: storage, scope, rotation, and history

A secret is any value that grants access: an API key, a password, a private key, a signing token, a database connection string. Four rules cover most failures:

**Store it outside the code.** Environment variables loaded from a secret manager, a platform secret store, or an encrypted file that is excluded from version control. `.env` files are acceptable for local development only, must be ignored by Git, and must never be the production mechanism.

**Scope it.** A token that can read one bucket should not be able to delete the account. Prefer short-lived credentials and per-environment values. A CI token that can write to production is a production credential, even if it lives in a test workflow.

**Rotate it.** Rotation is a procedure, not an intention: issue the new value, deploy it, verify the service, revoke the old value, and record the time. If rotation requires a code change, it will not happen during an incident.

**Assume history is permanent.** Deleting a line from `config.py` does not remove the blob from Git history, forks, CI logs, or a colleague's clone. The immediate action is **revoke and rotate**, not "rewrite history". After rotation, decide separately whether the history needs cleaning, who has clones, and whether the repository was ever public.

A secret scanner is a smoke detector. It finds patterns, not live credentials. It will miss a key split across lines, a token in an image, and a value that does not look like a key. It will also flag test fixtures. Triage is part of the job.

## 3. Authentication, authorisation, and least privilege

**Authentication** answers "who are you?" **Authorisation** answers "what may you do?" A service that authenticates every caller but lets any caller promote a model has authentication and no authorisation.

Least privilege is the practice of granting the smallest permission that lets a task succeed, for the shortest time. In practice:

- separate read and write paths; the serving process needs to read the model, not register a new one;
- do not give a CI job repository-write permission to run tests;
- use per-environment identities, so a preview deployment cannot touch production data;
- log privileged actions (promotion, deletion, access-control change) with the actor and the time;
- review permissions quarterly; a permission granted for a one-off migration tends to become permanent.

The hardest part is not the policy, it is the default. A platform that grants broad permissions unless you opt out will produce broad permissions. Choose defaults that fail closed.

## 4. Supply chain: dependencies, actions, and provenance

Your system is the code you wrote plus everything it imports. The supply-chain questions are:

- **What versions are you running?** Pin direct dependencies and lock transitive ones. A range like `pandas>=2` is not a version, it is a hope.
- **What do those versions contain?** Run a vulnerability scanner (`pip-audit`, `osv-scanner`) against the lock file. A finding is not automatically exploitable: check whether the vulnerable function is reachable, whether the input is attacker-controlled, and whether a fixed version exists.
- **Where did the artifact come from?** Record the package index, the hash, and the build. A lock file with hashes is stronger than a requirements list.
- **Can a build be reproduced?** A CI action pinned to `@main` can change under you. Pin third-party actions to a commit SHA or a released tag, and review the change when you update.
- **What is the licence?** A model or dataset can be technically usable and legally restricted. Record the licence, the source, and the permitted use. "Found on the internet" is not provenance.

An SBOM (software bill of materials) is a machine-readable inventory of components. It is useful for answering "are we affected?" during an incident. A `requirements.txt` plus a container image digest is a minimal version of the same idea.

## 5. Privacy: collect less, keep less, explain why

Privacy engineering starts before the model. For every field, ask:

| Question | If the answer is unclear |
|---|---|
| What decision does this field support? | Do not collect it yet |
| Is it necessary, or merely convenient? | Try the model without it |
| How long is it kept? | Set a retention period and a deletion job |
| Who can read it? | Restrict access and log reads |
| Is it sensitive (health, biometric, financial, precise location, a child's data)? | Require a stronger justification and review |
| Could it be a proxy for a protected attribute? | Test the model with and without it |

**Data minimisation** is not only a legal idea; it reduces the blast radius of a breach. A prediction log that stores a hashed trip ID and the model version is enough to monitor drift and join to outcomes. It does not need a name, an email, or a free-text comment.

**Purpose limitation** means using data for the purpose it was collected for. Training a support-risk model on data collected for fee administration is a different purpose, even if the table is already there.

**Retention** is a technical control: a scheduled deletion, verified by a count, not a policy sentence. Logs are the usual offender because they are cheap to keep and rarely reviewed.

**Synthetic data** is a useful teaching and testing tool, but it is not automatically anonymous. A generator trained on real records can memorise them. For this course, all datasets are generated from rules, not from real student records.

## 6. Lineage and auditability

An auditor does not need a dashboard; they need a chain:

```text
alias champion -> model version 2 -> run 4f1c... -> data hash 285bbf... -> commit ac4246f -> approved by ...
```

Each link should be recorded automatically, not reconstructed from memory. The registry in Module 09 stores the version, run, data hash, and commit as tags. The pipeline records the parameter file. The container image has a digest. The deployment record says which digest is live.

If any link is `unknown`, say so. An honest gap is manageable; a fabricated link is worse than no lineage.

## 7. Fairness: measure, then interpret carefully

A model can be accurate overall and unequal in its errors. Three families of metric are commonly used:

- **Selection rate** (the share of a group predicted positive) — useful for asking whether the model offers the same access.
- **True positive rate / recall** (of the people who need support, how many are identified) — useful when missing a positive is the harm.
- **False positive rate** (of the people who do not need support, how many are wrongly flagged) — useful when a false alarm has a cost.

**Demographic parity** asks for equal selection rates. **Equal opportunity** asks for equal TPR. **Equalised odds** asks for equal TPR and FPR. These cannot generally all hold at once when base rates differ; the choice is a value judgement, not a mathematical one.

Four cautions:

1. **Small groups produce unstable numbers.** Twenty-four rows cannot support a precise rate. Report counts and intervals, or say "insufficient data".
2. **The threshold is a policy choice.** Moving it changes every group's rate. Report the threshold and who chose it.
3. **A group attribute can be a proxy.** Using prior GPA band to predict support need may encode the very disadvantage you are trying to measure. Removing it from the model does not remove it from the world; it may only hide the disparity.
4. **Fairness on the test set is not fairness in use.** Labels are noisy, the population changes, and the intervention itself changes outcomes. Monitor after deployment.

The reference fairness script reports a stark split by prior GPA band because the synthetic generator uses that band to create the label. That is a lesson about proxy variables, not a claim about real students. The term split is much more stable: selection rates 0.244 and 0.255, TPR 0.667 and 0.615, but FPR 0.033 and 0.143 — a fourfold difference on a small sample. Which number matters depends on the intervention: a false flag that triggers a supportive conversation is different from one that removes an opportunity.

## 8. Explainability and the model card

Explainability has two audiences. **A user** needs to know why this decision affected them. **A reviewer** needs to know what the model relies on, where it fails, and what it must not be used for.

Global explanations (feature importance, partial dependence) describe the model; local explanations (per-prediction contributions) describe one case. Neither proves causation, and both can be unstable when features are correlated. Use them to generate questions, not to certify fairness.

A **model card** is the durable artifact. A useful card has:

- intended use and users;
- training data provenance and licence;
- evaluation metrics, slices, and the evaluation date;
- limitations, including populations not represented;
- prohibited uses (for example, using a support-risk score as a disciplinary decision);
- ethical and privacy considerations;
- monitoring and owner.

The card should be short enough that a non-specialist reads it, and specific enough that a specialist can challenge it. "The model may be biased" is not a limitation. "Zone Z07 has 18 test rows and an MAE of 10.4 minutes after a storm; do not use the model for dispatch guarantees in that zone until it is retrained" is.

## 9. Governance: decisions, owners, evidence

Governance is how an organisation makes and records decisions about a system. Minimum viable governance for a course project:

| Decision | Who | Evidence |
|---|---|---|
| What the system is for, and what it must not do | Product owner | A one-page purpose statement and prohibited uses |
| Which data may be collected | Data owner | Data inventory with purpose, retention, and access |
| Whether a model may be promoted | Model owner plus a reviewer | Gate output, evaluation report, approval record |
| How a security finding is handled | Security owner | Finding, severity, fix, verification, acceptance if deferred |
| When a model is retired | Model owner | Retirement date, replacement, notification |

Two rules make governance real: a decision has a named owner, and an accepted risk has a review date. "The team decided" is not an owner.

## 10. Incident response for a leaked credential

A credential leak is a incident with a predictable sequence. Write it down before it happens:

1. **Contain.** Revoke the credential. Do not wait to understand how it leaked. If it is a signing key, disable the signer; if it is a database password, rotate it.
2. **Assess.** Which systems did it grant access to? Check logs for use from unexpected locations or at unexpected times. Assume use until the logs say otherwise.
3. **Eradicate.** Remove the source, add a scanner rule, fix the CI step that printed it, and check for other copies.
4. **Recover.** Deploy the new credential, verify the service, and confirm the old one fails.
5. **Review.** Write a short timeline, the root cause, the controls that failed, and one verification for each new control. Do not name an individual as the cause.

The most common mistake is to rotate the key and stop. The second most common is to rewrite Git history before rotating, which leaves the live credential valid while the team celebrates a clean log.

## 11. A secure default configuration

The following are cheap and prevent whole classes of failure:

- container runs as a non-root user, with a read-only root filesystem where possible;
- no secrets in image layers or build arguments;
- dependency and action versions pinned; automated update PRs reviewed;
- CI permissions declared explicitly, read-only by default;
- production promotion requires a separate identity from the developer's;
- logs redact known sensitive fields at the logger, not in a downstream job;
- backups encrypted and restore-tested;
- an inventory of data, models, and credentials, with owners.

None of these makes a system secure. They remove the failures that are embarrassing precisely because they are easy to prevent.

## 12. What honesty looks like

A review that says "no issues found" is usually a review that did not look. A credible review ends with:

- what was checked, and with which tool and version;
- what was found, including false positives and accepted risks;
- what was not checked, and why;
- what would change the conclusion.

That last section is the one a reviewer remembers. It is also the one that protects you when the system fails in a way nobody predicted.
