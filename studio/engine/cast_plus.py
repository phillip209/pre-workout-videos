"""Extra cast for cinematic episodes (original designs):
- leo_face: native-resolution close-up of Leo (same hair, red headband, teal tank as cast.hero)
- antojo: the "Craving" monster — a wrapped pink candy gremlin (metaphor for sugar cravings)
- candy_aisle_bg: supermarket sweets aisle with two parallax layers + fluorescent light flicker
- gauge: sweetness dial; apple; spoon; vhs_rewind effect
"""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

from . import W, H
from . import gfx
from .gfx import P, outline, lerp, lerpc, clamp

SKIN, SKIN_D, SKIN_L = P["skin"], P["skin_d"], P["skin_l"]
CANDY, CANDY_D, CANDY_L = (255, 120, 180), (200, 60, 130), (255, 200, 225)


# ------------------------------------------------------------------ Leo close-up
def leo_face(mood: str = "neutral", t: float = 0.0, blink: bool = False, look: float = 0.0,
             tongue_out: float = 0.0, sweat: bool = False) -> Image.Image:
    """~96x104 bust. moods: neutral | shock | sad | happy | grit | taste | sly
    tongue_out 0..1 opens the mouth and pushes the tongue out (for the 'it happened to his tongue' beat)."""
    S = gfx.new(96, 104)
    d = ImageDraw.Draw(S)
    cx = 48
    breathe = int(round(math.sin(t * 2.4) * 1))
    # shoulders / tank
    d.rounded_rectangle([8, 86 + breathe, 88, 112], radius=10, fill=P["tank"])
    d.polygon([(34, 86 + breathe), (48, 98 + breathe), (62, 86 + breathe)], fill=SKIN)
    d.rectangle([40, 76, 56, 90 + breathe], fill=SKIN_D)
    # head
    d.rounded_rectangle([18, 18, 78, 84], radius=18, fill=SKIN)
    d.rectangle([18, 60, 22, 74], fill=SKIN_D)
    d.ellipse([12, 44, 24, 60], fill=SKIN)                 # ears
    d.ellipse([72, 44, 84, 60], fill=SKIN)
    d.ellipse([15, 48, 21, 56], fill=SKIN_D)
    d.ellipse([75, 48, 81, 56], fill=SKIN_D)
    # hair (spiky) + headband
    d.rounded_rectangle([16, 10, 80, 34], radius=12, fill=P["hair"])
    for i, hx in enumerate(range(18, 78, 10)):
        d.polygon([(hx, 14), (hx + 5, 2 + (i % 2) * 4), (hx + 10, 14)], fill=P["hair"])
    d.rectangle([16, 28, 80, 35], fill=P["red"])
    d.rectangle([16, 28, 80, 29], fill=P["red_l"])
    d.polygon([(78, 30), (90, 26), (88, 36)], fill=P["red"])  # headband knot
    # eyes
    ey = 50
    lx = int(round(look * 2))
    for sx in (34, 62):
        if blink or mood == "taste":
            d.arc([sx - 6, ey - 4, sx + 6, ey + 4], 20, 160, fill=P["ink"], width=2)
            continue
        if mood == "happy":
            d.arc([sx - 6, ey - 2, sx + 6, ey + 8], 200, 340, fill=P["ink"], width=3)
            continue
        r = 7 if mood == "shock" else 5
        d.ellipse([sx - r, ey - r, sx + r, ey + r], fill=P["white"], outline=P["ink"])
        pr = 2 if mood == "shock" else 3
        d.rectangle([sx - pr + lx, ey - pr, sx + pr + lx, ey + pr], fill=P["ink"])
        d.point((sx - pr + lx + 1, ey - pr + 1), fill=P["white"])
    # brows
    if mood in ("sad",):
        d.line([28, 40, 40, 37], fill=P["hair"], width=3); d.line([56, 37, 68, 40], fill=P["hair"], width=3)
    elif mood in ("grit", "sly"):
        d.line([28, 37, 40, 41], fill=P["hair"], width=3); d.line([56, 41, 68, 37], fill=P["hair"], width=3)
    elif mood == "shock":
        d.line([27, 36, 40, 33], fill=P["hair"], width=3); d.line([56, 33, 69, 36], fill=P["hair"], width=3)
    else:
        d.line([28, 39, 40, 38], fill=P["hair"], width=3); d.line([56, 38, 68, 39], fill=P["hair"], width=3)
    # nose + cheeks
    d.line([48, 54, 46, 62, 49, 62], fill=SKIN_D, width=2)
    if mood in ("happy", "taste"):
        d.ellipse([24, 60, 32, 64], fill=P["pink"]); d.ellipse([64, 60, 72, 64], fill=P["pink"])
    # mouth
    my = 70
    op = clamp(tongue_out)
    if mood == "shock" or op > 0:
        h = int(6 + 8 * max(op, 0.6 if mood == "shock" else 0))
        d.rounded_rectangle([cx - 9, my - 3, cx + 9, my - 3 + h], radius=5, fill=P["ink"])
        if op > 0:
            tl = int(4 + op * 14)
            d.rounded_rectangle([cx - 7, my, cx + 7, my + tl], radius=6, fill=(250, 140, 160))
            d.line([cx, my + 2, cx, my + tl - 3], fill=(210, 90, 116))
    elif mood == "happy":
        d.chord([cx - 10, my - 6, cx + 10, my + 8], 0, 180, fill=P["ink"])
        d.rectangle([cx - 7, my + 1, cx + 7, my + 3], fill=P["white"])
    elif mood == "sad":
        d.arc([cx - 8, my, cx + 8, my + 10], 200, 340, fill=P["ink"], width=3)
    elif mood == "grit":
        d.rectangle([cx - 9, my - 2, cx + 9, my + 4], fill=P["white"], outline=P["ink"])
        for x in (cx - 4, cx, cx + 4):
            d.line([x, my - 2, x, my + 4], fill=P["ink"])
    elif mood == "taste":
        d.ellipse([cx - 4, my - 2, cx + 4, my + 4], fill=P["ink"])
    elif mood == "sly":
        d.line([cx - 8, my + 2, cx + 8, my - 1], fill=P["ink"], width=2)
    else:
        d.line([cx - 6, my + 1, cx + 6, my + 1], fill=P["ink"], width=2)
    if sweat:
        k = (t * 1.5) % 1
        d.ellipse([80, 36 + k * 20, 86, 44 + k * 20], fill=P["sky"])
    return outline(S)


