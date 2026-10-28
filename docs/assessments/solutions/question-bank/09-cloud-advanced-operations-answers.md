# Answer key · Question bank 09

[Back to the questions](../../question-bank/09-cloud-advanced-operations.md)

---

## Section A (1 mark each)

**A1 — b.** A Deployment replaces pods gradually according to `maxSurge` and
`maxUnavailable`. Stopping everything (a) is a Recreate strategy; the Service (d)
selects pods by label and survives.

**A2 — b.** Readiness gates Service endpoints. Liveness (a) triggers restarts; it
does not decide traffic.

**A3 — a.** Requests influence scheduling and are the guaranteed share; limits cap
usage and cause throttling (CPU) or termination (memory).

**A4 — b.** The previous container's logs and `kubectl describe pod` give the exit
code, reason, and events. Scaling (a) multiplies a broken pod.

## Section B (3 marks each)

**B1.** The concepts — images, probes, rollouts, service discovery — are stable
and transfer; provider syntax changes. A provider lesson adds what the concepts
omit: IAM, managed identity, load balancer behaviour, storage classes, and the
cost model of that provider. Two marks for the distinction, one for naming a
provider-specific addition.

**B2.** With `maxUnavailable: 1` and no surge, one of three pods is removed before
its replacement is ready, so capacity drops by a third during the rollout. The
settings are `maxSurge` and `maxUnavailable`; readiness probes determine when a
replacement counts as available.

**B3.** Works: CPU-bound request handling, where load correlates with CPU and the
service is not waiting on a downstream. Misleads: a service that queues requests
while CPU stays low (waiting on I/O or a model server), or bursts that finish
before a new pod is ready; then use queue depth, in-flight requests, or p95 latency
as the scaling signal.

## Section C (4 marks each)

**C1.** Causes and confirmations:

| Cause | Confirmation |
|---|---|
| Insufficient schedulable CPU/memory | `kubectl describe pod` events: `Insufficient cpu` |
| Unsatisfiable node selector/affinity/taint | Events name the selector or taint; compare with node labels |
| Unschedulable PVC or unbound storage class | Events: `pod has unbound immediate PersistentVolumeClaims` |
| Image pull failure | `ErrImagePull`/`ImagePullBackOff` in events, not Pending |

Three causes with the check, one mark each, plus one for reading events rather
than guessing.

**C2.** About half the requests failing across ready pods points at the routing or
the service definition, not the application: for example a Service selecting pods
from two versions (the old ReplicaSet still matching the selector), or a port
mismatch between the Service `targetPort` and the container, or endpoints
including pods that are terminating. Fix: make selectors version-specific, ensure
the Service targets the right port, and use a `preStop` sleep plus a graceful
shutdown so terminating pods stop receiving traffic before exiting.

## Section D (9 marks)

| Element | Marks | What it looks like |
|---|---|---|
| Capacity | 2 | Estimate concurrency (50 × 0.2 s ≈ 10 in flight), choose replicas per pod from a measured per-pod throughput, add headroom for one node loss |
| Availability | 2 | Pod anti-affinity across nodes, PodDisruptionBudget, at least three replicas |
| Probes | 2 | Readiness requires model loaded; liveness checks the process without depending on downstream; start-up probe for slow load |
| Update and rollback | 2 | RollingUpdate with surge, `kubectl rollout undo` or a pinned image tag, and a tested rollback under five minutes |
| Evidence | 1 | Load test at target rate with p95, rollout log, rollback timing, and the image digests |

A strong answer admits that p95 under 200 ms cannot be guaranteed by Kubernetes
alone: it depends on the model, the request size, and the per-pod latency, which
must be measured first. A plan that adds replicas without a measured per-pod
throughput is a guess.
