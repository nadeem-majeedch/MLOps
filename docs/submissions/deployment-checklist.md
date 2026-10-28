# Deployment checklist

> Copy this into `docs/deployment-checklist.md`. Complete it before the first
> deployment and repeat the short form for every later one. A checklist that is
> never used is documentation; one with dates and initials is evidence.

---

## Release record

| | |
|---|---|
| **Release** | *service 0.4.0, model v7 (alias `champion`)* |
| **Date and time** | YYYY-MM-DD HH:MM, timezone |
| **Operator** | *name* |
| **Change** | *one sentence: what is different for a caller* |
| **Rollback version** | *service 0.3.2, model v6* |
| **Rollback tested?** | *yes, YYYY-MM-DD, 3 min 10 s* |

---

## 1. Before deployment

### Artifact and version

- [ ] The model artifact hash matches `run_meta.json`.
- [ ] The training data hash and version are recorded.
- [ ] The service image digest is recorded, not only the tag.
- [ ] The release was built from the commit being deployed.
- [ ] The previous artifact and image are still available.

### Quality

- [ ] Tests pass on the release commit (link to run).
- [ ] The metric gate passed against the pinned baseline (link).
- [ ] Slice metrics are within their floors.
- [ ] The contract test passed.
- [ ] A smoke prediction returns a plausible value.

### Configuration

- [ ] Every required environment variable is present in the target environment.
- [ ] No secret is in the image, the repository, or the compose file.
- [ ] Timeouts, concurrency, and payload limits are set explicitly.
- [ ] The model path or registry alias resolves in the target environment.

### Observability

- [ ] `/health`, `/ready`, and `/model-info` respond.
- [ ] Logs include a request ID and the model version.
- [ ] The alert route has a named owner and a tested destination.
- [ ] The dashboard or query for error rate exists before traffic arrives.

### Communication

- [ ] The caller knows the change and any contract change.
- [ ] The on-call person knows a deployment is happening.
- [ ] The rollback trigger is written down: *e.g. error rate > 2% for 5 minutes*.

---

## 2. Deploy

```bash
# The exact commands, with placeholders replaced.
docker build -t eta-service:0.4.0 .
docker run -d --name eta -p 8000:8000 --env-file .env eta-service:0.4.0
```

*Record the commands you actually ran. If you used a different port or a compose
file, the checklist should say so, because the next person will copy it.*

| Step | Time | Result |
|---|---|---|
| Build | | |
| Start | | |
| Readiness green | | |
| First prediction | | |

---

## 3. Verify

- [ ] `/model-info` reports the expected version and hash.
- [ ] A known input returns the expected prediction (tolerance stated).
- [ ] Five malformed payloads return 422 with the field named.
- [ ] p95 latency is within budget under the test load.
- [ ] No new errors in the log for five minutes.
- [ ] The prediction log is receiving records.

---

## 4. Rollback (if needed)

**Trigger:** *state it before deploying, not during the incident.*

1. Stop traffic to the new version, or redeploy the previous image digest.
2. Confirm `/model-info` reports the previous version.
3. Send the known input; confirm the previous prediction.
4. Record the elapsed time and the reason.
5. Keep the failed version's logs.

| Attempt | Started | Service restored | Elapsed | Reason |
|---|---|---|---|---|
| | | | | |

---

## 5. After deployment

- [ ] The release record is updated with the outcome.
- [ ] The model version and image digest are in the runbook.
- [ ] Any deviation from this checklist is written down.
- [ ] A follow-up task exists for each item that was skipped.

---

## Short form, every release

| Check | Yes/No | Evidence |
|---|---|---|
| Artifact hash matches metadata | | |
| Gate passed | | |
| `/model-info` shows the new version | | |
| Smoke prediction plausible | | |
| Rollback version available | | |
| Owner informed | | |

---

## What this checklist deliberately omits

Database migrations, multi-region failover, and load-balancer draining, because
this course's service has no database and one region. If your project adds them,
add the checks; do not inherit a checklist that does not describe your system.
