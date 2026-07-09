# Architecture

Algorithimia currently uses a small Python package organized around a deterministic encounter loop.

## Modules

- `algorithimia.cli`: terminal entry point.
- `algorithimia.encounters`: encounter data and test cases.
- `algorithimia.engine`: gameplay validation flow.
- `algorithimia.game_shell`: static browser shell export for the current encounter roster.
- `algorithimia.language.python_adapter`: Python-first player-code execution.
- `algorithimia.visualizers`: deterministic trace events and text labels for algorithm feedback.
- `algorithimia.trace_viewer`: static HTML trace viewer export for the current structured event stream.

## Verification

Local verification is `python -m unittest` from the repository root. The GitHub Actions workflow in `.github/workflows/tests.yml` installs the package on Python 3.11 and runs the same deterministic unit-test suite on pushes to `main` and pull requests.

## Gameplay Flow

1. The CLI loads an encounter.
2. The engine sends each case to the language adapter.
3. The adapter executes `solve(values)` in a child Python process.
4. The engine optionally applies encounter-specific output validation.
5. The engine compares JSON-compatible output against expected case results.
6. The CLI prints RPG-flavored feedback and per-case results.

## Encounter Validation Policy

`Sorting Slime` is a DSA teaching encounter, so its encounter metadata defines Python call restrictions that reject `sorted(...)`, indirect built-in `sorted` bindings, and `.sort()` before executing player code. The adapter also removes restricted built-in function names from the child runner's `SAFE_BUILTINS` for that encounter, keeping helper bans encounter-scoped for future challenges. Sorting Slime also has deterministic certification cases that run during attempts in addition to the public teaching fixtures, so hard-coded answers for the visible examples do not clear the encounter. The engine marks those certification results separately and the CLI redacts sealed expected/actual values, preserving hidden validation while still giving players a compact in-world anti-oracle bark.

The Python adapter also applies encounter-neutral source preflight before subprocess execution. Early puzzle submissions cannot use imports, dunder introspection, or dynamic evaluation/introspection helpers such as `eval`, `exec`, `open`, `getattr`, `globals`, or `__import__`. It also caps submitted source size before parsing and caps serialized result payloads inside the child runner before printing JSON back to the parent process. These checks keep the current educational contract narrow and reduce accidental local resource blowups, but they are not a substitute for OS-level sandboxing.

`Triage Line Dispatcher Trial` uses the same engine path with JSON ticket objects instead of integer rune values. Its output validator checks that returned ids were issued by the fixture and that every issued ticket is served exactly once before the expected policy order is compared. If the ids are valid but the order is wrong, the validator returns a compact encounter bark tied to the failed policy case: FIFO drift, buried urgency, broken stable ties, or ordinary starvation.

Encounter metadata can name a `trace_case_name` when the most useful preview is not the first non-empty fixture. Triage Line uses this to show the ordinary-guard fixture in the CLI trace, including arrival, urgent override, stable tie, ordinary guard, and served labels.

## Trace Visualizer Contract

Visualizers now expose renderer-ready `TraceEvent` values with:

- `kind`: a stable event category such as `comparison`, `arrival`, `urgent_override`, `stable_tie`, `ordinary_guard`, or `served`.
- `label`: the compact terminal string players see today.
- `payload`: JSON-compatible details a future renderer can bind to sprites, lanes, badges, or animation states.

The CLI still calls `encounter_trace(...)` for labels, but those labels are derived from `encounter_trace_events(...)`. Future graphical clients should consume the structured events instead of scraping terminal text.

`algorithimia.trace_viewer` is the first lightweight browser surface. It renders the selected encounter's current trace events into a self-contained HTML file and embeds the Phase 1 encounter badge plus trace-event SVG sheets as data images. Encounters with `certification_cases` also get a sealed-certification summary that shows public/certification counts and the certification marker sheet without exposing hidden case names, inputs, or expected outputs. This is deliberately a static viewer, not the final renderer or camera choice.

