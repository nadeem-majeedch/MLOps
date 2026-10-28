# Troubleshooting · Module 07

## Collection and fixtures

| Symptom | Cause | Fix |
|---|---|---|
| `fixture 'trips' not found` | `conftest.py` is not in a parent directory of the test | Put it in `tests/` next to the test files |
| Tests collected from `.venv` or notebooks | No `testpaths` | Set `testpaths = ["tests"]` in `[tool.pytest.ini_options]` |
| `ModuleNotFoundError` only under pytest | Package not installed; tests pass by accident of cwd | `pip install -e .`, then run from the repository root |
| Fixture mutated by an earlier test | Module- or session-scoped fixture returning a mutable frame | Return a fresh copy per test |
| `ScopeMismatch` | A function-scoped fixture requested by a module-scoped one | Match scopes or remove the wider scope |

## Assertions

**`ValueError: The truth value of a Series is ambiguous`.** You asserted on a whole column. Use `.all()`, `.any()`, or compare a scalar: `assert (predictions > 0).all()`.

**`pytest.approx` fails on what looks equal.** The value is a NumPy array inside a pandas object; convert first (`float(...)`) or use `np.allclose`.

**A model test passes alone, fails in the suite.** Shared state: a module-level model fitted on mutated data, or a globally changed random seed. Keep test data immutable and seeds explicit.

## Slow or flaky suites

| Symptom | Cause | Fix |
|---|---|---|
| Suite takes minutes | Refitting a large forest per test | Reduce trees; fit once per module in a fixture |
| Different results between runs | Unseeded model or hash-order iteration | Seed everything; sort before iterating |
| Test fails only on CI | Locale, time zone, or path separator assumptions | Use `pathlib`, UTC, and explicit encoding |
| Random failures in a distance test | Floating-point boundary | Use a tolerance, and choose values away from the boundary |

## The gate

**`FileNotFoundError: baseline.json`.** Run the evaluate stage first and copy its metrics, or let the skip condition handle a fresh clone. Do not commit a baseline you did not accept.

**Gate fails after a legitimate retrain.** The tolerance is too tight for your data's natural variation. Measure the MAE of three acceptable runs, then set the tolerance above their spread and below the smallest regression you care about. Record both numbers in the strategy note.

**Gate passes a model you know is worse.** Check that the metrics file is the one the gate reads: a stale `metrics.json` from an earlier stage is the usual cause. Print the file's mtime in the failure message while debugging.

## Coverage

- `--cov=raviride_eta` measures the installed package. If you see `src/raviride_eta/...` twice, the package is both imported from `src` and installed; remove one path.
- Missing lines listed as `2-79` mean a module was never imported by any test. That is information, not a defect, for stage entry points.
- Do not add `# pragma: no cover` until you can say why the line cannot be tested.

## When a test is genuinely wrong

Delete or rewrite it, and say so in the commit message. Keeping a bad test because "we have 40 tests" trades a real signal for a number, and the next person will trust it.
