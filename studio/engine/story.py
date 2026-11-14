"""Reusable scene builders for the approved story format (template: episodes/b01v2_azucar).

Every builder returns a draw function f(g) -> RGBA frame (g = global time) for kit.scenes_from().
Layout contract (270x480 canvas): HUD y 8-50, sources y 58, impact text y 88-160, characters
y 140-345, subtitles y ~356; nothing important in the bottom 15 %.

Story beats: hook close-up (open loop) -> context walk -> villain rises -> x-ray turn -> inner metric ->
villain lurks -> slow-mo setup -> reveal close-up (pays the hook) -> honest twist + CTA (loops to frame 1).
"""
from __future__ import annotations

import math
from typing import Callable

from PIL import ImageDraw

from . import W, H, gfx, fx, cast, hud, organs
from . import cast_plus as cp
from . import cast_villains as cv
from .gfx import P, prog, ease_out, ease_io, ease_back, ease_in, lerp, paste, clamp
from .kit import label, pop_scale, paste_scaled, impact_text, count_text, xray, blinking


# ------------------------------------------------------------------ helpers
def leo(pose=None, t=0.0):
    """Full-body Leo with breathing bob and blinks (never on frame 1)."""
    p = {"mouth": "smile", "bob": math.sin(t * 2.4) * 0.8}
    p.update(pose or {})
    if p.get("eyes", "open") == "open" and blinking(t, 3.1, 1.3):
        p["eyes"] = "blink"
    return cast.hero(p)


def source(img, text):
    label(img, text, 135, 58, color=P["fog"])


def texts_layer(img, g, texts):
    """texts = [(t_in, t_out|None, text, color, scale, y)]: impact words drawn on the final frame."""
    for (t0, t1, txt, col, sc, y) in texts:
        if g < t0 or (t1 is not None and g > t1 + 0.2):
            continue
        impact_text(img, txt, 135, y, g, t0, color=col, scale=sc, out_t=t1)


def cross(d, x, y, r=18):
    for w, c in ((7, P["ink"]), (4, P["red"])):
        d.line([x - r, y - r, x + r, y + r], fill=c, width=w)
        d.line([x + r, y - r, x - r, y + r], fill=c, width=w)


def check(d, x, y):
    for w, c in ((7, P["ink"]), (4, P["green"])):
        d.line([x - 14, y + 2, x - 4, y + 12, x + 16, y - 14], fill=c, width=w)


class Hud:
    """Counter at the top. keys = [(t, value[, race_dur])]; fmt like 'NOCHE {n}' or text_fn(g) -> str."""

    def __init__(self, keys, max_value, fmt="DÍA {n}", flashes=(), text_fn: Callable | None = None):
        self.keys, self.max, self.fmt, self.flashes, self.text_fn = keys, max_value, fmt, flashes, text_fn

    def __call__(self, img, g):
        v = hud.count_day(g, self.keys)
        fl = 0.0
        for tt in self.flashes:
            if 0 <= g - tt < 0.4:
                fl = 1 - (g - tt) / 0.4
        layer = gfx.new()
        hud.day_counter(layer, v, self.max, g, flash=fl, fmt=self.fmt,
                        text=self.text_fn(g) if self.text_fn else None)
        img.alpha_composite(layer)


