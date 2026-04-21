# Purpose Template

Use this template when creating `structure/Purpose/README.md` for a new repo.

The goal is fast role alignment.

This file is not the project-specific purpose layer itself.
It is the reusable scaffold for making one.

## Design Goal

`Purpose/README.md` should let you say:

- read `structure/Purpose/`

And get back a short, reliable imprint of:

- what the system is
- what the repo is for
- what the agent should do
- what the agent should not do
- how the workflow roles are split

If the file becomes long procedural documentation, it has failed.

Use `User_Guide/` for procedures.
Use `Development/` for build strategy.
Use `Purpose/` for role, intent, boundaries, and defaults.

## Canonical Section Order

Every project-level `Purpose/README.md` should use this order:

1. `System Purpose`
2. `Repo Purpose`
3. `Agent Purpose`
4. `Workflow Split`
5. `Default Behavior`
6. `Boundaries`
7. `Anti-Goals`
8. `Quick Pointers`

Keep the order stable so models learn the pattern.

## Writing Rules

- Keep it short
- Keep it direct
- Keep it model-agnostic where possible
- Make the agent role explicit
- Make the workflow split explicit
- Make the boundaries explicit
- Avoid long setup instructions
- Avoid duplicating detailed procedures from `User_Guide/`
- Avoid duplicating architecture detail better suited for `System Guide/`

## Reusable Template

```md
# Purpose

Short orientation layer for <PROJECT>.

Read this first when the goal is fast role alignment rather than step-by-step operation.

Use `User_Guide/` for procedures.
Use `Development/` for building the repo.
Use this file for purpose, role, boundaries, and defaults.

## System Purpose

<What the system/product/project is at the highest level.>

## Repo Purpose

<What this repo exists to build, ship, or operate.>

## Agent Purpose

When GPT-5.4 / Codex is working inside this repo, its default role is the development terminal.

That means:

- <read / inspect>
- <implement>
- <refactor>
- <improve architecture or structure>
- <deployment or repo-specific responsibility if relevant>

Its role is not to <common confusion 1> and not to <common confusion 2> by default.

## Workflow Split

<State the intended role split across tools or terminals.>

If the roles drift, reset to this split.

## Default Behavior

If working as the development terminal:

- <default behavior 1>
- <default behavior 2>
- <default behavior 3>
- <default behavior 4>

## Boundaries

Do not confuse these things:

- <layer 1>
- <layer 2>
- <layer 3>

<One short paragraph on what this repo should not absorb or impersonate.>

## Anti-Goals

Do not default to:

- <anti-goal 1>
- <anti-goal 2>
- <anti-goal 3>
- <anti-goal 4>

## Quick Pointers

If you want quick role alignment, say:

- `structure/Purpose/`

If you want setup or operating steps, say:

- `structure/User_Guide/`

If you want build strategy or implementation guidance, say:

- `structure/Development/`
```

## Notes

Project-specific files should adapt the content, not the section pattern.

If a repo does not need a workflow split, keep the section and say so briefly rather than deleting the section.

If a repo grows more layers, update `System Guide/` first and keep `Purpose/` short.
