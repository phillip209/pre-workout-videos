"""Cinematic director for native 1080x1920 episodes: scene timeline, narrative transitions, grade, captions.

Transitions (all motivated by the story, no generic glitches):
  dive   — the camera flies INTO a point of the previous shot (e.g. the abdomen) and the next world
           opens from that point as an expanding window, already in motion.
  bridge — a glucose particle at `point` flares and becomes the next shot.
  cut    — hard cut on action.
  fade   — short cross-dissolve (used for time jumps only).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Callable

from PIL import Image, ImageDraw

from .core import W, H, C, rgba, ease_io, ease_out, ease_in, clamp, lerp, font, film_grade
from ..director import chunk_words
from ..timeline import norm


@dataclass
class Shot:
    id: str
    start: float
    draw: Callable[[float], Image.Image]    # global time -> RGB W x H
    trans: str = "cut"
    dur: float = 0.0
    point: tuple = (W / 2, H / 2)


def _zoom(img, k, px, py):
    if abs(k - 1) < 1e-3:
        return img
    cw, ch = W / k, H / k
    x0 = clamp(px - cw * px / W, 0, W - cw)
    y0 = clamp(py - ch * py / H, 0, H - ch)
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)


def _circle_mask(cx, cy, r):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    return m


class CineDirector:
    def __init__(self, tl, shots: list[Shot], emph: dict[str, tuple], caption_y=1300, max_chars=18):
        self.tl = tl
        self.shots = sorted(shots, key=lambda s: s.start)
        self.emph = emph
        self.cy = caption_y
        self.chunks = chunk_words(tl, max_chars=max_chars)
        # build.py --silent sets spoken_dim = base: captions then show each chunk fully (no karaoke)
        self.sub = SimpleNamespace(base=1, spoken_dim=0, active=0)

    def shot_at(self, t):
        cur = self.shots[0]
        for s in self.shots:
            if s.start <= t:
                cur = s
        return cur

    def frame(self, t: float) -> Image.Image:
        sh = self.shot_at(t)
        img = sh.draw(t)
        i = self.shots.index(sh)
        if i > 0 and sh.trans != "cut" and t - sh.start < sh.dur:
            p = (t - sh.start) / sh.dur
            prev = self.shots[i - 1].draw(t)
            px, py = sh.point
            if sh.trans == "dive":
                a = _zoom(prev, 1 + 2.4 * ease_in(p), px, py)
                b = _zoom(img, 1.6 - 0.6 * ease_out(p), W / 2, H / 2)
                r = lerp(10, math.hypot(W, H), ease_io(p))
                a.paste(b, (0, 0), _circle_mask(px, py, r))
                img = a
            elif sh.trans == "bridge":
                flare = Image.new("RGB", (W, H), (0, 0, 0))
                fd = ImageDraw.Draw(flare)
                fr = lerp(20, 900, ease_in(min(1, p * 1.6)))
                for k in range(8, 0, -1):
                    rr = fr * k / 8
                    c = tuple(int(v * (1 - k / 9)) for v in C["orange_l"])
                    fd.ellipse([px - rr, py - rr, px + rr, py + rr], fill=c)
                base = Image.blend(prev, img, ease_io(clamp((p - 0.45) / 0.55)))
                from PIL import ImageChops
                img = ImageChops.screen(base, Image.eval(flare, lambda v: int(v * (1 - abs(p - 0.5) * 1.6) if p < 0.9 else 0)))
            elif sh.trans == "fade":
                img = Image.blend(prev, img, ease_io(p))
        img = film_grade(img, t)
        self._captions(img, t)
        return img

    # ---------------------------------------------------------------- captions
    def _captions(self, img, t):
        silent = self.sub.spoken_dim == self.sub.base
        for (s, e, words) in self.chunks:
            if not (s <= t < e):
                continue
            shown = words if silent else [w for w in words if w.start <= t + 0.05] or words[:1]
            toks = [(w.text.upper(), self.emph.get(norm(w.text))) for w in shown]
            p = ease_out(clamp((t - s) / 0.18))
            self._draw_line(img, toks, self.cy + (1 - p) * 26, p)
            break

    def _draw_line(self, img, toks, y, alpha):
        size = 66
        f = font(size, "bold")
        space = f.getlength(" ")
        lines, cur, wsum = [], [], 0.0
        for tok in toks:
            w = f.getlength(tok[0])
            if cur and wsum + space + w > 900:
                lines.append(cur)
                cur, wsum = [], 0.0
            cur.append((tok, w))
            wsum += (space if len(cur) > 1 else 0) + w
        if cur:
            lines.append(cur)
        d = ImageDraw.Draw(img, "RGBA")
        for li, line in enumerate(lines):
            total = sum(w for _, w in line) + space * (len(line) - 1)
            x = W / 2 - total / 2
            yy = y + li * (size + 18)
            for (word, col), w in line:
                if col:
                    d.rounded_rectangle([x - 14, yy - size * 0.62, x + w + 14, yy + size * 0.62], radius=14,
                                        fill=rgba(col, 0.95 * alpha))
                d.text((x, yy), word, font=f, anchor="lm", fill=rgba(C["white"], alpha), stroke_width=7,
                       stroke_fill=rgba(C["ink"], alpha))
                x += w + space
