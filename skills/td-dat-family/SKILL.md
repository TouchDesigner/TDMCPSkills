---
name: td-dat-family
description: DAT operations — table data, Python callbacks, parameter execute, CHOP execute. Use when creating or populating any DAT.
---

# DAT Scripts

Python scripts, callbacks, and table data in TouchDesigner DAT operators.

## DAT Types

- `textDAT` — text content: Python scripts, GLSL code, JSON, plain text. Set `language` parameter to match content (`python`, `glsl`, etc.)
- `tableDAT` — row/column table data (cells)
- `parameterexecuteDAT` — fires callbacks on parameter changes
- `chopexecuteDAT` — fires callbacks on CHOP value/channel changes
- `datexecuteDAT` — fires callbacks on DAT content changes
- `panelexecuteDAT` — fires callbacks on panel events (click, hover, etc.)
- `scriptDAT` — programmable DAT with onCook callback

## Setting DAT Content

Via MCP: `set_dat_content(path, text=...)` for text, `set_dat_content(path, rows=[[...]])` for table data (array of row arrays).

Always set `language` parameter on textDATs — defaults to `plain` which loses syntax highlighting and error checking.

## Callback DATs

Each callback DAT has a dedicated **source-reference par** that must be set. Without it, the DAT fires no callbacks and raises no error — silently inert. `fromop` is not the source; it's just where `op()` expressions evaluate.

- `chopexecuteDAT` → `chop` par
- `datexecuteDAT` → `dat` par
- `panelexecuteDAT` → `panel` par
- `parameterexecuteDAT` → `op` par

### parameterexecuteDAT
Routes parameter changes to handlers. Standard setup:
- `op` par = `..` (parent COMP)
- `pars` = `*` (all custom pars)
- `builtin` = False

Key callbacks:
```python
def onValueChange(par, prev):  # par value changed
def onPulse(par):              # pulse par triggered
```

### chopexecuteDAT
Fires when CHOP values change. Useful for event-driven responses to data.
- `chop` par = path to the CHOP to monitor
- Key callbacks: `onValueChange(channel, sampleIndex, val, prev)`, `onOffToOn(channel, ...)`

### datexecuteDAT
Fires when referenced DAT content changes.
- Key callbacks: `onTableChange(dat)`, `onRowChange(dat, rows)`, `onCellChange(dat, cells, prev)`

## Table DATs

- Access cells: `op('table1')['rowName', 'colName']` or `op('table1')[rowIndex, colIndex]`
- First row is typically headers
- Use TSV format when populating via MCP

## Sync to File

Any DAT containing code (Python, GLSL) should live on disk, not embedded in the `.toe`.
This enables version control and external editing — and it's the fastest way to author:
write in your editor, TD live-reloads. This is the agent's strong zone (text on disk),
so route code here rather than editing inside the DAT.

**Do it in one call.** `set_dat_content(path, file_content, file_path, file_type)` writes the
file, sets `file` + `syncfile=true`, and creates missing folders — atomically. Don't set
`file`/`syncfile` by hand; that's the slow path.

```
set_dat_content(
  path="/project1/MyEffect/glsl_raymarch_pixel",
  file_content="<source>",
  file_path="code/glsl/MyEffect/glsl_raymarch_pixel.glsl",
  file_type="glsl",   # 'glsl' | 'py' | 'dat'
)
```

- **Set `language` yourself — `set_dat_content` does NOT.** A code DAT you create with
  `create(textDAT)` defaults to `language=input` and renders as plain `text`: no syntax
  highlighting, and TD won't parse it as code. Set `language` to match the content (`python`,
  `glsl`, `json`, `yaml`, `xml`, …) right after syncing. (Auto-docked DATs — glsl `*_pixel`,
  `*_callbacks` — already have it set by their parent op; hand-created ones don't.) The sibling
  `extension` par ("Edit/View Extension") sets the external-editor file type; leaving it at
  `languageext` derives it from `language`, so usually only `language` needs setting.
- **Always pass an explicit `file_path`.** Omit it and the server auto-derives the path
  from the live op path — convenient until a rename/move silently forks to a new file
  and orphans the old one.
- **After the first sync, edit on disk.** TD live-reloads with no MCP touch: GLSL
  recompiles, Python extensions auto-re-init. Re-init runs `__init__`, so **in-memory
  extension state is wiped** — the one thing to watch.

### Standard flow

1. **Create the op with its final name.** Docked DATs and `file`/`pixeldat` references are
   resolved at creation and are static snapshots — a later rename does NOT follow them.
2. **Harvest the boilerplate.** glslTOP/glslmultiTOP auto-dock a DAT with known-good
   starter code — sync that instead of authoring from scratch. (baseCOMP extensions have no
   auto-dock: the Component Editor harvests TD's template, but bare `create(textDAT)` gives an
   empty DAT — see `td-python-extension` for the skeleton to author.)
3. **Sync to disk** — one `set_dat_content` call (above), then **set `language`** to match
   the code (it isn't set for you).
4. **Edit on disk** — your editor is now the source of truth; TD syncs along.

### File Path Convention

External files mirror the TD operator hierarchy under `code/`, relative to the `.toe`:
- **Python**: `code/py/<comp>/<subcomp>/<dat_name>.py`
- **GLSL**: `code/glsl/<comp>/<subcomp>/<dat_name>.glsl`

Example: `/project1/MyEffect/scripts/helper` → `code/py/MyEffect/scripts/helper.py`

## Pitfalls

- **Language not set** — textDAT defaults to `plain`, no syntax highlighting or error checking
- **Using textDAT for tables** — use tableDAT for row/column data
- **chopexec without selective cooking** — can fire excessively, use with quantized/selective nullCHOP upstream
- **Blocking Python in callbacks** — callbacks run on main thread, no HTTP/heavy compute. Use `run()` with `delayFrames` for deferred work
- **Missing callback DAT** — extensions won't react to parameter changes without parameterexecuteDAT
- **Silently-inert execute DAT** — `*executeDAT` with `active=true` and triggers enabled but the source par empty (`chop`/`dat`/`op`/`panel`) fires nothing and raises no error. Always set the source par when creating one