`algorithimia.game_shell` is the first browser game-shell surface. It exports a self-contained static browser screen for the current encounter roster through `--game-html`, showing generated build context in the normal shell header and opening on a real Algorithimia title/home screen. The companion `--static-bundle` command writes the same shell as `index.html` in a deployable folder with a minimal `vercel.json` and local/deploy notes, so the current title/home plus Chapter 0 shell can be checked locally or handed to Vercel as a static artifact without adding a backend, database, environment variables, or public code-execution service. The title screen is the current static-bundle front door: `Start Chapter 0` reveals a compact Chapter 0 briefing where Mira frames the jammed intake, Sorting Slime, visible rune repair, and non-disclosing Archive trust check; `Begin repair` then reveals the existing tiny explorable Queueworks room before the encounter tabs. The room opens with Mira's arrival line and a one-line objective to find the Sorting Slime and inspect the loose runes. The room uses simple DOM-positioned sprites, arrow/WASD/on-screen movement, lightweight blocked-tile collision for the Sorting Slime, jammed gate, and ledger clutter, an interactable Sorting Slime object, Agent 5's package-local Queueworks room sheet for the temporary Patchrunner and interaction prompt, Agent 5's room feedback sheet for movement/interact/failure/sealed/open status, Agent 5's room retry strip for the failed-return prompt, wrong-order return-to-room retry feedback, and a success return path that clears the jammed route blockers after the visible repair succeeds. The route-clear return now leaves a compact aftermath line that the stair accepts the repair and the intake starts moving again. The room status strip binds the current Agent 1/2 affordance cues to live states: blocked gate, visible-order retry, sealed-check retry, and route clear. Once the route is clear, repeated Sorting Slime interaction is disabled and the room cue stays on route-open feedback. The Sorting Slime panel includes a local browser interaction loop with rune-token selection, swaps, icon-supported check/reset controls, adjacent inspection marks, jammed/cleared route status, Mira feedback, and embedded Phase 1 Sorting Slime scene strip, Queueworks gate, Sorting Slime sprites, and action icons. Opening the exported shell with `?smoke=1` or `#smoke` runs a dependency-free in-page smoke path that verifies the title screen, start control, Chapter 0 briefing, and begin-repair control, enters the room, checks the arrival objective, then records whether the room viewport shows the normal build context, room, room status, room hint, and Sorting Slime target marker before any report-scrolling checks. It then covers keyboard/WASD movement via dispatched `keydown` events, on-screen movement, interaction, wrong-order return, rune swaps, success return, route-clear aftermath, repaired-state interaction, route-open status, visible cue dimensions, horizontal-overflow checks, 40px control-target checks, text-fit checks for key status cues, smoke-report row readability checks, and copyable build-context evidence; its smoke rows use Agent 5's `queueworks-browser-smoke-icons.svg` QA/status sheet while the normal playtest screen is unchanged. The smoke report also renders the shared browser evidence intake card fields so a live pass or fail can be copied back with generated build context, state tested, result, control path, viewport, viewport profile, orientation, page size, first viewport, capture quality, manual review prompt, observed cause, text/icon/collision agreement, likely owner, and next action. The report exposes the same content through a read-only copy field and `data-smoke-result`, `data-smoke-label`, `data-smoke-viewport`, `data-smoke-viewport-profile`, `data-smoke-orientation`, `data-smoke-page-size`, `data-smoke-first-viewport`, and `data-smoke-build` attributes for browser QA tooling. This interaction is a graphical vertical-slice bridge; it intentionally does not run player Python in the browser. Execution remains in the existing CLI adapter until the project has a stronger sandbox and a chosen live renderer target.

## Near-Term Extension Points

- Move encounter definitions into data files when content volume grows.
- Evolve the static shell into a live UI client after Henry chooses renderer/camera direction.
- Add more event kinds for graph traversal, stack/deque changes, recursion frames, and dynamic programming tables as those encounters land.
