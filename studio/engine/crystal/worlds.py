"""Environments and interior (anatomical) worlds for the Leo Cristal format.

Backgrounds are painted once, blurred for depth of field (cached), then animated with light,
parallax and foreground props drawn sharp. Interior worlds are fully procedural per frame.
"""
from __future__ import annotations

import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

from .core import (W, H, C, Cam, Frame, rgba, lerp, lerpc, clamp, ease_io, ease_out, vgradient, glow_dot,
                   glow_line, soft_light, text)


# ---------------------------------------------------------------- helpers
def _blurred(img, r):
    return img.filter(ImageFilter.GaussianBlur(r))


def paste_bg(frame: Frame, bg: Image.Image, dx=0.0, dy=0.0, zoom=1.0):
    """Place a cached (oversized) background with parallax offset and zoom."""
    bw, bh = bg.size
    cw, ch = W / zoom, H / zoom
    x0 = (bw - cw) / 2 - dx
    y0 = (bh - ch) / 2 - dy
    crop = bg.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)
    frame.base.paste(crop)


def bokeh(frame: Frame, pts, t, col, r=22, a=0.35):
    lay = frame.layer()
    d = ImageDraw.Draw(lay)
    for i, (x, y) in enumerate(pts):
        rr = r * (0.7 + 0.3 * math.sin(t * 0.8 + i))
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=rgba(col, a * (0.6 + 0.4 * math.sin(t * 1.3 + i * 2.1))))
    frame.add_base(lay.filter(ImageFilter.GaussianBlur(4)))


# ---------------------------------------------------------------- dining room
@lru_cache(maxsize=2)
def _dining_bg():
    img = Image.new("RGBA", (W + 300, H + 300), (0, 0, 0, 255))
    vgradient(img, (0, 0, W + 300, H + 300), [(0, (34, 30, 38)), (0.55, (46, 36, 34)), (1, (20, 16, 18))])
    d = ImageDraw.Draw(img)
    # window with night city
    d.rectangle([760, 380, 1240, 1080], fill=(18, 26, 48, 255))
    rnd = random.Random(3)
    for _ in range(70):
        x, y = rnd.randint(780, 1220), rnd.randint(640, 1060)
        d.rectangle([x, y, x + 6, y + 10], fill=(255, 200, 120, 255) if rnd.random() < 0.6 else (150, 190, 255, 255))
    d.rectangle([760, 380, 1240, 1080], outline=(70, 56, 50, 255), width=18)
    d.line([1000, 380, 1000, 1080], fill=(70, 56, 50, 255), width=12)
    # shelves + plant silhouettes
    d.rectangle([60, 700, 420, 720], fill=(60, 44, 36, 255))
    for k in range(5):
        d.rectangle([90 + k * 60, 610 - (k % 2) * 30, 130 + k * 60, 700], fill=(80 + k * 10, 60, 50, 255))
    d.ellipse([90, 980, 330, 1260], fill=(30, 52, 40, 255))
    return _blurred(img, 9)


def dining(frame: Frame, t, dx=0.0, dy=0.0, zoom=1.0):
    paste_bg(frame, _dining_bg(), dx, dy, zoom)
    # pendant lamp: warm pool + visible fixture (sharp-ish)
    soft_light(frame, W / 2 + dx * 0.4, 520 + dy * 0.4, 700, C["orange_l"], 0.22)
    d = ImageDraw.Draw(frame.base)
    lx, ly = W / 2 + dx * 0.4, 200 + dy * 0.4
    d.line([lx, -10, lx, ly], fill=(30, 26, 26, 255), width=4)
    d.polygon([(lx - 90, ly + 70), (lx + 90, ly + 70), (lx + 40, ly), (lx - 40, ly)], fill=(60, 46, 40, 255))
    glow_dot(frame, lx, ly + 76, 30, C["orange_l"], 0.9)
    bokeh(frame, [(880 + dx * 0.6, 760 + dy * 0.6), (1010 + dx * 0.6, 900 + dy * 0.6), (940 + dx * 0.6, 1000 + dy * 0.6)],
          t, C["orange_l"], 26, 0.25)


