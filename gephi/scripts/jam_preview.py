#!/usr/bin/env python3
"""Composite the 4K transparent PNG over dark and white backgrounds at half-res for inspection."""
import struct, zlib, os
D = os.path.expanduser("~/Desktop/JAM-Intelligence")
SRC = os.path.join(D, "jam_ai_landscape_network_4k.png")

def readpng(fn):
    d = open(fn, 'rb').read(); i = 8; idat = b''
    while i < len(d):
        ln = struct.unpack('>I', d[i:i+4])[0]; t = d[i+4:i+8]; dat = d[i+8:i+8+ln]
        if t == b'IHDR': W, H, bd, ct = struct.unpack('>IIBB', dat[:10])
        elif t == b'IDAT': idat += dat
        elif t == b'IEND': break
        i += 12 + ln
    raw = zlib.decompress(idat); ch = 4; stride = W*ch
    out = bytearray(W*H*ch); prev = bytearray(stride); pos = 0
    def pae(a, b, c):
        p = a+b-c; pa = abs(p-a); pb = abs(p-b); pc = abs(p-c)
        return a if pa <= pb and pa <= pc else (b if pb <= pc else c)
    for y in range(H):
        ft = raw[pos]; pos += 1; line = bytearray(raw[pos:pos+stride]); pos += stride
        for x in range(stride):
            a = line[x-ch] if x >= ch else 0; b = prev[x]; c = prev[x-ch] if x >= ch else 0
            if ft == 1: line[x] = (line[x]+a) & 255
            elif ft == 2: line[x] = (line[x]+b) & 255
            elif ft == 3: line[x] = (line[x]+((a+b) >> 1)) & 255
            elif ft == 4: line[x] = (line[x]+pae(a, b, c)) & 255
        out[y*stride:(y+1)*stride] = line; prev = line
    return W, H, out

def writepng(fn, W, H, rgb):
    stride = W*3; raw = bytearray()
    for y in range(H): raw.append(0); raw += rgb[y*stride:(y+1)*stride]
    comp = zlib.compress(bytes(raw), 6)
    def ch(t, d): return struct.pack('>I', len(d))+t+d+struct.pack('>I', zlib.crc32(t+d) & 0xffffffff)
    open(fn, 'wb').write(b'\x89PNG\r\n\x1a\n' +
        ch(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)) + ch(b'IDAT', comp) + ch(b'IEND', b''))

W, H, px = readpng(SRC)
sc = 2; NW, NH = W//sc, H//sc
for bg, name in [((12, 12, 14), "_preview_dark.png"), ((255, 255, 255), "_preview_white.png")]:
    out = bytearray(NW*NH*3)
    for y in range(NH):
        for x in range(NW):
            o = ((y*sc)*W + x*sc)*4; r, g, b, a = px[o], px[o+1], px[o+2], px[o+3]; af = a/255
            j = (y*NW + x)*3
            out[j] = int(r*af + bg[0]*(1-af)); out[j+1] = int(g*af + bg[1]*(1-af)); out[j+2] = int(b*af + bg[2]*(1-af))
    writepng(os.path.join(D, name), NW, NH, out)
print("previews written")
