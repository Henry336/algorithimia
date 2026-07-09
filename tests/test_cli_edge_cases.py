from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from algorithimia.cli import main


class CliEdgeCaseTests(unittest.TestCase):
    def test_missing_solution_file_returns_clean_failure(self) -> None:
        missing = Path("missing-player-solution.py")

        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = main(["--solution", str(missing)])

        self.assertNotEqual(exit_code, 0)
        self.assertIn("solution", stderr.getvalue().lower())

    def test_trace_html_writes_static_viewer_without_running_solution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "trace.html"
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(["--encounter", "triage_line", "--trace-html", str(output_path)])

            html = output_path.read_text(encoding="utf-8")

        self.assertEqual(0, exit_code)
        self.assertIn("Wrote trace viewer", stdout.getvalue())
        self.assertIn("Triage Line Dispatcher Trial", html)
        self.assertIn("data:image/svg+xml;base64", html)
        self.assertIn("ordinary guard: A served after two urgent", html)

    def test_game_html_writes_static_shell_without_running_solution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "game.html"
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(["--game-html", str(output_path)])

            html = output_path.read_text(encoding="utf-8")

        self.assertEqual(0, exit_code)
        self.assertIn("Wrote game shell", stdout.getvalue())
        self.assertIn("Sorting Slime", html)
        self.assertIn("Triage Line Dispatcher Trial", html)
        self.assertIn("role=\"tablist\"", html)
        self.assertIn("data:image/svg+xml;base64", html)

    def test_static_bundle_writes_vercel_ready_folder_without_running_solution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "site"
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(["--static-bundle", str(output_dir)])

            html = (output_dir / "index.html").read_text(encoding="utf-8")
            vercel = (output_dir / "vercel.json").read_text(encoding="utf-8")
            readme = (output_dir / "README.txt").read_text(encoding="utf-8")

        self.assertEqual(0, exit_code)
        self.assertIn("Wrote static browser bundle", stdout.getvalue())
        self.assertIn("data-game-root data-screen=\"title\"", html)
        self.assertIn("Start Chapter 0", html)
        self.assertIn("local --game-html export", html)
        self.assertIn('"cleanUrls": true', vercel)
        self.assertIn("no backend, database, or environment variables", readme)

    def test_certification_cases_are_sealed_in_cli_output(self) -> None:
        source = """
def solve(values):
    fixtures = {
        (5, 1, 4, 2): [1, 2, 4, 5],
        (1, 2, 3): [1, 2, 3],
        (3, 1, 3, 2): [1, 2, 3, 3],
        (): [],
    }
    return fixtures[tuple(values)]
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            solution_path = Path(temp_dir) / "oracle.py"
            solution_path.write_text(source, encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(["--solution", str(solution_path)])

        output = stdout.getvalue()
        self.assertNotEqual(0, exit_code)
        self.assertIn("FAIL [CERT]: cert_reverse_runes expected=<sealed> actual=<sealed>", output)
        self.assertIn("hidden spill proved the routine was memorized", output)
        self.assertNotIn("(9, 7, 5, 3, 1)", output)
        self.assertNotIn("(1, 3, 5, 7, 9)", output)


if __name__ == "__main__":
    unittest.main()
