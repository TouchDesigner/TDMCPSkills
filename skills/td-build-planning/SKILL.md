---
description: Plan TouchDesigner builds — scout networks, decide operators, allocate positions, phase work. Use before any multi-operator build.
---

# Build Planning

Plan before building. Scout the target network, decide what to create, allocate positions, phase the work.

## Process

### 1. Scout

Understand what exists before adding anything.

- `project_info` — project name, `rootPath` + `parentShortcut` from /perform winop, open panes. **Always call first** — use `rootPath` for all subsequent tool calls instead of assuming `/project1`
- `list_operators(path, depth=2)` — structure, positions, types, overlaps, existing annotations
- `get_connections(path, graph=true)` — full signal flow topology in execution order with cycle detection
- `get_errors(path)` — existing problems
- `get_operator_info(path)` — details on specific ops (position, params, flags). Add `include_extensions=true` for COMPs with extensions to see methods, clone source, config

Capture: rightmost X (for insertion point), Y range in use, existing null endpoints, available families, any overlaps to fix.

### 2. Plan operators

For each operator to create, decide:
- **Type** — opType name (e.g. `noiseTOP`, `blurTOP`, `lfoCHOP`)
- **Name** — follow naming in `td-general` (`optype_purpose`)
- **Family** — determines which builder skill to consult
- **Position** — X,Y following the `td-node-layout` skill conventions
- **Parameters** — use `get_help` tool for correct par names
- **Connections** — what wires into what, which input index

### 2b. Plan data flow

- **Same family** → wire directly
- **Cross-family** → expression: `op('chop')['chan']`, `op('table')['row','col']`
- **Cross-COMP** → select operators or parent shortcuts
- **Into/out of COMP** → in*/out* operators
- **State** → readonly custom pars with extension expressions (see td-comp-architecture)

### 3. Allocate positions

Load `td-node-layout` skill before placing any op. Start from the insertion point (rightmost existing X + 175, or 0 if empty). Use 210px Y offset between parallel chains to leave room for annotation headers during td-network-cleanup.

Track a position map as you go: `{op_name: [x, y]}`. Update it after each build step.

### 4. Phase the build

Group into phases based on dependencies:

- **Phase 1**: Infrastructure — COMPs, in/out ops, structural containers
- **Phase 2**: Sources — generators, inputs, constants (no upstream dependencies)
- **Phase 3**: Processing — operators that consume sources
- **Phase 4**: Wiring — cross-family references, expressions, select ops
- **Phase 5**: Parameters — set values that reference other ops (must exist first)
- **Phase 6**: Init — `pulse_parameter` for `reinitextensions`, `initializepulse`, `startpulse` as needed

Independent operators within a phase can be created together via `build_network`.

### 5. Prefer build_network

`build_network` creates multiple operators and wires them in one MCP call. Always prefer it over individual `create_operator` + `wiring` sequences. Plan your operator list and connection list upfront.

## Pitfalls

- **Not scouting first** — creating at 0,0 overlaps existing ops
- **Forgetting node width** — 130px default, COMPs/DATs can be much larger
- **Single-phase thinking** — complex builds need multiple phases with dependency ordering
- **Wiring across families** — impossible, use expressions or conversion ops (topToCHOP, choptoSOP)
- **Relative paths across COMPs** — break on restructure, use parent shortcuts
- **Referencing non-null ops** — inserting a new op breaks all downstream references, always reference nulls
- **Missing in* op** — COMP has no input connectors until you create an in* op inside it
- **in\* operator `connectorder`** — when a COMP has multiple in\* ops (any family: inPOP, inTOP, inCHOP, etc.), set `connectorder` explicitly (0=top connector, 1=next, etc.). Default ordering is by creation time, not name — gets wrong after edits/deletions
- **pbrMAT without environment light** — renders black. Plan an environmentlightCOMP + moviefileinTOP (env map) alongside any pbrMAT
- **build_network partial failure** — if it errors mid-way (e.g. bad parameter name), operators created before the error persist with numbered suffixes (e.g. `logic_top_hit1`). Always check `list_operators` after a failed `build_network` and clean up orphans
- **Camera far clipping** — default cameraCOMP `far` can clip dynamic cameras. If camera distance is computed (auto-fit), set `far` high enough or expose as custom par

### 6. Finish

Make the build user-friendly and self-contained:

- **Parent shortcut** — set `parentshortcut` on the baseCOMP (e.g. `FluidSim`). Reference internally as `parent.FluidSim.par.Name`
- **Custom parameters** — expose all tunable values on the parent COMP. Use Headers and sections for organization, sort logically. Internal operators reference via `parent().par.Name`
- **in\* with defaults** — create `inTOP`/`inCHOP` for external inputs. Wire a default source to the in\*'s input 0 — used when nothing is connected externally
- **Pulse linking** — for Reset/Init pulses, set each target's pulse parameter expression to `parent().par.Resetpulse` directly. Multiple ops can reference the same parent pulse — no callback DAT needed
