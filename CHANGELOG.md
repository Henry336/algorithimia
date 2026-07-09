# Changelog

## Unreleased

- Reframed Sorting Slime as a Queueworks intake-ordering repair.
- Replaced the demo solution with manual insertion-sort logic.
- Rejected `sorted(...)` and `.sort()` for Sorting Slime submissions.
- Added CLI and sorting-helper regression coverage.
- Moved Python helper restrictions into encounter metadata so future encounters can set their own rules.
- Hardened Sorting Slime helper rejection so a simple alias of `sorted` is rejected too.
- Added `Triage Line Dispatcher Trial` as a second CLI encounter with urgent-ticket ordering, stable ties, and the two-urgent ordinary guard.
- Added encounter selection with `python -m algorithimia --encounter triage_line`.
- Improved the Triage CLI trace so it previews the ordinary-guard case with arrival, urgent override, stable tie, ordinary guard, and served labels.
- Added renderer-ready trace events with stable kinds, player-facing labels, and metadata payloads while preserving the current CLI trace text.
- Added validator-linked Triage debrief barks for buried urgency, broken stable ties, ordinary starvation, FIFO drift, and ticket identity mistakes.
- Added a static browser trace viewer export with embedded Phase 1 badge and trace-event icons through `--trace-html`.
- Hardened Sorting Slime again so indirect built-in `sorted` bindings through default arguments, lambda arguments, or tuple indexing are rejected.
- Added a GitHub Actions unit-test workflow for Python 3.11 pushes and pull requests.
- Hardened the Python adapter preflight so imports, dunder introspection, and dynamic evaluation/introspection helpers are rejected before player code runs.
- Added source-size and result-payload caps to the Python adapter to limit oversized local submissions and outputs.
- Added Sorting Slime certification cases so hard-coded answers for the public examples do not clear the encounter.
- Marked certification results separately from public teaching cases and sealed their CLI expected/actual values so hidden validation inputs are not exposed.
- Added a sealed-certification summary to the static trace viewer for encounters with hidden certification cases.
- Added a static browser game shell export with tabbed encounter selection, trace previews, run commands, embedded Phase 1 assets, and sealed-certification status.
- Added a browser-playable Sorting Slime swap/check slice inside the game shell with the Sorting Slime scene strip, Queueworks gate art, Sorting Slime placeholder art, visible rune tokens, Mira feedback, and reset/check controls.
- Added visible jammed/cleared route status and adjacent inspection marks to the browser-playable Sorting Slime slice.
- Added a tiny explorable Queueworks room to the browser game shell with player movement, an interactable Sorting Slime, Agent 5's room-sheet Patchrunner/prompt art, encounter transition, success return, and route-open room feedback.
- Wired Agent 5's Queueworks room feedback sheet and retry strip into the browser shell, then added wrong-order return-to-room retry feedback so failed repairs keep the intake visibly jammed.
- Added basic blocked-tile collision to the Queueworks room and made the jammed route blockers clear after a successful Sorting Slime repair.
- Added simple blocked tiles and collision feedback to the Queueworks room so the Patchrunner navigates around the Sorting Slime, jammed gate, and ledger clutter instead of walking through them.
- Integrated Agent 5's Sorting Slime action icon sheet into the browser repair controls and sealed-check reminder.
- Added a dependency-free browser self-smoke path for the exported game shell through `?smoke=1` or `#smoke`, covering movement, Sorting Slime interaction, wrong-order retry, rune swaps, successful return, and route-open status.
- Added live Queueworks room-affordance cues for blocked gate, retry, sealed-check, and route-clear states, plus a repeated-interact guard after the route is repaired.
- Integrated Agent 5's browser-smoke QA/status icon sheet into the optional `?smoke=1` / `#smoke` report without changing normal play.
- Expanded the optional browser self-smoke so it checks rendered visibility for room status, hint, retry, route-open, action-control, and smoke-report cues.
- Strengthened the optional browser self-smoke so it dispatches Arrow/WASD keydown movement, checks on-screen movement reaches interact range, and confirms repaired interaction cannot reopen the cleared room.
- Extended the optional browser self-smoke with horizontal-overflow checks, 40px control-target checks, cue text-fit checks, and smoke-report row readability checks across the room, Sorting Slime, retry, cleared, and report states.
- Added a browser evidence intake card to the optional self-smoke report so live-browser results include tested states, pass/fail label, control path, viewport, observed cause, owner, and next action.
- Fixed the optional browser self-smoke rune-swap script so the scripted visible spill stays sorted before the route-clear check.
- Added copyable text and machine-readable result metadata to the optional browser self-smoke report so Agent 4 or Henry can capture live-browser evidence more reliably.
- Added viewport profile and page-size metadata to the optional browser self-smoke report so narrow/mobile evidence is easier to classify.
- Added orientation, capture-quality, and manual-review prompts to the optional browser self-smoke evidence card so normal/narrow browser findings are easier to report.
- Added first-viewport composition capture to the optional browser self-smoke report so QA can tell whether the initial room/status/hint view was visible before smoke-report scrolling.
- Fixed the optional browser self-smoke first-viewport target marker so the Sorting Slime visibility summary can detect the room object it already reports.
- Added generated build context to the optional browser self-smoke evidence card so QA can distinguish stale exported HTML from the latest game head.
- Surfaced the generated build context in the normal browser shell header and made the optional self-smoke verify that it is visible before smoke-report scrolling.
- Added `data-smoke-orientation` and a self-smoke copy-field check so browser evidence metadata and copyable text both carry the generated build context cleanly.
- Added a static Algorithimia title/home screen to the browser shell, with `Start Chapter 0` opening the existing Queueworks room and the optional self-smoke verifying the title gate before room checks.
- Added `--static-bundle` to export a Vercel-ready static folder with `index.html`, minimal `vercel.json`, and local/deploy notes for the current title/home and Chapter 0 browser shell.
- Added a compact Chapter 0 briefing between the title screen and Queueworks room so Mira frames the jammed intake, Sorting Slime, and sealed trust check before player control.

## 0.1.0 - 2026-07-08

- Bootstrapped the Python package.
- Added terminal playable loop.
- Added first sorting encounter.
- Added Python-first adapter with timeout.
- Added deterministic unit tests.
