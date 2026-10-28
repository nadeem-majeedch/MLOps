#!/usr/bin/env python3
"""Validate the course repository before a build or a pull request.

    python scripts/validate_course.py
    python scripts/validate_course.py --verbose
    python scripts/validate_course.py --skip-python

Checks, in order:

1. Every published page is in the MkDocs navigation, and every navigation target
   exists.
2. Every relative Markdown link and image resolves, including ``#anchors`` that
   point at headings in another page.
3. Every module 01-17 has the full page set, and no module is a stub.
4. The 20 lab pages carry the required student sections.
5. The root README follows the student-facing policy (overview, outcomes,
   audience, roadmap, links) and contains no build or environment commands.
6. The instructor details are present in the README and the About page.
7. Code fences are balanced.
8. Every tracked Python file compiles (syntax only, no imports executed).
9. The generated dataset manifest, if present, still matches its files.
10. No obvious credential pattern appears in the site, scripts, or workflows.
11. Workflow YAML parses, and every ``uses:`` reference is pinned to a version.

The script uses only the standard library, except that PyYAML is used when it is
installed (it is, in the documentation environment) to parse workflows. It does
not build the site: run ``mkdocs build --strict`` as well, because MkDocs
resolves links and navigation independently.

Exit codes: 0 all checks passed (warnings allowed), 1 at least one check failed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MKDOCS = ROOT / "mkdocs.yml"

# Kept in sync with `exclude_docs` in mkdocs.yml. Templates are authoring aids
# with placeholder paths; the audit is a historical record, not a site page.
EXCLUDED = {Path("templates"), Path("audit-phase-0.md")}

MODULE_PAGES = [
    "index.md",
    "learning-objectives.md",
    "concepts.md",
    "worked-example.md",
    "lab.md",
    "independent-challenge.md",
    "knowledge-check.md",
    "troubleshooting.md",
    "references.md",
]

LAB_HEADINGS = [
    "## Scenario",
    "## What you will be able to do",
    "## Prerequisites and setup",
    "## Your task",
    "## Data and starter files",
    "## Steps",
    "## Expected output",
    "## Acceptance criteria",
    "## Troubleshooting",
    "## Reflection questions",
    "## Optional extension",
    "## Cleanup",
    "## Checklist",
]

README_REQUIRED = [
    "## What this course is",
    "## What you will be able to do",
    "## Who this course is for",
    "## How the course is organised",
    "## How to study",
    "## About",
]

README_FORBIDDEN = [
    "python -m venv",
    "pip install",
    "mkdocs build",
    "mkdocs serve",
    "gh-deploy",
    "git push",
]

INSTRUCTOR = [
    "Engr. Dr. Muhammad Nadeem Majeed",
    "Professor",
    "Department of Data Science (PUCIT)",
    "University of the Punjab, Lahore, Pakistan",
]

LINK_RE = re.compile(r"!?\[[^\]]*\]\((?:<([^>]+)>|([^)\s]+))(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^\s*```")
USES_RE = re.compile(r"^\s*(?:-\s+)?uses:\s*([^\s#]+)", re.MULTILINE)
SECRET_PATTERNS = {
    "GitHub personal token": re.compile(r"\bghp_[A-Za-z0-9]{20,}"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Private key block": re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
}

results: list[tuple[str, str, str]] = []  # status, check, detail


def record(status: str, check: str, detail: str = "") -> None:
    results.append((status, check, detail))


def published_pages() -> list[Path]:
    pages = []
    for path in sorted(DOCS.rglob("*.md")):
        rel = path.relative_to(DOCS)
        if any(rel == excluded or rel.parts[:1] == excluded.parts for excluded in EXCLUDED):
            continue
        pages.append(path)
    return pages


def strip_markdown(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_~]", "", text)
    return text


def slugify(text: str) -> str:
    """Approximate Python-Markdown's TOC slug, which is what MkDocs uses."""
    value = unicodedata.normalize("NFKD", strip_markdown(text)).encode("ascii", "ignore").decode()
    value = value.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[-\s]+", "-", value)
    return value.strip("-")


def heading_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.startswith("#"):
            continue
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if not match:
            continue
        base = slugify(match.group(2))
        if not base:
            continue
        count = counts.get(base, 0)
        anchor = base if count == 0 else f"{base}_{count}"
        counts[base] = count + 1
        anchors.add(anchor)
    # Raw HTML anchors are rare here but cheap to include.
    anchors.update(re.findall(r"<a\s+[^>]*id=\"([^\"]+)\"", text))
    return anchors