def table_front(frame: Frame, cam: Cam, t, plate=1.0, steam=True, top_y=-40):
    """Foreground table top + plate in world coords (top surface at world y=top_y). Drawn over the body."""
    lay = frame.layer()
    d = ImageDraw.Draw(lay)
    x0, y0 = cam.p(-900, top_y)
    x1, y1 = cam.p(900, top_y + 600)
    d.rectangle([x0, y0, x1, y1], fill=(64, 40, 30, 255))
    d.rectangle([x0, y0, x1, y0 + cam.s(14)], fill=(110, 72, 52, 255))
    for k in range(6):   # wood grain
        gy = y0 + cam.s(40 + k * 70)
        d.line([x0, gy, x1, gy + cam.s(10)], fill=(56, 34, 26, 255), width=max(1, int(cam.s(3))))
    # plate + food
    px, py = cam.p(0, top_y + 70)
    rx, ry = cam.s(190), cam.s(52)
    d.ellipse([px - rx, py - ry, px + rx, py + ry], fill=(236, 236, 240, 255), outline=(190, 192, 200, 255), width=3)
    d.ellipse([px - rx * 0.7, py - ry * 0.65, px + rx * 0.7, py + ry * 0.65], fill=(222, 222, 228, 255))
    if plate > 0:
        rnd = random.Random(5)
        for k in range(int(26 * plate)):
            fx = px + rnd.uniform(-0.55, 0.55) * rx
            fy = py + rnd.uniform(-0.45, 0.3) * ry
            col = rnd.choice([(232, 186, 90), (210, 120, 60), (110, 170, 80), (240, 220, 160)])
            r = cam.s(rnd.uniform(10, 22))
            d.ellipse([fx - r, fy - r * 0.7, fx + r, fy + r * 0.7], fill=col + (255,))
    # glass of water
    gx, gy = cam.p(330, top_y + 30)
    d.polygon([(gx - cam.s(40), gy - cam.s(150)), (gx + cam.s(40), gy - cam.s(150)), (gx + cam.s(32), gy + cam.s(10)),
               (gx - cam.s(32), gy + cam.s(10))], fill=(200, 230, 255, 70), outline=(220, 240, 255, 160))
    frame.add_glass(lay)
    if steam and plate > 0.3:
        for k in range(3):
            ph = (t * 0.6 + k * 0.33) % 1
            sx = px - cam.s(60) + k * cam.s(60) + math.sin(t * 2 + k) * cam.s(12)
            sy = py - cam.s(40) - ph * cam.s(220)
            glow_dot(frame, sx, sy, cam.s(14 + 10 * ph), (230, 230, 240), 0.12 * (1 - ph))


# ---------------------------------------------------------------- living room
@lru_cache(maxsize=2)
def _living_bg():
    img = Image.new("RGBA", (W + 300, H + 300), (0, 0, 0, 255))
    vgradient(img, (0, 0, W + 300, H + 300), [(0, (26, 28, 40)), (0.6, (34, 32, 44)), (1, (16, 14, 20))])
    d = ImageDraw.Draw(img)
    for k in range(9):   # curtain folds
        x = 80 + k * 46
        d.rectangle([x, 200, x + 30, 1300], fill=(60 + (k % 2) * 10, 30, 46, 255))
    d.rectangle([880, 520, 1180, 760], fill=(30, 60, 90, 255))       # TV glow
    return _blurred(img, 10)


def living(frame: Frame, t, dx=0.0, dy=0.0, zoom=1.0):
    paste_bg(frame, _living_bg(), dx, dy, zoom)
    soft_light(frame, 220 + dx * 0.4, 700 + dy * 0.4, 520, C["orange_l"], 0.2)      # floor lamp
    flick = 0.15 + 0.05 * math.sin(t * 9) * math.sin(t * 3.1)
    soft_light(frame, 1000 + dx * 0.4, 660 + dy * 0.4, 520, C["cyan"], flick)        # TV light


