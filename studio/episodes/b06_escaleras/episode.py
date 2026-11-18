"""B06 · "3 pisos de escaleras, 3 veces al día" — story format, EXP-001 test (outcome-first hook).

Fact (checked 2026-11-14): Jenkins EM et al., Appl Physiol Nutr Metab 2019 (doi 10.1139/apnm-2018-0675):
sedentary young adults (n = 12 per group) climbed a 3-flight stairwell (60 steps) vigorously, 3 times a day
(1-4 h apart), 3 days a week for 6 weeks vs non-training controls. VO2peak was higher after training
(P = 0.003); the authors call the absolute increase modest. Small study.
"""
from __future__ import annotations

import math

from engine import W, H, gfx, fx, cast, organs
from engine import cast_plus as cp, cast_villains as cv, story as st
from engine.gfx import P, prog, ease_out, ease_io, ease_back, lerp, paste
from engine.kit import label, scenes_from, impact_text, text_sprite
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "b06_escaleras"
EXPERIMENT = {"id": "EXP-001", "arm": "test", "hook_type": "outcome_first"}
BPM = 116
LEAD_IN = 0.08
TAIL = 1.4
NARRATION_FILE = "episodes/b06_escaleras/narration.mp3"

LINES = [
    {"id": "hook", "text": "Tres pisos de escaleras, tres veces al día... y en seis semanas su condición física mejoró."},
    {"id": "hook2", "text": "Sin gimnasio.", "hold": 0.1},
    {"id": "ctx", "text": "Semana uno. Leo trabaja en un tercer piso. Siempre en ascensor."},
    {"id": "mon", "text": "Y cada mañana, el monstruo lo espera con la puerta abierta."},
    {"id": "turn", "text": "Pero esta vez, Leo subió a pie. Sesenta escalones, rápido."},
    {"id": "data", "text": "En un estudio, jóvenes sedentarios hicieron eso tres veces al día, tres días por semana."},
    {"id": "still", "text": "Y el monstruo... seguía esperándolo."},
    {"id": "setup", "text": "Seis semanas después, los midieron en una prueba de esfuerzo..."},
    {"id": "reveal", "text": "y su capacidad aeróbica había subido. ¡Con apenas unos minutos al día!", "hold": 0.1},
    {"id": "twist", "text": "Ojo: la mejora fue modesta y el estudio, pequeño."},
    {"id": "cta", "text": "¿Escaleras o ascensor? ¿Qué usas tú?"},
]

TITLE = "3 pisos de escaleras, 3 veces al día: esto le pasó en 6 semanas 🪜 #Shorts"
DESCRIPTION = (
    "Leo subió 3 pisos de escaleras 3 veces al día y en 6 semanas su capacidad aeróbica mejoró. Sin gimnasio.\n\n"
    "Fuente: Jenkins et al., Applied Physiology, Nutrition, and Metabolism, 2019 — jóvenes sedentarios (12 por "
    "grupo) subieron 3 pisos (60 escalones) a ritmo vigoroso, 3 veces al día, 3 días por semana durante 6 "
    "semanas, frente a un grupo que no entrenó. Su VO2 pico fue mayor después del entrenamiento; los autores "
    "describen la mejora como modesta. Estudio pequeño.\nContenido educativo, no es consejo médico.\n"
    "Voz: ElevenLabs.\n\n#ejercicio #cardio #salud #habitossaludables #fitness")
TAGS = ["subir escaleras", "escaleras ejercicio", "condición física", "snacks de ejercicio", "qué le pasa a tu cuerpo"]


def sound_cues(tl):
    c, L = tl.cue, tl.line
    return [(0.0, "impact", 0.9), (0.0, "sparkle", 0.6),
            (c("hook", "pisos"), "step", 0.7), (c("hook", "escaleras"), "step", 0.7), (c("hook", "veces"), "step", 0.7),
            (c("hook", "mejoró"), "bar_up", 0.9), (c("hook2", "gimnasio"), "ding", 0.7),
            (L("ctx").start - 0.25, "rewind", 0.9), (c("ctx", "ascensor"), "ding", 0.5),
            (c("mon", "monstruo") - 0.1, "growl", 0.8), (c("mon", "puerta"), "whoosh", 0.6),
            (c("turn", "pie"), "whoosh", 0.5), (c("turn", "sesenta"), "step", 0.7), (c("turn", "rápido"), "step", 0.8),
            (c("data", "estudio"), "ding", 0.6), (c("data", "veces"), "pop", 0.5), (c("data", "semana"), "pop", 0.5),
            (c("still", "monstruo"), "growl", 0.5), (c("still", "esperándolo"), "ding", 0.4),
            (c("setup", "semanas"), "ding", 0.7), (c("setup", "esfuerzo"), "heartbeat", 0.8),
            (c("reveal", "aeróbica") - 0.04, "impact", 1.0), (c("reveal", "subido"), "bar_up", 0.8),
            (c("reveal", "minutos"), "sparkle", 0.6),
            (c("twist", "ojo"), "alarm", 0.4), (c("twist", "pequeño"), "thud", 0.5),
            (L("cta").start - 0.1, "pop", 0.6), (c("cta", "tú"), "ding", 0.7)]


