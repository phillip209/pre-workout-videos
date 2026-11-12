"""Episode 15 (pilot, pixel-art style): "¿Si dejas el gym, el músculo se convierte en grasa?"

Verdict: MITO.
Sources (checked 2026-11-12):
  - Muscle fibers and adipocytes are different cell types; one cannot turn into the other
    (basic histology/physiology).
  - Bruusgaard JC et al. 2010, PNAS 107(34):15111-6 - mice: myonuclei gained with overload were
    retained during later atrophy (denervation). Contested by later rodent work.
  - Seaborne RA et al. 2018, Sci Rep 8:1898 - humans (small sample): DNA-methylation marks from
    training persisted through detraining and were associated with greater regrowth on retraining.
"""
from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw

from engine import W, H
from engine import gfx, fx
from engine import cast
from engine.gfx import P, prog, ease_out, ease_back, ease_io, ease_in, clamp, lerp, paste
from engine.font import draw_text, text_width
from engine.director import Director, Scene, SubStyle
from engine.timeline import norm

SLUG = "e15_musculo_grasa"
BPM = 96
LEAD_IN = 0.15
NARRATION_FILE = "episodes/e15_musculo_grasa/narration.mp3"   # ElevenLabs, voz "David C - Viral Storytelling", eleven_multilingual_v2
TAIL = 2.2

# ------------------------------------------------------------------ SCRIPT
# Spanish (LatAm) narration. Per-line voice overrides tune the performance.
LINES = [
    {"id": "hook", "text": "Si dejas el gimnasio, tu músculo se convierte en grasa.", "pause": 0.55, "hold": 0.35,
     "voice": {"style": 0.55, "stability": 0.35}},
    {"id": "doubt", "text": "Eso dicen... y parece verdad.", "pause": 0.45},
    {"id": "cells", "text": "Pero hay un problema: el músculo y la grasa ni siquiera son el mismo tipo de célula.",
     "pause": 0.35},
    {"id": "brick", "text": "Una no puede convertirse en la otra. Es como querer convertir un ladrillo en una almohada.",
     "pause": 0.75, "hold": 0.8, "voice": {"style": 0.45}},
    {"id": "what", "text": "Entonces, ¿qué pasa de verdad? Dos cosas, al mismo tiempo.", "pause": 0.3},
    {"id": "shrink", "text": "Sin entrenamiento, el músculo se encoge.", "pause": 0.3},
    {"id": "grow", "text": "Y si sigues comiendo igual, pero te mueves menos, la grasa crece.", "pause": 0.35, "hold": 0.5},
    {"id": "seesaw", "text": "Uno baja, el otro sube... y desde afuera parece una transformación.", "pause": 0.6, "hold": 0.2},
    {"id": "twist", "text": "Pero aquí viene lo bueno.", "pause": 0.55,
     "voice": {"stability": 0.3, "style": 0.65, "speed": 0.92}},
    {"id": "mice", "text": "En ratones, los núcleos que el músculo ganó entrenando se quedaron, aunque el músculo se encogiera.",
     "pause": 0.35, "hold": 0.6},
    {"id": "dna", "text": "Y en un estudio con personas, el músculo guardó marcas en su ADN que lo ayudaron a volver a crecer.",
     "pause": 0.55, "hold": 0.5},
    {"id": "resolve", "text": "Tu músculo no se convierte en grasa. Te está esperando.", "pause": 0.7, "hold": 0.6,
     "voice": {"style": 0.5, "stability": 0.4}},
    {"id": "cta", "text": "¿A quién le mandarías esto?", "pause": 0.2, "voice": {"style": 0.4}},
]

VOICE = {
    # Chosen from the ElevenLabs account (see README "Voz"). Override with PW_VOICE_ID.
    "voice_id": os.environ.get("PW_VOICE_ID", "REPLACE_WITH_VOICE_ID"),
    "model": os.environ.get("PW_TTS_MODEL", "eleven_multilingual_v2"),
    "settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True,
                 "speed": 1.02},
}

TITLE = "¿Si dejas el gym, tu músculo se convierte en grasa? MITO #Shorts"
DESCRIPTION = (
    "¿Si dejas el gimnasio, el músculo se convierte en grasa? MITO. Son células distintas: al dejar de "
    "entrenar el músculo se encoge y, si comes igual y te mueves menos, la grasa puede aumentar. Y hay "
    "una buena noticia: el músculo parece \"recordar\" el entrenamiento.\n\n"
    "Fuentes: Bruusgaard et al., PNAS, 2010 (ratones) · Seaborne et al., Sci Rep, 2018 (personas, "
    "estudio pequeño).\n\n#fitness #musculo #memoriamuscular #mitosfitness #fitnesssinhumo #Shorts"
)
TAGS = ["memoria muscular", "músculo y grasa", "dejar el gimnasio", "mitos fitness", "fitness sin humo"]


