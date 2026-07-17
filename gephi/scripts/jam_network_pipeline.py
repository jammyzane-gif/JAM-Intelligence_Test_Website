#!/usr/bin/env python3
"""JAM Intelligence — weekly network pipeline (Workflow 6).

One command builds every enabled network from the master Event Log workbook,
styles it in Gephi (via the gephi-mcp REST API), exports a dated 4K PNG,
archives the outgoing edition and updates the networks.js manifest that the
website renders from. Stdlib only.

Usage:
    python3 gephi/scripts/jam_network_pipeline.py            # all enabled networks
    python3 gephi/scripts/jam_network_pipeline.py ai         # just one
    python3 gephi/scripts/jam_network_pipeline.py --force ai # rebuild even with no new events
"""
import json, urllib.request, time, sys, collections, os, random, math, re
import subprocess, shutil, zipfile, datetime
import xml.etree.ElementTree as ET

B = "http://127.0.0.1:8080"
ROOT = os.path.expanduser("~/Desktop/JAM-Intelligence")
SCRIPTS = os.path.join(ROOT, "gephi", "scripts")
WORKBOOK = os.path.join(ROOT, "data", "Jam_Intelligence_Network_EventLog_Everyday_Update.xlsx")
MANIFEST = os.path.join(ROOT, "networks.js")
WEB_ASSETS = os.path.join(ROOT, "web_assets")
ARCHIVE = os.path.join(WEB_ASSETS, "archive")
THUMBS = os.path.join(ARCHIVE, "thumbs")

NETWORKS = {
    "ai": {
        "sheet": "Event Log",
        "name": "AI Landscape",
        "out": "jam_ai_network",
        "sectorPage": "ai_transformation_for_smes.html",
        "archivePage": "network_archive_ai.html",
        "sizing": "tiered",   # dense net: bucket sizes so differences read clearly
        "shape": "circle",    # equalise x/y spread after layout (FA2 tends to a tall oval here)
        "enabled": True,
    },
    "economy": {
        "sheet": "Monetary Event Log",
        "name": "Economy & Monetary",
        "out": "jam_economy_network",
        "sectorPage": "eu_tech_economics.html",
        "archivePage": "network_archive_eu.html",
        "sizing": "linear",   # small net reads well with plain 15–45 scaling
        "enabled": True,
    },
    # Flip enabled to True (and create the sector/archive pages) when enough
    # energy events are logged — nothing else needs to change.
    "energy": {
        "sheet": "Energy Event Log",
        "name": "Energy & AI Buildout",
        "out": "jam_energy_network",
        "sectorPage": "energy_ai_buildout.html",
        "archivePage": "network_archive_energy.html",
        "enabled": False,
    },
}

# The pre-pipeline AI export referenced by index.html's featured card — copy,
# never move, so the homepage image keeps working.
PINNED_FILES = {"web_assets/jam_ai_landscape_network_4k.png"}

# Edge colour: bright cyan — burgundy #800020 blended into the dark page background.
EDGE_COLOR = "#4EE2EC"

# ---------------------------------------------------------------- gephi REST
def call(path, payload=None, method="POST"):
    if payload is None and method == "GET":
        req = urllib.request.Request(B + path, method="GET")
    else:
        req = urllib.request.Request(B + path, data=json.dumps(payload or {}).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())

def must(path, payload=None, method="POST", quiet=False):
    res = call(path, payload, method)
    if not res.get("success", False):
        print(f"  ! {path}: {res.get('error') or res.get('message')}")
    elif not quiet:
        msg = res.get("message") or res.get("added") or res.get("status") or "ok"
        print(f"  {path}: {msg}")
    return res

# ---------------------------------------------------------------- xlsx reader
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

