# Troubleshooting · Module 16

## Diagnose in this order

1. **Is the object accepted?** `kubectl apply` errors, schema versions, admission policy.
2. **Is the pod scheduled?** `Pending` means capacity, taints, affinity, or quotas.
3. **Does the image start?** `ImagePullBackOff`, `CrashLoopBackOff`, logs.
4. **Is the pod ready?** Probe path, port, thresholds, startup budget.
5. **Is it in the Service?** Selector, endpoints, target port.
6. **Is it reachable?** Ingress, network policy, DNS, TLS.
7. **Is it healthy under load?** Requests, limits, HPA, node pressure.

## Failure table

| Symptom | Likely cause | Fix |
|---|---|---|
| `Pending` pods | Insufficient CPU/memory, taint, affinity, or quota | `kubectl describe pod` events; reduce requests or add capacity |
| `ImagePullBackOff` | Wrong tag, private registry, or image not loaded into kind | Correct the reference; add an image pull secret; `kind load docker-image` |
| `CrashLoopBackOff` | Missing config, read-only filesystem, model missing, OOM | `kubectl logs --previous`; add `emptyDir`; check limits and the image contents |
| `Running` but not ready | Probe path/port wrong, model still loading, dependency down | Port-forward and call the probe path; check the startup budget |
| Service has no endpoints | Selector does not match pod labels, or pods are not ready | Compare labels; `kubectl get endpoints` |
| Connection refused through the Service | `targetPort` does not match the container port | Align the numbers or use the named port |
| HPA shows `<unknown>` | Metrics server missing | Install metrics-server; note it as unverified otherwise |
| HPA does not scale | At min/max, no metrics, or the request is missing | Check bounds, metrics, and the CPU request |
| Rollout stalls | New pods never ready; `maxUnavailable: 0` keeps old pods | Inspect new pods; fix readiness; `rollout undo` |
| Rollback does not fix it | Destructive migration, config drift, or a dependency change | Restore the data/config too; a Deployment rollback is not a system rollback |
| Node drain blocks | PDB `minAvailable` equals replicas | Lower the PDB or add replicas |
| Cost higher than expected | Over-requested CPU, idle nodes, egress, or fixed add-ons | Compare requests to usage; right-size; check the bill's line items |

## Case 1: healthy pods, no traffic

The pods are `Running` and `Ready`, the Deployment is available, and users get connection errors.

Check, in order:

```bash
kubectl -n raviride get pods --show-labels
kubectl -n raviride get svc raviride-eta -o yaml
kubectl -n raviride get endpoints raviride-eta
```

If the endpoints list is empty, the selector does not match the pod labels, or the readiness probe is failing. If the endpoints exist, compare `targetPort` with `containerPort`. If both are correct, check the ingress, network policy, and DNS.

The most common cause is a copy-paste label change on the Deployment that was not mirrored in the Service selector. The second is a port number that was correct in Docker Compose and wrong in Kubernetes.

## Case 2: the probe that restarts a healthy service

A liveness probe points at `/ready`, which checks the model store. The model store has a 30-second blip. Every pod fails liveness, restarts, and takes longer to load than the probe's grace period. The service goes down for ten minutes because a dependency was briefly slow.

Fix:

- liveness should check the process, not its dependencies: `/health`;
- readiness should check the model, and a temporary failure should remove the pod from endpoints without restarting it;
- add a startup probe so a slow initial load does not count as a liveness failure;
- tune thresholds from measured cold start, not from a template.

A probe is a control with a failure mode. Ask what happens when it is wrong.

## Case 3: the rollout that will not finish

`kubectl rollout status` hangs, old pods keep serving, and the new ReplicaSet has pods that are not ready.

That is the strategy working: `maxUnavailable: 0` refuses to remove capacity while the new pods cannot serve. Do not "fix" it by setting `maxUnavailable: 1` until you know why the new pods are not ready. Inspect:

```bash
kubectl -n raviride describe pod <new-pod>
kubectl -n raviride logs <new-pod>
kubectl -n raviride get events --sort-by=.lastTimestamp
```

Common causes: the image lacks the model artifact, the readiness path changed, the model store is unreachable, the container writes to a read-only filesystem, or the startup budget is too short. Fix the cause, then let the rollout continue or undo it.

## Case 4: the HPA that scales the wrong thing

CPU utilization is high, but the service is I/O-bound and latency is fine. Or CPU is low, but requests queue because the worker pool is saturated.

CPU is a proxy for load, not load itself. Use a metric that tracks the bottleneck: requests per second, concurrent requests, queue depth, or latency. If you keep CPU, set the request from measurement; utilization is a percentage of the request, so an inflated request hides saturation.

Also check that the cluster can place the new pods. An HPA that wants five replicas on a cluster with room for two will leave two `Pending`.

## Case 5: the rollback that rolls back the wrong thing

`kubectl rollout undo` restores the pod template. It does not:

- reverse a database migration;
- restore a ConfigMap or Secret changed outside the Deployment;
- revert an ingress or DNS change;
- restore data deleted by the new version;
- pull an image that has been overwritten.

For a release with a migration, use expand-and-contract and keep the old code compatible with the new schema for at least one release. For configuration, version it with the Deployment and roll it back together. For data, restore from backup and accept that some writes may be lost; say so in the incident record.

## Case 6: the bill nobody expected

A small service with two replicas should not cost a large sum. Check:

- **Requests**: 1 CPU per pod when the service uses 50m wastes capacity and nodes.
- **Fixed charges**: load balancers, NAT gateways, log storage, and monitoring can dominate.
- **Egress**: cross-zone traffic and external responses are often billed.
- **Idle capacity**: autoscaling pods does not shrink nodes unless cluster autoscaling is enabled.
- **Retention**: logs and artifacts kept forever.

Write the assumptions and the price date. A cost estimate that cannot be reproduced is not a budget.

## When to stop and ask for help

Escalate when:

- a production namespace has no owner and no quota;
- a cluster-admin credential is needed to fix an application problem;
- a rollback would require deleting data;
- the provider's quota blocks the release and the cost is unclear;
- a security control (network policy, admission, RBAC) is being disabled to make a deployment pass.

The last one is not a troubleshooting step; it is a decision that needs an owner and a record.
