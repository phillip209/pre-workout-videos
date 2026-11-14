"""B03 · "Café a las 4 PM: lo más raro es que no notó nada" — story format (template b01v2).

Fact (checked 2026-11-14): Drake C, Roehrs T, Shambroom J, Roth T. J Clin Sleep Med 2013;9(11):1195-1200.
12 healthy normal sleepers; 400 mg caffeine 0, 3 or 6 h before habitual bedtime vs placebo. Even at 6 h
before bed, objectively measured total sleep time fell by more than 1 h; participants did not report the
disturbance. Authors recommend avoiding substantial caffeine at least 6 h before bed.
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast, organs, hud
from engine import cast_plus as cp, cast_villains as cv, story as st
from engine.gfx import P, prog, ease_out, ease_io, ease_back, lerp, paste
from engine.kit import label, pop_scale, paste_scaled, count_text, scenes_from, impact_text, blinking
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "b03_cafe"
BPM = 116
LEAD_IN = 0.08
TAIL = 1.4
NARRATION_FILE = "episodes/b03_cafe/narration.mp3"

LINES = [
    {"id": "hook", "text": "Leo se tomó un café fuerte a las cuatro de la tarde."},
    {"id": "hook2", "text": "Y lo más raro... es que él no notó nada."},
    {"id": "hook3", "text": "Pero su sueño, sí.", "hold": 0.1},
    {"id": "ctx", "text": "Cuatro de la tarde. Una dosis alta: como cuatro tazas."},
    {"id": "night", "text": "Diez de la noche: se acuesta. Y el monstruo de la cafeína... sigue despierto."},
    {"id": "turn", "text": "Por dentro, la cafeína bloquea la señal que le dice al cerebro que ya es hora de dormir."},
    {"id": "data", "text": "En un estudio, tomarla seis horas antes de acostarse le quitó a la gente más de una hora de sueño."},
    {"id": "still", "text": "Y el monstruo... seguía de fiesta."},
    {"id": "setup", "text": "A la mañana siguiente, Leo se levanta y dice..."},
    {"id": "reveal", "text": "dormí perfecto."},
    {"id": "reveal2", "text": "¡Pero las mediciones decían otra cosa!", "hold": 0.1},
    {"id": "twist", "text": "En el estudio, la gente tampoco se dio cuenta. Por eso, los autores recomiendan cortar la cafeína fuerte seis horas antes de dormir."},
    {"id": "cta", "text": "¿A qué hora te tomas tu último café?"},
]

TITLE = "Café a las 4 de la tarde: lo más raro es que no notó nada ☕ #Shorts"
DESCRIPTION = (
    "Leo se tomó un café fuerte a las 4 de la tarde. Él no notó nada… pero su sueño sí.\n\n"
    "Fuente: Drake et al., J Clin Sleep Med, 2013 — 12 adultos sanos; 400 mg de cafeína (una dosis alta, "
    "aprox. 4 tazas de café filtrado) 0, 3 o 6 horas antes de dormir frente a placebo. Incluso 6 horas antes, "
    "el sueño medido bajó más de 1 hora, y los participantes no lo notaron. Los autores recomiendan evitar "
    "cafeína fuerte al menos 6 horas antes de acostarse.\nEstudio pequeño; los resultados pueden variar entre "
    "personas. Contenido educativo, no es consejo médico.\nVoz: ElevenLabs.\n\n"
    "#cafe #cafeina #sueño #quelepasaatucuerpo #Shorts")
TAGS = ["café y sueño", "cafeína", "dormir mejor", "café en la tarde", "qué le pasa a tu cuerpo", "salud"]


def sound_cues(tl):
    c, L = tl.cue, tl.line
    return [(0.0, "impact", 0.9), (0.0, "whoosh", 0.6),
            (c("hook", "café"), "pop", 0.6), (c("hook", "cuatro"), "ding", 0.6),
            (c("hook2", "nada"), "blip", 0.6),
            (c("hook3", "sueño") - 0.05, "glitch", 0.7), (c("hook3", "sueño"), "impact", 0.8),
            (L("ctx").start - 0.25, "rewind", 0.9),
            (c("ctx", "dosis"), "clank", 0.5), (c("ctx", "tazas"), "pop", 0.6), (c("ctx", "tazas") + 0.12, "pop", 0.6),
            (c("ctx", "tazas") + 0.24, "pop", 0.6), (c("ctx", "tazas") + 0.36, "pop", 0.6),
            (c("night", "diez"), "tick", 0.5), (c("night", "acuesta"), "thud", 0.5),
            (c("night", "monstruo") - 0.1, "growl", 0.8), (c("night", "monstruo"), "glitch", 0.6),
            (c("night", "despierto"), "alarm", 0.5),
            (L("turn").start, "scan", 0.9), (c("turn", "bloquea"), "clank", 0.8), (c("turn", "dormir"), "blip", 0.5),
            (c("data", "seis"), "ding", 0.6), (c("data", "hora", 2), "bar_down", 0.9), (c("data", "sueño"), "deflate", 0.6),
            (c("still", "monstruo"), "growl", 0.5), (c("still", "fiesta"), "boing", 0.7),
            (c("setup", "mañana"), "ding", 0.6), (c("setup", "dice"), "whoosh", 0.4),
            (c("reveal", "perfecto"), "sparkle", 0.6),
            (c("reveal2", "mediciones") - 0.04, "impact", 1.0), (c("reveal2", "otra"), "bar_down", 0.8),
            (c("twist", "tampoco"), "alarm", 0.4), (c("twist", "seis"), "stamp", 0.7),
            (L("cta").start - 0.1, "pop", 0.6), (c("cta", "café"), "ding", 0.7)]


def music_sections(tl):
    c, L = tl.cue, tl.line
    t_hit = c("reveal2", "mediciones")
    return [(0.0, L("ctx").start - 0.25, "pulse"), (L("ctx").start, L("night").start, "drive"),
            (L("night").start, L("turn").start - 0.1, "low"), (L("turn").start, L("still").start, "drive"),
            (L("still").start, L("setup").start, "groove"), (L("setup").start, t_hit - 0.6, "mystery"),
            (t_hit - 0.6, t_hit, "silence"), (t_hit, L("twist").start, "tense"),
            (L("twist").start, tl.total, "pulse")]


def make_director(tl):
    c, L = tl.cue, tl.line
    T = {"ctx": L("ctx").start, "night": c("night", "diez"), "turn": L("turn").start, "still": L("still").start,
         "setup": c("setup", "mañana"), "cta": L("cta").start}

    def clock(g):
        if g < T["night"] or g > T["cta"]:
            return "16:00"
        if g < T["turn"]:
            return "22:00"
        if g < T["still"]:
            return "23:00"
        if g < T["setup"]:
            return "02:00"
        return "07:00"

    def clock_val(g):
        return {"16:00": 16, "22:00": 22, "23:00": 23, "02:00": 26, "07:00": 31}[clock(g)]

    hudl = st.Hud([(0, 16), (T["night"], 22, 0.4), (T["turn"], 23, 0.3), (T["still"], 26, 0.4), (T["setup"], 31, 0.4),
                   (T["cta"], 16, 0.3)], 31, flashes=[0.2, T["night"], T["setup"], T["cta"]],
                  text_fn=lambda g: "⏰ " + clock(g) if False else clock(g))

    def office(g):
        return cv.office_bg(g, 0.0, None)   # the HUD already shows the time

    def night_room(g):
        return gfx.darken(cast.bedroom_bg(g, dawn=0.0), 0.25)

    s_hook = st.hook_closeup(
        office, hudl,
        beats=[(0, "neutral", 0), (c("hook2", "nada"), "happy", 0), (c("hook3", "sueño") - 0.1, "shock", 0)],
        texts=[(c("hook", "cuatro"), c("hook2", "nada") - 0.2, "CAFÉ A LAS 4 PM", P["fat_l"], 3, 98),
               (c("hook2", "nada") - 0.1, c("hook3", "sueño") - 0.1, "¿NO NOTÓ NADA?", P["white"], 3, 98),
               (c("hook3", "sueño"), None, "¿SU SUEÑO?", P["sky"], 5, 100)],
        t_punch=c("hook3", "sueño"),
        side=(c("hook", "café"), L("hook2").start, lambda g: cv.coffee_cup(g), 999))

    tz = c("ctx", "tazas")
    s_ctx = st.context_walk(
        lambda g, s: office(g), hudl, T["ctx"], T["ctx"], rewind=True, walk_px=0,
        items=[(tz, cv.coffee_cup(0), 45, None), (tz + 0.12, cv.coffee_cup(0), 105, None),
               (tz + 0.24, cv.coffee_cup(0), 165, None), (tz + 0.36, cv.coffee_cup(0), 225, None)],
        texts=[(c("ctx", "dosis"), tz - 0.1, "DOSIS ALTA", P["orange"], 3, 175),
               (tz, None, "≈ 4 TAZAS · 400 MG", P["white"], 2, 175)])

    s_night = st.villain_rise(
        night_room, hudl, "cafeina", c("night", "monstruo"), c("night", "despierto") + 0.6,
        leo_pose=lambda g, sc: {"mouth": "flat" if not sc else "o", "eyes": "wide" if sc else "open",
                                "arm_l": (5, 5), "arm_r": (5, 5)},
        texts=[(c("night", "acuesta"), c("night", "monstruo") - 0.1, "A LA CAMA", P["sky"], 4, 112),
               (c("night", "monstruo"), c("night", "despierto") - 0.1, "LA CAFEÍNA", P["fat_l"], 4, 112),
               (c("night", "despierto"), None, "SIGUE DESPIERTA", P["red_l"], 3, 112)])

    def brain_block(g):
        img = cast.tissue_bg(g, hue="pink")
        paste(img, organs.brain("sad" if g > c("turn", "bloquea") else "happy", g), 135, 205, scale=2.4, anchor="center")
        # "sleep signal" Zz's flying toward the brain, bounced by caffeine beans
        blocked = g > c("turn", "bloquea")
        for i in range(5):
            ph = (g * 0.9 + i * 0.2) % 1
            x = lerp(30, 120 if not blocked else 95, ph)
            y = 150 + i * 22
            if blocked and ph > 0.9:
                continue
            label(img, "Z", x, y, color=P["lav"], scale=2)
        if blocked:
            for i in range(3):
                paste(img, cv.villain("cafeina", "jitter", g, size=0.35), 92, 160 + i * 34, anchor="center")
        return img

    s_turn = st.xray_turn(lambda g: night_room(g), hudl, T["turn"], brain_block,
                          texts=[(c("turn", "bloquea"), c("turn", "dormir") - 0.1, "BLOQUEADA", P["red_l"], 4, 108),
                                 (c("turn", "dormir"), None, "SEÑAL DE SUEÑO", P["lav"], 3, 108)],
                          leo_pose={"mouth": "o", "eyes": "wide"})

    t_hr = c("data", "hora", 2)

    def draw_data(img, g):
        paste(img, organs.brain("sad", g), 135, 230, scale=2.0, anchor="center")
        hud.stat_bar(img, 70, 290, 130, "SUEÑO", lerp(0.95, 0.8, ease_out(prog(g, t_hr, 0.6))), P["lav"], g,
                     delta=-1 if g > t_hr else 0, appear=prog(g, L("data").start, 0.3))
        if g > c("data", "seis"):
            label(img, "6 H ANTES DE DORMIR", 135, 160, color=P["fat_l"], scale=1)

    s_data = st.inner_metric(lambda g: cast.tissue_bg(g, hue="pink"), hudl, draw_data,
                             texts=[(t_hr - 0.1, None, "-1 H DE SUEÑO", P["red_l"], 4, 112)],
                             src="DRAKE 2013 · 400 MG · 6 H ANTES")

    def s_still(g):
        img = night_room(g)
        d = ImageDraw.Draw(img)
        for i in range(6):   # disco lights
            a = g * 3 + i
            col = [P["pink"], P["sky"], P["gold"], P["green"]][i % 4]
            d.line([135, 0, 135 + math.cos(a) * 200, 300 + math.sin(a) * 60], fill=gfx.lerpc(col, P["night"], 0.4), width=3)
        paste(img, st.leo({"mouth": "flat", "eyes": "wide", "droop": 0.3}, g), 70, 336, scale=2.3)
        dance = math.sin(g * 9)
        paste(img, cv.villain("cafeina", "jitter", g), 190 + dance * 12, 230 - abs(dance) * 18, scale=1.6, anchor="center")
        impact_text(img, "DE FIESTA", 135, 112, g, c("still", "fiesta"), color=P["pink"], scale=4)
        hudl(img, g)
        return img

    s_setup = st.slowmo(
        lambda g: cast.bedroom_bg(g, dawn=1.0), hudl, T["setup"],
        lambda k: {"mouth": "grin", "eyes": "happy", "arm_l": (lerp(10, 170, k), 20), "arm_r": (lerp(10, 170, k), 20)},
        texts=[(c("setup", "dice"), None, "07:00", P["gold"], 4, 100)], zoom_to=(135, 200), zoom=0.45)

    t_hit = c("reveal2", "mediciones")
    s_reveal = st.reveal_closeup(
        lambda g: cast.bedroom_bg(g, dawn=1.0), hudl, t_hit, ("SUEÑO REAL", 0.92, 0.62, t_hit),
        texts=[(c("reveal", "perfecto") - 0.2, t_hit - 0.15, "DORMÍ PERFECTO", P["white"], 3, 104),
               (t_hit, None, "-1 H", P["red_l"], 7, 104),
               (c("reveal2", "otra"), None, "SEGÚN LAS MÁQUINAS", P["white"], 2, 160)],
        mood_pre="happy", mood_hit="shock", src="DRAKE 2013 · SUEÑO MEDIDO")

    s_end = st.twist_loop(
        office, hudl, "cafeina", c("twist", "tampoco"), c("twist", "seis"), T["cta"],
        cta_lines=(("¿A QUÉ HORA", P["white"]), ("TU ÚLTIMO CAFÉ?", P["fat_l"])),
        ojo_text="NI LO NOTARON", src="DRAKE 2013", villain_mood="jitter",
        extra_texts=[(c("twist", "seis"), T["cta"] - 0.15, "CORTA 6 H ANTES", P["green"], 3, 150)])

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("ctx", "ctx", s_ctx, "cut", 0.2, 0.3),
        ("night", "night", s_night, "pixelate", 0.3, 0.2),
        ("turn", "turn", s_turn, "cut", 0.2, 0.15),
        ("data", "data", s_data, "dither", 0.25, 0.2),
        ("still", "still", s_still, "whip_left", 0.25, 0.15),
        ("setup", "setup", s_setup, "iris", 0.35, 0.2),
        ("reveal", "reveal", s_reveal, "cut", 0.15, 0.1),
        ("end", "twist", s_end, "pixelate", 0.25, 0.1),
    ])
    emph = {norm(w): col for w, col in [("café", P["fat_l"]), ("cuatro", P["gold"]), ("nada", P["white"]),
            ("sueño", P["sky"]), ("tazas", P["fat_l"]), ("monstruo", P["fat_l"]), ("despierto", P["red_l"]),
            ("bloquea", P["red_l"]), ("dormir", P["lav"]), ("seis", P["gold"]), ("hora", P["red_l"]),
            ("fiesta", P["pink"]), ("perfecto", P["green"]), ("mediciones", P["red_l"]), ("tampoco", P["red_l"]),
            ("último", P["gold"])]}
    return Director(tl, scenes, SubStyle(y=356, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.25))
