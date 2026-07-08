from __future__ import annotations

import unittest

from algorithimia.encounters import get_encounter
from algorithimia.trace_viewer import render_trace_viewer


class TraceViewerTests(unittest.TestCase):
    def test_render_trace_viewer_embeds_assets_and_events(self) -> None:
        html = render_trace_viewer(get_encounter("sorting_slime"))

        self.assertIn("Sorting Slime", html)
        self.assertIn("data:image/svg+xml;base64", html)
        self.assertIn("data-kind=\"comparison\"", html)
        self.assertIn("5 &gt; 1", html)
        self.assertIn("Sealed certification active", html)
        self.assertIn("4 public teaching cases and 3 sealed checks", html)

    def test_render_trace_viewer_escapes_event_text(self) -> None:
        html = render_trace_viewer(get_encounter("sorting_slime"))

        self.assertNotIn("5 > 1", html)

    def test_render_trace_viewer_does_not_expose_certification_values(self) -> None:
        html = render_trace_viewer(get_encounter("sorting_slime"))

        self.assertNotIn("cert_reverse_runes", html)
        self.assertNotIn("9, 7, 5, 3, 1", html)
        self.assertNotIn("1, 3, 5, 7, 9", html)

    def test_render_trace_viewer_omits_certification_summary_without_cert_cases(self) -> None:
        html = render_trace_viewer(get_encounter("triage_line"))

        self.assertNotIn("Sealed certification active", html)


if __name__ == "__main__":
    unittest.main()
