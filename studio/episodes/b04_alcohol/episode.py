"""B04 · "Un mes sin alcohol: lo más raro fue su análisis de sangre" — story format (template b01v2).

Fact (checked 2026-11-14): Mehta G et al. BMJ Open 2018;8:e020673. Moderate-heavy drinkers who chose to
abstain for 1 month (n=94) vs who kept drinking (n=47). Abstainers: insulin resistance (HOMA) -25.9 %,
systolic BP -6.6 %, weight -1.5 %; no significant changes in the drinking group. Not randomised.
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast, organs
from engine import cast_plus as cp, cast_villains as cv, story as st
from engine.gfx import P, prog, ease_out, ease_io, lerp, paste
from engine.kit import label, count_text, scenes_from
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "b04_alcohol"
BPM = 110
LEAD_IN = 0.08
TAIL = 1.5
NARRATION_FILE = "episodes/b04_alcohol/narration.mp3"

LINES = [
    {"id": "hook", "text": "Leo dejó el alcohol un mes."},
    {"id": "hook2", "text": "Y lo más raro... no fue despertar sin resaca."},
    {"id": "hook3", "text": "Fue su análisis de sangre.", "hold": 0.1},
    {"id": "w1", "text": "Semana uno. Cero cervezas, cero copas."},
    {"id": "fri", "text": "Viernes: llega el monstruo. Amigos, música y la pregunta de siempre: ¿solo una?"},
    {"id": "turn", "text": "Pero por dentro, algo cambiaba."},
    {"id": "data", "text": "En un estudio con bebedores habituales, un mes sin alcohol bajó la presión casi un siete por ciento."},
    {"id": "still", "text": "Y el monstruo... seguía invitando."},
    {"id": "setup", "text": "Día treinta. Llegan los resultados..."},
    {"id": "reveal", "text": "Resistencia a la insulina: un veintiséis por ciento menos.", "hold": 0.15},
    {"id": "twist", "text": "Ojo: quienes siguieron bebiendo no cambiaron."},
    {"id": "cta", "text": "¿Tú aguantarías un mes?"},
]

TITLE = "Un mes sin alcohol: lo más raro fue su análisis de sangre 🍺 #Shorts"
DESCRIPTION = (
    "Leo dejó el alcohol un mes. Lo más raro no fue despertar sin resaca: fue su análisis de sangre.\n\n"
    "Fuente: Mehta et al., BMJ Open, 2018 — bebedores habituales (moderados a altos) que eligieron dejar el "
    "alcohol 1 mes (94) frente a quienes siguieron bebiendo (47). En quienes lo dejaron, la resistencia a la "
    "insulina bajó 25,9 %, la presión sistólica 6,6 % y el peso 1,5 %; en quienes siguieron bebiendo no hubo "
    "cambios significativos. No fue un ensayo aleatorizado.\nLos resultados pueden variar entre personas. "
    "Contenido educativo, no es consejo médico.\nVoz: ElevenLabs.\n\n"
    "#alcohol #mesSinAlcohol #salud #quelepasaatucuerpo #Shorts")
TAGS = ["dejar el alcohol", "un mes sin alcohol", "resistencia a la insulina", "presión arterial",
        "qué le pasa a tu cuerpo", "salud"]


def sound_cues(tl):
    c, L = tl.cue, tl.line
    return [(0.0, "impact", 0.9), (0.0, "whoosh", 0.6),
            (c("hook", "alcohol"), "pop", 0.6), (c("hook", "mes"), "ding", 0.6),
            (c("hook2", "resaca"), "blip", 0.6),
            (c("hook3", "sangre") - 0.05, "glitch", 0.7), (c("hook3", "sangre"), "impact", 0.8),
            (L("w1").start - 0.25, "rewind", 0.9), (c("w1", "cervezas"), "thud", 0.6), (c("w1", "copas"), "thud", 0.6),
            (c("w1", "copas") + 0.4, "ding", 0.6),
            (c("fri", "viernes"), "tick", 0.5), (c("fri", "monstruo") - 0.1, "growl", 0.9), (c("fri", "monstruo"), "impact", 0.7),
            (c("fri", "amigos"), "pop", 0.5), (c("fri", "música"), "boing", 0.4), (c("fri", "una"), "alarm", 0.4),
            (L("turn").start, "scan", 0.9),
            (c("data", "presión"), "heartbeat", 0.8), (c("data", "siete"), "bar_down", 0.8),
            (c("still", "monstruo"), "growl", 0.5), (c("still", "invitando"), "glitch", 0.5),
            (c("setup", "treinta"), "ding", 0.8), (c("setup", "resultados"), "whoosh", 0.4),
            (c("reveal", "veintiséis") - 0.04, "impact", 1.0), (c("reveal", "veintiséis"), "sparkle", 0.7),
            (c("reveal", "menos"), "bar_down", 0.7),
            (c("twist", "ojo"), "alarm", 0.4), (c("twist", "cambiaron"), "thud", 0.6),
            (L("cta").start - 0.1, "pop", 0.6), (c("cta", "mes"), "ding", 0.7)]


def music_sections(tl):
    c, L = tl.cue, tl.line
    t_hit = c("reveal", "veintiséis")
    return [(0.0, L("w1").start - 0.25, "pulse"), (L("w1").start, L("fri").start, "drive"),
            (L("fri").start, L("turn").start - 0.1, "groove"), (L("turn").start, L("still").start, "drive"),
            (L("still").start, L("setup").start, "pulse"), (L("setup").start, t_hit - 0.6, "mystery"),
            (t_hit - 0.6, t_hit, "silence"), (t_hit, L("twist").start, "triumph"),
            (L("twist").start, tl.total, "pulse")]


def make_director(tl):
    c, L = tl.cue, tl.line
    t_w1, t_fri, t_turn = L("w1").start, c("fri", "viernes"), L("turn").start
    t_still, t_30 = c("still", "invitando"), c("setup", "treinta")
    hudl = st.Hud([(0, 30), (t_w1 - 0.3, 30), (t_w1 + 0.35, 1, 0.6), (t_fri, 5, 0.35), (t_turn + 0.2, 12, 0.4),
                   (t_30, 30, max(0.5, t_30 - t_still))], 30, flashes=[0.2, t_w1 + 0.35, t_fri, t_30])

    def bar(g):
        return cv.bar_bg(g)

    s_hook = st.hook_closeup(
        bar, hudl,
        beats=[(0, "neutral", 0), (c("hook2", "resaca"), "happy", 0), (c("hook3", "sangre") - 0.1, "shock", 0)],
        texts=[(c("hook", "mes"), c("hook2", "resaca") - 0.2, "1 MES SIN ALCOHOL", P["gold"], 3, 98),
               (c("hook2", "resaca") - 0.1, c("hook3", "sangre") - 0.1, "¿SIN RESACA?", P["white"], 3, 98),
               (c("hook3", "sangre"), None, "¿SU SANGRE?", P["red_l"], 5, 100)],
        t_punch=c("hook3", "sangre"),
        side=(c("hook", "alcohol"), L("hook2").start, lambda g: cv.beer(g), c("hook", "mes")))

    s_w1 = st.context_walk(
        lambda g, s: bar(g), hudl, t_w1, t_w1, rewind=True, walk_px=0,
        items=[(c("w1", "cervezas"), cv.beer(0), 60, False), (c("w1", "copas"), cv.beer(0), 135, False),
               (c("w1", "copas") + 0.4, cv.water_glass(0.8), 210, True)],
        texts=[(c("w1", "cervezas"), None, "CERO ALCOHOL", P["white"], 3, 175)])

    s_fri = st.villain_rise(
        bar, hudl, "cerveza", c("fri", "monstruo"), c("fri", "amigos"),
        leo_pose=lambda g, sc: {"mouth": "grit" if sc else "smile", "eyes": "open", "arm_l": (5, 5),
                                "arm_r": (40, 60) if sc else (5, 5)},
        popups=[(c("fri", "amigos"), lambda g: cast.tiny_person(P["pink"]), 30, 300, 2.5),
                (c("fri", "amigos") + 0.15, lambda g: cast.tiny_person(P["sky"]), 250, 300, 2.5)],
        texts=[(c("fri", "viernes"), c("fri", "monstruo") - 0.1, "VIERNES", P["lav"], 4, 112),
               (c("fri", "monstruo"), c("fri", "pregunta") - 0.1, "LA TENTACIÓN", P["gold"], 3, 112),
               (c("fri", "una"), None, "¿SOLO UNA?", P["gold"], 4, 112)], dark=0.1)

    def heart_bg(g):
        return cast.tissue_bg(g, hue="pink")

    def heart_inner(g):
        img = heart_bg(g)
        paste(img, cv.heart("sad", g, bpm=90), 135, 215, scale=2.4, anchor="center")
        label(img, "SU CORAZÓN", 135, 285, color=P["white"], scale=2)
        return img

    s_turn = st.xray_turn(bar, hudl, t_turn, heart_inner,
                          texts=[(c("turn", "cambiaba"), None, "¿QUÉ CAMBIA?", P["gold"], 4, 108)],
                          leo_pose={"mouth": "flat"})

    t_pr, t_7 = c("data", "presión"), c("data", "siete")

    def draw_data(img, g):
        k = ease_io(prog(g, t_7 - 0.2, 0.8))
        paste(img, cv.heart("happy" if k > 0.5 else "sad", g, bpm=lerp(90, 66, k)), 90, 225, scale=2.0, anchor="center")
        paste(img, cp.gauge(lerp(0.78, 0.6, k), g, "PRESIÓN"), 200, 230, scale=1.1, anchor="center")
        if g > t_pr:
            label(img, "PRESIÓN ARTERIAL", 135, 290, color=P["white"])

    s_data = st.inner_metric(heart_bg, hudl, draw_data,
                             texts=[(t_7 - 0.1, None, "≈ -7 %", P["green"], 6, 112)],
                             src="MEHTA 2018 · 94 BEBEDORES · 1 MES")

    def street(g, s):
        from engine.kit import street_bg
        return street_bg(g, scroll=s, tod="night")

    s_still = st.lurk(street, hudl, "cerveza", L("still").start, c("still", "monstruo"),
                      texts=[(t_still, None, "SEGUÍA INVITANDO", P["gold"], 3, 108)], page_base=12)

    def lab(g):
        return cast.lab_bg(g)

    s_setup = st.slowmo(
        lab, hudl, L("setup").start, lambda k: {"mouth": "o" if k > 0.6 else "flat", "arm_r": (lerp(20, 110, k), 40)},
        props=[(lambda g, k: cast.doc_stack(3), lambda k: lerp(60, 190, k), lambda k: lerp(300, 250, k), 1.6)],
        texts=[(c("setup", "resultados"), None, "RESULTADOS", P["sky"], 4, 104)], zoom_to=(140, 215))

    t_hit = c("reveal", "veintiséis")
    s_reveal = st.reveal_closeup(
        lab, hudl, t_hit, ("INSULINA", 0.78, 0.5, t_hit),
        texts=[(L("reveal").start, t_hit - 0.15, "RESISTENCIA A LA INSULINA", P["white"], 2, 104),
               (t_hit - 0.05, None, "-26 %", P["green"], 7, 104),
               (c("reveal", "menos") + 0.1, None, "MANEJA MEJOR EL AZÚCAR", P["white"], 2, 160)],
        mood_pre="neutral", mood_hit="happy",
        src="MEHTA 2018 · RESISTENCIA A LA INSULINA")

    s_end = st.twist_loop(
        bar, hudl, "cerveza", c("twist", "ojo"), c("twist", "cambiaron"), L("cta").start,
        cta_lines=(("¿AGUANTARÍAS", P["white"]), ("UN MES?", P["gold"])), src="MEHTA 2018 · GRUPO QUE SIGUIÓ BEBIENDO",
        extra_texts=[(c("twist", "cambiaron"), L("cta").start - 0.15, "SIN CAMBIOS", P["red_l"], 3, 150)])

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("w1", "w1", s_w1, "cut", 0.2, 0.3),
        ("fri", "fri", s_fri, "pixelate", 0.3, 0.2),
        ("turn", "turn", s_turn, "cut", 0.2, 0.15),
        ("data", "data", s_data, "dither", 0.25, 0.2),
        ("still", "still", s_still, "whip_left", 0.25, 0.15),
        ("setup", "setup", s_setup, "iris", 0.35, 0.2),
        ("reveal", "reveal", s_reveal, "cut", 0.15, 0.1),
        ("end", "twist", s_end, "pixelate", 0.25, 0.1),
    ])
    emph = {norm(w): col for w, col in [("alcohol", P["gold"]), ("mes", P["gold"]), ("raro", P["gold"]),
            ("resaca", P["white"]), ("sangre", P["red_l"]), ("cervezas", P["gold"]), ("copas", P["gold"]),
            ("monstruo", P["gold"]), ("una", P["gold"]), ("presión", P["sky"]), ("siete", P["green"]),
            ("invitando", P["gold"]), ("treinta", P["gold"]), ("insulina", P["sky"]), ("veintiséis", P["green"]),
            ("cambiaron", P["red_l"])]}
    return Director(tl, scenes, SubStyle(y=356, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.25))