def read_workbook(path):
    """Return {sheet_name: [[cell, ...], ...]} for every sheet."""
    z = zipfile.ZipFile(path)
    try:
        ss = ET.fromstring(z.read("xl/sharedStrings.xml"))
        strings = ["".join(t.text or "" for t in si.iter(NS + "t")) for si in ss]
    except KeyError:
        strings = []
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid2t = {r.get("Id"): r.get("Target") for r in rels}
    sheets = {}
    for s in wb.iter(NS + "sheet"):
        tgt = rid2t[s.get(REL_NS + "id")]
        part = "xl/" + tgt if not tgt.startswith("/") else tgt[1:]
        sh = ET.fromstring(z.read(part))
        rows = []
        for row in sh.iter(NS + "row"):
            vals = {}
            for c in row.iter(NS + "c"):
                ref = c.get("r") or ""
                col = "".join(ch for ch in ref if ch.isalpha())
                idx = 0
                for ch in col:
                    idx = idx * 26 + (ord(ch) - 64)
                v = c.find(NS + "v")
                if c.get("t") == "s" and v is not None:
                    val = strings[int(v.text)]
                elif c.get("t") == "inlineStr":
                    val = "".join(t.text or "" for t in c.iter(NS + "t"))
                else:
                    val = v.text if v is not None else ""
                vals[idx - 1] = val
            width = max(vals) + 1 if vals else 0
            rows.append([vals.get(i, "") for i in range(width)])
        sheets[s.get("name")] = rows
    return sheets

def parse_date(v):
    """Excel serial number or ISO-ish string -> datetime.date (or None)."""
    v = str(v).strip()
    if not v:
        return None
    try:
        serial = float(v)
        return (datetime.date(1899, 12, 30) + datetime.timedelta(days=serial))
    except ValueError:
        pass
    m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", v)
    if m:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None

# ---------------------------------------------------------------- data layer
def load_events(sheets, sheet_name):
    """Rows -> [(date, source, target, verb, weight)], with validation warnings."""
    rows = sheets[sheet_name]
    events, warnings = [], []
    for i, row in enumerate(rows[1:], start=2):  # skip header; 1-based + header
        row = list(row) + [""] * (6 - len(row))
        d, src, tgt, verb, w, _title = row[:6]
        if not str(src).strip() and not str(tgt).strip():
            continue  # blank row
        date = parse_date(d)
        if date is None:
            warnings.append(f"row {i}: bad date {d!r}")
        try:
            weight = float(w)
            if weight < 0:
                warnings.append(f"row {i}: negative weight {w!r}")
        except (TypeError, ValueError):
            warnings.append(f"row {i}: bad weight {w!r} -> using 1.0")
            weight = 1.0
        events.append((date, str(src).strip(), str(tgt).strip(), str(verb).strip(), weight))
    return events, warnings

def load_registry(sheets):
    reg = {}
    for row in sheets.get("Node Registry", [])[1:]:
        row = list(row) + [""] * 2
        name, ntype = str(row[0]).strip(), str(row[1]).strip()
        if name:
            reg[name] = ntype or "Sector/Theme"
    return reg

# ---------------------------------------------------------------- styling data
PAL_COMPANY = ["#EEEEEE", "#E5E4E2", "#BCC6CC", "#98AFC7", "#838996", "#778899",
               "#708090", "#6D7B8D", "#657383", "#616D7E", "#646D7E", "#6E7F80",
               "#71797E", "#566D7E", "#737CA1"]
PAL_INVESTOR = ["#A0CFEC", "#B7CEEC", "#B4CFEC", "#ADDFFF", "#C2DFFF", "#C6DEFF",
                "#BDEDFF", "#B0E0E6", "#AFDCEC", "#ADD8E6", "#B0CFDE", "#C9DFEC"]
PAL_INSTITUTION = ["#99C68E", "#A0D6B4", "#8FBC8F", "#829F82", "#A2AD9C", "#B8BC86", "#9CB071"]
PAL_OTHER = ["#FFE4B5", "#FFE5B4", "#FED8B1", "#FFDAB9", "#FBD5AB", "#FFDEAD",
             "#FBE7A1", "#F3E3C3", "#F0E2B6", "#F1E5AC", "#F3E5AB"]

