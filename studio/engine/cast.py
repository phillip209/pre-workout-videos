"""Reusable pixel-art cast & sets for the channel (all drawn procedurally, original designs).

Characters are drawn at native pixel size into small RGBA sprites, auto-outlined, and can be
pasted at integer scales so the pixel grid stays consistent.
"""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

from . import W, H
from .gfx import P, new, outline, lerpc, vgradient, dither_fill, clamp


# ============================================================ HERO ("Leo")
def hero(pose: dict | None = None) -> Image.Image:
    """Gym-goer, ~40x60 px native. pose keys (all optional):
    arm_l, arm_r: (shoulder_deg, elbow_deg) 0 = hanging down, positive = forward/up
    bicep: 0..1   belly: 0..1   mouth: smile|grin|sad|o|flat|grit   eyes: open|blink|wide|sad|happy|closed
    walk: phase (radians) or None   bob: px   look: -1..1 (pupil offset)   sweat: bool
    holding: None|'dumbbell'   tint_arm: 0..1 (muscle->fat colour on right arm)
    """
    p = {"arm_l": (10, 10), "arm_r": (10, 10), "bicep": 0.5, "belly": 0.0, "mouth": "smile",
         "eyes": "open", "walk": None, "bob": 0, "look": 0, "sweat": False, "holding": None,
         "tint_arm": 0.0, "droop": 0.0}
    if pose:
        p.update(pose)
    S = new(56, 72)
    d = ImageDraw.Draw(S)
    cx = 28
    by = 70 - int(p["bob"])          # feet line
    hip = by - 18
    sh_y = hip - 18                   # shoulder line
    # ---- legs
    ph = p["walk"]
    for side, sgn in ((-1, 1), (1, -1)):
        off = int(round(math.sin(ph) * 3 * sgn)) if ph is not None else 0
        lift = max(0, int(round(math.sin(ph) * 2 * sgn))) if ph is not None else 0
        x = cx + side * 4
        d.rectangle([x - 2, hip, x + 2, hip + 7], fill=P["shorts"])
        d.rectangle([x - 2 + off, hip + 7, x + 1 + off, by - 3 - lift], fill=P["skin"])
        d.rectangle([x - 3 + off, by - 3 - lift, x + 3 + off, by - 1 - lift], fill=P["shoe"])
    # ---- torso (tank top) + belly
    bel = clamp(p["belly"])
    tw = 9 + int(bel * 3)
    d.rounded_rectangle([cx - tw, sh_y, cx + tw, hip + 2], radius=3, fill=P["tank"])
    d.rectangle([cx - tw, sh_y + 2, cx - tw + 1, hip], fill=P["tank_d"])
    if bel > 0.05:
        r = 3 + int(bel * 6)
        d.ellipse([cx - r - 1, hip - 6 - r, cx + r + 1, hip - 6 + r + 2], fill=P["tank"])
        d.arc([cx - r - 1, hip - 6 - r, cx + r + 1, hip - 6 + r + 2], 20, 160, fill=P["tank_d"])
    d.line([cx - 4, sh_y, cx, sh_y + 4, cx + 4, sh_y], fill=P["skin"], width=2)  # neckline
    # ---- head
    hy = sh_y - 15 + int(p["droop"] * 2)
    d.rectangle([cx - 2, sh_y - 3, cx + 2, sh_y + 1], fill=P["skin_d"])      # neck
    d.rounded_rectangle([cx - 8, hy, cx + 8, hy + 14], radius=4, fill=P["skin"])
    d.rectangle([cx - 8, hy + 9, cx - 7, hy + 12], fill=P["skin_d"])
    # hair (spiky top)
    d.rounded_rectangle([cx - 9, hy - 2, cx + 9, hy + 4], radius=3, fill=P["hair"])
    for i, hx in enumerate(range(cx - 8, cx + 8, 4)):
        d.polygon([(hx, hy - 1), (hx + 2, hy - 4 - (i % 2)), (hx + 4, hy - 1)], fill=P["hair"])
    d.rectangle([cx + 6, hy + 2, cx + 8, hy + 6], fill=P["hair"])
    # headband
    d.rectangle([cx - 8, hy + 3, cx + 8, hy + 4], fill=P["red"])
    # eyes
    ex = int(round(p["look"] * 1))
    ey = hy + 7
    e = p["eyes"]
    for sx in (cx - 4, cx + 3):
        if e in ("blink", "closed"):
            d.line([sx - 1, ey + 1, sx + 1, ey + 1], fill=P["ink"])
        elif e == "happy":
            d.line([sx - 1, ey + 1, sx, ey, sx + 1, ey + 1], fill=P["ink"])
        elif e == "wide":
            d.rectangle([sx - 1, ey - 1, sx + 1, ey + 1], fill=P["white"])
            d.point((sx + ex, ey), fill=P["ink"])
        else:
            d.rectangle([sx + ex, ey, sx + ex, ey + 1], fill=P["ink"])
        if e == "sad":
            d.line([sx - 1, ey - 2 + (1 if sx < cx else 0), sx + 1, ey - 2 + (0 if sx < cx else 1)], fill=P["hair"])
    # mouth
    my = hy + 11
    m = p["mouth"]
    if m == "smile":
        d.line([cx - 2, my, cx - 1, my + 1, cx + 1, my + 1, cx + 2, my], fill=P["ink"])
    elif m == "grin":
        d.rectangle([cx - 3, my, cx + 3, my + 1], fill=P["white"])
        d.line([cx - 3, my + 2, cx + 3, my + 2], fill=P["ink"])
    elif m == "sad":
        d.line([cx - 2, my + 1, cx - 1, my, cx + 1, my, cx + 2, my + 1], fill=P["ink"])
    elif m == "o":
        d.rectangle([cx - 1, my - 1, cx + 1, my + 1], fill=P["ink"])
    elif m == "grit":
        d.rectangle([cx - 3, my, cx + 3, my + 1], fill=P["white"])
        d.line([cx - 1, my, cx - 1, my + 1], fill=P["ink"])
        d.line([cx + 1, my, cx + 1, my + 1], fill=P["ink"])
    else:
        d.line([cx - 2, my, cx + 2, my], fill=P["ink"])
    if p["sweat"]:
        d.rectangle([cx + 9, hy + 4, cx + 10, hy + 6], fill=P["sky"])
    # ---- arms
    for side, key in ((-1, "arm_l"), (1, "arm_r")):
        sdeg, edeg = p[key]
        sx, sy = cx + side * (tw + 1), sh_y + 3
        a1 = math.radians(sdeg)
        ux, uy = sx + side * math.sin(a1) * 9, sy + math.cos(a1) * 9
        a2 = math.radians(sdeg + edeg)
        fx, fy = ux + side * math.sin(a2) * 9, uy + math.cos(a2) * 9
        tint = p["tint_arm"] if side == 1 else 0.0
        skin = lerpc(P["skin"], P["fat"], tint)
        skin_d = lerpc(P["skin_d"], P["fat_d"], tint)
        d.line([sx, sy, ux, uy], fill=skin, width=5)
        d.line([ux, uy, fx, fy], fill=skin, width=4)
        d.ellipse([ux - 2, uy - 2, ux + 2, uy + 2], fill=skin)
        # bicep bulge (on the upper arm, towards the elbow)
        b = (p["bicep"] if side == 1 else p["bicep"] * 0.9)
        r = 1.5 + b * 4.0
        mx, my2 = sx + (ux - sx) * 0.55, sy + (uy - sy) * 0.55
        perp = (-(uy - sy), (ux - sx))
        ln = math.hypot(*perp) or 1
        bx = mx + perp[0] / ln * r * 0.6 * (-side)
        byy = my2 + perp[1] / ln * r * 0.6 * (-side)
        d.ellipse([bx - r, byy - r, bx + r, byy + r], fill=skin)
        d.point((int(bx - side), int(byy - r + 1)), fill=lerpc(P["skin_l"], P["fat_l"], tint))
        d.arc([bx - r, byy - r, bx + r, byy + r], 30, 150, fill=skin_d)
        # hand
        d.rectangle([fx - 2, fy - 2, fx + 2, fy + 2], fill=skin)
        if p["holding"] == "dumbbell" and side == 1:
            d.rectangle([fx - 6, fy - 1, fx + 6, fy + 1], fill=P["steel_d"])
            d.rectangle([fx - 8, fy - 4, fx - 5, fy + 4], fill=P["steel"])
            d.rectangle([fx + 5, fy - 4, fx + 8, fy + 4], fill=P["steel"])
    return outline(S)


