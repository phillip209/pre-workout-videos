"""Personified inner world for Paco's comedy (visual METAPHORS, labelled as illustration on screen).

- glucose_char: a golden hexagon with a face (the glucose 'guests')
- cell_char: a muscle cell with a face, arms and states: sleep / startled / work
- slide_world: glucose characters ride a water slide from the gut into the bloodstream
- cells_world: the leg muscle as a workplace: cells asleep (NO MOLESTAR) → alarm → open the GLUT4
  doors and pull glucose in; most glucose keeps flowing along the capillary (not all is taken up).
"""
from __future__ import annotations

import math
import random

from PIL import ImageDraw, ImageFilter

from .core import W, H, C, Frame, rgba, lerp, lerpc, clamp, ease_out, ease_io, vgradient, glow_dot, glow_line, text, font


def glucose_char(frame: Frame, x, y, r, mood="happy", t=0.0, arms_up=False, a=1.0):
    d = ImageDraw.Draw(frame.glass)
    pts = [(x + math.cos(math.radians(60 * k + 30)) * r, y + math.sin(math.radians(60 * k + 30)) * r) for k in range(6)]
    d.polygon(pts, fill=rgba(C["orange_l"], a))
    glow_line(frame, pts + [pts[0]], C["gold"], 0.9 * a, max(2, int(r * 0.12)))
    e = r * 0.28
    for sg in (-1, 1):
        d.ellipse([x + sg * e - r * 0.1, y - r * 0.25, x + sg * e + r * 0.1, y - r * 0.02], fill=rgba(C["ink"], a))
    if mood == "happy":
        d.arc([x - r * 0.3, y - r * 0.1, x + r * 0.3, y + r * 0.35], 20, 160, fill=rgba(C["ink"], a), width=max(2, int(r * 0.09)))
    elif mood == "wow":
        d.ellipse([x - r * 0.14, y + r * 0.05, x + r * 0.14, y + r * 0.35], fill=rgba(C["ink"], a))
    else:
        d.line([x - r * 0.2, y + r * 0.2, x + r * 0.2, y + r * 0.2], fill=rgba(C["ink"], a), width=max(2, int(r * 0.08)))
    if arms_up:
        for sg in (-1, 1):
            d.line([x + sg * r * 0.8, y, x + sg * r * 1.25, y - r * 0.7 - math.sin(t * 12) * r * 0.1],
                   fill=rgba(C["orange_l"], a), width=max(2, int(r * 0.14)))


def cell_char(frame: Frame, x, y, r, state="sleep", t=0.0, i=0, energy=0.0, reach=0.0):
    """state: sleep | startled | work. reach 0..1 raises the arms (pulling glucose in)."""
    d = ImageDraw.Draw(frame.glass)
    jump = 0.0
    if state == "startled":
        jump = abs(math.sin(t * 14 + i)) * r * 0.35
    y = y - jump
    body = lerpc((200, 90, 100), (240, 110, 70), energy)
    d.ellipse([x - r, y - r * 0.9, x + r, y + r], fill=rgba(body, 1.0), outline=rgba((120, 40, 50), 1.0), width=4)
    d.ellipse([x - r * 0.55, y - r * 0.75, x - r * 0.1, y - r * 0.4], fill=rgba((255, 190, 190), 0.8))
    if energy > 0.05:
        glow_dot(frame, x, y, r * 1.1, C["orange"], 0.25 * energy)
    # arms
    ay = y + r * 0.1
    for sg in (-1, 1):
        if state == "work":
            tip = (x + sg * r * 0.9, ay - r * (0.4 + 1.1 * reach))
        elif state == "startled":
            tip = (x + sg * r * 1.5, ay - r * 0.9)
        else:
            tip = (x + sg * r * 1.3, ay + r * 0.4)
        d.line([(x + sg * r * 0.8, ay), tip], fill=rgba((150, 60, 70), 1.0), width=max(3, int(r * 0.16)))
    # face
    ex = r * 0.34
    for sg in (-1, 1):
        cx, cy = x + sg * ex, y - r * 0.1
        if state == "sleep":
            d.arc([cx - r * 0.18, cy - r * 0.12, cx + r * 0.18, cy + r * 0.12], 20, 160, fill=rgba(C["ink"], 1), width=4)
        else:
            rr = r * (0.2 if state == "startled" else 0.15)
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=rgba(C["white"], 1))
            d.ellipse([cx - rr * 0.45, cy - rr * 0.45, cx + rr * 0.45, cy + rr * 0.45], fill=rgba(C["ink"], 1))
    my = y + r * 0.35
    if state == "sleep":
        d.ellipse([x - r * 0.08, my - r * 0.05, x + r * 0.08, my + r * 0.1], fill=rgba(C["ink"], 1))
    elif state == "startled":
        d.ellipse([x - r * 0.16, my - r * 0.12, x + r * 0.16, my + r * 0.22], fill=rgba(C["ink"], 1))
    else:
        d.arc([x - r * 0.3, my - r * 0.25, x + r * 0.3, my + r * 0.12], 20, 160, fill=rgba(C["ink"], 1), width=5)
    if state == "sleep":
        for k in range(2):
            ph = (t * 0.6 + k * 0.5 + i * 0.3) % 1
            text(frame.top, "z", x + r * 0.8 + ph * 40, y - r - ph * 70, size=int(34 + 20 * ph), color=C["cyan_l"],
                 stroke=3, alpha=1 - ph)
    if state == "startled":
        text(frame.top, "!", x, y - r * 1.5, size=int(r * 0.9), color=C["gold"], stroke=6)


