# Knowledge check · Module 07

## Questions

1. Name the five test layers and one thing each cannot catch.
2. Why do data tests use a fixture instead of `data/raw/trips.csv`?
3. Write down one invariance test and explain the class of bug it catches.
4. A directional test asserts "longer distance never predicts a shorter duration". Name two bugs it cannot catch.
5. What two design decisions define a regression gate, and what happens if each is set badly?
6. A module shows 0% coverage and is a stage entry point. Is that a problem? Justify.
7. `features.py` is 97% covered, yet a unit bug survived the suite. Explain the discrepancy.
8. What is the test for whether an existing test is worth keeping?
9. Why should `pytest.skip` be visible in the summary rather than silent?
10. Name one thing your suite cannot protect against, and the module that addresses it.

## Answers and reasoning

**1.** Unit (cannot see data or model meaning); data (cannot see whether values mean the right thing); model behaviour (cannot see tomorrow's distribution); integration (cannot see statistical quality); regression gate (cannot see a slice regression when the aggregate is unchanged).

**2.** Because a test that depends on the live file fails when the data changes (not a code regression) and passes when the file happens to be clean (not a proof the check works). The fixture makes the defect explicit and the test fast and deterministic.

**3.** Example: permuting rows must permute predictions identically. It catches index misalignment, row-order dependence, and leakage from batch statistics computed during prediction.

**4.** A monotonic but wrong transform (for example, log-distance computed in miles); a constant offset or scaling error; a unit mismatch that preserves ordering. Direction is weak evidence of correctness.

**5.** The tolerance and the baseline. Too tight: legitimate runs fail, people disable the gate. Too loose: real regressions pass. A baseline that is the previous run allows slow degradation to slip through; a recorded accepted baseline does not.

**6.** Generally not a problem, if the logic it wires is tested elsewhere. Coverage of a `main()` measures plumbing. It becomes a problem when the wiring contains decisions (defaults, path construction) that nothing asserts.

**7.** Coverage counts executed lines. The bug's line was executed by tests that asserted shape, range, or direction, none of which pins the formula. The assertion, not the execution, is what would have caught it.

**8.** Break the behaviour deliberately; if the test does not fail, it is not testing that behaviour. A test that cannot fail is a false assurance and should be fixed or deleted.

**9.** A silent skip hides a broken environment or missing baseline for months, and the suite reports green. Marked skips with a reason are honest; unconditional ones are usually an unfinished test.

**10.** Any one of: data drift (Module 14), distribution shift between slices (Module 06/14), deployment-time contract drift (Module 10), or the decision to ship at all (Module 09). The point is that testing protects decided behaviour, not fitness for a changing world.

## Scoring

| Score | Next step |
|---|---|
| 8–10 | Continue to Module 08 |
| 5–7 | Reread sections 4–7 of [Concepts](concepts.md) and redo the lab's Part 4 |
| 0–4 | Rebuild the suite from the worked example, then repeat the lab with the gate |
