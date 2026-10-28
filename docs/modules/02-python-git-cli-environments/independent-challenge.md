# Independent challenge · Break it, then prove it rebuilds

**Time:** 2 hours. **Deliverable:** `docs/rebuild-report.md` and two deliberately corrupted lock files.

The guided lab proved your environment works. This challenge proves something stronger: that the repository, not your memory, can rebuild it - and that you recognise the failure modes when it cannot.

## Part A: rebuild from the repository alone

1. Push your branch to a private remote, or copy the repository folder to a new location **without** `.venv` and without generated data.
2. In the copy, follow only what the repository documents. If you have to consult your memory or this page, the repository is incomplete: fix the documentation, then start again.
3. Record the elapsed time and every undocumented step you had to take.

**Evidence:** a table with `step`, `command`, `source in the repository` (which file told you). Any step whose source column is empty is a documentation defect.

## Part B: break the lock in two different ways

4. **Break 1 - impossible pin.** Add `numpy==0.0.1` to a copy of the lock file and install it. Record the exact error and the line that identifies the culprit.
5. **Break 2 - removed bound.** Remove a transitive dependency from the lock file (choose one that another package requires, for example `joblib`). Install, then run the tests. Record what breaks and whether the failure is at install time or at run time.
6. Restore the original lock and confirm the tests pass again.

## Part C: explain the difference

7. In `docs/rebuild-report.md`, answer in a short paragraph each:
   - Why did Break 1 fail immediately, while Break 2 may have installed successfully?
   - Which failure is more dangerous in production, and why?
   - What would have to be true for the lock file to be genuinely sufficient?

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Rebuild honesty | The report lists real undocumented steps, not "everything was documented" |
| Error capture | Both breaks have the verbatim message and the command that produced it |
| Diagnosis | The explanation distinguishes install-time failure from run-time failure |
| Restoration | The repository ends in a working state with a clean `git status` |

## Hints

- Break 2's outcome depends on whether the removed package is still importable from somewhere else. Check `python -c "import joblib"` before concluding.
- If Break 1 produces a wall of "Ignored the following versions", read the final three lines. The answer is nearly always there.
- `pip check` reports dependency conflicts in an installed environment. Run it after Break 2.

## Extension

Repeat Part A on a machine or a fresh user account where Python has never been installed for this project. The steps you discover are the ones your README is missing, and they are exactly what a new teammate will hit on day one.
