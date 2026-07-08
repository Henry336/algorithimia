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
QUEUEWORKS_ROOM_SHEET = ASSET_DIR / "queueworks-room-sheet.svg"
QUEUEWORKS_ROOM_FEEDBACK_SHEET = ASSET_DIR / "queueworks-room-feedback.svg"
QUEUEWORKS_ROOM_RETRY_SHEET = ASSET_DIR / "queueworks-room-retry-strip.svg"

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
    room_sheet_uri = _svg_data_uri(QUEUEWORKS_ROOM_SHEET)
    room_feedback_uri = _svg_data_uri(QUEUEWORKS_ROOM_FEEDBACK_SHEET)
    room_retry_uri = _svg_data_uri(QUEUEWORKS_ROOM_RETRY_SHEET)
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
    .room-hint {{
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font: 0.88rem/1.25 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
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
  <main style="--room-feedback: url(&quot;{room_feedback_uri}&quot;); --room-retry: url(&quot;{room_retry_uri}&quot;)">
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
        <div class="room-hint"><span class="feedback-icon" data-icon="move_hint" aria-hidden="true"></span><span>move close, then test the repair</span></div>
        <div class="room-log" data-room-log>Use arrow keys, WASD, or the buttons to reach the Sorting Slime.</div>
      </div>
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
        interact.disabled = !isNearSlime();
        room.dataset.roomState = roomState;
        if (roomState === 'cleared_intake') {{
          roomStatus.textContent = 'ROUTE OPEN';
          roomStateIcon.dataset.icon = 'route_open';
        }} else if (roomState === 'diagnostic_failed') {{
          roomStatus.textContent = 'RETRY REPAIR';
          roomStateIcon.dataset.icon = 'repair_failed';
        }} else if (roomState === 'sealed_check') {{
          roomStatus.textContent = 'SEALED CHECK';
          roomStateIcon.dataset.icon = 'sealed_check_ready';
        }} else {{
          roomStatus.textContent = isNearSlime() ? 'SLIME READY' : 'ROUTE JAMMED';
          roomStateIcon.dataset.icon = isNearSlime() ? 'interact_ready' : 'move_hint';
        }}
      }}

      function movePlayer(dx, dy) {{
        const nextPosition = {{
          x: Math.max(0, Math.min(bounds.width - 1, playerPosition.x + dx)),
          y: Math.max(0, Math.min(bounds.height - 1, playerPosition.y + dy)),
        }};
        const blocker = blockedTileAt(nextPosition);
        if (blocker) {{
          roomLog.textContent = `Blocked by ${{blocker.label}}. Move beside it and interact from there.`;
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
        roomState = 'repair_in_progress';
        selectTab(document.querySelector('#tab-sorting_slime'));
        document.querySelector('#panel-sorting_slime').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        roomLog.textContent = 'Encounter opened: sort the visible spill, check it, then return to the room.';
        renderRoom();
      }});

      window.algorithimiaRoom = {{
        markSortingSlimeCleared() {{
          roomState = 'cleared_intake';
          roomLog.textContent = 'The route opens. The Patchrunner returns to the Queueworks room.';
          renderRoom();
          room.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }},
        markSortingSlimeFailed() {{
          roomState = 'diagnostic_failed';
          roomLog.textContent = 'The stair is still jammed. Try the visible spill again before trusting the route.';
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
) -> str:
    active = " active" if index == 0 else ""
    badge_cell = BADGE_CELLS.get(encounter.slug, 0)
    trace_events = "\n".join(_event_row(event, event_sheet_uri) for event in encounter_trace_events(encounter))
    certification = _certification_block(encounter, certification_sheet_uri)
    encounter_flag = "" if encounter.slug == "sorting_slime" else f" --encounter {encounter.slug}"
    trace_path = "build\\game-trace.html" if encounter.slug == "sorting_slime" else f"build\\{encounter.slug}-trace.html"
    playable_slice = (
        _sorting_slime_playable_slice(sorting_slime_uri, queue_gate_uri, sorting_scene_uri)
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
) -> str:
    return f"""        <div class="slice" data-sorting-slime-playfield data-values="5,1,4,2" data-state="inspect">
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
            <button class="action primary" type="button" data-check-order>Check order</button>
            <button class="action" type="button" data-reset-order>Reset spill</button>
            <button class="action" type="button" data-return-room>Return to room</button>
          </div>
          <div class="cert-row"><span class="feedback-icon" data-icon="sealed_check_ready" aria-hidden="true"></span><span>sealed check stays hidden until the local Python adapter validates the repair</span></div>
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
