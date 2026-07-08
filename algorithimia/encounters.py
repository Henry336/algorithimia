from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal


PythonCallTarget = Literal["function", "method"]
TraceKind = Literal["comparison", "triage"]
OutputValidator = Callable[["EncounterCase", object], str | None]


@dataclass(frozen=True)
class PythonCallRestriction:
    target: PythonCallTarget
    name: str
    message: str


@dataclass(frozen=True)
class EncounterCase:
    name: str
    input_values: object
    expected: object


@dataclass(frozen=True)
class Encounter:
    slug: str
    title: str
    prompt: str
    cases: tuple[EncounterCase, ...]
    success_message: str
    failure_message: str
    trace_kind: TraceKind
    default_solution: str
    python_call_restrictions: tuple[PythonCallRestriction, ...] = ()
    output_validator: OutputValidator | None = None
    trace_case_name: str | None = None


SORTING_SLIME = Encounter(
    slug="sorting_slime",
    title="Sorting Slime",
    prompt=(
        "Queueworks gate gunk has mixed the intake runes out of order. Define solve(values) "
        "with visible sorting logic so the runes return from smallest to largest. Built-in "
        "sorting helpers are rejected in this encounter."
    ),
    cases=(
        EncounterCase("mixed_runes", (5, 1, 4, 2), (1, 2, 4, 5)),
        EncounterCase("already_ordered", (1, 2, 3), (1, 2, 3)),
        EncounterCase("duplicates", (3, 1, 3, 2), (1, 2, 3, 3)),
        EncounterCase("empty", (), ()),
    ),
    python_call_restrictions=(
        PythonCallRestriction(
            target="function",
            name="sorted",
            message="Sorting Slime requires visible sorting logic; replace sorted(...) with your own loop.",
        ),
        PythonCallRestriction(
            target="method",
            name="sort",
            message="Sorting Slime requires visible sorting logic; replace .sort() with your own loop.",
        ),
    ),
    success_message="The Sorting Slime dissolves into a clean path.",
    failure_message="The slime reforms. Review the failed cases.",
    trace_kind="comparison",
    default_solution="""\
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
""",
)


def _ticket(ticket_id: str, arrival: int, urgent: bool) -> dict[str, object]:
    return {"id": ticket_id, "arrival": arrival, "urgent": urgent}


TRIAGE_POLICY_BARKS = {
    "stable_ordinary_line": "Mira taps the counter strip: ordinary tickets still need first-in, first-out service.",
    "urgent_override": "The alarm rune was buried. Urgent tickets may step ahead without erasing the line.",
    "stable_urgent_ties": "The Dispatcher points to the timestamps: equal urgency still keeps arrival order.",
    "ordinary_guard_after_two_urgent": (
        "Mira marks the third alarm: after two urgent tickets, the oldest ordinary ticket needs a turn."
    ),
}


def _validate_triage_line(case: EncounterCase, actual: object) -> str | None:
    if not isinstance(actual, (list, tuple)):
        return "Triage Line needs solve(tickets) to return a list of ticket ids."

    actual_ids = list(actual)
    known_ids = {ticket["id"] for ticket in case.input_values if isinstance(ticket, dict)}
    unknown_ids = [ticket_id for ticket_id in actual_ids if ticket_id not in known_ids]
    if unknown_ids:
        return "The counter called a ticket the Queueworks never issued."

    if len(actual_ids) != len(known_ids) or len(set(actual_ids)) != len(actual_ids):
        return "Every issued ticket id must be served exactly once."

    if tuple(actual_ids) != case.expected:
        return TRIAGE_POLICY_BARKS.get(case.name, "The archived strip does not match the expected service policy.")

    return None


TRIAGE_LINE = Encounter(
    slug="triage_line",
    title="Triage Line Dispatcher Trial",
    prompt=(
        "The Dispatcher opens an archived counter strip. Define solve(tickets) and return ticket ids "
        "in service order: urgent tickets may advance, equal priority keeps arrival order, and after "
        "two urgent services the oldest waiting ordinary ticket must be served if one exists."
    ),
    cases=(
        EncounterCase("empty_intake", (), ()),
        EncounterCase(
            "stable_ordinary_line",
            (
                _ticket("A", 0, False),
                _ticket("B", 1, False),
                _ticket("C", 2, False),
            ),
            ("A", "B", "C"),
        ),
        EncounterCase(
            "urgent_override",
            (
                _ticket("A", 0, False),
                _ticket("B", 1, True),
                _ticket("C", 2, False),
            ),
            ("B", "A", "C"),
        ),
        EncounterCase(
            "stable_urgent_ties",
            (
                _ticket("A", 0, True),
                _ticket("B", 1, True),
                _ticket("C", 2, False),
            ),
            ("A", "B", "C"),
        ),
        EncounterCase(
            "ordinary_guard_after_two_urgent",
            (
                _ticket("A", 0, False),
                _ticket("B", 1, True),
                _ticket("C", 2, True),
                _ticket("D", 3, True),
                _ticket("E", 4, False),
            ),
            ("B", "C", "A", "D", "E"),
        ),
    ),
    success_message="The counter breathes again: alarms rose, ties held, and no ordinary ticket disappeared.",
    failure_message="The archived strip flickers. Check urgency, stable ties, and the ordinary guard.",
    trace_kind="triage",
    default_solution="""\
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
""",
    output_validator=_validate_triage_line,
    trace_case_name="ordinary_guard_after_two_urgent",
)


ENCOUNTERS = {encounter.slug: encounter for encounter in (SORTING_SLIME, TRIAGE_LINE)}


def get_encounter(slug: str) -> Encounter:
    try:
        return ENCOUNTERS[slug]
    except KeyError as exc:
        raise ValueError(f"Unknown encounter: {slug}") from exc
