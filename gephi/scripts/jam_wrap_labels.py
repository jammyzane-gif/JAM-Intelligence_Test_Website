#!/usr/bin/env python3
"""Rewrite the exported network SVG: any node label longer than 15 chars is
wrapped onto two centred lines (split at the last space) using <tspan>s, which
shrinks its horizontal footprint. Operates in place on the SVG file."""
import re, sys, os, html

SVG = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/Desktop/JAM-Intelligence/jam_ai_landscape_network.svg")
MAXLEN = 15

s = open(SVG).read()

def wrap(m):
    open_tag, body, close = m.group(1), m.group(2), m.group(3)
    text = html.unescape(body).strip()
    if len(text) <= MAXLEN or " " not in text:
        return m.group(0)
    cut = text.rfind(" ")               # split at last space -> last word on line 2
    l1, l2 = text[:cut].rstrip(), text[cut+1:].lstrip()
    xm = re.search(r'\bx="([^"]+)"', open_tag)
    x = xm.group(1) if xm else "0"
    esc = lambda t: t.replace("&", "&amp;").replace("<", "&lt;")
    inner = (f'<tspan x="{x}" dy="-0.45em">{esc(l1)}</tspan>'
             f'<tspan x="{x}" dy="1.05em">{esc(l2)}</tspan>')
    return open_tag + inner + close

new = re.sub(r'(<text\b[^>]*>)(.*?)(</text>)', wrap, s, flags=re.S)
open(SVG, "w").write(new)
print(f"wrapped labels >{MAXLEN} chars in {os.path.basename(SVG)}")
