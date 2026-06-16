#!/usr/bin/env python3
"""Resolve residual node-label overlaps by nudging nodes apart based on the
WRAPPED label boxes (local separation, no global expansion), then re-export +
re-wrap the SVG. Repeats until the overlap checker reports zero."""
import json, urllib.request, time, os, re, html, subprocess, sys, math

B = "http://127.0.0.1:8080"
SVG = os.path.expanduser("~/Desktop/JAM-Intelligence/jam_ai_landscape_network.svg")
CHAR_W, LINE_H, PAD = 0.55, 1.05, 4.0   # glyph width frac, line-height frac, extra px padding

def call(path, payload=None, method="POST"):
    if method == "GET":
        req = urllib.request.Request(B + path, method="GET")
    else:
        req = urllib.request.Request(B + path, data=json.dumps(payload or {}).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())

FONT_K = 1.18   # proportional label font = node size * K (Arial-PLAIN-6 base)
MAXLEN = 15     # names longer than this wrap onto 2 lines (matches jam_wrap_labels.py)

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

def export_wrap():
    call("/export/svg", {"file": SVG})
    subprocess.run([sys.executable, "/tmp/jam_wrap_labels.py", SVG], capture_output=True)

def n_overlaps():
    r = subprocess.run([sys.executable, "/tmp/jam_label_overlap.py", SVG], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("OVERLAPPING LABEL PAIRS:"):
            return int(line.split(":")[1])
    return -1

def main():
    export_wrap()
    n = n_overlaps()
    print(f"start: {n} overlaps")
    prev, stall = n, 0
    for outer in range(40):
        if n == 0:
            break
        nodes = call("/graph/nodes", method="GET")["nodes"]
        # label box per node from its size + name (avoids SVG's flipped-Y coordinate)
        geo = [{"id": nd["id"], "x": nd["x"], "y": nd["y"],
                **dict(zip(("hw", "hh"), half_dims(nd["size"], nd["id"])))} for nd in nodes]
        # gentle global expansion only when local separation has stalled with overlaps left
        if stall >= 1:
            for g in geo:
                g["x"] *= 1.06; g["y"] *= 1.06
        # iterative local separation (push overlapping label boxes apart along least-penetration axis)
        for _ in range(800):
            moved = 0.0
            for i in range(len(geo)):
                for j in range(i+1, len(geo)):
                    a, b = geo[i], geo[j]
                    px = (a["hw"]+b["hw"]) - abs(a["x"]-b["x"])
                    py = (a["hh"]+b["hh"]) - abs(a["y"]-b["y"])
                    if px > 0 and py > 0:
                        if px < py:
                            s = px/2 * (1 if a["x"] >= b["x"] else -1)
                            a["x"] += s; b["x"] -= s; moved += px
                        else:
                            s = py/2 * (1 if a["y"] >= b["y"] else -1)
                            a["y"] += s; b["y"] -= s; moved += py
            if moved < 0.5:
                break
        call("/graph/nodes/positions", {"positions": [
            {"id": g["id"], "x": g["x"], "y": g["y"]} for g in geo]})
        export_wrap()
        n = n_overlaps()
        stall = stall + 1 if n >= prev else 0
        prev = n
        print(f"pass {outer+1}: {n} overlaps{' (stalled -> expand)' if stall >= 1 and n else ''}")

if __name__ == "__main__":
    main()
