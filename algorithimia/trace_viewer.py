from __future__ import annotations

import base64
import html
from pathlib import Path

from .encounters import Encounter
from .visualizers import TraceEvent, encounter_trace_events

ASSET_DIR = Path(__file__).parent / "assets" / "phase1"
EVENT_SHEET = ASSET_DIR / "trace-event-kinds.svg"
BADGE_SHEET = ASSET_DIR / "encounter-badges.svg"
CERTIFICATION_SHEET = ASSET_DIR / "sorting-certification-markers.svg"

EVENT_ICON_CELLS = {
    "comparison": 0,
    "arrival": 1,
    "arrival_empty": 1,
    "urgent_override": 2,
    "stable_tie": 3,
    "ordinary_guard": 4,
    "served": 5,
    "empty": 0,
}

BADGE_CELLS = {
    "sorting_slime": 0,
    "triage_line": 1,
}


def write_trace_viewer(encounter: Encounter, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_trace_viewer(encounter), encoding="utf-8")
    return output_path


def render_trace_viewer(encounter: Encounter) -> str:
    events = encounter_trace_events(encounter)
    event_sheet_uri = _svg_data_uri(EVENT_SHEET)
    badge_sheet_uri = _svg_data_uri(BADGE_SHEET)
    certification_sheet_uri = _svg_data_uri(CERTIFICATION_SHEET)
    badge_cell = BADGE_CELLS.get(encounter.slug, 0)
    event_rows = "\n".join(_event_row(event, index) for index, event in enumerate(events, start=1))
    certification_summary = _certification_summary(encounter, certification_sheet_uri)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(encounter.title)} Trace</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #10151d;
      --panel: #18212c;
      --line: #2d3a4a;
      --text: #f8fafc;
      --muted: #aab6c5;
      --gold: #f8c14a;
      --cyan: #38bdf8;
      --green: #39d98a;
      --rose: #ef476f;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font: 16px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      width: min(980px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 32px;
    }}
    header {{
      border-bottom: 2px solid var(--line);
      padding-bottom: 18px;
      display: grid;
      gap: 10px;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(1.65rem, 4vw, 2.5rem);
      line-height: 1.08;
      letter-spacing: 0;
    }}
    .meta {{
      display: flex;
      gap: 12px;
      align-items: center;
      color: var(--muted);
      flex-wrap: wrap;
    }}
    .badge, .icon {{
      display: inline-block;
      flex: 0 0 auto;
      image-rendering: pixelated;
      background-repeat: no-repeat;
      background-size: auto 32px;
      width: 32px;
      height: 32px;
    }}
    .badge {{
      background-image: url("{badge_sheet_uri}");
      background-position: -{badge_cell * 32}px 0;
    }}
    .icon {{
      background-image: url("{event_sheet_uri}");
    }}
    .cert-icon {{
      background-image: url("{certification_sheet_uri}");
    }}
    .prompt {{
      max-width: 72ch;
      color: var(--muted);
      margin: 0;
    }}
    .trace {{
      margin-top: 22px;
      display: grid;
      gap: 10px;
    }}
    .certification {{
      margin-top: 18px;
      padding: 12px;
      display: grid;
      grid-template-columns: 40px minmax(0, 1fr);
      gap: 12px;
      align-items: center;
      background: var(--panel);
      border: 1px solid var(--line);
      border-left: 5px solid var(--gold);
    }}
    .cert-title {{
      font-weight: 700;
    }}
    .cert-copy {{
      color: var(--muted);
      margin-top: 2px;
      overflow-wrap: anywhere;
    }}
    .event {{
      min-height: 54px;
      display: grid;
      grid-template-columns: 36px 40px minmax(0, 1fr);
      gap: 12px;
      align-items: center;
      padding: 10px 12px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-left: 5px solid var(--cyan);
    }}
    .event[data-kind="urgent_override"], .event[data-kind="ordinary_guard"] {{
      border-left-color: var(--rose);
    }}
    .event[data-kind="stable_tie"] {{
      border-left-color: var(--gold);
    }}
    .event[data-kind="served"] {{
      border-left-color: var(--green);
    }}
    .step {{
      color: var(--muted);
      font-variant-numeric: tabular-nums;
      text-align: right;
    }}
    .label {{
      overflow-wrap: anywhere;
      font-weight: 650;
    }}
    .payload {{
      margin-top: 3px;
      color: var(--muted);
      font: 0.85rem/1.3 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      overflow-wrap: anywhere;
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div class="meta"><span class="badge" aria-hidden="true"></span><span>{html.escape(encounter.slug)}</span></div>
      <h1>{html.escape(encounter.title)}</h1>
      <p class="prompt">{html.escape(encounter.prompt)}</p>
    </header>
{certification_summary}
    <section class="trace" aria-label="Trace events">
{event_rows}
    </section>
  </main>
</body>
</html>
"""


def _event_row(event: TraceEvent, index: int) -> str:
    cell = EVENT_ICON_CELLS.get(event.kind, 0)
    payload = " ".join(f"{key}={value!r}" for key, value in event.payload.items())
    return f"""      <article class="event" data-kind="{html.escape(event.kind)}">
        <div class="step">{index:02d}</div>
        <span class="icon" aria-hidden="true" style="background-position: -{cell * 32}px 0"></span>
        <div>
          <div class="label">{html.escape(event.label)}</div>
          <div class="payload">{html.escape(payload)}</div>
        </div>
      </article>"""


def _certification_summary(encounter: Encounter, sheet_uri: str) -> str:
    public_count = len(encounter.cases)
    certification_count = len(encounter.certification_cases)
    if certification_count == 0:
        return ""

    return f"""    <section class="certification" aria-label="Certification checks">
      <span class="icon cert-icon" aria-hidden="true" style="background-image: url(&quot;{sheet_uri}&quot;); background-position: -32px 0"></span>
      <div>
        <div class="cert-title">Sealed certification active</div>
        <div class="cert-copy">{public_count} public teaching cases and {certification_count} sealed checks. Hidden inputs stay sealed; memorized public answers do not clear this encounter.</div>
      </div>
    </section>"""


def _svg_data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"
