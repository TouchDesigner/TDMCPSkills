# Python Extension Reference

## ext0object Syntax

Constant-mode string (never expression):
```
me.mod("ExtDATName").ClassName(me)
```
- `ExtDATName` = name of the textDAT inside the COMP
- `ClassName` = Python class defined in that DAT
- `me` passes the ownerComp to `__init__`

## Extension Class API

```python
class MyExt:
    def __init__(self, ownerComp):    # required — store ownerComp, init state
    def onInitTD(self):               # all extensions attached, safe cross-ext access
    def onDestroyTD(self):            # cleanup on delete (not __del__)
```

### Parameter callback methods (called by parameterexecuteDAT routing):
```python
def onParValueChange(self, par, prev):  # par value changed
def onParPulse(self, par):              # pulse par triggered
```

### Access patterns:
- Promoted: `comp.MethodName()` (requires `ext0promote=True`)
- By class: `comp.ext.ClassName`
- Direct: `comp.extensions[i]`

## Generic parameterexecuteDAT Content

Works for any extension — routes to all extensions on the COMP:
```python
def onValueChange(par, prev):
    for ext in par.owner.extensions:
        if hasattr(ext, 'onParValueChange'):
            ext.onParValueChange(par, prev)
    return

def onPulse(par):
    for ext in par.owner.extensions:
        if hasattr(ext, 'onParPulse'):
            ext.onParPulse(par)
    return
```

## scriptTOP Callbacks DAT

```python
def onSetupParameters(scriptOp):
    return

def onPulse(par):
    return

def onCook(scriptOp):
    ext = scriptOp.parent().ext.MyExt
    ext.Cook(scriptOp)
    return
```

## Safe Operator Resolution

```python
def _resolveSource(self):
    raw = self.ownerComp.par.Source.eval()
    if not raw:
        return None
    source = op(raw) if isinstance(raw, str) else raw
    return source if source is not None else None
```

## OP Reference Parameters

Assign by operator object when setting from outside the component context:
```python
setattr(script_top.par, 'callbacks', comp.op('output_callbacks'))  # object
setattr(script_top.par, 'callbacks', 'output_callbacks')           # relative string OK from inside
```

## Reinit Sequence

1. `pulse_parameter` with `reinitextensions`
2. Check errors via `get_errors`
3. If the extension has an Initialize pulse, pulse it
