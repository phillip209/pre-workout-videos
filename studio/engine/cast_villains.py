"""Villain family (shared face rig, different bodies), extra organs, backgrounds and props for the
story-format Shorts. All original designs."""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

from . import W, H
from . import gfx
from .gfx import P, outline, lerpc, clamp
from .cast_plus import antojo

VILLAIN_COLORS = {
    "hambre": ((255, 160, 70), (200, 100, 40), (255, 210, 150)),
    "cafeina": ((120, 72, 44), (80, 44, 26), (170, 116, 80)),
    "cerveza": ((255, 190, 60), (200, 130, 30), (255, 240, 200)),
    "glucosa": ((240, 244, 255), (170, 180, 220), (255, 255, 255)),
    "plato": ((236, 236, 240), (170, 170, 190), (255, 255, 255)),
    "ascensor": ((150, 160, 180), (90, 96, 120), (210, 216, 230)),
}


def _villain_face(d, cx, cy, mood, t, glow, brow):
    gcol = lerpc(P["gold_d"], P["gold"], clamp(glow))
    for side in (-1, 1):
        ex = cx + side * 10
        if mood == "wink" and side == 1:
            d.line([ex - 5, cy, ex + 5, cy], fill=P["ink"], width=2)
            continue
        if mood == "sleepy":
            d.line([ex - 5, cy + 1, ex + 5, cy + 1], fill=P["ink"], width=2)
            continue
        r = 7 if mood == "jitter" else 6
        d.ellipse([ex - r, cy - 5, ex + r, cy + 5], fill=gcol, outline=P["ink"])
        px = int(math.sin(t * (30 if mood == "jitter" else 2)) * 2) if mood != "confused" else side * 2
        d.rectangle([ex - 1 + px, cy - 3, ex + 1 + px, cy + 3], fill=P["ink"])
        if mood in ("sly", "roar", "jitter"):
            d.line([ex - 7, cy - 9 + (3 if side == -1 else 0), ex + 7, cy - 9 + (0 if side == -1 else 3)],
                   fill=brow, width=3)
    my = cy + 14
    if mood == "roar":
        d.ellipse([cx - 14, my - 6, cx + 14, my + 14], fill=P["ink"])
        for x in range(cx - 12, cx + 13, 6):
            d.polygon([(x, my - 3), (x + 3, my + 3), (x + 6, my - 3)], fill=P["white"])
            d.polygon([(x, my + 11), (x + 3, my + 5), (x + 6, my + 11)], fill=P["white"])
    elif mood in ("confused", "sad"):
        d.arc([cx - 8, my, cx + 8, my + 8], 200, 340, fill=P["ink"], width=2)
    elif mood == "sleepy":
        d.ellipse([cx - 3, my, cx + 3, my + 5], fill=P["ink"])
    else:
        d.chord([cx - 14, my - 6, cx + 14, my + 8], 0, 180, fill=P["ink"])
        for x in range(cx - 12, cx + 12, 5):
            d.polygon([(x, my + 1), (x + 2, my + 5), (x + 4, my + 1)], fill=P["white"])


