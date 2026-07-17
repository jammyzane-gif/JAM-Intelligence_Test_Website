# JAM Weekly Network System — Design

Approved 14 Jul 2026. Unifies CLAUDE.md Workflows 2 (Gephi update), 3 (push viz to web) and 4 (sector page viz) into a single one-command **Workflow 6 — Weekly network update**.

## Goal

Regenerate the AI network from the up-to-date Event Log, build a first Economy network from the Monetary Event Log, and make both a repeatable one-command weekly workflow with per-sector archive galleries. Energy is pre-stubbed in config but disabled until enough events are logged.

## Decisions (user-confirmed)

| Topic | Decision |
|---|---|
| Master data | `data/Jam_Intelligence_Network_EventLog_Everyday_Update.xlsx` — user logs events into it directly; pipeline reads it fresh each run; file is git-ignored (local-only, never public) |
| Layout engine | Live Gephi + gephi-mcp REST API at `http://127.0.0.1:8080` (verified working); user launches Gephi before a run |
| Automation level | One-command run; preview → push origin → ask → push prod gates stay manual |
| Trigger | User says "update the networks" to Claude, or runs `python3 gephi/scripts/jam_network_pipeline.py` |
| Archive UI | Dedicated gallery page per sector: edition cards (thumbnail, date, events · nodes, Current badge), newest first; card opens full 4K PNG |
| AI sector page | Animated iframe (`ai_network_map.html`, data frozen 12 Jun) replaced by newest weekly PNG; decorative CSS background animation stays |
| Economy network home | New `eu_tech_economics.html` sector page on the AI-page pattern; Sector B card rewires to it |
| Data → page contract | `networks.js` manifest (mirror of articles.js): weekly runs rewrite the manifest + PNG files, never HTML |
| Energy later | Flip `enabled: True` in the pipeline's NETWORKS config + create its sector page; weekly runs then include it |

## Architecture

1. **Pipeline** `gephi/scripts/jam_network_pipeline.py` (stdlib-only): health-check Gephi → read workbook sheets (Event Log / Monetary Event Log) + Node Registry → validate (unknown nodes, bad weights/dates → warnings) → aggregate cumulative node/edge weights → build + style in Gephi (triangle seeding; ForceAtlas 2 Stronger Gravity ON 0.05, LinLog, scaling 0.1, prevent overlap; sizes 15–45; category palettes; #800020 edges; label wrap >15 chars + overlap fix) → export SVG → 4K PNG → 480px thumbnail (sips) → archive outgoing PNG → prepend edition to `networks.js`. Skips a network when no events are newer than its last edition.
2. **Manifest** `networks.js`: per network — name, sectorPage, archivePage, `editions[{date, file, thumb, events, nodes}]` newest-first.
3. **Pages**: AI + EU sector pages render newest PNG, "Last updated" caption and Past-editions button from the manifest; `network_archive_ai.html` / `network_archive_eu.html` render the edition grid from it.

## Backfill

`jam_ai_landscape_network_4k.png` = AI edition #1, dated 12 Jun 2026.

## Out of scope

Energy network build-out (config stub only), automated unattended scheduling (launchd), updating the animated `ai_network_map.html` data.