# ------------------------------------------------------------------ the Craving monster
def antojo(mood: str = "sly", t: float = 0.0, size: float = 1.0, glow: float = 1.0) -> Image.Image:
    """Wrapped candy gremlin. moods: sly | roar | wink | confused | sleepy. size scales native drawing
    (use paste scale for big zooms). glow 0..1 = eye glow intensity."""
    base_w = 64
    S = gfx.new(base_w + 40, 70)
    d = ImageDraw.Draw(S)
    cx, cy = (base_w + 40) // 2, 38
    wob = math.sin(t * 6) * 2
    # wrapper twists (ears) flapping
    for side in (-1, 1):
        x0 = cx + side * 26
        fl = int(math.sin(t * 9 + side) * 3)
        d.polygon([(x0, cy - 4), (x0 + side * 18, cy - 14 + fl), (x0 + side * 20, cy + 12 - fl), (x0, cy + 4)],
                  fill=CANDY_L)
        d.line([x0 + side * 6, cy - 6, x0 + side * 8, cy + 6], fill=CANDY)
    # body (candy) with swirl
    r = 26
    d.ellipse([cx - r, cy - r + wob, cx + r, cy + r + wob], fill=CANDY)
    for k in range(3):
        a0 = (t * 80 + k * 120) % 360
        d.arc([cx - r + 5, cy - r + 5 + wob, cx + r - 5, cy + r - 5 + wob], a0, a0 + 50, fill=P["white"], width=4)
    d.ellipse([cx - 16, cy - 20 + wob, cx - 6, cy - 12 + wob], fill=CANDY_L)
    # eyes
    gcol = lerpc(P["gold_d"], P["gold"], clamp(glow))
    ey = cy - 4 + wob
    for side in (-1, 1):
        ex = cx + side * 10
        if mood == "wink" and side == 1:
            d.line([ex - 5, ey, ex + 5, ey], fill=P["ink"], width=2)
            continue
        if mood == "sleepy":
            d.line([ex - 5, ey + 1, ex + 5, ey + 1], fill=P["ink"], width=2)
            continue
        d.ellipse([ex - 6, ey - 5, ex + 6, ey + 5], fill=gcol, outline=P["ink"])
        px = int(math.sin(t * 2) * 2) if mood != "confused" else (side * 2)
        d.rectangle([ex - 1 + px, ey - 3, ex + 1 + px, ey + 3], fill=P["ink"])
        # angry brows
        if mood in ("sly", "roar"):
            d.line([ex - 7, ey - 9 + (3 if side == -1 else 0), ex + 7, ey - 9 + (0 if side == -1 else 3)],
                   fill=CANDY_D, width=3)
        if mood == "confused" and side == -1:
            d.arc([ex - 7, ey - 12, ex + 7, ey - 4], 200, 340, fill=CANDY_D, width=2)
    # mouth
    my = cy + 10 + wob
    if mood == "roar":
        d.ellipse([cx - 14, my - 6, cx + 14, my + 14], fill=P["ink"])
        for x in range(cx - 12, cx + 13, 6):
            d.polygon([(x, my - 3), (x + 3, my + 3), (x + 6, my - 3)], fill=P["white"])
            d.polygon([(x, my + 11), (x + 3, my + 5), (x + 6, my + 11)], fill=P["white"])
    elif mood == "confused":
        d.line([cx - 8, my + 2, cx - 3, my, cx + 2, my + 3, cx + 8, my], fill=P["ink"], width=2)
    elif mood == "sleepy":
        d.ellipse([cx - 3, my, cx + 3, my + 5], fill=P["ink"])
    else:  # sly / wink: jagged grin
        d.chord([cx - 14, my - 6, cx + 14, my + 8], 0, 180, fill=P["ink"])
        for x in range(cx - 12, cx + 12, 5):
            d.polygon([(x, my + 1), (x + 2, my + 5), (x + 4, my + 1)], fill=P["white"])
    # stubby arms
    for side in (-1, 1):
        ax = cx + side * 22
        lift = int(math.sin(t * 5 + side) * 3) - (10 if mood == "roar" else 0)
        d.line([ax, cy + 10 + wob, ax + side * 8, cy + 18 + lift + wob], fill=CANDY_D, width=4)
        d.ellipse([ax + side * 8 - 3, cy + 15 + lift + wob, ax + side * 8 + 3, cy + 21 + lift + wob], fill=CANDY)
    out = outline(S)
    if size != 1.0:
        out = out.resize((max(1, int(out.width * size)), max(1, int(out.height * size))), Image.NEAREST)
    return out