def villain(kind: str, mood: str = "sly", t: float = 0.0, glow: float = 1.0, size: float = 1.0) -> Image.Image:
    """kinds: antojo, hambre (stomach), cafeina (coffee bean), cerveza (beer mug), glucosa (sugar cube),
    plato (dinner plate), ascensor (elevator). moods: sly | roar | wink | jitter | confused | sad | sleepy"""
    if kind == "antojo":
        return antojo(mood if mood in ("sly", "roar", "wink", "confused", "sleepy") else "sly", t, size=size, glow=glow)
    C, CD, CL = VILLAIN_COLORS[kind]
    S = gfx.new(104, 82)
    d = ImageDraw.Draw(S)
    cx, cy = 52, 44
    cx += int(math.sin(t * 40) * 2) if mood == "jitter" else 0
    wob = int(math.sin(t * 6) * 2)
    if kind == "hambre":
        d.ellipse([cx - 30, cy - 22 + wob, cx + 26, cy + 26 + wob], fill=C)
        d.ellipse([cx + 10, cy - 30 + wob, cx + 30, cy - 10 + wob], fill=C)
        d.rectangle([cx + 16, cy - 40 + wob, cx + 24, cy - 26 + wob], fill=CD)
        d.ellipse([cx - 22, cy - 16 + wob, cx - 8, cy - 8 + wob], fill=CL)
        if mood in ("sly", "roar"):
            k = (t * 1.2) % 1
            d.ellipse([cx + 4, cy + 24 + wob + k * 8, cx + 8, cy + 30 + wob + k * 8], fill=P["sky"])
    elif kind == "cafeina":
        d.ellipse([cx - 26, cy - 30 + wob, cx + 26, cy + 30 + wob], fill=C)
        d.arc([cx - 8, cy - 28 + wob, cx + 8, cy + 28 + wob], 250, 110, fill=CD, width=3)
        d.ellipse([cx - 18, cy - 24 + wob, cx - 8, cy - 14 + wob], fill=CL)
        for i in range(3):
            sx = cx - 10 + i * 10
            ph = (t * 2 + i * 0.3) % 1
            d.line([sx, cy - 34 - ph * 6, sx + 3, cy - 40 - ph * 6], fill=P["fog"], width=2)
    elif kind == "cerveza":
        d.rounded_rectangle([cx - 24, cy - 18 + wob, cx + 20, cy + 32 + wob], radius=4, fill=C)
        d.arc([cx + 12, cy - 8 + wob, cx + 34, cy + 20 + wob], 270, 90, fill=P["fog"], width=5)
        for i in range(6):
            d.ellipse([cx - 28 + i * 9, cy - 30 + wob - (i % 2) * 3, cx - 14 + i * 9, cy - 12 + wob], fill=P["white"])
        for i in range(4):
            by = cy + 28 - ((t * 30 + i * 11) % 34)
            d.ellipse([cx - 16 + i * 9, by + wob, cx - 13 + i * 9, by + 3 + wob], fill=CL)
    elif kind == "glucosa":
        d.rectangle([cx - 26, cy - 26 + wob, cx + 26, cy + 30 + wob], fill=C)
        d.polygon([(cx - 26, cy - 26 + wob), (cx - 16, cy - 34 + wob), (cx + 34, cy - 34 + wob),
                   (cx + 26, cy - 26 + wob)], fill=CL)
        d.polygon([(cx + 26, cy - 26 + wob), (cx + 34, cy - 34 + wob), (cx + 34, cy + 22 + wob),
                   (cx + 26, cy + 30 + wob)], fill=CD)
        rnd = random.Random(4)
        for _ in range(16):
            x, y = rnd.randint(cx - 24, cx + 22), rnd.randint(cy - 24, cy + 28)
            d.point((x, y + wob), fill=CD)
    elif kind == "plato":
        d.ellipse([cx - 32, cy - 26 + wob, cx + 32, cy + 34 + wob], fill=C)
        d.ellipse([cx - 22, cy - 16 + wob, cx + 22, cy + 24 + wob], fill=CL, outline=CD)
        for side in (-1, 1):
            ax = cx + side * 40
            d.line([ax, cy + 20 + wob, ax, cy - 14 + wob], fill=P["steel"], width=3)
            if side < 0:
                for k in range(3):
                    d.line([ax - 3 + k * 3, cy - 14 + wob, ax - 3 + k * 3, cy - 22 + wob], fill=P["steel"])
            else:
                d.polygon([(ax - 2, cy - 14 + wob), (ax + 3, cy - 24 + wob), (ax + 3, cy - 10 + wob)], fill=P["steel_l"])
    elif kind == "ascensor":
        d.rectangle([cx - 28, cy - 34 + wob, cx + 28, cy + 34 + wob], fill=C)
        d.rectangle([cx - 22, cy - 8 + wob, cx + 22, cy + 34 + wob], fill=CD)
        d.line([cx, cy - 8 + wob, cx, cy + 34 + wob], fill=P["ink"], width=2)
        d.rectangle([cx - 10, cy - 32 + wob, cx + 10, cy - 24 + wob], fill=P["ink"])
        on = (t * 3) % 1 < 0.5
        d.polygon([(cx - 4, cy - 25 + wob), (cx, cy - 31 + wob), (cx + 4, cy - 25 + wob)],
                  fill=P["gold"] if on else P["steel_d"])
    face_y = (cy + 4 + wob) if kind == "ascensor" else (cy - 4 + wob)
    _villain_face(d, cx, face_y, mood, t, glow, CL if kind == "ascensor" else CD)
    out = outline(S)
    if size != 1.0:
        out = out.resize((max(1, int(out.width * size)), max(1, int(out.height * size))), Image.NEAREST)
    return out


