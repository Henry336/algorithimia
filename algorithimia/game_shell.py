from __future__ import annotations

import base64
import html
from pathlib import Path

from .encounters import ENCOUNTERS, Encounter
from .visualizers import TraceEvent, encounter_trace_events

ASSET_DIR = Path(__file__).parent / "assets" / "phase1"
BADGE_SHEET = ASSET_DIR / "encounter-badges.svg"
EVENT_SHEET = ASSET_DIR / "trace-event-kinds.svg"
CERTIFICATION_SHEET = ASSET_DIR / "sorting-certification-markers.svg"
SORTING_SLIME_SPRITE = ASSET_DIR / "sorting-slime.svg"
QUEUE_GATE_SPRITE = ASSET_DIR / "queue-intake-gate.svg"
SORTING_SLIME_SCENE_STRIP = ASSET_DIR / "sorting-slime-scene-strip.svg"
SORTING_ACTION_ICONS = ASSET_DIR / "sorting-action-icons.svg"
QUEUEWORKS_ROOM_SHEET = ASSET_DIR / "queueworks-room-sheet.svg"
QUEUEWORKS_ROOM_FEEDBACK_SHEET = ASSET_DIR / "queueworks-room-feedback.svg"
QUEUEWORKS_ROOM_RETRY_SHEET = ASSET_DIR / "queueworks-room-retry-strip.svg"
QUEUEWORKS_BROWSER_SMOKE_ICONS = ASSET_DIR / "queueworks-browser-smoke-icons.svg"

BADGE_CELLS = {
    "sorting_slime": 0,
    "triage_line": 1,
}

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


def write_game_shell(output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_game_shell(), encoding="utf-8")
    return output_path


