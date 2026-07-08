# Algorithimia

Algorithimia is a DSA programming RPG. The current build is a terminal-first prototype with two Python encounters.

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
python -m algorithimia --encounter triage_line --trace-html build/triage-trace.html
```

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

The engine runs several deterministic cases and reports whether the encounter is cleared.
The Sorting Slime encounter rejects `sorted(...)`, indirect built-in `sorted` bindings, and `.sort()` so the player demonstrates visible sorting logic.

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
The `--trace-html` export writes a self-contained static HTML trace viewer that embeds the current Phase 1 encounter badge and trace-event icon sheets.

## Security Note

Player Python runs in a child process with timeout, isolated mode, a minimal environment, restricted builtins, JSON-only I/O, source/result size caps, and a syntax preflight that rejects imports, dunder introspection, and dynamic evaluation/introspection helpers. This is a baseline local safety model, not a complete sandbox for hostile untrusted code.
