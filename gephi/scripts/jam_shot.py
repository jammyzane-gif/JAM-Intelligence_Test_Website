#!/usr/bin/env python3
"""Stdlib-only Chrome DevTools Protocol screenshot tool."""
import json, os, socket, struct, base64, subprocess, time, sys, urllib.request, hashlib

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9355
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "/tmp/shots"
os.makedirs(OUTDIR, exist_ok=True)

# captures: (url, out_name, width, height, full_page, scroll_y)
CAPTURES = [
    ("http://localhost:3000/insight.html?id=ai-marathon",        "art-marathon-hero.png", 1440, 900, False, 0),
    ("http://localhost:3000/insight.html?id=ai-marathon",        "art-marathon-full.png", 1440, 1000, True, 0),
    ("http://localhost:3000/insight.html?id=london-ai-value-chain","art-london-full.png", 1440, 1000, True, 0),
    ("http://localhost:3000/insight.html?id=energy-beneath-ai",  "art-energy-full.png",  1440, 1000, True, 0),
    ("http://localhost:3000/index.html",                          "index-insights.png",   1440, 900, False, 3100),
]

def launch():
    prof = "/tmp/jam_chrome_prof"
    p = subprocess.Popen([CHROME, "--headless=new", f"--remote-debugging-port={PORT}",
        f"--user-data-dir={prof}", "--no-first-run", "--no-default-browser-check",
        "--hide-scrollbars", "--force-device-scale-factor=1", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        try:
            urllib.request.urlopen(f"http://localhost:{PORT}/json/version", timeout=1); return p
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("chrome did not start")

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
    def _frame(self):
        while True:
            while len(self.buf) < 2:
                self.buf += self.sock.recv(65536)
            b1, b2 = self.buf[0], self.buf[1]; ln = b2 & 0x7f; idx = 2
            if ln == 126:
                while len(self.buf) < 4: self.buf += self.sock.recv(65536)
                ln = struct.unpack(">H", self.buf[2:4])[0]; idx = 4
            elif ln == 127:
                while len(self.buf) < 10: self.buf += self.sock.recv(65536)
                ln = struct.unpack(">Q", self.buf[2:10])[0]; idx = 10
            while len(self.buf) < idx + ln: self.buf += self.sock.recv(65536)
            payload = self.buf[idx:idx+ln]; self.buf = self.buf[idx+ln:]
            return payload
    def wait(self, sid):
        while True:
            msg = json.loads(self._frame().decode("utf-8", "replace"))
            if msg.get("id") == sid: return msg

def main():
    proc = launch()
    try:
        info = json.loads(urllib.request.urlopen(f"http://localhost:{PORT}/json").read())
        page = next(t for t in info if t["type"] == "page")
        ws = WS(page["webSocketDebuggerUrl"])
        ws.wait(ws.send("Page.enable")); ws.wait(ws.send("Runtime.enable"))
        for url, name, w, h, full, scy in CAPTURES:
            ws.wait(ws.send("Emulation.setDeviceMetricsOverride",
                {"width": w, "height": h, "deviceScaleFactor": 1, "mobile": False}))
            ws.wait(ws.send("Page.navigate", {"url": url}))
            time.sleep(1.8)
            # force reveal elements visible, kill animations
            ws.wait(ws.send("Runtime.evaluate", {"expression":
                "document.querySelectorAll('.reveal').forEach(e=>{e.style.opacity='1';e.style.transform='none';e.style.transition='none';});"
                "document.querySelectorAll('.art-nebula').forEach(e=>e.style.animation='none');true",
                "awaitPromise": False}))
            if scy:
                ws.wait(ws.send("Runtime.evaluate", {"expression": f"window.scrollTo(0,{scy});true"}))
                time.sleep(0.5)
            params = {"format": "png", "captureBeyondViewport": True}
            if full:
                m = ws.wait(ws.send("Runtime.evaluate", {"expression":
                    "JSON.stringify({h:document.body.scrollHeight})"}))
                bh = json.loads(m["result"]["result"]["value"])["h"]
                bh = min(bh, 14000)
                ws.wait(ws.send("Emulation.setDeviceMetricsOverride",
                    {"width": w, "height": bh, "deviceScaleFactor": 1, "mobile": False}))
                time.sleep(0.4)
            r = ws.wait(ws.send("Page.captureScreenshot", params))
            data = base64.b64decode(r["result"]["data"])
            out = os.path.join(OUTDIR, name)
            with open(out, "wb") as f: f.write(data)
            print(f"{name}: {len(data)//1024}KB  sha={hashlib.md5(data).hexdigest()[:8]}")
    finally:
        proc.terminate()

if __name__ == "__main__":
    main()
