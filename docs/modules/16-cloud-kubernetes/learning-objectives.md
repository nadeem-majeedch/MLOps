# Learning objectives · Module 16

| # | Objective | Evidence |
|---|---|---|
| 1 | Compare virtual machines, managed platforms, and orchestrators | A decision table with control, cost, and operational burden |
| 2 | Read and write the core Kubernetes objects | A Deployment, Service, ConfigMap, HPA, and PDB that pass the checker |
| 3 | Explain the difference between a request and a limit | A QoS class and a failure scenario for each |
| 4 | Design probes that answer different questions | Readiness, liveness, and startup probes with paths and thresholds |
| 5 | Scale without breaking the rollout | An HPA with a minimum above one and a PDB that protects capacity |
| 6 | Plan a release with abort criteria | A rollout plan with signals, thresholds, and an owner |
| 7 | Roll back and time it | A command, a verification, and an elapsed time |
| 8 | Provision infrastructure reproducibly | A Terraform/OpenTofu plan and a note on state |
| 9 | Estimate cost with stated assumptions | A range, not a single number, with the drivers named |
| 10 | Define SLOs and an error budget | Two SLOs, a measurement source, and a policy when the budget is spent |

## Production-readiness checklist

A stateless service is ready for a shared environment when these are true. Each is checkable from the repository or the cluster.

- [ ] The image is pinned to a version or digest, never `latest`.
- [ ] At least two replicas, and a disruption budget that keeps one available.
- [ ] Readiness and liveness probes hit different endpoints and have sensible thresholds.
- [ ] CPU and memory requests are set; limits are set and justified.
- [ ] The container runs as non-root, without privilege escalation, with a read-only root filesystem where possible.
- [ ] No credential appears in an environment value, image layer, or ConfigMap.
- [ ] A rollout strategy keeps capacity and has an abort rule.
- [ ] A rollback command is documented and has been rehearsed.
- [ ] Logs go to stdout/stderr; no application log files inside the container.
- [ ] The service has an owner, an SLO, and an alert that a human can act on.

## The question behind every object

Kubernetes is a set of controllers reconciling desired state with observed state. For each object, ask:

| Object | Desired state it declares | What breaks without it |
|---|---|---|
| Deployment | How many replicas of which pod template | No self-healing, no rollout |
| Service | A stable virtual address for a changing set of pods | Callers need pod IPs; pods change |
| ConfigMap | Non-secret configuration | Configuration baked into images |
| Secret | Sensitive configuration, access-controlled | Credentials in manifests or images |
| HPA | A scaling rule | Manual scaling, or a fixed capacity |
| PDB | A disruption floor | A node drain takes every replica |
| Ingress | External routing and TLS | A bespoke proxy per service |

A manifest that exists but does not express the intended property is worse than a missing one: it looks like a control.

## Self-check before you start

You should have a container image (Module 11), a CI workflow (Module 12), and a monitored service (Module 14). You do not need a cloud account. If you do not have Docker or `kind`, you can complete the module with the offline checker and a written rollout plan; say so in your evidence.

After the module, you can answer:

1. Why does a readiness probe fail a pod that a liveness probe would restart?
2. What happens when a container exceeds its memory limit, and what happens when it exceeds its request?
3. Why is `maxUnavailable: 0` not enough to guarantee zero downtime?
4. When is a managed platform a better choice than Kubernetes?
5. What does a Terraform state file contain, and why is it a secret?
