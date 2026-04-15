# timerCHOP Reference

The timerCHOP is a state machine for timed processes. Replaces fragile multi-operator setups with built-in states, segments, cycling, callbacks, and scrubbing. Use `get_help` for full parameter list — this covers **behavior**.

## State Machine

States: idle → Initialize → initializing → ready → Start → delay → running → done

- Start implies Initialize — auto-initializes if not already done
- `onInitialize()` returning > 0 retries after that many frames (deferred init for async resources)
- On Done parameter controls post-completion: Do Nothing, Re-Initialize, Re-Start, Re-Initialize and Re-Start
- Go to Done jumps to done state from anywhere

## Output Channels

- `ready` — 1 when initialized and waiting for Start
- `running` — 1 during delay and counting
- `done` — 1 when finished
- `timer_fraction` — 0→1 ramp during counting

## Segments

Table DAT rows define sequential or parallel timers. First row = headers. Column names map to parameters.

**Columns**: `length`, `delay`, `begin`, `speed`, `cycle`, `cyclelimit`, `maxcycles`, `cycleendalert`, plus any custom columns

- **Serial** (`segmethod`): segments play back-to-back, one `timer_fraction` channel
- **Parallel**: all run simultaneously, one fraction channel per segment (`timer_fraction0`, `timer_fraction1`, ...)
- **Begin-time**: absolute `begin` values for timeline-style layout (overrides delay)
- **Custom channels**: non-built-in column names become output channels (set `channelcolumns`). Interpolation via `interpolation` par

## Callbacks

TD auto-creates a `<name>_callbacks` textDAT. Use it — don't create a separate one.

```python
def onInitialize(timerOp, callCount):  # return >0 to retry, 0 = ready
def onReady(timerOp):
def onStart(timerOp):
def whileTimerActive(timerOp, segment, cycle, fraction):  # every frame while counting
def onTimerPulse(timerOp, segment):  # segment reached its length
def onSegmentEnter(timerOp, segment, interrupt):
def onSegmentExit(timerOp, segment, interrupt):
def onCycleStart(timerOp, segment, cycle):
def onCycle(timerOp, segment, cycle):  # end of each cycle
def onCycleEndAlert(timerOp, segment, cycle, alertSegment, alertDone, interrupt):
def onDone(timerOp, segment, interrupt):
```

**Segment object members**: `.index`, `.owner`, `.lengthSeconds`, `.delaySeconds`, `.speed`, `.cycle`, `.row.<column>`, `.custom` (dict of non-built-in columns). Auto-casts to int for comparisons.

## Python Members

**Time**: `.fraction`, `.runningSeconds`, `.runningFrames`, `.cumulativeSeconds`, `.playingSeconds`, `.masterSeconds`, `.masterFraction`
**State**: `.segment`, `.segments`, `.cycle`, `.lastCycle`
**Methods**: `.goTo(seconds=, frames=, segment=, cycle=, fraction=, endofcycle=)`, `.goToCycleEnd()`, `.goToNextSegment()`, `.goToPrevSegment()`

## Key Parameters (Non-Obvious)

- **Active** (`active`): `While Running` saves performance when idle
- **Defer Par Changes** (`deferpars`): Essential with segments — prevents mid-playback disruption
- **Length Type** (`lengthtype`): `Infinite` mode disables fraction, seconds rise forever
- **Time Control** (`timecontrol`): `Sequential` (independent) or `Locked to Timeline` (deterministic but limited callbacks)

## Common Patterns

- **Simple countdown**: `timerCHOP (length=5, ondone=donothing) → nullCHOP`
- **Looping timer**: `timerCHOP (length=2, cycle=true, cyclelimit=false) → nullCHOP`
- **Sequenced events**: `tableDAT → timerCHOP (segdat=table, deferpars=true)` with callbacks per segment
- **State machine chain**: Timer A's `onDone()` calls `op('timerB').par.start.pulse()`

# Threshold Detection Patterns

logicCHOP `convert` modes `gt`/`lt`/`ge`/`le` do NOT compare against `boundmin`. They detect value changes or compare between inputs.

**"value > threshold":** mathCHOP `preoff=-threshold` → logicCHOP `convert=pos`
**"value < threshold":** mathCHOP `preop=negate, postoff=threshold` → logicCHOP `convert=pos`

mathCHOP order: `(input preop + preoff) * gain + postoff`

countCHOP `offtoon` menu values: `inc`/`dec`/`reset` (not `countup`/`countdown`)

# Feedback Loop Patterns

- feedbackCHOP provides 1-frame delay for accumulation loops (position += velocity * dt)
- Loops start with 0 channels — bootstrap with switchCHOP selecting between constantCHOP (initial state) and physics chain
- Use selectCHOP `chop` param pointing at null_state to avoid backward wires. Wire selectCHOP → feedbackCHOP → chain → null_state
- CHOPs without wire outputs don't cook (demand-driven). Add nullCHOP downstream to force recooking
- triggerCHOP won't re-fire when input stays above threshold. Use chopexecuteDAT onOffToOn for reliable event detection from CHOP transitions
