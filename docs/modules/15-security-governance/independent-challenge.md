# Independent challenge · Three mitigations, one recommendation

## The brief

The ETA model is accurate overall, but the last review found that one peripheral zone has a materially higher error and that the partner's proposed authentication scheme would give the dispatch console a token that can also promote models. You have one sprint, one engineer, and no authority to change the partner's contract.

Propose **three** mitigations for the worst disparity or the worst security finding. For each, state the cost, the expected effect, the residual risk, and how you would verify it. Then recommend **one** and explain what you are deliberately not doing.

The recommendation must be defensible to two audiences: an engineer who will implement it and a manager who will pay for it. "Improve fairness" and "improve security" score zero.

## Choose a target

Pick one, and say why it is the worst:

| Candidate | Evidence you might use |
|---|---|
| A zone with high MAE and many users | Slice table from Module 06 or 14 |
| A group with a low TPR at the current threshold | Fairness table from the lab |
| A partner token with excessive scope | Threat model and the proposed contract |
| Personal data in the prediction log | Data inventory and retention |
| An unpinned CI action with write permission | Workflow review |

The target must be supported by a number or a concrete artifact, not a feeling.

## Requirements

1. **Three distinct mitigations.** At least one technical, one procedural, and one design change. They must not be three versions of the same idea.
2. **Cost.** Engineer-days, ongoing operational cost, and any user-visible change. A range is acceptable; "cheap" is not.
3. **Expected effect.** Quantified where possible: expected MAE change, expected reduction in exposed records, expected false-positive change. If you cannot quantify it, say what measurement would tell you.
4. **Residual risk.** What remains after the mitigation, who owns it, and when it is reviewed.
5. **Verification.** A command, test, or audit that would show the mitigation works — and one that would show it failed.
6. **Recommendation.** One option, with the trade-off stated in two sentences.
7. **What you are not doing.** At least one rejected option and the reason.

## Suggested options

You are not limited to these, but they are realistic:

- **Recalibrate the threshold per zone.** Cheaper than retraining; changes the error/flag trade-off; may increase false positives.
- **Add zone-level features or a zone-specific model.** Higher cost; risks small-sample overfitting; needs a gate.
- **Collect better labels in the weak zone.** Improves measurement before modelling; takes time.
- **Scope the partner token to `/predict` and a rate limit.** Low cost; does not fix a compromised partner host.
- **Move the token to a short-lived credential with an audience claim.** More engineering; limits blast radius.
- **Remove a field from the prediction log and re-run monitoring.** Low cost; may reduce slice analysis.
- **Add a human review step before a high-risk flag becomes an action.** Changes the product, not the model; needs an owner.

## Deliverable

A two-page memo:

```text
1. Decision requested
2. Evidence (one table or figure)
3. Three options, with cost / effect / residual risk / verification
4. Recommendation and trade-off
5. What we are not doing, and why
6. Review date and owner
```

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Target | One problem, supported by a number or artifact |
| Distinctness | Technical, procedural, and design options are genuinely different |
| Cost | Engineer time and ongoing cost are stated |
| Effect | Quantified, or a measurement plan is given |
| Residual risk | Named, owned, and dated |
| Verification | Both a success check and a failure check |
| Recommendation | One option, with a trade-off a manager can repeat |
| Rejection | At least one option is declined for a stated reason |
| Honesty | No claim of "secure" or "fair" without scope |

## Questions to answer

1. Which option has the best effect per engineer-day, and which has the best worst-case outcome?
2. If the manager approves only the cheapest option, what risk remains, and would you accept it?
3. What would you measure for two weeks after the change to know whether it worked?
4. Which option would you revisit if the partner's traffic doubles?

## Stretch

Write the **one-page access decision** for the partner: what they may call, with which credential, at what rate, with what logging, and what happens when the credential is suspected compromised. Have someone else read it and try to find a permission you did not intend to grant.
