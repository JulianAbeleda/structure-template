# Repository Automation Template

This template turns two repository rules into local, repeatable checks:

- commit subjects use a consistent bracketed area;
- owned source stays visible against review, repository, surface, and file-size
  budgets.

The policy is data in `repository-policy.json`. The hooks and scripts consume
that file; they should not grow project-specific area names or budget numbers
inside their code.

## Install the hooks

From the repository root:

```sh
scripts/install-hooks.sh
```

This sets the repository-local Git configuration:

```text
core.hooksPath=.githooks
```

Git does not enable versioned hooks merely because they were cloned. Every new
checkout must run the installer once. To remove this repository's hook-path
override:

```sh
scripts/install-hooks.sh remove
```

## Hook flows

### `commit-msg`

Validates the first line of each commit message against the configured areas.
The default form is:

```text
[area] concise summary
[area][test] concise summary
[area] NFC - extract helper without changing behavior
```

Git-generated merge and revert subjects and Git's `fixup!`, `squash!`, and
`amend!` workflows are supported. Edit `commit.areas` in
`repository-policy.json` before copying the template into a real project; the
generic list is only a starting point.

The same checker can run outside the hook:

```sh
python3 scripts/check-commit-message.py --subject '[docs] explain the release path'
python3 scripts/check-commit-message.py --range origin/main..HEAD
```

The range form is suitable for CI and pre-merge checks, so local and hosted
validation use the same authority.

### `pre-commit`

Runs `python3 sz.py --check`. If the project provides an executable
`scripts/check-fast.sh`, the hook runs it afterward. Put formatting, linting,
and focused tests in that project-owned entry point instead of editing the
hook for each language.

### `pre-push`

Runs an executable `scripts/check-full.sh` when the project provides one.
Otherwise it still checks `sz.py`. This gives projects a stable place for the
slower test suite without assuming a build system in the generic template.

Hooks are guardrails, not the only verification surface. A person can bypass a
local hook with Git options, so important repositories should call the same
scripts from CI or branch protection. The included
`.github/workflows/repository-policy.yml` does that for pull requests and
pushes to `main`; adapt its triggers if the project uses another branch model.

## Size policy

`sz.py` counts nonblank lines in common source formats and extensionless files
with a shebang. It ignores dependencies, generated output, caches, and build
directories named in the policy.

Run it as a report:

```sh
python3 sz.py
```

Run it as a gate or produce JSON:

```sh
python3 sz.py --check
python3 sz.py --json
```

The default policy contains:

- a soft total `review_threshold` that prints `REVIEW` but does not fail;
- a total `hard_limit` that fails with `--check`;
- a `file_limit` for every counted file;
- ordered `surfaces` for tests, tooling, and shipping source, each with its own
  patterns and optional limit;
- an `uncategorized` report for source that matches no surface.

Surface order matters: the first matching surface owns the file. Tests are
listed before general source so `crates/example/tests/case.rs` counts as a test
rather than shipping source.

## Adopt in another repository

Copy these paths together:

```text
.githooks/
.github/workflows/repository-policy.yml
scripts/check-commit-message.py
scripts/install-hooks.sh
structure/Development/repository-policy.json
sz.py
```

Then:

1. Replace the generic commit areas with the project's real subsystem names.
2. Adjust source extensions, ignored directories, surfaces, and budgets from a
   measured baseline.
3. Add `scripts/check-fast.sh` and `scripts/check-full.sh` only when the project
   has commands those names can own.
4. Run the hook installer in each checkout.
5. Add the range checker and `sz.py --check` to CI if the rules are
   load-bearing.

Do not raise a budget only to make the current change pass. Record why the
surface needs more room or reduce the duplicated/obsolete code first.
