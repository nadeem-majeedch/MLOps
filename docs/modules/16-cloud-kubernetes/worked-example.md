# Worked example · Thirty-five checks, twenty-four failures

The kit contains two manifest sets for the same ETA service. `starter/` is a plausible first draft: it runs on a laptop, the image was built locally, and the author has not operated a shared cluster. `solution/` is the corrected set.

The offline checker reports:

```text
starter/   11/35 checks passed, 24 failed
solution/  35/35 checks passed, 0 failed
```

This example walks the failures in the order they would hurt, not the order the checker prints them.

## The failures that take the service down

| Defect | What happens | Fix |
|---|---|---|
| Service `targetPort: 8080` while the container listens on 8000 | The Service has endpoints, but connections are refused or time out. The pod is healthy; the service is not. | Point `targetPort` at the container port, or use the named port `http` |
| One replica | A node drain, a crash, or a rollout is a full outage | At least two replicas, spread across nodes |
| `strategy: Recreate` | Every old pod is killed before a new one starts; downtime is guaranteed | `RollingUpdate` with `maxUnavailable: 0`, `maxSurge: 1` |
| No readiness probe | Kubernetes sends traffic to a pod before the model loads; early requests fail | `GET /ready` with a 5-second period and a 3-failure threshold |
| No liveness probe | A deadlocked process is never restarted | `GET /health` with a longer period than readiness |
| No startup probe | A slow model load is treated as a failed liveness probe and the pod restart-loops | A startup probe with a budget larger than the measured cold start |
| PDB `minAvailable: 0` | A node drain can evict every pod at once | `minAvailable: 1` with at least two replicas |
| HPA `minReplicas: 1`, `maxReplicas: 1` | The autoscaler exists but cannot scale; it is configuration theatre | Minimum 2, maximum above the expected peak, with a metric that tracks load |

The port mismatch is the most instructive. The Deployment is healthy, the readiness probe (once added) passes, and `kubectl get pods` is green. The failure is a mismatch between two objects, which no single-object check catches. The checker compares the Service's `targetPort` with the container's `containerPort`; a human reviewing only the Deployment would miss it.

## The failures that make it unsafe

| Defect | What happens | Fix |
|---|---|---|
| `image: raviride-eta:latest` | The tag can move; two pods can run different code; a rollback is not reproducible | Pin `1.0.0` or a digest; record the digest in the release note |
| No `imagePullPolicy` | With a mutable tag, the node may use a stale cached image | `IfNotPresent` for a pinned tag; `Always` for a mutable one, but pin instead |
| Plaintext `API_KEY` in `env` | The credential is in the manifest, the repository, and every clone | `secretKeyRef`, with the value in an external secret store |
| No `resources` | The scheduler cannot place the pod sensibly; one pod can starve a node; no QoS protection | CPU/memory requests from measurement; limits above the peak |
| No `securityContext` | The container runs as root with a writable filesystem and all capabilities | `runAsNonRoot`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, drop `ALL` |
| `namespace: default` | The service shares a namespace with everything else; RBAC and quotas cannot distinguish it | A dedicated namespace, with a quota and a role binding |
| No ConfigMap reference | Configuration is duplicated in the manifest or baked into the image | `envFrom.configMapRef`; keep secrets separate |

Running as root inside a container is not automatically a host compromise, but it removes a layer of defence and violates most cluster policies. The read-only root filesystem is the control that catches an application writing logs or caches to disk; the ETA service writes only to stdout, so it can run read-only with a small `emptyDir` at `/tmp`.

## The one check that is easy to fake

`maxUnavailable: 0` is necessary for a zero-downtime rollout and not sufficient. The rollout still depends on:

- the readiness probe being correct;
- the new image starting within the startup budget;
- enough cluster capacity for the surge pod;
- the old pod draining in-flight requests.

A manifest can declare the first three properties; only a cluster can demonstrate the fourth. This is why the module distinguishes static validation from a live exercise, and why the quality report records that no cluster was available.

## The rollout, on paper

If the corrected manifests were applied to a two-node cluster, the expected sequence for a new image is:

```text
t+0      kubectl set image deployment/raviride-eta api=raviride-eta:1.0.1
t+0      Deployment creates a new ReplicaSet; maxSurge 1 allows a third pod
t+2 s    new pod scheduled; image pulled
t+6 s    container starts; startup probe begins
t+9 s    startup probe passes; readiness probe begins
t+12 s   readiness passes; new pod added to Service endpoints
t+12 s   one old pod terminated; preStop/grace period drains requests
t+18 s   second new pod ready; second old pod terminated
t+24 s   rollout complete; old ReplicaSet retained for rollback
```

These timings are illustrative, not measured: no cluster was available in the authoring environment. The sequence is the part to understand; the seconds will differ with image size, node speed, and probe settings.

Abort criteria for this rollout:

| Signal | Threshold | Action |
|---|---|---|
| 5xx rate | > 1% for 2 minutes | `kubectl rollout undo`, then investigate |
| p95 latency | > 500 ms for 5 minutes | Pause the rollout, inspect the new pods |
| Readiness failures | Any new pod not ready after 60 s | `kubectl rollout undo`; check the startup budget and image |
| Error budget | More than 25% consumed in the window | Stop the rollout; reliability review before continuing |

A rollout without abort criteria is a hope with a YAML file.

## The cost worksheet

The bill is driven by capacity, not by the number of YAML files. A small estimate:

| Assumption | Value | Why it matters |
|---|---|---|
| Requests per second | 20 peak, 5 average | Sizes the pods and the node count |
| Latency per request | 15 ms p50, 40 ms p95 | Determines concurrency per pod |
| Pods | 2 minimum, 5 maximum | HPA bounds |
| CPU request per pod | 100m | Scheduler packing |
| Memory request per pod | 256Mi | Node sizing |
| Node | 2 vCPU, 8 GB | Illustrative; use the provider's current size |
| Node-hours per month | 730 | 24 × 30.4 |
| Nodes | 2 (one per failure domain) | Availability, not throughput |
| Assumed node price | $0.12/hour | Illustrative only; replace with the provider's current price |

The compute line is `2 nodes × 730 hours × $0.12 = $175.20/month` at the assumed price. Add the load balancer, NAT gateway, log storage, image registry, and monitoring; for a small deployment those fixed charges can exceed the compute line. The estimate is not a quote, and the price must be checked on the date of the decision.

The most sensitive assumption is not the node price; it is the request size. A 500m CPU request instead of 100m can cut the pods per node by a factor of five, and the node count rises with it. Measure before requesting.

## What the review establishes

| Claim | Evidence |
|---|---|
| The starter cannot serve traffic reliably | Port mismatch, one replica, no readiness probe, `Recreate` |
| The starter is unsafe | Root container, plaintext key, writable filesystem, no limits |
| The solution declares the intended controls | 35/35 static checks |
| The solution is proven in a cluster | **Not established**; no cluster was available |
| The rollout has an abort rule | The table above, with thresholds and an action |
| The cost is understood | A formula with assumptions, not a single invented price |

The fourth row is the one to keep in the report. Static validation is evidence about configuration; it is not evidence about behaviour.

## What the checker cannot see

- Whether the image exists, pulls, or starts.
- Whether the readiness endpoint actually returns 200 after the model loads.
- Whether the cluster has capacity for the surge pod.
- Whether the CNI enforces NetworkPolicy.
- Whether the storage class supports the volume.
- Whether the provider's load balancer has a quota.
- Whether the rollout drains connections before the process exits.

Those require a cluster and a load test. If you have one, run the optional lab and replace this paragraph with your own evidence. If you do not, say so.
