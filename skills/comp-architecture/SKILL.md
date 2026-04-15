---
description: Component design — baseCOMPs, extensions, custom parameters, parent shortcuts, modularity. Use when creating COMPs or structuring projects.
---

# Component Architecture

How to structure COMPs for modularity, reusability, and clean hierarchy.

## COMP Types

- `baseCOMP` — general container, extensions, custom pars. Most common for modules. Always set `display=true` after creating
- `containerCOMP` — has a UI panel, use for anything with a visual interface
- `geometryCOMP` — renders geometry, contains SOPs/POPs + MATs, has instancing support

## Parent Shortcuts

Every COMP that others reference should have a `parentshortcut`. Set on the COMP itself.

- CamelCase, capital first: `Project`, `Render`, `Camera`, `MyModule`
- Depth-independent — `parent.Project` works from any nesting level
- Refactor-safe — reparenting doesn't break references
- Always prefer over `../../` or `parent(2)`

## In/Out Operators

COMPs use in/out ops to define their boundaries:
- `inTOP`/`outTOP`, `inCHOP`/`outCHOP`, `inSOP`/`outSOP`, `inDAT`/`outDAT`
- `in*` receives data from external wires into the COMP
- `out*` sends data out of the COMP
- **Create the in* op before wiring** — a fresh baseCOMP has no input connectors until an in* op exists inside
- **Default input** — wire a default source to any in\* operator's input 0. When nothing is connected externally to the parent COMP, the in\* outputs this default instead. Works for all in\* types (inTOP, inCHOP, inSOP, inDAT)

## Custom Parameters

Use `edit_custom_parameters` tool — `add`, `edit`, `delete`, `sort`, `rename`, `delete_page`. Name = code identifier, Label = human-readable display. Custom pars persist in .tox — never create via init scripts.

- `enableExpr` — grey out conditionally: `par.enableExpr = 'me.par.SomeToggle'`
- `startSection` — visual divider above a parameter

## State Output Pattern

Expose computed state as readonly custom pars with expressions to extension `@property` methods. Downstream ops reference pars, never extension properties directly. Visible in UI, linkable, accessible via parameterCHOP.

## Extensions

For Python-driven components, see the `python-extension` skill. Use `get_operator_info(path, include_extensions=true)` to inspect existing COMPs — returns extension classes, promoted method signatures, clone sources, and config COMP contents.

## Network Size

- **Create sub-baseCOMPs whenever a functional group feels self-contained** — like splitting code into functions. Don't wait until a network is too big; decompose early when a group of operators has a clear purpose (e.g. "bat collision", "score detection")
- Each sub-COMP is self-contained: inCHOP → processing → outCHOP
- Parent COMP wires sub-COMPs in sequence, handles state/switching logic
- ~20 operators per COMP is a practical guideline, but the real signal is "does this group have a clear single responsibility?"

## Clone Pattern

When two sub-COMPs have identical networks but different parameter values (e.g. bat1/bat2 detection), use **clones**:
- Build the master baseCOMP with custom parameters for all variable values
- Internal network references `parent().par.Paramname`
- Set `clone` parameter on the copy to point at the master
- The clone inherits the master's internal network; only custom par values differ

## Self-Contained Components

- Keep everything inside one parent COMP — processing chain, materials, utilities
- Don't spill operators up to the parent level
- Use nulls at chain endpoints for stable internal references
- Use `./operatorName` for child references, `operatorName` for siblings

## geometryCOMP Specifics

- Delete auto-created torus immediately after creating
- Output nullPOP needs `display=true render=true`
- Material pattern: `materialMAT → null_material`, reference as `./null_material`
- For instancing: see `geometry-instancing` skill

## Pitfalls

- **No in* op before wiring** — baseCOMP has no connectors until you create one inside
- **ext0object as expression** — must be constant mode string, not expression
- **Forgetting reinitextensions** — edited extension code doesn't reload automatically
- **Editing clone-controlled internals** — changes silently revert, customize via external ops only
- **Relative paths across COMPs** — use parent shortcuts instead
- **Custom par naming** — uppercase first letter, then lowercase + digits only. `Campadding` not `camPadding` or `CAMpadding`
