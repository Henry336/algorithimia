# Algorithimia

Algorithimia is a DSA programming RPG. The current build has two Python encounter prototypes and a self-contained browser shell with a tiny explorable Queueworks room that transitions into a playable Sorting Slime ordering slice.

## Run

```powershell
python -m algorithimia
```

Choose a specific encounter:

```powershell
python -m algorithimia --encounter triage_line
```

Export a static browser trace viewer for an encounter:

```powershell
python -m algorithimia --trace-html build/sorting-trace.html
python -m algorithimia --encounter triage_line --trace-html build/triage-trace.html
```

Export the current browser game shell:

```powershell
python -m algorithimia --game-html build/game-shell.html
```

Open `build/game-shell.html` in a browser. The first screen is a small Queueworks room: move the Patchrunner with arrow keys, WASD, or the on-screen buttons, navigate around blocked ledger/gate tiles, interact with the Sorting Slime, sort the visible rune spill, check the order, then return to the room. A correct order opens the route, clears the jammed gate blockers, and disables repeated repair interaction; a wrong order returns to the same room with retry feedback and the intake still jammed. The room status strip now names blocked-gate, retry, sealed-check, and route-clear states directly.

For a lightweight browser self-smoke, open the same file with `?smoke=1` or `#smoke` appended. The page will exercise movement, interaction, wrong-order return, rune swaps, check order, success return, and route-open status, then print a pass/fail report inside the room panel.

On Windows installations that use the Python launcher:

```powershell
py -m algorithimia
```

## Test

```powershell
python -m unittest
```

Or:

```powershell
py -m unittest
```

GitHub Actions also runs the same unit-test suite on pushes to `main` and on pull requests.

## Encounter Contracts

### Sorting Slime

The player submits Python that defines:

```python
def solve(values):
    ordered = list(values)
    for i in range(1, len(ordered)):
        current = ordered[i]
        j = i - 1
        while j >= 0 and ordered[j] > current:
            ordered[j + 1] = ordered[j]
            j -= 1
        ordered[j + 1] = current
    return ordered
```

The engine runs several deterministic public cases plus sealed certification cases and reports whether the encounter is cleared.
The Sorting Slime encounter rejects `sorted(...)`, indirect built-in `sorted` bindings, and `.sort()` so the player demonstrates visible sorting logic.
Certification cases are shown as sealed pass/fail checks in the CLI so hidden inputs stay hidden while memorized public-fixture answers still fail.

### Triage Line Dispatcher Trial

The player submits Python that defines:

```python
def solve(tickets):
    # Return ticket ids in service order.
    return []
```

Each ticket is a JSON-compatible object with `id`, `arrival`, and `urgent`.
Urgent tickets may advance, ties keep arrival order, and after two urgent services the oldest waiting ordinary ticket must be served if one exists.
The CLI trace previews the starvation-guard case so players see arrivals, urgent overrides, stable ties, ordinary guard behavior, and served ticket ids before reading the case results.
When a policy case fails, the counter now reports a compact debrief bark for the specific mistake: FIFO drift, buried urgency, broken stable ties, ordinary starvation, or ticket identity loss.

## Trace Metadata

The terminal trace text is generated from structured trace events. Future renderers can consume event kinds such as `comparison`, `arrival`, `urgent_override`, `stable_tie`, `ordinary_guard`, and `served` without parsing player-facing strings.
The `--trace-html` export writes a self-contained static HTML trace viewer that embeds the current Phase 1 encounter badge, trace-event icon sheets, and sealed-certification marker sheet when the encounter uses hidden certification cases.
The `--game-html` export writes a self-contained static browser shell with tabbed encounter selection, encounter prompts, run/export commands, trace previews, and sealed-certification status. It does not execute player Python in the browser; code execution still stays in the local CLI runner.

The browser game shell now opens with a tiny explorable Queueworks room. The player sprite can move around the room, the Sorting Slime is an interactable object, blocked ledger/gate tiles prevent walking through the jammed scene, Agent 5's package-local Queueworks room sheet provides the temporary Patchrunner and interaction prompt visuals, the room feedback sheet marks movement/interact/failure/sealed/open state, and the room retry strip appears after a wrong visible order. Interaction opens the Sorting Slime repair scene. In the Sorting Slime scene, click rune tokens to select and swap them, then use the icon-supported check/reset buttons to test the visible spill. The slice embeds the current Phase 1 Sorting Slime scene strip, Sorting Slime sprite, Queue Intake Gate placeholder sprite, and Sorting Slime action icons, shows adjacent inspection marks, flips between jammed and cleared route status, shows Mira feedback, returns to the room with retry feedback after a wrong order, and lets the player return to the room after success while hidden certification data stays sealed. Success removes the route blockers so the opened gate reads as passable instead of only changing text, and the room cue line keeps repeated interaction from implying another repair is needed.
The exported shell also has a dependency-free `?smoke=1` / `#smoke` self-check for Agent 4 and Henry. It is inactive during normal play.

## Security Note

Player Python runs in a child process with timeout, isolated mode, a minimal environment, restricted builtins, JSON-only I/O, source/result size caps, and a syntax preflight that rejects imports, dunder introspection, and dynamic evaluation/introspection helpers. This is a baseline local safety model, not a complete sandbox for hostile untrusted code.
