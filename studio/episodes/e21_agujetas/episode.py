"""Episode 21: "¿Las agujetas son culpa del ácido láctico?" — MITO.

Sources (checked 2026-11-13): Cheung K, Hume P, Maxwell L 2003, Sports Med 33(2):145-164 — DOMS peaks
24-72 h; most likely explained by muscle damage + the inflammatory/repair response, not lactic acid.
Schwane JA et al. 1983, Med Sci Sports Exerc — level running raised blood lactate without DOMS;
downhill running produced DOMS with little lactate.
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast
from engine.gfx import P, prog, ease_out, ease_io, ease_back, lerp, paste
from engine.kit import (blinking, label, pop_scale, paste_scaled, arrow, text_sprite, stamp_slam, bar,
                        end_card, scenes_from, hook_camera)
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "e21_agujetas"
VERDICT = "MITO"
BPM = 100
LEAD_IN = 0.15
TAIL = 2.2
NARRATION_FILE = "episodes/e21_agujetas/narration.mp3"

LINES = [
    {"id": "hook", "text": "Al día siguiente de entrenar pierna... no puedes ni bajar las escaleras."},
    {"id": "blame", "text": "Y todos culpan al mismo villano: el ácido láctico.", "hold": 0.3},
    {"id": "problem", "text": "Pero esa historia tiene un problema."},
    {"id": "flat", "text": "En un estudio, correr en plano subió mucho el lactato... y casi no dio agujetas."},
    {"id": "down", "text": "Correr en bajada lo subió poco... y dio muchas más.", "hold": 0.3},
    {"id": "when", "text": "Las agujetas aparecen entre uno y tres días después."},
    {"id": "cause", "text": "Se cree que vienen de pequeños daños en el músculo, y de la reparación que viene después."},
    {"id": "resolve", "text": "El ácido láctico es inocente.", "hold": 0.8},
    {"id": "cta", "text": "¿Qué entrenaste ayer?"},
]

TITLE = "¿Las agujetas son culpa del ácido láctico? MITO #Shorts"
DESCRIPTION = (
    "¿Las agujetas son culpa del ácido láctico? MITO. En un estudio, correr en plano subió mucho el lactato sin "
    "dar agujetas, y correr en bajada dio más agujetas con poco lactato. Las agujetas aparecen entre 24 y 72 horas "
    "después y se relacionan con pequeños daños musculares y la reparación posterior.\n\n"
    "Fuentes: Schwane et al., Med Sci Sports Exerc, 1983 · Cheung, Hume & Maxwell, Sports Med, 2003.\n"
    "Voz: ElevenLabs.\n\n#fitness #agujetas #acidolactico #mitosfitness #fitnesssinhumo #Shorts")
TAGS = ["agujetas", "ácido láctico", "dolor muscular", "mitos fitness", "fitness sin humo"]


def sound_cues(tl):
    c = tl.cue
    out = [(0.0, "impact", 0.8), (0.02, "whoosh", 0.6),
           (c("hook", "escaleras"), "boing", 0.6),
           (c("blame") - 0.2, "whoosh", 0.5), (c("blame", "villano"), "impact", 0.7),
           (c("blame", "ácido"), "alarm", 0.4), (c("blame", "láctico") + 0.3, "clank", 0.8),
           (c("problem", "problema"), "glitch", 0.6),
           (c("flat") - 0.2, "whoosh", 0.4), (c("flat", "mucho"), "rise", 0.5), (c("flat", "casi"), "blip", 0.6),
           (c("down", "poco"), "deflate", 0.5), (c("down", "muchas"), "impact", 0.7),
           (c("when") - 0.2, "whoosh", 0.4), (c("when", "uno"), "pop", 0.6), (c("when", "tres"), "pop", 0.6),
           (c("cause", "daños"), "glitch", 0.4), (c("cause", "reparación"), "sparkle", 0.6),
           (c("resolve") - 0.2, "whoosh", 0.4), (c("resolve", "inocente"), "clank", 0.9),
           (c("resolve", "inocente") + 0.3, "stamp", 1.0), (c("resolve", "inocente") + 0.35, "sparkle", 0.6),
           (c("cta") - 0.15, "pop", 0.6), (c("cta", "ayer"), "ding", 0.6)]
    st = c("hook")
    for i in range(6):
        out.append((st + 0.4 + i * 0.45, "step", 0.5))
    return out


def music_sections(tl):
    c = tl.cue
    return [(0.0, c("blame") - 0.1, "groove"), (c("blame") - 0.1, c("problem") - 0.05, "tense"),
            (c("problem") - 0.05, c("problem", "problema"), "silence"),
            (c("problem", "problema"), c("when") - 0.1, "mystery"),
            (c("when") - 0.1, c("resolve") - 0.2, "groove"),
            (c("resolve") - 0.2, c("cta") - 0.1, "hope"), (c("cta") - 0.1, tl.total, "outro")]


def lactic(g, mood="angry", cuffs=False):
    """Original villain character: 'Ácido Láctico', a green droplet with a moustache."""
    S = gfx.new(40, 46)
    d = ImageDraw.Draw(S)
    wob = int(round(math.sin(g * 6)))
    d.polygon([(20, 2), (34, 24 + wob), (30, 40), (10, 40), (6, 24 - wob)], fill=P["green"])
    d.ellipse([6, 18, 34, 43], fill=P["green"])
    d.ellipse([11, 22, 16, 27], fill=(200, 255, 200))
    ey = 26
    if mood == "angry":
        d.line([12, ey - 4, 17, ey - 2], fill=P["ink"]); d.line([23, ey - 2, 28, ey - 4], fill=P["ink"])
    elif mood == "worried":
        d.line([12, ey - 2, 17, ey - 4], fill=P["ink"]); d.line([23, ey - 4, 28, ey - 2], fill=P["ink"])
    d.rectangle([14, ey, 15, ey + 2], fill=P["ink"]); d.rectangle([25, ey, 26, ey + 2], fill=P["ink"])
    d.line([14, ey + 6, 20, ey + 5, 26, ey + 6], fill=P["ink"], width=2)  # moustache
    if mood == "happy":
        d.line([16, ey + 9, 20, ey + 10, 24, ey + 9], fill=P["ink"])
    else:
        d.line([17, ey + 10, 23, ey + 10], fill=P["ink"])
    if cuffs:
        d.rectangle([4, 36, 12, 40], outline=P["steel_l"]); d.rectangle([28, 36, 36, 40], outline=P["steel_l"])
        d.line([12, 38, 28, 38], fill=P["steel_l"])
    return gfx.outline(S)


def make_director(tl):
    c, L = tl.cue, tl.line

    # 1. HOOK: Leo vs the stairs
    def s_stairs(g):
        img = cast.end_bg(g)
        d = ImageDraw.Draw(img)
        for i in range(6):  # stairs going down to the right
            x0, y0 = 20 + i * 40, 180 + i * 28
            d.rectangle([x0, y0, W, y0 + 28], fill=lerpc_(P["wood"], P["wood_d"], i / 6))
            d.line([x0, y0, W, y0], fill=P["cream"])
        k = prog(g, 0.3, 3.0)
        step = min(3, int(k * 4))
        x = 40 + step * 40 + 10
        y = 180 + step * 28
        shake = math.sin(g * 40) * 1.5
        pose = {"mouth": "grit", "eyes": "sad", "sweat": True, "arm_l": (60, 20), "arm_r": (80, 30),
                "walk": 0.6 if (g * 3) % 1 < 0.5 else -0.6}
        paste(img, cast.hero(pose), x + shake, y, scale=3)
        if g > 0.6:
            for i, (tx, ty) in enumerate(((x - 70, y - 215), (x + 70, y - 195))):
                if (g * 2 + i * 0.5) % 1 < 0.6:
                    paste(img, text_sprite("¡AY!", P["red_l"], scale=2), tx, ty, anchor="center")
        # legs glowing red = soreness
        return hook_camera(img, g, cx=x, cy=y - 80)

    # 2-3. COURTROOM: lactic acid accused
    def s_court(g):
        img = cast.lab_bg(g)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W, 330], fill=(70, 44, 40))
        for x in range(0, W, 30):
            d.rectangle([x, 0, x + 3, 330], fill=(90, 58, 50))
        # judge bench
        d.rectangle([60, 70, 210, 140], fill=P["wood"])
        d.rectangle([60, 70, 210, 76], fill=P["wood_d"])
        label(img, "TRIBUNAL DEL GYM", 135, 40, color=P["gold"], scale=2)
        t_vil, t_ac = c("blame", "villano"), c("blame", "ácido")
        t_pro = c("problem", "problema")
        # dock with the accused
        d.rectangle([150, 220, 250, 330], fill=P["wood_d"])
        s = pop_scale(g, t_vil, 0.3)
        mood = "worried" if g > t_pro else "angry"
        paste_scaled(img, lactic(g, mood, cuffs=True), 200, 210, s * 2, anchor="center")
        if g > t_ac:
            paste_scaled(img, text_sprite("ACUSADO: ÁCIDO LÁCTICO", P["white"], scale=1), 135, 160,
                         pop_scale(g, t_ac, 0.25) * 1.5)
        # crowd pointing
        for i in range(8):
            x = 20 + i * 16
            img.alpha_composite(cast.tiny_person([P["fog"], P["sky"], P["pink"]][i % 3]).resize((10, 18), 0),
                                (x, 300 - int(abs(math.sin(g * 7 + i)) * 4)))
        # gavel
        gk = prog(g, c("blame", "láctico") + 0.2, 0.2)
        ang = lerp(-0.9, 0.2, gk) if gk < 1 else 0.2
        gx, gy = 135, 64
        d.line([gx, gy, gx + math.cos(ang) * 30, gy + math.sin(ang) * 30], fill=P["wood_d"], width=4)
        d.rectangle([gx + math.cos(ang) * 30 - 6, gy + math.sin(ang) * 30 - 5,
                     gx + math.cos(ang) * 30 + 6, gy + math.sin(ang) * 30 + 5], fill=P["wood"])
        if g > t_pro:
            paste_scaled(img, text_sprite("¿SEGURO?", P["gold"], scale=2), 135, 190, pop_scale(g, t_pro))
        out = gfx.camera(img, lerp(1.0, 1.1, prog(g, t_vil, 2)), 170, 200)
        if 0 < g - t_pro < 0.2:
            out = gfx.chroma_glitch(out, 6, g)
        return out

    # 4-5. EVIDENCE: flat vs downhill running
    def s_evidence(g):
        img = cast.end_bg(g)
        d = ImageDraw.Draw(img)
        t_flat, t_down = L("flat").start, L("down").start
        for i, (name, tt, y, slope) in enumerate((("PRUEBA A: EN PLANO", t_flat, 60, 0.0),
                                                   ("PRUEBA B: EN BAJADA", t_down, 200, 0.35))):
            s = pop_scale(g, tt, 0.3)
            if s <= 0:
                continue
            label(img, name, 135, y, color=P["gold"] if i == 0 else P["sky"])
            # mini track
            x0, x1 = 20, 130
            d.line([x0, y + 90, x1, y + 90 + (x1 - x0) * slope], fill=P["fog"], width=2)
            ph = ((g - tt) * 0.5) % 1
            rx = lerp(x0 + 10, x1 - 10, ph)
            ry = y + 90 + (rx - x0) * slope
            paste(img, cast.hero({"walk": g * 14, "mouth": "smile", "arm_l": (20 * math.sin(g * 14), 40),
                                  "arm_r": (-20 * math.sin(g * 14), 40)}), rx, ry, scale=1)
            # meters
            lac = 0.85 if i == 0 else 0.25
            pain = 0.12 if i == 0 else 0.85
            kl = ease_out(prog(g, c("flat", "mucho") if i == 0 else c("down", "poco"), 0.6))
            kp = ease_out(prog(g, c("flat", "casi") if i == 0 else c("down", "muchas"), 0.6))
            label(img, "LACTATO", 200, y + 24, color=P["green"])
            bar(img, 150, y + 36, 100, 7, lac * kl, P["green"])
            label(img, "AGUJETAS", 200, y + 56, color=P["red_l"])
            bar(img, 150, y + 68, 100, 7, pain * kp, P["red"])
        return img

    # 6-7. WHEN + CAUSE: calendar 1-3 days, micro damage and repair crew
    def s_cause(g):
        img = cast.tissue_bg(g)
        d = ImageDraw.Draw(img)
        t1, t3 = c("when", "uno"), c("when", "tres")
        t_dan, t_rep = c("cause", "daños"), c("cause", "reparación")
        for i, day in enumerate(("DÍA 1", "DÍA 2", "DÍA 3")):
            s = pop_scale(g, t1 + i * (t3 - t1) / 2, 0.25)
            card = gfx.new(60, 40)
            cd = ImageDraw.Draw(card)
            cd.rectangle([1, 1, 58, 38], fill=P["white"])
            cd.rectangle([1, 1, 58, 11], fill=P["red"])
            from engine.font import draw_text
            draw_text(card, day, 30, 18, color=P["ink"], align="center")
            paste_scaled(img, gfx.outline(card), 60 + i * 75, 70, s)
        fib = cast.muscle_fiber(90, 22, mood="sad" if g < t_rep else "happy", nuclei=6, t=g)
        paste(img, fib, 135, 200, scale=2, anchor="center")
        if g > t_dan:
            k = ease_out(prog(g, t_dan, 0.5))
            heal = ease_io(prog(g, t_rep + 0.2, 1.6))
            for j, x in enumerate((70, 115, 160, 205)):
                if j / 4 < heal:
                    continue
                d.line([x, 182, x + 5, 192, x - 2, 200, x + 4, 214], fill=P["ink"], width=2)
            if g > t_rep:
                for j in range(4):
                    bx = 70 + j * 45 + math.sin(g * 6 + j) * 3
                    by = 150 + abs(math.sin(g * 5 + j)) * 6
                    img.alpha_composite(cast.protein_block(P["gold"]), (int(bx), int(by)))
                label(img, "REPARACIÓN", 135, 250, color=P["gold"], scale=2)
            else:
                label(img, "MICRODAÑOS", 135, 250, color=P["red_l"], scale=2)
        return img

    # 8. RESOLVE: not guilty
    def s_resolve(g):
        img = cast.lab_bg(g)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W, 330], fill=(70, 44, 40))
        t_ino = c("resolve", "inocente")
        free = g > t_ino
        paste(img, lactic(g, "happy" if free else "worried", cuffs=not free), 135, 230, scale=3, anchor="center")
        if free:
            fx.burst(img, 135, 300, g - t_ino, n=24, speed=110, gravity=120, life=1.0,
                     colors=(P["gold"], P["pink"], P["sky"], P["green"]), seed=5)
            paste_scaled(img, text_sprite("INOCENTE", P["green"], scale=3), 135, 300, pop_scale(g, t_ino, 0.25))
        out = gfx.camera(img, 1.0)
        stamp_slam(out, VERDICT, g, t_ino + 0.3, y=100)
        return out

    def s_cta(g):
        img = cast.end_bg(g)
        end_card(img, g, L("cta").start, c("cta", "ayer"), VERDICT)
        return img

    scenes = scenes_from(tl, [
        ("stairs", "hook", s_stairs, "cut", 0.3, 0),
        ("court", "blame", s_court, "whip_left", 0.3, 0.2),
        ("evidence", "flat", s_evidence, "iris", 0.45, 0.25),
        ("cause", "when", s_cause, "dither", 0.3, 0.2),
        ("resolve", "resolve", s_resolve, "whip_left", 0.3, 0.25),
        ("cta", "cta", s_cta, "pixelate", 0.3, 0.15),
    ])
    emph = {norm(w): col for w, col in [("villano", P["red_l"]), ("ácido", P["green"]), ("láctico", P["green"]),
            ("lactato", P["green"]), ("agujetas", P["red_l"]), ("bajada", P["sky"]), ("daños", P["red_l"]),
            ("reparación", P["gold"]), ("inocente", P["green"]), ("problema", P["gold"])]}
    return Director(tl, scenes, SubStyle(y=352, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.3))


def lerpc_(a, b, t):
    return gfx.lerpc(a, b, t)