def sofa(frame: Frame, cam: Cam, front=False):
    """Leather sofa in world coords; front=True draws only the arm rests/seat edge over the body."""
    lay = frame.layer()
    d = ImageDraw.Draw(lay)
    col, dark = (96, 56, 40, 255), (64, 36, 26, 255)
    if not front:
        x0, y0 = cam.p(-420, -420)
        x1, y1 = cam.p(420, 40)
        d.rounded_rectangle([x0, y0, x1, y1], radius=int(cam.s(60)), fill=col)
        for k in (-1, 1):
            cx0, cy0 = cam.p(k * 200 - 170, -380)
            cx1, cy1 = cam.p(k * 200 + 170, -40)
            d.rounded_rectangle([min(cx0, cx1), cy0, max(cx0, cx1), cy1], radius=int(cam.s(40)), fill=(110, 66, 48, 255))
    else:
        x0, y0 = cam.p(-480, 20)
        x1, y1 = cam.p(480, 260)
        d.rounded_rectangle([x0, y0, x1, y1], radius=int(cam.s(40)), fill=dark)
        for k in (-1, 1):
            ax0, ay0 = cam.p(k * 430 - 70, -180)
            ax1, ay1 = cam.p(k * 430 + 70, 240)
            d.rounded_rectangle([min(ax0, ax1), ay0, max(ax0, ax1), ay1], radius=int(cam.s(50)), fill=col)
    frame.add_glass(lay)


# ---------------------------------------------------------------- park at dusk (frontal path)
@lru_cache(maxsize=2)
def _park_sky():
    img = Image.new("RGBA", (W + 400, H + 400), (0, 0, 0, 255))
    vgradient(img, (0, 0, W + 400, H + 400), [(0, (20, 24, 60)), (0.35, (70, 50, 110)), (0.52, (210, 110, 90)),
                                              (0.6, (40, 40, 60)), (1, (20, 22, 30))])
    d = ImageDraw.Draw(img)
    rnd = random.Random(8)
    for _ in range(40):   # city skyline far away
        x = rnd.randint(0, W + 400)
        hgt = rnd.randint(60, 260)
        d.rectangle([x, 1150 - hgt, x + rnd.randint(40, 110), 1160], fill=(36, 34, 56, 255))
    for _ in range(14):   # tree crowns
        x = rnd.randint(-50, W + 450)
        r = rnd.randint(120, 220)
        d.ellipse([x - r, 1050 - r, x + r, 1050 + r * 0.8], fill=(22, 36, 34, 255))
    return _blurred(img, 8)


def park(frame: Frame, t, travel=0.0, dx=0.0, dy=0.0, zoom=1.0, lamps=True):
    """Frontal view down a park path; `travel` (world units walked) moves lamp posts toward camera."""
    paste_bg(frame, _park_sky(), dx * 0.3, dy * 0.3, zoom)
    d = ImageDraw.Draw(frame.base)
    hz = 1100 + dy * 0.6
    vx = W / 2 + dx * 0.6
    # ground + path in perspective
    d.polygon([(0, hz), (W, hz), (W, H), (0, H)], fill=(26, 30, 30, 255))
    d.polygon([(vx - 30, hz), (vx + 30, hz), (vx + 620, H), (vx - 620, H)], fill=(58, 56, 60, 255))
    for k in range(10):   # paving lines moving toward camera
        z = ((k / 10) + travel / 900) % 1
        y = hz + (H - hz) * z ** 2
        w2 = 30 + 590 * z ** 2
        d.line([vx - w2, y, vx + w2, y], fill=(70, 68, 72, 255), width=max(1, int(1 + 4 * z)))
    if lamps:
        for k in range(6):
            z = ((k / 6) + travel / 1400) % 1
            sc = 0.15 + 1.6 * z ** 2
            for sg in (-1, 1):
                x = vx + sg * (60 + 760 * z ** 2)
                yb = hz + (H - hz) * z ** 2
                top = yb - 520 * sc
                d.line([x, yb, x, top], fill=(30, 30, 36, 255), width=max(2, int(9 * sc)))
                glow_dot(frame, x, top, 26 * sc, C["orange_l"], 0.9)
                soft_light(frame, x, top, 160 * sc, C["orange_l"], 0.12) if z > 0.4 else None
    # drifting leaves
    rnd = random.Random(11)
    for i in range(10):
        ph = (t * 0.12 + i * 0.1) % 1
        x = (rnd.random() * W + math.sin(t + i) * 80) % W
        y = ph * H
        d.ellipse([x - 7, y - 4, x + 7, y + 4], fill=(170, 110, 60, 200))


