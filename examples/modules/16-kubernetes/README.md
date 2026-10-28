# Module 16 · Kubernetes manifest kit

A deliberately unsafe first draft (`starter/`) and a corrected reference
(`solution/`) for the ETA service. `check_manifests.py` validates both without a
cluster.

```bash
cd examples/modules/16-kubernetes
python check_manifests.py --dir starter     # 11/35, expected to fail
python check_manifests.py --dir solution    # 35/35, expected to pass
```

The checker covers the failures that account for most first deployments: a
service pointing at the wrong port, a `latest` image, one replica, no probes, no
resource limits, a container running as root with a writable filesystem, a
plaintext credential, a `Recreate` rollout, an autoscaler that cannot scale, and a
disruption budget that protects nothing.

## What the checker is not

It parses YAML and inspects fields. It does **not** prove that Kubernetes will
schedule the pods, pull the image, pass cluster policy, or keep the service up
under load. Those require a cluster. The authoring environment did not have
Docker, `kind`, or `kubectl`, so no manifest in this kit was applied to a live
cluster; the reference values are static-analysis results, and the module says so.

## Optional live exercise

If Docker and `kind` are installed:

```bash
kind create cluster --name raviride
docker build -t raviride-eta:1.0.0 ../../raviride
kind load docker-image raviride-eta:1.0.0 --name raviride
kubectl apply -f solution/
kubectl -n raviride get pods,svc,hpa,pdb
kubectl -n raviride port-forward svc/raviride-eta 8080:80
curl http://127.0.0.1:8080/health
```

PowerShell uses the same commands; `curl` is an alias for `Invoke-WebRequest` in
Windows PowerShell 5.1, so use `curl.exe` or `Invoke-RestMethod` if the output
looks wrong.

The image tag must match `solution/deployment.yaml`. The HPA needs a metrics
server; `kind` does not install one by default, so the HPA will show
`<unknown>` until you add one. That is expected, not a manifest failure.

Cleanup:

```bash
kind delete cluster --name raviride
```

This is optional. Nothing in the course requires a cluster, a cloud account, or a
credit card.
