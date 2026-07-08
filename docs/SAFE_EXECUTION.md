# Safe Execution Notes

The first Python adapter is a baseline local guard, not a complete hostile-code sandbox.

Current controls:

- child process execution
- isolated Python mode (`-I`)
- per-case timeout
- temporary working directory
- minimal environment
- restricted builtins for player code
- source preflight that rejects imports
- source preflight that rejects dunder introspection
- source preflight that rejects dynamic evaluation/introspection helpers such as `eval`, `exec`, `open`, `getattr`, `globals`, and `__import__`
- submitted source-size cap before AST parsing or subprocess execution
- serialized result-size cap inside the child runner before stdout handoff
- preflight rejection of disallowed sorting helpers for the current DSA encounter
- JSON-only input/output

Known gaps:

- no OS-level syscall, CPU, or memory isolation
- no container or job-object limit
- no durable audit log for submissions
- no multi-language runner contract yet
- AST preflight is a local guardrail, not a security boundary against hostile Python experts
- size caps reduce accidental blowups but do not prevent all memory exhaustion inside hostile code

Before accepting public arbitrary code, replace this adapter boundary with OS-level isolation and resource limits.
