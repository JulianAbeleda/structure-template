#!/usr/bin/env python3
"""Validate bracketed commit subjects from the shared repository policy."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_POLICY = Path("structure/Development/repository-policy.json")
PREFIX_RE = re.compile(r"^((?:\[[a-z0-9][a-z0-9_-]*\])+)[ ](.+)$")
AREA_RE = re.compile(r"\[([a-z0-9][a-z0-9_-]*)\]")
FIXUP_PREFIXES = ("fixup! ", "squash! ", "amend! ")


def repository_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip())


def load_commit_policy(root: Path, policy_path: Path | None) -> dict[str, object]:
    path = policy_path or root / DEFAULT_POLICY
    if not path.is_absolute():
        path = root / path
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        commit = data["commit"]
        areas = commit["areas"]
        maximum = commit["subject_max_length"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load commit policy from {path}: {error}") from error
    if not isinstance(areas, list) or not areas or not all(isinstance(x, str) for x in areas):
        raise ValueError(f"{path}: commit.areas must be a non-empty string list")
    if not isinstance(maximum, int) or maximum < 20:
        raise ValueError(f"{path}: commit.subject_max_length must be an integer >= 20")
    return commit


def normalized_subject(subject: str) -> str:
    for prefix in FIXUP_PREFIXES:
        if subject.startswith(prefix):
            return subject[len(prefix) :]
    return subject


def validate_subject(subject: str, policy: dict[str, object]) -> list[str]:
    problems: list[str] = []
    maximum = int(policy["subject_max_length"])
    if len(subject) > maximum:
        problems.append(f"subject is {len(subject)} characters; maximum is {maximum}")

    if policy.get("allow_generated_merge_and_revert_subjects", True):
        if subject.startswith("Merge ") or subject.startswith('Revert "'):
            return problems

    candidate = normalized_subject(subject)
    match = PREFIX_RE.fullmatch(candidate)
    if not match:
        problems.append("expected: [area] concise summary (or [area][test] concise summary)")
        return problems

    allowed = set(policy["areas"])
    used = AREA_RE.findall(match.group(1))
    unknown = sorted(set(used) - allowed)
    if unknown:
        problems.append(
            f"unknown area(s): {', '.join(unknown)}; allowed: {', '.join(sorted(allowed))}"
        )
    if match.group(2).endswith("."):
        problems.append("subject should not end with a period")
    return problems


def subjects_for_range(revision_range: str) -> list[str]:
    result = subprocess.run(
        ["git", "log", "--format=%s", revision_range],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message_file", nargs="?", type=Path)
    parser.add_argument("--subject", help="validate one subject without a commit file")
    parser.add_argument("--range", dest="revision_range", help="validate every subject in a git range")
    parser.add_argument("--policy", type=Path, help="policy JSON path, relative to the repository")
    args = parser.parse_args()
    choices = sum(bool(value) for value in (args.message_file, args.subject, args.revision_range))
    if choices != 1:
        parser.error("choose exactly one of message_file, --subject, or --range")
    return args


def main() -> int:
    args = parse_args()
    try:
        root = repository_root()
        policy = load_commit_policy(root, args.policy)
        if args.message_file:
            subjects = [args.message_file.read_text(encoding="utf-8").splitlines()[0]]
        elif args.subject:
            subjects = [args.subject]
        else:
            subjects = subjects_for_range(args.revision_range)
    except (OSError, IndexError, subprocess.CalledProcessError, ValueError) as error:
        print(f"commit policy: {error}", file=sys.stderr)
        return 2

    failed = False
    for subject in subjects:
        problems = validate_subject(subject, policy)
        if not problems:
            continue
        failed = True
        print(f"invalid commit subject: {subject}", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
    if failed:
        return 1
    print(f"commit policy: {len(subjects)} subject(s) valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