# ------------------------------------------------------------------ backgrounds
_AISLE_CACHE: dict = {}


def _shelf_strip(seed: int, dark: bool) -> Image.Image:
    """A long horizontally tiling shelf strip of candy boxes (W*3 wide)."""
    key = (seed, dark)
    if key in _AISLE_CACHE:
        return _AISLE_CACHE[key]
    rnd = random.Random(seed)
    w = W * 3
    S = gfx.new(w, 300)
    d = ImageDraw.Draw(S)
    cols = [P["pink"], P["red"], P["gold"], P["sky"], P["orange"], P["lav"], P["green"], CANDY]
    for row, y in enumerate((40, 110, 180, 250)):
        d.rectangle([0, y + 44, w, y + 50], fill=P["steel"] if not dark else P["steel_d"])
        d.rectangle([0, y + 50, w, y + 54], fill=P["steel_d"])
        x = 0
        while x < w:
            bw = rnd.randint(14, 26)
            bh = rnd.randint(22, 42)
            c = rnd.choice(cols)
            if dark:
                c = lerpc(c, P["night"], 0.55)
            d.rectangle([x + 1, y + 44 - bh, x + bw - 1, y + 44], fill=c)
            d.rectangle([x + 3, y + 44 - bh + 4, x + bw - 3, y + 44 - bh + 9], fill=lerpc(c, P["white"], 0.5))
            if rnd.random() < 0.5:
                d.ellipse([x + bw // 2 - 3, y + 44 - bh // 2 - 2, x + bw // 2 + 3, y + 44 - bh // 2 + 4],
                          fill=lerpc(c, P["ink"], 0.3))
            x += bw
    _AISLE_CACHE[key] = S
    return S


def candy_aisle_bg(t: float = 0.0, scroll: float = 0.0, dim: float = 0.0) -> Image.Image:
    """Supermarket sweets aisle. scroll = camera travel in px (parallax: back shelves move slower)."""
    img = gfx.new(W, H, P["deep"] + (255,))
    gfx.vgradient(img, (0, 0, W, 90), [(0, P["ink"]), (1, P["deep"])])
    d = ImageDraw.Draw(img)
    # ceiling fluorescent lights (one flickers)
    for i, x in enumerate(range(-40, W + 80, 90)):
        lx = int(x - (scroll * 0.3) % 90)
        on = not (i == 2 and (t * 7) % 5 < 0.4)
        d.rectangle([lx, 20, lx + 50, 24], fill=P["white"] if on else P["steel_d"])
        if on:
            d.polygon([(lx - 6, 26), (lx + 56, 26), (lx + 70, 60), (lx - 20, 60)], fill=lerpc(P["deep"], P["lav"], 0.25))
    back = _shelf_strip(11, True)
    bx = -int(scroll * 0.45) % W
    img.alpha_composite(back.crop((bx, 0, bx + W, 300)), (0, 40))
    front = _shelf_strip(5, False)
    fx_ = -int(scroll) % W
    # front shelves only on the side edges for depth (frame the subject)
    edge = front.crop((fx_, 0, fx_ + 60, 300))
    img.alpha_composite(edge, (0, 30))
    edge2 = front.crop((fx_ + 120, 0, fx_ + 180, 300))
    img.alpha_composite(edge2, (W - 60, 30))
    # floor
    d.rectangle([0, 330, W, H], fill=P["steel_l"])
    for x in range(-40, W + 40, 34):
        ox = int(x - scroll % 34)
        d.line([ox, 330, ox - 60, H], fill=P["steel"])
    d.rectangle([0, 330, W, 334], fill=P["steel"])
    if dim > 0:
        img = gfx.darken(img, dim)
    return img


# ------------------------------------------------------------------ props & fx
def gauge(value: float, t: float = 0.0, label_txt: str = "DULZOR") -> Image.Image:
    """Semicircular dial 0..1 (green -> pink). Needle jitters slightly."""
    from .font import draw_text
    S = gfx.new(120, 76)
    d = ImageDraw.Draw(S)
    cx, cy, r = 60, 62, 52
    d.pieslice([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], 180, 360, fill=P["ink"])
    segs = [P["green"], P["gold"], P["orange"], P["pink"]]
    for i, c in enumerate(segs):
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 180 + i * 45, 180 + (i + 1) * 45, fill=c)
    d.pieslice([cx - r + 12, cy - r + 12, cx + r - 12, cy + r - 12], 180, 360, fill=P["ink"])
    v = clamp(value) + math.sin(t * 25) * 0.008
    a = math.radians(180 + v * 180)
    d.line([cx, cy, cx + math.cos(a) * (r - 6), cy + math.sin(a) * (r - 6)], fill=P["white"], width=3)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=P["steel_l"])
    draw_text(S, label_txt, cx, cy - 22, color=P["white"], align="center")
    return outline(S)