def _illustration_tag(frame):
    text(frame.top, "Ilustración", W - 40, 190, size=30, color=(180, 190, 220), anchor="rm", stroke=3)


# ---------------------------------------------------------------- the glucose water slide
def slide_world(frame: Frame, t, level=0.0):
    vgradient(frame.base, (0, 0, W, H), [(0, (60, 26, 30)), (0.5, (80, 34, 38)), (1, (40, 10, 18))])
    d = ImageDraw.Draw(frame.base)
    # gut (top) and blood vessel (bottom)
    d.rounded_rectangle([-60, 280, W + 60, 560], radius=120, fill=(170, 84, 72, 255))
    d.rounded_rectangle([-60, 300, W + 60, 540], radius=110, fill=(205, 110, 92, 255))
    for x in range(20, W, 46):
        d.line([x, 540, x + 6, 500], fill=(230, 140, 120, 255), width=10)
    text(frame.top, "Intestino", 80, 260, size=40, color=C["orange_l"], anchor="lm", stroke=4)
    vy = 1500
    d.rounded_rectangle([-60, vy - 140, W + 60, vy + 140], radius=130, fill=(110, 18, 30, 255))
    d.rounded_rectangle([-60, vy - 110, W + 60, vy + 110], radius=110, fill=(170, 30, 44, 255))
    text(frame.top, "Sangre", 80, vy - 175, size=40, color=C["red_l"], anchor="lm", stroke=4)
    for i in range(10):   # red cells flowing
        k = (t * 0.22 + i / 10) % 1
        x = -60 + k * (W + 120)
        d.ellipse([x - 34, vy - 18 + (i % 3) * 30 - 30, x + 34, vy + 18 + (i % 3) * 30 - 30], fill=(225, 64, 76, 255))
    # the slide: an S-curve tube from the gut wall to the vessel
    path = [(lerp(260, 780, u) + 240 * math.sin(u * math.pi * 2.0), lerp(560, vy - 110, u)) for u in [k / 40 for k in range(41)]]
    d.line(path, fill=(120, 190, 230, 255), width=96, joint="curve")
    d.line(path, fill=(170, 225, 250, 255), width=70, joint="curve")
    d.line([(x - 18, y) for x, y in path], fill=(230, 250, 255, 255), width=8, joint="curve")
    # glucose riders
    n = 6
    for i in range(n):
        k = (t * 0.33 + i / n) % 1
        j = min(int(k * 40), 39)
        fr = k * 40 - j
        x = lerp(path[j][0], path[j + 1][0], fr)
        y = lerp(path[j][1], path[j + 1][1], fr)
        glucose_char(frame, x, y - 30, 34, mood="wow" if k < 0.8 else "happy", t=t, arms_up=True)
        if 0.3 < k < 0.45 and i % 2 == 0:
            text(frame.top, "¡WIII!", x + 80, y - 70, size=46, color=C["white"], stroke=5)
    # glucose already in the blood, more over time
    rnd = random.Random(2)
    for i in range(int(3 + 9 * level)):
        k = (t * 0.2 + rnd.random()) % 1
        glucose_char(frame, -40 + k * (W + 80), vy + rnd.uniform(-60, 60), 26, mood="happy", t=t)
    _illustration_tag(frame)