# ------------------------------------------------------------------ 1. hook close-up
def hook_closeup(bg: Callable, hudl: Hud, beats, texts, t_punch, side=None):
    """bg(g) -> image. beats = [(t, mood, tongue_out)] (last one whose t <= g wins).
    side = (t_in, t_out, sprite_fn(g), t_cross) — an icon beside Leo that gets crossed out.
    t_punch = snap zoom to the mouth/face with glitch."""
    def f(g):
        img = bg(g)
        mood, tongue = "neutral", 0.0
        for (t, m, tg) in beats:
            if g >= t:
                mood, tongue = m, tg
        tg_k = ease_back(prog(g, t_punch - 0.1, 0.3)) * tongue if g > t_punch - 0.1 else 0
        look = math.sin(g * 1.3) * 0.6 if g < t_punch - 1.5 else 0
        face = cp.leo_face(mood, g, blink=g < t_punch - 0.3 and blinking(g, 2.7, 1.3), look=look, tongue_out=tg_k, sweat=g > t_punch)
        paste(img, face, 135, 345, scale=2.0)
        if side and side[0] - 0.1 < g < side[1]:
            s = pop_scale(g, side[0] - 0.1)
            paste_scaled(img, side[2](g), 236, 250, s * 2.2)
            if g > side[3]:
                cross(ImageDraw.Draw(img), 236, 230, 22)
        z = lerp(1.25, 1.0, ease_out(prog(g, 0, 0.45))) + 0.04 * prog(g, 0.5, 5.0)
        cy = 240
        if g > t_punch - 0.1:
            k = ease_out(prog(g, t_punch - 0.1, 0.25))
            z += 0.3 * k
            cy = lerp(240, 290, k)
        out = gfx.camera(img, z, 135, cy, shake=2.5 if 0 <= g - t_punch < 0.25 else 0, t=g)
        if g < 0.3:
            fx.speed_lines(out, 135, 240, g, n=30)
        if 0 <= g - t_punch < 0.15:
            out = gfx.chroma_glitch(out, 6, g)
        texts_layer(out, g, texts)
        hudl(out, g)
        return out
    return f


# ------------------------------------------------------------------ 2. context walk
def context_walk(bg: Callable, hudl: Hud, t0, t_stop, items, texts, rewind=True, grab=None, walk_px=140):
    """bg(g, scroll) -> image. items = [(t, sprite, x, ok)] pop above Leo with ✓/✗.
    grab = (t, item_index): that item flies into Leo's hand."""
    def f(g):
        scroll = 30 + walk_px * ease_io(prog(g, t0, max(0.5, t_stop - t0)))
        img = bg(g, scroll)
        walking = g < t_stop
        gk = ease_back(prog(g, grab[0] - 0.25, 0.3)) if grab else 0
        pose = {"walk": g * 12 if walking else None, "mouth": "grit" if walking else "grin",
                "arm_l": (20 * math.sin(g * 12), 30) if walking else (10, 10),
                "arm_r": (-20 * math.sin(g * 12), 30) if walking else (lerp(10, 150, gk), lerp(10, 30, gk))}
        paste(img, leo(pose, g), 120, 336, scale=2.6)
        d = ImageDraw.Draw(img)
        for i, (tt, spr, x, ok) in enumerate(items):
            s = pop_scale(g, tt)
            if s <= 0:
                continue
            yy = 122 + math.sin(g * 4 + x) * 3
            if grab and grab[1] == i and g > grab[0] - 0.25:
                k = ease_in(prog(g, grab[0] - 0.25, 0.3))
                if k < 1:
                    paste_scaled(img, spr, lerp(x, 150, k), lerp(yy, 190, k), s * 2.2)
                continue
            paste_scaled(img, spr, x, yy, s * 2.2)
            if g > tt + 0.12 and ok is not None:
                (check if ok else cross)(d, x, yy)
        out = img
        texts_layer(out, g, texts)
        if rewind:
            rw = 1 - prog(g, t0 - 0.3, 0.75)
            if rw > 0:
                out = cp.vhs_rewind(out, rw, g)
        hudl(out, g)
        return out
    return f


