---
name: td-sop-family
description: SOP geometry — procedural modeling, CPU-based geometry operations. Use when SOPs are needed (prefer POPs for GPU work).
---

# SOP Networks

CPU-based geometry operators. SOPs are the traditional geometry family — procedural modeling, deformation, boolean operations. For GPU-accelerated point work, prefer POPs (see td-pop-family skill).

## When to Use SOPs vs POPs

- **Always prefer POPs over SOPs** — even for simple shapes (torus, grid, sphere). POPs run on GPU, are animation-ready, and avoid CPU bottlenecks
- **SOPs only when no POP equivalent exists**: boolean operations, UV unwrapping, specific polygon operations
- For parametric shapes: use gridPOP → glslPOP with a compute shader instead of torusSOP/sphereSOP
- **Avoid SOPs inside geometryCOMPs** when POPs exist — use spherePOP not sphereSOP

## Common Generators

- `gridSOP` — structured grid
- `sphereSOP` — sphere
- `boxSOP` — box
- `tubeSOP` — tube/cylinder
- `circleSOP` — circle/arc/ellipse
- `lineSOP` — line
- `curveSOP` — NURBS/Bezier curves
- `textSOP` — 3D text geometry
- `scriptSOP` — Python-generated geometry

## Common Processing

- `transformSOP` — translate/rotate/scale
- `noiseSOP` — noise displacement
- `facetSOP` — cusp, consolidate, compute normals
- `convertSOP` — between polygon/mesh/NURBS
- `booleanSOP` — union/intersect/subtract
- `copySOP` — copy to template points
- `deleteSOP` — remove primitives/points
- `mergeSOP` — combine geometry
- `switchSOP` — select between inputs
- `nullSOP` — chain endpoint

## SOP to POP Conversion

`soptoPOP` converts SOP geometry into the POP family for GPU processing.

## Pitfalls

- **CPU-bound** — SOPs run on CPU, not GPU. Large meshes are slow
- **Using SOPs where POPs exist** — sphereSOP inside geometryCOMP won't render properly with POP instancing