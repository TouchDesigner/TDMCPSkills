---
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

For any DAT containing code (Python, GLSL), sync to disk:
- Set `file` parameter to relative path from .toe file
- Set `syncfile=true`
- Set `language` to match content
- Code on disk, not embedded in .toe — enables version control and external editing

### File Path Convention

External files mirror the TD operator hierarchy under `src/`:
- **Python**: `src/py/<comp>/<subcomp>/<dat_name>.py`
- **GLSL**: `src/glsl/<comp>/<subcomp>/<dat_name>.glsl`

Example: `/project1/MyEffect/scripts/helper` → `src/py/MyEffect/scripts/helper.py`

The `file` parameter on the DAT uses the same relative path from the .toe file.

## Pitfalls

- **Language not set** — textDAT defaults to `plain`, no syntax highlighting or error checking
- **Using textDAT for tables** — use tableDAT for row/column data
- **chopexec without selective cooking** — can fire excessively, use with quantized/selective nullCHOP upstream
- **Blocking Python in callbacks** — callbacks run on main thread, no HTTP/heavy compute. Use `run()` with `delayFrames` for deferred work
- **Missing callback DAT** — extensions won't react to parameter changes without parameterexecuteDAT
