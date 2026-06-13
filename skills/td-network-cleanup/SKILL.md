---
name: td-network-cleanup
description: Clean up TouchDesigner network layout — alignment, spacing, annotations, colors. Use after builds to organize operators.
---

# Cleanup

Organize operator networks into clean, readable layouts. Only moves, resizes, colors, and annotates — never creates functional operators or changes parameters.

## Process

0. **Load `td-node-layout` skill** — required for spacing, padding formulas, and containment checks. Do not skip this step
1. **Survey** — `list_operators(path, depth=2)` for positions, sizes, overlaps, and existing annotations. Use `get_connections(path, graph=true)` for full signal flow topology in execution order
2. **Delete old annotations** — destroy any existing `annotateCOMP` ops before reorganizing
3. **Plan layout** — identify functional groups, chains, parallel branches. Independent groups go **side-by-side** when they have similar vertical extent (saves space vs stacking). Use actual `nodeWidth`/`nodeHeight` to compute bounding boxes. Replace long cross-network wires with selectCHOP `chop` parameter references — especially for merge inputs and fan-out patterns
4. **Apply layout** — use `reposition_operators` to batch-move operators (see Positioning below)
5. **Check vertical spacing** — ensure enough Y gap between groups for annotation headers (60px top padding) + 20px gap between annotations. If groups are too close, move ops down before annotating
6. **Compute annotation bounds** — for each group, find min/max X/Y from actual operator positions + sizes, then add padding (25px sides/bottom, 60px top). Don't guess dimensions — calculate them
7. **Add annotations** — `annotation(parent_path=..., comment=...)` around every functional group. All groups get annotated, not just complex ones
8. **Verify containment** — for each annotation, confirm all ops in the group satisfy: `op.nodeY >= ann.nodeY + 25` (bottom padding) and `op.nodeY + op.nodeHeight <= ann.nodeY + ann.nodeHeight - 60` (60px top padding = 25px content gap + ~35px header). If any op fails, fix the annotation or move the op
9. **Verify no annotation overlaps** — check that no two annotations share any area. For each pair: `ann1.nodeY + ann1.nodeHeight + 20 <= ann2.nodeY` (vertically stacked) or `ann1.nodeX + ann1.nodeWidth + 20 <= ann2.nodeX` (side by side). Fix before proceeding
10. **Apply colors** — only for special patterns (see Operator Colors below). Do not color by family
11. **Final verify** — `list_operators` one more time. Check for: ops overlapping annotation headers, excessive margins, misaligned annotations, backward wires. Fix anything found. Repeat until clean

## Positioning & Colors

- **Batch reposition** — use `reposition_operators(parent_path, positions)` with a dict of `{name: [x, y]}`. Preferred over `execute_code` for moving multiple ops
- **Single op** — use `edit_operator(path, nodeX, nodeY)` for one-off moves
- **Annotation edits** — use `annotation(path=..., ...)` to update position/size/comment/color in place. No need to delete and recreate
- **Operator color** — use `edit_operator(path, color=[r, g, b])`

## Annotation Rules

Follow `td-node-layout` skill for spacing, alignment, and sizing formulas. Additional cleanup-specific rules:

- Use `annotation` tool with `parent_path`, `comment`, `nodeX`, `nodeY`, `width`, `height`, `color` (RGB array 0-1)
- **`comment` writes `Titletext` ONLY** — the heading; it never touches the body. For any explanation longer than a heading, follow up with `set_parameters` on the annotateCOMP: `Titletext` = short heading, `Bodytext` = the explanation. Body pars: `Bodyfontsize` (def 10), `Bodywordwrap` (def on), `Bodylimitwidth`/`Bodymaxwidth`. Batch in one `set_parameters` call
- Compute bounds from actual `nodeWidth`/`nodeHeight` — never guess
- Every functional group gets an annotation, even small ones
- **Short titles, body for detail** — `Titletext` = single word / short phrase ("Render", "Data Select"). Put explanatory sentences in `Bodytext`, never the title (font scales down → long titles unreadable)
- **Colors**: muted backgrounds (~0.25–0.35 range) — blue-gray `[0.25, 0.28, 0.35]`, green `[0.22, 0.33, 0.22]`, purple `[0.30, 0.22, 0.33]`, amber `[0.35, 0.30, 0.18]`
- **Stacked alignment** — after computing per-group bounds, unify X and width across all stacked annotations. All should share left edge and width for a clean column

## Operator Colors

Do **not** color operators by family — that's already visually obvious from operator shape/type. Only color for special patterns where two related ops need to stand out as a pair. E.g. feedback loop: color both feedbackPOP and its target null the same color. Default gray is 0.67, 0.67, 0.67.

## Layout Reference

Load the `td-node-layout` skill for full positioning rules (spacing, flow direction, special patterns, annotation layout). Follow naming in `td-general` when verifying operator names.

## Pitfalls

- **Annotations are properties not parameters** — `nodeX`, `nodeY`, `nodeWidth`, `nodeHeight` must be set via `execute_code`, not `set_parameters`
- **Text dumped in the title** — `annotation(comment=...)` sets `Titletext` only; explanation must go in `Bodytext` via `set_parameters` (see Annotation Rules)
- **Forgetting to delete old annotations** — leftover `annotateCOMP` ops overlap with new ones
- **Not verifying containment** — after creating annotations, check all ops are inside the box and below the header
- **Insufficient vertical spacing** — minimum ~105px Y gap between last op in one group and first op in the next (25px bottom padding + 20px gap + 60px top padding)
- **Never use `networkbox` mode** — hides the op from Python, making it undeletable via code