# ---------------------------------------------------------------- interior worlds
def _organic_bg(frame, t, base, glow_col, seed=1):
    vgradient(frame.base, (0, 0, W, H), [(0, lerpc(base, (0, 0, 0), 0.5)), (0.5, base), (1, lerpc(base, (0, 0, 0), 0.6))])
    lay = frame.layer()
    d = ImageDraw.Draw(lay)
    rnd = random.Random(seed)
    for i in range(18):
        x = rnd.random() * W
        y = (rnd.random() * H + t * 30 * (1 + i % 3)) % (H + 200) - 100
        r = rnd.randint(60, 200)
        d.ellipse([x - r, y - r, x + r, y + r], fill=rgba(glow_col, 0.06))
    frame.add_base(lay.filter(ImageFilter.GaussianBlur(20)))


def gut_world(frame: Frame, t, k_absorb=0.0):
    """Digestive tract cross-section: food chunks travel, break into glucose, cross into a capillary."""
    _organic_bg(frame, t, (60, 26, 30), C["orange"], 2)
    d = ImageDraw.Draw(frame.base)
    # intestine tube (curved band)
    tube = [(-100 + i * 60, 760 + 160 * math.sin(i * 0.45 + t * 0.3)) for i in range(23)]
    d.line(tube, fill=(150, 70, 60, 255), width=300, joint="curve")
    d.line(tube, fill=(190, 96, 80, 255), width=250, joint="curve")
    for x, y in tube[::2]:   # villi
        for v in range(-3, 4):
            d.line([x + v * 14, y + 120, x + v * 14 + 4, y + 90], fill=(220, 120, 100, 255), width=8)
    # capillary below
    cap = [(-100 + i * 60, 1220 + 60 * math.sin(i * 0.5 - t * 0.4)) for i in range(23)]
    d.line(cap, fill=(110, 20, 30, 255), width=110, joint="curve")
    d.line(cap, fill=(170, 34, 46, 255), width=80, joint="curve")
    for i in range(14):   # red cells drifting
        k = (t * 0.18 + i / 14) % 1
        j = int(k * 22)
        x, y = cap[j]
        d.ellipse([x - 22, y - 12, x + 22, y + 12], fill=(220, 60, 70, 255))
    # food chunks -> glucose
    rnd = random.Random(4)
    for i in range(9):
        k = (t * 0.12 + i / 9) % 1
        j = int(k * 21)
        x, y = tube[j]
        y += rnd.uniform(-60, 60)
        size = 34 * (1 - 0.7 * k)
        if k < 0.55:
            d.rounded_rectangle([x - size, y - size * 0.7, x + size, y + size * 0.7], radius=10, fill=(232, 186, 90, 255))
        else:
            for m in range(3):   # broken down into glucose that drops through the wall
                drop = clamp((k - 0.55) / 0.45) * k_absorb
                gx, gy = x + (m - 1) * 26, y + drop * (cap[j][1] - y)
                _glucose(frame, gx, gy, 13)


def _glucose(frame, x, y, r, a=1.0):
    pts = [(x + math.cos(math.radians(60 * k + 30)) * r, y + math.sin(math.radians(60 * k + 30)) * r) for k in range(6)]
    ImageDraw.Draw(frame.glass).polygon(pts, fill=rgba(C["orange_l"], a))
    glow_line(frame, pts + [pts[0]], C["gold"], 0.9 * a, 3)
    glow_dot(frame, x, y, r * 0.9, C["orange"], 0.35 * a)