# ------------------------------------------------------------------ SOUND
def sound_cues(tl):
    c = tl.cue
    out = [
        (0.0, "impact", 0.8), (0.02, "whoosh", 0.6),
        (c("hook", "convierte"), "heartbeat", 0.9),
        (c("hook", "grasa"), "melt", 1.0), (c("hook", "grasa"), "glitch", 0.7),
        (c("hook", "grasa") + 0.05, "impact", 0.7),
        (c("doubt") - 0.25, "whoosh", 0.4),
        (c("doubt", "parece"), "deflate", 0.4),
        (c("cells") - 0.3, "rise", 0.5),
        (c("cells", "músculo"), "whoosh", 0.6),
        (c("cells", "grasa"), "boing", 0.8),
        (c("cells", "célula"), "impact", 0.8),
        (c("brick") - 0.1, "thud", 0.7),
        (c("brick"), "machine", 0.5),
        (c("brick", "puede"), "glitch", 0.5),
        (c("brick", "ladrillo") - 0.2, "whoosh", 0.4),
        (c("brick", "ladrillo") + 0.35, "clank", 0.8),
        (c("brick", "ladrillo") + 0.4, "alarm", 0.5),
        (c("brick", "almohada"), "explode", 1.0),
        (c("brick", "almohada") + 0.55, "boing", 0.7),
        (c("what") - 0.2, "whoosh", 0.6),
        (c("what", "dos"), "pop", 0.8), (c("what", "cosas") + 0.15, "pop", 0.8),
        (c("shrink", "encoge"), "deflate", 0.8),
        (c("grow", "comiendo"), "chomp", 0.8), (c("grow", "comiendo") + 0.25, "chomp", 0.8),
        (c("grow", "igual"), "chomp", 0.8), (c("grow", "mueves"), "blip", 0.8),
        (c("grow", "crece"), "inflate", 0.9),
        (c("seesaw", "baja"), "deflate", 0.5), (c("seesaw", "sube"), "rise", 0.5),
        (c("seesaw", "afuera") - 0.15, "whoosh", 0.5),
        (c("seesaw", "transformación"), "glitch", 0.6),
        (c("twist", "aquí"), "heartbeat", 1.0),
        (c("twist", "bueno"), "sparkle", 0.9),
        (c("mice") - 0.15, "whoosh", 0.5),
        (c("mice", "núcleos"), "sparkle", 0.6),
        (c("mice", "encogiera"), "deflate", 0.5),
        (c("mice", "encogiera") + 0.6, "ding", 0.7),
        (c("dna") - 0.25, "whoosh", 0.5),
        (c("dna", "marcas"), "blip", 0.8), (c("dna", "marcas") + 0.18, "blip", 0.8),
        (c("dna", "marcas") + 0.36, "blip", 0.8),
        (c("dna", "crecer"), "rise", 0.6),
        (c("resolve") - 0.2, "whoosh", 0.4),
        (c("resolve", "esperando"), "stamp", 1.0),
        (c("resolve", "esperando") + 0.05, "sparkle", 0.7),
        (c("cta") - 0.15, "pop", 0.6),
        (c("cta", "mandarías"), "ding", 0.6),
    ]
    # footsteps in the resolve scene
    st = c("resolve")
    for i in range(6):
        out.append((st + 0.1 + i * 0.28, "step", 0.6))
    out.append((c("resolve", "grasa") + 0.1, "clank", 0.5))
    return out


def music_sections(tl):
    c = tl.cue
    return [
        (0.0, c("cells") - 0.2, "tense"),
        (c("cells") - 0.2, c("what") - 0.1, "mystery"),
        (c("what") - 0.1, c("twist") - 0.05, "groove"),
        (c("twist") - 0.05, c("twist", "bueno"), "silence"),
        (c("twist", "bueno"), c("cta") - 0.1, "hope"),
        (c("cta") - 0.1, tl.total, "outro"),
    ]


# ------------------------------------------------------------------ HELPERS
def blinking(t, period=3.1, off=0.0):
    return ((t + off) % period) < 0.12


def label(img, text, x, y, color=P["white"], scale=1, center=True, outline=P["ink"]):
    draw_text(img, text, x, y, color=color, scale=scale, outline=outline, align="center" if center else "left")


def pop_scale(t, start, dur=0.25):
    p = prog(t, start, dur)
    return ease_back(p) if p > 0 else 0.0


def paste_scaled(img, spr, x, y, s, anchor="center"):
    """Paste with a non-integer 'pop' scale (nearest neighbour keeps pixels crisp)."""
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
    for sx in range(x + 8, x + w, 8):  # segment ticks (RPG style)
        d.line([sx, y, sx, y + h], fill=back)
    if label_txt:
        draw_text(img, label_txt, x, y - 12, color=P["white"], outline=P["ink"])


def text_sprite(text, color, scale=2, outline=P["ink"]):
    spr = gfx.new(text_width(text, scale) + 6, 9 * scale + 6)
    draw_text(spr, text, 3, 2, color=color, scale=scale, outline=outline)
    return spr


