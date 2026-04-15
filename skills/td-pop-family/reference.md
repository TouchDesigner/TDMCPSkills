# POP Reference — Operators & Attributes

## Reserved Attributes

- `P` float3 — position
- `N` float3 — normal
- `T` float4 — tangent (4th = polarity)
- `Color` float4 — RGBA
- `Tex` float3 — texture coords
- `PointScale` float — per-point scale
- `LineWidth` float — line width
- `Weight` float — from Field POP

## Common Attributes (conventions — not auto-created, you define them)

- `Speed` float — speed
- `Accel` float3 — acceleration
- `Dir` float3 — direction
- `Dist` float — distance
- `Disp` float3 — displacement
- `Orientation` float4 — quaternion (xyz=vector, w=scalar)
- `Rotation` float3 — euler rotation
- `Up`, `Forward` float3 — orientation vectors
- `Nebr` — neighbor indices (from neighborPOP)
- `NumNebrs` — neighbor count

## particlePOP Attributes (auto-created by particlePOP)

- `PartVel` float3 — particle velocity
- `PartId` int — unique particle ID
- `PartAge` float — time since birth
- `PartLifeSpan` float — total life expectancy
- `PartDrag` float — per-particle drag
- `PartMass` float — per-particle mass
- `PartForce` float3 — accumulated force (written by forceradialPOP)

## Attribute Component Access

- Dot notation (preferred): `P.x`, `P.y`, `P.z`, `PartVel.x`, `Color.r`
- Index notation: `P(0)`, `P(1)`, `P(2)`
- Swizzle: `P.xy`, `Color.rgb`

## particlePOP Capacity

- `numpoints` (pointgeneratorPOP) — emission positions, NOT particle count
- `birthrate` (particlePOP) — particles emitted per second
- `life` (particlePOP) — seconds each particle lives
- `maxparticles` (particlePOP) — hard cap on simultaneous particles (default: 1000)
- **Rule of thumb**: set `maxparticles` ≥ `birthrate` × `life` or particles will be culled

## Read-Only Built-Ins (for parameter menus, not output)

- `_PointI` / `_PointU` / `_PointCy` — point index (int / normalized / cyclic)
- `_PrimI`, `_VertI` — same for prims/verts
- `_DimI[]` — position in dimensional structure
- `_StepSeconds` / `_StepFrames` — time since last cook

## Attribute Naming

- Derivative-defined: uppercase first letter (`Weight`, `Color`, `PartId`)
- User-defined: capital first letter for persistent/non-temporary attributes, lowercase for temporary/internal
- Alpha chars only, must start with letter

## Python POP Data Access

- `n.numPrims()` / `n.numPoints()` — methods, not properties
- `n.prims('AttrName', startIdx)` → AttribList of values from startIdx onward
- `n.primAttributes` / `n.pointAttributes` — list available attribute objects

## Generators

- `gridPOP` — structured grid (rows/cols)
- `boxPOP` — 3D grid
- `spherePOP` / `torusPOP` / `tubePOP` / `circlePOP` / `linePOP` / `rectanglePOP` — primitives
- `randomPOP` — random scatter in volume
- `sprinklePOP` — scatter on surface
- `pointgeneratorPOP` — most flexible
- `particlePOP` — built-in birth/death/forces/integration
- `patternPOP` — ramp/sine/pulse distributions
- `curvePOP` — Bezier/BSpline/Cardinal

## Converters

- `soptoPOP` / `choptoPOP` / `dattoPOP` / `toptoPOP` — family converters
- `alembicInPOP` / `fileinPOP` / `pointfileinPOP` — file import

## Math (No Code)

- `transformPOP` — translate/rotate/scale (Map page for per-point drive)
- `mathPOP` — arithmetic + functions
- `mathmixPOP` — multi-operation math processor (sign, abs, mult, clamp, mix, ifelse, etc.)
- `mathcombinePOP` — chain multiple operations (add, mult, ifelse, normalize, dot, cross, mix, comparison). The workhorse for no-code POP logic
- `normalizePOP` / `limitPOP` / `rerangePOP` / `quantizePOP` / `trigPOP` — value ops
- `noisePOP` — Perlin/simplex/sparse noise displacement