def blood_world(frame: Frame, t, level=0.5, speed=1.0):
    """First-person ride down a blood vessel: rings rush toward camera, glucose density = `level`."""
    vgradient(frame.base, (0, 0, W, H), [(0, (40, 4, 12)), (0.5, (90, 10, 24)), (1, (30, 2, 8))])
    d = ImageDraw.Draw(frame.base)
    cx, cy = W / 2, H / 2 - 80
    for k in range(14):
        z = ((k / 14) + t * 0.35 * speed) % 1
        r = 40 + 900 * z ** 2
        a = int(120 * (1 - z) + 40)
        d.ellipse([cx - r * 0.75, cy - r, cx + r * 0.75, cy + r], outline=(200, 60, 70, a), width=max(2, int(2 + 14 * z)))
    rnd = random.Random(7)
    n_rbc, n_glu = 26, int(6 + 30 * level)
    for i in range(n_rbc + n_glu):
        ang = rnd.random() * math.tau
        rad = 0.15 + rnd.random() * 0.7
        z = ((rnd.random()) + t * (0.25 + 0.2 * rnd.random()) * speed) % 1
        dist = (40 + 820 * z ** 2) * rad
        x = cx + math.cos(ang) * dist * 0.75
        y = cy + math.sin(ang) * dist
        sz = 6 + 70 * z ** 2
        if i < n_rbc:
            d.ellipse([x - sz, y - sz * 0.55, x + sz, y + sz * 0.55], fill=(210, 50, 62, 255))
            d.ellipse([x - sz * 0.45, y - sz * 0.2, x + sz * 0.45, y + sz * 0.2], fill=(160, 30, 44, 255))
        else:
            _glucose(frame, x, y, sz * 0.45, a=0.95)


def muscle_world(frame: Frame, t, active=0.0, flex=0.0, gates=0.0, uptake=0.0):
    """Macro view: muscle fibres (striated bundle) beside a capillary carrying glucose.
    active: 0 rest (cool colours) .. 1 working (warm); flex: contraction; gates: violet GLUT4 gates opening;
    uptake: fraction of passing glucose that turns into the fibre (most keep flowing)."""
    _organic_bg(frame, t, lerpc((22, 30, 60), (60, 24, 30), active), lerpc(C["cyan"], C["orange"], active), 5)
    d = ImageDraw.Draw(frame.base)
    # capillary across the top
    cy = 520
    d.rectangle([0, cy - 70, W, cy + 70], fill=(110, 20, 30, 255))
    d.rectangle([0, cy - 52, W, cy + 52], fill=(160, 32, 44, 255))
    # fibres (3 bundles) below
    squeeze = 1 - 0.12 * flex
    fcol = lerpc((90, 110, 160), (210, 80, 70), active)
    fcol_d = lerpc((60, 70, 110), (150, 50, 50), active)
    for b in range(3):
        y0 = 760 + b * 270
        hh = 110 * (1 + 0.14 * flex)
        x0, x1 = 60 + 30 * flex, W - 60 - 30 * flex
        d.rounded_rectangle([x0, y0 - hh, x1, y0 + hh], radius=int(hh), fill=fcol_d + (255,))
        d.rounded_rectangle([x0 + 8, y0 - hh + 8, x1 - 8, y0 + hh - 8], radius=int(hh - 8), fill=fcol + (255,))
        step = 26 * squeeze
        xs = x0 + 40
        while xs < x1 - 40:   # striations bunch together on contraction
            d.line([xs, y0 - hh + 18, xs, y0 + hh - 18], fill=fcol_d + (255,), width=5)
            xs += step
        if active > 0.3:
            glow_dot(frame, (x0 + x1) / 2, y0, hh * 0.9, C["orange"], 0.12 * active * (0.6 + flex))
    # GLUT4 gates on the top fibre membrane, facing the capillary
    gy = 760 - 110 * (1 + 0.14 * flex)
    for i, gx in enumerate(range(170, W - 100, 190)):
        op = gates * (0.5 + 0.5 * flex)
        gap = 8 + 26 * op
        col = lerpc((90, 80, 140), C["violet"], gates)
        d.rectangle([gx - 40, gy - 10, gx - gap, gy + 10], fill=col + (255,))
        d.rectangle([gx + gap, gy - 10, gx + 40, gy + 10], fill=col + (255,))
        if gates > 0.2:
            glow_line(frame, [(gx - 40, gy), (gx - gap, gy)], C["violet_l"], 0.6 * gates, 4)
            glow_line(frame, [(gx + gap, gy), (gx + 40, gy)], C["violet_l"], 0.6 * gates, 4)
    # glucose: flows along the capillary; a fraction dips through open gates into the fibre
    rnd = random.Random(9)
    for i in range(18):
        k = (t * 0.16 + i / 18) % 1
        x = -60 + k * (W + 120)
        y = cy + rnd.uniform(-30, 30)
        enters = uptake > 0 and (i % 3 == 0) and rnd.random() < uptake + 0.4
        if enters:
            nearest = min(range(170, W - 100, 190), key=lambda g: abs(g - x))
            dive = clamp(1 - abs(nearest - x) / 160) * gates
            y = lerp(y, gy + 60, dive)
            if dive > 0.9:
                glow_dot(frame, x, gy + 80, 30, C["orange_l"], 0.5)     # used as energy: small flash
        _glucose(frame, x, y, 16)


