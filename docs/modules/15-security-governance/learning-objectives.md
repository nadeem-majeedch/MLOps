# Learning objectives · Module 15

| # | Objective | Evidence |
|---|---|---|
| 1 | Threat-model a service before reviewing code | A data-flow sketch, trust boundaries, and a ranked STRIDE table |
| 2 | Distinguish authentication from authorisation, and a secret from a token | Correct use of the terms in the review, with one example of each failure |
| 3 | Manage a secret through its whole life | Storage location, access scope, rotation step, and verification |
| 4 | Read a dependency scan without panic | A triage table: reachable, exploitable, fixed, accepted, with reasons |
| 5 | Minimise personal data | A data inventory with purpose, retention, and the fields deliberately not collected |
| 6 | Measure disparity honestly | Group table with row counts, selection rate, TPR, FPR, and a stated caveat |
| 7 | Write a model card a reader can act on | Intended use, limitations, prohibited use, disparity, monitoring |
| 8 | Describe an auditable lineage | Alias → version → run → data hash → commit → approval |
| 9 | Respond to a credential leak | A timed containment, rotation, and verification record |
| 10 | Separate what the system protects from what it does not | A residual-risk section with owners |

## Release-review criteria

A reviewer should be able to answer these from the repository, without asking the author:

- [ ] Which credentials does the service need, where are they stored, and who can read them?
- [ ] What happens when a credential is rotated — is there a restart, a cache, a downtime window?
- [ ] Which personal data enters the system, why, where is it stored, and when is it deleted?
- [ ] Which dependency findings are known, and which have an owner and a date?
- [ ] Which group attributes are collected, under what purpose, and who approved that?
- [ ] What is the measured disparity, on how many rows, at which threshold?
- [ ] Can the live model be traced to a dataset version and a commit?
- [ ] Who can promote, who can roll back, and is the action logged?
- [ ] What is the first action if a key is found in a public log?
- [ ] Which risks are accepted, by whom, and when is the decision reviewed?

## The distinction that matters most

**Security** asks who can do what to the system. **Privacy** asks what the system knows about people and whether it should. **Fairness** asks how the system's errors and benefits are distributed. **Governance** asks who decided, on what evidence, and who can change it.

A control can improve one and worsen another. Encrypting a log protects confidentiality and does nothing for a retention policy that should have deleted the data. Removing a group attribute from the model can reduce one kind of disparate treatment and make proxy discrimination harder to detect. Write the trade-off down; do not claim a control solves all four.

## Self-check before you start

You should have a served model (Module 10), a registry alias (Module 09), and a container build (Module 11). You do not need a cloud account, a security product, or a legal adviser. The reference tools are `gitleaks`, `pip-audit`, and `fairlearn`, but the lab can be completed with the supplied Python scripts when those tools are unavailable.

After the module, you can answer:

1. Why does deleting a key from a file not remove it from the repository?
2. Why is "the scanner found nothing" weak evidence?
3. When is a fairness metric misleading even when the arithmetic is correct?
4. What is the difference between an accepted risk and an unexamined one?
5. What would you show an auditor if asked to prove which model is live?
