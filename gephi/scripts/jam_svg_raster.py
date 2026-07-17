#!/usr/bin/env python3
"""Rasterise a transparent SVG to a fixed-size transparent PNG via headless
Chrome's one-shot --screenshot mode (the old CDP-websocket approach broke with
Chrome 149). Stdlib only.

Usage: jam_svg_raster.py [svg] [out.png] [width] [height]
"""
import os, subprocess, sys, tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SVG = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Desktop/JAM-Intelligence/jam_ai_landscape_network.svg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/Desktop/JAM-Intelligence/jam_ai_landscape_network_4k.png")
W = int(sys.argv[3]) if len(sys.argv) > 3 else 3840
H = int(sys.argv[4]) if len(sys.argv) > 4 else 2160

def main():
    svg = open(SVG, encoding="utf-8").read()
    svg = svg[svg.find("<svg"):]  # drop xml/doctype prolog
    html = ("<!doctype html><html><head><meta charset='utf-8'><style>"
            "html,body{margin:0;padding:0;background:transparent}"
            f"svg{{display:block;width:{W}px;height:{H}px}}</style></head><body>" + svg + "</body></html>")
    html_path = os.path.join(tempfile.gettempdir(), "jam_svg_wrap.html")
    open(html_path, "w", encoding="utf-8").write(html)

    out_abs = os.path.abspath(OUT)
    # NOTE: no --user-data-dir — Chrome 149's one-shot headless mode hangs
    # until timeout when given a custom profile dir, but completes in ~5s
    # with its own ephemeral profile (verified 17 Jul 2026).
    r = subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
        "--no-default-browser-check", "--hide-scrollbars",
        "--force-device-scale-factor=1", "--default-background-color=00000000",
        f"--window-size={W},{H}",
        f"--screenshot={out_abs}", "file://" + html_path,
    ], capture_output=True, text=True, timeout=120)
    if not os.path.exists(out_abs) or os.path.getsize(out_abs) == 0:
        sys.stderr.write(r.stderr[-2000:] + "\n")
        sys.exit(f"chrome produced no screenshot at {out_abs}")
    print(f"wrote {out_abs}  ({os.path.getsize(out_abs)//1024} KB, {W}x{H})")

if __name__ == "__main__":
    main()
