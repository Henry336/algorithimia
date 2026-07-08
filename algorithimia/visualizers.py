from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .encounters import Encounter


@dataclass(frozen=True)
class TraceEvent:
    kind: str
    label: str
    payload: Mapping[str, object]


def encounter_trace_events(encounter: Encounter) -> list[TraceEvent]:
    preferred_case = (
        next((candidate for candidate in encounter.cases if candidate.name == encounter.trace_case_name), None)
        if encounter.trace_case_name
        else None
    )
    case = preferred_case or next((candidate for candidate in encounter.cases if list(candidate.input_values)), encounter.cases[0])
    if encounter.trace_kind == "comparison":
        return comparison_trace_events(case.input_values)
    if encounter.trace_kind == "triage":
        return triage_trace_events(case.input_values, case.expected)
    return [TraceEvent("empty", "no trace", {})]


def encounter_trace(encounter: Encounter) -> list[str]:
    return [event.label for event in encounter_trace_events(encounter)]


def comparison_trace_events(values: object) -> list[TraceEvent]:
    trace: list[TraceEvent] = []
    items = list(values)
    for index in range(len(items) - 1):
        left = items[index]
        right = items[index + 1]
        relation = "<=" if left <= right else ">"
        trace.append(
            TraceEvent(
                "comparison",
                f"{left} {relation} {right}",
                {"index": index, "left": left, "right": right, "relation": relation},
            )
        )
    return trace or [TraceEvent("empty", "no comparisons", {"count": len(items)})]


def comparison_trace(values: object) -> list[str]:
    return [event.label for event in comparison_trace_events(values)]


def triage_trace_events(tickets: object, served_order: object = ()) -> list[TraceEvent]:
    items = [ticket for ticket in list(tickets) if isinstance(ticket, dict)]
    if not items:
        return [TraceEvent("arrival_empty", "arrived: none", {"tickets": 0})]

    trace: list[TraceEvent] = []
    ordinary_waiting: list[str] = []
    urgent_waiting: list[str] = []
    for ticket in items:
        ticket_id = ticket.get("id", "?")
        arrival = ticket.get("arrival", "?")
        if ticket.get("urgent"):
            urgent_waiting.append(str(ticket_id))
            label = "urgent"
        else:
            ordinary_waiting.append(str(ticket_id))
            label = "ordinary"
        trace.append(
            TraceEvent(
                "arrival",
                f"arrived {ticket_id}@{arrival} {label}",
                {"ticket_id": ticket_id, "arrival": arrival, "urgent": bool(ticket.get("urgent"))},
            )
        )

    served_ids = [str(ticket_id) for ticket_id in served_order]
    urgent_streak = 0
    for ticket_id in served_ids:
        if ticket_id in urgent_waiting:
            if ordinary_waiting:
                trace.append(
                    TraceEvent(
                        "urgent_override",
                        f"urgent override: {ticket_id} before {ordinary_waiting[0]}",
                        {"ticket_id": ticket_id, "ordinary_ticket_id": ordinary_waiting[0]},
                    )
                )
            if urgent_streak:
                trace.append(
                    TraceEvent(
                        "stable_tie",
                        f"stable tie: {ticket_id} keeps urgent arrival order",
                        {"ticket_id": ticket_id, "urgent_streak": urgent_streak + 1},
                    )
                )
            urgent_waiting.remove(ticket_id)
            urgent_streak += 1
        elif ticket_id in ordinary_waiting:
            if urgent_streak >= 2:
                trace.append(
                    TraceEvent(
                        "ordinary_guard",
                        f"ordinary guard: {ticket_id} served after two urgent",
                        {"ticket_id": ticket_id, "urgent_streak": urgent_streak},
                    )
                )
            ordinary_waiting.remove(ticket_id)
            urgent_streak = 0
        trace.append(TraceEvent("served", f"served {ticket_id}", {"ticket_id": ticket_id}))
    return trace


def triage_trace(tickets: object, served_order: object = ()) -> list[str]:
    return [event.label for event in triage_trace_events(tickets, served_order)]