# ------------------------------------------------------------------ extra organs
def stomach(mood: str = "happy", t: float = 0.0, growl: float = 0.0) -> Image.Image:
    from .organs import _face
    S = gfx.new(70, 60)
    d = ImageDraw.Draw(S)
    sh = int(math.sin(t * 30) * 2 * growl)
    d.ellipse([6 + sh, 14, 60 + sh, 56], fill=(250, 160, 140))
    d.rounded_rectangle([44 + sh, 2, 56 + sh, 24], radius=5, fill=(250, 160, 140))
    d.arc([14 + sh, 22, 52 + sh, 52], 30, 150, fill=(210, 110, 100), width=2)
    _face(d, 33 + sh, 32, mood, t)
    return outline(S)


def heart(mood: str = "happy", t: float = 0.0, bpm: float = 70) -> Image.Image:
    from .organs import _face
    S = gfx.new(64, 60)
    d = ImageDraw.Draw(S)
    beat = 1 + 0.08 * max(0.0, math.sin(t * bpm / 60 * 2 * math.pi)) ** 8
    r = 15 * beat
    for side in (-1, 1):
        cx = 32 + side * 12
        d.ellipse([cx - r, 20 - r, cx + r, 20 + r], fill=P["red"])
    d.polygon([(32 - 27 * beat, 24), (32 + 27 * beat, 24), (32, 56)], fill=P["red"])
    d.ellipse([12, 10, 20, 18], fill=P["red_l"])
    _face(d, 32, 26, mood, t)
    return outline(S)


# ------------------------------------------------------------------ extra backgrounds
def office_bg(t: float = 0.0, dusk: float = 0.0, clock: str = "16:00") -> Image.Image:
    """Desk by a window; dusk 0..1 shifts afternoon -> night; the wall clock shows `clock`."""
    from .font import draw_text
    img = gfx.new(W, H, P["night"] + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 300], fill=lerpc((120, 110, 160), (50, 40, 80), dusk))
    gfx.vgradient(img, (150, 50, 250, 150), [(0, lerpc(P["sky"], P["ink"], dusk)), (1, lerpc(P["orange"], P["violet"], dusk))])
    d = ImageDraw.Draw(img)
    d.rectangle([150, 50, 250, 150], outline=P["steel_d"], width=4)
    d.line([200, 50, 200, 150], fill=P["steel_d"], width=3)
    if dusk > 0.6:
        d.ellipse([220, 64, 232, 76], fill=P["cream"])
    if clock:
        d.rounded_rectangle([30, 86, 110, 116], radius=4, fill=P["ink"], outline=P["steel"])
        draw_text(img, clock, 70, 94, color=P["red_l"], scale=2, align="center")
    d.rectangle([0, 270, W, 282], fill=P["wood"])
    d.rectangle([0, 282, W, H], fill=P["wood_d"])
    d.rectangle([20, 200, 110, 262], fill=P["ink"], outline=P["steel"])
    d.rectangle([26, 206, 104, 256], fill=lerpc(P["sky"], P["blue"], 0.5 + 0.5 * math.sin(t * 2)))
    for k in range(4):
        d.line([32, 214 + k * 10, 32 + (k * 17) % 60 + 20, 214 + k * 10], fill=P["white"])
    d.rectangle([58, 262, 70, 270], fill=P["steel_d"])
    return img


