"""Video-game HUD for the "¿Qué le pasa a tu cuerpo si…?" format: day counter + RPG stat bars.

Layout contract: the HUD lives in y < 70 (counter) or in a side column; impact text uses 90..300 and
subtitles y >= 352.
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from . import W
from . import gfx
from .gfx import P, clamp, ease_io, ease_back, prog, lerp
from .font import draw_text, text_width


def count_day(t: float, keys: list[tuple], dur: float = 0.6) -> float:
    """Day value at time t. keys = [(time, day)] or [(time, day, race_dur)] sorted by time; the counter
    races to each key's day over its race_dur (default `dur`) seconds, eased, so jumps like 3 -> 10 -> 90
    read as fast counting, never teleporting."""
    if not keys or t <= keys[0][0]:
        return float(keys[0][1]) if keys else 1.0
    day = float(keys[0][1])
    for a, b in zip(keys, keys[1:]):
        t1, d1 = b[0], b[1]
        rd = b[2] if len(b) > 2 else dur
        if t >= t1:
            day = float(d1)
            continue
        if t >= t1 - rd:
            day = lerp(a[1], d1, ease_io(prog(t, t1 - rd, rd)))
        break
    return day


def day_counter(img, day: float, max_day: int, t: float, flash: float = 0.0, y: int = 8) -> None:
    """Big 'DÍA N' at the top centre with a progress bar underneath. flash 0..1 = bounce + gold tint."""
    n = int(round(day))
    txt = f"DÍA {n}"
    s = 3
    bump = 1 + 0.25 * math.sin(clamp(flash) * math.pi)
    spr = gfx.new(text_width(txt, s) + 8, 9 * s + 8)
    col = gfx.lerpc(P["white"], P["gold"], clamp(flash * 1.5))
    draw_text(spr, txt, 4, 3, color=col, scale=s, outline=P["ink"], shadow=True)
    gfx.paste(img, spr, W // 2, y + spr.height // 2, scale=bump, anchor="center")
    # progress bar
    d = ImageDraw.Draw(img)
    bw, bh = 150, 6
    x0, y0 = (W - bw) // 2, y + 36
    d.rectangle([x0 - 2, y0 - 2, x0 + bw + 2, y0 + bh + 2], fill=P["ink"])
    d.rectangle([x0, y0, x0 + bw, y0 + bh], fill=P["deep"])
    fw = int(bw * clamp(day / max_day))
    if fw > 0:
        d.rectangle([x0, y0, x0 + fw, y0 + bh], fill=P["green"])
        d.rectangle([x0, y0, x0 + fw, y0 + 1], fill=P["fat_l"])
    # tick marks + glint
    for i in range(1, 10):
        sx = x0 + bw * i // 10
        d.line([sx, y0, sx, y0 + bh], fill=P["ink"])
    gx = x0 + int((t * 60) % (bw + 40)) - 20
    if x0 <= gx <= x0 + fw:
        d.line([gx, y0, gx, y0 + bh], fill=P["white"])


def stat_bar(img, x: int, y: int, w: int, name: str, value: float, color, t: float,
             delta: float = 0.0, appear: float = 1.0) -> None:
    """RPG stat bar with label; delta>0 draws a green up-arrow, delta<0 a red down-arrow (pulsing).
    appear 0..1 slides the bar in from the left."""
    if appear <= 0:
        return
    ox = int(lerp(-w - 40, 0, ease_back(clamp(appear))))
    x = x + ox
    d = ImageDraw.Draw(img)
    draw_text(img, name, x, y, color=P["white"], scale=1, outline=P["ink"])
    by = y + 12
    h = 8
    d.rectangle([x - 2, by - 2, x + w + 2, by + h + 2], fill=P["ink"])
    d.rectangle([x, by, x + w, by + h], fill=P["deep"])
    fw = int(w * clamp(value))
    if fw > 0:
        d.rectangle([x, by, x + fw, by + h], fill=color)
        d.rectangle([x, by, x + fw, by + 2], fill=gfx.lerpc(color, P["white"], 0.45))
    for sx in range(x + 10, x + w, 10):
        d.line([sx, by, sx, by + h], fill=P["ink"])
    if abs(delta) > 0.01:
        up = delta > 0
        col = P["green"] if up else P["red"]
        ax = x + w + 10
        ay = by + 4 + int(math.sin(t * 10) * 2)
        if up:
            d.polygon([(ax, ay - 6), (ax - 5, ay), (ax + 5, ay)], fill=col)
            d.rectangle([ax - 2, ay, ax + 2, ay + 5], fill=col)
        else:
            d.polygon([(ax, ay + 6), (ax - 5, ay), (ax + 5, ay)], fill=col)
            d.rectangle([ax - 2, ay - 5, ax + 2, ay], fill=col)
