"""Shared helpers for episodes: labels, pops, bars, arrows, charts, verdict stamps, end card."""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

from . import W, H
from . import gfx, cast, fx
from .gfx import P, prog, ease_out, ease_back, ease_in, clamp, lerp, paste
from .font import draw_text, text_width

VERDICT_COLORS = {"MITO": P["red"], "VERDAD": P["green_d"], "PARCIALMENTE CIERTO": P["gold_d"],
                  "ENGAÑOSO": P["orange"], "HUMO": P["steel_d"]}


def blinking(t, period=3.1, off=0.0):
    return ((t + off) % period) < 0.12


def label(img, text, x, y, color=P["white"], scale=1, center=True, outline=P["ink"]):
    draw_text(img, text, x, y, color=color, scale=scale, outline=outline, align="center" if center else "left")


def pop_scale(t, start, dur=0.25):
    p = prog(t, start, dur)
    return ease_back(p) if p > 0 else 0.0


def paste_scaled(img, spr, x, y, s, anchor="center"):
    if s <= 0.02:
        return
    paste(img, spr, x, y, scale=s, anchor=anchor)


def arrow(img, x, y, up=True, color=P["red"], size=8):
    d = ImageDraw.Draw(img)
    if up:
        d.polygon([(x, y - size), (x - size, y), (x + size, y)], fill=color)
        d.rectangle([x - size // 3, y, x + size // 3, y + size], fill=color)
    else:
        d.polygon([(x, y + size), (x - size, y), (x + size, y)], fill=color)
        d.rectangle([x - size // 3, y - size, x + size // 3, y], fill=color)


def bar(img, x, y, w, h, frac, color, back=P["ink"], label_txt=None):
    d = ImageDraw.Draw(img)
    d.rectangle([x - 1, y - 1, x + w + 1, y + h + 1], fill=P["white"])
    d.rectangle([x, y, x + w, y + h], fill=back)
    fw = int(w * clamp(frac))
    if fw > 0:
        d.rectangle([x, y, x + fw, y + h], fill=color)
        d.rectangle([x, y, x + fw, y + 1], fill=gfx.lerpc(color, P["white"], 0.4))
    for sx in range(x + 8, x + w, 8):
        d.line([sx, y, sx, y + h], fill=back)
    if label_txt:
        draw_text(img, label_txt, x, y - 12, color=P["white"], outline=P["ink"])


def text_sprite(text, color, scale=2, outline=P["ink"]):
    spr = gfx.new(text_width(text, scale) + 6, 9 * scale + 6)
    draw_text(spr, text, 3, 2, color=color, scale=scale, outline=outline)
    return spr


def verdict_sprite(verdict: str, scale=2):
    col = VERDICT_COLORS.get(verdict, P["red"])
    words = verdict.split()
    if len(words) > 1 and text_width(verdict, scale) > 150:
        # two-line stamp
        lines = [text_sprite(w, col, scale=scale, outline=None) for w in words]
        wmax = max(s.width for s in lines)
        box = gfx.new(wmax, sum(s.height for s in lines))
        y = 0
        for s in lines:
            box.alpha_composite(s, ((wmax - s.width) // 2, y))
            y += s.height
        return cast.stamp(box, col)
    return cast.stamp(text_sprite(verdict, col, scale=scale, outline=None), col)


def stamp_slam(out, verdict, t, t0, x=135, y=120, final_scale=2.0):
    """Big verdict stamp slamming down at t0 with dust."""
    if t < t0:
        return
    sp = verdict_sprite(verdict)
    final_scale = min(final_scale, 240 / sp.width)  # keep long verdicts inside the frame
    s = lerp(final_scale * 2.0, final_scale, ease_in(prog(t, t0, 0.22)))
    paste(out, sp, x, y, scale=s / 1.0 if s > 0 else 1, anchor="center")
    fx.burst(out, x, y + 30, t - t0 - 0.22, n=20, speed=90, gravity=60, life=0.8,
             colors=(P["fog"], P["white"]), seed=9, size=2)


def line_chart(img, box, pts, progress, color=P["gold"], axis=P["fog"], dot=True, fill=None):
    """Draw a polyline chart (pts in 0..1 data space) revealed up to `progress` (0..1)."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.line([x0, y0, x0, y1, x1, y1], fill=axis, width=1)
    n = len(pts)
    upto = progress * (n - 1)
    xy = []
    for i in range(n):
        if i > upto + 1e-6:
            # interpolate the partial segment
            if i - 1 <= upto:
                f = upto - (i - 1)
                px = lerp(pts[i - 1][0], pts[i][0], f)
                py = lerp(pts[i - 1][1], pts[i][1], f)
                xy.append((x0 + px * (x1 - x0), y1 - py * (y1 - y0)))
            break
        xy.append((x0 + pts[i][0] * (x1 - x0), y1 - pts[i][1] * (y1 - y0)))
    if fill and len(xy) > 1:
        d.polygon(xy + [(xy[-1][0], y1), (xy[0][0], y1)], fill=fill)
    if len(xy) > 1:
        d.line(xy, fill=color, width=2)
    if dot and xy:
        hx, hy = xy[-1]
        d.rectangle([hx - 2, hy - 2, hx + 2, hy + 2], fill=P["white"])
    return xy


def badge(text, icon=None, color=P["white"]):
    w = text_width(text, 1) + (34 if icon is not None else 14)
    b = gfx.new(w, 26)
    d = ImageDraw.Draw(b)
    d.rounded_rectangle([0, 0, w - 1, 25], radius=5, fill=P["ink"], outline=P["fog"])
    x = 7
    if icon is not None:
        b.alpha_composite(icon, (5, (26 - icon.height) // 2))
        x = 9 + icon.width
    draw_text(b, text, x, 8, color=color)
    return b


def end_card(img, t, t_cta, t_word, verdict, chars=("fiber", "fat"), seed_t=0.0):
    """Shared closing card: logo, two mascots, share arrow, verdict badge."""
    lp = pop_scale(t, t_cta, 0.3)
    logo = gfx.new(200, 60)
    draw_text(logo, "PRE-WORKOUT", 100, 4, color=P["gold"], scale=2, outline=P["ink"], align="center",
              wave=(1, 6), t=t)
    draw_text(logo, "FITNESS SIN HUMO", 100, 32, color=P["fog"], outline=P["ink"], align="center")
    paste_scaled(img, logo, 135, 90, lp, anchor="center")
    fib = cast.muscle_fiber(50, 16, mood="proud", nuclei=4, t=t, glow=0.5, blink=blinking(t, 2.0))
    paste(img, fib, 80, 200 + math.sin(t * 4) * 3, scale=2, anchor="center")
    fat = cast.fat_cell(15, mood="happy", t=t, wobble=0.3, blink=blinking(t, 2.4, 1))
    paste(img, fat, 200, 205 + math.cos(t * 4) * 3, scale=2, anchor="center")
    if t > t_word:
        b = abs(math.sin((t - t_word) * 6)) * 6
        share = gfx.new(40, 30)
        sd = ImageDraw.Draw(share)
        sd.polygon([(24, 2), (38, 12), (24, 22), (24, 16), (16, 16), (8, 19), (3, 27), (3, 20),
                    (8, 12), (16, 8), (24, 8)], fill=P["gold"])
        sd.line([(25, 5), (34, 12)], fill=P["fat_l"])
        paste(img, gfx.outline(share), 135, 270 - b, scale=2, anchor="center")
    paste(img, verdict_sprite(verdict, scale=1), 135, 322, scale=1, anchor="center")


def scenes_from(tl, spec):
    """spec = [(scene_id, line_id, draw_fn(g), transition, trans_dur, lead)] -> Scene list.
    draw_fn receives GLOBAL time; the scene starts `lead` seconds before its line."""
    from .director import Scene

    out = []
    for i, (sid, lid, fn, trans, tdur, lead) in enumerate(spec):
        start = 0.0 if i == 0 else tl.line(lid).start - lead
        out.append(Scene(sid, start, (lambda f: (lambda a, g: f(g)))(fn), trans=trans, trans_dur=tdur))
    return out


def hook_camera(img, g, t0=0.0, punch=1.35, cx=W / 2, cy=H / 2):
    """Punch-in at the very start of a video + speed lines (3-second rule)."""
    z = lerp(punch, 1.0, ease_out(prog(g, t0, 0.45)))
    out = gfx.camera(img, z, cx, cy)
    if g - t0 < 0.35:
        fx.speed_lines(out, cx, cy, g, n=30)
    return out


def street_bg(g, scroll=0.0, tod="night"):
    """City sidewalk with parallax scroll (for walking scenes)."""
    img = gfx.new(W, H, P["night"] + (255,))
    if tod == "sunrise":
        sky = [(0, P["violet"]), (0.6, P["pink"]), (1, P["orange"])]
    else:
        sky = [(0, P["ink"]), (0.7, P["deep"]), (1, P["violet"])]
    gfx.vgradient(img, (0, 0, W, 300), sky)
    d = ImageDraw.Draw(img)
    import random as _r
    for layer, (spd, col, hmin, hmax, wy) in enumerate(((0.2, P["deep"] if tod != "sunrise" else (110, 70, 120), 60, 140, 300),
                                                          (0.5, P["night"], 40, 110, 300))):
        rnd = _r.Random(layer + 3)
        x = -((scroll * spd) % 40) - 40
        while x < W + 40:
            bw = rnd.randint(22, 40)
            bh = rnd.randint(hmin, hmax)
            d.rectangle([x, wy - bh, x + bw, wy], fill=col)
            if layer == 1:
                for yy in range(wy - bh + 6, wy - 6, 8):
                    for xx in range(int(x) + 4, int(x) + bw - 4, 7):
                        if rnd.random() < (0.35 if tod != "sunrise" else 0.1):
                            d.rectangle([xx, yy, xx + 2, yy + 3], fill=P["gold"])
            x += bw + rnd.randint(2, 8)
    if tod == "sunrise":
        d.ellipse([170, 200, 230, 260], fill=P["gold"])
        d.rectangle([0, 240, W, 300], fill=(110, 70, 120))
    # sidewalk + road
    d.rectangle([0, 300, W, 345], fill=P["steel_d"])
    off = int(scroll) % 30
    for x in range(-off, W, 30):
        d.line([x, 300, x - 10, 345], fill=P["steel"])
    d.rectangle([0, 345, W, H], fill=P["ink"])
    for x in range(-(int(scroll * 1.5) % 40), W, 40):
        d.rectangle([x, 400, x + 20, 403], fill=P["gold_d"])
    # lamp posts
    for x in range(-(int(scroll) % 120) + 60, W + 60, 120):
        d.rectangle([x, 200, x + 3, 300], fill=P["steel_d"])
        d.rectangle([x - 6, 196, x + 9, 200], fill=P["steel"])
        if tod != "sunrise":
            d.rectangle([x - 4, 200, x + 7, 202], fill=P["fat_l"])
    return img
