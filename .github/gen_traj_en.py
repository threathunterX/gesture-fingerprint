"""Render English-labelled swipe-trajectory overlays from the blind-test CSVs.

Pure stdlib -> SVG; rendered to PNG with headless Chrome (see render_traj_en.sh).
"""
import csv, sys
from collections import defaultdict

DATA = "repo/人工测试数据/"
PANELS = [
    ("touch_20260724_193514", "Human", "#1f9d8f"),
    ("touch_20260724_194817", "Robotic arm", "#c2410c"),
    ("touch_20260724_194050", "Mouse clicker", "#7c3aed"),
    ("touch_20260724_194625", "Screen-recording script", "#dc2626"),
]

# Shared coordinate frame so panels are visually comparable.
X0, X1, Y0, Y1 = 0, 1080, 0, 1400
W, H = 430, 560                      # panel drawing box
PAD_L, PAD_R, PAD_T, PAD_B = 62, 18, 54, 52
FONT = "-apple-system, Helvetica Neue, Arial, sans-serif"


def load(stem):
    rows = list(csv.DictReader(open(f"{DATA}{stem}_trajectory.csv", encoding="utf-8-sig")))
    g = defaultdict(list)
    for r in rows:
        try:
            g[r["gesture_index"]].append((float(r["x"]), float(r["y"]), int(r["point_index"])))
        except (ValueError, KeyError):
            continue
    for k in g:
        g[k].sort(key=lambda p: p[2])
    return list(g.values())


def panel(x_off, stem, title, colour, align=False):
    strokes = load(stem)
    if align:
        # Translate every stroke so it starts at a common origin: isolates SHAPE
        # from where on the screen the gesture happened (capture tasks differed).
        cx, cy = (X0 + X1) / 2, Y1 * 0.80
        strokes = [[(x - s[0][0] + cx, y - s[0][1] + cy, i) for x, y, i in s]
                   for s in strokes if s]
    sx = lambda x: x_off + PAD_L + (x - X0) / (X1 - X0) * W
    sy = lambda y: PAD_T + (y - Y0) / (Y1 - Y0) * H
    o = []
    o.append(f'<rect x="{x_off+PAD_L}" y="{PAD_T}" width="{W}" height="{H}" '
             f'fill="#fdfdfd" stroke="#d4d4d8" stroke-width="1"/>')
    # grid
    for gx in range(200, X1, 200):
        o.append(f'<line x1="{sx(gx):.1f}" y1="{PAD_T}" x2="{sx(gx):.1f}" y2="{PAD_T+H}" '
                 f'stroke="#eeeef1" stroke-width="1"/>')
        o.append(f'<text x="{sx(gx):.1f}" y="{PAD_T+H+18}" font-family="{FONT}" font-size="11" '
                 f'fill="#8b8b93" text-anchor="middle">{gx}</text>')
    for gy in range(200, Y1, 200):
        o.append(f'<line x1="{x_off+PAD_L}" y1="{sy(gy):.1f}" x2="{x_off+PAD_L+W}" y2="{sy(gy):.1f}" '
                 f'stroke="#eeeef1" stroke-width="1"/>')
        o.append(f'<text x="{x_off+PAD_L-8}" y="{sy(gy)+4:.1f}" font-family="{FONT}" font-size="11" '
                 f'fill="#8b8b93" text-anchor="end">{gy}</text>')
    # trajectories
    o.append(f'<g fill="none" stroke="{colour}" stroke-width="1.5" stroke-linecap="round" '
             f'stroke-linejoin="round" opacity="0.34">')
    for st in strokes:
        if len(st) < 2:
            continue
        d = "M" + " L".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y, _ in st)
        o.append(f'<path d="{d}"/>')
    o.append("</g>")
    o.append(f'<text x="{x_off+PAD_L}" y="{PAD_T-30}" font-family="{FONT}" font-size="17" '
             f'font-weight="600" fill="#18181b">{title}</text>')
    o.append(f'<text x="{x_off+PAD_L}" y="{PAD_T-11}" font-family="{FONT}" font-size="12.5" '
             f'fill="#71717a">{len(strokes)} swipes overlaid</text>')
    o.append(f'<text x="{x_off+PAD_L+W/2}" y="{PAD_T+H+40}" font-family="{FONT}" font-size="12" '
             f'fill="#52525b" text-anchor="middle">X (px)</text>')
    return "\n".join(o)


def build(panels, out, align=False):
    pw = PAD_L + W + PAD_R
    total_w, total_h = pw * len(panels), PAD_T + H + PAD_B
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{total_h}" '
             f'viewBox="0 0 {total_w} {total_h}"><rect width="{total_w}" height="{total_h}" fill="white"/>']
    for i, (stem, title, colour) in enumerate(panels):
        parts.append(panel(i * pw, stem, title, colour, align))
    parts.append(f'<text x="16" y="{PAD_T+H/2}" font-family="{FONT}" font-size="12" fill="#52525b" '
                 f'transform="rotate(-90 16 {PAD_T+H/2})" text-anchor="middle">Y (px)</text>')
    parts.append("</svg>")
    open(out, "w", encoding="utf-8").write("\n".join(parts))
    print(f"  {out}  {total_w}x{total_h}  ({len(panels)} panels)")


if __name__ == "__main__":
    build(PANELS, "traj_en_all.svg")
    build(PANELS, "traj_en_shape.svg", align=True)
