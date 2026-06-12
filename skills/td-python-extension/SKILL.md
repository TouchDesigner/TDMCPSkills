---
name: td-python-extension
description: Python extensions — ext0object, extension classes, parameter callbacks, scriptTOP/numpy, lifecycle. Use when building Python-driven baseCOMPs.
---

# Python Extensions

Patterns for Python extension components in TouchDesigner. Complements `td-comp-architecture` (structure/custom pars) and `td-dat-family` (callback mechanics). See `reference.md` for API signatures and `examples.md` for complete patterns.

## Extension Wiring

Every extension needs three pieces on the baseCOMP:

1. **textDAT** inside the COMP — extension class, `language=python`
2. **ext0object** — constant-mode string: `me.mod("ExtDAT").ClassName(me)`
3. **ext0promote** = `True` — exposes Capitalized methods externally

After editing extension code: `pulse_parameter` with `reinitextensions`, then check errors.

To inspect an existing extension COMP: `get_operator_info(path, include_extensions=true)` — returns class names, promoted method signatures, and clone sources.

## Naming Conventions

- **Extension DAT**: `ComponentNameEXT` (e.g. `PongEXT`, `FluidEXT`)
- **Class inside**: `ComponentName` (e.g. `Pong`, `Fluid`)
- **ext0object**: `me.mod("PongEXT").Pong(me)`
- **Capitalized** methods/properties = promoted, externally accessible via `comp.MethodName()`
- **lowercase/underscore** = internal only
- `ext0promote` only exposes **methods**, not attributes — use `@property` for data access
- `self.ownerComp` — always store the parent baseCOMP reference

## Parameter Callback Routing

Extension reacts to custom parameter changes via `parameterexecuteDAT`:
- `op` = `..`, `pars` = `*`, `builtin` = False
- Generic routing loops through `par.owner.extensions` calling `onParValueChange` / `onParPulse`
- Without this DAT, the extension is deaf to parameter changes

## Lifecycle

- `__init__(ownerComp)` — creation/reinit, store refs, declare slots as None
- `onInitTD()` — after all extensions attached, safe to access other exts
- `onDestroyTD()` — cleanup (use instead of `__del__`)

Use `onInitTD` when depending on other components' extensions being ready.

## scriptTOP + numpy

`copyNumpyArray()` **must** run inside `onCook` — calling it elsewhere raises `tdError`.

**Stage-and-cook**: extension stages `self._pixels`, calls `script_top.cook(force=True)`, scriptTOP `onCook` calls back into extension which runs `copyNumpyArray`.

## Safe Operator Resolution

Custom parameters referencing operators (TOP, CHOP, etc.) may be empty or invalid. Always resolve safely — check for None and validate before using.

## Internal Layout

Extension DAT and parameterexecuteDAT at X=-200 (left of origin). Main operator chain flows right from X=0. Output null at chain end.

## DAT Module Imports

- **Same COMP**: `mod.datName` or `from datName import X` (module-level only)
- **Cross COMP**: `op('comp').mod.datName` — the only reliable pattern
- **External .py**: TD globals (`op`, `project`) are NOT available — only injected into DAT namespaces

## Pitfalls

- **ext0object as expression** — must be constant-mode string, not expression
- **ext0promote only promotes methods** — not attributes; use `@property` for data
- **copyNumpyArray outside onCook** — stage data on extension, call from onCook only
- **Language not set on extension DAT** — always `language=python`
- **No parameterexecuteDAT** — extension won't react to custom parameter changes
- **Module-level heavy imports** — import torch/numpy in a setup method, not at module top
- **Name collision on create** — TD silently appends numbers; verify `.name` matches requested
- **HTTP/urllib in main thread** — blocks cook loop; use webClientDAT or `run()` with `delayFrames`
- **Forgetting reinitextensions** — edited code doesn't reload until pulsed
- **`findChildren(type=textDAT)` without `maxDepth=1`** — crawls into annotateCOMPs and other utility COMPs, triggering compilation of their internal DATs as Python. Always use `maxDepth=1` when loading sibling modules
- **Assuming op reference pars are valid** — always check for None before using