def palette_for(node_type):
    if node_type == "Company": return PAL_COMPANY
    if node_type == "Investor": return PAL_INVESTOR
    if node_type == "Institution": return PAL_INSTITUTION
    return PAL_OTHER

def hex_rgb(h):
    return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))

# ---------------------------------------------------------------- label pass
CHAR_W, LINE_H, PAD = 0.55, 1.05, 4.0
FONT_K, MAXLEN = 1.18, 15

def label_lines(name):
    if len(name) <= MAXLEN or " " not in name:
        return [name]
    cut = name.rfind(" ")
    return [name[:cut].rstrip(), name[cut+1:].lstrip()]

def half_dims(size, name):
    font = size * FONT_K
    lines = label_lines(name)
    w = max(len(ln) for ln in lines) * font * CHAR_W + PAD
    h = len(lines) * font * LINE_H + PAD
    return w / 2, h / 2

def export_wrap(svg_path):
    call("/export/svg", {"file": svg_path})
    subprocess.run([sys.executable, os.path.join(SCRIPTS, "jam_wrap_labels.py"), svg_path],
                   capture_output=True)

def n_overlaps(svg_path):
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "jam_label_overlap.py"), svg_path],
                       capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("OVERLAPPING LABEL PAIRS:"):
            return int(line.split(":")[1])
    return -1

def fix_label_overlaps(svg_path):
    export_wrap(svg_path)
    n = n_overlaps(svg_path)
    print(f"  label overlaps: {n}")
    prev, stall = n, 0
    for outer in range(40):
        if n == 0:
            break
        nodes = call("/graph/nodes", method="GET")["nodes"]
        geo = [{"id": nd["id"], "x": nd["x"], "y": nd["y"],
                **dict(zip(("hw", "hh"), half_dims(nd["size"], nd["id"])))} for nd in nodes]
        if stall >= 1:
            for g in geo:
                g["x"] *= 1.06; g["y"] *= 1.06
        for _ in range(800):
            moved = 0.0
            for i in range(len(geo)):
                for j in range(i + 1, len(geo)):
                    a, b = geo[i], geo[j]
                    px = (a["hw"] + b["hw"]) - abs(a["x"] - b["x"])
                    py = (a["hh"] + b["hh"]) - abs(a["y"] - b["y"])
                    if px > 0 and py > 0:
                        if px < py:
                            s = px / 2 * (1 if a["x"] >= b["x"] else -1)
                            a["x"] += s; b["x"] -= s; moved += px
                        else:
                            s = py / 2 * (1 if a["y"] >= b["y"] else -1)
                            a["y"] += s; b["y"] -= s; moved += py
            if moved < 0.5:
                break
        call("/graph/nodes/positions", {"positions": [
            {"id": g["id"], "x": g["x"], "y": g["y"]} for g in geo]})
        export_wrap(svg_path)
        n = n_overlaps(svg_path)
        stall = stall + 1 if n >= prev else 0
        prev = n
        print(f"  label pass {outer+1}: {n} overlaps{' (stalled -> expand)' if stall >= 1 and n else ''}")

# ---------------------------------------------------------------- manifest
MANIFEST_HEADER = """/* ════════════════════════════════════════════════════════════════
   JAM Intelligence — network editions manifest.
   GENERATED by gephi/scripts/jam_network_pipeline.py — edit by hand only
   to correct mistakes. Pages render the newest edition + archives from it.
   ════════════════════════════════════════════════════════════════ */

const NETWORKS = """

