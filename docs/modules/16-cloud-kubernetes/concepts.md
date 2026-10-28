# Concepts · From a container on a laptop to a service someone operates

## 1. Three ways to run a container, and what each costs you

| Model | You manage | Provider manages | Good fit | Hidden cost |
|---|---|---|---|---|
| **Virtual machine** | OS, runtime, app, patching | Hardware, network, hypervisor | Long-lived, custom, or legacy workloads | You own the kernel and the uptime |
| **Managed container platform** | Image, configuration, scaling policy | Cluster, load balancer, patching | A small team that wants to ship an API | Less control over networking and runtime; platform limits |
| **Kubernetes (managed or local)** | Manifests, policy, capacity model | Control plane (if managed) | Many services, a platform team, portability | Operational complexity; you can build a distributed system by accident |
| **Serverless container** | Image and handler contract | Everything below the request | Spiky, event-driven work | Cold starts, execution limits, per-request pricing |

The question is not "which is modern?" It is "who should be on call for this?" A single prediction API with one team and predictable traffic is often cheaper and more reliable on a managed platform than on a cluster the team has to operate.

Kubernetes earns its complexity when you have many services, a need for portability, or a platform team that can own the cluster. It does not earn it because a job advert mentions it.

## 2. The mental model: desired state, reconciled

A Kubernetes cluster has a **control plane** (API server, scheduler, controller manager, etcd) and **nodes** (machines running kubelet and a container runtime). You submit objects to the API server; controllers compare the desired state in the object with the observed state and act.

```text
Deployment (desired: 2 replicas of image v1)
    └── ReplicaSet (desired: 2 pods)
            ├── Pod (node A)  ← kubelet, container runtime
            └── Pod (node B)
Service (stable address) → selects pods by label
```

A **Pod** is one or more containers sharing a network namespace and storage. It is disposable: it can be killed, rescheduled, and replaced at any time. Design for that; do not store state on the pod's local filesystem.

A **namespace** is a scope for names and, with RBAC and quotas, a boundary for access and capacity. Use one per environment or team, not one per service unless you have a reason.

## 3. The objects you need for a stateless API

**Deployment** declares a pod template and a replica count. It owns ReplicaSets and performs rollouts. Use it for stateless services.

**Service** gives a stable DNS name and virtual IP, and load-balances across pods selected by labels. `ClusterIP` is internal; `NodePort` exposes a port on every node; `LoadBalancer` asks the provider for an external load balancer.

**Ingress** (or a Gateway API resource) routes HTTP from outside the cluster to services, usually with TLS termination. It needs an ingress controller; the object alone does nothing.

**ConfigMap** holds non-secret configuration. **Secret** holds sensitive configuration, but by default it is only base64-encoded, not encrypted. Enable encryption at rest, restrict read access with RBAC, and prefer an external secret manager for production. A Secret in a Git manifest is a credential in Git.

**HorizontalPodAutoscaler** changes the replica count from a metric. **PodDisruptionBudget** limits how many pods can be voluntarily evicted at once (node drain, cluster upgrade). It does not protect against a crash or a bad rollout; it protects against planned disruption.

**Job** and **CronJob** run finite work, such as a nightly training job. **StatefulSet** gives stable identities and storage for databases and other stateful systems; a prediction API should not need it.

## 4. Probes: three different questions

Kubernetes can ask a container three questions:

| Probe | Question | Failure action | Use it for |
|---|---|---|---|
| **Readiness** | Can this pod serve traffic now? | Remove from Service endpoints; do not restart | Model loaded, dependencies reachable |
| **Liveness** | Is this process stuck in a way a restart fixes? | Restart the container | Deadlock, unrecoverable internal state |
| **Startup** | Has initialisation finished? | Keep other probes disabled until it passes; restart after the budget | Slow model load, migrations |

