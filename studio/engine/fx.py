"""Stateless pixel particle effects (computed from elapsed time, so any frame renders alone)."""
from __future__ import annotations

import math
import random

from PIL import ImageDraw

from .gfx import P


def burst(img, x, y, dt, n=24, speed=60, gravity=90, life=0.9, colors=(P["gold"], P["white"]),
          seed=1, size=2, spread=math.tau, angle=-math.pi / 2):
    if dt < 0 or dt > life:
        return
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for i in range(n):
        a = angle + (rnd.random() - 0.5) * spread
        v = speed * (0.4 + rnd.random() * 0.8)
        px = x + math.cos(a) * v * dt
        py = y + math.sin(a) * v * dt + 0.5 * gravity * dt * dt
        k = 1 - dt / life
        s = max(1, int(round(size * (0.5 + k))))
        c = colors[i % len(colors)]
        px, py = int(px), int(py)
        d.rectangle([px, py, px + s - 1, py + s - 1], fill=c)


def smoke(img, x, y, dt, n=10, life=1.6, seed=4, rise=30, color=P["fog"]):
    if dt < 0 or dt > life:
        return
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for i in range(n):
        st = rnd.random() * 0.4
        lt = dt - st
        if lt < 0:
            continue
        k = lt / life
        px = x + (rnd.random() - 0.5) * 30 * k + math.sin(lt * 3 + i) * 3
        py = y - rise * lt - rnd.random() * 6
        r = int(3 + 9 * k)
        if k < 1:
            d.ellipse([px - r, py - r, px + r, py + r], outline=color)


def drips(img, x0, x1, y, dt, n=7, seed=2, color=P["fat"], dark=P["fat_d"]):
    """Gooey drips falling from a surface."""
    if dt < 0:
        return
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for i in range(n):
        st = rnd.random() * 0.6
        lt = dt - st
        if lt < 0:
            continue
        x = x0 + (x1 - x0) * rnd.random()
        ln = min(10, lt * 30)
        drop_y = y + ln + 0.5 * 260 * max(0, lt - 0.35) ** 2
        d.line([x, y, x, y + ln], fill=color, width=2)
        d.ellipse([x - 2, drop_y - 1, x + 2, drop_y + 3], fill=color)
        d.point((x - 1, drop_y), fill=dark)


def speed_lines(img, cx, cy, t, n=28, r0=70, color=P["white"], seed=8):
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed + int(t * 15))
    for _ in range(n):
        a = rnd.random() * math.tau
        r = r0 + rnd.random() * 120
        ln = 12 + rnd.random() * 30
        d.line([cx + math.cos(a) * r, cy + math.sin(a) * r, cx + math.cos(a) * (r + ln),
                cy + math.sin(a) * (r + ln)], fill=color)


def sparkles(img, cx, cy, t, n=8, radius=30, seed=6, color=P["gold"]):
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for i in range(n):
        a = rnd.random() * math.tau + t * 0.6
        r = radius * (0.5 + rnd.random() * 0.6)
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        ph = (t * 3 + i * 0.37) % 1
        s = 1 if ph < 0.5 else 2
        if ph < 0.85:
            d.line([x - s, y, x + s, y], fill=color)
            d.line([x, y - s, x, y + s], fill=color)
