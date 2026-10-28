# Independent challenge · A policy that survives a persuasive colleague

## The brief

Write a promotion policy with at least three measurable gates, implement it, and prove that a model which fails those gates cannot become `champion` — even when a human with a deadline asks it to.

The interesting word is *prove*. A screenshot of a passing gate proves the happy path. You need to show the refusals, including the ones where the request is made politely, urgently, or with a flag someone added "just for now".

## What the policy must contain

At least one gate from each family:

1. **Absolute** — a ceiling that does not move when the champion changes.
2. **Relative** — a regression limit against the current champion.
3. **Slice or provenance** — a population-level or data-level requirement.

Plus:

- an explicit statement of what happens when the champion alias is empty;
- a documented override path (or a documented decision that none exists);
- failure messages that a reviewer can verify by hand.

## Adversarial tests to implement

Each test should assert that promotion is refused, and check the reason text.

| Test | What it simulates |
|---|---|
| `test_blocks_overall_regression` | A candidate 5% worse overall |
| `test_blocks_slice_regression` | A candidate better overall, worse in one zone |
| `test_blocks_missing_data_hash` | A run logged without provenance |
| `test_blocks_dropped_segment` | Training data missing a production zone |
| `test_alias_unchanged_after_refusal` | The most important one: a refused promotion must not move the alias |
| `test_break_glass_requires_reason` | Override without a written reason fails |
| `test_break_glass_is_recorded` | A permitted override leaves `approved_by` and `reason` tags |

`test_alias_unchanged_after_refusal` is the test most implementations fail the first time: the gate returns `False`, the caller ignores it, and the alias moves anyway.

## The persuasive colleague

Write a short section in `docs/promotion-evidence.md` describing three ways someone could get a failing model promoted, and what your implementation does about each:

- adding `--force` to the release script;
- editing `promotion_policy.yaml` in the same commit as the model;
- setting the alias directly with the client, bypassing `promote`.

You cannot prevent all three with code in one repository. Say which ones you prevented, which ones you detected after the fact, and which ones are organisational rather than technical. "Not prevented" is an acceptable answer when it is recorded.

## What to submit

1. `promotion_policy.yaml` with comments explaining each threshold.
2. The gate implementation and the seven tests.
3. `pytest -q` output showing all tests passing.
4. A blocked-promotion log with real output.
5. The override record (or the written decision that overrides are not permitted).
6. The "persuasive colleague" analysis.

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Coverage | Three gate families, each exercised by a test |
| Messages | Every refusal names values, limits, and the champion compared against |
| Alias safety | A refused promotion provably leaves the alias unchanged |
| Override | Either impossible, or recorded with who, why, and when |
| Tests | Fail when you remove the corresponding gate — you checked |
| Honesty | The analysis names at least one bypass you cannot prevent technically |

## Stretch

Add a **policy version** tag to every promotion (`policy: 2026-10-24`). Then show a candidate promoted under policy A that policy B would reject, and explain which policy governs an incident review six months later. This is the registry's hardest governance question, and there is no tool that answers it for you.
