# Answer key · Question bank 08

[Back to the questions](../../question-bank/08-security-governance.md)

---

## Section A (1 mark each)

**A1 — b.** Injected at run time from a secret store, never in the repository or
image. A default in code (a) becomes the production value eventually; `config.yaml`
without commitment is one `git add -f` away from exposure.

**A2 — b.** A generator and manifest are verifiable and reproducible. Hashing
columns (c) is pseudonymisation, not absence of personal data; the README (a) is a
claim.

**A3 — b.** A model card is a governance document: use, data, evaluation, limits,
ethics. It is not a results slide (a) and not a data dump (c).

**A4 — a.** Only what the task needs. Root (b) increases blast radius; a shared
credential (d) destroys attribution and rotation.

## Section B (3 marks each)

**B1.** An unhashed install can resolve to a different package version, and a
compromised or typosquatted release executes at install time with your privileges.
Mitigations: a lock file with hashes (`pip install --require-hashes`), a private
index, or installing from a reviewed requirements file in CI with network egress
restricted. Any one, with the reason, earns full marks.

**B2.** Lineage is the recorded chain from data and code to artifact and
deployment. Incident questions: which data and code produced the deployed model;
who approved that version and when; what else used the same data or model, so you
know the blast radius.

**B3.** The attribute's information remains in correlated features (postcode,
language, device, prior use), and the historical label may encode past
discrimination. Removing the column also removes the ability to *measure* the
disparity. Instead: keep a protected attribute for evaluation where lawful,
measure outcomes by group, choose a fairness criterion with stakeholders, and
document the trade-off.

## Section C (4 marks each)

**C1.** Order: (1) confirm the key is revoked and cannot be used — if not, revoke
immediately; (2) scan history and all forks/artifacts for copies; (3) remove from
history with a rewritten history or a documented exception, coordinating with
anyone who cloned; (4) add secret scanning and a pre-commit hook; (5) record the
incident and the rotation. Cannot be skipped: revocation, because rotation is the
only step that changes who can use it. Removing history without revoking is
theatre.

**C2.** Equal accuracy can coexist with different error mixes: one group has more
false positives, the other more false negatives, and the totals balance. Report
the confusion matrix by group, the false-negative and false-positive rates
separately, the base rates, and the decision threshold. A single accuracy figure
is not evidence of fairness.

## Section D (9 marks)

| Element | Marks | What it looks like |
|---|---|---|
| Spoofing | 2 | Caller impersonates a broker; mutual TLS or signed requests, per-client credentials, rate limits |
| Tampering | 2 | Request altered in transit; TLS, integrity checks, server-side validation, audit log |
| Information disclosure | 2 | Score or model extracted; return the minimum, avoid verbose errors, no model internals, log redaction |
| Denial of service | 1 | Flooding; quotas, timeouts, bounded concurrency, caching where safe |
| Elevation / abuse | 1 | Score used to probe the model (model inversion); limit queries per applicant, monitor patterns |
| Residual risk | 1 | A named risk accepted with a reason and an owner — e.g. a determined client can still probe with many applications, mitigated but not eliminated |

A strong answer connects a threat to the *business* consequence (unfair pricing,
regulatory breach) and notes that the model itself is an asset to protect, not
only the infrastructure. Listing mitigations without residual risk loses the last
mark.
