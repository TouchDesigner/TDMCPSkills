---
description: TouchDesigner optimization — selective cooking, operator-driven animation, avoiding per-frame Python.
---

# Performance

Optimization patterns for TouchDesigner. Core principle: let TD do the work — operators cook in C++, Python is the bottleneck.

## Optimized vs Unoptimized Expressions

TD recognizes common Python patterns and runs them in C++ instead:
- **Optimized**: `op('lfo1')['chan1']`, basic math, `abs()`, `math.sin()`
- **Unoptimized**: complex logic, conditionals, custom functions, extension calls

An optimized reference is essentially free. Unoptimized = full Python interpreter every frame per parameter.

## Operators Over Python

Use CHOPs for per-frame value changes, not Python scripts:
- `lfoCHOP` — oscillation
- `speedCHOP` — incremental values (accumulates input)
- `timerCHOP` — timed sequences, state machine
- `countCHOP` — event-driven counting
- `lookupCHOP` — range mapping via lookup table

Wire CHOP outputs to parameters via expressions: `op('null_lfo')['chan1']`

## Selective Cooking

When Python must react to values, filter the signal first:

lfoCHOP → limitCHOP (quantize) → nullCHOP (cooktype=selective) → chopexecuteDAT

The null only passes data when values change. Python fires on transitions, not every frame.

## Expressions Over Exports

Prefer expressions over exports — same performance, but parameters stay editable and visible in UI.

## Time Without Overflow

**Never `absTime.seconds` for installations** — floats lose precision, eventually overflow.

**Solution**: cyclical operators. lfoCHOP with sin+cos channels driving noise T/W parameters:
- 2 channels: `sin`, `cos` (phase expr: `me.chanIndex * 0.25`)
- Very low frequency (0.001–0.01 Hz)
- Drives `tz`/`tw` (or `t4d` for POPs) on noise operators
- Rotation in 4D noise space — never accumulates, never overflows

## Python Per-Frame Guidelines

- **Avoid**: driving parameters (use expressions), copying data between ops (wire them), animation (use CHOPs), conditional logic on signals (use limit/logic CHOPs)
- **OK**: extension event callbacks, one-off setup, scriptCHOP with minimal static logic, temporary debugging
- **expressionCHOP** — runs Python per sample per frame, can be heavy on high-sample-count CHOPs. Consider compiled alternatives (mathCHOP, functionCHOP, etc.) when possible

## Profiling

Use `get_cook_performance` to identify bottlenecks:
- Sorts operators by cook time (highest first). `top_n` limits results (default 20)
- Reports `cookTime`, `cpuCookTime`, `gpuCookTime`
- `sort` options: `cook` (default), `cpu`, `gpu`, `memory`, `cooks`
- `include_memory=true` for `cpuMemory`, `gpuMemory`, `totalCooks`

Use `inspect_values` to check runtime state. TOPs: `sample_grid=8` for stats + grid (prefer over `view_operator`).

## Cooking Rules

Operators cook when:
- In a visible output chain (connected to displayed/rendered output)
- Visible in an open network editor pane
- Explicitly force-cooked: `op.cook(force=True)`

`viewer=True` is a UI hint, not a cook guarantee. Ops inside unopened COMPs won't cook.
