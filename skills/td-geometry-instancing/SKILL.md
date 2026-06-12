---
name: td-geometry-instancing
description: Geometry instancing — geometryCOMP instance setup, data sources (CHOP/DAT/TOP/POP), transforms, textures. Use when instancing geometry.
---

# Geometry Instancing

Render one piece of geometry many times with per-instance transforms, colors, and textures via geometryCOMP instancing.

## Data Sources

`instanceop` accepts any operator family — pick based on data characteristics:

- **tableDAT** — static/hand-authored. Set `instancefirstrow=names`
- **CHOP** — animated/procedural (LFO, noise, soptoCHOP). Most common
- **TOP** — texture-driven, large instance counts
- **POP (via poptoCHOP)** — particle-driven. GPU→CPU cost

Split sources: `instancetop` (translate), `instancerop` (rotate), `instancesop` (scale). `instanceop` is the default fallback.

## Core Parameters

- `instancing` = `true`, `instanceop` = data source OP
- `instancecountmode` = `oplength` (auto-detect, default)
- `instancefirstrow` = `names` for DAT headers. **Must be lowercase**
- `instanceactive` — per-instance on/off channel

## Transform Channels

Each group has an OP override + X/Y/Z channel selectors:

- **Translate**: `instancetop`, `instancetx/ty/tz`
- **Rotate**: `instancerop`, `instancerx/ry/rz`
- **Scale**: `instancesop`, `instancesx/sy/sz`
- **Pivot**: `instancepop`, `instancepx/py/pz`
- **Rotate-to-vector**: `instancerottoop`, `instancerottox/y/z`
- **Rotate-up**: `instancerotupop`, `instancerotupx/y/z`
- **Transform order**: `instxord` (default: SRT), `instrord` (default: `rx ry rz` = intrinsic xyz)

Channel selectors map to CHOP channel names or DAT column headers.

## Rotate-to-Vector

Orient instances along a direction vector instead of Euler angles.

- `instancerottoforward` — local axis to align. Default `-Z`. Set `posy` for tubes/cylinders
- `instancerottoorder` — `rottoxform` (default), `rotaterotto`, `rottorotate`
- `instancerottoop` + `instancerottox/y/z` — direction source
- `instancerotupop` + `instancerotupx/y/z` — up vector (needed when direction is co-linear with default up)

**Scale caveat**: `instancesy` may not apply correctly in all `instancerottoorder` modes. Fall back to Euler angles if needed.

## Euler Angles from Direction Vectors

To align Y-axis geometry (tube) with direction (dx, dy, dz), with default `instrord` (intrinsic xyz):
- `rx = atan2(dz, sqrt(dx² + dy²))`, `ry = 0`, `rz = atan2(-dx, dy)`

Changing `instrord` changes which formula is correct. Use `functionCHOP(atan2)` + `mathCHOP(chanop=len)` for compiled computation.

## Color & Texture

- `instancecolorop` + `instancer/g/b/a`, `instancecolormode` = `none`/`op`/`constant`
- `instancetexcoordop` + `instanceu/v/w`, `instancetexs` (TOP array), `instancetexindexop` + `instancetexindex`

## Common Patterns

- **Static** — tableDAT → `instanceop`, `instancefirstrow=names`
- **Animated** — lfoCHOP → mathCHOP → nullCHOP → `instanceop`
- **POP-driven** — POP → nullPOP → poptoCHOP → nullCHOP → `instanceop`
- **TOP-driven** — noiseTOP → `instanceop`, pixel data drives transforms

## Pitfalls

- **`instancefirstrow` not set** — first row treated as header or vice versa
- **Menu values not lowercase** — `"Names"` silently becomes wrong entry
- **Channel name mismatch** — selectors must exactly match CHOP/DAT names
- **Missing `instanceop`** — no data source = no instances
- **Instance OP paths from geometryCOMP** — OP reference params resolve from inside the COMP. `../sibling` won't work. Use parent shortcut expressions: `{"expr": "parent.Shortcut.op('chop_name')"}`