def load_manifest():
    if not os.path.exists(MANIFEST):
        data = {}
        for key, cfg in NETWORKS.items():
            data[key] = {"name": cfg["name"], "sectorPage": cfg["sectorPage"],
                         "archivePage": cfg["archivePage"], "editions": []}
        # backfill: the June AI export is edition #1
        data["ai"]["editions"].append({
            "date": "2026-06-12",
            "file": "web_assets/jam_ai_landscape_network_4k.png",
            "thumb": None, "events": None, "nodes": None,
        })
        return data
    src = open(MANIFEST).read()
    body = src[src.index("const NETWORKS =") + len("const NETWORKS ="):].strip()
    body = body.rstrip(";\n ")
    return json.loads(body)

def save_manifest(data):
    with open(MANIFEST, "w") as f:
        f.write(MANIFEST_HEADER + json.dumps(data, indent=2) + ";\n")

# ---------------------------------------------------------------- build one net
def run_layout(algo, iters, props=None, maxwait=180):
    body = {"algorithm": algo, "iterations": iters}
    if props:
        body["properties"] = props
    must("/layout/run", body, quiet=True)
    t0 = time.time()
    while time.time() - t0 < maxwait:
        if not call("/layout/status", method="GET").get("running"):
            break
        time.sleep(1.5)
    call("/layout/stop", {})
    print(f"  {algo}: {time.time()-t0:.0f}s")

