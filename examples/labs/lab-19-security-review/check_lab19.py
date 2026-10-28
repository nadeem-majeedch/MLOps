"""Acceptance check for Lab 19.

    python check_lab19.py [--findings findings.yaml] [--card model-card.md]

The scanner supplies candidates; the review supplies judgement. Both are
checked, because a scanner run pasted into a report is not a review.
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

REQUIRED_SECTIONS = ["Intended use", "Data", "Model and evaluation", "Limitations",
                     "Ethical considerations", "Privacy and retention", "Monitoring and rollback"]


def section_body(text: str, heading: str) -> str:
    marker = f"## {heading}"
    if marker not in text:
        return ""
    body = text.split(marker, 1)[1]
    return body.split("\n## ", 1)[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--findings", default="findings.yaml")
    parser.add_argument("--card", default="model-card.md")
    args = parser.parse_args()
    lab = Lab("L19", "Review a deployment for security and privacy risk")

    scan_out = ROOT / "artifacts/scan.json"
    scanned = subprocess.run([sys.executable, "scan.py", "--root", "app", "--json", str(scan_out)],
                             cwd=ROOT, capture_output=True, text=True)
    lab.check("the scanner runs", scanned.returncode == 0 and scan_out.exists(),
              (scanned.stderr.strip().splitlines() or [""])[-1])
    candidates = json.loads(scan_out.read_text(encoding="utf-8")) if scan_out.exists() else []
    rules = {row["rule"] for row in candidates}
    for rule in ("hardcoded_secret", "pii_email", "secret_in_ci", "broad_permissions", "unpinned_dependency"):
        lab.check(f"the scanner surfaces {rule}", rule in rules, f"found {sorted(rules)}")
    secrets_found = sum(1 for row in candidates if row["rule"] == "hardcoded_secret")
    lab.check("both committed credentials are flagged", secrets_found >= 2, f"{secrets_found} secret matches")
    lab.check("no unredacted credential appears in the scan output",
              "sk_test_FAKE_do_not_use_1234567890" not in scan_out.read_text(encoding="utf-8"), "redacted")

    findings_path = ROOT / args.findings
    if not lab.check("findings.yaml exists", findings_path.exists(), str(findings_path)):
        return lab.finish()
    findings = yaml.safe_load(findings_path.read_text(encoding="utf-8")) or {}
    rows = findings.get("findings") or []
    lab.check("at least five distinct findings are recorded", len(rows) >= 5, f"{len(rows)} findings")

    severities = [str(row.get("severity", "")).lower() for row in rows]
    lab.check("severities use the agreed scale", all(s in {"high", "medium", "low"} for s in severities), str(severities))
    lab.check("at least three findings are rated high", severities.count("high") >= 3, f"{severities.count('high')} high")

    files = " ".join(str(row.get("file", "")) for row in rows)
    for target in ("config.py", "service.log", "deploy.yml"):
        lab.check(f"the review covers {target}", target in files, files[:90])

    for row in rows:
        identifier = row.get("id", "?")
        lab.check(f"{identifier} explains impact", len(str(row.get("impact", ""))) > 25, str(row.get("impact"))[:60])
        lab.check(f"{identifier} proposes a verifiable mitigation",
                  len(str(row.get("mitigation", ""))) > 40 and "TODO" not in str(row.get("mitigation")),
                  str(row.get("mitigation"))[:60])

    card_path = ROOT / args.card
    if not lab.check("the model card exists", card_path.exists(), str(card_path)):
        return lab.finish()
    card = card_path.read_text(encoding="utf-8")
    for heading in REQUIRED_SECTIONS:
        body = section_body(card, heading).strip()
        lab.check(f"the card has a filled '{heading}' section", len(body) > 40 and "TODO" not in body,
                  f"{len(body)} characters")

    limitations = section_body(card, "Limitations")
    lab.check("at least three specific limitations are named",
              sum(1 for line in limitations.splitlines() if line.strip().startswith("-")) >= 3,
              f"{sum(1 for line in limitations.splitlines() if line.strip().startswith('-'))} bullets")
    privacy = section_body(card, "Privacy and retention").lower()
    lab.check("the card states what is never logged", "never" in privacy and "log" in privacy, privacy[:80])
    intended = section_body(card, "Intended use").lower()
    lab.check("the card names a prohibited use", any(word in intended for word in ("must not", "not be used", "prohibit")),
              intended[:90])

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
