"""Validate the Kubernetes manifests without a cluster.

    python check_manifests.py                 # validates starter/ (expected to fail)
    python check_manifests.py --dir solution  # reference; all checks pass

This checks the properties that cause most first-deployment failures: a mismatched
service port, a missing readiness probe, no resource limits, a latest tag, a
container running as root, a plaintext secret, and a rollout strategy that can
take the service down. It cannot check scheduling, image pull, cluster policy, or
actual behaviour under load. If kubectl is installed, README.md shows the
server-side dry run and the kind exercise.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - the lab environment installs PyYAML
    print("PyYAML is required: python -m pip install pyyaml")
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent
REQUIRED_FILES = ["deployment.yaml", "service.yaml", "configmap.yaml", "hpa.yaml", "pdb.yaml"]
NAMESPACE = "raviride"
IMAGE_PORT = 8000

results: list[tuple[bool, str, str]] = []


def check(ok: bool, name: str, detail: str = "") -> None:
    results.append((bool(ok), name, detail))


def load(directory: Path) -> list[dict]:
    documents = []
    for path in sorted(directory.glob("*.yaml")):
        try:
            loaded = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
        except yaml.YAMLError as exc:
            check(False, "YAML parses", f"{path.name}: {exc}")
            continue
        documents.extend(item for item in loaded if isinstance(item, dict))
    return documents


def by_kind(documents: list[dict], kind: str) -> dict:
    for item in documents:
        if item.get("kind") == kind:
            return item
    return {}


def dig(mapping: object, *keys: str, default: object = None) -> object:
    current = mapping
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def containers(deployment: dict) -> list[dict]:
    value = dig(deployment, "spec", "template", "spec", "containers", default=[])
    return value if isinstance(value, list) else []


def probe(deployment: dict, name: str) -> dict:
    for container in containers(deployment):
        value = container.get(name)
        if isinstance(value, dict):
            return value
    return {}


def service_targets(service: dict, deployment: dict) -> tuple[bool, bool]:
    """Return (selector matches, target port resolves)."""
    selector = service.get("spec", {}).get("selector", {})
    labels = dig(deployment, "spec", "template", "metadata", "labels", default={})
    selector_ok = bool(selector) and all(labels.get(key) == value for key, value in selector.items())

    ports = service.get("spec", {}).get("ports", [])
    target = ports[0].get("targetPort") if ports else None
    pod_ports = [
        port for container in containers(deployment) for port in container.get("ports", [])
    ]
    numeric = {port.get("containerPort") for port in pod_ports}
    named = {port.get("name"): port.get("containerPort") for port in pod_ports}
    if isinstance(target, int):
        port_ok = target in numeric
    elif isinstance(target, str):
        port_ok = target in named
    else:
        port_ok = False
    return selector_ok, port_ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", type=Path, default=ROOT / "starter")
    args = parser.parse_args()
    directory = args.dir if args.dir.is_absolute() else ROOT / args.dir

    missing = [name for name in REQUIRED_FILES if not (directory / name).is_file()]
    check(not missing, "required files are present", f"missing: {', '.join(missing)}" if missing else "5 files")

    documents = load(directory)
    check(bool(documents), "manifests parse", f"{len(documents)} documents")

    deployment = by_kind(documents, "Deployment")
    service = by_kind(documents, "Service")
    configmap = by_kind(documents, "ConfigMap")
    hpa = by_kind(documents, "HorizontalPodAutoscaler")
    pdb = by_kind(documents, "PodDisruptionBudget")

    for kind, document in [
        ("Deployment", deployment),
        ("Service", service),
        ("ConfigMap", configmap),
        ("HorizontalPodAutoscaler", hpa),
        ("PodDisruptionBudget", pdb),
    ]:
        check(bool(document), f"{kind} exists")
        if document:
            check(
                dig(document, "metadata", "namespace") == NAMESPACE,
                f"{kind} uses the {NAMESPACE} namespace",
                str(dig(document, "metadata", "namespace")),
            )

    selector_ok, port_ok = service_targets(service, deployment) if service and deployment else (False, False)
    check(selector_ok, "Service selector matches the pod labels")
    check(port_ok, "Service targetPort resolves to a container port", "expected 8000")

    pod_labels = dig(deployment, "spec", "template", "metadata", "labels", default={})
    match_labels = dig(deployment, "spec", "selector", "matchLabels", default={})
    check(
        bool(match_labels) and all(pod_labels.get(key) == value for key, value in match_labels.items()),
        "Deployment selector matches the pod labels",
    )

    replicas = dig(deployment, "spec", "replicas", default=1)
    check(isinstance(replicas, int) and replicas >= 2, "at least two replicas", str(replicas))

    first = containers(deployment)[0] if containers(deployment) else {}
    image = str(first.get("image", ""))
    tag = image.rsplit(":", 1)[-1] if ":" in image.rsplit("/", 1)[-1] else ""
    check(bool(tag) and tag != "latest", "image is pinned to a version", image or "no image")
    check(
        first.get("imagePullPolicy") in {"IfNotPresent", "Always"},
        "imagePullPolicy is explicit",
        str(first.get("imagePullPolicy")),
    )

    ports = first.get("ports", [])
    check(
        any(port.get("containerPort") == IMAGE_PORT for port in ports),
        f"container listens on {IMAGE_PORT}",
    )

    readiness = probe(deployment, "readinessProbe")
    liveness = probe(deployment, "livenessProbe")
    startup = probe(deployment, "startupProbe")
    check(dig(readiness, "httpGet", "path") == "/ready", "readiness probe uses /ready")
    check(dig(liveness, "httpGet", "path") == "/health", "liveness probe uses /health")
    check(bool(startup), "startup probe is present")

    resources = first.get("resources", {})
    requests = resources.get("requests", {}) if isinstance(resources, dict) else {}
    limits = resources.get("limits", {}) if isinstance(resources, dict) else {}
    check(
        bool(requests.get("cpu")) and bool(requests.get("memory")),
        "CPU and memory requests are set",
    )
    check(
        bool(limits.get("cpu")) and bool(limits.get("memory")),
        "CPU and memory limits are set",
    )

    pod_security = dig(deployment, "spec", "template", "spec", "securityContext", default={})
    container_security = first.get("securityContext", {})
    check(pod_security.get("runAsNonRoot") is True, "pod runs as non-root")
    check(
        container_security.get("allowPrivilegeEscalation") is False,
        "privilege escalation is disabled",
    )
    check(
        container_security.get("readOnlyRootFilesystem") is True,
        "root filesystem is read-only",
    )
    drops = dig(container_security, "capabilities", "drop", default=[])
    check("ALL" in drops or "all" in drops, "all Linux capabilities are dropped")

    env = first.get("env", [])
    plaintext = [
        item.get("name")
        for item in env
        if isinstance(item, dict) and "value" in item and "KEY" in str(item.get("name", "")).upper()
    ]
    check(not plaintext, "no credential-shaped plaintext env value", ", ".join(plaintext))

    env_from = first.get("envFrom", [])
    referenced = [
        item.get("configMapRef", {}).get("name")
        for item in env_from
        if isinstance(item, dict) and item.get("configMapRef")
    ]
    check(
        bool(configmap) and dig(configmap, "metadata", "name") in referenced,
        "ConfigMap is consumed by the deployment",
    )

    strategy = dig(deployment, "spec", "strategy", "type")
    max_unavailable = dig(deployment, "spec", "strategy", "rollingUpdate", "maxUnavailable")
    check(strategy == "RollingUpdate", "rollout strategy is RollingUpdate", str(strategy))
    check(max_unavailable in {0, "0"}, "rollout keeps capacity during an update", str(max_unavailable))

    minimum = dig(hpa, "spec", "minReplicas", default=0)
    maximum = dig(hpa, "spec", "maxReplicas", default=0)
    check(
        isinstance(minimum, int) and isinstance(maximum, int) and minimum >= 2 and maximum > minimum,
        "HPA scales between at least two replicas",
        f"{minimum}..{maximum}",
    )
    check(
        dig(hpa, "spec", "scaleTargetRef", "name") == dig(deployment, "metadata", "name"),
        "HPA targets the deployment",
    )

    minimum_available = dig(pdb, "spec", "minAvailable", default=0)
    check(
        isinstance(minimum_available, int) and minimum_available >= 1,
        "PDB protects at least one pod",
        str(minimum_available),
    )

    passed = 0
    print(f"validating {directory}")
    print(f"{'result':<8}{'check':<52}detail")
    for ok, name, detail in results:
        print(f"{'PASS' if ok else 'FAIL':<8}{name:<52}{detail}")
        passed += ok
    failed = len(results) - passed
    print(f"\n{passed}/{len(results)} checks passed, {failed} failed")
    if failed:
        print("Fix the FAIL rows, then run again. A manifest that parses is not a manifest that works.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
