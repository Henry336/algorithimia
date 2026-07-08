from __future__ import annotations

import unittest

from algorithimia.game_shell import render_game_shell


class GameShellTests(unittest.TestCase):
    def test_render_game_shell_includes_current_encounters_and_assets(self) -> None:
        html = render_game_shell()

        self.assertIn("Algorithimia", html)
        self.assertIn("Sorting Slime", html)
        self.assertIn("Triage Line Dispatcher Trial", html)
        self.assertIn("role=\"tablist\"", html)
        self.assertIn("data:image/svg+xml;base64", html)
        self.assertIn("python -m algorithimia --encounter triage_line", html)
        self.assertIn("ordinary guard: A served after two urgent", html)

    def test_render_game_shell_includes_playable_sorting_slime_slice(self) -> None:
        html = render_game_shell()

        self.assertIn("data-sorting-slime-playfield", html)
        self.assertIn("data-values=\"5,1,4,2\"", html)
        self.assertIn("Blocked Queueworks Intake", html)
        self.assertIn("Sorting Slime scene strip", html)
        self.assertIn("Jammed Queueworks intake gate", html)
        self.assertIn("Loose rune tokens", html)
        self.assertIn("Check order", html)
        self.assertIn("Reset spill", html)
        self.assertIn("Mira: Public spill loaded", html)
        self.assertIn("Mira: Good. It works when the mess changes. That is a repair.", html)
        self.assertIn("swap ${first} with ${second}", html)

    def test_render_game_shell_seals_certification_values(self) -> None:
        html = render_game_shell()

        self.assertIn("Sealed certification active", html)
        self.assertIn("4 public teaching cases and 3 sealed checks", html)
        self.assertNotIn("cert_reverse_runes", html)
        self.assertNotIn("9, 7, 5, 3, 1", html)
        self.assertNotIn("1, 3, 5, 7, 9", html)

    def test_render_game_shell_escapes_trace_text(self) -> None:
        html = render_game_shell()

        self.assertIn("5 &gt; 1", html)
        self.assertNotIn("5 > 1", html)


if __name__ == "__main__":
    unittest.main()
