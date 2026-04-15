# TDMCP Skills

Skills teach Claude how to work with TouchDesigner effectively. They live in `skills/` as domain knowledge files and are auto-discovered by Claude Code.

## Structure

Each skill is a directory under `skills/` containing:

- `SKILL.md` — rules, conventions, pitfalls (always present)
- `reference.md` — API signatures, lookup tables, parameter lists (optional)
- `examples.md` — concrete patterns and recipes (optional)

## Available Skills

### Builder Skills (9)

- **`top-family`** — TOP chains, render pipelines, compositing, feedback loops
- **`chop-family`** — CHOP chains, audio, LFOs, animation, data-driven control
- **`pop-family`** — POP networks, particles, geometryCOMP lifecycle, forces, instancing
- **`sop-family`** — SOP geometry, modeling, procedural surfaces
- **`glsl-shaders`** — GLSL pixel, compute, vertex shaders, uniforms
- **`dat-family`** — Python callbacks, table DATs, text processing
- **`lister-ui`** — Lister/TreeLister, tables, interactive lists, data browsers
- **`comp-architecture`** — Extensions, custom pars, modularity
- **`python-extension`** — Extension classes, ext0object, parameter callbacks, scriptTOP/numpy

### Cross-Cutting Skills (2)

- **`node-layout`** — Network layout conventions: spacing, flow, positioning
- **`performance-check`** — Selective cooking, GPU vs CPU, time patterns

### Workflow Skills (4)

- **`build-planning`** — Before building: scout network, plan phases, allocate positions
- **`review-network`** — After building: validate errors, wiring, parameter correctness
- **`network-cleanup`** — After review: layout polish, annotations, alignment, spacing
- **`skill-optimizer`** — Meta: audit skills for consistency, efficiency, redundancy

## Build Order

1. **build-planning** — scout, plan, allocate positions
2. **builder skills** — create operators (combine multiple per build)
3. **review-network** — check errors, validate wiring/parameters
4. **network-cleanup** — align, annotate, polish

## Contributing

1. Create a directory under `skills/` with at least a `SKILL.md`
2. Add `reference.md` and/or `examples.md` if the skill has enough material
3. Use YAML frontmatter with a `description` field in `SKILL.md`
4. Add the skill to `skills/SKILLS.md` index
5. Test by asking Claude Code to perform the task the skill covers
