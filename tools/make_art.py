#!/usr/bin/env python3
"""Generate the studio's abstract cover plates as SVG.

Every project cover is original geometric artwork built from a seeded
composition, so the grid reads as a designed body of work without stock
photography. Re-run after editing a palette:  python3 tools/make_art.py
"""
import math
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "img")

# slug, composition, (background, ink, accent)
PROJECTS = [
    ("hollow-sound",   "arcs",    ("#101014", "#f4f2ed", "#ff4b1f")),
    ("meridian-type",  "letter",  ("#f4f2ed", "#0b0b0c", "#2b4cff")),
    ("northbound",     "waves",   ("#123227", "#eae6da", "#d8ff3e")),
    ("atlas-athletic", "stripes", ("#0b0b0c", "#f4f2ed", "#ff4b1f")),
    ("verso-press",    "blocks",  ("#e7e2d6", "#141416", "#c8462c")),
    ("field-notes",    "halftone",("#1b1440", "#f0ecff", "#ff9ecd")),
    ("kestrel-bank",   "grid",    ("#f0efeb", "#0b0b0c", "#0f6b4f")),
    ("salt-and-ash",   "rings",   ("#211a16", "#f2e9dd", "#e07a3c")),
]

def head(w, h, bg):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img">'
            f'<rect width="{w}" height="{h}" fill="{bg}"/>')

def arcs(w, h, ink, acc, rnd):
    p, cx, cy = [], w * 0.5, h * 0.52
    for i in range(9):
        r = (i + 1) * (min(w, h) * 0.055)
        col = acc if i % 3 == 2 else ink
        start, sweep = rnd.choice([(180, 180), (0, 180), (200, 140), (330, 200)])
        a0, a1 = math.radians(start), math.radians(start + sweep)
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        large = 1 if sweep > 180 else 0
        p.append(f'<path d="M{x0:.1f} {y0:.1f} A{r:.1f} {r:.1f} 0 {large} 1 {x1:.1f} {y1:.1f}" '
                 f'fill="none" stroke="{col}" stroke-width="{max(2, w*0.012):.1f}" stroke-linecap="round"/>')
    return "".join(p)

def letter(w, h, ink, acc, rnd):
    fs = min(w * 0.6, h * 0.62)
    return (f'<circle cx="{w*0.72:.0f}" cy="{h*0.3:.0f}" r="{min(w,h)*0.17:.0f}" fill="{acc}"/>'
            f'<text x="{w*0.5:.0f}" y="{h*0.68:.0f}" text-anchor="middle" fill="{ink}" '
            f'font-family="Times New Roman, serif" font-size="{fs:.0f}" font-style="italic">Aa</text>')

