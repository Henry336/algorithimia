from __future__ import annotations

import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from algorithimia.encounters import PythonCallRestriction


class PythonExecutionError(RuntimeError):
    """Raised when player Python cannot be executed cleanly."""


_DISALLOWED_DYNAMIC_NAMES = {
    "__import__",
    "compile",
    "delattr",
    "dir",
    "eval",
    "exec",
    "getattr",
    "globals",
    "input",
    "locals",
    "open",
    "setattr",
    "vars",
}


class PythonAdapter:
    def __init__(
        self,
        timeout_seconds: float = 2.0,
        max_source_chars: int = 20_000,
        max_result_json_chars: int = 20_000,
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._max_source_chars = max_source_chars
        self._max_result_json_chars = max_result_json_chars

    def run(
        self,
        source: str,
        input_values: object,
        python_call_restrictions: tuple[PythonCallRestriction, ...] = (),
    ) -> object:
        if len(source) > self._max_source_chars:
            raise PythonExecutionError("player code is too large for this encounter")

        _reject_disallowed_python_syntax(source)
        _reject_disallowed_python_calls(source, python_call_restrictions)

        with tempfile.TemporaryDirectory(prefix="algorithimia_") as tmp:
            tmp_path = Path(tmp)
            runner = tmp_path / "runner.py"
            runner.write_text(
                _runner_source(source, python_call_restrictions, self._max_result_json_chars),
                encoding="utf-8",
            )

            try:
                process = subprocess.run(
                    [sys.executable, "-I", str(runner)],
                    input=json.dumps({"values": list(input_values)}),
                    text=True,
                    capture_output=True,
                    timeout=self._timeout_seconds,
                    cwd=tmp,
                    env={"PYTHONIOENCODING": "utf-8"},
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise PythonExecutionError("player code timed out") from exc

        if process.returncode != 0:
            detail = process.stderr.strip() or process.stdout.strip() or "player code failed"
            raise PythonExecutionError(detail)

        try:
            payload = json.loads(process.stdout)
        except json.JSONDecodeError as exc:
            raise PythonExecutionError("player code did not return valid JSON") from exc

        if not payload.get("ok"):
            raise PythonExecutionError(str(payload.get("error", "player code failed")))
        return payload.get("result")


def _reject_disallowed_python_syntax(source: str) -> None:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise PythonExecutionError("Imports are not available in Algorithimia puzzle submissions.")
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise PythonExecutionError("Dunder introspection is not available in Algorithimia puzzle submissions.")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise PythonExecutionError("Dunder introspection is not available in Algorithimia puzzle submissions.")
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id in _DISALLOWED_DYNAMIC_NAMES:
            raise PythonExecutionError(f"{node.id} is not available in Algorithimia puzzle submissions.")


def _reject_disallowed_python_calls(source: str, restrictions: tuple[PythonCallRestriction, ...]) -> None:
    if not restrictions:
        return

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return

    disallowed_aliases = _find_disallowed_aliases(tree, restrictions)
    for node in ast.walk(tree):
        if _is_restricted_builtin_load(node, restrictions):
            raise PythonExecutionError(_restriction_message(node.id, restrictions))
        if not isinstance(node, ast.Call):
            continue
        for restriction in restrictions:
            if (
                restriction.target == "function"
                and isinstance(node.func, ast.Name)
                and (node.func.id == restriction.name or node.func.id in disallowed_aliases)
            ):
                raise PythonExecutionError(restriction.message)
            if (
                restriction.target == "method"
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == restriction.name
            ):
                raise PythonExecutionError(restriction.message)
            if (
                restriction.target == "method"
                and isinstance(node.func, ast.Name)
                and node.func.id in disallowed_aliases
            ):
                raise PythonExecutionError(restriction.message)


def _is_restricted_builtin_load(node: ast.AST, restrictions: tuple[PythonCallRestriction, ...]) -> bool:
    if not isinstance(node, ast.Name) or not isinstance(node.ctx, ast.Load):
        return False
    return any(
        restriction.target == "function" and node.id == restriction.name
        for restriction in restrictions
    )


def _restriction_message(name: str, restrictions: tuple[PythonCallRestriction, ...]) -> str:
    for restriction in restrictions:
        if restriction.target == "function" and restriction.name == name:
            return restriction.message
    return "That helper is restricted for this encounter."


def _find_disallowed_aliases(
    tree: ast.AST,
    restrictions: tuple[PythonCallRestriction, ...],
) -> set[str]:
    aliases: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not _is_disallowed_alias_value(node.value, restrictions, aliases):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                aliases.add(target.id)
    return aliases


def _is_disallowed_alias_value(
    value: ast.expr,
    restrictions: tuple[PythonCallRestriction, ...],
    aliases: set[str],
) -> bool:
    for restriction in restrictions:
        if restriction.target == "function" and isinstance(value, ast.Name):
            if value.id == restriction.name or value.id in aliases:
                return True
        if restriction.target == "method" and isinstance(value, ast.Attribute):
            if value.attr == restriction.name:
                return True
        if restriction.target == "method" and isinstance(value, ast.Name):
            if value.id in aliases:
                return True
    return False


def _restricted_builtin_names(restrictions: tuple[PythonCallRestriction, ...]) -> tuple[str, ...]:
    return tuple(
        restriction.name
        for restriction in restrictions
        if restriction.target == "function"
    )


def _runner_source(
    player_source: str,
    restrictions: tuple[PythonCallRestriction, ...],
    max_result_json_chars: int,
) -> str:
    encoded_source = json.dumps(player_source)
    restricted_builtin_names = json.dumps(_restricted_builtin_names(restrictions))
    encoded_max_result_json_chars = json.dumps(max_result_json_chars)
    return f"""
import json

SAFE_BUILTINS = {{
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "range": range,
    "reversed": reversed,
    "sorted": sorted,
    "sum": sum,
    "tuple": tuple,
}}

for blocked_name in {restricted_builtin_names}:
    SAFE_BUILTINS.pop(blocked_name, None)

namespace = {{"__builtins__": SAFE_BUILTINS}}
try:
    exec({encoded_source}, namespace, namespace)
    solve = namespace.get("solve")
    if not callable(solve):
        raise TypeError("submission must define solve(values)")
    payload = json.loads(input())
    result = solve(tuple(payload["values"]))
    result_json = json.dumps({{"ok": True, "result": result}})
    if len(result_json) > {encoded_max_result_json_chars}:
        raise ValueError("player result is too large")
    print(result_json)
except BaseException as exc:
    print(json.dumps({{"ok": False, "error": f"{{type(exc).__name__}}: {{exc}}"}}))
""".lstrip()
