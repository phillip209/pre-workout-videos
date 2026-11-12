"""Episode 19: "¿La cafeína mejora el rendimiento?" — VERDAD.

Source (checked 2026-11-12): Grgic J et al. 2020 (online 2019), Br J Sports Med 54(11):681-688 —
umbrella review of 21 meta-analyses (11 systematic reviews): caffeine was ergogenic for aerobic
endurance, muscle strength, muscle endurance, power, jumping and speed; evidence mostly moderate
quality; effect generally larger for aerobic than anaerobic exercise; most participants young men.
"""
from __future__ import annotations

import math
import os

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast
from engine.gfx import P, prog, ease_out, ease_io, ease_in, lerp, paste
from engine.kit import (blinking, label, pop_scale, paste_scaled, arrow, text_sprite, stamp_slam, bar,
                        badge, end_card, scenes_from, hook_camera)
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "e19_cafeina"
VERDICT = "VERDAD"
BPM = 104
LEAD_IN = 0.15
TAIL = 2.2
NARRATION_FILE = "episodes/e19_cafeina/narration.mp3"

LINES = [
    {"id": "hook", "text": "Un café antes de entrenar. ¿Truco real... o puro cuento?", "hold": 0.3},
    {"id": "setup", "text": "Hay muchísimos estudios sobre esto. Así que un equipo hizo algo distinto:"},
    {"id": "study", "text": "revisó veintiún metaanálisis a la vez.", "hold": 0.3},
    {"id": "result", "text": "Y encontró mejoras en resistencia, fuerza, potencia, saltos y velocidad.", "hold": 0.3},
    {"id": "aero", "text": "El efecto fue mayor en ejercicios de resistencia, como correr o pedalear."},
    {"id": "caveat", "text": "Ojo: la calidad de la evidencia fue moderada... y la mayoría de los estudios fueron en hombres jóvenes."},
    {"id": "resolve", "text": "Así que sí: la cafeína ayuda. Pero no reemplaza el entrenamiento.", "hold": 0.7},
    {"id": "cta", "text": "¿Tú entrenas con café?"},
]
SPOKEN = ("Un café antes de entrenar. ¿Truco real... o puro cuento? Hay muchísimos estudios sobre esto. Así que un "
          "equipo hizo algo distinto: revisó veintiún metaanálisis a la vez. Y encontró mejoras en resistencia, "
          "fuerza, potencia, saltos y velocidad. El efecto fue mayor en ejercicios de resistencia, como correr o "
          "pedalear. Ojo: la calidad de la evidencia fue moderada... y la mayoría de los estudios fueron en "
          "hombres jóvenes. <break time=\"0.7s\" /> Así que sí: la cafeína ayuda. Pero no reemplaza el "
          "entrenamiento. ¿Tú entrenas con café?")

