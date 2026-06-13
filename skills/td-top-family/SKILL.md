---
name: td-top-family
description: TOP chains — image processing, compositing, render pipelines, feedback loops. Use when building texture operator chains.
---

# TOP Networks

Image processing, compositing, render pipelines, and feedback loops using Texture Operators.

## Source Types

- `noiseTOP`, `rampTOP`, `constantTOP` — generated textures
- `renderTOP` — renders scene (needs camera + geometry). Lights optional (constantMAT ignores lighting). Keep `bgcolora=0` (default) for transparent background — composite over bg separately via compositeTOP or transformTOP
- `moviefileinTOP`, `videodevinTOP` — external input
- `inTOP` — receives from COMP input connector
- `selectTOP` — references TOP from elsewhere
- `feedbackTOP` — previous frame

## Processing Operators

- `levelTOP` — brightness, contrast, gamma, opacity
- `blurTOP` — blur/sharpen
- `compositeTOP` — layer compositing (over, add, multiply, screen)
- `transformTOP` — translate, rotate, scale
- `cropTOP`, `fitTOP` — crop, resize, fit
- `edgeTOP` — edge detection
- `hsvTOP` — HSV adjust
- `lookupTOP` — color lookup
- `resolveTOP` — resolve MSAA
- `glslmultiTOP` — custom GPU processing (see td-glsl-shaders skill)

## Output Convention

End every TOP chain with a `nullTOP`. Set `viewer=true` on important outputs.

## Resolution & Format

- TOPs inherit resolution from first input. No input = project resolution
- Set explicit resolution when needed
- `rgba8fixed` — default, clamps [0,1]
- `rgba32float` — for feedback, random, data, HDR, anything outside [0,1]
- `rgba16float` — good middle ground (depth buffers, etc.)

## Conversion

- `choptoTOP` — converts CHOP channels to a TOP. `dataformat` controls channel packing: `r` (default, 1 channel per row), `rg` (2), `rgb` (3), `rgba` (4 channels per RGBA row). Use `rgba` + `format=rgba32float` for data textures (e.g. animation bakes)

## Pitfalls

- **8-bit clamps data** — default format clamps to [0,1], use rgba32float for data
- **compositeTOP input order** — input 0 = foreground (on top), input 1 = background. Opposite of Photoshop
- **feedbackTOP format mismatch** — must match chain, mismatched = silent data corruption
- **Resolution inheritance** — unexpected resolution when first input changes
- **renderTOP needs geometry + camera** — set `geometry` and `camera` parameters
- **cameraCOMP projection** — menu value is `ortho` not `orthographic`
- **selectTOP stale references** — renaming source silently breaks the `top` parameter
- **moviefileinTOP paths** — relative to .toe file, not project root
- **depthTOP format** — use `pixelformat=rgba16float` + `depthspace=reranged` for usable 0-1 values
- **constantTOP defaults to white** — RGBA is (1,1,1,1) not (0,0,0,0). Set `colorr/g/b=0` and `alpha=0` for a clear/empty image
- **feedbackTOP resolution** — on reset, uses input resolution; next frame onward, uses `top` target's resolution. If these differ, resolution changes after first frame. Set `outputresolution='custom'` referencing a single source of truth (custom parameter) for consistent behavior
- **Phantom DAT auto-create** — every `glslTOP` creation spawns companion DATs at the default names `<glslOpName>_pixel` / `_compute` / `_info` **unconditionally**, regardless of (a) whether you pre-set `pixeldat` in the parameters dict at creation, (b) whether companion DATs with custom names already exist as siblings, or (c) the operator order in `build_network`. If the default name is already taken, TD adds a `1` suffix to the phantom. **Mandatory post-build sweep**: after creating any `glslTOP` (or a `build_network` containing one), enumerate `<glslOpName>_pixel/_compute/_info` (and the `1`-suffixed variants), delete any that aren't the DAT you actually docked. Same trap for cross-COMP refs via `infoDAT.par.op`
- **Sibling path notation** — `./glsl1_pixel1` fails silently as a sibling reference (warning only). Use bare name `glsl1_pixel1`. `./` is reserved for children inside the current op
- **constantTOP / noiseTOP 3D-mode trap** — both expose `type=texture3d` in the Output Type menu but **have no `customdepth` parameter**, so the output collapses to a single-slice 3D texture (effectively 2D). For a real volumetric seed (e.g. when a feedbackTOP's target is 3D), use a small `glslTOP` with `type=texture3d` + `depth=custom` + a one-line shader instead
- **Alpha-blended render corrupts framebuffer alpha** — transparent MATs leave the renderTOP's alpha channel wrong even when RGB looks right. Force opaque output (`reorderTOP outputalphachan=one`) or use MAT separate-alpha blend (`srcblenda=zero, destblenda=one`). Verify RGB via `inspect_values`, NOT the thumbnail (which composites alpha and lies)
