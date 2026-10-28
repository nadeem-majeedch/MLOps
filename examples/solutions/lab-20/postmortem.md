# Postmortem: INC-2026-10-18

This is a blameless postmortem. It names systems and decisions, not people. The
purpose is to find what made the failure possible and cheap to repeat, not to
assign fault.

## Summary

Release v5 of the ETA model was promoted outside the normal gate at 02:00 and
served a request schema that did not include a feature the model required. Every
prediction raised `KeyError: 'traffic_index'` and returned 500. The service was
restored to v4 at 04:20 after an approval step that had no out-of-hours path;
660 requests failed in 140 minutes.

## Impact

Between 02:00 and 04:20, 660 of roughly 3,600 prediction requests failed (about
18%). Dispatch clients saw "estimate unavailable" and two support tickets were
raised at 02:31 and 02:47. Registration and reporting were unaffected; no data
was lost and no model was retrained during the incident.

## Timeline

- 01:58:42 — v5 starts and logs a feature-schema mismatch warning.
- 02:00:04 — first 500 from `KeyError: 'traffic_index'`.
- 02:12:00 — `latency_p95_high` pages the on-call engineer.
- 02:18:00 — `http_5xx_rate_high` fires as critical.
- 02:22:51 — page acknowledged, eleven minutes after it fired.
- 02:58:30 — mismatch hypothesised from the startup warning.
- 03:20:44 — rollback blocked pending release-owner approval.
- 03:52:10 — approval granted.
- 04:20:00 — champion alias moved to v4.
- 04:24:00 — 5xx alert resolved; recovery verified.

## Root cause

The v5 artifact was trained with `traffic_index` in its feature set, while the
serving request schema accepts only hours, prior score and sleep hours. Nothing
in the release path compared the two, so the mismatch was discovered by the
first request rather than by a test. The gate that would have caught it was
overridden to ship a long-session accuracy fix before the Monday peak.

## Detection

The first error appeared at 02:00:04 but no alert covered it; the first page was
a latency alert twelve minutes later. On-call acknowledgement took eleven
minutes, and the 5xx alert that named the actual problem fired at 02:18. A
startup log line described the cause at 01:58 and nobody was watching for it.

## Response

Rollback was the correct action and it worked: the alias change restored the
error rate to 0.1% and latency to 190ms within four minutes. What slowed it down
was process, not diagnosis: the rollback required a release-owner approval, and
outside working hours that took 87 minutes. The team verified recovery against
the 5xx rate and p95 latency before closing the alert.

## Prevention

- Add a contract test to the release gate that loads the artifact and posts a
  sample request; block promotion when the signature and schema disagree. Owner:
  ML platform. Verified by a red run on a deliberately mismatched bundle.
- Introduce a 5% canary for 30 minutes with automatic rollback on 5xx rate above
  2%. Owner: platform on-call. Verified by replaying this incident against the
  canary configuration.
- Pre-approve rollback outside working hours and remove the approval dependency.
  Owner: release manager. Verified by a monthly timed drill with a target under
  ten minutes.
- Alert on the 5xx rate and on startup schema warnings, not only on latency.
  Owner: observability. Verified by a synthetic failing deploy in staging.

## Lessons

The gate was not wrong; it was optional. A release process that can be bypassed
under deadline pressure will be, so the useful change is to make the safe path
the fast path: contract checks that run in seconds, a canary that limits blast
radius, and a rollback that needs nobody's permission at 3am. The on-call
engineer diagnosed the cause in 36 minutes with the evidence available; the
system, not the person, made the recovery slow.
