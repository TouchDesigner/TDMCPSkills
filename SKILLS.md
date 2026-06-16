# TDMCP Skills

Skills teach AI coding agents how to work with TouchDesigner effectively. They are installed to each host's skill discovery directory (see [README.md](README.md) for supported hosts and install targets) and auto-discovered.

## Structure

Each skill is a directory containing:

- `SKILL.md` — rules, conventions, pitfalls (always present)
- `reference.md` — API signatures, lookup tables, parameter lists (optional)
- `examples.md` — concrete patterns and recipes (optional)

## Available Skills

### Builder Skills (11)

> Load `td-general` before any TD task for workflow + cross-cutting rules.


- **`td-top-family`** — TOP chains, render pipelines, compositing, feedback loops
- **`td-chop-family`** — CHOP chains, audio, LFOs, animation, data-driven control
- **`td-pop-family`** — POP networks, particles, geometryCOMP lifecycle, forces, instancing
- **`td-sop-family`** — SOP geometry, modeling, procedural surfaces
- **`td-mat-family`** — Materials: constantMAT, pbrMAT, pointspriteMAT, glslMAT, placement, blending
- **`td-glsl-shaders`** — GLSL pixel, compute, vertex shaders, uniforms
- **`td-dat-family`** — Python callbacks, table DATs, text processing
- **`td-lister-ui`** — Lister/TreeLister, tables, interactive lists, data browsers
- **`td-comp-architecture`** — Extensions, custom pars, modularity
- **`td-python-extension`** — Extension classes, ext0object, parameter callbacks, scriptTOP/numpy
- **`td-geometry-instancing`** — geometryCOMP instance setup, data sources (CHOP/DAT/TOP/POP), transforms, textures

### Cross-Cutting Skills (4)

- **`td-general`** — Workflow phases, naming, paths, tool preferences, universal pitfalls. Load first on any TD task
- **`td-colab`** — Collaborative mode—you're a thinking partner, not a builder. Load when you're sliding into auto-building or need to reset the frame
- **`td-node-layout`** — Network layout conventions: spacing, flow, positioning
- **`td-performance-check`** — Selective cooking, GPU vs CPU, time patterns

### Workflow Skills (3)

- **`td-build-planning`** — Before building: scout network, plan phases, allocate positions
- **`td-review-network`** — After building: validate errors, wiring, parameter correctness
- **`td-network-cleanup`** — After review: layout polish, annotations, alignment, spacing

### Contributor Skills

Not distributed via plugin or `install.py`. Live in `.claude/skills/` and auto-load only when Claude Code is working in a clone of this repo.

- **`td-learn`** — Review conversation, audit skills, propose updates (for skill authors)
- **`td-skills-local`** — Project-local install helper (legacy; superseded by plugin install)

## Build Order

1. **td-build-planning** — scout, plan, allocate positions
2. **builder skills** — create operators (combine multiple per build)
3. **td-review-network** — check errors, validate wiring/parameters
4. **td-network-cleanup** — align, annotate, polish
