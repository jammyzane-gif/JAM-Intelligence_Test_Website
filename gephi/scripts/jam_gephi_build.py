#!/usr/bin/env python3
"""Build the JAM Intelligence AI-landscape network in Gephi via the MCP REST API,
lay it out with ForceAtlas 2, and export a transparent SVG (rasterised to 4K PNG
by jam_svg_raster.py). Stdlib only."""
import json, urllib.request, time, sys, collections, os, random, math

B = "http://127.0.0.1:8080"
DESK = os.path.expanduser("~/Desktop/JAM-Intelligence")
SVG_OUT = os.path.join(DESK, "jam_ai_landscape_network.svg")
GEPHI_OUT = os.path.join(DESK, "jam_ai_landscape_network.gephi")

def call(path, payload=None, method="POST"):
    url = B + path
    if payload is None and method == "GET":
        req = urllib.request.Request(url, method="GET")
    else:
        req = urllib.request.Request(url, data=json.dumps(payload or {}).encode(),
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

# ---------------------------------------------------------------- data
# Node Registry: Node Name -> Node Type  (AI landscape; monetary-only nodes omitted)
REGISTRY = {
    # Company
    "Anthropic": "Company", "OpenAI": "Company", "Nvidia": "Company", "Broadcom": "Company",
    "Micron Technology": "Company", "CrowdStrike": "Company", "Dell": "Company",
    "Snowflake": "Company", "Salesforce": "Company", "SpaceX / xAI": "Company",
    "Google": "Company", "Meta": "Company", "Circle Internet": "Company",
    "Stripe": "Company", "Tesla": "Company",
    # Investor
    "Apollo": "Investor", "Blackstone": "Investor", "Blue Owl": "Investor",
    "BlackRock": "Investor", "Goldman Sachs": "Investor", "Morgan Stanley": "Investor",
    "Advent International": "Investor",
    # Financial Keyword
    "Capital Influx": "Financial Keyword", "Infrastructure & Spend": "Financial Keyword",
    "Metrics & Valuation": "Financial Keyword", "Exit & Liquidity": "Financial Keyword",
    # other registry types
    "EU / ENISA": "Regulator",
    "Federal Reserve": "Institution",
    "Hyperscalers": "Group", "Neo Cloud": "Group", "Big Four Consulting": "Group",
    "Asia Capex Boom": "Macro", "Iran War": "Macro",
    "Philadelphia SOX": "Index",
}
# unregistered edge endpoints -> Sector/Theme (handled by default below)

# Category pastel palettes (a random hex per node is drawn from its category's list)
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
    return PAL_OTHER  # Macro, Financial Keyword, Regulator, Index, Group, Sector/Theme

# AI 'Event Log' tab rows: (source, target, verb, weight)
EDGES_RAW = [
    ("China Gov", "AI Sector", "ALLOCATED", 1),
    ("China Gov", "Manufacturing", "ALLOCATED", 1),
    ("Circle Internet", "AI Agent Payments", "TARGETS", 1),
    ("Stripe", "AI Agent Payments", "TARGETS", 1),
    ("Capital Influx", "Visa", "REACHED", 1),
    ("Blackstone", "Capital Influx", "EXTENDED", 1),
    ("BlackRock", "Capital Influx", "EXTENDED", 1),
    ("Blue Owl", "Capital Influx", "EXTENDED", 1),
    ("Goldman Sachs", "Infrastructure & Spend", "GENERATES", 1),
    ("Federal Reserve", "Metrics & Valuation", "REACHED", 1),
    ("Iran War", "Capital Influx", "ALLOCATED", 1),
    ("Advent International", "Exit & Liquidity", "TARGETS", 1),
    ("Goldman Sachs", "Advent International", "FORMED", 1),
    ("Morgan Stanley", "Infrastructure & Spend", "GENERATES", 1),
    ("Asia Capex Boom", "AI Sector", "ALLOCATED", 2),
    ("Asia Capex Boom", "Defence", "ALLOCATED", 1),
    ("OpenAI", "Big Four Consulting", "TARGETS", 1),
    ("Anthropic", "Big Four Consulting", "TARGETS", 1),
    ("Micron Technology", "Metrics & Valuation", "REACHED", 1),
    ("Nvidia", "AI Sector", "GENERATES", 2),
    ("Snowflake", "Metrics & Valuation", "GENERATES", 1),
    ("Salesforce", "AI Sector", "ALLOCATED", 1),
    ("Dell", "Infrastructure & Spend", "GENERATES", 2),
    ("Dell", "Nvidia", "PROCURED", 2),
    ("Anthropic", "SpaceX / xAI", "LEASED", 3),
    ("SpaceX / xAI", "Infrastructure & Spend", "GENERATES", 3),
    ("Apollo", "Neo Cloud", "EXTENDED", 2),
    ("Blackstone", "Neo Cloud", "EXTENDED", 2),
    ("Anthropic", "Metrics & Valuation", "REACHED", 3),
    ("SpaceX / xAI", "Exit & Liquidity", "TARGETS", 2),
    ("SpaceX / xAI", "Metrics & Valuation", "REACHED", 2),
    ("Apollo", "Broadcom", "EXTENDED", 3),
    ("Blackstone", "Broadcom", "EXTENDED", 3),
    ("Broadcom", "Google", "FORMED", 2),
    ("Broadcom", "Anthropic", "FORMED", 2),
    ("Broadcom", "Metrics & Valuation", "GENERATES", 2),
    ("Nvidia", "Metrics & Valuation", "REACHED", 3),
    ("Philadelphia SOX", "Metrics & Valuation", "REACHED", 2),
    ("Anthropic", "EU / ENISA", "FORMED", 1),
    ("Anthropic", "Exit & Liquidity", "TARGETS", 2),
    ("Capital Influx", "Anthropic", "EXTENDED", 3),
    ("SpaceX / xAI", "Exit & Liquidity", "TARGETS", 3),
    ("Google", "Infrastructure & Spend", "ALLOCATED", 3),
    ("Google", "Capital Influx", "EXTENDED", 3),
    ("Hyperscalers", "Infrastructure & Spend", "EXPENSED", 3),
    ("Meta", "Infrastructure & Spend", "ALLOCATED", 2),
    ("Blue Owl", "Meta", "EXTENDED", 2),
    ("Broadcom", "Exit & Liquidity", "TARGETS", 2),
    ("CrowdStrike", "Metrics & Valuation", "REACHED", 1),
    ("SpaceX / xAI", "Metrics & Valuation", "OPERATES", 2),
    ("OpenAI", "Exit & Liquidity", "TARGETS", 3),
    ("SpaceX / xAI", "Exit & Liquidity", "TARGETS", 3),
    ("SpaceX / xAI", "Exit & Liquidity", "TARGETS", 3),
    ("SpaceX / xAI", "Metrics & Valuation", "REACHED", 3),
    ("Capital Influx", "SpaceX / xAI", "EXTENDED", 3),
    ("OpenAI", "Exit & Liquidity", "TARGETS", 3),
    ("Anthropic", "Exit & Liquidity", "TARGETS", 3),
    ("SpaceX / xAI", "Tesla", "TARGETS", 2),
    ("SpaceX / xAI", "Infrastructure & Spend", "ALLOCATED", 2),
    ("SpaceX / xAI", "Metrics & Valuation", "REACHED", 3),
    ("SpaceX / xAI", "Capital Influx", "EXTENDED", 3),
]

def ntype(name):
    return REGISTRY.get(name, "Sector/Theme")

def hex_rgb(h):
    return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))

