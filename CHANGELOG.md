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

## 0.1.0 - 2026-07-08

- Bootstrapped the Python package.
- Added terminal playable loop.
- Added first sorting encounter.
- Added Python-first adapter with timeout.
- Added deterministic unit tests.
