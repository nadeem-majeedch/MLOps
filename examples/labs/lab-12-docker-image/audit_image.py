"""Static audit of the image definition. It does not need Docker.

    python audit_image.py                       # audit ./Dockerfile
    python audit_image.py --dockerfile other/Dockerfile --ignore other/.dockerignore

The audit encodes the ten decisions that make an image reproducible, small,
and runnable by someone else. It cannot tell you the image works; only a build
and a request can. It tells you the definition is worth building.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

IGNORE_REQUIRED = [".git", "mlruns", "data", "__pycache__", ".venv"]
SECRET_WORDS = ("password", "secret", "token", "api_key", "apikey", "credential")


@dataclass
class Finding:
    check: str
    ok: bool
    detail: str


def read_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]


def instructions(lines: list[str]) -> list[str]:
    """Logical instructions: comment-free and with continuations joined.

    A HEALTHCHECK's embedded `CMD python -c ...` is part of the HEALTHCHECK,
    not a second CMD. Joining first is what keeps the two apart.
    """
    logical: list[str] = []
    buffer = ""
    for line in lines:
        if not line or line.startswith("#"):
            continue
        buffer = f"{buffer} {line}".strip() if buffer else line
        if buffer.endswith("\\"):
            buffer = buffer[:-1].strip()
            continue
        logical.append(buffer)
        buffer = ""
    if buffer:
        logical.append(buffer)
    return logical


def audit(dockerfile: Path, ignore_file: Path, requirements: Path) -> list[Finding]:
    lines = instructions(read_lines(dockerfile))
    upper = [line.upper() for line in lines]
    findings: list[Finding] = []

    froms = [line.split()[1] for line in lines if line.upper().startswith("FROM ")]
    unpinned = [image for image in froms if ":" not in image or image.endswith(":latest")]
    findings.append(
        Finding("base image is pinned", bool(froms) and not unpinned,
                f"FROM {', '.join(froms)}" if not unpinned else f"unpinned: {unpinned}")
    )

    findings.append(
        Finding("build stage is separate from runtime", len(froms) >= 2,
                f"{len(froms)} FROM instruction(s)")
    )

    requirements_at = next((i for i, line in enumerate(upper) if line.startswith("COPY ") and "REQUIREMENTS" in line), None)
    app_at = next((i for i, line in enumerate(upper) if line.startswith("COPY ") and "REQUIREMENTS" not in line
                   and ". /" not in line), None)
    findings.append(
        Finding("dependencies install before application code", requirements_at is not None
                and (app_at is None or requirements_at < app_at),
                f"requirements COPY at {requirements_at}, app COPY at {app_at}")
    )

    user_lines = [line for line in lines if line.upper().startswith("USER ")]
    non_root = bool(user_lines) and user_lines[-1].split()[1].lower() not in {"root", "0"}
    findings.append(Finding("container runs as a non-root user", non_root,
                            user_lines[-1] if user_lines else "no USER instruction"))

    findings.append(Finding("healthcheck is defined", any(line.upper().startswith("HEALTHCHECK") for line in lines),
                            "found" if any(line.upper().startswith("HEALTHCHECK") for line in lines) else "missing"))

    broad = [line for line in lines if re.fullmatch(r"COPY\s+\.\s+\./?", line)]
    findings.append(Finding("no blanket copy of the build context", not broad,
                            "COPY . . sends everything not ignored" if broad else "explicit copies"))

    ignored = set()
    if ignore_file.exists():
        ignored = {line.strip().strip("/") for line in ignore_file.read_text(encoding="utf-8").splitlines()
                   if line.strip() and not line.startswith("#")}
    missing = [name for name in IGNORE_REQUIRED if name not in ignored]
    findings.append(Finding("build context excludes generated and private files", not missing,
                            ", ".join(missing) if missing else f"{len(ignored)} patterns"))

    pinned = all("==" in line for line in requirements.read_text(encoding="utf-8").splitlines()
                 if line.strip() and not line.startswith("#"))
    findings.append(Finding("runtime requirements are pinned", pinned, str(requirements.name)))

    cmd = next((line for line in lines if line.upper().startswith("CMD ")), "")
    findings.append(Finding("the server binds all interfaces", "0.0.0.0" in cmd, cmd or "no CMD"))

    exposed = next((line for line in lines if line.upper().startswith("EXPOSE ")), "")
    port_in_cmd = re.search(r"--port[\"', ]+(\d+)", cmd)
    exposed_port = re.search(r"(\d+)", exposed) if exposed else None
    findings.append(
        Finding("EXPOSE matches the port the server uses",
                bool(port_in_cmd and exposed_port and port_in_cmd.group(1) == exposed_port.group(1)),
                f"{exposed or 'no EXPOSE'} vs {cmd or 'no CMD'}")
    )

    secrets = [line for line in lines if line.upper().startswith(("ENV ", "ARG "))
               and any(word in line.lower() for word in SECRET_WORDS)]
    findings.append(Finding("no credentials baked into the image", not secrets, str(secrets[:2])))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dockerfile", type=Path, default=Path("Dockerfile"))
    parser.add_argument("--ignore", type=Path, default=Path(".dockerignore"))
    parser.add_argument("--requirements", type=Path, default=Path("requirements.txt"))
    args = parser.parse_args()

    if not args.dockerfile.exists():
        print(f"no Dockerfile at {args.dockerfile}")
        return 2

    findings = audit(args.dockerfile, args.ignore, args.requirements)
    for finding in findings:
        print(f"  [{'PASS' if finding.ok else 'FAIL'}] {finding.check} -- {finding.detail}")
    failed = [finding for finding in findings if not finding.ok]
    print(f"\n{len(findings) - len(failed)}/{len(findings)} image checks passed")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