The ETA service's `/health` answers "the process is running"; `/ready` answers "the model is loaded". Readiness should use `/ready`; liveness should use `/health`. If liveness uses `/ready` and the model store is temporarily unavailable, Kubernetes will restart a healthy process repeatedly, which makes the outage worse.

Thresholds matter. A readiness probe with `periodSeconds: 1` and `failureThreshold: 1` removes a pod for a single slow request. A liveness probe with a 60-second timeout hides a hang. Start with a readiness probe every 5 seconds, three failures; a liveness probe every 10 seconds, three failures; and a startup probe that allows the observed cold start with margin. Measure the cold start (Module 10) rather than guessing.

A probe endpoint should be cheap and should not depend on downstream services unless that dependency genuinely makes the pod unable to serve. A readiness probe that checks the database can remove every pod during a database blip, turning a partial degradation into a full outage.

## 5. Requests, limits, and QoS

A **request** is what the scheduler reserves for the container. A **limit** is the ceiling the runtime enforces.

- CPU above the limit is **throttled**. The process runs slower; it does not usually crash.
- Memory above the limit is **OOM-killed**. The container restarts, often in a loop.
- A container with no requests is scheduled as if it needs nothing, which lets a node be oversubscribed.
- A container with requests far above its need wastes capacity and money.

Kubernetes assigns a **QoS class**:

| Class | Condition | Eviction priority |
|---|---|---|
| Guaranteed | Requests equal limits for every container | Last |
| Burstable | At least one request, not Guaranteed | Middle |
| BestEffort | No requests or limits | First |

Set requests from measurement: run the service, observe CPU and memory under expected load, add headroom. Set memory limits above the observed peak, not at the average. A limit equal to the average guarantees an OOM kill on a busy day.

## 6. Scaling: more replicas is not the only axis

**Horizontal** scaling adds pods (HPA). **Vertical** scaling gives a pod more CPU or memory (VPA, or a larger node). **Cluster** scaling adds nodes (Cluster Autoscaler, Karpenter, provider equivalent). They interact: an HPA that wants ten pods cannot help if the cluster has no room, and a cluster autoscaler cannot help if the pods' requests are too large to fit.

An HPA needs a metric that correlates with load. CPU utilization is common but misleading for I/O-bound services; requests per second, queue depth, or concurrency are often better. The HPA's `averageUtilization` is a percentage of the **request**, not of the node. If the request is wrong, the scaling rule is wrong.

Two cautions:

- **Scale-to-zero** is not what a plain HPA does; `minReplicas: 0` requires an event-driven autoscaler or a platform feature. A prediction API usually keeps at least two replicas for availability.
- **Autoscaling does not reduce cost by itself.** If nodes stay provisioned, fewer pods do not refund the node. Cost reduction comes from cluster autoscaling, bin packing, or a platform that bills per request.

## 7. Rollouts, availability, and rollback

A Deployment's default strategy is `RollingUpdate`. It creates new pods and removes old ones according to `maxSurge` (how many extra pods may exist) and `maxUnavailable` (how many may be unavailable).

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0
    maxSurge: 1