# ---------------------------------------------------------------- the muscle workplace
def cells_world(frame: Frame, t, wake=0.0, gates=0.0, uptake=0.0, alarm=0.0, sleepy_until=None, bonk_t=None):
    """wake 0 = all asleep, 1 = all awake/working. alarm 0..1 = siren flashing.
    sleepy_until: cell #2 keeps sleeping until this time (gag) — bonk_t: glucose hits it awake."""
    warm = wake
    vgradient(frame.base, (0, 0, W, H), [(0, lerpc((22, 30, 60), (60, 24, 30), warm)),
                                         (1, lerpc((10, 14, 30), (30, 10, 14), warm))])
    d = ImageDraw.Draw(frame.base)
    # capillary (top band)
    cy = 470
    d.rectangle([0, cy - 90, W, cy + 90], fill=(110, 20, 30, 255))
    d.rectangle([0, cy - 66, W, cy + 66], fill=(160, 32, 44, 255))
    text(frame.top, "Capilar", 40, cy - 115, size=38, color=C["red_l"], anchor="lm", stroke=4)
    # membrane with GLUT4 doors
    my = 640
    d.rectangle([0, my - 14, W, my + 14], fill=lerpc((90, 110, 160), (200, 90, 80), warm) + (255,))
    doors = [180, 450, 720, 990]
    for gx in doors:
        gap = 6 + 40 * gates
        col = lerpc((90, 80, 140), C["violet"], max(gates, 0.3))
        d.rectangle([gx - 70, my - 22, gx - gap, my + 22], fill=col + (255,))
        d.rectangle([gx + gap, my - 22, gx + 70, my + 22], fill=col + (255,))
        if gates > 0.2:
            glow_line(frame, [(gx - 70, my), (gx - gap, my)], C["violet_l"], 0.6 * gates, 5)
            glow_line(frame, [(gx + gap, my), (gx + 70, my)], C["violet_l"], 0.6 * gates, 5)
    # the NO MOLESTAR sign (running gag) hangs on the second door while asleep
    if wake < 0.5:
        sx, sy = doors[1], my + 70
        d.line([sx - 40, my + 14, sx, sy - 20], fill=(200, 200, 200, 255), width=3)
        d.line([sx + 40, my + 14, sx, sy - 20], fill=(200, 200, 200, 255), width=3)
        d.rounded_rectangle([sx - 120, sy - 20, sx + 120, sy + 46], radius=10, fill=(245, 240, 225, 255),
                            outline=(120, 90, 70, 255), width=4)
        text(frame.base, "NO MOLESTAR", sx, sy + 13, size=34, color=(160, 40, 40), stroke=0)
    # fibre floor
    d.rounded_rectangle([-40, 1260, W + 40, 1500], radius=110, fill=lerpc((70, 80, 120), (170, 60, 60), warm) + (255,))
    for x in range(30, W, 34):
        d.line([x, 1280, x, 1480], fill=lerpc((50, 60, 100), (130, 40, 44), warm) + (255,), width=6)
    # alarm light
    if alarm > 0:
        on = (t * 6) % 1 < 0.5
        glow_dot(frame, W / 2, 700 if False else 760, 0, C["red"], 0)
        lay = frame.layer()
        ImageDraw.Draw(lay).rectangle([0, 0, W, H], fill=rgba(C["red"], 0.18 * alarm if on else 0.04 * alarm))
        frame.add_glass(lay)
        glow_dot(frame, W - 120, 260, 60, C["red_l"], (0.9 if on else 0.3) * alarm)
    # cells
    rnd = random.Random(3)
    for i, gx in enumerate(doors):
        x, y = gx, 1080
        state = "sleep"
        if wake > 0.05:
            state = "startled" if wake < 0.6 else "work"
        if i == 2 and sleepy_until is not None and t < sleepy_until:
            state = "sleep"
        reach = clamp(gates) * (0.5 + 0.5 * math.sin(t * 6 + i))
        cell_char(frame, x, y, 110, state=state, t=t, i=i, energy=uptake if state == "work" else 0.0, reach=reach)
    # glucose characters along the capillary; some go through open doors (most keep flowing)
    for i in range(10):
        k = (t * 0.15 + i / 10) % 1
        x = -60 + k * (W + 120)
        y = cy + (i % 3 - 1) * 30
        mood = "flat"
        if wake < 0.05:
            near = min(doors, key=lambda g: abs(g - x))
            if abs(near - x) < 40 and i % 2 == 0:
                mood = "wow"       # knocking at a closed door
        elif gates > 0.3 and i % 3 == 0:
            near = min(doors, key=lambda g: abs(g - x))
            dive = clamp(1 - abs(near - x) / 150) * uptake
            y = lerp(y, 960, dive)
            mood = "happy"
        glucose_char(frame, x, y, 30, mood=mood, t=t)
    if bonk_t is not None and 0 <= t - bonk_t < 0.6:
        k = (t - bonk_t) / 0.6
        glucose_char(frame, doors[2] + 20, lerp(700, 960, min(1, k * 2)), 30, mood="wow", t=t)
        if k > 0.5:
            text(frame.top, "¡TOC!", doors[2] + 120, 900, size=54, color=C["gold"], stroke=6)
    _illustration_tag(frame)
