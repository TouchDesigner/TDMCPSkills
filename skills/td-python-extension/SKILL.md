---
name: td-python-extension
description: Python extensions — ext0object, extension classes, parameter callbacks, scriptTOP/numpy, lifecycle. Use when building Python-driven baseCOMPs.
---

# Python Extensions

Patterns for Python extension components in TouchDesigner. Complements `td-comp-architecture` (structure/custom pars) and `td-dat-family` (callback mechanics). See `reference.md` for API signatures and `examples.md` for complete patterns.

## Create an extension — one pass

The fixed choreography. Author the class (step 3) and verify (step 7); the rest is invariant.
Mirrors what TD's own Component Editor produces.

1. **`baseCOMP base_<x>`** — name it now; binding and docked refs snapshot at creation.
2. **`textDAT <Name>`** inside — DAT = module = class, one identifier (e.g. `SimpleExt`).
3. **`set_dat_content`** the Skeleton (below) → `code/py/<comp-path>/<Name>.py`.
4. **`language=python`** — set it explicitly; `set_dat_content` doesn't (see Sync to File).
5. **`ext0object = op('./<Name>').module.<Name>(me)` + `ext0promote=True`** — leave `ext0name`
   empty (promoted under the class name). `ext0` always exists → no sequence management.
6. **pulse `reinitextensions`.**
7. **Gate — not done until proven:** `get_errors` clean AND a promoted member called from outside
   returns a value (`op('base_<x>').Hello()`). Print it.

Inspect an existing one: `get_operator_info(path, include_extensions=true)` — class names, promoted
signatures, clone sources.

## Naming & promotion

- DAT == module == class — one identifier; `Ext`/`EXT` suffix optional. `me.mod("<Name>").<Name>(me)`
  is an equivalent shorthand for the step-5 binding.
- **Capitalized** members = promoted (external via `comp.Member`); **lowercase/underscore** = internal.
- Promotion exposes Capitalized **methods**; use `@property` (or `TDF.createProperty`) for promoted data.
- Store `self.ownerComp` in `__init__`.

## Skeleton

Bare MCP `create(textDAT)` gives you an empty DAT — author this skeleton (it mirrors TD's
Component Editor template). Going through the Component Editor harvests it for you.

```python
from TDStoreTools import StorageManager
import TDFunctions as TDF

class CounterExt:
	"""CounterExt description"""
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

		# Dependable property — cooks dependents when it changes
		TDF.createProperty(self, 'MyProperty', value=0, dependable=True, readOnly=False)

		self.a = 0   # internal attribute
		self.B = 1   # promoted attribute (Capitalized)

		# Persistent across saves AND re-initialization:
		storedItems = [
			{'name': 'StoredProperty', 'default': None, 'readOnly': False,
			 'property': True, 'dependable': True},
		]
		# self.stored = StorageManager(self, ownerComp, storedItems)

	def myFunction(self, v):        # internal
		debug(v)

	def PromotedFunction(self, v):  # external (Capitalized)
		debug(v)

	# def onInitTD(self):    # after all extensions attached — cross-ext deps
	# 	debug("onInitTD called")
	# def onDestroyTD(self): # cleanup; use instead of __del__
	# 	debug("onDestroyTD called")
```

## Sync to File

The editor (and `create`) make the extension DAT **embedded**, not on disk. Getting it into the
code-on-disk workflow is a **follow-on step** — one `set_dat_content` call writes the file and sets
`file`/`syncfile` (it does NOT set `language` — set that yourself, step 4):

- Path: `code/py/<comp>/<subcomp>/<Name>.py` — see `td-dat-family` for the canonical flow
- After syncing, **edit on disk**; the DAT auto-re-inits on external edit (no `reinitextensions`).
- **Re-init wipes plain state.** It runs `__init__`, so `self.a`-style attributes reset every edit.
  State that must survive re-init (and saves) belongs in `StorageManager` stored items (the
  `self.stored` block above), not plain attributes.

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
- **Syncing a DAT to a file does NOT strip TD globals** — a file-synced DAT is still a DAT, so
  `op`, `me`, `project`, `debug`, etc. are available (extensions sync to disk fine). The "no globals"
  caveat applies only to a plain `.py` imported as a module *outside* any DAT namespace.

## Pitfalls

- **ext0object as expression** — must be constant-mode string, not expression
- **ext0promote only promotes methods** — not attributes; use `@property` for data
- **copyNumpyArray outside onCook** — stage data on extension, call from onCook only
- **Language not set on extension DAT** — always `language=python`
- **No parameterexecuteDAT** — extension won't react to custom parameter changes
- **Module-level heavy imports** — import torch/numpy in a setup method, not at module top
- **Name collision on create** — TD silently appends numbers; verify `.name` matches requested
- **HTTP/urllib in main thread** — blocks cook loop; use webClientDAT or `run()` with `delayFrames`
- **Forgetting reinitextensions (in-DAT edits only)** — code edited *inside* the DAT doesn't reload
  until pulsed. A **file-synced** DAT auto-re-inits on external disk edit. Either way, re-init wipes
  plain attributes — persist anything that must survive via `StorageManager` (see Sync to File)
- **`findChildren(type=textDAT)` without `maxDepth=1`** — crawls into annotateCOMPs and other utility COMPs, triggering compilation of their internal DATs as Python. Always use `maxDepth=1` when loading sibling modules
- **Assuming op reference pars are valid** — always check for None before using
