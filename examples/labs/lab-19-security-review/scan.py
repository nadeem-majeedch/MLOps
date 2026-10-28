"""Scan the mini deployment for the classes of problem a reviewer must catch.

    python scan.py --root app --json artifacts/scan.json

This is a candidate finder, not a verdict. It prints a redacted excerpt so no
secret is copied into your report or into this terminal history. Deciding
severity, impact and mitigation is your job; the scanner cannot know whether a
key is live, whether an email is a test fixture, or whether a log is retained
for a week or five years.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", ".venv"}

RULES = [
    ("hardcoded_secret",
     re.compile(r"(?i)[A-Za-z0-9_]*(?:api_?key|secret|token|password)[A-Za-z0-9_]*\s*=\s*[\"'][^\"']{6,}[\"']"),
     {".py", ".yaml", ".yml", ".toml", ".ini", ".json"}),
    ("secret_in_ci", re.compile(r"\$\{\{\s*secrets\."), {".yml", ".yaml"}),
    ("broad_permissions", re.compile(r"permissions:\s*write-all"), {".yml", ".yaml"}),
    ("unpinned_action", re.compile(r"uses:\s*[\w.-]+/[\w.-]+@(main|master)\b"), {".yml", ".yaml"}),
    ("unpinned_dependency", re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*\s*$"), {"requirements.txt"}),
    ("pii_email", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), {".log", ".csv", ".py"}),
    ("pii_date_of_birth", re.compile(r"\b(19|20)\d{2}-\d{2}-\d{2}\b"), {".log", ".csv"}),
]


@dataclass
class Finding:
    rule: str
    file: str
    line: int
    excerpt: str


def redact(text: str) -> str:
    """Keep enough to locate the problem, not enough to reuse the value."""
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "<email>", text)
    text = re.sub(r"\b(19|20)\d{2}-\d{2}-\d{2}\b", "<date>", text)
    # Only mask credential-shaped values; masking every quoted string hides the
    # evidence the reviewer needs.
    text = re.sub(r"sk_[A-Za-z0-9_]+", "<redacted-key>", text)
    text = re.sub(r"(?i)(password|secret|token|api_?key)\s*=\s*[\"'][^\"']+[\"']", r'\1="<redacted>"', text)
    return text.strip()[:130]


def scan(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        suffixes = {path.suffix, path.name}
        for rule, pattern, targets in RULES:
            if not (suffixes & targets):
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if pattern.search(line):
                    findings.append(Finding(rule, str(path.relative_to(root)), number, redact(line)))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("app"))
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    findings = scan(args.root)
    payload = [finding.__dict__ for finding in findings]
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"{'rule':<22}{'file':<28}{'line':<6}excerpt")
    for finding in findings:
        print(f"{finding.rule:<22}{finding.file:<28}{finding.line:<6}{finding.excerpt}")
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.rule] = counts.get(finding.rule, 0) + 1
    print(f"\n{len(findings)} candidates: " + ", ".join(f"{rule}={count}" for rule, count in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
