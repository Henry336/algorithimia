from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .encounters import ENCOUNTERS, get_encounter
from .engine import GameEngine
from .game_shell import write_game_shell, write_static_bundle
from .language.python_adapter import PythonAdapter
from .trace_viewer import write_trace_viewer
from .visualizers import encounter_trace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Play the Algorithimia prototype.")
    parser.add_argument(
        "--encounter",
        choices=sorted(ENCOUNTERS),
        default="sorting_slime",
        help="Encounter to play. Defaults to sorting_slime.",
    )
    parser.add_argument(
        "--solution",
        type=Path,
        help="Path to a Python file defining the encounter's solve(...) function. If omitted, a demo solution is used.",
    )
    parser.add_argument(
        "--trace-html",
        type=Path,
        help="Write a static browser trace viewer for the selected encounter and exit.",
    )
    parser.add_argument(
        "--game-html",
        type=Path,
        help="Write a static browser game shell for the current encounters and exit.",
    )
    parser.add_argument(
        "--static-bundle",
        type=Path,
        help="Write a Vercel-ready static browser bundle directory with index.html and deployment notes, then exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    encounter = get_encounter(args.encounter)

    if args.game_html:
        output_path = write_game_shell(args.game_html)
        print(f"Wrote game shell: {output_path}")
        return 0

    if args.static_bundle:
        output_dir = write_static_bundle(args.static_bundle)
        print(f"Wrote static browser bundle: {output_dir}")
        return 0

    if args.trace_html:
        output_path = write_trace_viewer(encounter, args.trace_html)
        print(f"Wrote trace viewer: {output_path}")
        return 0

    engine = GameEngine(adapter=PythonAdapter())

    if args.solution:
        if not args.solution.is_file():
            print(f"Could not read solution file: {args.solution}", file=sys.stderr)
            return 2
        source = args.solution.read_text(encoding="utf-8")
    else:
        source = encounter.default_solution

    print("Algorithimia")
    print("Encounter:", encounter.title)
    print(encounter.prompt)
    print()
    print("Trace:", " -> ".join(encounter_trace(encounter)))
    print()

    result = engine.attempt(encounter, source)
    print(result.message)
    for case_result in result.case_results:
        marker = "PASS" if case_result.passed else "FAIL"
        detail = f" error={case_result.error!r}" if case_result.error else ""
        case_type = "CERT" if case_result.certification else "PUBLIC"
        expected = "<sealed>" if case_result.certification else repr(case_result.expected)
        actual = "<sealed>" if case_result.certification else repr(case_result.actual)
        print(
            f"{marker} [{case_type}]: {case_result.case_name} "
            f"expected={expected} actual={actual}{detail}"
        )

    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