def render_game_shell() -> str:
    badge_sheet_uri = _svg_data_uri(BADGE_SHEET)
    event_sheet_uri = _svg_data_uri(EVENT_SHEET)
    certification_sheet_uri = _svg_data_uri(CERTIFICATION_SHEET)
    sorting_slime_uri = _svg_data_uri(SORTING_SLIME_SPRITE)
    queue_gate_uri = _svg_data_uri(QUEUE_GATE_SPRITE)
    sorting_scene_uri = _svg_data_uri(SORTING_SLIME_SCENE_STRIP)
    sorting_action_uri = _svg_data_uri(SORTING_ACTION_ICONS)
    room_sheet_uri = _svg_data_uri(QUEUEWORKS_ROOM_SHEET)
    room_feedback_uri = _svg_data_uri(QUEUEWORKS_ROOM_FEEDBACK_SHEET)
    room_retry_uri = _svg_data_uri(QUEUEWORKS_ROOM_RETRY_SHEET)
    smoke_icons_uri = _svg_data_uri(QUEUEWORKS_BROWSER_SMOKE_ICONS)
    encounters = tuple(ENCOUNTERS.values())
    tabs = "\n".join(_tab_button(encounter, index) for index, encounter in enumerate(encounters))
    panels = "\n".join(
        _encounter_panel(
            encounter,
            index,
            badge_sheet_uri,
            event_sheet_uri,
            certification_sheet_uri,
            sorting_slime_uri,
            queue_gate_uri,
            sorting_scene_uri,
            sorting_action_uri,
        )
        for index, encounter in enumerate(encounters)
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Algorithimia Game Shell</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #10151d;
      --surface: #151d27;
      --panel: #1b2633;
      --line: #344255;
      --text: #f8fafc;
      --muted: #aab6c5;
      --gold: #f8c14a;
      --cyan: #38bdf8;
      --green: #39d98a;
      --rose: #ef476f;
      --ink: #0b1017;
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
      width: min(1120px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 24px 0 32px;
    }}
    .topbar {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 16px;
      padding-bottom: 14px;
      border-bottom: 2px solid var(--line);
    }}
    h1, h2, h3, p {{
      margin: 0;
    }}
    h1 {{
      font-size: clamp(1.6rem, 3vw, 2.35rem);
      line-height: 1.05;
      letter-spacing: 0;
    }}
    .status {{
      color: var(--muted);
      font-size: 0.95rem;
      white-space: nowrap;
    }}
    .tabs {{
      display: flex;
      gap: 8px;
      margin: 18px 0;
      overflow-x: auto;
      padding-bottom: 2px;
    }}
    .tab {{
      border: 1px solid var(--line);
      background: var(--surface);
      color: var(--text);
      min-height: 42px;
      padding: 8px 12px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      font: inherit;
      flex: 0 0 auto;
    }}
    .tab[aria-selected="true"] {{
      border-color: var(--cyan);
      box-shadow: inset 0 -3px 0 var(--cyan);
    }}
    .panel {{
      display: none;
      grid-template-columns: minmax(0, 1fr) minmax(300px, 0.86fr);
      gap: 18px;
      align-items: start;
    }}
    .panel.active {{
      display: grid;
    }}
    .section {{
      border: 1px solid var(--line);
      background: var(--panel);
      padding: 14px;
      display: grid;
      gap: 12px;
    }}
    .room-shell {{
      border: 1px solid var(--line);
      background: var(--panel);
      display: grid;
      gap: 12px;
      margin: 18px 0;
      padding: 14px;
    }}
    .room-header {{
      display: flex;
      align-items: start;
      justify-content: space-between;
      gap: 12px;
    }}
    .room-state {{
      display: flex;
      align-items: center;
      gap: 8px;
      white-space: nowrap;
      flex: 0 0 auto;
    }}
    .feedback-icon {{
      width: 24px;
      height: 24px;
      background-image: var(--room-feedback);
      background-repeat: no-repeat;
      background-size: auto 24px;
      image-rendering: pixelated;
      flex: 0 0 auto;
    }}
    .feedback-icon[data-icon="move_hint"] {{ background-position: 0 0; }}
    .feedback-icon[data-icon="interact_ready"] {{ background-position: -24px 0; }}
    .feedback-icon[data-icon="repair_failed"] {{ background-position: -48px 0; }}
    .feedback-icon[data-icon="sealed_check_ready"] {{ background-position: -72px 0; }}
    .feedback-icon[data-icon="route_open"] {{ background-position: -96px 0; }}
    .retry-panel {{
      display: none;
      gap: 8px;
      align-items: center;
      border: 1px solid rgba(239, 71, 111, 0.65);
      background: rgba(239, 71, 111, 0.08);
      padding: 8px 10px;
      color: var(--muted);
      font: 0.88rem/1.25 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    }}
    .room-shell[data-room-state="diagnostic_failed"] .retry-panel {{
      display: flex;
    }}
    .retry-icon {{
      width: 24px;
      height: 24px;
      background-image: var(--room-retry);
      background-repeat: no-repeat;
      background-size: auto 24px;
      image-rendering: pixelated;
      flex: 0 0 auto;
    }}
    .retry-icon[data-retry-icon="blocked_return"] {{ background-position: 0 0; }}
    .retry-icon[data-retry-icon="retry_prompt"] {{ background-position: -24px 0; }}
    .retry-icon[data-retry-icon="diagnostic_scratch"] {{ background-position: -48px 0; }}
    .retry-icon[data-retry-icon="visible_spill"] {{ background-position: -72px 0; }}
    .retry-icon[data-retry-icon="sealed_misread"] {{ background-position: -96px 0; }}
    .retry-icon[data-retry-icon="route_confirmed"] {{ background-position: -120px 0; }}
    .room-stage {{
      position: relative;
      min-height: 300px;
      border: 1px solid var(--line);
      background:
        linear-gradient(rgba(56, 189, 248, 0.08) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56, 189, 248, 0.08) 1px, transparent 1px),
        linear-gradient(#172231, #0c121a);
      background-size: 48px 48px, 48px 48px, auto;
      overflow: hidden;
    }}
    .room-stage::after {{
      content: "";
      position: absolute;
      inset: auto 0 0;
      height: 58px;
      background: rgba(11, 16, 23, 0.56);
      border-top: 1px solid rgba(248, 250, 252, 0.08);
      pointer-events: none;
    }}
    .room-blocker {{
      position: absolute;
      width: 48px;
      height: 48px;
      transform: translate(calc(var(--x) * 48px), calc(var(--y) * 48px));
      border: 1px solid rgba(248, 193, 74, 0.28);
      background:
        linear-gradient(135deg, rgba(248, 193, 74, 0.2) 25%, transparent 25%),
        linear-gradient(225deg, rgba(248, 193, 74, 0.2) 25%, transparent 25%),
        rgba(11, 16, 23, 0.42);
      background-size: 12px 12px;
      image-rendering: pixelated;
      z-index: 1;
    }}
    .room-shell[data-room-state="cleared_intake"] .room-blocker[data-route-blocker] {{
      display: none;
    }}
    .room-actor {{
      position: absolute;
      width: 48px;
      height: 48px;
      image-rendering: pixelated;
      transform: translate(calc(var(--x) * 48px), calc(var(--y) * 48px));
      transition: transform 120ms ease-out;
      z-index: 2;
    }}
    .player-sprite {{
      border: 2px solid var(--cyan);
      background-color: #203246;
      background-image: var(--room-sheet);
      background-repeat: no-repeat;
      background-size: auto 48px;
      background-position: -240px 0;
      box-shadow: inset 0 -8px 0 rgba(56, 189, 248, 0.12);
    }}
    .room-sprite {{
      width: 72px;
      height: 72px;
      object-fit: contain;
      filter: drop-shadow(0 8px 0 rgba(0, 0, 0, 0.25));
    }}
    .room-gate {{
      width: 88px;
      height: 88px;
    }}
    .room-shell[data-room-state="cleared_intake"] .room-gate {{
      opacity: 0.48;
      filter: drop-shadow(0 8px 0 rgba(0, 0, 0, 0.25)) saturate(0.65);
    }}
    .room-marker {{
      position: absolute;
      display: grid;
      grid-template-columns: 24px minmax(0, 1fr);
      gap: 6px;
      align-items: center;
      min-width: 132px;
      transform: translate(calc(var(--x) * 48px), calc((var(--y) * 48px) + 56px));
      z-index: 3;
      color: var(--text);
      background: rgba(11, 16, 23, 0.78);
      border: 1px solid var(--line);
      padding: 6px 8px;
      font: 0.82rem/1.2 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    }}
    .room-spark {{
      width: 24px;
      height: 24px;
      background-image: var(--room-sheet);
      background-repeat: no-repeat;
      background-size: auto 24px;
      background-position: -168px 0;
      image-rendering: pixelated;
    }}
    .room-controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}
    .move-pad {{
      display: grid;
      grid-template-columns: repeat(3, 40px);
      grid-template-rows: repeat(2, 40px);
      gap: 6px;
    }}
    .move-pad .action {{
      min-height: 40px;
      padding: 0;
      display: grid;
      place-items: center;
    }}
    .move-up {{ grid-column: 2; }}
    .move-left {{ grid-column: 1; grid-row: 2; }}
    .move-down {{ grid-column: 2; grid-row: 2; }}
    .move-right {{ grid-column: 3; grid-row: 2; }}
    .room-log {{
      min-height: 42px;
      border: 1px solid var(--line);
      background: var(--ink);
      color: var(--muted);
      padding: 8px 10px;
      font: 0.9rem/1.35 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      overflow-wrap: anywhere;
      flex: 1 1 260px;
    }}
    .smoke-report {{
      display: none;
      gap: 8px;
      border: 1px solid var(--line);
      background: var(--ink);
      color: var(--muted);
      padding: 8px 10px;
      font: 0.82rem/1.35 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      overflow-wrap: anywhere;
    }}
    .smoke-report[data-status="pass"] {{
      display: grid;
      border-color: var(--green);
    }}
    .smoke-report[data-status="fail"] {{
      display: grid;
      border-color: var(--rose);
    }}
    .smoke-summary, .smoke-row {{
      display: grid;
      grid-template-columns: 24px minmax(0, 1fr);
      gap: 8px;
      align-items: center;
    }}
    .smoke-summary {{
      color: var(--text);
      font-weight: 700;
    }}
    .smoke-evidence {{
      display: grid;
      gap: 4px;
      margin: 0;
      padding: 8px;
      border: 1px solid var(--line);
      background: rgba(12, 18, 26, 0.72);
    }}
    .smoke-evidence-row {{
      display: grid;
      grid-template-columns: minmax(120px, 0.34fr) minmax(0, 0.66fr);
      gap: 8px;
      min-height: 28px;
      align-items: start;
    }}
    .smoke-evidence-row dt {{
      color: var(--text);
      font-weight: 700;
    }}
    .smoke-evidence-row dd {{
      margin: 0;
    }}
    .smoke-copy {{
      width: 100%;
      min-height: 132px;
      border: 1px solid var(--line);
      background: rgba(12, 18, 26, 0.72);
      color: var(--muted);
      padding: 8px;
      font: inherit;
      resize: vertical;
    }}
    .smoke-list {{
      display: grid;
      gap: 6px;
      margin: 0;
      padding: 0;
      list-style: none;
    }}
    .smoke-row {{
      min-height: 28px;
    }}
    .smoke-row[data-passed="true"] {{
      color: var(--green);
    }}
    .smoke-row[data-passed="false"], .smoke-error {{
      color: var(--rose);
    }}
    .smoke-icon {{
      width: 24px;
      height: 24px;
      background-image: var(--smoke-icons);
      background-repeat: no-repeat;
      background-size: auto 24px;
      image-rendering: pixelated;
      flex: 0 0 auto;
    }}
    .smoke-icon[data-smoke-icon="keyboard_move"] {{ background-position: 0 0; }}
    .smoke-icon[data-smoke-icon="click_interact"] {{ background-position: -24px 0; }}
    .smoke-icon[data-smoke-icon="blocked_collision"] {{ background-position: -48px 0; }}
    .smoke-icon[data-smoke-icon="retry_return"] {{ background-position: -72px 0; }}
    .smoke-icon[data-smoke-icon="route_open_pass"] {{ background-position: -96px 0; }}
    .smoke-icon[data-smoke-icon="smoke_fail"] {{ background-position: -120px 0; }}
    .room-hint {{
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font: 0.88rem/1.25 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      flex: 1 1 220px;
      min-width: 0;
      overflow-wrap: anywhere;
    }}
    .encounter-title {{
      display: flex;
      gap: 10px;
      align-items: center;
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
    .prompt, .muted {{
      color: var(--muted);
      overflow-wrap: anywhere;
    }}
    .command {{
      display: block;
      margin-top: 6px;
      padding: 8px 10px;
      background: var(--ink);
      border: 1px solid var(--line);
      color: var(--green);
      font: 0.9rem/1.35 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      overflow-wrap: anywhere;
    }}
    .cert {{
      display: grid;
      grid-template-columns: 40px minmax(0, 1fr);
      gap: 10px;
      align-items: center;
      border-left: 5px solid var(--gold);
      padding: 10px;
      background: var(--surface);
    }}
    .slice {{
      border: 1px solid var(--line);
      background: #111923;
      display: grid;
      gap: 12px;
      padding: 12px;
    }}
    .slice[data-state="cleared"] {{
      border-color: var(--green);
    }}
    .slice[data-state="jammed"] {{
      border-color: var(--rose);
    }}
    .scene {{
      min-height: 170px;
      display: grid;
      grid-template-columns: minmax(120px, 0.8fr) minmax(0, 1.2fr) minmax(120px, 0.8fr);
      gap: 12px;
      align-items: end;
      background: linear-gradient(#172231, #0c121a);
      border: 1px solid var(--line);
      padding: 14px;
      overflow: hidden;
    }}
    .sprite {{
      width: min(96px, 100%);
      image-rendering: pixelated;
      justify-self: center;
      filter: drop-shadow(0 10px 0 rgba(0, 0, 0, 0.25));
    }}
    .scene-strip {{
      width: min(384px, 100%);
      image-rendering: pixelated;
      justify-self: center;
      background: var(--ink);
      border: 1px solid var(--line);
      padding: 6px;
    }}
    .token-row {{
      display: grid;
      grid-template-columns: repeat(4, minmax(44px, 1fr));
      gap: 8px;
      align-self: center;
    }}
    .rune {{
      min-height: 54px;
      border: 2px solid var(--line);
      background: #253144;
      color: var(--text);
      cursor: pointer;
      font: 700 1.15rem/1 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    }}
    .rune[aria-pressed="true"] {{
      border-color: var(--gold);
      box-shadow: inset 0 0 0 2px var(--gold);
    }}
    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .slice-status {{
      min-height: 38px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      border: 1px solid var(--line);
      background: var(--ink);
      padding: 8px 10px;
      color: var(--muted);
    }}
    .status-chip {{
      color: var(--gold);
      font-weight: 700;
      white-space: nowrap;
    }}
    .inspection-marks {{
      min-height: 36px;
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
      color: var(--muted);
    }}
    .inspection-mark {{
      border: 1px solid var(--line);
      background: var(--surface);
      min-height: 36px;
      display: grid;
      place-items: center;
      padding: 6px;
      text-align: center;
      font: 0.82rem/1.2 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      overflow-wrap: anywhere;
    }}
    .inspection-mark[data-ok="true"] {{
      border-color: var(--green);
      color: var(--green);
    }}
    .inspection-mark[data-ok="false"] {{
      border-color: var(--rose);
      color: var(--rose);
    }}
    .action {{
      border: 1px solid var(--line);
      background: var(--surface);
      color: var(--text);
      min-height: 40px;
      padding: 8px 12px;
      cursor: pointer;
      font: inherit;
    }}
    .action.primary {{
      border-color: var(--green);
      color: var(--green);
    }}
    .action.with-icon {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}
    .action-icon {{
      width: 24px;
      height: 24px;
      background-image: var(--sorting-actions);
      background-repeat: no-repeat;
      background-size: auto 24px;
      image-rendering: pixelated;
      flex: 0 0 auto;
    }}
    .action-icon[data-action-icon="select_rune"] {{ background-position: 0 0; }}
    .action-icon[data-action-icon="swap_runes"] {{ background-position: -24px 0; }}
    .action-icon[data-action-icon="check_order"] {{ background-position: -48px 0; }}
    .action-icon[data-action-icon="reset_spill"] {{ background-position: -72px 0; }}
    .action-icon[data-action-icon="sealed_check"] {{ background-position: -96px 0; }}
    .mira {{
      border-left: 5px solid var(--green);
      background: var(--surface);
      padding: 10px;
      color: var(--text);
    }}
    .repair-log {{
      min-height: 44px;
      color: var(--muted);
      font: 0.9rem/1.35 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      overflow-wrap: anywhere;
    }}
    .cert-row {{
      display: flex;
      gap: 8px;
      align-items: center;
      color: var(--muted);
      font: 0.88rem/1.25 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    }}
    .trace {{
      display: grid;
      gap: 8px;
    }}
    .event {{
      min-height: 52px;
      display: grid;
      grid-template-columns: 32px minmax(0, 1fr);
      gap: 10px;
      align-items: center;
      border: 1px solid var(--line);
      border-left: 5px solid var(--cyan);
      background: var(--surface);
      padding: 9px 10px;
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
    .label {{
      font-weight: 650;
      overflow-wrap: anywhere;
    }}
    .payload {{
      color: var(--muted);
      font: 0.82rem/1.35 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      overflow-wrap: anywhere;
    }}
    @media (max-width: 760px) {{
      main {{
        width: min(100vw - 20px, 1120px);
        padding-top: 14px;
      }}
      .topbar {{
        display: grid;
      }}
      .room-header {{
        display: grid;
      }}
      .room-state {{
        justify-content: start;
        white-space: normal;
      }}
      .room-stage {{
        min-height: 288px;
      }}
      .status {{
        white-space: normal;
      }}
      .panel.active {{
        display: grid;
        grid-template-columns: 1fr;
      }}
      .scene {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main style="--room-feedback: url(&quot;{room_feedback_uri}&quot;); --room-retry: url(&quot;{room_retry_uri}&quot;); --smoke-icons: url(&quot;{smoke_icons_uri}&quot;)">
    <header class="topbar">
      <h1>Algorithimia</h1>
      <div class="status">Python prototype shell - code execution stays in the local CLI</div>
    </header>
    <section class="room-shell" data-queueworks-room data-room-state="jammed_intake" style="--room-sheet: url(&quot;{room_sheet_uri}&quot;)">
      <div class="room-header">
        <div>
          <h2>Tiny Queueworks Room</h2>
          <p class="muted">Move the Patchrunner to the Sorting Slime and interact to repair the jammed intake.</p>
        </div>
        <div class="room-state">
          <span class="feedback-icon" data-room-state-icon data-icon="move_hint" aria-hidden="true"></span>
          <strong class="status-chip" data-room-status>ROUTE JAMMED</strong>
        </div>
      </div>
      <div class="room-stage" aria-label="Explorable Queueworks room">
        <div class="room-blocker" data-blocked-tile="ledger stack" style="--x: 3; --y: 1" aria-label="Blocked ledger stack tile"></div>
        <div class="room-blocker" data-blocked-tile="jammed gate base" data-route-blocker style="--x: 8; --y: 4" aria-label="Blocked jammed gate tile"></div>
        <div class="room-actor player-sprite" data-player style="--x: 1; --y: 4" aria-label="Patchrunner player sprite"></div>
        <img class="room-actor room-sprite room-gate" data-room-gate src="{queue_gate_uri}" alt="Queueworks intake gate" style="--x: 8; --y: 3">
        <img class="room-actor room-sprite" data-room-slime src="{sorting_slime_uri}" alt="Interactable Sorting Slime" style="--x: 5; --y: 3">
        <div class="room-marker" style="--x: 5; --y: 3"><span class="room-spark" aria-hidden="true"></span><span>Sorting Slime</span></div>
      </div>
      <div class="retry-panel" data-room-retry-panel>
        <span class="retry-icon" data-retry-icon="blocked_return" aria-hidden="true"></span>
        <span class="retry-icon" data-retry-icon="diagnostic_scratch" aria-hidden="true"></span>
        <span class="retry-icon" data-retry-icon="visible_spill" aria-hidden="true"></span>
        <span class="retry-icon" data-retry-icon="retry_prompt" aria-hidden="true"></span>
        <span>one rune is still out of order - retry the visible spill</span>
      </div>
      <div class="room-controls" aria-label="Queueworks room controls">
        <div class="move-pad" aria-label="Move Patchrunner">
          <button class="action move-up" type="button" data-move="up" aria-label="Move up">Up</button>
          <button class="action move-left" type="button" data-move="left" aria-label="Move left">Left</button>
          <button class="action move-down" type="button" data-move="down" aria-label="Move down">Down</button>
          <button class="action move-right" type="button" data-move="right" aria-label="Move right">Right</button>
        </div>
        <button class="action primary" type="button" data-room-interact disabled>Interact</button>
        <div class="room-hint"><span class="feedback-icon" data-icon="move_hint" aria-hidden="true"></span><span data-room-hint>move close, then test the repair</span></div>
        <div class="room-log" data-room-log>Use arrow keys, WASD, or the buttons to reach the Sorting Slime.</div>
      </div>
      <div class="smoke-report" data-smoke-report aria-live="polite"></div>
    </section>
    <nav class="tabs" role="tablist" aria-label="Encounters">
{tabs}
    </nav>
{panels}
  </main>
  <script>
    const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
    const panels = Array.from(document.querySelectorAll('[role="tabpanel"]'));
    function selectTab(tab) {{
      tabs.forEach((candidate) => candidate.setAttribute('aria-selected', String(candidate === tab)));
      panels.forEach((panel) => panel.classList.toggle('active', panel.id === tab.getAttribute('aria-controls')));
    }}
    tabs.forEach((tab) => tab.addEventListener('click', () => selectTab(tab)));

    const room = document.querySelector('[data-queueworks-room]');
    if (room) {{
      const player = room.querySelector('[data-player]');
      const interact = room.querySelector('[data-room-interact]');
      const roomLog = room.querySelector('[data-room-log]');
      const roomStatus = room.querySelector('[data-room-status]');
      const roomStateIcon = room.querySelector('[data-room-state-icon]');
      const roomHint = room.querySelector('[data-room-hint]');
      const slime = {{ x: 5, y: 3 }};
      const bounds = {{ width: 10, height: 6 }};
      const blockedTiles = [
        {{ x: slime.x, y: slime.y, label: 'Sorting Slime' }},
        {{ x: 8, y: 3, label: 'jammed intake gate', opensWhenClear: true }},
        {{ x: 8, y: 4, label: 'jammed gate base', opensWhenClear: true }},
        {{ x: 3, y: 1, label: 'ledger stack' }},
      ];
      let playerPosition = {{ x: 1, y: 4 }};
      let roomState = 'jammed_intake';

      function isNearSlime() {{
        return Math.abs(playerPosition.x - slime.x) + Math.abs(playerPosition.y - slime.y) <= 1;
      }}

      function blockedTileAt(position) {{
        return blockedTiles.find((tile) => {{
          if (roomState === 'cleared_intake' && tile.opensWhenClear) return false;
          return tile.x === position.x && tile.y === position.y;
        }});
      }}

      function renderRoom() {{
        player.style.setProperty('--x', String(playerPosition.x));
        player.style.setProperty('--y', String(playerPosition.y));
        interact.disabled = !isNearSlime() || roomState === 'cleared_intake';
        room.dataset.roomState = roomState;
        if (roomState === 'cleared_intake') {{
          roomStatus.textContent = 'ROUTE OPEN';
          roomStateIcon.dataset.icon = 'route_open';
          roomHint.textContent = 'Route clear. The stair will let you through.';
          interact.textContent = 'Repaired';
        }} else if (roomState === 'diagnostic_failed') {{
          roomStatus.textContent = 'RETRY REPAIR';
          roomStateIcon.dataset.icon = 'repair_failed';
          roomHint.textContent = 'One rune is still out of order. Try the repair again?';
          interact.textContent = 'Retry repair';
        }} else if (roomState === 'sealed_check') {{
          roomStatus.textContent = 'SEALED CHECK';
          roomStateIcon.dataset.icon = 'sealed_check_ready';
          roomHint.textContent = 'The visible spill held, but the Archive did not trust the repair yet.';
          interact.textContent = 'Retry repair';
        }} else {{
          roomStatus.textContent = isNearSlime() ? 'SLIME READY' : 'ROUTE JAMMED';
          roomStateIcon.dataset.icon = isNearSlime() ? 'interact_ready' : 'move_hint';
          roomHint.textContent = isNearSlime()
            ? 'Sort the runes and test the repair?'
            : 'move close, then test the repair';
          interact.textContent = 'Interact';
        }}
      }}

      function movePlayer(dx, dy) {{
        const nextPosition = {{
          x: Math.max(0, Math.min(bounds.width - 1, playerPosition.x + dx)),
          y: Math.max(0, Math.min(bounds.height - 1, playerPosition.y + dy)),
        }};
        const blocker = blockedTileAt(nextPosition);
        if (blocker) {{
          const blockCue = blocker.opensWhenClear
            ? 'The gate holds. The slime still owns this route.'
            : `Blocked by ${{blocker.label}}. Move beside it and interact from there.`;
          roomLog.textContent = blockCue;
          renderRoom();
          return;
        }}
        playerPosition = nextPosition;
        if (roomState === 'diagnostic_failed' && !isNearSlime()) {{
          roomLog.textContent = 'The stair is still jammed. Return to the slime and retry the visible spill.';
        }} else {{
          roomLog.textContent = isNearSlime()
            ? 'The slime is holding the intake shut. Sort the runes and test the repair?'
            : 'Queueworks floor clear. Move next to the Sorting Slime.';
        }}
        renderRoom();
      }}

      room.querySelectorAll('[data-move]').forEach((button) => {{
        button.addEventListener('click', () => {{
          const direction = button.dataset.move;
          if (direction === 'up') movePlayer(0, -1);
          if (direction === 'down') movePlayer(0, 1);
          if (direction === 'left') movePlayer(-1, 0);
          if (direction === 'right') movePlayer(1, 0);
        }});
      }});

      document.addEventListener('keydown', (event) => {{
        const keyMap = {{
          ArrowUp: [0, -1],
          w: [0, -1],
          W: [0, -1],
          ArrowDown: [0, 1],
          s: [0, 1],
          S: [0, 1],
          ArrowLeft: [-1, 0],
          a: [-1, 0],
          A: [-1, 0],
          ArrowRight: [1, 0],
          d: [1, 0],
          D: [1, 0],
        }};
        const delta = keyMap[event.key];
        if (!delta) return;
        event.preventDefault();
        movePlayer(delta[0], delta[1]);
      }});

      interact.addEventListener('click', () => {{
        if (!isNearSlime()) return;
        if (roomState === 'cleared_intake') {{
          roomLog.textContent = 'Route clear. The stair will let you through.';
          renderRoom();
          return;
        }}
        roomState = 'repair_in_progress';
        selectTab(document.querySelector('#tab-sorting_slime'));
        document.querySelector('#panel-sorting_slime').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        roomLog.textContent = 'Encounter opened: sort the visible spill, check it, then return to the room.';
        renderRoom();
      }});

      window.algorithimiaRoom = {{
        markSortingSlimeCleared() {{
          roomState = 'cleared_intake';
          roomLog.textContent = 'Route clear. The stair will let you through.';
          renderRoom();
          room.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }},
        markSortingSlimeFailed() {{
          roomState = 'diagnostic_failed';
          roomLog.textContent = 'One rune is still out of order. Try the repair again?';
          renderRoom();
          room.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }},
      }};

      renderRoom();
    }}

    const sortingGame = document.querySelector('[data-sorting-slime-playfield]');
    if (sortingGame) {{
      const initialValues = sortingGame.dataset.values.split(',').map(Number);
      const buttons = Array.from(sortingGame.querySelectorAll('[data-rune-index]'));
      const feedback = sortingGame.querySelector('[data-feedback]');
      const repairLog = sortingGame.querySelector('[data-repair-log]');
      const status = sortingGame.querySelector('[data-slice-status]');
      const statusChip = sortingGame.querySelector('[data-status-chip]');
      const inspectionMarks = Array.from(sortingGame.querySelectorAll('[data-inspection-mark]'));
      let values = initialValues.slice();
      let selectedIndex = null;
      let swaps = 0;

      function isOrdered() {{
        return values.every((value, index) => index === 0 || values[index - 1] <= value);
      }}

      function renderRunes() {{
        buttons.forEach((button, index) => {{
          button.textContent = String(values[index]);
          button.setAttribute('aria-pressed', String(index === selectedIndex));
        }});
      }}

      function setFeedback(message) {{
        feedback.textContent = message;
      }}

      function renderInspectionMarks() {{
        inspectionMarks.forEach((mark, index) => {{
          const left = values[index];
          const right = values[index + 1];
          const ok = left <= right;
          mark.textContent = `${{left}} <= ${{right}}`;
          mark.dataset.ok = String(ok);
        }});
      }}

      function setSliceState(state) {{
        sortingGame.dataset.state = state;
        if (state === 'cleared') {{
          status.textContent = 'Route open: visible spill is ordered.';
          statusChip.textContent = 'CLEARED';
        }} else if (state === 'jammed') {{
          status.textContent = 'Route sealed: at least one adjacent rune is out of order.';
          statusChip.textContent = 'JAMMED';
        }} else {{
          status.textContent = 'Route sealed: inspect and swap the loose runes.';
          statusChip.textContent = 'INSPECT';
        }}
      }}

      buttons.forEach((button, index) => {{
        button.addEventListener('click', () => {{
          if (selectedIndex === null) {{
            selectedIndex = index;
            repairLog.textContent = `selected rune ${{values[index]}}`;
          }} else if (selectedIndex === index) {{
            selectedIndex = null;
            repairLog.textContent = 'selection cleared';
          }} else {{
            const first = values[selectedIndex];
            const second = values[index];
            [values[selectedIndex], values[index]] = [values[index], values[selectedIndex]];
            swaps += 1;
            repairLog.textContent = `swap ${{first}} with ${{second}}`;
            selectedIndex = null;
            renderInspectionMarks();
            setSliceState(isOrdered() ? 'cleared' : 'jammed');
            setFeedback(isOrdered() ? 'Mira: Good. It works when the mess changes. That is a repair.' : 'Mira: Keep inspecting. The intake still reads out of order.');
          }}
          renderRunes();
        }});
      }});

      sortingGame.querySelector('[data-check-order]').addEventListener('click', () => {{
        renderInspectionMarks();
        setSliceState(isOrdered() ? 'cleared' : 'jammed');
        setFeedback(isOrdered() ? 'Mira: Good. It works when the mess changes. That is a repair.' : 'Mira: The gate still sees a larger rune before a smaller one.');
        repairLog.textContent = `checked after ${{swaps}} swap${{swaps === 1 ? '' : 's'}}`;
      }});

      sortingGame.querySelector('[data-reset-order]').addEventListener('click', () => {{
        values = initialValues.slice();
        selectedIndex = null;
        swaps = 0;
        setFeedback('Mira: Public spill loaded. Put the runes in smallest-to-largest order.');
        repairLog.textContent = 'spill reset: 5, 1, 4, 2';
        setSliceState('inspect');
        renderInspectionMarks();
        renderRunes();
      }});

      sortingGame.querySelector('[data-return-room]').addEventListener('click', () => {{
        if (window.algorithimiaRoom && isOrdered()) {{
          window.algorithimiaRoom.markSortingSlimeCleared();
        }} else if (window.algorithimiaRoom) {{
          window.algorithimiaRoom.markSortingSlimeFailed();
          setFeedback('Mira: The stair is still jammed. Try the visible spill again before trusting the route.');
        }} else {{
          setFeedback('Mira: Check the order before you reopen the intake.');
        }}
      }});

      setSliceState('inspect');
      renderInspectionMarks();
      renderRunes();
    }}

    function runGameShellSmoke() {{
      const report = document.querySelector('[data-smoke-report]');
      if (!report) return;
      const checks = [];
      let firstViewportSummary = 'not captured';
      function record(name, passed, icon = 'click_interact') {{
        checks.push({{ name, passed, icon }});
        if (!passed) throw new Error(name);
      }}
      function visibleInViewport(selector) {{
        const element = document.querySelector(selector);
        if (!element) return false;
        const rect = element.getBoundingClientRect();
        const styles = getComputedStyle(element);
        return (
          styles.display !== 'none' &&
          styles.visibility !== 'hidden' &&
          Number(styles.opacity || 1) > 0 &&
          rect.width >= 16 &&
          rect.height >= 16 &&
          rect.bottom > 0 &&
          rect.right > 0 &&
          rect.top < window.innerHeight &&
          rect.left < window.innerWidth
        );
      }}
      function captureFirstViewport() {{
        window.scrollTo(0, 0);
        const surfaces = [
          ['room', '[data-queueworks-room]'],
          ['status', '[data-room-status]'],
          ['hint', '[data-room-hint]'],
          ['slime', '[data-room-object="sorting_slime"]'],
          ['interact', '[data-room-interact]'],
        ];
        const visible = surfaces
          .filter((surface) => visibleInViewport(surface[1]))
          .map((surface) => surface[0]);
        firstViewportSummary = visible.length ? visible.join(', ') : 'none';
        record('first viewport shows room shell before smoke scroll', visible.includes('room'), 'blocked_collision');
        record('first viewport shows room status before smoke scroll', visible.includes('status'), 'blocked_collision');
        record('first viewport shows room hint before smoke scroll', visible.includes('hint'), 'keyboard_move');
      }}
      function click(selector) {{
        const element = document.querySelector(selector);
        record(`found ${{selector}}`, Boolean(element), selector.includes('move') ? 'keyboard_move' : 'click_interact');
        element.click();
        return element;
      }}
      function playerGridPosition() {{
        const player = document.querySelector('[data-player]');
        record('found [data-player]', Boolean(player), 'keyboard_move');
        return {{
          x: player.style.getPropertyValue('--x'),
          y: player.style.getPropertyValue('--y'),
        }};
      }}
      function keyMove(key, expectedX, expectedY) {{
        const event = new KeyboardEvent('keydown', {{ key, bubbles: true, cancelable: true }});
        document.dispatchEvent(event);
        record(`keyboard ${{key}} handled`, event.defaultPrevented, 'keyboard_move');
        const position = playerGridPosition();
        record(`keyboard ${{key}} moved player to ${{expectedX}},${{expectedY}}`, position.x === String(expectedX) && position.y === String(expectedY), 'keyboard_move');
      }}
      function readable(selector, name, icon = 'click_interact') {{
        const element = document.querySelector(selector);
        record(`found ${{selector}}`, Boolean(element), icon);
        element.scrollIntoView({{ block: 'center', inline: 'nearest' }});
        const rect = element.getBoundingClientRect();
        const styles = getComputedStyle(element);
        const rendered = (
          styles.display !== 'none' &&
          styles.visibility !== 'hidden' &&
          Number(styles.opacity || 1) > 0 &&
          rect.width >= 16 &&
          rect.height >= 16 &&
          rect.bottom > 0 &&
          rect.right > 0 &&
          rect.top < window.innerHeight &&
          rect.left < window.innerWidth
        );
        record(name, rendered, icon);
        return element;
      }}
      function viewportStable(name, icon = 'blocked_collision') {{
        const width = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth);
        record(name, width <= window.innerWidth + 1, icon);
      }}
      function tapTargets(selector, name, icon = 'click_interact') {{
        const elements = Array.from(document.querySelectorAll(selector));
        record(`found tap targets ${{selector}}`, elements.length > 0, icon);
        const tooSmall = elements.filter((element) => {{
          const rect = element.getBoundingClientRect();
          return rect.width < 40 || rect.height < 40;
        }});
        record(name, tooSmall.length === 0, icon);
      }}
      function textFits(selector, name, icon = 'click_interact') {{
        const element = document.querySelector(selector);
        record(`found text surface ${{selector}}`, Boolean(element), icon);
        record(name, element.scrollWidth <= element.clientWidth + 1 && element.scrollHeight <= element.clientHeight + 1, icon);
      }}
      function reportRowsReadable(name, icon = 'route_open_pass') {{
        const rows = Array.from(document.querySelectorAll('[data-smoke-report] .smoke-row'));
        record('found smoke report rows', rows.length > 0, icon);
        const cramped = rows.filter((row) => row.getBoundingClientRect().height < 28);
        record(name, cramped.length === 0, icon);
      }}
      function viewportProfile() {{
        const width = window.innerWidth;
        const height = window.innerHeight;
        const pageWidth = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth);
        const pageHeight = Math.max(document.documentElement.scrollHeight, document.body.scrollHeight);
        const category = width <= 480 ? 'mobile/narrow' : width <= 760 ? 'narrow' : 'desktop';
        const orientation = width >= height ? 'landscape' : 'portrait';
        return {{
          category,
          orientation,
          viewport: `${{width}}x${{height}}`,
          page: `${{pageWidth}}x${{pageHeight}}`,
          capture: `${{category}} ${{orientation}}; page ${{pageWidth}}x${{pageHeight}}`,
        }};
      }}
      function smokeEvidence(status, error) {{
        const failed = checks.find((check) => !check.passed);
        const failureLabel = failed ? failed.name : String(error || 'unknown failure');
        const passed = status === 'pass';
        const profile = viewportProfile();
        return [
          {{ label: 'State tested', value: 'first viewport, blocked route, interact-ready slime, wrong-order retry, route clear, repaired interaction, smoke report' }},
          {{ label: 'Result', value: passed ? 'pass' : `fail with label: ${{failureLabel}}` }},
          {{ label: 'Control path', value: 'ArrowRight, WASD, on-screen movement, Interact, Return, rune swaps, Check order' }},
          {{ label: 'Viewport', value: profile.viewport }},
          {{ label: 'Viewport profile', value: profile.capture }},
          {{ label: 'Orientation', value: profile.orientation }},
          {{ label: 'Page size', value: profile.page }},
          {{ label: 'First viewport', value: firstViewportSummary }},
          {{ label: 'Capture quality', value: 'self-smoke generated; mark manual capture clear, cropped, or inconclusive during review' }},
          {{ label: 'Observed cause', value: passed ? 'self-smoke checks passed in this browser viewport' : failureLabel }},
          {{ label: 'Manual review', value: 'confirm first-viewport composition, blocked route, interact-ready slime, wrong-order retry, route clear, repaired interaction, and narrow/mobile readability' }},
          {{ label: 'Text/icon/collision agreement', value: passed ? 'cue text, smoke icons, blocked collision, and route clearing agreed' : 'review failed row against cue text, smoke icon, collision, or route state' }},
          {{ label: 'Likely owner', value: passed ? 'Agent 4 or Henry for live readability judgment' : 'Agent 3 if this is placement, timing, state pairing, button, or layout' }},
          {{ label: 'Next action', value: passed ? 'manual browser readability pass or same-room polish only' : 'fix the labeled same-room failure before new content' }},
        ];
      }}
      function smokeText(status, error) {{
        const evidence = smokeEvidence(status, error).map((item) => `${{item.label}}: ${{item.value}}`);
        return [
          `Game shell smoke: ${{status.toUpperCase()}}`,
          ...evidence,
          ...checks.map((check) => `${{check.passed ? 'PASS' : 'FAIL'}} ${{check.name}}`),
          ...(error ? [String(error)] : []),
        ].join('\\n');
      }}
      function renderSmokeReport(status, error) {{
        const summaryIcon = status === 'pass' ? 'route_open_pass' : 'smoke_fail';
        const evidenceText = smokeText(status, error);
        const failed = checks.find((check) => !check.passed);
        const failureLabel = failed ? failed.name : '';
        const profile = viewportProfile();
        report.dataset.status = status;
        report.dataset.smokeResult = status;
        report.dataset.smokeLabel = failureLabel;
        report.dataset.smokeViewport = profile.viewport;
        report.dataset.smokeViewportProfile = profile.category;
        report.dataset.smokePageSize = profile.page;
        report.dataset.smokeFirstViewport = firstViewportSummary;
        report.setAttribute('aria-label', evidenceText);
        report.replaceChildren();

        const summary = document.createElement('div');
        summary.className = 'smoke-summary';
        summary.innerHTML = `<span class="smoke-icon" data-smoke-icon="${{summaryIcon}}" aria-hidden="true"></span><span>Game shell smoke: ${{status.toUpperCase()}}</span>`;
        report.append(summary);

        const evidence = document.createElement('dl');
        evidence.className = 'smoke-evidence';
        evidence.setAttribute('aria-label', 'Browser evidence intake card');
        smokeEvidence(status, error).forEach((item) => {{
          const row = document.createElement('div');
          row.className = 'smoke-evidence-row';
          const term = document.createElement('dt');
          term.textContent = item.label;
          const detail = document.createElement('dd');
          detail.textContent = item.value;
          row.append(term, detail);
          evidence.append(row);
        }});
        report.append(evidence);

        const copy = document.createElement('textarea');
        copy.className = 'smoke-copy';
        copy.readOnly = true;
        copy.dataset.smokeCopy = 'evidence';
        copy.setAttribute('aria-label', 'Copyable browser evidence card');
        copy.value = evidenceText;
        report.append(copy);

        const list = document.createElement('ul');
        list.className = 'smoke-list';
        checks.forEach((check) => {{
          const row = document.createElement('li');
          row.className = 'smoke-row';
          row.dataset.passed = String(check.passed);
          const icon = check.passed ? check.icon : 'smoke_fail';
          row.innerHTML = `<span class="smoke-icon" data-smoke-icon="${{icon}}" aria-hidden="true"></span><span>${{check.passed ? 'PASS' : 'FAIL'}} ${{check.name}}</span>`;
          list.append(row);
        }});
        report.append(list);

        if (error) {{
          const errorRow = document.createElement('div');
          errorRow.className = 'smoke-error';
          errorRow.textContent = String(error);
          report.append(errorRow);
        }}
      }}

      try {{
        captureFirstViewport();
        readable('[data-room-status]', 'room status cue is visible before movement', 'blocked_collision');
        readable('[data-room-hint]', 'room hint cue is visible before movement', 'keyboard_move');
        viewportStable('initial room has no horizontal overflow', 'blocked_collision');
        tapTargets('[data-room-interact], [data-move], .tab', 'room controls meet 40px tap target', 'keyboard_move');
        textFits('[data-room-status]', 'room status text fits before movement', 'blocked_collision');
        keyMove('ArrowRight', 2, 4);
        keyMove('d', 3, 4);
        click('[data-move="right"]');
        click('[data-move="up"]');
        record('on-screen movement reaches interact range', document.querySelector('[data-room-interact]').disabled === false, 'keyboard_move');
        readable('[data-room-interact]', 'interact control is visible beside slime', 'click_interact');
        record('interact enabled beside slime', !document.querySelector('[data-room-interact]').disabled, 'click_interact');
        click('[data-room-interact]');
        readable('[data-check-order]', 'sorting action controls are visible after interact', 'click_interact');
        tapTargets('.rune, [data-check-order], [data-reset-order], [data-return-room]', 'sorting controls meet 40px tap target', 'click_interact');
        viewportStable('sorting panel has no horizontal overflow', 'click_interact');
        record('sorting panel active after interact', document.querySelector('#panel-sorting_slime').classList.contains('active'), 'click_interact');
        click('[data-return-room]');
        record('wrong return keeps intake jammed', document.querySelector('[data-queueworks-room]').dataset.roomState === 'diagnostic_failed', 'retry_return');
        readable('[data-room-retry-panel]', 'retry panel is visible after wrong return', 'retry_return');
        readable('[data-room-hint]', 'retry hint cue is visible after wrong return', 'retry_return');
        textFits('[data-room-hint]', 'retry hint text fits after wrong return', 'retry_return');
        viewportStable('retry room has no horizontal overflow', 'retry_return');
        click('[data-rune-index="0"]');
        click('[data-rune-index="1"]');
        click('[data-rune-index="1"]');
        click('[data-rune-index="3"]');
        click('[data-check-order]');
        record('visible spill clears after swaps', document.querySelector('[data-sorting-slime-playfield]').dataset.state === 'cleared', 'route_open_pass');
        click('[data-return-room]');
        record('success return opens route', document.querySelector('[data-queueworks-room]').dataset.roomState === 'cleared_intake', 'route_open_pass');
        record('route status text updates', document.querySelector('[data-room-status]').textContent === 'ROUTE OPEN', 'route_open_pass');
        readable('[data-room-status]', 'route-open status cue is visible after success', 'route_open_pass');
        readable('[data-room-hint]', 'route-open hint cue is visible after success', 'route_open_pass');
        textFits('[data-room-hint]', 'route-open hint text fits after success', 'route_open_pass');
        viewportStable('cleared room has no horizontal overflow', 'route_open_pass');
        record('interact disabled after repair', document.querySelector('[data-room-interact]').disabled, 'route_open_pass');
        click('[data-room-interact]');
        record('repaired interaction leaves route open', document.querySelector('[data-queueworks-room]').dataset.roomState === 'cleared_intake', 'route_open_pass');
        click('[data-move="down"]');
        click('[data-move="right"]');
        click('[data-move="right"]');
        click('[data-move="right"]');
        click('[data-move="right"]');
        record('cleared route blocker becomes passable', playerGridPosition().x === '8', 'blocked_collision');
        renderSmokeReport('pass');
        readable('[data-smoke-report]', 'smoke report is visible after completion', 'route_open_pass');
        reportRowsReadable('smoke report rows keep readable height', 'route_open_pass');
        viewportStable('smoke report has no horizontal overflow', 'route_open_pass');
        renderSmokeReport('pass');
      }} catch (error) {{
        renderSmokeReport('fail', error);
        throw error;
      }}
    }}

    if (location.search.includes('smoke=1') || location.hash === '#smoke') {{
      window.addEventListener('load', runGameShellSmoke);
    }}
  </script>
</body>
</html>
"""


def _tab_button(encounter: Encounter, index: int) -> str:
    selected = "true" if index == 0 else "false"
    return (
        f'      <button class="tab" id="tab-{html.escape(encounter.slug)}" role="tab" '
        f'aria-selected="{selected}" aria-controls="panel-{html.escape(encounter.slug)}">'
        f"{html.escape(encounter.title)}</button>"
    )


def _encounter_panel(
    encounter: Encounter,
    index: int,
    badge_sheet_uri: str,
    event_sheet_uri: str,
    certification_sheet_uri: str,
    sorting_slime_uri: str,
    queue_gate_uri: str,
    sorting_scene_uri: str,
    sorting_action_uri: str,
) -> str:
    active = " active" if index == 0 else ""
    badge_cell = BADGE_CELLS.get(encounter.slug, 0)
    trace_events = "\n".join(_event_row(event, event_sheet_uri) for event in encounter_trace_events(encounter))
    certification = _certification_block(encounter, certification_sheet_uri)
    encounter_flag = "" if encounter.slug == "sorting_slime" else f" --encounter {encounter.slug}"
    trace_path = "build\\game-trace.html" if encounter.slug == "sorting_slime" else f"build\\{encounter.slug}-trace.html"
    playable_slice = (
        _sorting_slime_playable_slice(sorting_slime_uri, queue_gate_uri, sorting_scene_uri, sorting_action_uri)
        if encounter.slug == "sorting_slime"
        else ""
    )

    return f"""    <section class="panel{active}" id="panel-{html.escape(encounter.slug)}" role="tabpanel" aria-labelledby="tab-{html.escape(encounter.slug)}">
      <div class="section">
        <div class="encounter-title">
          <span class="badge" aria-hidden="true" style="background-image: url(&quot;{badge_sheet_uri}&quot;); background-position: -{badge_cell * 32}px 0"></span>
          <div>
            <h2>{html.escape(encounter.title)}</h2>
            <p class="muted">{html.escape(encounter.slug)}</p>
          </div>
        </div>
        <p class="prompt">{html.escape(encounter.prompt)}</p>
{playable_slice}
{certification}
        <div>
          <h3>Run locally</h3>
          <code class="command">python -m algorithimia{html.escape(encounter_flag)}</code>
          <code class="command">python -m algorithimia{html.escape(encounter_flag)} --trace-html {html.escape(trace_path)}</code>
        </div>
      </div>
      <div class="section">
        <h3>Trace Preview</h3>
        <div class="trace" aria-label="{html.escape(encounter.title)} trace events">
{trace_events}
        </div>
      </div>
    </section>"""


def _sorting_slime_playable_slice(
    sorting_slime_uri: str,
    queue_gate_uri: str,
    sorting_scene_uri: str,
    sorting_action_uri: str,
) -> str:
    return f"""        <div class="slice" data-sorting-slime-playfield data-values="5,1,4,2" data-state="inspect" style="--sorting-actions: url(&quot;{sorting_action_uri}&quot;)">
          <h3>Blocked Queueworks Intake</h3>
          <img class="scene-strip" src="{sorting_scene_uri}" alt="Sorting Slime scene strip">
          <div class="scene" aria-label="Sorting Slime ordering scene">
            <img class="sprite" src="{queue_gate_uri}" alt="Jammed Queueworks intake gate">
            <div class="token-row" aria-label="Loose rune tokens">
              <button class="rune" type="button" data-rune-index="0" aria-pressed="false"></button>
              <button class="rune" type="button" data-rune-index="1" aria-pressed="false"></button>
              <button class="rune" type="button" data-rune-index="2" aria-pressed="false"></button>
              <button class="rune" type="button" data-rune-index="3" aria-pressed="false"></button>
            </div>
            <img class="sprite" src="{sorting_slime_uri}" alt="Sorting Slime">
          </div>
          <div class="slice-status">
            <span data-slice-status>Route sealed: inspect and swap the loose runes.</span>
            <strong class="status-chip" data-status-chip>INSPECT</strong>
          </div>
          <div class="inspection-marks" aria-label="Adjacent rune inspection marks">
            <div class="inspection-mark" data-inspection-mark></div>
            <div class="inspection-mark" data-inspection-mark></div>
            <div class="inspection-mark" data-inspection-mark></div>
          </div>
          <div class="controls" aria-label="Sorting Slime actions">
            <button class="action primary with-icon" type="button" data-check-order><span class="action-icon" data-action-icon="check_order" aria-hidden="true"></span><span>Check order</span></button>
            <button class="action with-icon" type="button" data-reset-order><span class="action-icon" data-action-icon="reset_spill" aria-hidden="true"></span><span>Reset spill</span></button>
            <button class="action" type="button" data-return-room>Return to room</button>
          </div>
          <div class="cert-row"><span class="action-icon" data-action-icon="sealed_check" aria-hidden="true"></span><span>sealed check stays hidden until the local Python adapter validates the repair</span></div>
          <p class="mira" data-feedback>Mira: Public spill loaded. Put the runes in smallest-to-largest order.</p>
          <div class="repair-log" data-repair-log>spill loaded: 5, 1, 4, 2</div>
        </div>"""


def _event_row(event: TraceEvent, sheet_uri: str) -> str:
    cell = EVENT_ICON_CELLS.get(event.kind, 0)
    payload = " ".join(f"{key}={value!r}" for key, value in event.payload.items())
    return f"""          <article class="event" data-kind="{html.escape(event.kind)}">
            <span class="icon" aria-hidden="true" style="background-image: url(&quot;{sheet_uri}&quot;); background-position: -{cell * 32}px 0"></span>
            <div>
              <div class="label">{html.escape(event.label)}</div>
              <div class="payload">{html.escape(payload)}</div>
            </div>
          </article>"""


def _certification_block(encounter: Encounter, sheet_uri: str) -> str:
    certification_count = len(encounter.certification_cases)
    if certification_count == 0:
        return ""

    return f"""        <div class="cert">
          <span class="icon" aria-hidden="true" style="background-image: url(&quot;{sheet_uri}&quot;); background-position: -32px 0"></span>
          <div>
            <strong>Sealed certification active</strong>
            <p class="muted">{len(encounter.cases)} public teaching cases and {certification_count} sealed checks. Hidden inputs stay sealed.</p>
          </div>
        </div>"""


def _svg_data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"
