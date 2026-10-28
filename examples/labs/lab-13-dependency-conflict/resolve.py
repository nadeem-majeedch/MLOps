"""Find requirements that cannot be installed together. No network needed.

    python resolve.py requirements.txt requirements-legacy.txt

The check is deliberately simple: every `name==version` pin must satisfy every
range declared for that name across all files, and a package may not be pinned
to two different versions. That is enough to catch the class of mistake this
lab is about, and it runs in a second.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from packaging.requirements import Requirement
from packaging.version import Version

PIN = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*==\s*([^\s;#]+)")


def parse(paths: list[Path]) -> tuple[dict[str, list[tuple[str, str]]], list[str]]:
    pins: dict[str, list[tuple[str, str]]] = {}
    problems: list[str] = []
    for path in paths:
        if not path.exists():
            problems.append(f"missing file: {path}")
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.split("#")[0].strip()
            if not line or line.startswith("-"):
                continue
            try:
                requirement = Requirement(line)
            except Exception:  # noqa: BLE001 - report, do not crash
                problems.append(f"{path.name}: cannot parse {line!r}")
                continue
            name = requirement.name.lower().replace("_", "-")
            pins.setdefault(name, []).append((str(requirement.specifier), path.name))
    return pins, problems


def conflicts(pins: dict[str, list[tuple[str, str]]]) -> list[str]:
    found: list[str] = []
    for name, specs in sorted(pins.items()):
        versions = {spec[2:] for spec, _ in specs if spec.startswith("==") and spec[2:]}
        if len(versions) > 1:
            found.append(f"{name}: pinned to {', '.join(sorted(versions))} by different files")
            continue
        if versions:
            pinned = Version(next(iter(versions)))
            for spec, source in specs:
                if not spec.startswith("==") and spec:
                    from packaging.specifiers import SpecifierSet

                    if pinned not in SpecifierSet(spec):
                        found.append(f"{name}=={pinned} ({source}) violates {spec} declared elsewhere")
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    pins, problems = parse(args.files)
    found = problems + conflicts(pins)
    print(f"{len(pins)} packages across {len(args.files)} files")
    if not found:
        print("no conflicts: the set can be installed together")
        return 0
    for line in found:
        print(f"  CONFLICT {line}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
