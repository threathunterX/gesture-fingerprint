import math, random

W, H = 1280, 640
random.seed(20260726)

BG = "#0A0D14"
FG = "#E8EDF5"
MUTED = "#7B8794"
ACCENT = "#4DD4C4"      # 真人 / 强调
WARN = "#FF6B5B"        # 机器

parts = []
A = parts.append

A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
A(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

# 细网格
A('<g stroke="#151A24" stroke-width="1">')
for x in range(0, W, 40):
    A(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>')
for y in range(0, H, 40):
    A(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>')
A('</g>')


def human_path(x0, y0, w, h):
    """真人：起终点随机、带自然弯曲、自下而上的滑动轨迹"""
    pad = 0.06
    clamp = lambda v: min(max(v, pad), 1 - pad)
    sxr = clamp(random.uniform(0.12, 0.88))
    exr = clamp(sxr + random.uniform(-0.22, 0.22))
    sx, sy = x0 + w * sxr, y0 + h * random.uniform(0.80, 0.97)
    ex, ey = x0 + w * exr, y0 + h * random.uniform(0.03, 0.22)
    c1x = x0 + w * clamp(sxr + random.uniform(-0.16, 0.16))
    c1y = sy - (sy - ey) * random.uniform(0.28, 0.52)
    c2x = x0 + w * clamp(exr + random.uniform(-0.16, 0.16))
    c2y = ey + (sy - ey) * random.uniform(0.22, 0.46)
    return f'M{sx:.1f},{sy:.1f} C{c1x:.1f},{c1y:.1f} {c2x:.1f},{c2y:.1f} {ex:.1f},{ey:.1f}'


def machine_path(x0, y0, w, h):
    """机器：起终点几乎固定、近乎重合的直线"""
    sx = x0 + w * 0.5 + random.gauss(0, w * 0.010)
    sy = y0 + h * 0.94 + random.gauss(0, h * 0.008)
    ex = x0 + w * 0.5 + random.gauss(0, w * 0.012)
    ey = y0 + h * 0.08 + random.gauss(0, h * 0.008)
    mx = (sx + ex) / 2 + random.gauss(0, w * 0.006)
    my = (sy + ey) / 2
    return f'M{sx:.1f},{sy:.1f} Q{mx:.1f},{my:.1f} {ex:.1f},{ey:.1f}'


PANEL_X, PANEL_W = 742, 452
P1_Y, P2_Y, PANEL_H = 96, 356, 190

A('<defs>')
for i, py in enumerate([P1_Y, P2_Y]):
    A(f'<clipPath id="clip{i}"><rect x="{PANEL_X}" y="{py}" '
      f'width="{PANEL_W}" height="{PANEL_H}" rx="6"/></clipPath>')
A('</defs>')

for i, (py, fn, color, n) in enumerate([
    (P1_Y, human_path, ACCENT, 52),
    (P2_Y, machine_path, WARN, 52),
]):
    A(f'<rect x="{PANEL_X}" y="{py}" width="{PANEL_W}" height="{PANEL_H}" '
      f'rx="6" fill="#0E131C" stroke="#1E2632" stroke-width="1"/>')
    A(f'<g clip-path="url(#clip{i})" fill="none" stroke="{color}" '
      f'stroke-width="1.6" stroke-linecap="round">')
    for _ in range(n):
        A(f'<path d="{fn(PANEL_X, py, PANEL_W, PANEL_H)}" opacity="{random.uniform(0.30, 0.62):.2f}"/>')
    A('</g>')

FONT = "PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif"

# 面板标签
A(f'<text x="{PANEL_X+16}" y="{P1_Y-14}" font-family="{FONT}" font-size="19" '
  f'font-weight="600" fill="{ACCENT}">真人 · 250 次滑动</text>')
A(f'<text x="{PANEL_X+16}" y="{P2_Y-14}" font-family="{FONT}" font-size="19" '
  f'font-weight="600" fill="{WARN}">机器 · 250 次滑动</text>')

# 左侧文字
X = 72
A(f'<text x="{X}" y="128" font-family="{FONT}" font-size="17" font-weight="600" '
  f'fill="{MUTED}" letter-spacing="3">THREATHUNTER · OPEN SOURCE</text>')

A(f'<text x="{X}" y="228" font-family="{FONT}" font-size="52" font-weight="700" '
  f'fill="{FG}">不只判断「是不是人」</text>')
A(f'<text x="{X}" y="300" font-family="{FONT}" font-size="52" font-weight="700" '
  f'fill="{ACCENT}">还判断是「哪一种机器」</text>')

A(f'<line x1="{X}" y1="348" x2="{X+96}" y2="348" stroke="{ACCENT}" stroke-width="4"/>')

A(f'<text x="{X}" y="404" font-family="{FONT}" font-size="25" fill="#B4C0CE">'
  f'9 个行为维度 · 10 类工具 · 7.5 万条真实手势</text>')
A(f'<text x="{X}" y="446" font-family="{FONT}" font-size="25" fill="#B4C0CE">'
  f'从 61.9 元的电容点击器，到 1535 元的机械臂</text>')

A(f'<text x="{X}" y="546" font-family="{FONT}" font-size="34" font-weight="700" '
  f'fill="{FG}">gesture-fingerprint</text>')
A(f'<text x="{X}" y="580" font-family="{FONT}" font-size="18" fill="{MUTED}">'
  f'human vs. script vs. cheating hardware · Apache-2.0</text>')

A('</svg>')

open("social-preview.svg", "w", encoding="utf-8").write("\n".join(parts))
print("written")
