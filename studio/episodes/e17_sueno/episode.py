"""Episode 17: "¿Dormir poco frena tus músculos?" — PARCIALMENTE CIERTO.

Source (checked 2026-11-12): Saner NJ et al. 2020, J Physiol 598(8):1523-1536 — 24 healthy young
men, 5 nights: normal sleep (8 h in bed), sleep restriction (4 h), or 4 h + high-intensity interval
exercise. Myofibrillar protein synthesis fell with restriction (1.24 vs 1.53 %/day) and was
maintained with HIIE (1.61). Small study.
"""
from __future__ import annotations

import math
import os

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast
from engine.gfx import P, prog, ease_out, ease_io, lerp, paste
from engine.kit import (blinking, label, pop_scale, paste_scaled, arrow, text_sprite, stamp_slam,
                        badge, end_card, scenes_from, hook_camera)
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "e17_sueno"
VERDICT = "PARCIALMENTE CIERTO"
BPM = 88
LEAD_IN = 0.15
TAIL = 2.2
NARRATION_FILE = "episodes/e17_sueno/narration.mp3"

LINES = [
    {"id": "hook", "text": "Entrenas duro... pero duermes cuatro horas."},
    {"id": "q", "text": "¿Tus músculos lo notan?", "hold": 0.3},
    {"id": "study", "text": "Un estudio lo puso a prueba con veinticuatro hombres jóvenes, durante cinco noches."},
    {"id": "groups", "text": "Un grupo durmió ocho horas. Otro, solo cuatro."},
    {"id": "result", "text": "En los que durmieron cuatro horas, la construcción de proteína en el músculo bajó.", "hold": 0.3},
    {"id": "twist", "text": "Pero había un tercer grupo: también durmió cuatro horas... y además hizo ejercicio intenso por intervalos."},
    {"id": "twist2", "text": "En ellos, esa construcción se mantuvo normal.", "hold": 0.4},
    {"id": "caveat", "text": "Es un estudio pequeño, y falta más evidencia."},
    {"id": "resolve", "text": "Entrenar ayuda... pero dormir también es parte del entrenamiento.", "hold": 0.7},
    {"id": "cta", "text": "¿Cuántas horas dormiste anoche?"},
]
SPOKEN = ("Entrenas duro... pero duermes cuatro horas. ¿Tus músculos lo notan? Un estudio lo puso a prueba con "
          "veinticuatro hombres jóvenes, durante cinco noches. Un grupo durmió ocho horas. Otro, solo cuatro. "
          "En los que durmieron cuatro horas, la construcción de proteína en el músculo bajó. Pero había un "
          "tercer grupo: también durmió cuatro horas... y además hizo ejercicio intenso por intervalos. En ellos, "
          "esa construcción se mantuvo normal. Es un estudio pequeño, y falta más evidencia. "
          "<break time=\"0.7s\" /> Entrenar ayuda... pero dormir también es parte del entrenamiento. "
          "¿Cuántas horas dormiste anoche?")

