---
description: Network layout conventions — spacing, flow direction, positioning patterns. Use during any build or cleanup that places operators.
---

# Layout Conventions

Standard positioning rules for TouchDesigner networks. Loaded by td-build-planning and td-network-cleanup skills.

## Core Spacing

- **Horizontal spacing**: 175px (130 width + 45 gap) — standard for POP/TOP/CHOP chains
- **Vertical spacing**: 125px between parallel chains
- **Flow**: left-to-right always. No backward connections (exception: feedback loops)
- **Main chain Y**: 0
- **Coordinates**: Y-axis up, `nodeY` = bottom edge

## Positioning Patterns

- **Prefer a single Y=0 row** when all ops fit horizontally. Add a second row only for true branches (parallel paths, secondary-input feeders). Feeder chains that merge into the main chain sit on Y=0 to the left of the merge, not on a separate row
- **No wires through operators** — stagger multi-input sources vertically
- **Multi-input nodes** — all sources left of target; input 0 = highest Y; target at Y centroid
- **Fan-in stacking** — when multiple operators feed one target (e.g. 3 constants → joinCHOP), stack sources vertically at the same X, target to the right. Never spread inputs horizontally at the same Y
- **No same-X inputs** — an input operator must always be to the LEFT of its target (lower X). No operator shares the same X as the operator it feeds into — wires must never go backward or straight down
- **Helper ops** (e.g. LFO driving a parameter) — directly above target, same X
- **Secondary/debug branches** — below main chain
- **Bridge nodes** — null at intermediate Y to connect chains at different levels
- **Anchor to origin** — main chain at Y=0, first annotation left edge at X=0

## Special Patterns

- **GLSL DAT sandwich** — for each glslTOP/glslmultiTOP/glslMAT, stack vertically at the same X: info DAT *above* the operator (Y + 125), shader/pixel DAT *below* (Y - 125). The operator is the filling in a DAT sandwich. For glslMAT, docked DATs follow the parent automatically
- **Other text DATs below their operator** — 125px below associated Python op
- **Bypass null pattern** — when a switch bypasses an effect, place bypass null directly above the effect (same X, Y + 125), not above the switch
- **Secondary inputs** — operators feeding secondary inputs (index 1+) go *below* the main chain and at the *same X as the preceding main-chain op* (not the target), so wires flow left-to-right and don't cross the primary input
- **selectCHOP `chop` param** — use `chop` parameter instead of physical wires to reference remote CHOPs. Eliminates long cross-network wires and keeps regions self-contained. Especially useful for fan-out (one source → many consumers)
- **Merge feeder column** — when a mergeCHOP has many inputs, create selectCHOPs (via `chop` param) at the same X left of merge. Order by Y to match input index (highest Y = input 0) — connection lines won't cross

## Annotation Layout

- **Reading order** — arrange annotations left-to-right, top-to-bottom like text
- **Header alignment** — all annotations at the same level should have their tops (`nodeY + nodeHeight`) aligned, even if that means slightly resizing some annotations to match
- **Short titles** — single words or very short phrases (e.g. "Render", "Data Select", "Material"). Long descriptions become unreadable when the annotation is small because the font scales down
- **Match heights** of adjacent annotations for visual rhythm. Oversizing one annotation to match its neighbor is fine if it creates a cleaner grid
- **Same width** for stacked or adjacent annotations when sizes are close — unify to the wider one
- **Padding**: 25px sides/bottom, 60px top (25px content gap + ~35px header). Use these for bounding-box calculations
- **20px gap** between adjacent annotations, never overlap
- **Containment check**: every op must satisfy `op.nodeY >= ann.nodeY + 25` (bottom) and `op.nodeY + op.nodeHeight <= ann.nodeY + ann.nodeHeight - 60` (top/header)
- **Context-dependent rows** — one row or multiple rows depending on network shape. When a sub-chain hangs below the main chain, its annotation extends down but keeps its header aligned with the row
- **Stacked annotations** — align left edges (same X) and match widths across all stacked annotations. Use the widest group's width for all
- **Uniform gaps** — all gaps between annotations should be 20px. Apply this consistently in both directions

## Node Sizing

- Default operator size: 130x90
- COMPs are often wider (160+) and taller (130) — add extra spacing
- **Top-align mixed sizes** — when a COMP sits next to shorter DATs in the same row, align top edges (`nodeY + nodeHeight`). E.g. DAT at Y=0 (top=90), COMP should be at Y=90-130=-40 (top=90)
- Always use actual `nodeWidth`/`nodeHeight` from `list_operators` — don't assume defaults
