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
        self.assertIn("--sorting-actions: url(&quot;data:image/svg+xml;base64", html)
        self.assertIn("data-action-icon=\"check_order\"", html)
        self.assertIn("data-action-icon=\"reset_spill\"", html)
        self.assertIn("data-action-icon=\"sealed_check\"", html)
        self.assertIn(".action-icon[data-action-icon=\"check_order\"]", html)
        self.assertIn("data-state=\"inspect\"", html)
        self.assertIn("data-slice-status", html)
        self.assertIn("Adjacent rune inspection marks", html)
        self.assertIn("data-inspection-mark", html)
        self.assertIn("Route sealed: inspect and swap the loose runes.", html)
        self.assertIn("Route open: visible spill is ordered.", html)
        self.assertIn("Route sealed: at least one adjacent rune is out of order.", html)
        self.assertIn("Check order", html)
        self.assertIn("Reset spill", html)
        self.assertIn("--sorting-actions: url(&quot;data:image/svg+xml;base64", html)
        self.assertIn("data-action-icon=\"check_order\"", html)
        self.assertIn("data-action-icon=\"reset_spill\"", html)
        self.assertIn("data-action-icon=\"sealed_check\"", html)
        self.assertIn("Mira: Public spill loaded", html)
        self.assertIn("Mira: Good. It works when the mess changes. That is a repair.", html)
        self.assertIn("swap ${first} with ${second}", html)

    def test_render_game_shell_includes_sorting_action_icons(self) -> None:
        html = render_game_shell()

        self.assertIn("--sorting-actions: url(&quot;data:image/svg+xml;base64", html)
        self.assertIn("class=\"action primary with-icon\"", html)
        self.assertIn("data-action-icon=\"check_order\"", html)
        self.assertIn("data-action-icon=\"reset_spill\"", html)
        self.assertIn("data-action-icon=\"sealed_check\"", html)

    def test_render_game_shell_includes_explorable_queueworks_room(self) -> None:
        html = render_game_shell()

        self.assertIn("data-queueworks-room", html)
        self.assertIn("Tiny Queueworks Room", html)
        self.assertIn("Explorable Queueworks room", html)
        self.assertIn("Patchrunner player sprite", html)
        self.assertIn("--room-feedback: url(&quot;data:image/svg+xml;base64", html)
        self.assertIn("--room-retry: url(&quot;data:image/svg+xml;base64", html)
        self.assertIn("--room-sheet: url(&quot;data:image/svg+xml;base64", html)
        self.assertIn("room-spark", html)
        self.assertIn("data-blocked-tile=\"ledger stack\"", html)
        self.assertIn("data-blocked-tile=\"jammed gate base\"", html)
        self.assertIn("data-route-blocker", html)
        self.assertIn("Blocked ledger stack tile", html)
        self.assertIn("opensWhenClear: true", html)
        self.assertIn("roomState === 'cleared_intake' && tile.opensWhenClear", html)
        self.assertIn(".room-shell[data-room-state=\"cleared_intake\"] .room-blocker[data-route-blocker]", html)
        self.assertIn("data-room-hint", html)
        self.assertIn("The gate holds. The slime still owns this route.", html)
        self.assertIn("Blocked by ${blocker.label}. Move beside it and interact from there.", html)
        self.assertIn("blockedTileAt(nextPosition)", html)
        self.assertIn("Interactable Sorting Slime", html)
        self.assertIn("data-room-retry-panel", html)
        self.assertIn("data-retry-icon=\"blocked_return\"", html)
        self.assertIn("data-retry-icon=\"retry_prompt\"", html)
        self.assertIn("data-retry-icon=\"diagnostic_scratch\"", html)
        self.assertIn("data-retry-icon=\"visible_spill\"", html)
        self.assertIn("one rune is still out of order - retry the visible spill", html)
        self.assertIn("data-room-state=\"jammed_intake\"", html)
        self.assertIn("data-room-state-icon", html)
        self.assertIn("data-icon=\"move_hint\"", html)
        self.assertIn("data-icon=\"interact_ready\"", html)
        self.assertIn("data-icon=\"repair_failed\"", html)
        self.assertIn("data-icon=\"sealed_check_ready\"", html)
        self.assertIn("data-icon=\"route_open\"", html)
        self.assertIn("data-room-interact disabled", html)
        self.assertIn("interact.disabled = !isNearSlime() || roomState === 'cleared_intake'", html)
        self.assertIn("data-move=\"up\"", html)
        self.assertIn("data-move=\"left\"", html)
        self.assertIn("data-move=\"down\"", html)
        self.assertIn("data-move=\"right\"", html)
        self.assertIn("ArrowUp", html)
        self.assertIn("WASD", html)
        self.assertIn("selectTab(document.querySelector('#tab-sorting_slime'))", html)
        self.assertIn("window.algorithimiaRoom", html)
        self.assertIn("markSortingSlimeCleared", html)
        self.assertIn("markSortingSlimeFailed", html)
        self.assertIn("RETRY REPAIR", html)
        self.assertIn("One rune is still out of order. Try the repair again?", html)
        self.assertIn("The visible spill held, but the Archive did not trust the repair yet.", html)
        self.assertIn("Route clear. The stair will let you through.", html)
        self.assertIn("ROUTE OPEN", html)
        self.assertIn("Return to room", html)

    def test_render_game_shell_includes_browser_smoke_harness(self) -> None:
        html = render_game_shell()

        self.assertIn("data-smoke-report", html)
        self.assertIn("function runGameShellSmoke()", html)
        self.assertIn("location.search.includes('smoke=1')", html)
        self.assertIn("location.hash === '#smoke'", html)
        self.assertIn("interact enabled beside slime", html)
        self.assertIn("sorting panel active after interact", html)
        self.assertIn("wrong return keeps intake jammed", html)
        self.assertIn("visible spill clears after swaps", html)
        self.assertIn("success return opens route", html)
        self.assertIn("route status text updates", html)
        self.assertIn("interact disabled after repair", html)
        self.assertIn("cleared route blocker becomes passable", html)
        self.assertIn("document.querySelector('[data-player]').style.getPropertyValue('--x') === '8'", html)
        self.assertIn("Game shell smoke: PASS", html)
        self.assertIn("document.querySelector('[data-queueworks-room]').dataset.roomState === 'cleared_intake'", html)

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