## Attributes

- `attributePOP` — create explicit attribute (any type/class/arrays)
- `attributecombinePOP` — cherry-pick attrs from inputs
- `attributeconvertPOP` — transfer between point/vert/prim
- `normalPOP` — compute normals + tangents. Set `tang=alwayscompute` for pbrMAT (PBR lighting requires tangents)

## Spatial

- `neighborPOP` — GPU spatial hash, adds Nebr/NumNebrs
- `proximityPOP` — closest point on input 2
- `rayPOP` — cast rays onto input 2 (hit pos, normal, distance)
- `fieldPOP` — Weight (0-1) by distance to shape. `specpop` = data POP (1 point = 1 field instance, NOT a shape generator)
- `lookuptexturePOP` — sample TOP at point positions. **Defaults**: `lookupindexattr0/1` = `P(0)`/`P(1)` (world position). Set to `Tex(0)`/`Tex(1)` when sampling by UV
- `lookupchannelPOP` — map attribute value to CHOP curve

## Simulation / Time

- `feedbackPOP` — frame-to-frame loop (1 input = reset, loop automatic)
- `cachePOP` / `cacheblendPOP` / `cacheselectPOP` — store/interpolate/select cached frames
- `trailPOP` — line strips from point history over N frames
- `linemetricsPOP` — per-point direction/distance to neighbors along lines
- `skinPOP` — connect line strips into triangle/quad surfaces

## Topology

- `primitivePOP` — add/remove primitives
- `convertPOP` — between tri/quad/line/point
- `extrudePOP` / `subdividePOP` / `facetPOP` / `polygonizePOP`

## Flow Control

- `mergePOP` / `switchPOP` / `selectPOP` / `deletePOP` / `groupPOP` / `sortPOP` / `copyPOP` / `nullPOP` / `blendPOP`

## GLSL

- `glslPOP` — default choice, one attr class, multi-pass support
- `glsladvancedPOP` — multi-class read/write, extra outputs, index buffer writes
- `glslcopyPOP` — N copies with custom GLSL per copy
- `glslcreatePOP` — create points from scratch
- `glslselectPOP` — select extra output from glsladvancedPOP

### glslPOP Compute Shader API

