# JAM Intelligence — Test Website & AI Landscape Network

Source for the JAM Intelligence test website plus the pipeline that builds the
AI-landscape network visualization featured on it.

## Website

- `index.html` — main landing page
- `insight.html` — insights page
- `web_assets/` — site images
  - `jam_intelligence_logo.png`
  - `jam_ai_landscape_network_4k.png` — 3840×2160 transparent network map (final render)

Static site — no build step. Open the HTML directly or serve the folder
(`python3 -m http.server`).

## Gephi network visualization

A network map of the JAM Intelligence AI landscape, built from a Google Drive
EventLog spreadsheet via the Gephi-MCP REST API (`http://127.0.0.1:8080`) and
exported as a transparent 4K PNG for the dark site.

- `gephi/jam_ai_landscape_network.svg` — vector export (transparent, exact colors)
- `gephi/_preview_dark.png`, `gephi/_preview_white.png` — composites for inspection
- `gephi/scripts/` — build pipeline
  - `jam_gephi_build.py` — builds graph, styles, seeds layout, runs ForceAtlas 2,
    exports SVG, then runs the de-overlap fixer
  - `jam_svg_raster.py` — rasterizes the SVG to a 3840×2160 transparent PNG via
    headless Chrome (CDP); native Gephi PNG export is opaque-white only
  - `jam_wrap_labels.py` — wraps node labels >15 chars onto two lines (Gephi
    ignores `\n`, so this is post-processed in the SVG)
  - `jam_label_overlap.py` — checker: reports any intersecting label boxes
  - `jam_fix_label_overlap.py` — nudges nodes apart until 0 label overlaps
  - `jam_preview.py` — composites the 4K PNG over dark/white backgrounds
  - `jam_shot.py` — screenshot helper

### Design

- Nodes sized by cumulative edge Weight Increment (min 15 → max 45, 3× ratio)
- Nodes colored by category from pastel palettes (companies/investors/institutions/other)
- Uniform burgundy edges (`#800020`), thickness by cumulative weight
- Loose-triangle layout (ForceAtlas 2, seeded by category)

> Requires Gephi 0.10.1 running with the Gephi-MCP plugin to regenerate.