def check_navigation(pages: list[Path]) -> None:
    text = MKDOCS.read_text(encoding="utf-8")
    nav_match = re.search(r"^nav:\s*$", text, re.MULTILINE)
    if not nav_match:
        record("FAIL", "navigation", "mkdocs.yml has no nav: block")
        return
    nav_text = text[nav_match.start():]
    nav_targets = re.findall(r"([A-Za-z0-9_./-]+\.md)", nav_text)

    missing_files = [t for t in nav_targets if not (DOCS / t).is_file()]
    if missing_files:
        for target in sorted(set(missing_files)):
            record("FAIL", "navigation", f"nav lists a missing page: {target}")
    else:
        record("PASS", "navigation", f"{len(set(nav_targets))} nav targets exist")

    published = {p.relative_to(DOCS).as_posix() for p in pages}
    unlisted = sorted(published - set(nav_targets))
    if unlisted:
        for page in unlisted:
            record("FAIL", "navigation", f"page is not in nav: {page}")
    else:
        record("PASS", "navigation", f"all {len(published)} published pages are in nav")


def check_links(pages: list[Path]) -> None:
    broken: list[str] = []
    checked = 0
    anchor_cache: dict[Path, set[str]] = {}

    for page in pages:
        page = page.resolve()
        text = page.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1) or match.group(2)
            if not target:
                continue
            if target.startswith(("http://", "https://", "mailto:", "tel:")):
                continue
            target = unquote(target)
            path_part, _, fragment = target.partition("#")
            checked += 1
            if not path_part:
                resolved = page
            else:
                resolved = (page.parent / path_part).resolve()
            if not resolved.exists():
                broken.append(f"{page.relative_to(ROOT)} -> {target}")
                continue
            if fragment and resolved.suffix == ".md":
                if resolved not in anchor_cache:
                    anchor_cache[resolved] = heading_anchors(resolved)
                if fragment not in anchor_cache[resolved]:
                    broken.append(f"{page.relative_to(ROOT)} -> {target} (anchor not found)")

    if broken:
        for problem in broken:
            record("FAIL", "links", problem)
    else:
        record("PASS", "links", f"{checked} relative links and images resolve")


def check_modules() -> None:
    modules = sorted((DOCS / "modules").glob("[0-9][0-9]-*"))
    failures = 0
    for module in modules:
        missing = [name for name in MODULE_PAGES if not (module / name).is_file()]
        if missing:
            record("FAIL", "modules", f"{module.name}: missing {', '.join(missing)}")
            failures += 1
            continue

        body = (module / "index.md").read_text(encoding="utf-8")
        if "## What you will be able to do" not in body:
            record("FAIL", "modules", f"{module.name}: missing 'What you will be able to do'")
            failures += 1

        total = sum(len((module / name).read_text(encoding="utf-8").split()) for name in MODULE_PAGES)
        if total < 2500:
            record("FAIL", "modules", f"{module.name}: only {total} words across the module")
            failures += 1
        for name in MODULE_PAGES:
            words = len((module / name).read_text(encoding="utf-8").split())
            if words < 120:
                record("FAIL", "modules", f"{module.name}/{name}: only {words} words")
                failures += 1

    if not failures:
        record("PASS", "modules", f"{len(modules)} modules have the full 9-page set")


def check_labs() -> None:
    labs = sorted((DOCS / "labs").glob("lab-[0-9][0-9]-*.md"))
    failures = 0
    if len(labs) != 20:
        record("FAIL", "labs", f"expected 20 lab pages, found {len(labs)}")
        failures += 1
    for lab in labs:
        body = lab.read_text(encoding="utf-8")
        missing = [heading for heading in LAB_HEADINGS if heading not in body]
        if missing:
            record("FAIL", "labs", f"{lab.name}: missing {', '.join(missing)}")
            failures += 1
    if not failures:
        record("PASS", "labs", f"{len(labs)} lab pages have the required student sections")


def check_readme_policy() -> None:
    readme = ROOT / "README.md"
    if not readme.is_file():
        record("FAIL", "readme", "root README.md is missing")
        return
    text = readme.read_text(encoding="utf-8")
    failures = []
    for heading in README_REQUIRED:
        if heading not in text:
            failures.append(f"missing section: {heading}")
    for command in README_FORBIDDEN:
        if command in text:
            failures.append(f"developer command belongs in reference-guides: {command}")
    if "```" in text:
        failures.append("root README contains a fenced code block; move commands to reference-guides")
    if failures:
        for failure in failures:
            record("FAIL", "readme", failure)
    else:
        record("PASS", "readme", "student-facing policy satisfied; no build commands")


def check_instructor() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    about_path = DOCS / "about" / "index.md"
    about = about_path.read_text(encoding="utf-8") if about_path.is_file() else ""
    missing = []
    for value in INSTRUCTOR:
        if value not in readme:
            missing.append(f"README: {value}")
        if value not in about:
            missing.append(f"about page: {value}")
    if missing:
        for value in missing:
            record("FAIL", "instructor", f"missing {value}")
    else:
        record("PASS", "instructor", "name, title, department, and university present")

def check_code_fences(pages: list[Path]) -> None:
    unbalanced = []
    for page in pages:
        page = page.resolve()
        fences = sum(1 for line in page.read_text(encoding="utf-8").splitlines() if FENCE_RE.match(line))
        if fences % 2:
            unbalanced.append(str(page.relative_to(ROOT)))
    if unbalanced:
        for page in unbalanced:
            record("FAIL", "markdown", f"unbalanced code fence: {page}")
    else:
        record("PASS", "markdown", "code fences are balanced on every page")


