# Structure

Human-facing layer. Model-agnostic. Not runtime internals.

`structure/` exists so a project can be understood, used, built, and deployed without depending on a specific model, prompt, or orchestration setup.

## First Pointer

If the goal is fast role alignment for a model or operator, start with `Purpose/`.

- `Purpose/README.md` — shortest statement of system purpose, repo purpose, agent role, workflow split, and boundaries

## Default Project Layers

The portable `structure/` defaults are:

- `INDEX.md`
- `Purpose/`
- `User_Guide/`
- `Development/`
- `System Guide/`
- `Deployment/`

These are the load-bearing human layers.

## Rule

Keep `structure/` useful even if:

- the active model changes
- the runtime changes
- the deployment target changes

The point is legibility outside the live runtime.

## How To Use This Template

Use this repo as the canonical source when creating or updating project `structure/` folders.

Adapt the project-specific content, but keep the folder pattern and the role of each layer stable unless there is a strong reason to change it.