def music_sections(tl):
    c, L = tl.cue, tl.line
    t_hit = c("reveal", "aeróbica")
    return [(0.0, L("ctx").start - 0.25, "drive"), (L("ctx").start, L("mon").start, "groove"),
            (L("mon").start, L("turn").start - 0.1, "low"), (L("turn").start, L("still").start, "drive"),
            (L("still").start, L("setup").start, "pulse"), (L("setup").start, t_hit - 0.6, "mystery"),
            (t_hit - 0.6, t_hit, "silence"), (t_hit, L("twist").start, "triumph"),
            (L("twist").start, tl.total, "pulse")]


def make_director(tl):
    c, L = tl.cue, tl.line
    t_w1, t_6 = L("ctx").start, c("setup", "semanas")
    hudl = st.Hud([(0, 6), (t_w1 - 0.3, 6), (t_w1 + 0.35, 1, 0.6), (L("still").start + 0.3, 3, 0.4),
                   (t_6, 6, 0.6)], 6, fmt="SEMANA {n}", flashes=[0.15, t_w1 + 0.35, t_6])

    def office(g):
        return cv.office_bg(g, 0.0, None)

    def stairs(g):   # hook/loop background: no floor sign so frame 1 == last frame
        return cv.stairs_bg(g, climb=(g * 40) % 140, sign=False)

    # 1. HOOK — outcome first: fitness gauge already high, week 6
    s_hook = st.hook_closeup(
        stairs, hudl,
        beats=[(0, "happy", 0), (c("hook2", "gimnasio") - 0.1, "grit", 0)],
        texts=[(0.0, c("hook", "mejoró") - 0.15, "3 PISOS × 3 AL DÍA", P["gold"], 3, 98),
               (c("hook", "mejoró") - 0.1, c("hook2", "gimnasio") - 0.15, "MÁS CONDICIÓN", P["green"], 4, 98),
               (c("hook2", "gimnasio"), None, "SIN GIMNASIO", P["white"], 4, 100)],
        t_punch=c("hook2", "gimnasio"),
        side=(0.0, L("ctx").start, lambda g: cp.gauge(lerp(0.4, 0.7, ease_io(prog(g, 0.2, 1.2))), g, "CONDICIÓN"), 999),
        side_xy=(212, 300), side_scale=0.85)

    # 2. CONTEXT — week 1, third floor, always the elevator
    s_ctx = st.context_walk(
        lambda g, s: office(g), hudl, t_w1, t_w1, rewind=True, walk_px=0,
        items=[(c("ctx", "piso"), text_sprite("PISO 3", P["gold"], scale=1), 70, None),
               (c("ctx", "ascensor"), cv.villain("ascensor", "sly", 0, size=0.5), 200, None)],
        texts=[(c("ctx", "ascensor"), None, "SIEMPRE EN ASCENSOR", P["white"], 2, 175)])

    # 3. VILLAIN — the elevator tempts him
    s_mon = st.villain_rise(
        lambda g: cast.gym_bg("night").copy(), hudl, "ascensor", c("mon", "monstruo"), c("mon", "puerta"),
        leo_pose=lambda g, sc: {"mouth": "smile" if not sc else "flat", "eyes": "open", "arm_r": (40, 20) if sc else (5, 5)},
        texts=[(c("mon", "monstruo"), None, "EL ASCENSOR", P["steel_l"], 4, 112)], dark=0.2)

    # 4. TURN — he climbs the stairs (scrolling stairwell)
    def s_turn(g):
        st_ = L("turn").start
        img = cv.stairs_bg(g, climb=max(0.0, g - st_) * 140)
        bob = abs(math.sin(g * 10)) * 4
        paste(img, st.leo({"walk": g * 14, "mouth": "grit", "sweat": g > c("turn", "rápido"),
                           "arm_l": (30 * math.sin(g * 14), 40), "arm_r": (-30 * math.sin(g * 14), 40), "bob": bob}, g),
              140, 320, scale=2.6)
        if g > c("turn", "sesenta"):
            n = int(lerp(0, 60, ease_out(prog(g, c("turn", "sesenta"), 1.4))))
            impact_text(img, f"{n} ESCALONES", 135, 120, g, c("turn", "sesenta"), color=P["gold"], scale=4)
        else:
            impact_text(img, "A PIE", 135, 120, g, c("turn", "pie"), color=P["green"], scale=5)
        hudl(img, g)
        return img

    # 5. DATA — the study routine as a 3×3 grid
    t_v, t_s = c("data", "veces"), c("data", "semana")

    def draw_data(img, g):
        paste(img, cv.heart("happy", g, bpm=110), 135, 250, scale=1.6, anchor="center")
        for i in range(3):
            for j in range(3):
                tt = t_v + i * 0.12 if j == 0 else t_s + (i * 3 + j) * 0.05
                if g > tt:
                    x, y = 75 + i * 60, 120 + j * 0  # 3 climbs per day
                    label(img, "▲" if False else "3P", 75 + i * 60, 150, color=P["gold"], scale=2)
        if g > t_v:
            label(img, "3 VECES AL DÍA", 135, 120, color=P["white"], scale=2)
        if g > t_s:
            label(img, "3 DÍAS POR SEMANA", 135, 190, color=P["sky"], scale=2)

    s_data = st.inner_metric(lambda g: cast.lab_bg(g), hudl, draw_data,
                             src="JENKINS 2019 · JÓVENES SEDENTARIOS · 12 POR GRUPO")

    # 6. STILL — the elevator keeps waiting (lurk in the lobby)
    s_still = st.lurk(lambda g, s: cv.office_bg(g, 0.3, None), hudl, "ascensor", L("still").start,
                      c("still", "esperándolo") - 0.3,
                      texts=[(c("still", "esperándolo"), None, "SEGUÍA ESPERANDO", P["steel_l"], 3, 108)],
                      pages=True, page_base=7, villain_mood="sad")

    # 7. SETUP — treadmill test in the lab
    s_setup = st.slowmo(lambda g: cast.lab_bg(g), hudl, L("setup").start,
                        lambda k: {"walk": k * 30, "mouth": "grit", "sweat": k > 0.5},
                        texts=[(c("setup", "esfuerzo"), None, "PRUEBA DE ESFUERZO", P["white"], 3, 100)], zoom=0.3)

    # 8. REVEAL
    t_hit = c("reveal", "aeróbica")
    s_reveal = st.reveal_closeup(
        lambda g: cast.lab_bg(g), hudl, t_hit, ("CONDICIÓN", 0.45, 0.7, t_hit - 0.05),
        texts=[(t_hit - 0.05, None, "SUBIÓ", P["green"], 6, 104),
               (c("reveal", "minutos"), None, "UNOS MINUTOS AL DÍA", P["white"], 2, 160)],
        mood_pre="grit", mood_hit="happy", src="JENKINS 2019 · VO2 PICO")

    # 9. TWIST + CTA — loops to the stairwell close-up
    s_end = st.twist_loop(
        stairs, hudl, "ascensor", c("twist", "ojo"), c("twist", "pequeño"), L("cta").start,
        cta_lines=(("¿ESCALERAS", P["gold"]), ("O ASCENSOR?", P["steel_l"])),
        src="JENKINS 2019 · ESTUDIO PEQUEÑO", villain_mood="sly",
        extra_texts=[(c("twist", "modesta"), L("cta").start - 0.15, "MEJORA MODESTA", P["fat_l"], 3, 150)])

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("ctx", "ctx", s_ctx, "cut", 0.2, 0.3),
        ("mon", "mon", s_mon, "pixelate", 0.3, 0.2),
        ("turn", "turn", s_turn, "whip_left", 0.25, 0.15),
        ("data", "data", s_data, "dither", 0.25, 0.2),
        ("still", "still", s_still, "whip_left", 0.25, 0.15),
        ("setup", "setup", s_setup, "iris", 0.35, 0.2),
        ("reveal", "reveal", s_reveal, "cut", 0.15, 0.1),
        ("end", "twist", s_end, "pixelate", 0.25, 0.1),
    ])
    emph = {norm(w): col for w, col in [("escaleras", P["gold"]), ("tres", P["gold"]), ("mejoró", P["green"]),
            ("gimnasio", P["white"]), ("ascensor", P["steel_l"]), ("monstruo", P["steel_l"]), ("pie", P["green"]),
            ("sesenta", P["gold"]), ("sedentarios", P["sky"]), ("esperándolo", P["steel_l"]), ("seis", P["gold"]),
            ("aeróbica", P["green"]), ("minutos", P["gold"]), ("ojo", P["red_l"]), ("modesta", P["fat_l"])]}
    return Director(tl, scenes, SubStyle(y=356, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.25))
