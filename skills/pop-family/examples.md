# POP Examples

## Basic Point Cloud

```
gridPOP → noisePOP (displace P) → noisePOP (create Color) → nullPOP
```

## Particle Simulation (Feedback)

sourcePOP → feedbackPOP → [force chain] → nullPOP (loop back automatic)

## Built-in Particles

```
pointgeneratorPOP → particlePOP → nullPOP
```

ParticlePOP handles velocity, forces, birth rate, life span, integration internally.

## Manual Velocity Integration (No Particle POP)

Inside feedback loop, use mathcombinePOP chain:
1. `positionStep = Velocity * _StepSeconds` (multiply)
2. `P = P + positionStep` (add)
3. Delete temp `positionStep`

## Spatial Interaction (Neighbor)

```
inputPOP → neighborPOP → glslPOP (reads Nebr/NumNebrs) → nullPOP
```

neighborPOP adds Nebr (indices) and NumNebrs via GPU spatial hashing.

## Field-Driven Activation

fieldPOP outputs `Weight` (0-1) based on distance. Animate field origin via CHOPs:
```
source → fieldPOP → lookuptexturePOP (color from Weight via rampTOP) → nullPOP
```

## Lifetime with Respawn (Fixed Count)

mathcombinePOP with InitialData as second input (renamed with `Init` prefix):
1. `dead = Lifetime < 0` (test)
2. `P = ifelse(InitP, P, dead)` — reset position when dead
3. `Lifetime = ifelse(InitLifetime, Lifetime, dead)` — reset lifetime
4. `Lifetime = Lifetime - _StepSeconds` — decrement

No birth/death — fixed particle count with recycling.

## Trail → Tube Geometry

```
feedbackLoop → trailPOP (surftype=rows) → linemetricsPOP → sortPOP (by LineStripIndex)
  → copyPOP (circlePOP input 0, sorted trail input 1) → skinPOP → normalPOP → nullPOP
```

- trailPOP: `surftype=rows` for per-entity line strips
- sortPOP: required for multi-entity trails (interleaved points)
- skinPOP: `skinops=group`, `inc=trailLength+1`
- deletePOP after skin: remove long segments where trail jumped

## GLSL POP as General Compute

Not just for particles — one thread per pixel/tile:
```
gridPOP (rows=height, cols=width, surftype=none) → attributePOP (output storage) → glslPOP
```
Set `outputattrs` to list all written attributes. Downstream: glslmultiTOP reads via TDBuffer_*().

## GPU Instancing

Child geometryCOMP with `instancing=true`, `instanceop=null_render` (POP with position data):
Parent geometryCOMP contains: POP chain → null_render, and a child geometryCOMP with instancing=true, instanceop=null_render, containing spherePOP (display=true, render=true).

POP attribute format for instance pars: `P(0)`, `P(1)`, `P(2)`, `Color(0)`, etc.

## Color from Velocity (No GLSL)

```
mathmixPOP (comb0oper=length: length(Vel) → Speed)
  → lookuptexturePOP (rampTOP driven by tableDAT of color keys, fromhigh0=max speed)
  → nullPOP
```

Prefer built-in POP math over GLSL for simple operations — more flexible, artist-tweakable.