def build_network(key, cfg, sheets, registry, manifest, force=False):
    today = datetime.date.today()
    print(f"\n══ {cfg['name']} ({key}) ══")
    events, warnings = load_events(sheets, cfg["sheet"])
    for w in warnings[:10]:
        print(f"  ⚠ {w}")
    if len(warnings) > 10:
        print(f"  ⚠ …and {len(warnings)-10} more warnings")

    net = manifest.setdefault(key, {"name": cfg["name"], "sectorPage": cfg["sectorPage"],
                                    "archivePage": cfg["archivePage"], "editions": []})
    dates = [d for d, *_ in events if d]
    last = net["editions"][0]["date"] if net["editions"] else None
    newest_event = max(dates).isoformat() if dates else None
    if not force and last and newest_event and newest_event <= last:
        print(f"  no events newer than last edition ({last}) — skipped (use --force to rebuild)")
        return False

    # aggregate
    names = sorted({s for _, s, *_ in events} | {t for _, _, t, *_ in events})
    unknown = [n for n in names if n not in registry]
    if unknown:
        print(f"  ⚠ {len(unknown)} nodes not in Node Registry (default 'Sector/Theme'): "
              + ", ".join(unknown[:8]) + ("…" if len(unknown) > 8 else ""))
    agg = collections.OrderedDict()
    cumw = collections.Counter()
    for _, s, t, verb, w in events:
        k = (s, t)
        agg.setdefault(k, 0)
        agg[k] += w
        cumw[s] += w
        cumw[t] += w
    cwmin, cwmax = min(cumw.values()), max(cumw.values())
    span = f"{min(dates)} → {max(dates)}" if dates else "no dates"
    print(f"  {len(events)} events | {len(names)} nodes | {len(agg)} edges | {span}")

    def ntype(name):
        return registry.get(name, "Sector/Theme")

    # ---- Gephi build (recipe ported verbatim from jam_gephi_build.py) ----
    must("/project/new")
    must("/graph/clear", quiet=True)
    must("/graph/columns/add", {"name": "nodeType", "type": "STRING", "defaultValue": ""})
    must("/graph/nodes/add", {"nodes": [{"id": n, "label": n} for n in names]})
    must("/graph/nodes/attributes",
         {"updates": [{"id": n, "attributes": {"nodetype": ntype(n)}} for n in names]})
    must("/graph/edges/add", {"edges": [
        {"source": s, "target": t, "weight": w} for (s, t), w in agg.items()]})

    random.seed(42)
    SEED_POS = {"Company": (-300, 100), "Investor": (300, 100), "Institution": (0, -300)}
    positions = []
    for n in names:
        t = ntype(n)
        if t in SEED_POS:
            cx, cy = SEED_POS[t]
            positions.append({"id": n, "x": cx + random.uniform(-60, 60),
                              "y": cy + random.uniform(-60, 60)})
        else:
            ang = random.uniform(0, 2 * math.pi); rad = random.uniform(650, 900)
            positions.append({"id": n, "x": rad * math.cos(ang), "y": rad * math.sin(ang)})
    must("/graph/nodes/positions", {"positions": positions})

    if cfg.get("sizing") == "tiered":
        # Tiered sizing so differences read clearly:
        #   repeats 1–3  -> SMALL, repeats 4–8 -> MED (1:3 ratio),
        #   repeats >8   -> grows with the repeat count, capped at TOP for the biggest hub.
        SMALL, MED, TOP = 12.0, 36.0, 64.0
        for n in names:
            w = cumw[n]
            if w <= 3:
                size = SMALL
            elif w <= 8:
                size = MED
            else:
                size = MED + (w - 8) / max(cwmax - 8, 1) * (TOP - MED) if cwmax > 8 else MED
            call("/appearance/node/size", {"id": n, "size": round(size, 2)})
    else:
        # linear: plain min–max scaling by cumulative weight
        SMIN, SMAX = 15.0, 45.0
        for n in names:
            frac = 0.0 if cwmax == cwmin else (cumw[n] - cwmin) / (cwmax - cwmin)
            call("/appearance/node/size", {"id": n, "size": round(SMIN + frac * (SMAX - SMIN), 2)})

    FA2 = {
        "ForceAtlas2.strongGravityMode.name": True,
        "ForceAtlas2.gravity.name": 0.05,
        "ForceAtlas2.linLogMode.name": True,
        "ForceAtlas2.scalingRatio.name": float(os.environ.get("FA2_SCALE", "20")),
        "ForceAtlas2.edgeWeightInfluence.name": 1.0,
    }
    run_layout("ForceAtlas 2", 2000, FA2)
    run_layout("ForceAtlas 2", 400, {**FA2, "ForceAtlas2.adjustSizes.name": True})
    run_layout("Noverlap", 600, {"Noverlap.ratio.name": 1.5, "Noverlap.margin.name": 14.0})
    for _ in range(6):
        run_layout("Label Adjust", 1000)

    if cfg.get("shape") == "circle":
        # widen the cloud: rescale x so horizontal spread matches vertical
        ns = call("/graph/nodes", method="GET")["nodes"]
        cx = sum(nd["x"] for nd in ns) / len(ns)
        cy = sum(nd["y"] for nd in ns) / len(ns)
        sx = max(abs(nd["x"] - cx) for nd in ns) or 1.0
        sy = max(abs(nd["y"] - cy) for nd in ns) or 1.0
        k = sy / sx
        print(f"  circularise: x-spread {sx:.0f} vs y-spread {sy:.0f} -> scale x by {k:.2f}")
        must("/graph/nodes/positions", {"positions": [
            {"id": nd["id"], "x": cx + (nd["x"] - cx) * k, "y": nd["y"]} for nd in ns]}, quiet=True)
        run_layout("Noverlap", 300, {"Noverlap.ratio.name": 1.5, "Noverlap.margin.name": 14.0})
        run_layout("Label Adjust", 800)

    for n in names:
        r, g, b = hex_rgb(random.choice(palette_for(ntype(n))))
        call("/appearance/node/color", {"id": n, "r": r, "g": g, "b": b})
    br, bg_, bb = hex_rgb(EDGE_COLOR)
    for (s, t) in agg:
        call("/appearance/edge/color", {"source": s, "target": t, "r": br, "g": bg_, "b": bb})

    must("/preview/settings", {
        "node.label.show": True,
        "node.label.proportinalSize": True,
        "node.label.font": "Arial-PLAIN-6",
        "node.label.color": "#0a0a0c",
        "node.label.outline.color": "#FFFFFF",
        "node.label.outline.size": 4.0,
        "node.label.outline.opacity": 100.0,
        "edge.label.show": False,
        "edge.color": "original",
        "edge.rescale-weight": True,
        "edge.rescale-weight.min": 1.0,
        "edge.rescale-weight.max": 14.0,
        "edge.opacity": 100.0,
        "edge.curved": True,
    })

    svg_path = os.path.join(ROOT, "gephi", f"{cfg['out']}.svg")
    fix_label_overlaps(svg_path)
    must("/project/save", {"file": os.path.join(ROOT, "gephi", f"{cfg['out']}.gephi")}, quiet=True)

    # ---- raster + thumbnail + archive + manifest ----
    stamp = today.isoformat()
    png_rel = f"web_assets/{cfg['out']}_{stamp}.png"
    png_abs = os.path.join(ROOT, png_rel)
    subprocess.run([sys.executable, os.path.join(SCRIPTS, "jam_svg_raster.py"),
                    svg_path, png_abs, "3840", "2160"], check=True)
    os.makedirs(THUMBS, exist_ok=True)
    thumb_rel = f"web_assets/archive/thumbs/{cfg['out']}_{stamp}.png"
    subprocess.run(["sips", "-Z", "480", png_abs, "--out", os.path.join(ROOT, thumb_rel)],
                   capture_output=True, check=True)

    entry = {
        "date": stamp, "file": png_rel, "thumb": thumb_rel,
        "events": len(events), "nodes": len(names),
        "categories": len({ntype(n) for n in names}),
        "edgeTypes": len({verb for _, _, _, verb, _ in events if verb}),
    }
    same_day = net["editions"] and net["editions"][0]["date"] == stamp
    if same_day:
        # re-run on the same day = refresh the current edition in place
        net["editions"][0] = entry
    else:
        # archive the outgoing edition's file (copy pinned files, move the rest)
        if net["editions"]:
            prev_ed = net["editions"][0]
            src_abs = os.path.join(ROOT, prev_ed["file"])
            if os.path.exists(src_abs) and not prev_ed["file"].startswith("web_assets/archive/"):
                dst_rel = f"web_assets/archive/{os.path.basename(prev_ed['file'])}"
                os.makedirs(ARCHIVE, exist_ok=True)
                if prev_ed["file"] in PINNED_FILES:
                    shutil.copy2(src_abs, os.path.join(ROOT, dst_rel))
                else:
                    shutil.move(src_abs, os.path.join(ROOT, dst_rel))
                prev_ed["file"] = dst_rel
        net["editions"].insert(0, entry)
    save_manifest(manifest)
    print(f"  ✓ {png_rel} ({len(events)} events, {len(names)} nodes, "
          f"{entry['categories']} categories, {entry['edgeTypes']} edge types)"
          f"{' — same-day refresh' if same_day else ''} — manifest updated")
    return True

# ---------------------------------------------------------------- main
def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    force = "--force" in sys.argv
    keys = args or [k for k, c in NETWORKS.items() if c["enabled"]]
    for k in keys:
        if k not in NETWORKS:
            sys.exit(f"unknown network {k!r} — choose from {', '.join(NETWORKS)}")

    try:
        h = call("/health", method="GET")
        assert h.get("success")
    except Exception:
        sys.exit("Gephi MCP API not reachable at http://127.0.0.1:8080 — launch Gephi first.")
    print(f"Gephi MCP API up ({call('/health', method='GET').get('version', '?')})")

    if not os.path.exists(WORKBOOK):
        sys.exit(f"workbook not found: {WORKBOOK}")
    sheets = read_workbook(WORKBOOK)
    registry = load_registry(sheets)
    print(f"workbook: {len(sheets)} sheets, registry {len(registry)} nodes")

    manifest = load_manifest()
    built = [k for k in keys if build_network(k, NETWORKS[k], sheets, registry, manifest, force)]
    print(f"\ndone — built: {', '.join(built) or 'nothing'}")
    if built:
        print("next: preview the site locally, then commit web_assets/*.png, "
              "web_assets/archive/, networks.js")

if __name__ == "__main__":
    main()
