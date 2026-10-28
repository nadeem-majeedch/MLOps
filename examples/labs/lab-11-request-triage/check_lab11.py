"""Acceptance check for Lab 11.

    python check_lab11.py [--triage triage.yaml]

Two things are checked: that the probe evidence matches the service, and that
the triage table classifies each ticket correctly and explains the cause.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402

EXPECTED = {
    "p01": (200, "ok", ["valid", "200"]),
    "p02": (422, "client", ["hours", "range", "less"]),
    "p03": (422, "client", ["prior_score", "100", "less"]),
    "p04": (422, "client", ["sleep_hours", "missing", "required"]),
    "p05": (200, "contract", ["extra", "ignored", "ignored field", "dropped", "not used", "no effect"]),
    "p06": (500, "service", ["zero", "division", "divide", "prior_score"]),
    "p07": (405, "client", ["method", "get", "not allowed"]),
    "p08": (404, "client", ["route", "not found", "unknown", "404"]),
    "p09": (422, "client", ["missing", "required", "hours"]),
    "p10": (422, "client", ["null", "none", "type", "missing"]),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--triage", default="triage.yaml")
    args = parser.parse_args()
    lab = Lab("L11", "Triage malformed requests")

    trained = subprocess.run([sys.executable, "make_model.py"], cwd=ROOT, capture_output=True, text=True)
    lab.check("the service artifact exists", trained.returncode == 0 and (ROOT / "models/model.joblib").exists(),
              (trained.stderr.strip().splitlines() or [""])[-1])

    probes = subprocess.run([sys.executable, "probes.py"], cwd=ROOT, capture_output=True, text=True)
    evidence_path = ROOT / "artifacts/probes.json"
    lab.check("probes.py runs and writes evidence", probes.returncode == 0 and evidence_path.exists(),
              (probes.stderr.strip().splitlines() or [""])[-1])
    if not evidence_path.exists():
        return lab.finish()

    evidence = {row["id"]: row["status"] for row in json.loads(evidence_path.read_text(encoding="utf-8"))}
    lab.equal("every probe was executed", sorted(evidence), sorted(EXPECTED))
    for probe_id, (status, _, _) in EXPECTED.items():
        lab.equal(f"{probe_id} status captured", evidence.get(probe_id), status)

    triage_path = ROOT / args.triage
    if not lab.check("triage.yaml exists", triage_path.exists(), str(triage_path)):
        return lab.finish()
    triage = yaml.safe_load(triage_path.read_text(encoding="utf-8")) or {}
    rows = {row["id"]: row for row in triage.get("tickets", []) if isinstance(row, dict) and row.get("id")}
    lab.equal("every ticket is triaged", sorted(rows), sorted(EXPECTED))

    for probe_id, (_, expected_class, keywords) in EXPECTED.items():
        row = rows.get(probe_id, {})
        lab.equal(f"{probe_id} classification", str(row.get("class", "")).strip().lower(), expected_class)
        cause = str(row.get("cause", "")).lower()
        lab.check(f"{probe_id} cause explains the behaviour", any(word in cause for word in keywords),
                  f"cause: {row.get('cause')}")

    lab.check("the fix names the failing operation rather than a file",
              isinstance(triage.get("first_fix"), str) and len(triage["first_fix"]) > 20
              and "TODO" not in triage["first_fix"], str(triage.get("first_fix"))[:90])

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
