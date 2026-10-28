# Postmortem: INC-2026-10-18

A blameless postmortem. Name systems and decisions, not people. The question is
what made the failure possible, not who was on call.

## Summary

TODO: three sentences. What broke, for how long, and what stopped it.

## Impact

TODO: failed requests, the window, what a user saw, and what was not affected.

## Timeline

TODO: at least six timestamps from the first signal to the verified recovery.
Use the times in `incident/app.log` and `incident/alerts.json`.

## Root cause

TODO: the mechanism, not the person. Include the schema mismatch and why it was
not caught before it reached traffic.

## Detection

TODO: which signal fired first, how long it took a human to act, and what was
missing that would have shortened it.

## Response

TODO: what worked, what slowed the rollback down, and what you verified before
declaring recovery.

## Prevention

TODO: at least three changes, each with an owner role and a way to check it
worked.

## Lessons

TODO: what this incident says about the release process, and what you would
change about the gate rather than about the person who overrode it.
