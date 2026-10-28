# MP5 · Operate and hand over (optional extension)

| | |
|---|---|
| **After** | Modules 13–16, with MP3 and MP4 complete |
| **Integrates** | Orchestration, security, cloud concepts, handover |
| **Effort** | About 14 hours |
| **Weight** | Not in the default total; optional portfolio piece |
| **Assumes** | A served, monitored system and a working gate |

---

## Brief

Someone else operates your system for a week while you watch. They have the
runbook and the repository, and you are not allowed to answer questions during an
incident. This is the last skill the course teaches and the one most often
skipped: most engineers can build a system, fewer can make it operable by
another person under time pressure.

The project is deliberately not about new technology. Orchestration here means a
scheduled retrain with retries and a backfill; security means a threat model and
a scan; cloud means a capacity estimate and optional manifests. None of it
requires a paid account.

---

## Deliverables

1. **Scheduled workflow** with retries, a failure alert, and a documented
   backfill procedure.
2. **Threat model** for the service, with four categories, mitigations, and
   residual risks.
3. **Security evidence**: secret scan clean or findings explained, dependency scan
   report, and a permissions sketch for the service's identity.
4. **Runbook** covering deploy, rollback, and the top three alerts, written for
   someone who has not seen the code.
5. **Capacity estimate** on paper: per-pod throughput, replicas for a target rate,
   headroom for one node loss, and the assumptions.
6. **Handover drill record**: a peer (or you, after a day away) follows the runbook
   to deploy and roll back, with timings and every question they had to answer
   themselves.
7. **Incident review** of one injected fault: timeline, cause, detection gap, one
   control.
8. **Optional**: Kubernetes manifests, validated with `--dry-run=client`, and a
   statement of what was not executed.

---

## Acceptance criteria

- [ ] The scheduled workflow retries a transient failure and records the retry.
- [ ] A backfill of a missed interval produces no duplicate rows, demonstrated.
- [ ] The secret scan has no unexplained findings.
- [ ] The runbook's rollback section is followed by someone else in under 15
      minutes, and the elapsed time is recorded.
- [ ] Every alert in the runbook has an owner, a first step, and a closing
      condition.
- [ ] The capacity estimate shows its arithmetic and one assumption that could be
      wrong.
- [ ] The incident review names the detection gap, not only the cause.
- [ ] Anything not executed (a cluster, a cloud service) is labelled as untested
      with the procedure that would test it.

---

## Evidence

| Claim | Weak | Strong |
|---|---|---|
| Operable by another person | "The runbook is complete" | A peer's timings and the questions they had to resolve |
| Retries work | Retry configured | The failed attempt, the retry, and the run history |
| Backfill is safe | "It is idempotent" | Row counts before and after, and the key that prevents duplicates |
| Secure | "No secrets" | Scan output, dependency report, and residual risks named |
| Scales | "Kubernetes handles it" | Measured per-pod throughput and the replica arithmetic |

---

## Rubric

| Criterion | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Operability** | No runbook | Steps exist, untested | Peer completes deploy and rollback | As level 2, plus timings and the questions they had to resolve |
| **Failure handling** | None | Retry configured | Retry and backfill demonstrated, no duplicates | As level 2, plus a failure alert with an owner |
| **Security** | No evidence | A scan run | Scan, dependency report, threat model | As level 2, plus residual risks and permissions justified |
| **Judgement** | Claims scale without evidence | Capacity guessed | Arithmetic shown with assumptions | As level 2, plus one assumption tested or marked untested |

---

## Build order

1. Write the runbook from the commands you actually use, not from memory.
2. Have someone else follow it; fix the first three places they stall.
3. Add the schedule, retry, and failure alert.
4. Backfill one interval; check for duplicates.
5. Threat-model; scan; record findings.
6. Estimate capacity; label what is unmeasured.
7. Inject a fault; review it while the evidence is fresh.

The peer drill in step 2 is the centre of the project. Everything else supports
it.

---

## Common failures

| Failure | Signature | Fix |
|---|---|---|
| Runbook written from memory | Commands that no longer exist | Copy from shell history and test each |
| Backfill duplicates rows | Row count doubles | Upsert on a natural key; verify counts |
| Retry without idempotence | Duplicate side effects | Make the task idempotent before enabling retries |
| Threat model as a list | No residual risk | Name what remains after mitigation |
| Capacity with no measurement | A confident number | Measure one pod, show the division |
| Optional cloud claimed as done | "Deployed to EKS" with no evidence | Label as unexecuted, or show the receipt |

---

## Extension

Run the drill with a second person who has not read the modules. Their questions
are the findings. If no second person is available, wait 48 hours and follow your
own runbook with the repository closed; the gaps you find are the same ones.

See also: [Module 15 · Security and governance](../../modules/15-security-governance/index.md),
[Module 16 · Cloud and Kubernetes](../../modules/16-cloud-kubernetes/index.md),
[Lab 19 · Security review](../../labs/lab-19-security-review.md), and
[Lab 20 · Incident review](../../labs/lab-20-incident-review.md).