def viz_world(frame: Frame, t, p_sit=0.0, p_walk=0.0, cam_shift=0.0):
    """Clean scientific visualisation: two ILLUSTRATIVE post-meal glucose curves."""
    vgradient(frame.base, (0, 0, W, H), [(0, (8, 14, 32)), (1, (16, 26, 56))])
    d = ImageDraw.Draw(frame.base)
    for gx in range(80, W, 80):
        d.line([gx + cam_shift % 80, 0, gx + cam_shift % 80, H], fill=(20, 32, 64, 255), width=1)
    for gy in range(80, H, 80):
        d.line([0, gy, W, gy], fill=(20, 32, 64, 255), width=1)
    x0, x1, yb, yt = 140, 960, 1060, 500
    d.line([x0, yt - 40, x0, yb, x1 + 20, yb], fill=(170, 190, 220, 255), width=4)
    text(frame.top, "Glucosa en sangre", x0 - 10, yt - 80, size=40, color=C["cyan_l"], anchor="lm", stroke=3)
    text(frame.top, "Tiempo después de comer", (x0 + x1) / 2, yb + 54, size=40, color=C["cyan_l"], stroke=3)

    def curve(peak, p, col):
        pts = []
        n = 60
        for i in range(int(n * p) + 1):
            u = i / n
            v = 0.12 + peak * math.exp(-((u - 0.32) ** 2) / 0.035)
            pts.append((lerp(x0, x1, u), lerp(yb, yt, v)))
        if len(pts) > 1:
            glow_line(frame, pts, col, 0.95, 9)
            glow_dot(frame, pts[-1][0], pts[-1][1], 12, col, 1.0)
        return pts

    curve(0.82, p_sit, C["orange"])
    curve(0.55, p_walk, C["cyan"])
    if p_sit > 0.2:
        text(frame.top, "Sentado", 820, 580, size=46, color=C["orange_l"], stroke=4)
    if p_walk > 0.2:
        text(frame.top, "Caminando", 820, 820, size=46, color=C["cyan_l"], stroke=4)
    # honest labelling
    d.rounded_rectangle([W / 2 - 170, 250, W / 2 + 170, 310], radius=18, fill=(40, 50, 90, 255))
    text(frame.top, "ILUSTRATIVO", W / 2, 280, size=36, color=C["white"], stroke=0)
