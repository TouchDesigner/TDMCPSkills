# Python Extension Examples

## Basic Extension Component

```
baseCOMP (ext0object, ext0promote=True, viewer=True)
  ├── MyExt (textDAT, language=python) at X=-200, Y=0
  ├── parameter_callbacks (parameterexecuteDAT, op=.., pars=*, builtin=False) at X=-200, Y=-125
  └── [main ops] at X=0+, flowing right → nullTOP at chain end
```

## Extension Class Template

```python
class MyExt:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self._data = None

    @property
    def Data(self):
        return self._data

    def Refresh(self):
        pass

    def onParValueChange(self, par, prev):
        if par.name == 'Speed':
            self._update(par.eval())

    def onParPulse(self, par):
        if par.name == 'Refresh':
            self.Refresh()

    def _update(self, value):
        pass
```

## Stage-and-Cook (scriptTOP + numpy)

Extension side:
```python
def Refresh(self):
    source = self._resolveSource()
    if source is None:
        self._pixels = None
    else:
        self._pixels = source.numpyArray()
    script_top = self.ownerComp.op('output')
    if script_top and self._pixels is not None:
        h, w = self._pixels.shape[:2]
        setattr(script_top.par, 'resolutionw', w)
        setattr(script_top.par, 'resolutionh', h)
    if script_top:
        script_top.cook(force=True)

def Cook(self, scriptOP):
    if self._pixels is not None:
        scriptOP.copyNumpyArray(self._pixels)
    else:
        w, h = scriptOP.par.resolutionw.eval(), scriptOP.par.resolutionh.eval()
        scriptOP.copyNumpyArray(np.zeros((h, w, 4), dtype=np.float32))
```

## Start/Stop Active Toggle

```python
def __init__(self, ownerComp):
    self.ownerComp = ownerComp
    if ownerComp.par.Active.eval():
        self.Start()

def Start(self):
    debug(f'{self.ownerComp.name} started')

def Stop(self):
    debug(f'{self.ownerComp.name} stopped')

def onParValueChange(self, par, prev):
    if par.name == 'Active':
        self.Start() if par.eval() else self.Stop()
```

## Lazy Import (Heavy Libraries)

```python
def __init__(self, ownerComp):
    self.ownerComp = ownerComp
    self.torch = None

def Initialize(self):
    import torch
    self.torch = torch
    self._model = torch.load(self.ownerComp.par.Modelpath.eval())
```

Never `import torch` at module level — venv/asyncio may not be ready.