```

`maxUnavailable: 0` means Kubernetes will not remove an old pod until a new one is ready. It does **not** guarantee zero downtime: if the readiness probe is wrong, if the new pods cannot start, or if the service has no spare capacity, users still see errors. Zero downtime requires:

1. at least two replicas, spread across failure domains;
2. a readiness probe that only passes when the pod can serve;
3. a rollout that keeps capacity (`maxUnavailable: 0` or a canary);
4. graceful shutdown that drains in-flight requests;
5. a database schema that is compatible with both versions during the rollout.

Rollback is `kubectl rollout undo deployment/raviride-eta -n raviride`. It is fast only if the previous ReplicaSet still exists and the image is still pullable. Record the image digest of the previous version; a rollback to a tag that has been overwritten is not a rollback.

Database migrations are the hard part. A migration that drops a column cannot be undone by rolling back the Deployment. Use expand-and-contract: add the new column, deploy code that writes both, backfill, switch reads, then remove the old column in a later release.

## 8. Infrastructure as code

Infrastructure as code (IaC) makes the environment reviewable and reproducible. Terraform (source-available) and OpenTofu (open-source fork) are common choices; cloud-native tools and Kubernetes manifests with Kustomize or Helm are others.

The **state file** maps declared resources to real ones. It can contain sensitive values, so it belongs in an encrypted, access-controlled backend with locking, not in Git. `terraform plan` is the review artifact: it shows what will change before it changes. `apply` without a plan review is how a staging change becomes a production incident.

Drift is the difference between the state and reality. Someone edits a console, a controller changes a default, or a resource is deleted manually. Detect drift with a scheduled plan and decide whether to reconcile or accept it. An accepted drift is a configuration change that nobody reviewed.

## 9. Reliability: SLOs, error budgets, and failure domains

A **service-level indicator** (SLI) is a measurement: the share of requests with status < 500 and latency under 300 ms. A **service-level objective** (SLO) is a target over a window: 99.5% over 30 days. An **error budget** is what the target allows: 0.5% of requests, or about 3.6 hours of full outage in 30 days.

The budget turns reliability into a decision:

- budget remaining → ship features, run experiments;
- budget exhausted → freeze risky changes, fix reliability;
- budget consistently under-used → the target may be too loose, or the service is over-provisioned.

Reliability engineering is also about **failure domains**. Two replicas on the same node are one failure domain. Use topology spread constraints or anti-affinity across nodes and zones. A readiness probe that depends on a shared database is a shared failure domain; decide deliberately.

Retries need a budget and jitter, or they amplify an outage. Timeouts must be shorter than the caller's timeout. Idempotency keys make retries safe for writes. A circuit breaker protects a caller from a failing dependency; it does not fix the dependency.

## 10. Security in a shared cluster

The cluster is a multi-tenant system even when you think it is not. Minimum controls:

- **RBAC**: namespace-scoped roles, no cluster-admin for application teams, no default service-account tokens unless needed.
- **Network policy**: default-deny ingress, allow only the service ports that are required. Not all CNIs enforce it; verify.
- **Pod security**: non-root, no privilege escalation, read-only root filesystem, dropped capabilities, seccomp profile.
- **Image provenance**: scan images, pin digests, admit only signed images where the platform supports it.
- **Secrets**: external secret manager or encrypted secrets, not base64 in Git; rotate.
- **Admission policy**: reject `latest`, missing limits, or hostPath mounts at the API boundary, so a mistake fails before it runs.

The manifests in this module apply the pod-level controls. They do not configure RBAC, network policy, or admission; those are cluster-level and are named in the production checklist as owner work.

## 11. Cost: the bill is made of requests and time

A useful estimate has four parts:

1. **Compute**: nodes or platform instances × hours × price. Requests determine how many pods fit per node; over-requesting wastes capacity.
2. **Storage**: images, logs, model artifacts, backups, and the registry. Logs are usually larger than people expect.
3. **Network**: egress to users and between zones; cross-zone traffic can be billed.
4. **Managed services**: load balancers, NAT gateways, monitoring, and secret stores often have a fixed monthly charge that dominates a small deployment.

Write the assumptions down: requests per second, average latency, replicas, node size, hours per month, and the price source and date. Give a range, and say which assumption would change the answer most. A cost estimate without assumptions is a number that cannot be checked.

## 12. What to do when you cannot run a cluster

The learning outcomes are about decisions, not `kubectl` muscle memory. If Docker or `kind` is unavailable:

- review the manifests against the 35 checks in the kit;
- trace a rollout on paper, including the readiness gate and the rollback;
- write the abort criteria and the cost worksheet;
- explain what each probe and limit prevents;
- record the limitation in your evidence.

That is a legitimate path through the module. Claiming you deployed when you did not is not.
