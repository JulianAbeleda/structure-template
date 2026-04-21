# Structure Template

Reusable human-facing project structure.

This repo is the canonical source of truth for the `structure/` pattern used across projects.

Its job is to define:

- the default `structure/` folder shape
- the purpose of each layer
- the boilerplate-ready templates for those layers
- the conventions for keeping project docs model-agnostic and human-readable

Use this repo when you want to:

- start a new project with a clean `structure/` layer
- copy the default folders and starter docs
- align models quickly without making them read long procedural guides
- keep documentation conventions consistent across repos

## Canonical Scope

This repo is the specification, not a project implementation.

Other repos may adapt the template, but this repo should define the canonical pattern.

## Default Shape

The core template is:

- `structure/INDEX.md`
- `structure/Purpose/README.md`
- `structure/User_Guide/README.md`
- `structure/Development/README.md`
- `structure/System Guide/README.md`
- `structure/Deployment/README.md`

Projects can add more folders, but these are the load-bearing defaults.

## Core Rule

`structure/` is the human-facing layer.

It should stay useful even if:

- the active model changes
- the runtime changes
- the deployment target changes
- the implementation details shift underneath it

The point is legibility outside the live runtime.
