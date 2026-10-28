# Learning objectives · Module 07

| # | Objective | Evidence |
|---|---|---|
| 1 | Match test type to risk | A table of risk → test → what it cannot catch |
| 2 | Test feature logic exhaustively and cheaply | Unit tests with fixed inputs, including zero, missing, and boundary values |
| 3 | Test data contracts without the live dataset | Parametrised data tests over small fixtures |
| 4 | Test model behaviour, not model shape | Invariance, directional, and minimum-performance tests |
| 5 | Gate a metric | `baseline.json` plus a tolerance test that fails on a degraded model |
| 6 | Read coverage critically | A report with an explanation of each uncovered region |

## Test-strategy review criteria

A suite is reviewable when a reader can answer these from the tests and one page of notes:

- [ ] Every test would fail if the behaviour it covers broke. (Ask: "mutate the code; does this fail?")
- [ ] Data tests use fixtures, not `data/raw/`.
- [ ] At least one test asserts a *meaning* (direction or invariance), not just a shape.
- [ ] The regression gate has a stated tolerance and a recorded baseline.
- [ ] Slow tests are marked or separated.
- [ ] No test depends on the order in which others run.
- [ ] Skips are explained, never used to hide a failure.

## Self-check before you start

You should have run `pytest` at least once and be able to read an assertion failure. You do not need prior testing experience; the module builds the vocabulary.

After the module, you can answer:

1. What can a unit test never tell you about a model?
2. Why do data tests use fixtures rather than the live file?
3. What is an invariance test, and what class of bug does it catch that a shape test misses?
4. Why is a regression gate at 5% tolerance often better than one at 0.1%?
5. What does 53% coverage tell you, and what does it not tell you?
