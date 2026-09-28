from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
COMMIT_CHECK = REPOSITORY / "scripts" / "check-commit-message.py"
SIZE_CHECK = REPOSITORY / "sz.py"


class CommitMessageTests(unittest.TestCase):
    def run_check(self, subject: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(COMMIT_CHECK), "--subject", subject],
            cwd=REPOSITORY,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_accepts_one_or_more_known_areas(self) -> None:
        self.assertEqual(self.run_check("[docs] explain hook setup").returncode, 0)
        self.assertEqual(self.run_check("[core][test] cover parser boundary").returncode, 0)
        self.assertEqual(self.run_check("[repo] NFC - move policy loader").returncode, 0)

    def test_rejects_missing_and_unknown_areas(self) -> None:
        missing = self.run_check("explain hook setup")
        unknown = self.run_check("[banana] explain hook setup")
        self.assertEqual(missing.returncode, 1)
        self.assertIn("expected:", missing.stderr)
        self.assertEqual(unknown.returncode, 1)
        self.assertIn("unknown area", unknown.stderr)


class SizeTests(unittest.TestCase):
    def write_fixture(self, root: Path, hard_limit: int) -> None:
        policy = {
            "size": {
                "review_threshold": 4,
                "hard_limit": hard_limit,
                "file_limit": 20,
                "extensions": [".py", ".sh"],
                "ignored_directories": [".git", "vendor"],
                "surfaces": [
                    {"name": "tests", "patterns": ["tests/**"], "limit": 10},
                    {"name": "tooling", "patterns": ["scripts/**"], "limit": 10},
                    {"name": "source", "patterns": ["src/**"], "limit": 10},
                ],
            }
        }
        (root / "policy.json").write_text(json.dumps(policy), encoding="utf-8")
        (root / "src").mkdir()
        (root / "src/main.py").write_text("x = 1\n\nx = 2\n", encoding="utf-8")
        (root / "tests").mkdir()
        (root / "tests/test_main.py").write_text("assert True\n", encoding="utf-8")
        (root / "scripts").mkdir()
        (root / "scripts/run").write_text("#!/bin/sh\necho ok\n", encoding="utf-8")
        (root / "vendor").mkdir()
        (root / "vendor/ignored.py").write_text("ignored\n" * 100, encoding="utf-8")

    def run_size(self, root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SIZE_CHECK),
                "--root",
                str(root),
                "--config",
                "policy.json",
                *arguments,
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_counts_nonblank_lines_and_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_fixture(root, hard_limit=6)
            result = self.run_size(root, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["total_lines"], 5)
            self.assertTrue(report["review_required"])
            self.assertEqual(
                {surface["name"]: surface["lines"] for surface in report["surfaces"]},
                {"tests": 1, "tooling": 2, "source": 2},
            )

    def test_check_fails_at_hard_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_fixture(root, hard_limit=4)
            result = self.run_size(root, "--check")
            self.assertEqual(result.returncode, 1)
            self.assertIn("exceeds hard limit", result.stderr)


if __name__ == "__main__":
    unittest.main()
