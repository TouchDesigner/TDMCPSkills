---
name: td-review-network
description: Validate completed builds — check errors, verify wiring, diagnose root causes. Use after builds to verify correctness.
---

# Review

Validate completed builds. Check for errors, verify structure, diagnose root causes. Review only — does not apply fixes.

## Process

1. **Error check** — `get_errors(path)` — blocking, build cannot pass with errors
2. **Structure** — `list_operators(path, depth=2)` for layout + overlaps, `get_connections(path, graph=true)` for full signal flow in execution order. Verify all ops exist, no orphans, no unexpected cycles, null flags correct
3. **Parameters** — `get_parameters(path)` on key ops. Check expressions, material refs, feedback targets. For COMPs: `get_operator_info(path, include_extensions=true)` to verify extension wiring, promoted methods, clone sources
4. **Runtime values** — `inspect_values` on key ops. CHOPs: check channels, `include_samples=true` for waveforms. TOPs: `sample_grid=8` for stats + grid (prefer over `view_operator`). SOPs: point/prim counts
5. **Performance** — `get_cook_performance(path, sort="gpu", include_memory=true)` to catch bottlenecks early
6. **Output** — `get_errors(output)` first, then `inspect_values(sample_grid=8)`. Only `view_operator` when spatial detail matters
7. **Diagnose** (if errors) — classify, trace to root cause, propose fixes

## Diagnostic Patterns

- **"Operator not found"** → missing reference, check parameter paths
- **"Compile error" / GLSL** → `get_errors` returns `infoLog` with detailed line numbers for GLSL ops. Also read shader DAT content, check uniforms declared
- **"Python error"** → read script content, check ext0object syntax
- **"No input" / not connected** → check connections, verify wiring
- **Cook error / blank output** → check parameters against `get_help`, verify input chain
- **Black/wrong output** → trace upstream, check intermediate ops

## Key Principles

- **Always trace upstream** — if error op looks correct, follow input chain to find actual broken node
- **Chain reactions** — 5 errors from 1 missing connection = 1 fix, not 5. Group them
- **False errors from cook order** — on first cook, some ops error because upstream hasn't cooked yet. `pulse_parameter` to reinit feedback, recheck
- **Feedback sims need time** — don't judge on frame 0, `pulse_parameter` for init+start, wait, then check
- **Read shader code** — GLSL errors need actual code to diagnose, not just the error message

## Verdict Format

For each area: PASS / WARN / FAIL
- Error check, structure, parameters, performance, output
- For each error: message, category, root cause, specific fix
- Group chain reactions, recommend fix order
