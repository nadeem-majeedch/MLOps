# Independent challenge · A debt register a manager can budget from

**Time:** 2 hours. **Deliverable:** `docs/debt-register-reviewed.md`.

The lab produced a debt register for one script. A manager cannot approve "improve the code"; they can approve three items with costs and dates. This challenge is about that translation.

## The task

1. Take the "before" snapshot your instructor provides, or your own `legacy_train.py` plus its Git history before the refactor.
2. Interview it as a stranger would, using only the repository:
   - Clone it somewhere clean and follow its documentation. Note every undocumented step.
   - Search for absolute paths, credentials, and duplicated constants.
   - Check whether a value you might want to change appears in more than one file.
   - Run the tests, if any, and note what they do not cover.
3. Produce a register with **at least eight items**, covering at least four categories. For each: ID, category, symptom, risk, fix, cost (S/M/L with hours), owner role, and priority.
4. Add a one-page summary for a manager: what the top three items buy, what they cost, and what happens if nothing is done.
5. Rank by *risk reduced per hour*, and state your ranking rule explicitly. Any ranking is arguable; an unstated rule is not.

## What separates a strong register

| Weak | Strong |
|---|---|
| "Code is messy" | "The peak-hour list appears in `features.py` and `evaluate.py`; changing one silently changes the other's definition of peak" |
| "Add tests" | "The split boundary has no test; a change from `<` to `<=` moves one day of trips and changes the metric without an error" |
| Cost: "large" | Cost: "M - 6 hours, one developer, no dependencies" |
| Everything rated critical | Risk tied to a consequence: an unreproducible metric, a leak, a broken release |

## Rules

- Every item must be checkable by a reviewer in under five minutes.
- At least one item must be **accepted debt**, with a condition and a review date. Not everything should be fixed.
- No item may name a person; name roles.
- Do not include items that would require a redesign to fix in a week. Those go in an appendix labelled "beyond this quarter".

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Coverage | Four categories, eight items, each with evidence |
| Pricing | Every item has a cost in hours or S/M/L, and an owner role |
| Prioritisation | A stated rule produces the stated order |
| Manager summary | A non-engineer can decide what to approve from it alone |

## Extension

Take the three highest-priority items and implement one. Update the register with what actually happened: the cost estimate versus the real time, and any new debt the fix introduced. The gap between estimated and actual cost is the most useful number in the document.
