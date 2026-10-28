# Guided lab · Repair the manifests, then deploy if you can

**Time:** 6 hours (4 hours without a cluster). **Tools:** Python 3.11/3.12 and PyYAML for the checker; optional Docker, `kind`, and `kubectl` for the live exercise. **Resources:** the live exercise needs about 8 GB RAM and 10 GB disk. No cloud account.

## Scenario and business problem

RaviRide's ETA API has run on a developer's laptop for three months. Operations wants it on the shared platform next week. The first manifest draft was written in an afternoon and "works" because the developer tested one pod with `kubectl port-forward`.

The platform team's review found 24 problems. Your job is to fix the manifests, explain what each defect would do in production, and produce a rollout plan with abort criteria. If you have a local cluster, you also deploy it and record the evidence; if you do not, you say so and stop at the static review.

### Skills practised

- Reading a Deployment, Service, ConfigMap, HPA, and PDB as one system.
- Choosing probes and thresholds from measured behaviour.
- Setting requests and limits that match the service.
- Applying pod-level security controls.
- Planning a rollout with signals and a rollback.
- Writing a cost estimate with assumptions.

### Prerequisites

Module 11 (a built image) and Module 14 (a monitored service). The checker needs PyYAML. The optional live exercise needs Docker and `kind`; if `kind` is unavailable, `minikube` or a managed cluster works, but the commands differ.

### Input data

No dataset. The inputs are the manifests in `examples/modules/16-kubernetes/starter/` and the service contract from Module 10:

| Endpoint | Purpose | Probe |
|---|---|---|
| `GET /health` | Process is alive | Liveness |
| `GET /ready` | Model is loaded | Readiness |
| `POST /predict` | Prediction | Not a probe |

### Directory layout

```text
examples/modules/16-kubernetes/
├── starter/              # 24 defects; do not deploy
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── hpa.yaml
│   └── pdb.yaml
├── solution/             # reference; 35/35 checks
├── check_manifests.py
└── README.md
```

Work in a copy of `starter/`, for example `work/`. Keep `solution/` closed until you have attempted the repair.

## Part 1: see the failures (30 minutes)

1. Run the checker on the starter:

   ```bash
   cd examples/modules/16-kubernetes
   python check_manifests.py --dir starter
   ```

   PowerShell is identical.

   Expected: `11/35 checks passed, 24 failed`. Read every FAIL row before changing anything.

2. Group the failures by consequence: outage, unsafe, unmaintainable. Write the three groups in your notes.
3. Answer before fixing: which single defect would cause the most user-visible harm, and which would be hardest to notice in a green `kubectl get pods`?

**Checkpoint 1:** you can explain the port mismatch and the `Recreate` strategy without looking at the solution.

## Part 2: make it serve (60 minutes)

4. Create `work/` and copy the five starter files into it.
5. Move every object to the `raviride` namespace. Keep the labels consistent across the Deployment selector, pod template, Service selector, HPA target, and PDB selector.
6. Fix the Service `targetPort` so it resolves to the container's port 8000. Prefer the named port `http` if you name the container port.
7. Set `replicas: 2`, `strategy: RollingUpdate`, `maxUnavailable: 0`, `maxSurge: 1`.
8. Add a readiness probe on `/ready` (period 5 s, failure threshold 3) and a liveness probe on `/health` (period 10 s, failure threshold 3). Add a startup probe with a budget larger than the measured cold start.
9. Run the checker on `work/`. Expect the serving-related failures to disappear.

**Checkpoint 2:** the Service resolves to the container port and the rollout keeps capacity.

*Recovery:* if the checker still reports the port failure, confirm the `containerPort` and the Service `targetPort` are both 8000 or both use the same port name. A string `targetPort` must match a named container port exactly.

## Part 3: make it safe and sized (75 minutes)