VOICE = {"voice_id": os.environ.get("PW_VOICE_ID", "qRUgOhnxGASxirG4fKjv"), "model": "eleven_multilingual_v2",
         "settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True}}

TITLE = "¿Dormir poco frena tus músculos? PARCIALMENTE CIERTO #Shorts"
DESCRIPTION = (
    "¿Dormir poco frena la creación de músculo? PARCIALMENTE CIERTO. En un estudio con 24 hombres jóvenes, "
    "5 noches durmiendo 4 horas redujeron la síntesis de proteína muscular frente a dormir 8 horas; el grupo "
    "que además hizo ejercicio intervalado la mantuvo en niveles normales. Fue un estudio pequeño: falta más "
    "evidencia.\n\nFuentes: Saner et al., J Physiol, 2020.\nVoz: ElevenLabs.\n\n"
    "#fitness #sueno #musculo #mitosfitness #fitnesssinhumo #Shorts")
TAGS = ["sueño", "músculo", "recuperación", "fitness", "fitness sin humo"]


def sound_cues(tl):
    c = tl.cue
    return [(0.0, "impact", 0.8), (0.02, "whoosh", 0.6),
            (c("hook", "pero") - 0.15, "whoosh", 0.6), (c("hook", "cuatro"), "alarm", 0.6),
            (c("q") - 0.1, "rise", 0.4), (c("q", "notan"), "pop", 0.6),
            (c("study") - 0.2, "whoosh", 0.5), (c("study", "veinticuatro"), "sparkle", 0.5),
            (c("study", "cinco"), "blip", 0.7),
            (c("groups", "ocho"), "pop", 0.7), (c("groups", "cuatro"), "pop", 0.7),
            (c("result") - 0.2, "whoosh", 0.4), (c("result", "bajó"), "deflate", 0.8),
            (c("twist", "tercer"), "impact", 0.6), (c("twist", "intervalos"), "rise", 0.6),
            (c("twist2", "normal"), "ding", 0.8),
            (c("caveat") - 0.2, "whoosh", 0.4), (c("caveat", "pequeño"), "boing", 0.5),
            (c("resolve") - 0.2, "whoosh", 0.4), (c("resolve", "entrenamiento"), "stamp", 1.0),
            (c("resolve", "entrenamiento") + 0.05, "sparkle", 0.6),
            (c("cta") - 0.15, "pop", 0.6), (c("cta", "anoche"), "ding", 0.6)]


def music_sections(tl):
    c = tl.cue
    return [(0.0, c("hook", "pero") - 0.1, "groove"), (c("hook", "pero") - 0.1, c("study") - 0.2, "tense"),
            (c("study") - 0.2, c("twist") - 0.1, "mystery"),
            (c("twist") - 0.1, c("twist", "tercer"), "silence"),
            (c("twist", "tercer"), c("caveat") - 0.1, "groove"),
            (c("caveat") - 0.1, c("resolve") - 0.2, "mystery"),
            (c("resolve") - 0.2, c("cta") - 0.1, "hope"), (c("cta") - 0.1, tl.total, "outro")]


def make_director(tl):
    c, L = tl.cue, tl.line

    def zzz(img, x, y, g, n=3, color=P["lav"]):
        for i in range(n):
            ph = (g * 0.7 + i / n) % 1
            draw_s = 1 if ph < 0.5 else 2
            from engine.font import draw_text
            draw_text(img, "Z", x + ph * 20 + i * 2, y - ph * 40, color=color, scale=draw_s, outline=P["ink"])

    # 1. HOOK: lifting hard -> whip -> awake in bed at 3am
    def s_hook(g):
        t_pero = c("hook", "pero")
        if g < t_pero - 0.05:
            img = cast.gym_bg("night").copy()
            rep = math.sin(g * 7) ** 2
            paste(img, cast.hero({"arm_r": (5, 10 + 140 * rep), "arm_l": (5, 10 + 140 * (1 - rep)), "bicep": 0.9,
                                  "mouth": "grit", "sweat": True, "holding": "dumbbell"}), 135, 342, scale=3)
            return hook_camera(img, g, cx=135, cy=240)
        img = cast.bedroom_bg(g)
        tired = cast.sleeping_head("tired")
        paste(img, cast.bed(tired, t=g), 135, 330, scale=2)
        t4 = c("hook", "cuatro")
        clock = cast.digital_clock("03:00" if g < t4 else "04 H", P["red"])
        if g > t4 and (g * 6) % 1 < 0.5:
            clock = gfx.flash(clock, 0.4, P["red_l"])
        paste(img, clock, 40, 270, scale=1, anchor="mid_bottom")
        out = gfx.camera(img, lerp(1.25, 1.0, ease_out(prog(g, t_pero - 0.05, 0.4))), 135, 280)
        if g > t4:
            out = gfx.camera(out, 1.0, 135, 240, shake=2 * (1 - prog(g, t4, 0.5)), t=g)
        return out

    # 2. Q: the sleepy muscle fiber
    def s_q(g):
        img = cast.tissue_bg(g)
        fib = cast.muscle_fiber(80, 22, mood="sad", nuclei=5, t=g * 0.3, blink=(g % 1.6) < 0.5)
        paste(img, fib, 135, 200 + math.sin(g * 2) * 2, scale=2, anchor="center")
        zzz(img, 190, 160, g)
        if g > c("q", "notan"):
            paste_scaled(img, text_sprite("?", P["gold"], scale=4), 135, 110, pop_scale(g, c("q", "notan")))
        return img

    # 3. STUDY: 24 men, 5 nights
    def s_study(g):
        img = cast.end_bg(g)
        t24, t5 = c("study", "veinticuatro"), c("study", "cinco")
        k = ease_out(prog(g, t24 - 0.1, 0.9))
        for i in range(int(k * 24)):
            img.alpha_composite(cast.tiny_person(P["sky"]).resize((10, 18), 0), (63 + (i % 8) * 18, 80 + (i // 8) * 26))
        if k > 0:
            label(img, "24 HOMBRES JÓVENES", 135, 166, color=P["sky"])
        for i in range(5):
            s = pop_scale(g, t5 + i * 0.12, 0.25)
            moon = gfx.new(14, 14)
            md = ImageDraw.Draw(moon)
            md.ellipse([1, 1, 12, 12], fill=P["cream"])
            md.ellipse([5, -1, 15, 10], fill=(0, 0, 0, 0))
            paste_scaled(img, gfx.outline(moon), 63 + i * 36, 220, s * 2)
        if g > t5:
            label(img, "5 NOCHES", 135, 248, color=P["cream"], scale=2)
        return img

    # 4-7. LAB OF BEDS + PROTEIN "CONSTRUCTION"
    def s_beds(g):
        img = cast.bedroom_bg(g)
        d = ImageDraw.Draw(img)
        t8, t4 = c("groups", "ocho"), c("groups", "cuatro")
        t_res, t_baj = L("result").start, c("result", "bajó")
        t_3, t_int, t_nor = c("twist", "tercer"), c("twist", "intervalos"), c("twist2", "normal")
        cols = [(55, "8 H", t8, "calm"), (135, "4 H", t4, "tired"), (215, "4 H + HIIT", t_3, "tired")]
        # columns of protein blocks (myofibrillar protein synthesis)
        rates = [1.53, 1.24, 1.61]
        build = prog(g, t_res, 2.4)
        for i, (x, name, tt, mood) in enumerate(cols):
            s = pop_scale(g, tt, 0.3)
            if s <= 0:
                continue
            if i == 2 and g > t_int - 0.3:
                rider = cast.hero({"arm_l": (60, 40), "arm_r": (60, 40), "mouth": "grit", "sweat": True,
                                   "walk": g * 16}).crop((4, 0, 52, 60))
                paste_scaled(img, cast.stationary_bike(g * (3 if g > t_int else 1), rider), x, 160, s, anchor="center")
            else:
                paste_scaled(img, cast.bed(cast.sleeping_head(mood), t=g + i), x, 150, s * 0.85, anchor="center")
            label(img, name, x, 196, color=P["gold"] if i == 2 else P["white"])
            if g > t_res - 0.2:
                hmax = 90
                prog_i = build if i < 2 else prog(g, t_int, 2.0)
                n = int(prog_i * hmax * rates[i] / 1.61 / 9)
                for b in range(n):
                    blk = cast.protein_block(P["muscle_l"] if not (i == 1 and g > t_baj) else P["muscle_d"])
                    img.alpha_composite(blk, (int(x - 5), int(318 - b * 9)))
        if g > t_res - 0.2:
            label(img, "SÍNTESIS DE PROTEÍNA", 135, 216, color=P["muscle_l"])
            d.line([20, 328, 250, 328], fill=P["fog"])
        if g > t_baj and g < t_3:
            arrow(img, 135, 230, up=False, color=P["red"], size=6)
        if g > t_nor:
            paste_scaled(img, text_sprite("=", P["green"], scale=3), 175, 250, pop_scale(g, t_nor))
            paste_scaled(img, text_sprite("NORMAL", P["green"], scale=2), 215, 232, pop_scale(g, t_nor + 0.1))
        z = 1.0
        if L("twist").start - 0.3 < g < t_nor + 0.6:
            z = lerp(1.0, 1.12, ease_io(prog(g, t_int - 0.6, 0.6)))
        return gfx.camera(img, z, 175 if z > 1 else 135, 240)

    # 8. CAVEAT
    def s_caveat(g):
        img = cast.lab_bg(g)
        t_peq = c("caveat", "pequeño")
        s = pop_scale(g, L("caveat").start, 0.3)
        paste_scaled(img, badge("ESTUDIO PEQUEÑO: 24 PERSONAS"), 135, 120, s * 1.5)
        d = ImageDraw.Draw(img)
        # evidence scale: tiny pile vs big empty pan
        tilt = math.sin(g * 2) * 2
        d.line([80, 230 + tilt, 190, 230 - tilt], fill=P["steel_l"], width=3)
        d.rectangle([132, 230, 138, 300], fill=P["steel"])
        d.rectangle([110, 300, 160, 306], fill=P["steel_d"])
        paste(img, cast.doc_stack(1), 80, 230 + tilt, scale=1)
        label(img, "?", 190, 196 - tilt, color=P["gold"], scale=2)
        if g > t_peq:
            label(img, "FALTA MÁS EVIDENCIA", 135, 320, color=P["fog"])
        return img

    # 9. RESOLVE: peaceful sleep -> sunrise, stamp
    def s_resolve(g):
        st = L("resolve").start
        dawn = ease_io(prog(g, st, 3.0))
        img = cast.bedroom_bg(g, dawn=dawn)
        paste(img, cast.bed(cast.sleeping_head("calm"), blanket=P["green_d"], t=g), 135, 330, scale=2)
        if dawn < 0.8:
            zzz(img, 150, 240, g)
        paste(img, cast.digital_clock("8 H", P["green"]), 40, 270, scale=1, anchor="mid_bottom")
        out = gfx.camera(img, 1.0)
        stamp_slam(out, VERDICT, g, c("resolve", "entrenamiento"), y=110)
        return out

    def s_cta(g):
        img = cast.end_bg(g)
        end_card(img, g, L("cta").start, c("cta", "anoche"), VERDICT)
        return img

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("q", "q", s_q, "iris", 0.4, 0.25),
        ("study", "study", s_study, "whip_left", 0.3, 0.2),
        ("beds", "groups", s_beds, "dither", 0.3, 0.2),
        ("caveat", "caveat", s_caveat, "pixelate", 0.3, 0.2),
        ("resolve", "resolve", s_resolve, "dither", 0.35, 0.25),
        ("cta", "cta", s_cta, "pixelate", 0.3, 0.15),
    ])
    emph = {norm(w): col for w, col in [("cuatro", P["red_l"]), ("ocho", P["green"]), ("bajó", P["red_l"]),
            ("intervalos", P["gold"]), ("normal", P["green"]), ("pequeño", P["lav"]), ("dormir", P["sky"]),
            ("proteína", P["muscle_l"])]}
    return Director(tl, scenes, SubStyle(y=352, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.3))
