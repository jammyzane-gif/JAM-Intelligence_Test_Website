#!/usr/bin/env python3
"""Rasterise a transparent SVG to a fixed-size transparent PNG via headless Chrome (CDP). Stdlib only."""
import json, os, socket, struct, base64, subprocess, time, sys, urllib.request

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9356
SVG = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Desktop/JAM-Intelligence/jam_ai_landscape_network.svg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/Desktop/JAM-Intelligence/jam_ai_landscape_network_4k.png")
W = int(sys.argv[3]) if len(sys.argv) > 3 else 3840
H = int(sys.argv[4]) if len(sys.argv) > 4 else 2160

svg = open(SVG, encoding="utf-8").read()
svg = svg[svg.find("<svg"):]  # drop xml/doctype prolog
html = ("<!doctype html><html><head><meta charset='utf-8'><style>"
        "html,body{margin:0;padding:0;background:transparent}"
        f"svg{{display:block;width:{W}px;height:{H}px}}</style></head><body>" + svg + "</body></html>")
HTML_PATH = "/tmp/jam_svg_wrap.html"
open(HTML_PATH, "w", encoding="utf-8").write(html)

def launch():
    prof = "/tmp/jam_chrome_raster_prof"
    p = subprocess.Popen([CHROME, "--headless=new", f"--remote-debugging-port={PORT}",
        f"--user-data-dir={prof}", "--no-first-run", "--no-default-browser-check",
        "--hide-scrollbars", "--force-device-scale-factor=1", "--default-background-color=00000000",
        "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        try:
            urllib.request.urlopen(f"http://localhost:{PORT}/json/version", timeout=1); return p
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("chrome did not start")

def page_ws():
    for _ in range(40):
        try:
            info = json.loads(urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=2).read())
            for t in info:
                if t.get("type") == "page":
                    return t["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(0.25)
    # fall back to creating one
    req = urllib.request.Request(f"http://localhost:{PORT}/json/new?file://{HTML_PATH}", method="PUT")
    return json.loads(urllib.request.urlopen(req, timeout=5).read())["webSocketDebuggerUrl"]

class WS:
    def __init__(self, url):
        h = url.split("://")[1]; host, rest = h.split(":"); port, path = rest.split("/", 1)
        self.sock = socket.create_connection((host, int(port)))
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET /{path} HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\n"
               f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.sock.sendall(req.encode())
        data = b""
        while b"\r\n\r\n" not in data: data += self.sock.recv(4096)
        self.buf = data.split(b"\r\n\r\n", 1)[1]; self._id = 0
    def send(self, method, params=None):
        self._id += 1
        payload = json.dumps({"id": self._id, "method": method, "params": params or {}}).encode()
        hdr = bytearray([0x81]); n = len(payload); mask = os.urandom(4)
        if n < 126: hdr.append(0x80 | n)
        elif n < 65536: hdr.append(0x80 | 126); hdr += struct.pack(">H", n)
        else: hdr.append(0x80 | 127); hdr += struct.pack(">Q", n)
        hdr += mask; masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(hdr) + masked); return self._id
    def _raw_frame(self):
        while len(self.buf) < 2: self.buf += self.sock.recv(1 << 20)
        b1 = self.buf[0]; b2 = self.buf[1]; fin = b1 & 0x80; ln = b2 & 0x7f; idx = 2
        if ln == 126:
            while len(self.buf) < 4: self.buf += self.sock.recv(1 << 20)
            ln = struct.unpack(">H", self.buf[2:4])[0]; idx = 4
        elif ln == 127:
            while len(self.buf) < 10: self.buf += self.sock.recv(1 << 20)
            ln = struct.unpack(">Q", self.buf[2:10])[0]; idx = 10
        while len(self.buf) < idx + ln: self.buf += self.sock.recv(1 << 20)
        payload = self.buf[idx:idx+ln]; self.buf = self.buf[idx+ln:]
        return fin, payload
    def _frame(self):
        # reassemble fragmented messages (continuation frames)
        fin, payload = self._raw_frame()
        while not fin:
            f2, p2 = self._raw_frame(); payload += p2; fin = f2
        return payload
    def wait(self, sid):
        while True:
            msg = json.loads(self._frame().decode("utf-8", "replace"))
            if msg.get("id") == sid: return msg

def main():
    proc = launch()
    try:
        ws = WS(page_ws())
        ws.wait(ws.send("Page.enable")); ws.wait(ws.send("Runtime.enable"))
        ws.wait(ws.send("Emulation.setDeviceMetricsOverride",
            {"width": W, "height": H, "deviceScaleFactor": 1, "mobile": False}))
        ws.wait(ws.send("Emulation.setDefaultBackgroundColorOverride",
            {"color": {"r": 0, "g": 0, "b": 0, "a": 0}}))
        ws.wait(ws.send("Page.navigate", {"url": "file://" + HTML_PATH}))
        time.sleep(2.0)
        r = ws.wait(ws.send("Page.captureScreenshot",
            {"format": "png", "captureBeyondViewport": False, "fromSurface": True}))
        data = base64.b64decode(r["result"]["data"])
        with open(OUT, "wb") as f: f.write(data)
        print(f"wrote {OUT}  ({len(data)//1024} KB, {W}x{H})")
    finally:
        proc.terminate()

if __name__ == "__main__":
    main()
