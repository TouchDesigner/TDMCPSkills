# glsladvancedPOP Reference

Multi-class read/write compute shader. Use for simultaneous point/vert/prim writes or index buffer (`I[]`) access.

## Buffer Allocation

SSBOs only exist when max allocation > 0:
- `oTDPoint_*[]` — needs `maxpointsmode`=custom, `maxpoints`>0
- `oTDPrim_*[]`, `oTDVert_*[]`, `I[]` — needs `maxtrianglesmode`=custom, `maxtriangles`>0
- **"Undeclared identifier" = check allocation is non-zero** (expressions may not evaluate if input isn't connected yet)

## Output Attributes

Both required for custom attributes — missing either one causes "undeclared identifier" or missing `TDIn` accessors downstream:
- **Create Attribs** — defines storage (class, name, type)
- **Output Attributes** (`ptoutputattrs`/`primoutputattrs`/`vertoutputattrs`) — enables SSBO for writing AND enables `TDIn` accessor generation on downstream operators
- **Rule**: always add custom attributes to BOTH Create Attribs AND the matching output attributes parameter. A prim Create Attrib needs `primoutputattrs`, a point Create Attrib needs `ptoutputattrs`

## Output Count Control

Output more points/triangles than input: `maxpointsmode`=custom + `topoinfo`=fromparams + `pointcountmode`=set. Same for triangles.

## Multi-Pass

- `npasses`=N, `prevpassoutput`=true — pass N+1 reads pass N output
- `initoutputattrs`=true **reinitializes each pass** — data doesn't carry forward. Copy explicitly or use single-pass
- Large local arrays (>~128 vec3) can trigger internal TD bugs

## Cache Feedback Pattern

For iterative processing (cut→cache→cut again), use `cachePOP → nullPOP (locked)`:
- cachePOP captures the glsladvancedPOP output via selectPOP
- nullPOP after cachePOP is **locked** — holds stable geometry, breaks cook dependency loops
- **Unlock-cook-lock sequence**: `null.lock = False; null.cook(force=True); null.lock = True` to refresh from new cache data
- switchPOP selects between initial input (index 0) and locked null (index 1)
- **cpureadback=true on deletePOP** — when the pipeline includes a deletePOP before caching, enable `cpureadback`. New point/primitive allocations from glsladvancedPOP need CPU-side topology info for the next generation's buffer sizing

## Pitfalls

- **Create Attribs name conflict** — if input data has an attribute with the same name as a Create Attribs entry, compilation fails (`AttPrimData1: nameless block contains a member that already has a name at global scope`). Use `attributePOP` with `deleteprim`/`deletepoint` to strip conflicting attrs before re-entry in feedback/cache loops
- **`centroid`** — GLSL 4.60 reserved keyword
- **Vertex soup fallback** — if `I[]` unavailable: `convertPOP`(deleteprims) + `primitivePOP`(set, triangles, all)
