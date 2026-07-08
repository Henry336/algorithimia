from __future__ import annotations

import unittest

from algorithimia.encounters import Encounter, EncounterCase, get_encounter
from algorithimia.engine import GameEngine
from algorithimia.language.python_adapter import PythonAdapter, PythonExecutionError
from algorithimia.visualizers import encounter_trace, encounter_trace_events

MANUAL_SORT = """
def solve(values):
    ordered = list(values)
    for i in range(1, len(ordered)):
        current = ordered[i]
        j = i - 1
        while j >= 0 and ordered[j] > current:
            ordered[j + 1] = ordered[j]
            j -= 1
        ordered[j + 1] = current
    return ordered
"""

TRIAGE_POLICY = """
def solve(tickets):
    waiting = sorted(tickets, key=lambda ticket: ticket["arrival"])
    served = []
    urgent_streak = 0

    while waiting:
        ordinary = [ticket for ticket in waiting if not ticket["urgent"]]
        if urgent_streak >= 2 and ordinary:
            chosen = ordinary[0]
            urgent_streak = 0
        else:
            urgent = [ticket for ticket in waiting if ticket["urgent"]]
            if urgent:
                chosen = urgent[0]
                urgent_streak += 1
            else:
                chosen = waiting[0]
                urgent_streak = 0

        served.append(chosen["id"])
        waiting.remove(chosen)

    return served
"""


