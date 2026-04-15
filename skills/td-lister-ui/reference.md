# Lister Reference

## colDefine Rows (all 19, order matters)

- `column` — internal ID: `Name`, `Value`, `close`
- `columnLabel` — header text (`*` = use column name)
- `sourceData` — data key (column name, dict key, attribute, index)
- `sourceDataMode` — `string`, `int`, `float`, `blank`, `rowNum`, `constant`, `eval`, `color`
- `textFormat` — f-string formatting
- `cellLook` — textTOP name for styling: `button`, empty for default
- `topPath` — image TOP, `*` = wildcard (e.g. `toggle*` + data "True" → `toggleTrue` TOP)
- `topFill` — `BEST`, empty
- `help` — tooltip (`*` = cell value)
- `width` — pixels or `auto`
- `stretch` — fill available space (0/1)
- `sizable` — user drag-resize (0/1)
- `editable` — 0=none, 1=click, 2=dbl-click
- `draggable` — enable dragging (0/1)
- `clickOnDrag` — click on drag start (0/1)
- `selectRow` — click selects row (0/1)
- `justify` — `CENTERLEFT`, `CENTER`
- `fontBold` — 0/1
- `fontItalic` — 0/1

## sourceDataMode Values

- `string` — as-is, sort alphabetically
- `int` / `float` — sort numerically
- `blank` — hide text, retain data (for topPath graphics)
- `rowNum` — auto row numbers
- `constant` — repeat literal sourceData across all cells
- `eval` — evaluate as Python (`object` = row object)
- `color` — `[r, g, b, a]` or `[r, g, b, a, 'label']`

## Lister Parameters

**Post-clone setup (NOT inherited from clone):**
- `ext0object` — `op('./ListerExt').module.ListerExt(me)` (constant string)
- `ext0promote` — `True`
- `parentshortcut` — `Lister`
- `callbacks` — `./internalCallbacks` (builtin listCOMP param, `./` prefix required)

**Custom parameters (on Lister/Advanced pages):**
- `clone` — `op.TDTox.op('lister')` (expression)
- `Configcomp` — `me.parent().op('listerConfig').path` (expression)
- `Callbackdat` — auto-derived: `me.par.Configcomp.eval().op('callbacks') if me.par.Configcomp else ''`
- `Inputtabledat` — source tableDAT path (expression)
- `Rawdata` — Python data (expression)
- `Inputtablehasheaders` — True for tableDAT with headers
- `Autosyncinputtable` — push edits back
- `Refreshoninputchange` — auto-refresh on input change
- `Advancedcallbacks` — required for onClick, onInitCell, onSelectRow
- `Autodefinecols` — False for external colDefine

## ListerExt API

- `Refresh()` — full re-init
- `DataChanged()` — notify data modification
- `DeleteRows([rows])` — remove by row number list
- `Data` — list of ordered dicts
- `SetCellText(row, col, text)` — update cell
- `SelectRow(row)` — select single row
- `SetCellOverlay()` / `SetRowOverlay()` — color overlays

## colDefine Tips

- Omitted rows default to empty/0 — you don't need all 19 values for every column
- `positionx` on look textTOPs controls text left-padding. Use 10 for comfortable spacing
- **Button column**: `cellLook=button`, `sourceData=X`, `sourceDataMode=constant`, `selectRow=0`, `width=30`
- **Toggle column**: `topPath=toggle*`, `sourceDataMode=blank`, `topFill=BEST`, `selectRow=0`. Requires `toggleTrue`/`toggleFalse` TOPs in config

## Callback info Keys

- `ownerComp` — the lister listCOMP
- `row` — row number (0=header, -1=past end)
- `col` / `colName` — column number / name
- `cellText` — cell text content
- `rowData` — full row dict (includes rowObject)

## Callback Examples

```python
# Delete button
def onClick(info):
    if info.get('colName') == 'close':
        info['ownerComp'].DeleteRows([info['row']])

# Toggle checkbox
def onSelectRow(info):
    if info.get('colName') == 'state':
        table = info['ownerComp'].par.Inputtabledat.eval()
        row = info['row']
        current = table[row, 'state'].val
        table[row, 'state'] = 'False' if current == 'True' else 'True'

# Right-click menu
def onClickRight(info):
    op.TDResources.op('popMenu').Open(
        items=['A', 'B', 'C'], callback=onMenuSelect, callbackDetails=info)
```

## TreeLister Differences

- Clone from `op.TDTox.op('treeLister')`
- Look ops are textCOMPs (not textTOPs) with `clickthrough=True`
- Post-clone: ext0object, ext0promote, parentshortcut, hmode/vmode NOT inherited
- `info['ownerComp'].parent().parent()` to reach wrapper from callbacks

## Full Pitfall List

**Showstoppers (dead lister, no cells):**
1. **`callbacks` must be `./internalCallbacks`** — the builtin `callbacks` param (List page) must point to the clone's internal DAT with `./` prefix. Without `./` the path won't resolve. Wrong target = rows=0, cols=0, completely dead lister with NO error messages. Also causes stuck resetRun. This is the #1 setup failure
2. **Post-clone params not inherited** — `ext0object`, `ext0promote`, `parentshortcut` must be set manually. ext0object = `op('./ListerExt').module.ListerExt(me)` (constant string), ext0promote = True, parentshortcut = `Lister`. Without these the ListerExt won't load
3. **listerConfig must be inside the wrapper container** — `Configcomp` expression `me.parent().op('listerConfig').path` requires listerConfig as a sibling of the lister inside the same containerCOMP. Moving it outside breaks the path resolution

**Silent failures:**
4. Exactly 19 colDefine rows — no header row, just 19 data rows. Extra/missing = columns silently ignored
5. External config required — edits inside clone revert on project reload
6. sourceData is case-sensitive — must match tableDAT headers or dict keys exactly
7. Missing look TOPs → blank cells
8. callbacks textDAT language must be python — default plain = code won't execute
9. Clone/Configcomp are expressions not strings — use `{'expr': '...'}` syntax

**Data issues:**
10. topPath wildcard: `toggle*` + "True" → looks for `toggleTrue` TOP
11. Inputtablehasheaders must be True when tableDAT has header row
12. define table: 2-column (name, value). Colors = space-separated RGBA
13. Rawdata must return cached objects — new list each eval = infinite refresh loop. Use extension `self._data`
14. Rawdata: call `Refresh()` after updating data. `Refreshoninputchange` only watches Inputtabledat

**Callback issues:**
15. **Two callback systems** — `callbacks` (builtin, lowercase) → `./internalCallbacks` (clone machinery). `Callbackdat` (custom, capitalized) → your external callbacks in listerConfig. Confusing them is fatal
16. Advancedcallbacks=True — required for onClick, onInitCell, onSelectRow to fire
17. Row 0 = header, row -1 = past end — guard for both in callbacks
18. DeleteRows takes a list — `DeleteRows([row])` not `DeleteRows(row)`
19. cellLook required for clickable columns — without it, clicks route as text selection

**Layout:**
20. containerCOMP alignorder=0 for fill layout
21. textTOP resolutionh = row height in pixels
22. ext0object is plain string — constant mode, not expression
23. Autodefinecols=False for external colDefine
24. `./` prefix for COMP internal paths — COMP parameters resolve from inside; bare names don't resolve

**TreeLister specific:**
25. treeLister look ops are textCOMPs (not textTOPs) with `clickthrough=True`
26. treeLister post-clone: same ext0object/ext0promote/parentshortcut setup needed
27. `info['ownerComp'].parent().parent()` to reach wrapper from treeLister callbacks
