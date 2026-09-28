#!/usr/bin/env python3
"""Report and optionally enforce configurable repository source-size budgets."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path("structure/Development/repository-policy.json")


@dataclass(frozen=True)
class Surface:
    name: str
    patterns: tuple[str, ...]
    limit: int | None


@dataclass(frozen=True)
class FileCount:
    path: str
    lines: int
    surface: str


@dataclass(frozen=True)
class SizePolicy:
    review_threshold: int
    hard_limit: int
    file_limit: int
    extensions: frozenset[str]
    ignored_directories: frozenset[str]
    surfaces: tuple[Surface, ...]


def positive_integer(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"size.{field} must be a positive integer")
    return value


def load_policy(path: Path) -> SizePolicy:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        size = data["size"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load size policy from {path}: {error}") from error

    review = positive_integer(size.get("review_threshold"), "review_threshold")
    hard = positive_integer(size.get("hard_limit"), "hard_limit")
    file_limit = positive_integer(size.get("file_limit"), "file_limit")
    if review > hard:
        raise ValueError("size.review_threshold cannot exceed size.hard_limit")

    extensions = size.get("extensions")
    ignored = size.get("ignored_directories")
    raw_surfaces = size.get("surfaces")
    if not isinstance(extensions, list) or not extensions:
        raise ValueError("size.extensions must be a non-empty list")
    if not all(isinstance(item, str) and item.startswith(".") for item in extensions):
        raise ValueError("every size.extensions entry must begin with a dot")
    if not isinstance(ignored, list) or not all(isinstance(item, str) for item in ignored):
        raise ValueError("size.ignored_directories must be a string list")
    if not isinstance(raw_surfaces, list):
        raise ValueError("size.surfaces must be a list")

    surfaces: list[Surface] = []
    names: set[str] = set()
    for index, item in enumerate(raw_surfaces):
        if not isinstance(item, dict):
            raise ValueError(f"size.surfaces[{index}] must be an object")
        name = item.get("name")
        patterns = item.get("patterns")
        limit = item.get("limit")
        if not isinstance(name, str) or not name or name in names:
            raise ValueError(f"size.surfaces[{index}].name must be unique and non-empty")
        if not isinstance(patterns, list) or not patterns or not all(
            isinstance(pattern, str) and pattern for pattern in patterns
        ):
            raise ValueError(f"size.surfaces[{index}].patterns must be a non-empty string list")
        if limit is not None:
            limit = positive_integer(limit, f"surfaces[{index}].limit")
        names.add(name)
        surfaces.append(Surface(name, tuple(patterns), limit))

    return SizePolicy(
        review,
        hard,
        file_limit,
        frozenset(extension.lower() for extension in extensions),
        frozenset(ignored),
        tuple(surfaces),
    )


def is_shebang_file(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return handle.read(2) == b"#!"
    except OSError:
        return False


def classify(relative_path: str, surfaces: tuple[Surface, ...]) -> str:
    for surface in surfaces:
        if any(fnmatch.fnmatch(relative_path, pattern) for pattern in surface.patterns):
            return surface.name
    return "uncategorized"


def count_nonblank_lines(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def collect(root: Path, policy: SizePolicy) -> list[FileCount]:
    counts: list[FileCount] = []
    for directory, child_directories, file_names in os.walk(root):
        child_directories[:] = sorted(
            name
            for name in child_directories
            if name not in policy.ignored_directories
        )
        base = Path(directory)
        for name in sorted(file_names):
            path = base / name
            if path.is_symlink():
                continue
            relative = path.relative_to(root).as_posix()
            if path.suffix.lower() not in policy.extensions and not is_shebang_file(path):
                continue
            counts.append(
                FileCount(relative, count_nonblank_lines(path), classify(relative, policy.surfaces))
            )
    return counts


def build_report(counts: list[FileCount], policy: SizePolicy) -> dict[str, Any]:
    totals: dict[str, int] = defaultdict(int)
    for item in counts:
        totals[item.surface] += item.lines
    total = sum(item.lines for item in counts)
    violations: list[str] = []
    if total > policy.hard_limit:
        violations.append(f"total {total} exceeds hard limit {policy.hard_limit}")
    for surface in policy.surfaces:
        actual = totals[surface.name]
        if surface.limit is not None and actual > surface.limit:
            violations.append(
                f"surface {surface.name} has {actual} lines; limit is {surface.limit}"
            )
    for item in counts:
        if item.lines > policy.file_limit:
            violations.append(
                f"file {item.path} has {item.lines} lines; limit is {policy.file_limit}"
            )

    configured = [
        {
            "name": surface.name,
            "lines": totals[surface.name],
            "limit": surface.limit,
        }
        for surface in policy.surfaces
    ]
    if totals["uncategorized"]:
        configured.append(
            {"name": "uncategorized", "lines": totals["uncategorized"], "limit": None}
        )
    return {
        "total_lines": total,
        "review_threshold": policy.review_threshold,
        "hard_limit": policy.hard_limit,
        "file_limit": policy.file_limit,
        "review_required": total > policy.review_threshold,
        "surfaces": configured,
        "largest_files": [
            {"path": item.path, "lines": item.lines, "surface": item.surface}
            for item in sorted(counts, key=lambda entry: (-entry.lines, entry.path))[:10]
        ],
        "violations": violations,
    }


def display(report: dict[str, Any]) -> None:
    print("Repository size")
    print()
    for surface in report["surfaces"]:
        limit = surface["limit"]
        status = "OK" if limit is None or surface["lines"] <= limit else "FAIL"
        suffix = "report only" if limit is None else f"limit {limit}"
        print(f"  {surface['lines']:7d}  {status:4s}  {surface['name']:<16s} {suffix}")
    print()
    review = "REVIEW" if report["review_required"] else "OK"
    print(f"  {report['total_lines']:7d}  {review:6s} total")
    print(f"  {report['review_threshold']:7d}         review threshold")
    print(f"  {report['hard_limit']:7d}         hard limit")
    print()
    print("Largest files")
    for item in report["largest_files"]:
        print(f"  {item['lines']:7d}  {item['surface']:<16s} {item['path']}")
    if report["violations"]:
        print("\nViolations", file=sys.stderr)
        for problem in report["violations"]:
            print(f"  - {problem}", file=sys.stderr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="policy path, relative to --root unless absolute",
    )
    parser.add_argument("--check", action="store_true", help="fail when a hard budget is exceeded")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    config = args.config if args.config.is_absolute() else root / args.config
    try:
        policy = load_policy(config)
        report = build_report(collect(root, policy), policy)
    except (OSError, ValueError) as error:
        print(f"sz: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        display(report)
    if args.check and report["violations"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
