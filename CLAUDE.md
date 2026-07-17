# JAM Intelligence Website Project

## Repo setup
- Private working repo: JAM-Intelligence_Test_Website (origin)
- Public production repo: JAM-Intelligence (prod)
- Live site: jammyzane.com (Vercel auto-deploys from prod)

## Workflow
- Work freely: git push origin main (private repo — saves progress, nothing goes public)
- Go live: git push prod main (public repo — triggers Vercel deploy to jammyzane.com)
- Internal files (CLAUDE.md, README.md, gephi/) are listed in .vercelignore so
  Vercel never serves them on the live site. Add any new internal/working file
  to .vercelignore before it first reaches prod.

## Tech stack
- Static HTML/CSS/JS
- Vercel deployment
- React components: shadcn, Tailwind, TypeScript

## Key files
- index.html — main site
- ai_transformation_for_smes.html — AI sector page
- web_assets/ — images including network visualisation
- components/ui/ — React components

## Design system
- Primary: #800020 (burgundy), #560319 (dark scarlet)
- Background: #000000
- Font: Antic (Google Fonts)
- Reference: CIL Strategy Consultants (cil.com)

## Current priorities
- ~~Insight page restructure (Workflow 5)~~ — done, live 14 Jul 2026
- ~~Weekly network system (Workflow 6, absorbs 2+3)~~ — built 17 Jul 2026; AI + Economy networks live weekly
- Next: enable Energy network (Workflow 6 doc, "Enabling the Energy network later") once enough events are logged

## Recurring Workflows

### Workflow 1 — Publish new insight from Google Drive
Trigger phrase: "publish new insight"
Steps:
1. I will drop the insight file (docx/txt) into assets/incoming/
2. Read it, extract title, sector tag, date
3. Create a new insight HTML page using the existing 
   article page template (match layout, fonts, like button)
4. Add the article card to the top of the correct 
   sector's insight listing
5. Add the like button (white star, white frame, white 
   count, localStorage persistence)
6. Show me the preview before pushing
7. On my approval: git push origin main, then ask 
   before git push prod main

### Workflow 6 — Weekly network update (replaces Workflows 2 + 3)
Trigger phrase: "update the networks"
One command rebuilds all enabled networks (AI, Economy; Energy stubbed)
from data/Jam_Intelligence_Network_EventLog_Everyday_Update.xlsx via live
Gephi, exports dated 4K PNGs, archives old editions, updates networks.js.
Requires Gephi running. Preview → approval → push origin → ask → push prod.
Full runbook: @docs/workflows/network-update.md

### Workflow 4 — Add visualisation section to a sector page
Trigger phrase: "add visualisation to [sector] page"
Steps:
1. Duplicate the arched visualisation frame from the 
   AI sector page as a reusable pattern
2. Insert placeholder image + heading + caption + 
   detail panel (3-row layout: metrics top, components 
   middle, detail bottom)
3. Wire "Explore Sector" on the Sectors page to the 
   new sector page (new tab)
4. Update the fallback: sectors without a page keep 
   linking to Insights

### Workflow 5 — Insight page restructure (one-off)
The Insights nav link should lead to a hub page with 
3 sector columns (AI Transformation for SMEs / EU Tech 
and Economics Landscapes / Energy & AI Buildout), each 
column showing the sector title + latest article previews.
Clicking a sector title opens that sector's own insight 
listing page showing only its articles.
File plan:
- insights.html → becomes the 3-column hub
- insights_ai.html, insights_eu.html, insights_energy.html 
  → per-sector listings
- Existing article pages unchanged, but each article 
  card lives only on its sector's listing