10. Pin the image to `raviride-eta:1.0.0` and set `imagePullPolicy: IfNotPresent`.
11. Add CPU and memory requests and limits. Use 100m/256Mi requests and 500m/512Mi limits as a starting point, then justify them from the Module 10 latency measurement or a local load test.
12. Add the pod security context: `runAsNonRoot: true`, `runAsUser: 10001`, `seccompProfile: RuntimeDefault`.
13. Add the container security context: `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, drop `ALL` capabilities. Add an `emptyDir` at `/tmp` if the process needs a writable temporary directory.
14. Remove the plaintext `API_KEY`. Reference a Secret with `secretKeyRef`, and set `optional: true` only if the service truly works without it. Move non-secret settings into the ConfigMap and consume it with `envFrom`.
15. Run the checker. Expect only the rollout/scaling checks to remain.

**Checkpoint 3:** no credential-shaped plaintext value remains, and the container is non-root with a read-only root filesystem.

*Recovery:* if the app fails to start with a read-only filesystem, find what it writes. Logs belong on stdout; caches belong in an `emptyDir`; model artifacts belong in the image or a mounted read-only volume. Do not make the whole filesystem writable to hide the problem.

## Part 4: make it scale and survive disruption (45 minutes)

16. Set the HPA minimum to 2 and the maximum to at least 5. Choose a CPU target (70% is a starting point) and explain why it tracks load for this service.
17. Set the PDB `minAvailable: 1`. With two replicas, that permits one voluntary eviction at a time.
18. Run the checker on `work/`.

   Expected: `35/35 checks passed, 0 failed`.

19. Compare your `work/` with `solution/`. Note every difference; some are stylistic, some are functional. Explain which differences you would keep and why.

**Checkpoint 4:** the checker passes, and you can explain why `maxUnavailable: 0` is necessary but not sufficient for zero downtime.

## Part 5: optional live deployment (90 minutes, only if Docker and kind are installed)

Skip this part if the tools are unavailable; record the limitation in your evidence instead of claiming a deployment.

20. Create a local cluster and load the image:

    ```bash
    kind create cluster --name raviride
    docker build -t raviride-eta:1.0.0 ../../raviride
    kind load docker-image raviride-eta:1.0.0 --name raviride
    kubectl create namespace raviride
    kubectl apply -f work/
    ```

21. Watch the rollout:

    ```bash
    kubectl -n raviride get pods -w
    kubectl -n raviride rollout status deployment/raviride-eta
    ```

    Expected: two pods reach `Running` and `Ready`; the rollout completes without unavailable replicas.

22. Forward the service and test it:

    ```bash
    kubectl -n raviride port-forward svc/raviride-eta 8080:80
    curl http://127.0.0.1:8080/health
    curl http://127.0.0.1:8080/ready
    ```

    Expected: `{"status":"ok"}` and a readiness body naming the model.

23. Break the readiness probe on purpose: change the path to `/nope`, apply, and watch the rollout stall. A stalled rollout with old pods still serving is the correct behaviour — this is why `maxUnavailable: 0` matters. Restore the path.

24. Rehearse a rollback:

    ```bash
    kubectl -n raviride set image deployment/raviride-eta api=raviride-eta:9.9.9
    kubectl -n raviride rollout status deployment/raviride-eta --timeout=30s
    kubectl -n raviride rollout undo deployment/raviride-eta
    kubectl -n raviride rollout status deployment/raviride-eta
    ```

    Record the elapsed time from the failed rollout to the restored one. Note whether the rollout to a nonexistent tag created any pods (it should not have replaced the ready ones).

25. Delete the cluster:

    ```bash
    kind delete cluster --name raviride
    ```

**Checkpoint 5 (if run):** the rollout, the stalled readiness, and the rollback are each recorded with commands and output. If not run, the evidence says "not executed; Docker/kind unavailable" and the rest of the lab is complete.

## Part 6: rollout plan and cost (45 minutes)

26. Write a one-page rollout plan: the image change, the strategy, the readiness gate, the abort signals and thresholds, the rollback command, and the owner.
27. Write a cost worksheet with the assumptions from Concepts §11. Give a monthly range and name the assumption that would change it most.
28. Write a reliability memo with two SLOs, an error budget, and the first alert you would configure. State what the alert means and what the on-call person should do first.

**Checkpoint 6:** the rollout plan has measurable abort criteria; the cost worksheet has assumptions; the SLOs have a measurement source.

## Expected outputs

| Output | Reference value |
|---|---|
| Starter checker | 11/35 passed, 24 failed |
| Repaired checker | 35/35 passed, 0 failed |
| Image | `raviride-eta:1.0.0`, not `latest` |
| Replicas / HPA | 2 minimum, 5 maximum |
| Probes | `/ready` readiness, `/health` liveness and startup |
| Rollout | `RollingUpdate`, `maxUnavailable: 0`, `maxSurge: 1` |
| PDB | `minAvailable: 1` |
| Live deployment | Not run here; record your own output if you run it |

## Acceptance criteria

| # | Criterion | Passes when |
|---|---|---|
| 1 | Namespace | All five objects in `raviride` |
| 2 | Ports | Service target resolves to container port 8000 |
| 3 | Image | Pinned tag or digest; explicit pull policy |
| 4 | Availability | ≥ 2 replicas; PDB protects ≥ 1 |
| 5 | Probes | Readiness `/ready`, liveness `/health`, startup present |
| 6 | Resources | CPU and memory requests and limits set |
| 7 | Security | Non-root, no privilege escalation, read-only root, drop ALL |
| 8 | Secrets | No credential-shaped plaintext env value |
| 9 | Rollout | `RollingUpdate` with `maxUnavailable: 0` |
| 10 | Scaling | HPA min ≥ 2, max > min, targets the Deployment |
| 11 | Explanation | Each defect's consequence is written, not just fixed |
| 12 | Rollback | A command and a verification are documented |
| 13 | Cost | Assumptions and a range, with the sensitive driver named |
| 14 | Honesty | Live deployment marked run or not run, with evidence |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Service targetPort` still fails | Named port mismatch or a string vs int | Use the same name on the container port and the Service, or use 8000 in both |
| Pods `CrashLoopBackOff` | Read-only filesystem, missing model, or a missing env var | Read `kubectl logs`; add an `emptyDir` for temp files; check the image contains the model |
| Pods `Pending` | No node has the requested CPU/memory, or a taint | Reduce requests or add capacity; check `kubectl describe pod` events |
| Readiness never passes | Wrong path, wrong port, or the model is not loaded | Test `/ready` with a port-forward; check the startup budget |
| Rollout stalls | New pods are not ready; `maxUnavailable: 0` keeps old pods | Inspect the new pod; fix readiness; `rollout undo` if needed |
| HPA shows `<unknown>` | Metrics server is not installed | Install metrics-server, or note that the HPA is unverified in this cluster |
| `ImagePullBackOff` | Image not loaded into kind, or a private registry credential | `kind load docker-image`; check the image name and tag |
| Rollback does not restore | The previous ReplicaSet is gone, or the image tag moved | Use an image digest; keep the previous version pullable |
| PDB blocks a drain | `minAvailable` equals the replica count | Lower it to leave room for one eviction, or add replicas |
| Cost estimate feels arbitrary | No assumptions, or a price without a date | Write requests/sec, replicas, node size, hours, and price source/date |

