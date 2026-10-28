"""A local registry: versions, one alias, a gate, and a rollback.

This is a **local demonstration**, not a model registry service. It has no
concurrency control, no artifact storage, and no audit log beyond what the JSON
file happens to contain. Module 09 explains what a real registry (MLflow, for
example) adds: immutable versions, artifact lineage, alias history, and access
control.

What it does demonstrate, in about a page of code, is the rule that matters:
promotion is decided by a policy applied to recorded metrics, not by remembering
that the last run looked good.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ALIAS = "champion"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Registry:
    def __init__(self, root: str | Path = "artifacts/registry") -> None:
        self.root = Path(root)
        self.path = self.root / "registry.json"
        self.root.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(
                json.dumps({"versions": [], "aliases": {}}, indent=2) + "\n",
                encoding="utf-8",
            )

    def _read(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def versions(self) -> list[dict]:
        return self._read()["versions"]

    def champion(self) -> dict | None:
        data = self._read()
        version = data["aliases"].get(ALIAS)
        return next((v for v in data["versions"] if v["version"] == version), None)

    def register(self, meta: dict, artifact: str, note: str = "") -> dict:
        data = self._read()
        version = len(data["versions"]) + 1
        entry = {
            "version": version,
            "registered_at": _now(),
            "artifact": str(artifact),
            "note": note,
            "metrics": meta["metrics"],
            "model_sha256": meta.get("model_sha256"),
            "train_machines": meta.get("train_machines"),
            "params": meta.get("params"),
        }
        data["versions"].append(entry)
        self._write(data)
        return entry

    def decision(self, meta: dict, policy: dict) -> tuple[bool, list[str]]:
        """Apply the promotion policy to recorded metrics. Failure reasons are explicit."""
        metrics = meta["metrics"]
        reasons: list[str] = []
        if metrics["roc_auc"] < float(policy["min_roc_auc"]):
            reasons.append(
                f"roc_auc {metrics['roc_auc']:.4f} < required {policy['min_roc_auc']}"
            )
        if metrics["recall"] < float(policy["min_recall"]):
            reasons.append(
                f"recall {metrics['recall']:.4f} < required {policy['min_recall']}"
            )
        if metrics["precision"] < float(policy["min_precision"]):
            reasons.append(
                f"precision {metrics['precision']:.4f} < required {policy['min_precision']}"
            )
        return (not reasons, reasons)

    def promote(self, version: int | None = None) -> dict:
        data = self._read()
        if not data["versions"]:
            raise ValueError("nothing is registered yet")
        target = version or data["versions"][-1]["version"]
        if not any(v["version"] == target for v in data["versions"]):
            raise ValueError(f"version {target} does not exist")
        data["aliases"][ALIAS] = target
        self._write(data)
        return next(v for v in data["versions"] if v["version"] == target)

    def rollback(self) -> dict:
        """Point the alias at the highest numbered version below the current one."""
        data = self._read()
        current = data["aliases"].get(ALIAS)
        if current is None:
            raise ValueError("there is no champion to roll back from")
        candidates = [v["version"] for v in data["versions"] if v["version"] < current]
        if not candidates:
            raise ValueError(f"version {current} is the oldest; there is nothing to roll back to")
        data["aliases"][ALIAS] = max(candidates)
        self._write(data)
        return next(v for v in data["versions"] if v["version"] == data["aliases"][ALIAS])
