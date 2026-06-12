---
name: td-lister-ui
description: Lister and TreeLister UI — tables, interactive lists, data browsers. Use when building list-based interfaces.
---

# Lister UI

Tables, interactive lists, data browsers, and tree views using TD's built-in lister/treeLister components. See `reference.md` for colDefine schema, API, and full pitfall list.

## Lister vs TreeLister

- **lister** — flat tables, data grids, parameter editors
- **treeLister** — hierarchical with expand/collapse (node browsers, file trees)

## Architecture

All customization must be **external** — operators inside cloned listers are read-only (changes revert).

Wrapper containerCOMP (layout fill, alignorder=0) contains:
- **listerConfig** (baseCOMP, **must be inside wrapper**) — colDefine (tableDAT, 19 rows), define (tableDAT), callbacks (textDAT, language=python), look TOPs (master, header, rowRoll, rowSelect, + button/toggle/icon)
- **lister** (listCOMP) — cloned from `op.TDTox.op('lister')`

## Key Setup Steps

1. Create wrapper containerCOMP with `alignorder=0`, layout fill
2. Create **listerConfig** baseCOMP **inside the wrapper** (required — `Configcomp` expression uses `me.parent()`)
3. Create colDefine tableDAT (**exactly 19 rows**, no header row), define tableDAT, callbacks textDAT (language=python)
4. Create look textTOPs inside listerConfig: master, header, rowRoll, rowSelect
5. Create listCOMP inside the wrapper, then clone: `clone=op.TDTox.op('lister')` (expression)
6. **Post-clone setup** (these are NOT inherited from the clone):
   - `ext0object` = `op('./ListerExt').module.ListerExt(me)` (constant string, not expression)
   - `ext0promote` = `True`
   - `parentshortcut` = `Lister`
   - `callbacks` = `./internalCallbacks` (**CRITICAL** — must use `./` prefix, must point to the clone's internal DAT, NOT any external callbacks DAT)
7. Set `Configcomp` = `me.parent().op('listerConfig').path` (expression)
8. Set `Autodefinecols=False`, `Advancedcallbacks=True`
9. Wire data source: `Inputtabledat` (expression) for table, `Rawdata` for Python data
10. Pulse `reinitextensions`, then pulse `Refresh`

## Two Separate Callback Systems

The lister has **two** callback parameters — confusing them causes a completely dead lister (rows=0, cols=0, no cells):

- **`callbacks`** (builtin, lowercase, List page) — must point to `./internalCallbacks` inside the clone. This is the listCOMP's internal machinery. **Never point this at your external callbacks.**
- **`Callbackdat`** (custom, capitalized, Advanced page) — auto-derived expression: `me.par.Configcomp.eval().op('callbacks')`. Points to your external callbacks textDAT in listerConfig. **This is where your onClick/onSelectRow code lives.**

## Data Sources

- **tableDAT**: set `Inputtabledat` (expression), `Inputtablehasheaders=True`
- **Python list**: set `Rawdata` expression. Must return **cached** objects (new list each eval = infinite refresh)
- **List of dicts**: sourceData = dict key names
- **List of objects**: sourceData = attribute names, full object via `info['rowData']['rowObject']`

## Critical Pitfalls

- **`callbacks` → `./internalCallbacks`** — wrong target = dead lister with 0 rows/cols, no error messages. Most common setup failure
- **Post-clone params not inherited** — ext0object, ext0promote, parentshortcut must be set manually after cloning
- **listerConfig must be inside wrapper** — `Configcomp` expression `me.parent().op('listerConfig').path` requires it as a sibling of the lister
- **`./` prefix for internal paths** — COMP parameters resolve paths from inside the COMP; `internalCallbacks` without `./` won't resolve
- **Exactly 19 colDefine rows** — no header row, just 19 data rows. Extra/missing = silent failure
- **Clone/Configcomp are expressions** — not strings
- **Advancedcallbacks=True** — required for onClick, onInitCell, onSelectRow
- **callbacks language=python** — default plain = code won't execute
- **Rawdata must return cached objects** — use extension with `self._data`
- **ext0object is plain string** — constant mode, not expression
