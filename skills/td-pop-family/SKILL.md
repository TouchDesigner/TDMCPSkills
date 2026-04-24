---
description: POP networks — particles, geometryCOMP lifecycle, feedback, forces, instancing. Use when building GPU point operations.
---

# POP Networks

GPU-accelerated point operations. POPs replace SOPs for 3D geometry with massively parallel GPU compute. See `reference.md` for operator decision tree and attribute reference.

## Core Concepts

- **Points with attributes**: P (position), N (normal), Color, Tex, custom
- **GPU-resident**: all data stays on GPU, downloading to CPU causes stalls
- **Memory model**: unmodified input attributes pass by reference (zero-copy)
- **Points alone don't render** — need Point Primitives (set Connectivity on generators)
- **Rendering**: POPs in geometryCOMPs, rendered by renderTOP. MATs read POP attributes
- **Data sourcing**: POPs can exist in any COMP (baseCOMP, etc.) for data extraction without rendering
- **GPU→CPU cost**: `poptoCHOP` and `poptoDAT` copy data from GPU to CPU — can be heavy for large point counts

## geometryCOMP Setup

1. Create geometryCOMP
2. **Delete auto-created torus** immediately
3. Build POP chain inside, end with nullPOP
4. Set `display=true render=true` on output nullPOP
5. Material: place MAT inside geometryCOMP, reference as `./mat_name`. See `td-mat-family` skill
6. For instancing: see `td-geometry-instancing` skill

## Feedback Simulation

feedbackPOP has 1 input (reset/initial geometry). Loop back from output null is automatic.
- **Lifecycle**: `initializepulse` (reset) → `startpulse` (begin playback) → `play` (pause/resume)
- **particlePOP same lifecycle** — also requires `initializepulse` then `startpulse` to reset and run
- **Reinit after attribute changes**: `pulse_parameter` with `initializepulse` then `startpulse`
- **Conservative initial forces**: start low (gravity ~0.1-0.2, damping ~0.98)
- **forceradialPOP planar force** — creates soft repulsion, not hard bounces. Use mathmixPOP for floor collision (see reference.md)

## GLSL POP

- `glslPOP` — default choice, one attribute class, supports multi-pass
- `glsladvancedPOP` — only when needed: multi-class read/write, index buffer (`I[]`), extra outputs. See `td-glsl-shaders/glsladvancedPOP.md` for buffer allocation, output count control, and pitfalls
- Set `computedat` to textDAT name, list output attributes in `outputattrs`
- **Custom attributes** — use the `attr` sequence: `attr0name=color`, `attr0type=color`. GLSL buffer is auto-declared as `Color` (capital C, matching POP attribute name). Write as `Color[idx] = vec4(...)`. Do NOT manually declare an SSBO — it compiles but writes to an unmapped buffer
- **Attribute must exist before writing** — `outputattrs` only grants write access to attributes that already exist on the points. To write a new attribute: either create it with the `attr` sequence on the glslPOP itself, or place an `attributePOP` upstream to initialize it. Then list it in `outputattrs` explicitly
- **writeonly caveat** — with default `outputaccess=writeonly`, attributes listed in `outputattrs` that aren't written in the shader may get zeroed
- `TDPerlinNoise()` NOT available — write custom noise or use sampler input
- Multi-pass: `Passes=N, prevPassOutput=ON` for iterative solvers
- **`vec` not `const` for uniforms** — `const` sequence recompiles shader on every value change. Use `vec` for runtime parameters (see `td-glsl-shaders` skill)
- **Prefer built-in POPs over trivial glslPOP** — operations like texture lookup + math (abs, multiply, add) can use `lookuptexturePOP → mathmixPOP` chain instead of custom GLSL

## Common Patterns

- **Basic point cloud**: `gridPOP → noisePOP → nullPOP`
- **Particle sim**: `sourcePOP → feedbackPOP → [forces] → nullPOP`
- **Built-in particles**: `pointgeneratorPOP → particlePOP → [forces/bounce] → nullPOP`
- **Spatial interaction**: `neighborPOP` adds `Nebr`/`NumNebrs` for flocking/collision
- **SOP conversion**: `soptoPOP → attributePOP → nullPOP`
- **Copy/instance**: `copyPOP` (simple) or `glslcopyPOP` (custom per-copy transform, see below)

## GLSL Copy POP

`glslcopyPOP` copies source geometry N times with a custom GLSL transform per copy. See `reference.md` for full shader API.
- **Inputs**: input 0 = source geometry, input 1 = template points (optional, determines copy count)
- **Shader in docked DAT only** — write to `<name>_ptCompute`, never a separate textDAT (TDCopyIndex breaks). Delete unused `_vertCompute` and `_primCompute` docked DATs if not writing vert/prim shaders
- **Key functions**: `TDCopyIndex()`, `TDTemplate_P()`, `TDTemplate_AttribName()`, `TDIn_P()`

## Attributes

- See `reference.md` for full attribute list (reserved, common, particlePOP-specific)
- **Component access**: `P.x`, `P.y`, `P.z` (preferred) or `P(0)`, `P(1)`, `P(2)`. Use `.x/.y/.z` for readability
- **User-defined**: lowercase first letter to avoid conflicts with Derivative attrs
- **Debug values**: `inspect_values(path)` returns `pointAttributes[name].values` — sampled point values per attribute. `max_points=100` default (cap 10000), even-spaced stride when over cap. `attributes=["P","Cd"]` to filter. Type strings: `float3`, `int`, `float` (TD doesn't expose color/dir semantics — infer from name)

## Pitfalls

- **Locked nullPOP breaks POP cook loops** — cachePOPs keep cooking even when `active=false`, creating dependency loops in iterative POP pipelines. Place a `nullPOP` after the cachePOP and lock it (`op.lock = True`). The locked null holds stable geometry and breaks the cook chain. See `td-glsl-shaders/glsladvancedPOP.md` for the full cache feedback pattern
- **Default torus not deleted** — renders instead of your chain
- **No display/render flags on output null** — nothing renders
- **feedbackPOP not reinitialized after attribute changes** — stale attribute schema
- **Avoid SOPs inside geometryCOMPs** — use POP equivalents (spherePOP not sphereSOP)
- **copyPOP too heavy** — N vertices × M particles. Use instancing instead for many copies
- **GPU download stalls** — use `delayed=True` in Python for POP data access
- **lookuptexturePOP defaults wrong** — `lookupindexattr0/1` default to `P(0)`/`P(1)` (world position), NOT `Tex(0)`/`Tex(1)`. Explicitly set to Tex coords when sampling by UV
- **normalPOP tangents for PBR** — set `tang=alwayscompute` when using pbrMAT. Without tangents, PBR lighting fails
- **Point vs vertex attributes for materials** — glslPOP writes point attributes. pbrMAT/phongMAT read Tex as vertex attributes. Use `attributeconvertPOP` (`convertop=pointtovert`, `inputattrs=Tex`) to convert before the output null. Also disable spherePOP's built-in vertex Tex (`texture=none`) to avoid conflicts
- **mathmixPOP/mathcombinePOP sequences start empty** — `vec`/`comb` sequence pars don't exist until you add blocks: `n.par.comb.sequence.numBlocks = 2`. Must do this before setting `comb0oper` etc.
- **rectanglePOP size is `sizeu`/`sizev`**, NOT `sizex/y/z/w` despite get_help showing those as components. Setting `sizex` silently does nothing. Same U/V naming on other 2D primitives with UV semantics — always verify live pars with `get_parameters(include_defaults=true)` before trusting get_help's `components` list
