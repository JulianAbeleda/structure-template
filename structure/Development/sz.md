# sz.py

`sz.py` keeps the codebase's size visible and bounded. It counts the lines
of source the project owns, groups them by area, and fails the commit when
a budget is exceeded.

It turns "the code is getting big" from a feeling into a number someone
reviews.

## What it does

1. **Walks the repo** and picks up source files: known extensions, plus
   extensionless scripts that start with `#!`. It skips dependencies,
   caches, build output, and symlinks.
2. **Counts nonblank lines** in each file.
3. **Sorts each file into a surface**, such as `tests`, `tooling`, or
   `source`. The first surface whose glob pattern matches owns the file.
   Anything that matches nothing is reported as `uncategorized`.
4. **Compares the totals to budgets**:

   | Budget             | Scope         | Effect when exceeded              |
   | ------------------ | ------------- | --------------------------------- |
   | `review_threshold` | whole repo    | prints `REVIEW`, never fails      |
   | `hard_limit`       | whole repo    | violation                         |
   | surface `limit`    | one surface   | violation (omit for report-only)  |
   | `file_limit`       | each file     | violation                         |

5. **Reports** a per-surface table and the ten largest files. With
   `--check`, any violation makes it exit 1, which blocks the commit or
   push.

## Where the rules live

The script has no project-specific numbers. All extensions, ignored
directories, surfaces, and budgets come from the `size` section of
`structure/Development/repository-policy.json`. To adopt it in a new repo,
edit that file, not the script.

## Where it runs

- `.githooks/pre-commit` runs `sz.py --check` on every commit.
- `.githooks/pre-push` runs it when the project has no
  `scripts/check-full.sh`.
- `.github/workflows/repository-policy.yml` runs it in CI, so bypassing a
  local hook does not bypass the rule.

## Usage

```sh
python3 sz.py            # human-readable report
python3 sz.py --check    # same report; exit 1 on any violation
python3 sz.py --json     # machine-readable report
python3 sz.py --root ../other-repo --config path/to/policy.json
```

Exit codes: `0` within budget, `1` violation under `--check`, `2` the
policy is missing or invalid.

Example output:

```text
Repository size

       92  OK    tests            limit 30000
      369  OK    tooling          limit 10000
        0  OK    source           limit 40000

      461  OK     total
    40000         review threshold
    50000         hard limit

Largest files
      213  tooling          sz.py
      113  tooling          scripts/check-commit-message.py
```

## The rule behind it

A budget is a decision, not an obstacle to route around. When a change hits
a limit, first remove duplicated or obsolete code. If the area really needs
more room, raise the number in its own reviewed change and record the
reason.

See `repository-automation.md` for hook installation and the full adoption
checklist.
