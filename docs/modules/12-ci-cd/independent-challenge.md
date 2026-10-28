# Independent challenge · A gate that cannot be talked around

## The brief

Build a merge gate for model changes that survives a motivated colleague with a deadline. Then write the incident note for the one bypass you could not prevent.

"Survives" is measurable: for each attack below, either the attempt fails, or it succeeds **and** leaves a record that a reviewer will see. Silent success is the failure mode.

## Attacks to attempt

| # | Attack | What should happen |
|---|---|---|
| 1 | Open a PR that degrades overall MAE | Required check fails; merge blocked |
| 2 | Degrade only one zone, improve overall | Slice gate fails; merge blocked |
| 3 | Update `baseline.json` in the same PR as the model change | Requires code-owner review; the diff is visible |
| 4 | Loosen `--tolerance` in the workflow file in the same PR | Requires review of the workflow path; recorded |
| 5 | Push directly to `main` | Rejected by branch protection |
| 6 | Disable the workflow in a commit | Requires review; the change is visible in the diff |
| 7 | Re-run the workflow until it passes | Same commit, same result; record how you verified determinism |
| 8 | Add `continue-on-error: true` to the gate step | Requires review; add a test that fails if it appears |
| 9 | Use a fork PR to run privileged code | Secrets unavailable; the attempt is harmless |
| 10 | Approve your own PR | Blocked, or recorded as an exception |

You do not need all ten to behave perfectly. You need to know which do, which do not, and why.

## Requirements

1. **Required checks** on `main` for lint, tests, and the model gate.
2. **Path protection** for the files that define the gate: `baseline.json`, `params.yaml`, `.github/workflows/**`, and the gate script itself.
3. **Provenance in the evidence**: the gate log must print the baseline's hash and the data hash it compared, so a reviewer can tell which baseline was used.
4. **A guard test** that fails if `continue-on-error` appears on the gate step or if the tolerance is loosened beyond an agreed maximum. Yes, a test that parses YAML — it is crude and it works.
5. **An audit note** for each attack: prevented, detected, or not prevented.

## What to submit

- The workflow files and branch protection settings (screenshots or an exported description are acceptable).
- The guard test, and its output when you deliberately add `continue-on-error`.
- A table of the ten attacks: outcome, mechanism, and residual risk.
- One paragraph on the bypass you cannot prevent with repository settings, and what compensating control you would use.

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Enforcement | A failing gate genuinely prevents merging, demonstrated |
| Tamper resistance | Changing the baseline or the tolerance requires an independent review |
| Provenance | The gate log identifies the baseline and data it used |
| Guard | The guard test fails when the workflow is weakened, and you showed it |
| Coverage | At least eight of the ten attacks have a recorded outcome |
| Honesty | Residual risks are named, including administrator bypass |

## Questions to answer

1. Which attack was easiest to prevent, and which was hardest? Why?
2. If an administrator can override branch protection, what makes the override acceptable? (Consider audit logs, post-hoc review, and on-call authority.)
3. Why is "the workflow file is also code" a security property, not just a convenience?
4. What would you monitor to detect a gate that has been quietly weakened?

## Stretch

Implement the gate as a **reusable workflow** (`workflow_call`) shared by three repositories, with the tolerance defined in one place. Explain what centralising buys and what it costs when one repository needs a different policy.
