#!/usr/bin/env python3
"""Convert Excalidraw JSON to SVG — minimal faithful render"""

import json, math

IN = "E:/MyCodeProjects/Claude工具全景导航图.excalidraw"
OUT = "E:/MyCodeProjects/Claude工具全景导航图.svg"

with open(IN, "r", encoding="utf-8") as f:
    scene = json.load(f)

els = scene["elements"]

# Find bounding box
xs, ys = [], []
for e in els:
    if e["type"] == "text":
        xs += [e["x"], e["x"] + e["width"]]
        ys += [e["y"], e["y"] + e["height"]]
    elif e["type"] == "rectangle":
        xs += [e["x"], e["x"] + e["width"]]
        ys += [e["y"], e["y"] + e["height"]]
    elif e["type"] == "arrow":
        xs += [e["x"], e["x"] + e["width"]]
        ys += [e["y"], e["y"] + e["height"]]

min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)
W = max_x - min_x + 80
H = max_y - min_y + 80
PAD = 40

def _esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def _round_rect_path(x, y, w, h, r=6):
    r = min(r, w/2, h/2)
    if r <= 0:
        return f"M{x},{y}h{w}v{h}h{-w}z"
    return (f"M{x+r},{y}h{w-2*r},{r}a{r},{r}0,0,1,{r},{r}v{h-2*r}"
            f"a{r},{r}0,0,1,{-r},{r}h{-w+2*r}a{r},{r}0,0,1,{-r},{-r}v{-h+2*r}"
            f"a{r},{r}0,0,1,{r},{-r}z")

svg_parts = []
svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x-PAD} {min_y-PAD} {W} {H}" style="background:#f8f9fa;font-family:system-ui,sans-serif">')
svg_parts.append(f'<rect x="{min_x-PAD}" y="{min_y-PAD}" width="{W}" height="{H}" fill="#f8f9fa"/>')

# Sort: rectangles first, then arrows, then text (text on top)
sorted_els = sorted(els, key=lambda e: {"rectangle": 0, "arrow": 1, "text": 2}.get(e["type"], 3))

for e in sorted_els:
    t = e["type"]
    if t == "rectangle":
        x, y, w, h = e["x"], e["y"], e["width"], e["height"]
        stroke = e.get("strokeColor", "#1971c2")
        bg = e.get("backgroundColor", "transparent")
        sw = e.get("strokeWidth", 2)
        r = 6
        if e.get("roundness"):
            r = 8
        fill_attr = f'fill="{bg}"' if bg and bg != "transparent" else 'fill="none"'
        svg_parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'rx="{r}" ry="{r}" '
            f'{fill_attr} stroke="{stroke}" stroke-width="{sw}" opacity="{e.get("opacity",100)/100}"/>'
        )
    elif t == "arrow":
        x1, y1 = e["x"], e["y"]
        pts = e.get("points", [])
        if pts:
            # First point is [0,0], last point is the arrow end
            x2 = x1 + pts[-1][0]
            y2 = y1 + pts[-1][1]
        else:
            x2 = x1 + e["width"]
            y2 = y1 + e["height"]
        stroke = e.get("strokeColor", "#1971c2")
        sw = e.get("strokeWidth", 2)
        end_arrow = e.get("endArrowhead") == "arrow"
        svg_parts.append(f'<defs><marker id="a{e["id"]}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{stroke}"/></marker></defs>')
        marker = f'marker-end="url(#a{e["id"]})"' if end_arrow else ""
        svg_parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" {marker}/>')
    elif t == "text":
        x, y = e["x"], e["y"]
        w, h = e["width"], e["height"]
        txt = e.get("text", "")
        fs = e.get("fontSize", 16)
        color = e.get("strokeColor", "#1e1e1e")
        align = e.get("textAlign", "left")
        valign = e.get("verticalAlign", "top")
        ff = e.get("fontFamily", 2)
        font_map = {1: "Virgil, Comic Sans MS, cursive", 2: "system-ui, sans-serif", 3: "Cascadia Code, monospace"}
        font_fam = font_map.get(ff, "system-ui, sans-serif")

        lines = txt.split("\n")
        line_h = fs * 1.25
        # Calculate starting Y based on vertical align
        total_h = len(lines) * line_h
        if valign == "middle":
            base_y = y + (h - total_h) / 2 + fs * 0.9
        elif valign == "bottom":
            base_y = y + h - total_h + fs * 0.9
        else:
            base_y = y + fs * 0.9

        # Text anchor
        anchor = {"left": "start", "center": "middle", "right": "end"}.get(align, "start")
        text_x = x if align == "left" else (x + w/2 if align == "center" else x + w)

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            # Bold detection if line starts with **
            fw = "bold" if line.startswith("**") else "normal"
            svg_parts.append(
                f'<text x="{text_x}" y="{base_y + i*line_h}" '
                f'font-size="{fs}" font-family="{font_fam}" '
                f'font-weight="{fw}" fill="{color}" '
                f'text-anchor="{anchor}">{_esc(line)}</text>'
            )

svg_parts.append("</svg>")

svg_content = "\n".join(svg_parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"[OK] SVG: {OUT}")
print(f"     Size: {len(svg_content)} bytes")
print(f"     BBox: {min_x-PAD},{min_y-PAD} to {min_x-PAD+W},{min_y-PAD+H}")