def stairs_bg(t: float = 0.0, climb: float = 0.0) -> Image.Image:
    """Stairwell from the side; `climb` (px) scrolls the steps as the hero goes up."""
    from .font import draw_text
    img = gfx.new(W, H, P["deep"] + (255,))
    gfx.vgradient(img, (0, 0, W, H), [(0, (70, 76, 100)), (1, (40, 42, 64))])
    d = ImageDraw.Draw(img)
    sw, sh = 26, 14
    ph = climb % sh
    for i in range(-3, 32):
        x = W - i * sw + (ph / sh) * sw
        y = 120 + i * sh + ph
        d.polygon([(x - sw, y), (W + 40, y), (W + 40, H), (x - sw, H)], fill=P["steel"] if i % 2 else P["steel_l"])
        d.line([x - sw, y, x, y], fill=P["white"])
    floor_n = int(climb // 140) + 1
    d.rectangle([20, 86, 70, 118], fill=P["green_d"], outline=P["white"])
    draw_text(img, f"P{floor_n}", 45, 94, color=P["white"], scale=2, align="center")
    return img


def bar_bg(t: float = 0.0) -> Image.Image:
    """Night bar/party: string lights, bottle shelf, counter."""
    img = gfx.new(W, H, P["ink"] + (255,))
    gfx.vgradient(img, (0, 0, W, 300), [(0, P["ink"]), (1, P["violet"])])
    d = ImageDraw.Draw(img)
    d.line([0, 84, W, 84], fill=P["steel_d"])
    for i in range(12):
        x = i * 24 + 6
        y = 86 + int(8 * math.sin(i * 0.9))
        on = ((t * 3 + i) % 3) < 2
        c = [P["gold"], P["pink"], P["sky"], P["green"]][i % 4]
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=c if on else P["deep"])
    for i in range(8):
        x = 20 + i * 30
        c = [P["green_d"], P["orange"], P["red_d"], P["sky"]][i % 4]
        d.rectangle([x, 150, x + 10, 190], fill=c)
        d.rectangle([x + 3, 140, x + 7, 150], fill=c)
    d.rectangle([0, 190, W, 196], fill=P["wood"])
    d.rectangle([0, 290, W, 306], fill=P["wood"])
    d.rectangle([0, 306, W, H], fill=P["wood_d"])
    return img


# ------------------------------------------------------------------ props
def water_glass(level: float = 1.0) -> Image.Image:
    S = gfx.new(22, 30)
    d = ImageDraw.Draw(S)
    d.polygon([(2, 2), (19, 2), (17, 28), (4, 28)], fill=(200, 230, 255, 130))
    h = int(24 * clamp(level))
    if h > 0:
        d.polygon([(4, 28 - h), (17, 28 - h), (17, 28), (4, 28)], fill=P["sky"])
        d.line([5, 28 - h, 16, 28 - h], fill=P["white"])
    return outline(S)


def coffee_cup(t: float = 0.0) -> Image.Image:
    S = gfx.new(26, 26)
    d = ImageDraw.Draw(S)
    d.rounded_rectangle([3, 8, 19, 24], radius=3, fill=P["white"])
    d.arc([15, 11, 25, 20], 270, 90, fill=P["white"], width=3)
    d.rectangle([5, 9, 17, 12], fill=P["wood_d"])
    for i in range(2):
        ph = (t * 1.5 + i * 0.5) % 1
        d.line([8 + i * 5, 6 - ph * 5, 10 + i * 5, 2 - ph * 5], fill=P["fog"], width=2)
    return outline(S)


def beer(t: float = 0.0) -> Image.Image:
    S = gfx.new(24, 28)
    d = ImageDraw.Draw(S)
    d.rectangle([3, 7, 15, 26], fill=P["gold"])
    d.ellipse([1, 2, 17, 10], fill=P["white"])
    d.arc([12, 10, 22, 20], 270, 90, fill=P["fog"], width=3)
    return outline(S)


def plate(full: bool = True) -> Image.Image:
    S = gfx.new(40, 18)
    d = ImageDraw.Draw(S)
    d.ellipse([1, 4, 38, 17], fill=P["white"])
    if full:
        d.ellipse([8, 1, 22, 11], fill=P["fat"])
        d.ellipse([18, 3, 32, 11], fill=P["green"])
        d.ellipse([12, 6, 28, 13], fill=P["wood"])
    return outline(S)


def phone(t: float = 0.0) -> Image.Image:
    S = gfx.new(14, 24)
    d = ImageDraw.Draw(S)
    d.rounded_rectangle([1, 1, 12, 22], radius=2, fill=P["ink"])
    d.rectangle([3, 3, 10, 18], fill=lerpc(P["sky"], P["lav"], 0.5 + 0.5 * math.sin(t * 5)))
    return outline(S)