# ------------------------------------------------------------------ 3. villain rises
def villain_rise(bg: Callable, hudl: Hud, kind, t_mon, t_calm, leo_pose: Callable, bars=(), popups=(), texts=(),
                 src=None, villain_xy=(180, 175), villain_scale=1.9, dark=0.35):
    """bars = [(t, name, v0, v1, color, delta, x)]; popups = [(t, sprite_fn(g), x, y, scale)].
    leo_pose(g, scared:bool) -> pose dict."""
    def f(g):
        img = bg(g)
        if dark:
            img = gfx.darken(img, dark)
        grow = ease_back(prog(g, t_mon - 0.35, 0.5))
        if grow > 0:
            mood = "roar" if g < t_calm else ("jitter" if kind == "cafeina" else "sly")
            m = cv.villain(kind, mood, g, glow=0.7 + 0.3 * math.sin(g * 6))
            sh = m.copy()
            sh.putdata([(10, 6, 20, a // 2) for (_, _, _, a) in sh.getdata()])
            paste(img, sh, villain_xy[0] + 10, villain_xy[1] - 25, scale=villain_scale * 1.35 * grow, anchor="center")
            paste(img, m, villain_xy[0] + math.sin(g * 2) * 4, villain_xy[1], scale=villain_scale * grow, anchor="center")
        paste(img, leo(leo_pose(g, g > t_mon), g), 80, 336, scale=2.5)
        for (tt, spr_fn, x, y, sc) in popups:
            if g > tt - 0.15:
                paste_scaled(img, spr_fn(g), x, y + math.sin(g * 9) * 2, pop_scale(g, tt - 0.15) * sc)
        for (tt, name, v0, v1, col, dl, x) in bars:
            hud.stat_bar(img, x, 70, 110, name, lerp(v0, v1, ease_out(prog(g, tt, 0.5))), col, g, delta=dl,
                         appear=prog(g, tt - 0.2, 0.3))
        if src:
            source(img, src)
        z = 1.0 + 0.05 * prog(g, t_mon - 1, 3.0)
        out = gfx.camera(img, z, 135, 230, shake=3 if 0 <= g - t_mon < 0.45 else 0, t=g)
        texts_layer(out, g, texts)
        hudl(out, g)
        return out
    return f


# ------------------------------------------------------------------ 4. x-ray turn
def xray_turn(bg_out: Callable, hudl: Hud, t0, inner: Callable, texts=(), leo_pose=None):
    def f(g):
        outside = bg_out(g)
        paste(outside, leo(leo_pose or {"mouth": "flat"}, g), 135, 336, scale=2.6)
        out = xray(outside, inner(g), 140, 255, prog(g, t0, 1.0))
        texts_layer(out, g, texts)
        hudl(out, g)
        return out
    return f


# ------------------------------------------------------------------ 5. inner metric
def inner_metric(bg: Callable, hudl: Hud, draw_inner: Callable, texts=(), src=None):
    """draw_inner(img, g) paints organs/bars/counters; texts drawn on top."""
    def f(g):
        img = bg(g)
        draw_inner(img, g)
        if src:
            source(img, src)
        texts_layer(img, g, texts)
        hudl(img, g)
        return img
    return f


# ------------------------------------------------------------------ 6. villain lurks
def lurk(bg: Callable, hudl: Hud, kind, t0, t_peek, texts=(), pages=True, page_base=10, villain_mood="wink"):
    """bg(g, scroll). Leo walks; the villain peeks in from the left on t_peek; calendar pages fly."""
    def f(g):
        img = bg(g, (g - t0) * 70)
        paste(img, leo({"walk": g * 12, "mouth": "smile", "arm_l": (20 * math.sin(g * 12), 30),
                        "arm_r": (-20 * math.sin(g * 12), 30), "look": -1 if g > t_peek else 0}, g), 160, 330, scale=2.4)
        peek = ease_back(prog(g, t_peek - 0.1, 0.3))
        mx = lerp(-50, 60, peek) if g < t_peek + 1.2 else lerp(60, -70, ease_in(prog(g, t_peek + 1.2, 0.4)))
        paste(img, cv.villain(kind, villain_mood if g > t_peek + 0.3 else "sly", g), mx, 230, scale=1.3, anchor="center")
        if pages and g > t_peek:
            for i in range(8):
                ph = ((g - t0) * 1.6 + i * 0.13) % 1
                paste(img, cp.calendar_page(page_base + i * 3), W + 20 - ph * (W + 60), 120 + (i * 37) % 160,
                      scale=1.2, anchor="center")
        texts_layer(img, g, texts)
        hudl(img, g)
        return img
    return f


# ------------------------------------------------------------------ 7. slow-mo setup
def slowmo(bg: Callable, hudl: Hud, t0, leo_pose: Callable, props=(), texts=(), zoom_to=(140, 215), zoom=0.4,
           zoom_dur=1.3):
    """leo_pose(k) with k 0..1 progress; props = [(sprite_fn(g, k), x_fn(k), y_fn(k), scale)]."""
    def f(g):
        img = bg(g)
        k = ease_io(prog(g, t0 - 0.2, 1.2))
        paste(img, leo(leo_pose(k), g), 135, 336, scale=2.6)
        for (spr_fn, xf, yf, sc) in props:
            paste(img, spr_fn(g, k), xf(k), yf(k), scale=sc, anchor="center")
        out = gfx.camera(img, 1.0 + zoom * ease_in(prog(g, t0, zoom_dur)), zoom_to[0], zoom_to[1])
        texts_layer(out, g, texts)
        hudl(out, g)
        return out
    return f


# ------------------------------------------------------------------ 8. reveal close-up
def reveal_closeup(bg: Callable, hudl: Hud, t_hit, gauge_cfg, texts=(), mood_pre="taste", mood_hit="shock",
                   tongue=0.0, popup=None, src=None):
    """gauge_cfg = (label, v0, v1, t_start). popup = (t, sprite_fn(g), bubble_text)."""
    def f(g):
        img = bg(g)
        hit = g > t_hit - 0.05
        face = cp.leo_face(mood_pre if not hit else mood_hit, g,
                           tongue_out=ease_back(prog(g, t_hit - 0.05, 0.3)) * tongue if hit else 0,
                           blink=(not hit) and blinking(g, 2.7, 1.3))
        paste(img, face, 95, 345, scale=2.0)
        lbl, v0, v1, ts = gauge_cfg
        val = lerp(v0, v1, ease_back(prog(g, ts, 1.2))) if g > ts else v0
        paste(img, cp.gauge(val, g, lbl), 205, 300, scale=1.15, anchor="center")
        if hit:
            fx.sparkles(img, 95, 280, g, n=10, radius=60, color=P["gold"])
        if popup and g > popup[0] - 0.1:
            paste_scaled(img, popup[1](g), 222, 205, pop_scale(g, popup[0] - 0.1) * 1.1)
            paste_scaled(img, organs.speech(popup[2], tail="right"), 180, 150, pop_scale(g, popup[0]) * 1.2)
        if src:
            source(img, src)
        out = gfx.camera(img, 1.0 + (0.08 if 0 <= g - t_hit < 0.2 else 0), 135, 240,
                         shake=3 if 0 <= g - t_hit < 0.3 else 0, t=g)
        if 0 <= g - t_hit < 0.08:
            out = gfx.flash(out, 0.6, (255, 240, 220))
        texts_layer(out, g, texts)
        hudl(out, g)
        return out
    return f


# ------------------------------------------------------------------ 9. twist + CTA (loops to the hook framing)
def twist_loop(bg: Callable, hudl: Hud, kind, t_ojo, t_drop, t_cta, cta_lines, ojo_text="¡OJO!", gauge_cfg=None,
               src=None, villain_mood="wink", extra_texts=()):
    """bg must be the hook background so the last frame matches the first. gauge_cfg = (label, v0, v1)."""
    def f(g):
        img = bg(g)
        face = cp.leo_face("shock" if t_ojo < g < t_drop + 0.3 else ("sly" if g < t_cta else "neutral"), g,
                           blink=blinking(g, 2.7, 1.3), look=-1 if t_ojo < g < t_cta else 0)
        slide = ease_io(prog(g, t_ojo - 0.1, 0.3)) * (1 - ease_io(prog(g, t_cta, 0.35)))
        paste(img, face, 135 + 22 * slide, 345, scale=2.0)
        if g < t_cta + 0.4:
            pk = ease_back(prog(g, t_ojo - 0.1, 0.35))
            mx = lerp(-60, 55, pk) - 140 * ease_in(prog(g, t_cta, 0.35))
            paste(img, cv.villain(kind, villain_mood, g), mx, 168, scale=1.3, anchor="center")
        if gauge_cfg and t_ojo < g < t_cta:
            lbl, v0, v1 = gauge_cfg
            gv = lerp(v0, v1, ease_io(prog(g, t_drop - 0.2, 0.6)))
            paste(img, cp.gauge(gv, g, lbl), 52, 300, scale=0.8, anchor="center")
        if src and t_ojo < g < t_cta:
            source(img, src)
        out = gfx.camera(img, 1.0 + 0.04 * prog(g, t_ojo, 3.0), 135, 240, t=g)
        if t_ojo < g < t_cta:
            impact_text(out, ojo_text, 135, 96, g, t_ojo, color=P["red_l"], scale=6 if len(ojo_text) < 7 else 3)
        texts_layer(out, g, extra_texts)
        if g > t_cta:
            (l1, c1), (l2, c2) = cta_lines
            impact_text(out, l1, 135, 88, g, t_cta, color=c1, scale=3)
            impact_text(out, l2, 135, 122, g, t_cta + 0.12, color=c2, scale=4)
        hudl(out, g)
        return out
    return f
