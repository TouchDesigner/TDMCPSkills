# TDMCP Skills

Skills teach Claude how to work with TouchDesigner effectively. They are installed to Claude Code's skill directories and auto-discovered.

## Structure

Each skill is a directory containing:

- `SKILL.md` — rules, conventions, pitfalls (always present)
- `reference.md` — API signatures, lookup tables, parameter lists (optional)
- `examples.md` — concrete patterns and recipes (optional)

## Available Skills

### Builder Skills (9)

- **`td-top-family`** — TOP chains, render pipelines, compositing, feedback loops
- **`td-chop-family`** — CHOP chains, audio, LFOs, animation, data-driven control
- **`td-pop-family`** — POP networks, particles, geometryCOMP lifecycle, forces, instancing
- **`td-sop-family`** — SOP geometry, modeling, procedural surfaces
- **`td-glsl-shaders`** — GLSL pixel, compute, vertex shaders, uniforms
- **`td-dat-family`** — Python callbacks, table DATs, text processing
- **`td-lister-ui`** — Lister/TreeLister, tables, interactive lists, data browsers
- **`td-comp-architecture`** — Extensions, custom pars, modularity
- **`td-python-extension`** — Extension classes, ext0object, parameter callbacks, scriptTOP/numpy

### Cross-Cutting Skills (2)

- **`td-node-layout`** — Network layout conventions: spacing, flow, positioning
- **`td-performance-check`** — Selective cooking, GPU vs CPU, time patterns

### Workflow Skills (5)

- **`td-build-planning`** — Before building: scout network, plan phases, allocate positions
- **`td-review-network`** — After building: validate errors, wiring, parameter correctness
- **`td-network-cleanup`** — After review: layout polish, annotations, alignment, spacing
- **`td-learn`** — Meta: analyze session tool usage, audit skills for consistency
- **`td-skills-local`** — Install, update, or remove skills in the current project

## Build Order

1. **td-build-planning** — scout, plan, allocate positions
2. **builder skills** — create operators (combine multiple per build)
3. **td-review-network** — check errors, validate wiring/parameters
4. **td-network-cleanup** — align, annotate, polish