def lerp_rgb(c1, c2, t):
    a, b = hex_rgb(c1), hex_rgb(c2)
    return tuple(round(a[i] + (b[i]-a[i])*t) for i in range(3))

def main():
    os.makedirs(DESK, exist_ok=True)
    # nodes
    names = sorted({s for s, *_ in EDGES_RAW} | {t for _, t, *_ in EDGES_RAW})
    # aggregate edges per (source,target)
    agg = collections.OrderedDict()
    for s, t, verb, w in EDGES_RAW:
        k = (s, t)
        if k not in agg:
            agg[k] = {"weight": 0, "verbs": collections.Counter(), "count": 0}
        agg[k]["weight"] += w
        agg[k]["verbs"][verb] += 1
        agg[k]["count"] += 1
    weights = [d["weight"] for d in agg.values()]
    wmin, wmax = min(weights), max(weights)
    # cumulative Weight Increment per node (sum over every Event Log row it appears in, as src or tgt)
    cumw = collections.Counter()
    for s, t, verb, w in EDGES_RAW:
        cumw[s] += w
        cumw[t] += w
    cwmin, cwmax = min(cumw.values()), max(cumw.values())
    print(f"{len(names)} nodes, {len(agg)} aggregated edges (from {len(EDGES_RAW)} rows); "
          f"summed-weight range {wmin}-{wmax}; node cumulative-weight range {cwmin}-{cwmax}")

    print("\n[1] project + column")
    must("/project/new")
    must("/graph/clear", quiet=True)
    must("/graph/columns/add", {"name": "nodeType", "type": "STRING", "defaultValue": ""})

    print("\n[2] add nodes")
    must("/graph/nodes/add", {"nodes": [{"id": n, "label": n} for n in names]})
    must("/graph/nodes/attributes",
         {"updates": [{"id": n, "attributes": {"nodetype": ntype(n)}} for n in names]})

    print("\n[3] add aggregated edges (weight)")
    must("/graph/edges/add", {"edges": [
        {"source": s, "target": t, "weight": d["weight"]} for (s, t), d in agg.items()]})

    print("\n[4] seed positions by category (loose triangle)")
    random.seed(42)
    SEED = {"Company": (-300, 100), "Investor": (300, 100), "Institution": (0, -300)}
    positions = []
    for n in names:
        t = ntype(n)
        if t in SEED:
            cx, cy = SEED[t]
            positions.append({"id": n, "x": cx + random.uniform(-60, 60),
                              "y": cy + random.uniform(-60, 60)})
        else:  # scatter on a ring around the outside
            ang = random.uniform(0, 2 * math.pi); rad = random.uniform(650, 900)
            positions.append({"id": n, "x": rad * math.cos(ang), "y": rad * math.sin(ang)})
    must("/graph/nodes/positions", {"positions": positions})

    print("\n[5] node size by cumulative weight (min 15, max 26 — compressed ~1.7x range)")
    SMIN, SMAX = 15.0, 45.0
    for n in names:
        frac = 0.0 if cwmax == cwmin else (cumw[n] - cwmin) / (cwmax - cwmin)
        size = SMIN + frac * (SMAX - SMIN)
        call("/appearance/node/size", {"id": n, "size": round(size, 2)})
    print(f"  sized {len(names)} nodes by cumulative weight ({SMIN}-{SMAX}, ratio {SMAX/SMIN:.2f}x)")

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

    FA2 = {
        "ForceAtlas2.strongGravityMode.name": True,
        "ForceAtlas2.gravity.name": 0.05,
        "ForceAtlas2.linLogMode.name": True,
        "ForceAtlas2.scalingRatio.name": float(os.environ.get("FA2_SCALE", "20")),
        "ForceAtlas2.edgeWeightInfluence.name": 1.0,
    }
    print(f"\n[6] ForceAtlas 2 (scaling={FA2['ForceAtlas2.scalingRatio.name']}) -> Prevent Overlap finish")
    run_layout("ForceAtlas 2", 2000, FA2)
    run_layout("ForceAtlas 2", 400, {**FA2, "ForceAtlas2.adjustSizes.name": True})  # Prevent Overlap (nodes)
    run_layout("Noverlap", 600, {"Noverlap.ratio.name": 1.5, "Noverlap.margin.name": 14.0})
    # Label Adjust to convergence: separate labels until none overlap (priority: no label intersects)
    for _ in range(6):
        run_layout("Label Adjust", 1000)
    ns = call("/graph/nodes", method="GET")["nodes"]
    xs = [n["x"] for n in ns]; ys = [n["y"] for n in ns]
    print(f"  coord spread: x[{min(xs):.0f},{max(xs):.0f}] y[{min(ys):.0f},{max(ys):.0f}]")

    print("\n[7] node colours: random pastel per category (r,g,b)")
    for n in names:
        r, g, b = hex_rgb(random.choice(palette_for(ntype(n))))
        call("/appearance/node/color", {"id": n, "r": r, "g": g, "b": b})
    print(f"  coloured {len(names)} nodes")

    print("\n[8] edge colours: uniform burgundy #800020 (r,g,b)")
    br, bg_, bb = hex_rgb("#800020")
    for (s, t) in agg:
        call("/appearance/edge/color", {"source": s, "target": t, "r": br, "g": bg_, "b": bb})
    print(f"  coloured {len(agg)} edges")

    print("\n[9] preview settings")
    must("/preview/settings", {
        "node.label.show": True,
        "node.label.proportinalSize": True,
        "node.label.font": "Arial-PLAIN-6",  # smaller base => proportional labels shrunk overall
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

    print("\n[10] export + wrap long labels + de-overlap (no two labels may intersect)")
    must("/export/svg", {"file": SVG_OUT})
    must("/project/save", {"file": GEPHI_OUT}, quiet=True)
    import subprocess
    # wrap labels >15 chars onto 2 lines, then nudge nodes until 0 label overlaps, re-export
    subprocess.run([sys.executable, "/tmp/jam_fix_label_overlap.py"])
    print(f"\nSVG: {SVG_OUT}")
    print(f"GEPHI: {GEPHI_OUT}")
    print(json.dumps(call("/graph/stats", method="GET"), indent=2))

if __name__ == "__main__":
    main()