def apple() -> Image.Image:
    S = gfx.new(18, 20)
    d = ImageDraw.Draw(S)
    d.ellipse([1, 4, 16, 19], fill=P["red"])
    d.ellipse([4, 7, 7, 10], fill=P["red_l"])
    d.line([9, 1, 9, 6], fill=P["wood_d"], width=2)
    d.ellipse([10, 1, 16, 5], fill=P["green"])
    return outline(S)


def spoon(full: bool = True) -> Image.Image:
    S = gfx.new(34, 12)
    d = ImageDraw.Draw(S)
    d.line([2, 6, 22, 6], fill=P["steel_l"], width=3)
    d.ellipse([20, 1, 33, 11], fill=P["steel_l"])
    if full:
        d.ellipse([22, 2, 31, 9], fill=P["fat"])
    return outline(S)


def vhs_rewind(img: Image.Image, p: float, t: float) -> Image.Image:
    """VHS rewind look: tearing horizontal slices, scanlines, '◀◀' and a white noise band.
    p 0..1 = intensity."""
    if p <= 0:
        return img
    out = img.copy()
    rnd = random.Random(int(t * 30))
    for _ in range(int(6 + 14 * p)):
        y = rnd.randint(0, H - 8)
        h = rnd.randint(2, 10)
        dx = int(rnd.randint(-24, 24) * p)
        band = img.crop((0, y, W, y + h))
        out.paste(band, (dx, y))
    d = ImageDraw.Draw(out)
    for y in range(0, H, 3):
        d.line([0, y, W, y], fill=(0, 0, 0, int(70 * p)))
    ny = int((t * 600) % H)
    d.rectangle([0, ny, W, ny + 6], fill=(240, 240, 255, int(140 * p)))
    # ◀◀ icon
    for k in range(2):
        x0 = 22 + k * 14
        d.polygon([(x0 + 12, 70), (x0, 78), (x0 + 12, 86)], fill=P["white"])
    return out


