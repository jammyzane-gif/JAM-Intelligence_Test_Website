#!/usr/bin/env python3
"""Parse the exported network SVG and report any pairs of node labels whose
bounding boxes visually intersect. Ground-truth check for 'no labels overlap'."""
import re, sys, os, html

SVG = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/Desktop/JAM-Intelligence/jam_ai_landscape_network.svg")
CHAR_W = 0.55   # avg glyph width as fraction of font-size (sans)
H_FACT = 1.0    # label box height as fraction of font-size

s = open(SVG).read()
labels = {}  # class -> (x, y, font, [lines])
for m in re.finditer(r'<text\b([^>]*)>(.*?)</text>', s, re.S):
    attrs, body = m.group(1), m.group(2)
    def g(k):
        mm = re.search(rf'{k}="([^"]+)"', attrs)
        return mm.group(1) if mm else None
    x, y, fs = g("x"), g("y"), g("font-size")
    if x is None or y is None or fs is None:
        continue
    cls = g("class") or body
    tspans = re.findall(r'<tspan[^>]*>(.*?)</tspan>', body, re.S)
    lines = [html.unescape(t).strip() for t in tspans] if tspans else [html.unescape(body).strip()]
    labels[cls] = (float(x), float(y), float(fs), lines)  # dedupe outline+fill by class

boxes = []
for cls, (x, y, fs, lines) in labels.items():
    w = max(len(ln) for ln in lines) * fs * CHAR_W
    h = len(lines) * fs * 1.05 * H_FACT
    label = " / ".join(lines)
    boxes.append((label, x - w/2, y - h/2, x + w/2, y + h/2))

def overlap(a, b):
    return not (a[3] <= b[1] or b[3] <= a[1] or a[4] <= b[2] or b[4] <= a[2])

pairs = []
for i in range(len(boxes)):
    for j in range(i+1, len(boxes)):
        if overlap(boxes[i], boxes[j]):
            # intersection area for ranking
            ix = min(boxes[i][3], boxes[j][3]) - max(boxes[i][1], boxes[j][1])
            iy = min(boxes[i][4], boxes[j][4]) - max(boxes[i][2], boxes[j][2])
            pairs.append((round(ix*iy), boxes[i][0], boxes[j][0]))

print(f"labels parsed: {len(boxes)}")
print(f"OVERLAPPING LABEL PAIRS: {len(pairs)}")
for area, a, b in sorted(pairs, reverse=True)[:25]:
    print(f"  [{area:6}]  {a}  <->  {b}")
sys.exit(1 if pairs else 0)
