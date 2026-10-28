"""Small assertion harness shared by the lab kits.

Every kit ends with a table of checks, so a student can tell success from
near-success without reading the source. Exit code 0 means every check passed.

No third-party dependency: the harness must work in a bare virtual environment
before the lab's own packages are installed.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

LABS_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class Lab:
    """Collects checks and prints a verdict table."""

    lab_id: str
    title: str
    checks: list[Check] = field(default_factory=list)

    def check(self, name: str, ok: bool, detail: str = "") -> bool:
        self.checks.append(Check(name, bool(ok), detail))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
        return bool(ok)

    def equal(self, name: str, actual, expected, detail: str = "") -> bool:
        ok = actual == expected
        text = f"got {actual!r}, expected {expected!r}"
        return self.check(name, ok, f"{detail}; {text}" if detail else text)

    def fail(self, name: str, detail: str = "") -> None:
        self.check(name, False, detail)

    def finish(self) -> int:
        passed = sum(c.ok for c in self.checks)
        total = len(self.checks)
        print()
        print(f"{self.lab_id} {self.title}: {passed}/{total} checks passed")
        failed = [c for c in self.checks if not c.ok]
        for c in failed:
            print(f"  - still failing: {c.name}")
        if not failed:
            print("  ACCEPTED")
        return 0 if passed == total else 1


def section(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def timed(label: str):
    """Context manager that prints elapsed seconds for a step."""

    class _Timer:
        def __enter__(self):
            self.start = time.perf_counter()
            return self

        def __exit__(self, *exc):
            print(f"  {label}: {time.perf_counter() - self.start:.2f}s")
            return False

    return _Timer()


def load_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"setup error: {message}")


def python_hint() -> str:
    return f"interpreter: {sys.executable} ({sys.version.split()[0]})"