**Setup parameters:**
- `computedat` — name of textDAT containing compute shader
- `outputattrs` — space-separated attribute names to write (e.g., `"P Vel Color"`)
- `outputaccess` — `writeonly` (default) or `readwrite`. Use `readwrite` when the shader needs to read its own output (e.g., reading other points' positions in a simulation)
- `attr` / `attr0name` / `attr0customname` / `attr0type` / `attr0numcomps` — Create Attributes page (sequence). Custom attrs like `Vel` must be created here before they appear as SSBO buffers

**Buffer access in compute shader:**
```glsl
// Current point index
uint idx = gl_GlobalInvocationID.x;

// Total number of points (via SSBO length)
int numPts = P.length();

// Read/write output attributes by index (SSBO arrays)
vec3 pos = P[idx];           // read position of any point
vec3 vel = Vel[idx];         // read custom attribute
P[idx] = newPos;             // write position
Vel[idx] = newVel;           // write custom attribute
PointScale[idx] = 3.0;       // write built-in float attribute

// Read input attributes (from wired input, read-only)
vec3 inputPos = TDIn_P();              // current point from input 0
vec3 otherPos = TDIn_P(0, otherIdx);   // specific point from input 0
```

**Important notes:**
- With `outputaccess="writeonly"`, you can ONLY write to output buffers. To read other points' positions in a simulation loop, you MUST set `outputaccess="readwrite"`
- Custom attributes (e.g., `Vel`) must be added in the Create Attributes sequence page AND listed in `outputattrs`
- `TDPerlinNoise()` is NOT available in compute shaders — write custom noise or use sampler input
- Multi-pass: set `npasses=N`, `prevpassoutput=true` for iterative solvers
- Guard against out-of-bounds: `if (idx >= uint(numPts)) return;`
- GLSL compile errors: read the docked `<name>_info` infoDAT for detailed errors with line numbers (the operator's `.errors()` only shows "Compile failed")

### glslcopyPOP Compute Shader API

Copies source geometry N times with custom GLSL per copy.

**Inputs:**
- Input 0: source geometry (what to copy)
- Input 1: template points (optional). Template point count determines number of copies. Without template, use `ncy` parameter

**Setup parameters:**
- `ptcomputedat` — DAT containing point compute shader. **Must be the auto-docked `<name>_ptCompute` DAT** — separate textDATs compile without errors but `TDCopyIndex()` returns 0 for all copies
- `ptoutputattrs` — point attributes modified by shader (e.g. `"P N"`)
- `sampler`, `vec`, `buffer`, `array`, `const` sequences — same as glslPOP
- `attr` sequence — create custom output attributes (same as glslPOP)

**Buffer access in compute shader:**
```glsl
void main() {
    const uint id = TDIndex();          // output point index (global across all copies)
    if (id >= TDNumPoints()) return;

    uint copyIdx = TDCopyIndex();       // which copy (0-based)
    uint srcIdx = TDInputIndex();       // matching point index on source input

    // Read source geometry (input 0)
    vec3 srcPos = TDIn_P();             // current point from source
    vec3 otherSrc = TDIn_P(0, otherIdx); // specific source point

    // Read template (input 1) — defaults to TDCopyIndex() for element ID
    vec3 worldPos = TDTemplate_P();                  // template position
    float myAttr = TDTemplate_MyCustomAttr();        // any custom template attribute
    vec3 specificPt = TDTemplate_P(someIdx);          // specific template point

    // Write outputs
    P[id] = srcPos + worldPos;
    N[id] = someNormal;
    MyOutputAttr[id] = vec4(1.0);

    TDUpdatePointGroups();  // required at end
}
```

**Other shader types:**
- `vertcomputedat` → vertex shader (`TDVertIndex()`, `TDNumVertsBatch()`)
- `primcomputedat` → primitive shader (`TDPrimIndex()`, `TDNumPrimsBatch()`)

**Utility functions:**
- `TDTemplateNumPoints()` — number of template points
- `TDInputNumPoints()` — number of source input points
- `TDUpdateTopology()` — call in vertex shader if modifying topology
- `TDUpdateLineStripsInfo()` — call if modifying line strip topology

## POP → TOP

- `glslmultiTOP` with `buffer0pop`/`buffer0attr`/`buffer0name` — read POP attrs as textures via `TDBuffer_*()`
- `glslMAT` with Attributes page — per-vertex via `TDAttrib_*()` in vertex shader
- `poptoDAT` / `poptoCHOP` — CPU download (causes stall)

## Sequence Parameters (mathmixPOP / mathcombinePOP)

`vec`/`comb` sequence pars don't exist by default. Add blocks before setting values:
```python
n.par.comb.sequence.numBlocks = 3  # creates comb0*, comb1*, comb2*
n.par.vec.sequence.numBlocks = 2   # creates vec0*, vec1*
```

## mathcombinePOP Operations

The chain workhorse. Each operation reads from previous results:
- Arithmetic: add, subtract, multiply, divide, power
- Comparison: less-than, greater-than → 0/1
- Branching: `ifelse(a, b, condition)` — select between values
- Vector: normalize, dot, cross, length
- Blending: `mix(a, b, weight)`
- Temp attrs: create intermediates, delete with `delattrs`/`delnewattrs`
- Second input: pull attrs from another POP (rename to avoid collision)

## mathmixPOP Floor Bounce Pattern

Floor collision at Y=0 using 3 combine blocks:
- **comb0**: `sign`, scopeA=`P.y`, result=`bSign` — store floor side (1 above, -1 below)
- **comb1**: `abs`, scopeA=`P.y`, result=`P.y` — reflect position above floor
- **comb2**: `mult`, scopeA=`PartVel.y`, scopeB=`bSign`, result=`PartVel.y` — flip velocity on impact
- Set `delattrs=bSign` to clean up temp attribute

## feedbackPOP Lifecycle

1. `initializepulse` — reset to input geometry (no playback)
2. `startpulse` — begin playback (re-reads input, starts)
3. `play` toggle — pause/resume without reset
4. Wire Reset custom par: `feedbackPOP startpulse expr: parent().par.Reset` (no `.pulse()`)
