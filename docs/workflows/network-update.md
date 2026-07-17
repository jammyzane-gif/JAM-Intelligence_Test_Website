# Workflow 6 — Weekly Network Update

Trigger phrase: **"update the networks"** (absorbs old Workflows 2 and 3).

## What it does

One command rebuilds every enabled network visualisation from the master Event
Log workbook, in the locked house style, and updates the website + archives —
touching zero HTML.

## Prerequisites

- **Gephi is running** with the gephi-mcp plugin (REST API on
  `http://127.0.0.1:8080` — the pipeline checks `/health` and aborts with a
  clear message if it's down).
- The master workbook is up to date:
  `data/Jam_Intelligence_Network_EventLog_Everyday_Update.xlsx`
  (user logs events directly into it; sheets: `Event Log` = AI,
  `Monetary Event Log` = Economy, `Energy Event Log` = Energy,
  plus `Node Registry` and per-network Legends).
  The `data/` folder is git-ignored — this file never leaves the Mac.

## Steps

1. `python3 gephi/scripts/jam_network_pipeline.py`
   (no args = all enabled networks; or name them: `… ai economy`;
   `--force` rebuilds even when no new events are logged)
2. Review the console output: validation warnings (unknown nodes, bad
   weights/dates), event/node counts, label-overlap convergence.
3. Eyeball the new PNGs in `web_assets/` (dated `jam_<net>_network_<date>.png`).
4. Local preview: `python3 -m http.server 8000` → check sector pages
   (image + "Last updated" caption) and archive galleries.
5. On user approval: commit `networks.js`, new PNGs, `web_assets/archive/`,
   then `git push origin main`.
6. **Ask** before `git push prod main` (Vercel deploy → live).

## What the pipeline does internally

Per network: reads workbook → validates + aggregates (cumulative node/edge
weights) → builds in Gephi via REST (triangle cluster seeding; ForceAtlas 2
Stronger Gravity ON 0.05, LinLog, edge-weight influence 1.0; Prevent Overlap;
Noverlap; Label Adjust) → node sizing per config (`tiered` for dense nets:
repeats 1–3 small / 4–8 at 3× / >8 growing with count; `linear` 15–45 for
small nets), category pastel palettes, cyan #4EE2EC edges (burgundy blended
into the dark background) → exports SVG → wraps labels >15 chars + nudges
nodes until zero label overlaps → rasterises 3840×2160 transparent PNG via
headless Chrome one-shot → 480px thumbnail via `sips` → moves the outgoing
edition into `web_assets/archive/` → prepends the new edition to the
`networks.js` manifest (same-day reruns refresh the current edition in place).

Manifest editions carry `events`, `nodes`, `categories`, `edgeTypes` — the
sector pages' metric bars render from these, so the numbers update weekly
with no HTML edits.

`networks.js` is GENERATED — sector pages and archive galleries render the
newest image, caption date, and edition grids from it.

Skip logic: a network with no events newer than its last edition date is
skipped (use `--force` to override).

## Enabling the Energy network later

1. In `gephi/scripts/jam_network_pipeline.py`, set `NETWORKS['energy']['enabled'] = True`.
2. Create its sector page (clone the EU page pattern → `energy_ai_buildout.html`)
   and archive page (clone `network_archive_eu.html` → `network_archive_energy.html`,
   change `NET_KEY` to `'energy'`).
3. Rewire Sector C's "Explore Sector" card on index.html to the new page.
4. Run the pipeline — energy is included automatically from then on.

## Troubleshooting

- **"Gephi MCP API not reachable"** — launch the Gephi app, wait for the
  mcp plugin to start, re-run.
- **Raster fails / blank PNG** — headless Chrome one-shot mode
  (`jam_svg_raster.py`); check Chrome is installed at the standard path.
- **Unknown-node warnings** — add the node to the `Node Registry` sheet
  (name, type, category) and re-run with `--force`, or accept the default
  'Sector/Theme' (peach palette).
- Old single-network scripts (`jam_gephi_build.py`) are superseded but kept
  for reference.