# ============================================================ MUSCLE FIBER
def muscle_fiber(length=90, thick=22, mood="happy", nuclei=6, glow=0.0, t=0.0, blink=False,
                 dim_nuclei=0.0) -> Image.Image:
    """Long striated capsule with a face and purple nuclei along its edge."""
    L, T = int(length), max(4, int(thick))
    S = new(L + 8, T + 12)
    d = ImageDraw.Draw(S)
    x0, y0 = 4, 6
    d.rounded_rectangle([x0, y0, x0 + L, y0 + T], radius=T // 2, fill=P["muscle"])
    # striations (cross bands) that slide slightly = "alive"
    off = int(t * 6) % 4
    for x in range(x0 + T // 2 + off, x0 + L - T // 2, 4):
        d.line([x, y0 + 2, x, y0 + T - 2], fill=P["muscle_d"])
    d.line([x0 + T // 2, y0 + 1, x0 + L - T // 2, y0 + 1], fill=P["muscle_l"])
    d.line([x0 + T // 2, y0 + T - 1, x0 + L - T // 2, y0 + T - 1], fill=P["muscle_d"])
    # nuclei sit at the edge of the fiber
    if nuclei:
        span = L - T
        for i in range(nuclei):
            nx = x0 + T // 2 + int((i + 0.5) * span / nuclei)
            ny = y0 + (2 if i % 2 == 0 else T - 4)
            col = lerpc(P["nucleus"], P["nucleus_l"], glow * (0.6 + 0.4 * math.sin(t * 6 + i)))
            col = lerpc(col, P["muscle_d"], dim_nuclei)
            d.ellipse([nx - 3, ny - 1, nx + 3, ny + 2], fill=col)
            if glow > 0.3:
                d.point((nx - 1, ny), fill=P["white"])
    # face on the left end
    fx, fy = x0 + T // 2 + 2, y0 + T // 2
    if T >= 10:
        if blink:
            d.line([fx, fy - 2, fx + 2, fy - 2], fill=P["ink"])
            d.line([fx + 6, fy - 2, fx + 8, fy - 2], fill=P["ink"])
        else:
            d.rectangle([fx, fy - 3, fx + 1, fy - 1], fill=P["ink"])
            d.rectangle([fx + 6, fy - 3, fx + 7, fy - 1], fill=P["ink"])
        if mood == "happy":
            d.line([fx + 1, fy + 1, fx + 3, fy + 2, fx + 5, fy + 2, fx + 7, fy + 1], fill=P["ink"])
        elif mood == "sad":
            d.line([fx + 1, fy + 2, fx + 3, fy + 1, fx + 5, fy + 1, fx + 7, fy + 2], fill=P["ink"])
            d.rectangle([fx - 1, fy, fx, fy + 2], fill=P["sky"])
        elif mood == "shock":
            d.rectangle([fx + 3, fy, fx + 5, fy + 2], fill=P["ink"])
        elif mood == "proud":
            d.line([fx + 1, fy + 1, fx + 7, fy + 1], fill=P["ink"])
            d.line([fx - 1, fy - 5, fx + 2, fy - 4], fill=P["ink"])
            d.line([fx + 5, fy - 4, fx + 8, fy - 5], fill=P["ink"])
    else:  # very thin fiber: tiny sad face
        d.point((fx, fy - 1), fill=P["ink"])
        d.point((fx + 4, fy - 1), fill=P["ink"])
    return outline(S)


# ============================================================ FAT CELL
def fat_cell(r=18, mood="happy", t=0.0, wobble=0.0, blink=False) -> Image.Image:
    R = int(r)
    S = new(2 * R + 12, 2 * R + 12)
    d = ImageDraw.Draw(S)
    c = R + 6
    wx = int(round(math.sin(t * 9) * wobble * 2))
    wy = -wx
    d.ellipse([c - R - wx, c - R - wy, c + R + wx, c + R + wy], fill=P["fat"])
    # inner lipid droplet highlight + shadow
    d.ellipse([c - R + 3, c - R + 3, c - R // 3, c - R // 3], fill=P["fat_l"])
    d.arc([c - R - wx, c - R - wy, c + R + wx, c + R + wy], 20, 160, fill=P["fat_d"])
    # squashed nucleus pushed to the edge (real adipocyte feature)
    d.ellipse([c + R - 7, c + 2, c + R - 2, c + 6], fill=P["fat_d"])
    # face
    ex = 4 + R // 6
    ey = c - 1
    if blink:
        d.line([c - ex - 1, ey, c - ex + 1, ey], fill=P["ink"])
        d.line([c + ex - 1, ey, c + ex + 1, ey], fill=P["ink"])
    else:
        d.rectangle([c - ex, ey - 1, c - ex + 1, ey + 1], fill=P["ink"])
        d.rectangle([c + ex - 1, ey - 1, c + ex, ey + 1], fill=P["ink"])
    my = ey + 4
    if mood == "happy":
        d.line([c - 3, my, c - 1, my + 1, c + 1, my + 1, c + 3, my], fill=P["ink"])
    elif mood == "greedy":
        d.ellipse([c - 3, my - 1, c + 3, my + 3], fill=P["ink"])
        d.rectangle([c - 1, my + 1, c + 1, my + 2], fill=P["red"])
    elif mood == "smug":
        d.line([c - 3, my + 1, c + 3, my], fill=P["ink"])
    elif mood == "shock":
        d.rectangle([c - 1, my - 1, c + 1, my + 2], fill=P["ink"])
    d.point((c - ex - 3, ey + 3), fill=P["pink"])
    d.point((c + ex + 3, ey + 3), fill=P["pink"])
    return outline(S)


# ============================================================ PROPS
def mouse(t=0.0, scale_body=1.0) -> Image.Image:
    S = new(28, 20)
    d = ImageDraw.Draw(S)
    d.ellipse([6, 6, 22, 17], fill=P["fog"])
    d.ellipse([16, 2, 22, 8], fill=P["pink"])
    d.ellipse([17, 3, 21, 7], fill=P["fog"])
    d.ellipse([20, 8, 27, 14], fill=P["fog"])
    d.point((24, 10), fill=P["ink"])
    d.point((27, 11), fill=P["pink"])
    tail = int(math.sin(t * 8) * 2)
    d.line([6, 13, 2, 11 + tail, 0, 14], fill=P["pink"])
    return outline(S)


def food(kind: str) -> Image.Image:
    S = new(16, 16)
    d = ImageDraw.Draw(S)
    if kind == "pizza":
        d.polygon([(1, 2), (14, 2), (8, 15)], fill=P["fat"])
        d.rectangle([1, 1, 14, 3], fill=P["wood"])
        for (x, y) in ((5, 5), (9, 6), (7, 9)):
            d.rectangle([x, y, x + 1, y + 1], fill=P["red"])
    elif kind == "burger":
        d.ellipse([1, 2, 14, 9], fill=P["orange"])
        d.rectangle([1, 8, 14, 9], fill=P["green"])
        d.rectangle([1, 10, 14, 11], fill=P["wood_d"])
        d.rounded_rectangle([1, 11, 14, 14], radius=2, fill=P["orange"])
    elif kind == "donut":
        d.ellipse([1, 2, 14, 14], fill=P["pink"])
        d.ellipse([6, 6, 9, 9], fill=(0, 0, 0, 0))
        d.point((4, 5), fill=P["sky"])
        d.point((11, 6), fill=P["gold"])
        d.point((10, 11), fill=P["white"])
    elif kind == "soda":
        d.rectangle([4, 2, 11, 14], fill=P["red"])
        d.rectangle([4, 6, 11, 9], fill=P["white"])
        d.rectangle([5, 1, 10, 2], fill=P["steel"])
    return outline(S)


def brick() -> Image.Image:
    S = new(20, 12)
    d = ImageDraw.Draw(S)
    d.rectangle([1, 1, 18, 10], fill=P["red_d"])
    d.line([1, 5, 18, 5], fill=P["muscle_d"])
    d.line([9, 1, 9, 5], fill=P["muscle_d"])
    d.line([5, 5, 5, 10], fill=P["muscle_d"])
    d.line([14, 5, 14, 10], fill=P["muscle_d"])
    d.line([2, 2, 7, 2], fill=P["red_l"])
    return outline(S)


def pillow() -> Image.Image:
    S = new(24, 16)
    d = ImageDraw.Draw(S)
    d.rounded_rectangle([1, 2, 22, 13], radius=4, fill=P["white"])
    d.line([3, 4, 8, 4], fill=P["fog"])
    d.arc([1, 2, 22, 13], 20, 160, fill=P["fog"])
    return outline(S)


def dumbbell(size=1) -> Image.Image:
    S = new(26, 12)
    d = ImageDraw.Draw(S)
    d.rectangle([5, 5, 20, 6], fill=P["steel_d"])
    for x in (2, 19):
        d.rectangle([x, 1, x + 4, 10], fill=P["steel"])
        d.line([x, 2, x, 9], fill=P["steel_l"])
    return outline(S)


def machine(t=0.0, shake=0.0, light="green") -> Image.Image:
    """'TRANSMUTADOR' contraption: funnel in, pipes, chimney, output chute."""
    S = new(110, 120)
    d = ImageDraw.Draw(S)
    rnd = random.Random(int(t * 30))
    jx = int(round(rnd.uniform(-1, 1) * shake))
    # chimney
    d.rectangle([78 + jx, 6, 90 + jx, 36], fill=P["steel_d"])
    d.rectangle([76 + jx, 4, 92 + jx, 8], fill=P["steel"])
    # funnel
    d.polygon([(14 + jx, 10), (52 + jx, 10), (40 + jx, 32), (26 + jx, 32)], fill=P["steel"])
    d.line([(16 + jx, 12), (50 + jx, 12)], fill=P["steel_l"])
    # body
    d.rounded_rectangle([8 + jx, 30, 100 + jx, 98], radius=6, fill=P["violet"])
    d.rectangle([14 + jx, 36, 94 + jx, 40], fill=P["lav"])
    # window with swirling contents
    d.ellipse([34 + jx, 48, 74 + jx, 84], fill=P["night"])
    for i in range(6):
        a = t * 5 + i * 1.05
        px, py = 54 + jx + math.cos(a) * 12, 66 + math.sin(a) * 12
        d.rectangle([px - 1, py - 1, px + 1, py + 1], fill=P["fat"] if i % 2 else P["muscle_l"])
    d.arc([34 + jx, 48, 74 + jx, 84], 200, 300, fill=P["fog"])
    # gauge + light
    d.ellipse([14 + jx, 46, 28 + jx, 60], fill=P["cream"])
    na = math.radians(200 + 140 * clamp(0.5 + 0.5 * math.sin(t * (3 + shake * 3))))
    d.line([21 + jx, 53, 21 + jx + math.cos(na) * 5, 53 + math.sin(na) * 5], fill=P["red"])
    lc = {"green": P["green"], "red": P["red"], "off": P["steel_d"]}[light]
    d.ellipse([82 + jx, 46, 92 + jx, 56], fill=lc)
    d.point((85 + jx, 48), fill=P["white"])
    # output chute + legs
    d.rectangle([86 + jx, 74, 106 + jx, 84], fill=P["steel_d"])
    d.rectangle([14 + jx, 98, 22 + jx, 112], fill=P["steel_d"])
    d.rectangle([86 + jx, 98, 94 + jx, 112], fill=P["steel_d"])
    return outline(S)


def dna(t=0.0, height=150, marks=(), mark_glow=0.0) -> Image.Image:
    """Rotating double helix. marks = indices of rungs that glow gold (epigenetic marks)."""
    S = new(70, height + 10)
    d = ImageDraw.Draw(S)
    cx = 35
    rungs = []
    for y in range(4, height + 4, 2):
        a = y * 0.09 + t * 2.4
        x1 = cx + math.sin(a) * 24
        x2 = cx + math.sin(a + math.pi) * 24
        z1 = math.cos(a)
        rungs.append((y, x1, x2, z1))
    for i, (y, x1, x2, z1) in enumerate(rungs):
        if i % 4 == 0:
            idx = i // 4
            col = P["lav"]
            if idx in marks:
                col = lerpc(P["lav"], P["gold"], mark_glow)
            d.line([x1, y, x2, y], fill=col)
            if idx in marks and mark_glow > 0.5:
                d.rectangle([min(x1, x2) - 1, y - 1, max(x1, x2) + 1, y + 1], outline=P["gold"])
    for (y, x1, x2, z1) in rungs:
        back, front = ((x1, P["blue_d"]), (x2, P["sky"])) if z1 < 0 else ((x2, P["blue_d"]), (x1, P["sky"]))
        d.rectangle([back[0] - 1, y, back[0] + 1, y + 1], fill=back[1])
    for (y, x1, x2, z1) in rungs:
        fx_, col = (x2, P["sky"]) if z1 < 0 else (x1, P["sky"])
        d.rectangle([fx_ - 2, y, fx_ + 2, y + 1], fill=col)
    return outline(S)


def stamp(text_img: Image.Image, color=P["red"], paper=P["cream"]) -> Image.Image:
    pad = 6
    S = new(text_img.width + pad * 2 + 4, text_img.height + pad * 2 + 4)
    d = ImageDraw.Draw(S)
    if paper:
        d.rectangle([1, 1, S.width - 2, S.height - 2], fill=paper)
    d.rectangle([1, 1, S.width - 2, S.height - 2], outline=color, width=3)
    S.alpha_composite(text_img, (pad + 2, pad + 2))
    # worn ink: knock out a few pixels
    rnd = random.Random(3)
    px = S.load()
    for _ in range(S.width * S.height // 14):
        x, y = rnd.randrange(S.width), rnd.randrange(S.height)
        if px[x, y][3] > 0 and px[x, y][:3] == tuple(color):
            px[x, y] = (*paper, 255) if paper else (0, 0, 0, 0)
    return S


# ============================================================ SETS
_CACHE = {}


def gym_bg(time_of_day="night", parallax=0.0) -> Image.Image:
    """Gym interior with big window (city), racks, mirror, floor mats. Cached per tod."""
    key = ("gym", time_of_day, int(parallax))
    if key in _CACHE:
        return _CACHE[key]
    img = new(W, H, P["night"] + (255,))
    d = ImageDraw.Draw(img)
    if time_of_day == "night":
        sky = [(0, P["ink"]), (0.6, P["deep"]), (1, P["violet"])]
        wall_a, wall_b = P["deep"], P["night"]
    elif time_of_day == "sunrise":
        sky = [(0, P["violet"]), (0.5, P["pink"]), (1, P["orange"])]
        wall_a, wall_b = (70, 54, 96), P["deep"]
    else:  # gloomy/day
        sky = [(0, P["steel_d"]), (1, P["steel"])]
        wall_a, wall_b = (60, 60, 84), P["night"]
    # wall
    vgradient(img, (0, 0, W, 330), [(0, wall_b), (1, wall_a)])
    # window
    wx0, wy0, wx1, wy1 = 30, 40, 240, 190
    vgradient(img, (wx0, wy0, wx1, wy1), sky)
    rnd = random.Random(11)
    ox = int(parallax)
    # city skyline (far)
    for i in range(14):
        bx = wx0 + i * 16 - 6 + ox // 3
        bh = rnd.randint(30, 90)
        col = P["night"] if time_of_day != "sunrise" else (90, 60, 110)
        d.rectangle([bx, wy1 - bh, bx + 13, wy1], fill=col)
        for yy in range(wy1 - bh + 4, wy1 - 4, 6):
            for xx in (bx + 3, bx + 8):
                if rnd.random() < (0.45 if time_of_day == "night" else 0.15):
                    d.rectangle([xx, yy, xx + 1, yy + 2], fill=P["gold"])
    if time_of_day == "sunrise":
        d.ellipse([150, 150, 200, 200], fill=P["gold"])
        d.rectangle([wx0, 190, wx1, 192], fill=P["violet"])
    else:
        d.rectangle([200, 55, 206, 61], fill=P["cream"])  # moon
    # window frame
    d.rectangle([wx0 - 4, wy0 - 4, wx1 + 4, wy0], fill=P["steel_d"])
    d.rectangle([wx0 - 4, wy1, wx1 + 4, wy1 + 5], fill=P["steel_d"])
    for x in (wx0 - 4, (wx0 + wx1) // 2 - 2, wx1):
        d.rectangle([x, wy0 - 4, x + 4, wy1 + 5], fill=P["steel_d"])
    # dumbbell rack (left)
    d.rectangle([10, 250, 90, 256], fill=P["steel_d"])
    d.rectangle([14, 256, 18, 330], fill=P["steel_d"])
    d.rectangle([82, 256, 86, 330], fill=P["steel_d"])
    for i in range(5):
        x = 16 + i * 15
        d.rectangle([x, 242, x + 10, 249], fill=P["steel"])
        d.rectangle([x, 242, x + 2, 249], fill=P["steel_l"])
    # squat rack (right)
    d.rectangle([200, 200, 205, 330], fill=P["red_d"])
    d.rectangle([250, 200, 255, 330], fill=P["red_d"])
    d.rectangle([194, 238, 262, 241], fill=P["steel"])
    d.rectangle([188, 228, 196, 250], fill=P["ink"])
    d.rectangle([258, 228, 266, 250], fill=P["ink"])
    # neon sign
    d.rectangle([100, 205, 170, 226], outline=P["pink"])
    for i, x in enumerate(range(106, 166, 8)):
        d.rectangle([x, 212, x + 4, 219], fill=P["pink"] if i % 2 == 0 else P["sky"])
    # floor
    vgradient(img, (0, 330, W, H), [(0, P["wood"]), (1, P["wood_d"])])
    for y in range(338, H, 14):
        d.line([0, y, W, y], fill=P["wood_d"])
    # rubber mat under the hero (thin, so captions stay readable)
    d.rectangle([60, 338, 210, 344], fill=P["ink"])
    d.rectangle([60, 338, 210, 338], fill=P["deep"])
    _CACHE[key] = img
    return img


def tissue_bg(t=0.0, hue="pink") -> Image.Image:
    """Inside-the-body world: dark tissue with drifting cells/particles (animated)."""
    base = _CACHE.get(("tissue", hue))
    if base is None:
        base = new(W, H, P["tissue"] + (255,))
        c1, c2 = (P["tissue"], P["tissue_l"]) if hue == "pink" else (P["night"], P["deep"])
        vgradient(base, (0, 0, W, H), [(0, c1), (0.5, c2), (1, c1)])
        d = ImageDraw.Draw(base)
        rnd = random.Random(5)
        for _ in range(26):
            x, y, r = rnd.randrange(W), rnd.randrange(H), rnd.randint(6, 18)
            d.ellipse([x - r, y - r, x + r, y + r], outline=lerpc(c2, P["pink"], 0.25))
        _CACHE[("tissue", hue)] = base
    img = base.copy()
    d = ImageDraw.Draw(img)
    rnd = random.Random(9)
    for i in range(40):
        x0, y0 = rnd.randrange(W), rnd.randrange(H)
        sp = rnd.uniform(4, 14)
        y = (y0 - t * sp) % H
        x = x0 + math.sin(t * 0.8 + i) * 4
        c = P["pink"] if i % 3 else P["fog"]
        d.point((x, y), fill=c)
        if i % 5 == 0:
            d.rectangle([x, y, x + 1, y + 1], fill=c)
    return img


def lab_bg(t=0.0) -> Image.Image:
    base = _CACHE.get("lab")
    if base is None:
        base = new(W, H, P["night"] + (255,))
        vgradient(base, (0, 0, W, 340), [(0, P["ink"]), (1, P["deep"])])
        d = ImageDraw.Draw(base)
        # tiled wall
        for y in range(0, 340, 16):
            d.line([0, y, W, y], fill=P["night"])
        for x in range(0, W, 16):
            d.line([x, 0, x, 340], fill=P["night"])
        # shelves with flasks
        for sy in (90, 150):
            d.rectangle([12, sy, 100, sy + 3], fill=P["wood"])
            for i, fx in enumerate(range(18, 96, 16)):
                col = (P["green"], P["sky"], P["pink"], P["gold"], P["lav"])[i % 5]
                d.rectangle([fx + 3, sy - 14, fx + 6, sy - 9], fill=P["fog"])
                d.ellipse([fx, sy - 10, fx + 9, sy], fill=col)
        vgradient(base, (0, 340, W, H), [(0, P["steel_d"]), (1, P["night"])])
        d.line([0, 340, W, 340], fill=P["steel"])
        _CACHE["lab"] = base
    img = base.copy()
    d = ImageDraw.Draw(img)
    # blinking flask bubbles
    for i in range(6):
        x = 22 + i * 16
        y = 80 - (t * 10 + i * 7) % 16
        d.point((x, y), fill=P["white"])
    return img


def end_bg(t=0.0) -> Image.Image:
    img = new(W, H, P["ink"] + (255,))
    vgradient(img, (0, 0, W, H), [(0, P["ink"]), (0.6, P["night"]), (1, P["deep"])])
    d = ImageDraw.Draw(img)
    rnd = random.Random(2)
    for i in range(50):
        x, y = rnd.randrange(W), rnd.randrange(H)
        if (int(t * 4) + i) % 7 != 0:
            d.point((x, y), fill=P["fog"] if i % 4 else P["gold"])
    return img
