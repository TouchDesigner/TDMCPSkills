---
name: td-glsl-shaders
description: GLSL shaders in TouchDesigner — pixel, compute, vertex, POP, uniforms, docked DATs. Use when writing GLSL or creating glslTOP/glslMAT/glslPOP.
---

# GLSL Shaders

Custom GPU shaders in TouchDesigner. Three contexts: TOP (image processing), MAT (materials), POP (particle compute). See `reference.md` for built-in uniforms, functions, and template shaders.

## Contexts

- `glslmultiTOP` (prefer over glslTOP) — image processing, procedural textures, compute. Supports >3 inputs and POP buffer reads
- `glslMAT` — custom materials with vertex + pixel shaders, TD lighting system
- `glslPOP` / `glsladvancedPOP` — per-point GPU compute on particle data (see td-pop-family skill). Compute shader API (`P[idx]`, `TDIn_P()`, `N[idx]`) documented in td-pop-family `reference.md`. For `glsladvancedPOP` (multi-class, index buffer, extra outputs), see `glsladvancedPOP.md`. Custom attributes via attr sequence — buffer name is `Color` (capital C), auto-declared (see td-pop-family skill)

## Naming Conventions

- Uniforms `uName`, Samplers `sName`, Functions `CapitalCase()`, Locals `camelCase`, Constants `UPPER_SNAKE`
- Input index defines at top: `#define TEX_FEEDBACK 0`

## Docked DAT Pattern (glslTOP/glslmultiTOP)

Creating a glslmultiTOP auto-docks `<name>_pixel`, `<name>_compute`, `<name>_info` and auto-wires
`pixeldat` to `<name>_pixel`.

**Name the TOP at creation** (`glsl_<shader>`) so the docks inherit the prefix
(`glsl_<shader>_pixel`, …) and `pixeldat` is already correct — no rename, no repoint. (Docked refs
snapshot at creation; renaming the TOP later does NOT follow them.)

1. Create the glslmultiTOP with its final name `glsl_<shader>`.
2. Delete the unused mode dock (`_compute` for a pixel shader).
3. Write/sync the shader into `<name>_pixel` (already wired to `pixeldat`).
4. Keep `<name>_info` for compile-error visibility.

**glslPOP/glslcopyPOP**: always write shaders into the auto-docked DATs (`<name>_compute`, `<name>_ptCompute`). Never create separate textDATs for POP shaders. Delete unused docked DATs (e.g. `_vertCompute`, `_primCompute` if not writing vert/prim shaders).

**glslMAT**: See `td-mat-family` skill for docked DAT setup and placement. Use `#ifdef TD_VERTEX_SHADER` / `#ifdef TD_PIXEL_SHADER` guards in combined shader DAT. See `reference.md` for MAT vertex/pixel functions and templates.

## Uniforms

Up to 32 uniform vectors via operator parameters (`vec0name`, `vec0valuex`, etc.).

**TOP/MAT**: uniforms are NOT auto-declared. Setting `vec0name=uTime` does nothing unless the shader has `uniform float uTime;`. TD infers the type from the GLSL declaration.

**POP (glslPOP/glslcopyPOP)**: uniforms ARE auto-declared as `float`. Do NOT redeclare them — causes "Redeclaration" compile error. Cannot override the type to `vec3` etc.; use constants or sampler inputs for multi-component data.

To use N uniforms, first set the sequence block count, then access `vec0name`, `vec1name`, etc.

### glslPOP `vec` vs `const` Sequences

- **`vec` sequence** — runtime uniforms, GPU reads value each frame. Use for any parameter that changes at runtime (expressions, custom pars, animated values)
- **`const` sequence** — baked into shader source, triggers full recompilation on every value change. Use ONLY for truly static compile-time constants
- **Wrong choice causes hard switching** — `const` with expression-driven values recompiles each frame and produces threshold jumps instead of smooth interpolation

## Key Rules

- **Always `TDOutputSwizzle()`** on all color outputs — wrong channel ordering without it
- **No `#version` statement** — TD auto-injects it
- **`texture()` not `texture2D()`** — old GLSL 1.20 names don't work
- **`nonuniformEXT()`** for dynamically-indexed sampler arrays (Vulkan requirement)
- **glslMAT always `TDDeform(TDPos())`** — raw TDPos() breaks instancing
- **`rgba32float` format** for data textures — 8-bit clamps to [0,1]
- **Expression-driven resolutions** — never hardcode `resolutionw`/`resolutionh`
- **Prefer nodes over GLSL** — use built-in operators for common operations (circleTOP for splats, noiseCHOP for motion, lookupCHOP for curves) instead of reimplementing in shaders. Reserve GLSL for operations that truly need custom GPU code (advection, pressure solving, etc.)

## Feedback Pattern

constantTOP (clear) → feedbackTOP → glslmultiTOP → nullTOP. feedbackTOP `top` par must reference the downstream null.
- feedbackTOP = 1 iteration per frame. Use `npasses` on glslmultiTOP for iterative solvers
- Close the feedback loop before compiling shaders that depend on it (2D/3D type mismatch otherwise)

## Sync to File

Sync the pixel DAT to disk — the fast way to author: edit the `.glsl` on disk, TD recompiles.
- One `set_dat_content(file_content, file_path, file_type='glsl')` call writes the file and sets
  `file`/`syncfile`. The auto-docked pixel DAT already has `language=glsl`; a textDAT you create
  yourself needs `language=glsl` set (`set_dat_content` doesn't set it).
- Path: `code/glsl/<comp>/<subcomp>/<dat_name>.glsl`
  (e.g. `/project1/MyEffect/glsl_raymarch_pixel` → `code/glsl/MyEffect/glsl_raymarch_pixel.glsl`)
- Once synced, **edit on disk** — don't round-trip through the DAT.

See the `td-dat-family` skill for the full canonical flow.

## Pitfalls

- **Uniforms not declared in shader** — compiles but reads zero
- **TDPerlinNoise() in GLSL POP** — not available in compute shaders, only TOP/MAT
- **Creating separate textDATs for glslTOP** — rename and reuse auto-created docked DATs
- **Not checking `<name>_info` for compile errors** — `.errors()` only shows "Compile failed"; read the docked infoDAT for actual line numbers and error details
- **feedbackTOP before wiring** — outputs 2D texture, causes 3D compile errors downstream
- **Inline noise functions** — use noiseTOP as sampler input instead
- **Delta time** — `me.time.step` doesn't exist, use `1.0/me.time.rate` or `absTime.stepSeconds`
- **`centroid` in GLSL** — reserved keyword in GLSL 4.60, use `ctr` or similar
- **glslmultiTOP has no `resolution` par** — use `resolutionw`/`resolutionh` + `outputresolution='custom'` (or `'useinput'`). Setting `resolution` errors with `'td.ParCollection' object has no attribute 'resolution'` and halts `build_network` mid-way
