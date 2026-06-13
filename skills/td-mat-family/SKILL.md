---
name: td-mat-family
description: Materials — constantMAT, pbrMAT, pointspriteMAT, glslMAT, placement, blending. Use when assigning or creating materials for rendering.
---

# Materials

Materials control how geometry appears when rendered by a renderTOP.

## Material Types

- **constantMAT** — flat color, no lighting. Simplest, cheapest. Good for debug, UI, flat graphics
- **phongMAT** — classic diffuse+specular lighting. Maps for diffuse, specular, normal, bump, emit
- **pbrMAT** — physically based rendering. Metallic/roughness workflow, environment maps. Requires environmentlightCOMP with map TOP (see PBR Setup below)
- **pointspriteMAT** — renders points as camera-facing quads with configurable size. Essential for particle rendering
- **glslMAT** — custom GLSL vertex/pixel shaders. Full control. Load `td-glsl-shaders` skill for shader code
- **lineMAT** — renders line primitives (proximityPOP/linePOP graphs, edges). Per-line color, pixel or world width
- **wirePOP** — wireframe rendering via material wireframe toggle

## When to Use What

- **Flat particles/points** → pointspriteMAT (set `pointsize`, optional `colormap` texture)
- **Lit geometry** → pbrMAT (default choice) or phongMAT
- **Unlit solid color** → constantMAT
- **Custom shading** → glslMAT
- **Debug/wireframe** → constantMAT with `wireframe=true`

## pointspriteMAT

Renders each point as a camera-facing square. Without this, points render as single pixels.

- `pointsize` — sprite size in pixels (default 1)
- `colormap` — optional TOP texture mapped onto each sprite
- `alpha` — global opacity multiplier
- `blending` — enable for transparency
- `sizingmodel` — `constant/attenuate` or `attrib`. Attenuate scales with distance

## Placement

- **Inside geometryCOMP** — reference as `./mat_name`. Material lives with its geometry
- **Sibling level** — reference by name only (`mat_name`). Shared across geometryCOMPs
- **Naming**: `mattype_purpose` (e.g. `pointsprite_particle`, `pbr_surface`, `constant_debug`)
- Always use `get_help` before setting parameters — par names vary between MAT types

## PBR Setup

pbrMAT renders completely black without an environment light:
1. Create `environmentlightCOMP` inside the geometryCOMP (or sibling)
2. Create `moviefileinTOP` with `file` = `app.samplesFolder + '/Map/CloudyOcean_2Kx1K_8bit.tif'`
3. Set environmentlightCOMP `envmap` to the moviefileinTOP
4. POP geometry using pbrMAT also needs `normalPOP` with `tang=alwayscompute` — PBR lighting requires tangent vectors

## glslMAT Setup

**From scratch** — creating a glslMAT auto-docks three DATs: `<name>_vertex`, `<name>_pixel`, `<name>_info`.

1. Delete `_pixel` docked DAT
2. Rename `_vertex` → `<name>_shader` (stays docked to MAT)
3. Write combined shader with `#ifdef TD_VERTEX_SHADER` / `#ifdef TD_PIXEL_SHADER` guards
4. Set both `vdat` and `pdat` to the renamed DAT
5. Keep `_info` docked for compile error visibility
6. Assign via `./mat_name` when inside a geometryCOMP

**From pbrMAT/phongMAT** — pulse `outputshader` on the existing material. This creates a glslMAT with all built-in uniforms and shader code pre-populated in separate vertex/pixel DATs. Better starting point when extending PBR-style materials — modify the generated shaders instead of writing from scratch.

Layout follows the GLSL DAT sandwich pattern (see `td-node-layout` skill). Load `td-glsl-shaders` skill for shader code, uniforms, and templates.

## Pitfalls

- **Points invisible** — using constantMAT/pbrMAT for point-only geometry. Use pointspriteMAT
- **Wrong path prefix** — `./` means child, no prefix means sibling. Match placement to reference
- **Blending off** — transparent materials need `blending=true` on the MAT
- **pbrMAT renders black** — missing environmentlightCOMP with an environment map TOP. Always include one
- **PBR on POPs missing tangents** — normalPOP `tang` must be `alwayscompute`, otherwise lighting fails
- **pbrMAT `metallic` defaults to 1** — must explicitly set `metallic=0` for non-metallic surfaces, otherwise geometry looks like chrome
- **pbrMAT reads vertex Tex, not point Tex** — glslPOP writes point attributes, but pbrMAT samples `basecolormap` from vertex Tex coords. Use `attributeconvertPOP` (`convertop=pointtovert`) to convert. See `td-pop-family` skill
- **glslMAT on POPs: `Cd`/`N` silent failure** — referencing `Cd` or `N` as vertex attributes silently kills rendering (geometry vanishes, no errors). Use `TDPointColor()` for vertex color, derive normals via `dFdx/dFdy(worldPos)` in fragment shader
- **lineMAT per-line color** — `linecoloratt='Color'` reads per-primitive `Color` (RGBA incl alpha). Without it, lines use flat `colorr/g/b`
- **lineMAT width vanishes under normalized camera** — `widthaffectedbyfov=ON` scales width with orthowidth; normalizing the cam (orthowidth 1920→1.0) makes lines sub-pixel/invisible. Fixed-resolution output: `widthaffectedbyfov=OFF` + pixel widths