## Reflection questions

1. Which defect would a green `kubectl get pods` hide, and why?
2. Why is a readiness probe a better fit than a liveness probe for "the model is still loading"?
3. What does `maxUnavailable: 0` guarantee, and what does it not guarantee?
4. If the HPA scales to five pods but the cluster has room for two, what happens, and which component should you fix?
5. When would you choose a managed platform over Kubernetes for this service?
6. What is the most sensitive assumption in your cost estimate, and how would you measure it?
7. Which control in the manifests is cluster-level rather than pod-level, and who owns it?

## Optional extension

Add a **canary** path: a second Deployment with one replica and a Service that splits traffic, or an ingress weight. Define the metric, the threshold, and the rollback before you start. Then simulate a bad canary by pointing it at an image that fails readiness and confirm that the stable deployment keeps serving.

A second extension: add a NetworkPolicy that denies all ingress except from the ingress controller to port 8000, and explain why applying it without an ingress controller would make the service unreachable.

## Cleanup

```bash
rm -rf examples/modules/16-kubernetes/work
kind delete cluster --name raviride      # only if you created it
docker image rm raviride-eta:1.0.0       # optional
```

PowerShell:

```powershell
Remove-Item examples/modules/16-kubernetes/work -Recurse -Force -ErrorAction SilentlyContinue
kind delete cluster --name raviride
docker image rm raviride-eta:1.0.0
```

Confirm the cluster is gone with `kind get clusters`. Do not delete a cluster you did not create.

## Checklist

- [ ] I ran the checker on the starter and read all 24 failures
- [ ] The repaired manifests pass 35/35
- [ ] Every defect has a written consequence, not just a fix
- [ ] The image is pinned and the pull policy is explicit
- [ ] Probes answer different questions and the thresholds are justified
- [ ] Requests and limits are set, with a measurement or a stated assumption
- [ ] The container is non-root, read-only, and drops capabilities
- [ ] The rollout has abort criteria and a rollback command
- [ ] The cost worksheet has assumptions, a range, and a date
- [ ] I marked the live deployment as run or not run, with evidence
