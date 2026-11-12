"""Scene sequencing, transitions and synced subtitles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from PIL import Image

from . import W, H
from . import gfx
from .font import draw_text, text_width
from .timeline import Timeline, norm


@dataclass
class Scene:
    id: str
    start: float
    draw: Callable[[float, float], Image.Image]   # (t_local, t_global) -> RGBA W x H
    trans: str = "cut"                             # transition INTO this scene
    trans_dur: float = 0.3
    end: float = 0.0


@dataclass
class SubStyle:
    y: int = 318
    scale: int = 2
    max_chars: int = 16
    base: tuple = gfx.P["white"]
    spoken_dim: tuple = (200, 196, 210)
    active: tuple = gfx.P["gold"]
    emph: dict = field(default_factory=dict)   # norm(word) -> colour
    outline: tuple = gfx.P["ink"]


def chunk_words(tl: Timeline, max_chars=16):
    """Group words into short subtitle chunks (<= max_chars, break after punctuation)."""
    chunks = []
    for ln in tl.lines:
        cur = []
        for w in ln.words:
            cand = " ".join(x.text for x in cur + [w])
            if cur and len(cand) > max_chars:
                chunks.append(cur)
                cur = []
            cur.append(w)
            if w.text.endswith((".", ",", "?", "!", ":", ";", "…")) and len(" ".join(x.text for x in cur)) >= 6:
                chunks.append(cur)
                cur = []
        if cur:
            chunks.append(cur)
    out = []
    for i, c in enumerate(chunks):
        start = c[0].start
        nxt = chunks[i + 1][0].start if i + 1 < len(chunks) else c[-1].end + 0.6
        end = min(nxt, c[-1].end + 0.6)
        out.append((start, end, c))
    return out


class Director:
    def __init__(self, tl: Timeline, scenes: list[Scene], sub: SubStyle, post=None):
        self.tl = tl
        self.scenes = sorted(scenes, key=lambda s: s.start)
        for i, s in enumerate(self.scenes):
            s.end = self.scenes[i + 1].start if i + 1 < len(self.scenes) else tl.total + 10
        self.sub = sub
        self.chunks = chunk_words(tl, sub.max_chars)
        self.post = post
        self._cache = {}

    def scene_at(self, t):
        cur = self.scenes[0]
        for s in self.scenes:
            if s.start <= t:
                cur = s
        return cur

    def frame(self, t: float) -> Image.Image:
        sc = self.scene_at(t)
        img = sc.draw(t - sc.start, t)
        i = self.scenes.index(sc)
        if i > 0 and sc.trans != "cut" and t - sc.start < sc.trans_dur:
            prev = self.scenes[i - 1]
            p = (t - sc.start) / sc.trans_dur
            a = prev.draw(t - prev.start, t)
            img = gfx.transition(a, img, sc.trans, p)
        if self.post:
            img = self.post(img, t)
        self.draw_subs(img, t)
        return img.convert("RGB")

    def draw_subs(self, img, t):
        st = self.sub
        for (s, e, words) in self.chunks:
            if not (s <= t < e):
                continue
            text = " ".join(w.text for w in words).upper()
            # per-character colours: emphasis > active word > spoken > upcoming
            cols = []
            for wi, w in enumerate(words):
                key = norm(w.text)
                if key in st.emph:
                    c = st.emph[key]
                elif w.start <= t < (words[wi + 1].start if wi + 1 < len(words) else e):
                    c = st.active
                elif t >= w.start:
                    c = st.base
                else:
                    c = st.spoken_dim
                cols.extend([c] * len(w.text))
                if wi + 1 < len(words):
                    cols.append(c)
            # pop-in animation
            p = gfx.prog(t, s, 0.12)
            dy = int(round((1 - gfx.ease_back(p)) * 6))
            key = (text, tuple(cols))
            spr = self._cache.get(key)
            if spr is None:
                tw = text_width(text, st.scale) + 8
                spr = gfx.new(tw, 9 * st.scale + 8)
                draw_text(spr, text, 4, 3, scale=st.scale, colors=cols, outline=st.outline,
                          shadow=st.outline)
                if len(self._cache) > 400:
                    self._cache.clear()
                self._cache[key] = spr
            img.alpha_composite(spr, (int(W / 2 - spr.width / 2), st.y + dy))
            break