class EngineTests(unittest.TestCase):
    def test_sorting_slime_accepts_correct_solution(self) -> None:
        engine = GameEngine(PythonAdapter())
        result = engine.attempt(get_encounter("sorting_slime"), MANUAL_SORT)

        self.assertTrue(result.passed)
        self.assertTrue(all(case.passed for case in result.case_results))

    def test_sorting_slime_rejects_built_in_sorted(self) -> None:
        engine = GameEngine(PythonAdapter())
        result = engine.attempt(get_encounter("sorting_slime"), "def solve(values):\n    return sorted(values)\n")

        self.assertFalse(result.passed)
        self.assertIn("visible sorting logic", result.case_results[0].error or "")

    def test_sorting_slime_rejects_aliased_built_in_sorted(self) -> None:
        engine = GameEngine(PythonAdapter())
        source = "def solve(values):\n    helper = sorted\n    return helper(values)\n"
        result = engine.attempt(get_encounter("sorting_slime"), source)

        self.assertFalse(result.passed)
        self.assertIn("visible sorting logic", result.case_results[0].error or "")

    def test_sorting_slime_rejects_list_sort(self) -> None:
        engine = GameEngine(PythonAdapter())
        source = "def solve(values):\n    ordered = list(values)\n    ordered.sort()\n    return ordered\n"
        result = engine.attempt(get_encounter("sorting_slime"), source)

        self.assertFalse(result.passed)
        self.assertIn("visible sorting logic", result.case_results[0].error or "")

    def test_python_call_restrictions_are_encounter_scoped(self) -> None:
        encounter = Encounter(
            slug="debug_sort",
            title="Debug Sort",
            prompt="Sort with any helper.",
            cases=(EncounterCase("mixed", (2, 1), (1, 2)),),
            success_message="ok",
            failure_message="failed",
            trace_kind="comparison",
            default_solution="def solve(values):\n    return sorted(values)\n",
        )
        engine = GameEngine(PythonAdapter())
        result = engine.attempt(encounter, "def solve(values):\n    return sorted(values)\n")

        self.assertTrue(result.passed)

    def test_sorting_slime_rejects_wrong_solution(self) -> None:
        engine = GameEngine(PythonAdapter())
        result = engine.attempt(get_encounter("sorting_slime"), "def solve(values):\n    return list(values)\n")

        self.assertFalse(result.passed)
        self.assertTrue(any(not case.passed for case in result.case_results))

    def test_triage_line_accepts_locked_policy(self) -> None:
        engine = GameEngine(PythonAdapter())
        result = engine.attempt(get_encounter("triage_line"), TRIAGE_POLICY)

        self.assertTrue(result.passed)
        self.assertTrue(all(case.passed for case in result.case_results))

    def test_triage_line_rejects_priority_sort_without_starvation_guard(self) -> None:
        engine = GameEngine(PythonAdapter())
        source = """
def solve(tickets):
    return [ticket["id"] for ticket in sorted(tickets, key=lambda ticket: (not ticket["urgent"], ticket["arrival"]))]
"""
        result = engine.attempt(get_encounter("triage_line"), source)

        self.assertFalse(result.passed)
        failed_cases = {case.case_name for case in result.case_results if not case.passed}
        self.assertIn("ordinary_guard_after_two_urgent", failed_cases)

    def test_triage_line_rejects_unknown_ticket_ids_with_bark(self) -> None:
        engine = GameEngine(PythonAdapter())
        result = engine.attempt(get_encounter("triage_line"), "def solve(tickets):\n    return ['MISSING']\n")

        self.assertFalse(result.passed)
        self.assertIn("Queueworks never issued", result.case_results[1].error or "")

    def test_triage_line_reports_urgent_buried_bark(self) -> None:
        engine = GameEngine(PythonAdapter())
        result = engine.attempt(get_encounter("triage_line"), "def solve(tickets):\n    return [ticket['id'] for ticket in tickets]\n")

        urgent_case = next(case for case in result.case_results if case.case_name == "urgent_override")
        self.assertFalse(urgent_case.passed)
        self.assertIn("alarm rune was buried", urgent_case.error or "")

    def test_triage_line_reports_stable_tie_bark(self) -> None:
        engine = GameEngine(PythonAdapter())
        source = """
def solve(tickets):
    if len(tickets) == 3 and tickets[0]["urgent"] and tickets[1]["urgent"]:
        return [tickets[1]["id"], tickets[0]["id"], tickets[2]["id"]]
    waiting = sorted(tickets, key=lambda ticket: ticket["arrival"])
    urgent = [ticket for ticket in waiting if ticket["urgent"]]
    ordinary = [ticket for ticket in waiting if not ticket["urgent"]]
    return [ticket["id"] for ticket in urgent + ordinary]
"""
        result = engine.attempt(get_encounter("triage_line"), source)

        stable_tie_case = next(case for case in result.case_results if case.case_name == "stable_urgent_ties")
        self.assertFalse(stable_tie_case.passed)
        self.assertIn("equal urgency still keeps arrival order", stable_tie_case.error or "")

    def test_triage_line_reports_ordinary_starved_bark(self) -> None:
        engine = GameEngine(PythonAdapter())
        source = """
def solve(tickets):
    waiting = sorted(tickets, key=lambda ticket: ticket["arrival"])
    return [ticket["id"] for ticket in sorted(waiting, key=lambda ticket: (not ticket["urgent"], ticket["arrival"]))]
"""
        result = engine.attempt(get_encounter("triage_line"), source)

        guard_case = next(case for case in result.case_results if case.case_name == "ordinary_guard_after_two_urgent")
        self.assertFalse(guard_case.passed)
        self.assertIn("after two urgent tickets", guard_case.error or "")

    def test_triage_line_trace_previews_starvation_guard_case(self) -> None:
        trace = encounter_trace(get_encounter("triage_line"))

        self.assertIn("urgent override: B before A", trace)
        self.assertIn("stable tie: C keeps urgent arrival order", trace)
        self.assertIn("ordinary guard: A served after two urgent", trace)
        self.assertIn("served A", trace)

    def test_trace_events_preserve_renderer_ready_triage_metadata(self) -> None:
        events = encounter_trace_events(get_encounter("triage_line"))
        event_kinds = [event.kind for event in events]

        self.assertIn("arrival", event_kinds)
        self.assertIn("urgent_override", event_kinds)
        self.assertIn("stable_tie", event_kinds)
        self.assertIn("ordinary_guard", event_kinds)
        self.assertIn("served", event_kinds)

        ordinary_guard = next(event for event in events if event.kind == "ordinary_guard")
        self.assertEqual("A", ordinary_guard.payload["ticket_id"])
        self.assertEqual(2, ordinary_guard.payload["urgent_streak"])

    def test_trace_events_keep_existing_terminal_labels(self) -> None:
        encounter = get_encounter("sorting_slime")
        self.assertEqual(encounter_trace(encounter), [event.label for event in encounter_trace_events(encounter)])

    def test_adapter_requires_solve_function(self) -> None:
        adapter = PythonAdapter()

        with self.assertRaises(PythonExecutionError):
            adapter.run("answer = 42", (1, 2, 3))

    def test_adapter_times_out_infinite_loop(self) -> None:
        adapter = PythonAdapter(timeout_seconds=0.25)

        with self.assertRaises(PythonExecutionError):
            adapter.run("def solve(values):\n    while True:\n        pass\n", (1, 2, 3))


if __name__ == "__main__":
    unittest.main()