def python_files() -> list[Path]:
    roots = [ROOT / "scripts", ROOT / "datasets", ROOT / "examples"]
    skip = {".venv", ".venv-docs", ".venv-verify", "__pycache__", ".verify", "site"}
    files = []
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            if any(part in skip for part in path.parts):
                continue
            files.append(path)
    return files


def check_python(verbose: bool) -> None:
    failures = []
    files = python_files()
    for path in files:
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (SyntaxError, UnicodeDecodeError) as exc:
            failures.append(f"{path.relative_to(ROOT)}: {exc}")
    if failures:
        for failure in failures:
            record("FAIL", "python", failure)
    else:
        detail = f"{len(files)} Python files compile"
        if verbose and files:
            detail += f" (e.g. {files[0].relative_to(ROOT)})"
        record("PASS", "python", detail)


def check_dataset_manifest() -> None:
    manifest_path = ROOT / "datasets" / "generated" / "manifest.json"
    if not manifest_path.exists():
        record("SKIP", "dataset manifest", "not generated; run python datasets/generate.py")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("datasets", []):
        file_path = manifest_path.parent / entry["file"]
        if not file_path.exists():
            failures.append(f"{entry['file']} is missing")
            continue
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            failures.append(f"{entry['file']} hash differs from the manifest")
    if failures:
        for failure in failures:
            record("FAIL", "dataset manifest", failure)
    else:
        record("PASS", "dataset manifest", f"{len(manifest.get('datasets', []))} files match their hashes")


def check_secrets() -> None:
    scan_roots = [DOCS, ROOT / ".github", ROOT / "scripts", MKDOCS, ROOT / "requirements-docs.txt"]
    findings = []
    for base in scan_roots:
        if not base.exists():
            continue
        paths = [base] if base.is_file() else [p for p in base.rglob("*") if p.is_file()]
        for path in paths:
            if path.suffix not in {".md", ".yml", ".yaml", ".py", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for name, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    findings.append(f"{path.relative_to(ROOT)}: possible {name}")
    if findings:
        for finding in findings:
            record("FAIL", "secrets", finding)
    else:
        record("PASS", "secrets", "no credential patterns in docs, scripts, or workflows")


def check_workflows() -> None:
    workflow_dir = ROOT / ".github" / "workflows"
    if not workflow_dir.exists():
        record("SKIP", "workflows", "no .github/workflows directory")
        return

    try:
        import yaml  # type: ignore
    except ImportError:
        record("SKIP", "workflows", "PyYAML is not installed")
        return

    failures = []
    workflow_files = sorted([*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml")])
    for path in workflow_files:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            failures.append(f"{path.name}: YAML does not parse: {exc}")
            continue
        text = path.read_text(encoding="utf-8")
        if not isinstance(data, dict) or not data.get("jobs"):
            failures.append(f"{path.name}: no jobs defined")
            continue
        if "permissions" not in data:
            failures.append(f"{path.name}: no top-level permissions block")
        if "pull_request_target" in text:
            failures.append(f"{path.name}: pull_request_target is not used in this repository")
        if "write-all" in text:
            failures.append(f"{path.name}: write-all permissions are not allowed")
        for reference in USES_RE.findall(text):
            if reference.startswith("./"):
                continue
            if "@" not in reference:
                failures.append(f"{path.name}: action without a version: {reference}")
                continue
            ref = reference.rsplit("@", 1)[1]
            if ref in {"main", "master"} or not re.match(r"^v\d+(?:\.\d+){0,2}$", ref):
                if not re.fullmatch(r"[0-9a-f]{40}", ref):
                    failures.append(f"{path.name}: unpinned action reference: {reference}")

    if failures:
        for failure in failures:
            record("FAIL", "workflows", failure)
    else:
        record("PASS", "workflows", f"{len(workflow_files)} workflow file(s) parse and pin actions")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true", help="show sample paths")
    parser.add_argument("--skip-python", action="store_true", help="skip the syntax check")
    args = parser.parse_args()

    pages = published_pages()
    check_navigation(pages)
    check_links(pages)
    check_modules()
    check_labs()
    check_readme_policy()
    check_instructor()
    check_code_fences(pages)
    if not args.skip_python:
        check_python(args.verbose)
    check_dataset_manifest()
    check_secrets()
    check_workflows()

    failures = 0
    for status, check, detail in results:
        print(f"{status:4}  {check:16}  {detail}")
        failures += status == "FAIL"

    passed = sum(1 for status, _, _ in results if status == "PASS")
    skipped = sum(1 for status, _, _ in results if status == "SKIP")
    print(f"\n{passed} passed, {failures} failed, {skipped} skipped")
    if failures:
        print("Fix the failures above before committing. Run mkdocs build --strict too.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