# ------------------------------------------------------------------ SCENES
def make_director(tl):
    c = tl.cue
    L = tl.line

    # ---------------------------------------------------------- 1. HOOK
    def s_hook(tl_, t):
        img = cast.gym_bg("night").copy()
        tg = c("hook", "grasa")
        tm = t - tg  # time since "grasa"
        melt = ease_io(prog(t, tg, 0.7))
        flex = 0.85 + 0.15 * math.sin(t * 9) if tm < 0 else 1.0 - melt * 0.75
        pose = {
            "arm_l": (95, 85 + 6 * math.sin(t * 9)),
            "arm_r": (95 - melt * 40, 85 + 6 * math.sin(t * 9) - melt * 70),
            "bicep": flex, "mouth": "grin" if tm < 0 else ("o" if tm < 1.0 else "sad"),
            "eyes": "happy" if tm < 0 else "wide", "tint_arm": melt, "bob": 1 if (t * 2.5) % 1 < 0.5 else 0,
        }
        if tm < 0 and blinking(t, 2.3):
            pose["eyes"] = "blink"
        spr = cast.hero(pose)
        paste(img, spr, 135, 342, scale=3)
        # bicep pulse rings before the reveal
        if tm < 0:
            d = ImageDraw.Draw(img)
            r = 8 + (t * 30) % 22
            d.ellipse([180 - r, 235 - r, 180 + r, 235 + r], outline=P["gold"])
            fx.sparkles(img, 180, 232, t, n=6, radius=24)
        else:
            fx.drips(img, 166, 196, 246, tm, n=9, seed=4)
        # camera: punch-in at start, then push to the arm on the reveal
        z0 = lerp(1.35, 1.0, ease_out(prog(t, 0, 0.45)))
        zr = lerp(1.0, 1.7, ease_out(prog(t, tg, 0.5)))
        z = z0 * zr
        cx = lerp(135, 182, ease_out(prog(t, tg, 0.5)))
        cy = lerp(250, 238, ease_out(prog(t, tg, 0.5)))
        shake = 4 * (1 - prog(t, tg, 0.6)) if tm >= 0 else 0
        out = gfx.camera(img, z, cx, cy, shake=shake, t=t)
        if t < 0.35:
            fx.speed_lines(out, 135, 240, t, n=30)
        if 0 <= tm < 0.25:
            out = gfx.chroma_glitch(out, 8, t)
            out = gfx.flash(out, 0.5 * (1 - tm / 0.25), P["fat_l"])
        if 0.15 < tm:
            sp = text_sprite("¿!", P["fat"], scale=3)
            paste_scaled(out, sp, 60, 120, pop_scale(t, tg + 0.15), anchor="center")
        return out

    # ---------------------------------------------------------- 2. DOUBT (weeks pass)
    def s_doubt(tl_, t):
        img = cast.gym_bg("gloomy").copy()
        ln = L("doubt")
        dur = (c("cells") - ln.start)
        k = ease_io(prog(t, 0.1, dur - 0.3))
        weeks = 1 + int(k * 11)
        # wall calendar with flipping pages
        d = ImageDraw.Draw(img)
        d.rectangle([20, 50, 92, 120], fill=P["white"])
        d.rectangle([20, 50, 92, 64], fill=P["red"])
        draw_text(img, "SEMANA", 56, 53, color=P["white"], align="center")
        draw_text(img, str(weeks), 56, 76, color=P["ink"], scale=3, align="center")
        flip = (k * 11) % 1
        if flip < 0.35 and k < 0.98:
            h = int(56 * (1 - flip / 0.35))
            d.polygon([(20, 64), (92, 64), (92 - 10, 64 + h), (24, 64 + h)], fill=P["cream"])
        pose = {"arm_l": (8, 6), "arm_r": (8, 6), "bicep": lerp(0.6, 0.15, k), "belly": lerp(0.0, 0.85, k),
                "mouth": "flat" if k < 0.5 else "sad", "eyes": "sad" if k > 0.4 else "open",
                "droop": k, "look": 1 if k > 0.6 else 0}
        if blinking(t, 2.7, 0.4):
            pose["eyes"] = "blink"
        paste(img, cast.hero(pose), 150, 342, scale=3)
        # floating "?" over head late in the line
        if k > 0.55:
            sp = text_sprite("?", P["fog"], scale=3)
            paste(img, sp, 205, 140 + math.sin(t * 4) * 3, anchor="center")
        z = lerp(1.0, 1.15, ease_io(prog(t, 0, dur)))
        return gfx.camera(img, z, 140, 250)

    # ---------------------------------------------------------- 3. CELLS
    def s_cells(tl_, t):
        img = cast.tissue_bg(t)
        T0 = L("cells").start
        tm, tg, tc = c("cells", "músculo") - T0, c("cells", "grasa") - T0, c("cells", "célula") - T0
        label(img, "ZOOM X1000", 135, 36, color=P["pink"])
        # muscle fiber slides in from the left
        p1 = ease_out(prog(t, tm - 0.15, 0.45))
        fxm = lerp(-120, 135, p1)
        shocked = t > tc
        fib = cast.muscle_fiber(70, 16, mood="shock" if shocked else "happy", nuclei=5, t=t,
                                blink=blinking(t, 2.5))
        paste(img, fib, fxm, 130, scale=2, anchor="center")
        if p1 > 0.9:
            label(img, "MÚSCULO", 135, 166, color=P["muscle_l"], scale=2)
            label(img, "(FIBRA MUSCULAR)", 135, 187, color=P["fog"])
        # fat cell bounces in from the right
        p2 = prog(t, tg - 0.1, 0.55)
        fxf = lerp(380, 135, ease_out(p2))
        hop = abs(math.sin(p2 * math.pi * 2)) * 30 * (1 - p2)
        fat = cast.fat_cell(17, mood="shock" if shocked else "happy", t=t, wobble=1 - p2,
                            blink=blinking(t, 2.9, 1))
        paste(img, fat, fxf, 250 - hop, scale=2, anchor="center")
        if p2 > 0.9:
            label(img, "GRASA", 135, 294, color=P["fat"], scale=2)
            label(img, "(ADIPOCITO)", 135, 315, color=P["fog"])
        # big ≠ between them on "célula"
        if t > tc:
            s = pop_scale(t, tc, 0.3) * 1.0
            neq = text_sprite("≠", P["white"], scale=4)
            paste_scaled(img, neq, 225, 200, s, anchor="center")
        shake = 3 * (1 - prog(t, tc, 0.35)) if t > tc else 0
        out = gfx.camera(img, 1.0, 135, 240, shake=shake, t=t)
        if t > tc and t - tc < 0.12:
            out = gfx.flash(out, 0.4)
        return out

    # ---------------------------------------------------------- 4. BRICK -> PILLOW machine
    def s_brick(tl_, t):
        img = cast.lab_bg(t)
        T0 = L("brick").start
        t_no = c("brick", "puede") - T0
        t_br = c("brick", "ladrillo") - T0
        t_al = c("brick", "almohada") - T0
        t_conv = c("brick", "convertir") - T0
        exploded = t > t_al
        # machine drops in
        drop = ease_back(prog(t, 0, 0.35))
        my = lerp(-60, 345, drop)
        shake_m = 0.0
        if t > t_br + 0.35:
            shake_m = min(3.0, (t - t_br - 0.35) * 5)
        light = "green"
        if t > t_br + 0.35:
            light = "red" if (t * 8) % 1 < 0.5 else "off"
        if exploded:
            light = "off"
        mach = cast.machine(t, shake=shake_m if not exploded else 0, light=light)
        if exploded:
            mach = gfx.darken(mach, 0.45)
        paste(img, mach, 135, my, scale=2)
        label(img, "TRANSMUTADOR", 135, 22, color=P["gold"], scale=2)
        # "MÚSCULO → GRASA" sign gets crossed on "puede"
        sign_y = 46
        label(img, "MÚSCULO → GRASA", 135, sign_y, color=P["white"], scale=2)
        if t > t_no:
            k = ease_out(prog(t, t_no, 0.25))
            d = ImageDraw.Draw(img)
            x0, x1 = 135 - 92, 135 - 92 + int(184 * k)
            d.line([x0, sign_y + 2, x1, sign_y + 18], fill=P["red"], width=3)
            d.line([x0, sign_y + 18, x1, sign_y + 2], fill=P["red"], width=3)
        # thought bubble: brick -> pillow?
        if t > t_conv and not exploded:
            bp = pop_scale(t, t_conv, 0.25)
            bub = gfx.new(96, 40)
            bd = ImageDraw.Draw(bub)
            bd.rounded_rectangle([1, 1, 94, 30], radius=8, fill=P["white"])
            bd.polygon([(20, 30), (28, 30), (18, 38)], fill=P["white"])
            bub.alpha_composite(cast.brick(), (8, 9))
            draw_text(bub, "→", 36, 9, color=P["ink"])
            draw_text(bub, "?", 86, 9, color=P["red"])
            bub.alpha_composite(cast.pillow(), (54, 7))
            bub = gfx.outline(bub)
            paste_scaled(img, bub, 190, 96, bp * 1.2, anchor="center")
        # brick falls into the funnel
        if t_br - 0.2 < t < t_br + 0.4:
            k = ease_in(prog(t, t_br - 0.2, 0.55))
            paste(img, cast.brick(), 91, lerp(60, 150, k), scale=2, anchor="center")
        # explosion
        if exploded:
            dt = t - t_al
            fx.burst(img, 135, 240, dt, n=40, speed=150, gravity=160, life=1.2,
                     colors=(P["orange"], P["gold"], P["red"], P["white"]), seed=3, size=3)
            fx.smoke(img, 195, 115, dt, n=12, life=1.8, rise=40)
            # brick pops out of the chute intact and bounces
            bx = lerp(222, 248, prog(dt, 0.4, 0.6))
            by = 263 + 70 * prog(dt, 0.4, 0.4) ** 2 if dt < 0.8 else 333 - abs(math.sin((dt - 0.8) * 8)) * 12 * max(0, 1 - (dt - 0.8) * 2)
            if dt > 0.35:
                paste(img, cast.brick(), bx, by, scale=2, anchor="center")
            if dt > 0.5:
                sp = text_sprite("IMPOSIBLE", P["red"], scale=2)
                paste_scaled(img, cast.stamp(sp), 135, 200, pop_scale(t, t_al + 0.5, 0.2), anchor="center")
        shake = 0
        if exploded:
            shake = 6 * (1 - prog(t, t_al, 0.6))
        elif t > t_br + 0.35:
            shake = 1
        out = gfx.camera(img, lerp(1.0, 1.06, ease_io(prog(t, t_br, 1.0))), 135, 220, shake=shake, t=t)
        if exploded and t - t_al < 0.15:
            out = gfx.flash(out, 0.8 * (1 - (t - t_al) / 0.15))
        return out

    # ---------------------------------------------------------- 5-7. SPLIT: two things happen
    def s_split(tl_, t):
        tg_ = tl_ + L("what").start - 0.0  # global time
        img = cast.tissue_bg(tg_, hue="dark")
        d = ImageDraw.Draw(img)
        t_dos = c("what", "dos")
        t_sh0, t_sh = L("shrink").start, c("shrink", "encoge")
        t_gr0 = L("grow").start
        t_com, t_mue, t_cre = c("grow", "comiendo"), c("grow", "mueves"), c("grow", "crece")
        focus = 0  # 0 none, -1 left, 1 right
        if tg_ >= t_sh0:
            focus = -1
        if tg_ >= t_gr0:
            focus = 1
        # panels
        lp = (6, 90, 132, 300)
        rp = (138, 90, 264, 300)
        d.rectangle(lp, fill=(48, 26, 52), outline=P["muscle_l"] if focus == -1 else P["violet"], width=2)
        d.rectangle(rp, fill=(56, 44, 38), outline=P["fat"] if focus == 1 else P["violet"], width=2)
        # numbers pop
        for i, (x, tt) in enumerate(((69, t_dos), (201, t_dos + 0.15))):
            s = pop_scale(tg_, tt, 0.3)
            paste_scaled(img, text_sprite(str(i + 1), P["gold"], scale=3), x, 72, s, anchor="center")
        # LEFT: muscle shrinks
        sk = ease_io(prog(tg_, t_sh - 0.2, 0.9))
        thick = lerp(18, 6, sk)
        fib = cast.muscle_fiber(48, thick, mood="sad" if sk > 0.2 else "happy", nuclei=4, t=tg_,
                                blink=blinking(tg_, 2.6))
        paste(img, fib, 69, 190, scale=2, anchor="center")
        label(img, "MÚSCULO", 69, 250, color=P["muscle_l"])
        if sk > 0.1:
            if (tg_ * 3) % 1 < 0.7:
                arrow(img, 69, 130, up=False, color=P["red"], size=7)
            label(img, "ATROFIA", 69, 270, color=P["fog"])
        # RIGHT: fat grows (food falls in, steps counter drops)
        gk = ease_out(prog(tg_, t_cre - 0.1, 0.9))
        foods = ("pizza", "burger", "donut", "soda")
        eat_times = (t_com, t_com + 0.25, c("grow", "igual"), c("grow", "igual") + 0.25)
        eaten = sum(1 for et in eat_times if tg_ > et + 0.25)
        r = lerp(13, 17, eaten / 4) + gk * 9
        mood = "greedy" if tg_ > t_com and tg_ < t_cre + 0.6 else ("smug" if tg_ >= t_cre else "happy")
        fat = cast.fat_cell(r, mood=mood, t=tg_, wobble=0.6 if t_com < tg_ < t_cre + 0.5 else 0.0,
                            blink=blinking(tg_, 3.0))
        paste(img, fat, 201, 190, scale=2, anchor="center")
        label(img, "GRASA", 201, 250, color=P["fat"])
        for kind, et in zip(foods, eat_times):
            if et - 0.35 < tg_ < et + 0.25:
                k = ease_in(prog(tg_, et - 0.35, 0.6))
                paste(img, cast.food(kind), 201 + (8 if kind in ("burger", "soda") else -8), lerp(96, 180, k),
                      scale=2, anchor="center")
        if tg_ > t_mue:
            steps = int(lerp(9000, 2000, ease_out(prog(tg_, t_mue, 0.6))))
            label(img, f"PASOS: {steps}", 201, 270, color=P["fog"])
        if gk > 0.1 and (tg_ * 3) % 1 < 0.7:
            arrow(img, 201, 130, up=True, color=P["gold"], size=7)
        # focus: dim the other panel
        if focus == -1:
            dk = gfx.darken(img.crop(rp), 0.45)
            img.paste(dk, (rp[0], rp[1]))
        elif focus == 1:
            dk = gfx.darken(img.crop(lp), 0.45)
            img.paste(dk, (lp[0], lp[1]))
        return img

    # ---------------------------------------------------------- 8. STATS + MIRROR
    def s_seesaw(tl_, t):
        tg_ = t + L("seesaw").start
        t_b, t_s, t_af, t_tr = c("seesaw", "baja"), c("seesaw", "sube"), c("seesaw", "afuera"), c("seesaw", "transformación")
        img = cast.gym_bg("gloomy").copy()
        mk = ease_io(prog(tg_, t_b - 0.3, 0.6))
        fk = ease_io(prog(tg_, t_s - 0.2, 0.6))
        # RPG stat window
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([20, 46, 250, 132], radius=4, fill=P["ink"], outline=P["white"], width=2)
        draw_text(img, "ESTADO: SIN ENTRENAR", 30, 54, color=P["gold"])
        bar(img, 30, 82, 150, 8, lerp(0.85, 0.35, mk), P["muscle"], label_txt="MÚSCULO")
        bar(img, 30, 112, 150, 8, lerp(0.3, 0.75, fk), P["fat"], label_txt="GRASA")
        if mk > 0.05:
            draw_text(img, "-" + str(int(mk * 50)), 190, 80, color=P["red"])
        if fk > 0.05:
            draw_text(img, "+" + str(int(fk * 45)), 190, 110, color=P["gold"])
        # hero + mirror (after "afuera")
        mp = ease_out(prog(tg_, t_af - 0.2, 0.5))
        pose = {"arm_l": (10, 8), "arm_r": (25, 70), "bicep": 0.2, "belly": 0.85, "mouth": "o",
                "eyes": "wide" if tg_ > t_tr else "open", "look": 1}
        paste(img, cast.hero(pose), lerp(135, 95, mp), 342, scale=3)
        if mp > 0:
            mx = int(lerp(330, 205, mp))
            d.rectangle([mx - 34, 170, mx + 34, 345], fill=P["steel_d"])
            d.rectangle([mx - 30, 174, mx + 30, 341], fill=P["sky"])
            refl = cast.hero({**pose, "eyes": "sad", "mouth": "sad"}).transpose(Image.FLIP_LEFT_RIGHT)
            refl = gfx.darken(refl, 0.15, P["blue_d"])
            mirror = gfx.new(60, 167)
            mirror.alpha_composite(refl.resize((refl.width * 2, refl.height * 2), Image.NEAREST),
                                   (30 - refl.width, 167 - refl.height * 2 + 2))
            img.alpha_composite(mirror, (mx - 30, 174))
            d.line([mx - 26, 180, mx - 16, 170 + 30], fill=P["white"])
        out = gfx.camera(img, lerp(1.0, 1.12, mp), lerp(135, 160, mp), 240)
        if tg_ > t_tr:
            dt = tg_ - t_tr
            if dt < 0.3:
                out = gfx.chroma_glitch(out, 6, tg_)
            sp = text_sprite('"TRANSFORMACIÓN"', P["fog"], scale=1)
            paste_scaled(out, sp, 135, 156, pop_scale(tg_, t_tr, 0.25) * 2, anchor="center")
        return out

    # ---------------------------------------------------------- 9. TWIST (silence + spotlight)
    def s_twist(tl_, t):
        tg_ = t + L("twist").start
        t_aq, t_bu = c("twist", "aquí"), c("twist", "bueno")
        img = cast.end_bg(tg_)
        fib = cast.muscle_fiber(40, 7, mood="sad" if tg_ < t_bu else "proud", nuclei=4, t=tg_,
                                glow=ease_out(prog(tg_, t_bu, 0.5)))
        paste(img, fib, 135, 230, scale=2, anchor="center")
        r = lerp(0, 70, ease_out(prog(tg_, t_aq - 0.2, 0.6)))
        out = gfx.spotlight(img, 135, 230, r, dark=0.92)
        if tg_ > t_bu:
            fx.sparkles(out, 135, 230, tg_, n=10, radius=50)
        return out

    # ---------------------------------------------------------- 10. MICE: nuclei stay
    def s_mice(tl_, t):
        tg_ = t + L("mice").start
        t_nu, t_qu, t_en = c("mice", "núcleos"), c("mice", "quedaron"), c("mice", "encogiera")
        img = cast.tissue_bg(tg_)
        # mouse badge
        d = ImageDraw.Draw(img)
        bp = pop_scale(tg_, L("mice").start, 0.3)
        badge = gfx.new(110, 34)
        bd = ImageDraw.Draw(badge)
        bd.rounded_rectangle([0, 0, 109, 33], radius=5, fill=P["ink"], outline=P["fog"])
        badge.alpha_composite(cast.mouse(tg_), (6, 7))
        draw_text(badge, "RATONES", 38, 13, color=P["white"])
        paste_scaled(img, badge, 135, 60, bp, anchor="center")
        sk = ease_io(prog(tg_, t_en - 0.1, 1.0))
        thick = lerp(24, 10, sk)
        glow = ease_out(prog(tg_, t_nu, 0.4))
        fib = cast.muscle_fiber(90, thick, mood="proud" if sk > 0.8 else ("happy" if sk < 0.2 else "sad"),
                                nuclei=8, t=tg_, glow=glow, blink=blinking(tg_, 2.8))
        paste(img, fib, 135, 200, scale=2, anchor="center")
        if tg_ > t_nu:
            col = P["nucleus_l"] if sk < 0.9 else (P["gold"] if (tg_ * 4) % 1 < 0.6 else P["white"])
            label(img, "NÚCLEOS: 8", 135, 262, color=col, scale=2)
        if tg_ > t_qu and sk < 0.05:
            label(img, "SE QUEDAN", 135, 286, color=P["fog"])
        if sk > 0.9:
            label(img, "MÚSCULO ↓  NÚCLEOS =", 135, 286, color=P["fog"])
        z = lerp(1.0, 1.1, ease_io(prog(tg_, t_en, 1.0)))
        return gfx.camera(img, z, 135, 220)

    # ---------------------------------------------------------- 11. DNA marks
    def s_dna(tl_, t):
        tg_ = t + L("dna").start
        t_pe, t_ma, t_cr = c("dna", "personas"), c("dna", "marcas"), c("dna", "crecer")
        img = cast.end_bg(tg_)
        marks = tuple(i for i, tt in zip((3, 7, 11, 15), (t_ma, t_ma + 0.18, t_ma + 0.36, t_ma + 0.54)) if tg_ > tt)
        hel = cast.dna(tg_, height=170, marks=marks, mark_glow=1.0)
        paste(img, hel, 85, 300, scale=1.5, anchor="mid_bottom")
        label(img, "ADN", 85, 50, color=P["sky"], scale=2)
        if tg_ > t_pe:
            sp = gfx.new(60, 40)
            bp = pop_scale(tg_, t_pe, 0.3)
            label(img, "PERSONAS", 200, 50, color=P["white"], scale=2)
            draw = cast.hero({"mouth": "smile", "eyes": "blink" if blinking(tg_, 2.2) else "open"})
            paste_scaled(img, draw, 200, 205, bp * 2, anchor="mid_bottom")
        # regrowing fiber on the right
        gk = ease_out(prog(tg_, t_cr - 0.2, 0.8))
        fib = cast.muscle_fiber(36, lerp(8, 18, gk), mood="proud" if gk > 0.5 else "happy", nuclei=4, t=tg_,
                                glow=0.6)
        paste(img, fib, 200, 275, scale=2, anchor="center")
        if gk > 0.1 and (tg_ * 3) % 1 < 0.7:
            arrow(img, 200, 238, up=True, color=P["green"], size=6)
        if marks:
            label(img, "MARCAS", 85, 310, color=P["gold"])
        return img

    # ---------------------------------------------------------- 12. RESOLVE: back to the gym
    def s_resolve(tl_, t):
        tg_ = t + L("resolve").start
        st = L("resolve").start
        t_es = c("resolve", "esperando")
        img = cast.gym_bg("sunrise").copy()
        walk_end = st + 1.7
        wk = prog(tg_, st, walk_end - st)
        x = lerp(-30, 135, ease_out(wk) if wk < 1 else 1)
        walking = wk < 1
        curl_k = prog(tg_, walk_end, 2.0)
        if walking:
            pose = {"walk": tg_ * 11, "bob": 1 if (tg_ * 5.5) % 1 < 0.5 else 0, "bicep": 0.35, "belly": 0.5,
                    "mouth": "smile", "arm_l": (15 * math.sin(tg_ * 11), 10), "arm_r": (-15 * math.sin(tg_ * 11), 10),
                    "holding": None}
        else:
            # curls: elbow angle oscillates; bicep grows with each rep (muscle memory!)
            rep = math.sin(curl_k * math.pi * 5) ** 2
            grow = ease_out(prog(tg_, walk_end, 2.2))
            pose = {"arm_r": (5, 10 + 140 * rep), "arm_l": (10, 10), "bicep": 0.35 + grow * 0.65 + rep * 0.1,
                    "belly": lerp(0.5, 0.15, grow), "mouth": "grit" if rep > 0.6 else "grin",
                    "eyes": "happy" if tg_ > t_es else "open", "holding": "dumbbell", "sweat": rep > 0.5}
        paste(img, cast.hero(pose), x, 342, scale=3)
        if not walking:
            fx.sparkles(img, 175, 245, tg_, n=8, radius=26)
        # stamp MITO
        out = gfx.camera(img, lerp(1.0, 1.08, prog(tg_, walk_end, 3)), 135, 240,
                         shake=5 * (1 - prog(tg_, t_es + 0.25, 0.4)) if tg_ > t_es + 0.25 else 0, t=tg_)
        if tg_ > t_es:
            s = lerp(4.0, 3.0, ease_out(prog(tg_, t_es, 0.25)))
            sp = cast.stamp(text_sprite("MITO", P["red"], scale=2, outline=None), P["red"])
            # slight tilt-free slam: scale down from big
            if tg_ - t_es < 0.25:
                s = lerp(6.0, 3.0, ease_in(prog(tg_, t_es, 0.25)))
            paste(out, sp, 135, 120, scale=s / 1.5, anchor="center")
            fx.burst(out, 135, 150, tg_ - t_es - 0.25, n=20, speed=90, gravity=60, life=0.8,
                     colors=(P["fog"], P["white"]), seed=9, size=2)
        return out

    # ---------------------------------------------------------- 13. CTA / end card
    def s_cta(tl_, t):
        tg_ = t + L("cta").start
        img = cast.end_bg(tg_)
        d = ImageDraw.Draw(img)
        # logo
        lp = pop_scale(tg_, L("cta").start, 0.3)
        logo = gfx.new(200, 60)
        draw_text(logo, "PRE-WORKOUT", 100, 4, color=P["gold"], scale=2, outline=P["ink"], align="center",
                  wave=(1, 6), t=tg_)
        draw_text(logo, "FITNESS SIN HUMO", 100, 32, color=P["fog"], outline=P["ink"], align="center")
        paste_scaled(img, logo, 135, 90, lp, anchor="center")
        # the two cell characters waving goodbye
        fib = cast.muscle_fiber(50, 16, mood="proud", nuclei=4, t=tg_, glow=0.5, blink=blinking(tg_, 2.0))
        paste(img, fib, 80, 200 + math.sin(tg_ * 4) * 3, scale=2, anchor="center")
        fat = cast.fat_cell(15, mood="happy", t=tg_, wobble=0.3, blink=blinking(tg_, 2.4, 1))
        paste(img, fat, 200, 205 + math.cos(tg_ * 4) * 3, scale=2, anchor="center")
        # share icon bouncing
        tm = c("cta", "mandarías")
        if tg_ > tm:
            b = abs(math.sin((tg_ - tm) * 6)) * 6
            sx, sy = 135, 270 - b
            share = gfx.new(40, 30)
            sd = ImageDraw.Draw(share)
            # curved "share" arrow pointing right
            sd.polygon([(24, 2), (38, 12), (24, 22), (24, 16), (16, 16), (8, 19), (3, 27), (3, 20),
                        (8, 12), (16, 8), (24, 8)], fill=P["gold"])
            sd.line([(25, 5), (34, 12)], fill=P["fat_l"])
            share = gfx.outline(share)
            paste(img, share, sx, sy, scale=2, anchor="center")
        # small MITO badge stays
        sp = cast.stamp(text_sprite("MITO", P["red"], scale=2, outline=None), P["red"])
        paste(img, sp, 135, 330, scale=1, anchor="center")
        return img

    scenes = [
        Scene("hook", 0.0, lambda tl_, t: s_hook(tl_, t)),
        Scene("doubt", L("doubt").start - 0.25, lambda tl_, t: s_doubt(tl_, tl_), trans="dither", trans_dur=0.3),
        Scene("cells", L("cells").start - 0.3, lambda tl_, t: s_cells(tl_, tl_), trans="iris", trans_dur=0.5),
        Scene("brick", L("brick").start - 0.1, lambda tl_, t: s_brick(tl_, tl_ - 0.0), trans="pixelate",
              trans_dur=0.3),
        Scene("split", L("what").start - 0.2, lambda tl_, t: s_split(t - L("what").start, t),
              trans="whip_left", trans_dur=0.3),
        Scene("seesaw", L("seesaw").start - 0.2, lambda tl_, t: s_seesaw(t - L("seesaw").start, t - L("seesaw").start),
              trans="dither", trans_dur=0.3),
        Scene("twist", L("twist").start - 0.05, lambda tl_, t: s_twist(0, t - L("twist").start), trans="cut"),
        Scene("mice", L("mice").start - 0.15, lambda tl_, t: s_mice(0, t - L("mice").start), trans="iris",
              trans_dur=0.4),
        Scene("dna", L("dna").start - 0.25, lambda tl_, t: s_dna(0, t - L("dna").start), trans="whip_left",
              trans_dur=0.3),
        Scene("resolve", L("resolve").start - 0.2, lambda tl_, t: s_resolve(0, t - L("resolve").start),
              trans="dither", trans_dur=0.35),
        Scene("cta", L("cta").start - 0.15, lambda tl_, t: s_cta(0, t - L("cta").start), trans="pixelate",
              trans_dur=0.3),
    ]
    # local time correction: scenes that use line-relative time get t_local relative to scene start
    fix = {"doubt": "doubt", "cells": "cells", "brick": "brick"}
    for sc in scenes:
        if sc.id in fix:
            ln = L(fix[sc.id])
            off = ln.start - sc.start
            f = sc.draw
            sc.draw = (lambda f_, off_: (lambda tl_, t: f_(tl_ - off_, t)))(f, off)
    emph = {norm(w): col for w, col in [
        ("grasa", P["fat"]), ("músculo", P["muscle_l"]), ("célula", P["pink"]), ("ladrillo", P["red_l"]),
        ("almohada", P["fog"]), ("encoge", P["red_l"]), ("crece", P["fat"]), ("transformación", P["lav"]),
        ("núcleos", P["nucleus_l"]), ("adn", P["sky"]), ("esperando", P["green"]), ("bueno", P["gold"]),
        ("ratones", P["fog"]), ("marcas", P["gold"]),
    ]}

    def post(img, t):
        return gfx.vignette_cached(img, 0.3)

    return Director(tl, scenes, SubStyle(y=352, scale=2, max_chars=15, emph=emph), post=post)
