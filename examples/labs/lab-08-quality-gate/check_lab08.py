"""Acceptance check for Lab 08.

    python check_lab08.py [--gate gate.py]

Six candidates, five rules, and one that must pass. A gate that blocks
everything is as useless as one that blocks nothing.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402

CHAMPION = "candidates/baseline_v1.json"
CASES = {
    "candidates/deeper_v2.json": ("pass", set(), 0),
    "candidates/shallow_v3.json": ("block", {"absolute_ceiling", "overall_regression"}, 1),
    "candidates/no_z08_v5.json": ("block", {"dropped_zone"}, 1),
    "candidates/zone_regression_v6.json": ("block", {"zone_limit"}, 1),
    "candidates/missing_slice_v7.json": ("block", {"missing_slice"}, 1),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", default="gate.py")
    args = parser.parse_args()
    lab = Lab("L08", "Block a model that fails the quality policy")
    gate = (ROOT / args.gate).resolve()

    for candidate, (decision, rules, code) in CASES.items():
        out = ROOT / "artifacts" / (Path(candidate).stem + ".json")
        proc = subprocess.run(
            [sys.executable, str(gate), "--candidate", candidate, "--champion", CHAMPION, "--json", str(out)],
            cwd=ROOT, capture_output=True, text=True,
        )
        lab.equal(f"{Path(candidate).stem} exits {code}", proc.returncode, code)
        if not out.exists():
            lab.fail(f"{Path(candidate).stem} writes a verdict", (proc.stderr.strip().splitlines() or [""])[-1])
            continue
        verdict = json.loads(out.read_text(encoding="utf-8"))
        lab.equal(f"{Path(candidate).stem} decision", verdict.get("decision"), decision)
        found = {reason.get("rule") for reason in verdict.get("reasons", [])}
        for rule in rules:
            lab.check(f"{Path(candidate).stem} names {rule}", rule in found, f"reasons: {sorted(found)}")
        if decision == "pass":
            lab.equal(f"{Path(candidate).stem} has no reasons", verdict.get("reasons"), [])
        else:
            lab.check(f"{Path(candidate).stem} explains every block with a number",
                      all(any(ch.isdigit() for ch in r.get("detail", "")) for r in verdict["reasons"]),
                      str(verdict["reasons"])[:120])

    lab.check("zone_regression improves overall MAE but is still blocked",
              json.loads((ROOT / "artifacts/zone_regression_v6.json").read_text(encoding="utf-8"))["decision"]
              == "block" if (ROOT / "artifacts/zone_regression_v6.json").exists() else False,
              "overall improvement is not a licence to hurt a zone")

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
