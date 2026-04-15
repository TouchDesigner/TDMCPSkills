---
description: Build CHOP chains for audio, LFOs, animation, and data-driven control. Use when creating CHOPs or driving parameters from CHOPs.
---

# CHOP Networks

Build CHOP chains for audio, animation, LFOs, and data-driven parameter control. Prefer operator-driven animation (lfoCHOP, timerCHOP) over Python or `absTime.seconds`.

## Scope

**IN**: LFOs/oscillators, audio input/analysis, animation curves, math ops, filtering/smoothing, channel manipulation, timing, data conversion, selective cooking, CHOP references
**OUT**: Parameters on other families driven by CHOP values via expressions

## Sources

- `lfoCHOP` — periodic oscillation
- `waveCHOP` — waveform generator
- `noiseCHOP` — smooth random (types: sparse, harmonic, random — check `get_help`)
- `audiodevinCHOP` — audio input
- `oscCHOP`, `midiinCHOP` — external data
- `animationCHOP` — keyframed curves
- `timerCHOP` — timed sequences, state machine (see `reference.md`)
- `constantCHOP` — fixed values. Sequence pars: `const0name`/`const0value`, `const1name`/`const1value`, etc.
- `parameterCHOP` — reads custom parameters as CHOP channels. **Has separate `custom` and `builtin` toggles.** Default: `custom=true, builtin=false`. Must enable `builtin=true` to capture built-in pars like `tx`/`ty`/`tz`. Filter pattern alone won't work if the category toggle is off

## Sequence Expansion

Built-in sequence parameters (constantCHOP `const`, glslTOP `vec`, etc.) default to 1 block. The `set_parameters` tool auto-expands sequences when you set a parameter index that doesn't exist yet — e.g. setting `const3name` on a 1-block CHOP auto-creates blocks 0–3

## Conversion (GPU → CPU)

- `poptoCHOP` — extract POP attributes as CHOP channels. **Copies GPU→CPU, can be heavy.** Extract modes: `points`, `primitives`, `vertices`. Attribute channels named by attribute + component index (e.g. P vec3 → `P_0`, `P_1`, `P_2`)
- `soptoCHOP` — extract SOP point positions, normals, UVs as CHOP channels

## Conversion (DAT → CHOP)

- `dattoCHOP` — converts DAT table columns to CHOP channels. Set `output=chanpercol`, `firstrow=names`. Use `extractcols=bynames` + `colnames` to pick specific columns

## Processing

- `mathCHOP` — arithmetic + combine operations. Key modes: `chopop` (avg/sub between inputs), `chanop` (len = vector magnitude, add/sub across channels), `preop`/`postop` (negate/square/root per value)
- `functionCHOP` — compiled math functions: atan2, sqrt, sin/cos/tan, asin/acos, log, pow. Binary ops (atan2, pow) use two inputs. Set `angunit=degrees` for trig output
- `lookupCHOP` — index-based gather: input 0 = index values, input 1 = lookup table. Set `index1`/`index2` to match index range (use expr `me.inputs[1].numSamples-1` for generic max)
- `shuffleCHOP` — reorganize samples. `method=spliteveryn` + `nval=2` splits interleaved samples into separate channels (even/odd)
- `filterCHOP`, `lagCHOP` — smoothing. lagCHOP pars: `lag1`, `lag2` (not `lag`), `lagunit`
- `limitCHOP` — clamping
- `expressionCHOP` — custom math per sample. **Runs Python per sample per frame — can be heavy.** Consider compiled alternatives (mathCHOP, functionCHOP) when possible
- `audiospectrumCHOP`, `audiobandCHOP` — frequency analysis
- `speedCHOP` — rate of change / integration
- `resampleCHOP` — fix rate mismatches between CHOPs
- `selectCHOP` — channel selection + rename. Use `chop` parameter to reference remote CHOPs without wires (cleaner than physical connections for fan-out). `channames` supports TD pattern matching: `P_[0-2]1`, `t[xyz]`. Rename with `renamefrom: *`, `renameto: t[xyz]`

## Pattern Matching (channames, scope, rename)

`*`, `?`, `[xyz]`, `[0-2]`, `[0-6:2]` (range+step), `|` (union), `~` (exclude). No spaces inside `[]`. Works in `channames`, `scope`, `renamefrom`/`renameto`

## scriptCHOP with modoutsidecook

When a scriptCHOP is driven by an extension, **always** use `modoutsidecook=True` and write data from the extension. Never split logic between extension and scriptCHOP callbacks. Pattern: extension parses data → calls `chop.clear()`, `chop.numSamples = n`, appends channels and writes values. The scriptCHOP callbacks should be empty defaults.

## Output Convention

End every CHOP chain with a `nullCHOP`. Other ops reference it via expression: `op('null_name')['channel']`

Set `cooktype=selective` on output nulls that don't need per-frame updates.

## Debugging

Use `inspect_values(path, include_samples=true)` to read full sample arrays from multi-sample CHOPs (audio, LFOs, animation curves). Without `include_samples`, only the current single value per channel is returned.

## Comparison / Threshold Detection

- **logicCHOP gt/lt/ge/le do NOT compare against boundmin** — use `mathCHOP` (subtract threshold) + `logicCHOP convert=pos` instead. See `reference.md` for patterns
- **CHOPs without wire outputs don't cook** — add a nullCHOP downstream to force cooking
- **feedbackCHOP loops start empty** — bootstrap with switchCHOP + constantCHOP for initial state. Use selectCHOP `chop` param for the backward reference (avoids long wires). See `reference.md`
- **triggerCHOP won't re-fire** when input stays high — use chopexecuteDAT `onOffToOn` for reliable event detection

## Pitfalls

- **No selective cooking on output** — forces entire upstream chain to cook every frame
- **absTime.seconds for animation** — floats lose precision after hours, use lfoCHOP or timerCHOP
- **CHOP reference syntax** — use `op('path')['channelname']` not `op('path').chan('name')`
- **Rate mismatch** — different CHOPs may run at different sample rates, use resampleCHOP
- **noiseCHOP types** — defaults may not be what you want, check `get_help` for type options
- **expressionCHOP performance** — runs full Python interpreter per sample. For pure math (atan2, sqrt, trig), use functionCHOP or mathCHOP instead
- **logicCHOP gt/lt** — does NOT compare against boundmin. See "Comparison / Threshold Detection" above
- **scriptCHOP exec() scope** — `exec(op('dat').text)` in TD Python: nested functions can't access file-scope variables. Use flat loop structure or inline all logic in main loop body