def waves(w, h, ink, acc, rnd):
    p = []
    for i in range(14):
        y = h * 0.12 + i * (h * 0.058)
        amp = h * 0.035 * (0.4 + i / 14)
        d = f"M0 {y:.1f}"
        for x in range(0, w + 1, max(8, w // 24)):
            d += f" L{x} {y + math.sin(x / w * math.pi * 3 + i * 0.6) * amp:.1f}"
        col = acc if i in (4, 9) else ink
        p.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{max(1.5, w*0.006):.1f}" opacity="{0.35 + i/22:.2f}"/>')
    return "".join(p)

def stripes(w, h, ink, acc, rnd):
    p = [f'<g transform="rotate(-24 {w/2:.0f} {h/2:.0f})">']
    x, i = -h, 0
    while x < w + h:
        bw = rnd.choice([w * 0.02, w * 0.045, w * 0.085])
        col = acc if i % 5 == 0 else ink
        p.append(f'<rect x="{x:.1f}" y="{-h:.0f}" width="{bw:.1f}" height="{h*3:.0f}" fill="{col}" opacity="{0.9 if col==acc else 0.85:.2f}"/>')
        x += bw + rnd.choice([w * 0.03, w * 0.06, w * 0.1])
        i += 1
    p.append("</g>")
    return "".join(p)

def blocks(w, h, ink, acc, rnd):
    p, cols, rows = [], 3, 4
    cw, ch = w / cols, h / rows
    for r in range(rows):
        for c in range(cols):
            if rnd.random() < 0.34:
                continue
            x, y = c * cw, r * ch
            kind = rnd.choice(["sq", "circ", "tri", "half"])
            col = acc if rnd.random() < 0.35 else ink
            m = cw * 0.12
            if kind == "sq":
                p.append(f'<rect x="{x+m:.1f}" y="{y+m:.1f}" width="{cw-2*m:.1f}" height="{ch-2*m:.1f}" fill="{col}"/>')
            elif kind == "circ":
                p.append(f'<circle cx="{x+cw/2:.1f}" cy="{y+ch/2:.1f}" r="{min(cw,ch)/2-m:.1f}" fill="{col}"/>')
            elif kind == "tri":
                p.append(f'<polygon points="{x+m:.1f},{y+ch-m:.1f} {x+cw/2:.1f},{y+m:.1f} {x+cw-m:.1f},{y+ch-m:.1f}" fill="{col}"/>')
            else:
                p.append(f'<path d="M{x+m:.1f} {y+ch-m:.1f} A{cw/2-m:.1f} {cw/2-m:.1f} 0 0 1 {x+cw-m:.1f} {y+ch-m:.1f} Z" fill="{col}"/>')
    return "".join(p)

def halftone(w, h, ink, acc, rnd):
    p, cols, rows = [], 12, 15
    for r in range(rows):
        for c in range(cols):
            t = r / rows
            rad = (w / cols) * 0.5 * (0.16 + t * 0.92)
            col = acc if (r + c) % 9 == 0 else ink
            p.append(f'<circle cx="{(c+0.5)*w/cols:.1f}" cy="{(r+0.5)*h/rows:.1f}" r="{rad:.1f}" fill="{col}" opacity="{0.3+t*0.7:.2f}"/>')
    return "".join(p)

def grid(w, h, ink, acc, rnd):
    p, n = [], 7
    cw, ch = w / n, h / (n + 2)
    for r in range(n + 2):
        for c in range(n):
            x, y = (c + 0.5) * cw, (r + 0.5) * ch
            s = min(cw, ch) * 0.34
            rot = rnd.choice([0, 15, 30, 45])
            col = acc if rnd.random() < 0.14 else ink
            p.append(f'<rect x="{x-s:.1f}" y="{y-s:.1f}" width="{s*2:.1f}" height="{s*2:.1f}" fill="none" '
                     f'stroke="{col}" stroke-width="{max(1, w*0.004):.1f}" transform="rotate({rot} {x:.1f} {y:.1f})" opacity="0.8"/>')
    return "".join(p)

def rings(w, h, ink, acc, rnd):
    p = []
    for i in range(5):
        cx = w * (0.28 + 0.11 * i)
        cy = h * (0.32 + 0.08 * i)
        r = min(w, h) * (0.3 - i * 0.03)
        col = acc if i == 2 else ink
        p.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{col}" '
                 f'stroke-width="{max(2, w*0.018):.1f}" opacity="{0.5 + i*0.11:.2f}"/>')
    return "".join(p)

DRAW = {"arcs": arcs, "letter": letter, "waves": waves, "stripes": stripes,
        "blocks": blocks, "halftone": halftone, "grid": grid, "rings": rings}

def build(slug, kind, palette, w, h, seed_extra=""):
    bg, ink, acc = palette
    rnd = random.Random(slug + kind + seed_extra)
    return head(w, h, bg) + DRAW[kind](w, h, ink, acc, rnd) + "</svg>"

def main():
    os.makedirs(OUT, exist_ok=True)
    made = 0
    for slug, kind, palette in PROJECTS:
        for name, w, h, extra in (("", 800, 1000, ""), ("-wide", 1600, 1000, "w")):
            path = os.path.join(OUT, f"{slug}{name}.svg")
            with open(path, "w") as fh:
                fh.write(build(slug, kind, palette, w, h, extra))
            made += 1
    print(f"wrote {made} plates to {os.path.normpath(OUT)}")

if __name__ == "__main__":
    main()