VOICE = {"voice_id": os.environ.get("PW_VOICE_ID", "qRUgOhnxGASxirG4fKjv"), "model": "eleven_multilingual_v2",
         "settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True}}

TITLE = "¿La cafeína mejora el rendimiento deportivo? VERDAD #Shorts"
DESCRIPTION = (
    "¿La cafeína mejora el rendimiento deportivo? VERDAD. Una revisión de 21 metaanálisis encontró mejoras en "
    "resistencia aeróbica, fuerza, potencia, saltos y velocidad, con mayor efecto en ejercicio aeróbico "
    "(evidencia de calidad moderada, sobre todo en hombres jóvenes).\n\n"
    "Fuentes: Grgic et al., Br J Sports Med, 2020.\nVoz: ElevenLabs.\n\n"
    "#fitness #cafeina #rendimiento #mitosfitness #fitnesssinhumo #Shorts")
TAGS = ["cafeína", "rendimiento", "suplementos", "fitness", "fitness sin humo"]


def sound_cues(tl):
    c = tl.cue
    out = [(0.0, "impact", 0.8), (0.02, "whoosh", 0.6),
           (c("hook", "truco"), "sparkle", 0.6), (c("hook", "cuento"), "glitch", 0.6),
           (c("setup") - 0.2, "whoosh", 0.5), (c("setup", "distinto"), "thud", 0.7),
           (c("study", "veintiún"), "rise", 0.6), (c("study", "vez"), "impact", 0.7),
           (c("aero") - 0.2, "whoosh", 0.4), (c("aero", "correr"), "step", 0.6),
           (c("caveat") - 0.2, "whoosh", 0.4), (c("caveat", "moderada"), "boing", 0.5),
           (c("resolve") - 0.2, "whoosh", 0.4), (c("resolve", "ayuda"), "stamp", 1.0),
           (c("resolve", "ayuda") + 0.05, "sparkle", 0.6), (c("resolve", "entrenamiento"), "clank", 0.6),
           (c("cta") - 0.15, "pop", 0.6), (c("cta", "café"), "ding", 0.6)]
    for w in ("resistencia", "fuerza", "potencia", "saltos", "velocidad"):
        out.append((c("result", w), "pop", 0.7))
    return out


def music_sections(tl):
    c = tl.cue
    return [(0.0, c("setup") - 0.2, "tense"), (c("setup") - 0.2, c("study", "vez"), "mystery"),
            (c("study", "vez"), c("caveat") - 0.1, "groove"),
            (c("caveat") - 0.1, c("resolve") - 0.2, "mystery"),
            (c("resolve") - 0.2, c("cta") - 0.1, "hope"), (c("cta") - 0.1, tl.total, "outro")]


def make_director(tl):
    c, L = tl.cue, tl.line

    # 1. HOOK: mug slides in, sparkle vs glitch
    def s_hook(g):
        img = cast.gym_bg("night").copy()
        x = lerp(330, 150, ease_out(prog(g, 0.0, 0.5)))
        t_tr, t_cu = c("hook", "truco"), c("hook", "cuento")
        mood = "smug" if g < t_cu else "shock"
        paste(img, cast.hero({"arm_r": (40, 60), "mouth": "o" if g > t_cu else "smile", "eyes": "wide" if g > t_cu else "open"}),
              90, 342, scale=3)
        paste(img, cast.coffee(g, mood=mood), x, 300, scale=3, anchor="mid_bottom")
        if t_tr < g < t_cu:
            fx.sparkles(img, x, 220, g, n=10, radius=40)
        if g > t_cu:
            paste_scaled(img, text_sprite("?", P["gold"], scale=4), x + 30, 140, pop_scale(g, t_cu))
        out = hook_camera(img, g, cx=135, cy=230)
        if 0 < g - t_cu < 0.25:
            out = gfx.chroma_glitch(out, 7, g)
        return out

    # 2-3. SETUP + STUDY: paper rain -> evidence pyramid with an umbrella (umbrella review)
    def s_study(g):
        img = cast.lab_bg(g)
        d = ImageDraw.Draw(img)
        t_di, t_21, t_vez = c("setup", "distinto"), c("study", "veintiún"), c("study", "vez")
        frozen = g > t_di
        # paper rain
        import random
        rnd = random.Random(3)
        for i in range(30):
            x = rnd.randrange(10, 260)
            sp = rnd.uniform(60, 120)
            y = ((g if not frozen else t_di) * sp + rnd.randrange(480)) % 480
            if not frozen or i % 2 == 0:
                d.rectangle([x, y, x + 8, y + 10], fill=P["white"] if i % 2 else P["cream"])
                d.line([x + 2, y + 3, x + 6, y + 3], fill=P["fog"])
        if frozen:
            img = gfx.darken(img, 0.45)
            d = ImageDraw.Draw(img)
        # pyramid: base = studies, mid = 21 meta-analyses, umbrella on top
        if g > t_21 - 0.2:
            k = ease_out(prog(g, t_21 - 0.2, 1.0))
            n = int(k * 21)
            rows = [6, 5, 4, 3, 2, 1]
            idx = 0
            for r, cnt in enumerate(rows):
                for j in range(cnt):
                    if idx >= n:
                        break
                    bx = 135 - cnt * 15 + j * 30 + 2
                    by = 300 - r * 22
                    d.rectangle([bx, by, bx + 26, by + 18], fill=P["blue"], outline=P["sky"])
                    d.line([bx + 5, by + 6, bx + 20, by + 6], fill=P["sky"])
                    idx += 1
            label(img, f"{n} METAANÁLISIS", 135, 322, color=P["sky"], scale=2)
        if g > t_vez:
            k = ease_out(prog(g, t_vez, 0.4))
            uy = lerp(30, 150, k)
            d.pieslice([55, uy, 215, uy + 80], 180, 360, fill=P["red"])
            for xx in range(55, 216, 32):
                d.arc([xx, uy + 30, xx + 32, uy + 50], 180, 360, fill=P["red_d"])
            d.line([135, uy + 40, 135, uy + 110], fill=P["wood"], width=3)
            label(img, "REVISIÓN PARAGUAS", 135, uy - 14, color=P["gold"], scale=2)
        return img

    # 4-5. RESULT: five stat cards; aerobic biggest
    def s_result(g):
        img = cast.end_bg(g)
        stats = [("RESISTENCIA", "resistencia", P["green"]), ("FUERZA", "fuerza", P["red_l"]),
                 ("POTENCIA", "potencia", P["gold"]), ("SALTOS", "saltos", P["sky"]),
                 ("VELOCIDAD", "velocidad", P["pink"])]
        t_aero = L("aero").start
        paste(img, cast.coffee(g, mood="happy"), 135, 96, scale=2, anchor="mid_bottom")
        for i, (name, w, col) in enumerate(stats):
            tt = c("result", w)
            s = pop_scale(g, tt, 0.25)
            if s <= 0:
                continue
            y = 120 + i * 34
            label(img, name, 30, y, color=col, center=False)
            val = 0.55 if i else 0.55
            if g > t_aero and i == 0:
                val = lerp(0.55, 0.9, ease_out(prog(g, t_aero, 0.6)))
            bar(img, 30, y + 12, 150, 7, val * ease_out(prog(g, tt, 0.4)), col)
            label(img, "+", 196, y + 8, color=col, scale=2)
        if g > t_aero:
            d = ImageDraw.Draw(img)
            k = ease_out(prog(g, t_aero, 0.4))
            d.rectangle([24, 116, 246, 146], outline=P["green"], width=2)
            label(img, "MAYOR EFECTO", 215, 118, color=P["green"])
            if g > c("aero", "correr"):
                rider = cast.hero({"walk": g * 14, "mouth": "grin", "arm_l": (20 * math.sin(g * 14), 40),
                                   "arm_r": (-20 * math.sin(g * 14), 40)})
                paste(img, rider, lerp(-30, 225, prog(g, c("aero", "correr"), 1.6)), 330, scale=1.5)
        return img

    # 6. CAVEAT: quality gauge + who was studied
    def s_caveat(g):
        img = cast.lab_bg(g)
        d = ImageDraw.Draw(img)
        t_mod, t_hom = c("caveat", "moderada"), c("caveat", "hombres")
        label(img, "CALIDAD DE LA EVIDENCIA", 135, 70, color=P["white"])
        cx, cy, r = 135, 170, 60
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 240, fill=P["red"])
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 240, 300, fill=P["gold"])
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 300, 360, fill=P["green"])
        d.pieslice([cx - r + 14, cy - r + 14, cx + r - 14, cy + r - 14], 180, 360, fill=P["night"])
        ang = math.radians(lerp(185, 270, ease_out(prog(g, L("caveat").start, 0.8))) + math.sin(g * 6) * 0.03)
        d.line([cx, cy, cx + math.cos(ang) * (r - 8), cy + math.sin(ang) * (r - 8)], fill=P["white"], width=3)
        if g > t_mod:
            label(img, "MODERADA", 135, 182, color=P["gold"], scale=2)
        if g > t_hom - 0.1:
            k = ease_out(prog(g, t_hom - 0.1, 0.8))
            for i in range(int(k * 20)):
                col = P["sky"] if i % 5 else P["pink"]
                img.alpha_composite(cast.tiny_person(col).resize((10, 18), 0), (45 + (i % 10) * 18, 230 + (i // 10) * 24))
            label(img, "MAYORÍA: HOMBRES JÓVENES", 135, 284, color=P["sky"])
        return img

    # 7. RESOLVE: coffee power-up, keeps training, stamp
    def s_resolve(g):
        img = cast.gym_bg("sunrise").copy()
        t_ay, t_en = c("resolve", "ayuda"), c("resolve", "entrenamiento")
        rep = math.sin(g * 6) ** 2
        paste(img, cast.hero({"arm_r": (5, 10 + 140 * rep), "bicep": 0.85, "holding": "dumbbell", "mouth": "grin",
                              "eyes": "happy" if g > t_ay else "open", "sweat": True}), 150, 342, scale=3)
        paste(img, cast.coffee(g, mood="happy"), 60, 330, scale=2, anchor="mid_bottom")
        if g > t_ay:
            d = ImageDraw.Draw(img)
            for i in range(10):
                a = g * 3 + i * 0.63
                rr = 70 + math.sin(g * 6 + i) * 4
                d.rectangle([150 + math.cos(a) * rr, 260 + math.sin(a) * rr * 1.2,
                             152 + math.cos(a) * rr, 262 + math.sin(a) * rr * 1.2], fill=P["gold"])
        out = gfx.camera(img, 1.0)
        stamp_slam(out, VERDICT, g, t_ay, y=110)
        return out

    def s_cta(g):
        img = cast.end_bg(g)
        end_card(img, g, L("cta").start, c("cta", "café"), VERDICT)
        return img

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("study", "setup", s_study, "whip_left", 0.3, 0.2),
        ("result", "result", s_result, "iris", 0.45, 0.25),
        ("caveat", "caveat", s_caveat, "dither", 0.3, 0.2),
        ("resolve", "resolve", s_resolve, "whip_left", 0.3, 0.25),
        ("cta", "cta", s_cta, "pixelate", 0.3, 0.15),
    ])
    emph = {norm(w): col for w, col in [("café", P["wood"]), ("veintiún", P["gold"]), ("metaanálisis", P["sky"]),
            ("resistencia", P["green"]), ("fuerza", P["red_l"]), ("potencia", P["gold"]), ("saltos", P["sky"]),
            ("velocidad", P["pink"]), ("moderada", P["gold"]), ("ayuda", P["green"])]}
    return Director(tl, scenes, SubStyle(y=352, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.3))