# ------------------------------------------------------------------ kitchen props (moved from b01)
def donut(bitten=0.0):
    S = gfx.new(30, 26)
    d = ImageDraw.Draw(S)
    d.ellipse([1, 4, 28, 25], fill=P["wood"])
    d.ellipse([1, 1, 28, 21], fill=P["pink"])
    d.ellipse([11, 8, 18, 14], fill=(0, 0, 0, 0))
    for (x, y, c) in ((6, 6, P["sky"]), (21, 5, P["gold"]), (24, 13, P["white"]), (5, 14, P["green"]),
                      (14, 3, P["white"]), (18, 17, P["sky"])):
        d.rectangle([x, y, x + 1, y], fill=c)
    if bitten > 0:
        r = int(4 + bitten * 4)
        for k in range(3):
            d.ellipse([22 - r + k * 3, -r + k * 2, 22 + r + k * 3, r + k * 2], fill=(0, 0, 0, 0))
    return gfx.outline(S)


def soda(crossed=False):
    S = gfx.new(18, 28)
    d = ImageDraw.Draw(S)
    d.rectangle([3, 3, 14, 26], fill=P["red"])
    d.rectangle([3, 10, 14, 15], fill=P["white"])
    d.rectangle([5, 1, 12, 3], fill=P["steel"])
    if crossed:
        d.line([0, 27, 17, 0], fill=P["ink"], width=4)
        d.line([0, 27, 17, 0], fill=P["red_l"], width=2)
    return gfx.outline(S)


def pudding():
    S = gfx.new(26, 24)
    d = ImageDraw.Draw(S)
    d.polygon([(2, 12), (23, 12), (20, 23), (5, 23)], fill=P["steel_l"])
    d.ellipse([3, 4, 22, 16], fill=P["fat"])
    d.ellipse([6, 3, 19, 9], fill=P["wood"])
    return gfx.outline(S)


def trash():
    S = gfx.new(30, 34)
    d = ImageDraw.Draw(S)
    d.polygon([(3, 6), (26, 6), (23, 33), (6, 33)], fill=P["steel_d"])
    d.rectangle([1, 3, 28, 7], fill=P["steel"])
    for x in (10, 15, 20):
        d.line([x, 10, x - 1, 30], fill=P["steel"])
    return gfx.outline(S)


def calendar_page(n):
    S = gfx.new(26, 30)
    d = ImageDraw.Draw(S)
    d.rectangle([1, 1, 24, 28], fill=P["white"])
    d.rectangle([1, 1, 24, 8], fill=P["red"])
    from .font import draw_text
    draw_text(S, str(n), 13, 13, color=P["ink"], scale=1, align="center")
    return gfx.outline(S)


def kitchen_bg(g, dark=0.0, warm=False):
    """Original kitchen at night: tiles, counter, fridge glow."""
    img = gfx.new(W, H, P["night"] + (255,))
    top = [(0, P["deep"]), (1, P["violet"])] if not warm else [(0, P["violet"]), (0.7, P["pink"]), (1, P["orange"])]
    gfx.vgradient(img, (0, 0, W, 300), top)
    d = ImageDraw.Draw(img)
    for y in range(120, 300, 16):
        for x in range(0 if (y // 16) % 2 else 8, W, 16):
            d.rectangle([x, y, x + 14, y + 14], outline=gfx.lerpc(P["violet"], P["lav"], 0.25))
    # window
    d.rectangle([150, 40, 240, 110], fill=P["ink"] if not warm else P["sky"])
    d.rectangle([150, 40, 240, 110], outline=P["steel_d"], width=3)
    d.line([195, 40, 195, 110], fill=P["steel_d"], width=2)
    if not warm:
        d.ellipse([210, 52, 224, 66], fill=P["cream"])
    else:
        d.ellipse([160, 80, 190, 110], fill=P["gold"])
    # fridge
    d.rectangle([14, 130, 70, 300], fill=P["steel_l"])
    d.line([14, 190, 70, 190], fill=P["steel"], width=2)
    d.rectangle([60, 150, 64, 175], fill=P["steel_d"])
    # counter
    d.rectangle([0, 300, W, 312], fill=P["wood"])
    d.rectangle([0, 312, W, H], fill=P["wood_d"])
    if dark > 0:
        img = gfx.darken(img, dark)
    return img


