"""Organ characters with faces (original designs). Fixed colours so the viewer always knows who is who:
brain = pink, liver = wine red (+ yellow fat droplets), tongue = light pink.
moods: happy | sad | angry | shock | pain
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from . import gfx
from .gfx import P, outline
from .font import draw_text, text_width

BRAIN, BRAIN_D, BRAIN_L = (246, 150, 180), (196, 96, 132), (255, 196, 214)
LIVER, LIVER_D, LIVER_L = (150, 46, 60), (100, 24, 40), (196, 84, 96)
TONGUE, TONGUE_D, TONGUE_L = (250, 140, 160), (210, 90, 116), (255, 190, 200)


def _face(d, cx, cy, mood, t, s=1):
    """Eyes + mouth centred at (cx, cy). s scales spacing."""
    ex = 6 * s
    blink = (t % 3.3) < 0.1
    for side in (-1, 1):
        x = cx + side * ex
        if mood == "happy":
            d.arc([x - 3, cy - 3, x + 3, cy + 3], 200, 340, fill=P["ink"], width=2)
        elif mood in ("pain", "angry"):
            d.line([x - 3, cy - 1, x + 3, cy + 1] if side < 0 else [x - 3, cy + 1, x + 3, cy - 1], fill=P["ink"], width=2)
            d.rectangle([x - 1, cy + 1, x + 1, cy + 3], fill=P["ink"])
            if mood == "angry":
                d.line([x - 4, cy - 5, x + 3, cy - 3] if side < 0 else [x - 3, cy - 3, x + 4, cy - 5], fill=P["ink"], width=2)
        elif mood == "shock":
            d.ellipse([x - 3, cy - 4, x + 3, cy + 3], fill=P["white"], outline=P["ink"])
            d.rectangle([x - 1, cy - 1, x, cy], fill=P["ink"])
        else:  # sad
            if blink:
                d.line([x - 2, cy, x + 2, cy], fill=P["ink"])
            else:
                d.rectangle([x - 1, cy - 1, x + 1, cy + 2], fill=P["ink"])
            d.line([x - 3, cy - 4, x + 2, cy - 5] if side < 0 else [x - 2, cy - 5, x + 3, cy - 4], fill=P["ink"])
    my = cy + 7 * s
    if mood == "happy":
        d.chord([cx - 5, my - 4, cx + 5, my + 4], 0, 180, fill=P["ink"])
        d.rectangle([cx - 2, my + 1, cx + 2, my + 3], fill=P["red_l"])
    elif mood == "shock":
        d.ellipse([cx - 3, my - 2, cx + 3, my + 5], fill=P["ink"])
    elif mood == "angry":
        d.rectangle([cx - 5, my, cx + 5, my + 3], fill=P["ink"])
        for x in range(cx - 4, cx + 5, 3):
            d.line([x, my, x, my + 3], fill=P["white"])
    elif mood == "pain":
        d.line([cx - 5, my + 2, cx - 2, my, cx + 1, my + 2, cx + 4, my], fill=P["ink"], width=2)
    else:
        d.arc([cx - 5, my, cx + 5, my + 7], 200, 340, fill=P["ink"], width=2)


def brain(mood: str = "happy", t: float = 0.0) -> "gfx.Image.Image":
    S = gfx.new(60, 48)
    d = ImageDraw.Draw(S)
    throb = 1 if (mood == "pain" and (t * 6) % 1 < 0.5) else 0
    d.ellipse([4 - throb, 6 - throb, 56 + throb, 44 + throb], fill=BRAIN)
    # folds
    for (x0, y0, x1, y1, a0, a1) in ((10, 10, 26, 24, 180, 360), (28, 8, 46, 22, 180, 360), (14, 26, 30, 40, 0, 180),
                                     (34, 26, 50, 40, 0, 180), (24, 16, 36, 30, 90, 270)):
        d.arc([x0, y0, x1, y1], a0, a1, fill=BRAIN_D, width=1)
    d.line([30, 7, 30, 18], fill=BRAIN_D)
    d.ellipse([12, 9, 22, 14], fill=BRAIN_L)
    _face(d, 30, 24, mood, t)
    if mood == "pain":  # stress marks
        for (x, y) in ((2, 6), (54, 4), (56, 30)):
            d.line([x, y, x + 3, y + 3], fill=P["red"], width=2)
            d.line([x + 3, y, x, y + 3], fill=P["red"], width=2)
    return outline(S)


def liver(fat: float = 0.0, mood: str = "happy", t: float = 0.0) -> "gfx.Image.Image":
    """fat 0..1 controls how many / how big the yellow fat droplets are (and a bloated outline)."""
    S = gfx.new(76, 52)
    d = ImageDraw.Draw(S)
    puff = int(fat * 5)
    d.polygon([(4, 18 - puff), (30, 6 - puff), (70, 8 - puff), (72 + puff // 2, 20), (52, 40 + puff),
               (26, 46 + puff), (8, 36 + puff)], fill=LIVER)
    d.line([30, 8 - puff, 34, 30], fill=LIVER_D, width=2)
    d.polygon([(10, 18), (28, 10), (30, 14), (12, 22)], fill=LIVER_L)
    n = int(round(fat * 12))
    # droplets kept clear of the face (x 30-50, y 12-36) so emotions stay readable
    rnd = [(14, 28), (20, 36), (22, 22), (58, 15), (62, 25), (57, 34), (48, 41), (27, 42), (13, 20), (66, 18),
           (37, 42), (20, 30)]
    for i in range(n):
        x, y = rnd[i]
        r = 2 + int(fat * 3) + (i % 2)
        wob = int(math.sin(t * 5 + i) * 1)
        d.ellipse([x - r, y - r + wob, x + r, y + r + wob], fill=P["fat"], outline=P["fat_d"])
        d.point((x - r // 2, y - r // 2 + wob), fill=P["fat_l"])
    _face(d, 40, 22, mood, t)
    return outline(S)


def tongue(mood: str = "happy", t: float = 0.0) -> "gfx.Image.Image":
    S = gfx.new(48, 60)
    d = ImageDraw.Draw(S)
    wig = int(math.sin(t * 7) * 2)
    d.rounded_rectangle([6 + wig // 2, 6, 42 + wig // 2, 56], radius=16, fill=TONGUE)
    d.line([24 + wig // 2, 30, 24 + wig, 52], fill=TONGUE_D, width=2)
    for (x, y) in ((14, 40), (32, 42), (18, 48), (30, 50), (12, 32), (36, 34)):
        d.point((x + wig // 2, y), fill=TONGUE_L)
        d.point((x + 1 + wig // 2, y), fill=TONGUE_L)
    _face(d, 24 + wig // 2, 18, mood, t)
    return outline(S)


def speech(text: str, color=P["ink"], tail: str = "left") -> "gfx.Image.Image":
    """White speech bubble with a tail. Text is uppercase-friendly 5x7 font at scale 1."""
    w = text_width(text, 1) + 14
    b = gfx.new(w, 28)
    d = ImageDraw.Draw(b)
    d.rounded_rectangle([1, 1, w - 2, 19], radius=5, fill=P["white"])
    tx = 8 if tail == "left" else w - 16
    d.polygon([(tx, 19), (tx + 8, 19), (tx + (0 if tail == "left" else 10), 27)], fill=P["white"])
    draw_text(b, text, 7, 6, color=color)
    return outline(b)
