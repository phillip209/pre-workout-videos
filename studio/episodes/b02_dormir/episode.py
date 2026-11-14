"""B02 · "Durmió 4 horas: lo más raro fue su hambre" — story format (template b01v2).

Fact (checked 2026-11-14): Spiegel K, Tasali E, Penev P, Van Cauter E. Ann Intern Med 2004;141:846-850.
Randomized crossover, 12 healthy young men; 2 nights of 4 h in bed vs 2 nights of 10 h, with controlled
calorie intake and activity. Sleep restriction: leptin -18 %, ghrelin +28 %, hunger +24 %.
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast, organs
from engine import cast_plus as cp, cast_villains as cv, story as st
from engine.gfx import P, prog, ease_out, ease_io, ease_back, lerp, paste
from engine.kit import label, pop_scale, paste_scaled, count_text, scenes_from
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "b02_dormir"
BPM = 108
LEAD_IN = 0.08
TAIL = 1.4
NARRATION_FILE = "episodes/b02_dormir/narration.mp3"

LINES = [
    {"id": "hook", "text": "Leo durmió solo cuatro horas, dos noches seguidas."},
    {"id": "hook2", "text": "Y lo más raro... no fue el cansancio."},
    {"id": "hook3", "text": "Fue su hambre.", "hold": 0.1},
    {"id": "n1", "text": "Noche uno. Celular, una serie más... y a dormir a las tres."},
    {"id": "n2", "text": "Noche dos: llega el monstruo. Ojeras, bostezos, cero energía."},
    {"id": "turn", "text": "Pero por dentro, dos hormonas estaban peleando."},
    {"id": "gre", "text": "La grelina, la que te da hambre, subió un veintiocho por ciento."},
    {"id": "lep", "text": "La leptina, la que te sacia, bajó un dieciocho."},
    {"id": "still", "text": "Y el monstruo... tenía hambre."},
    {"id": "setup", "text": "En el estudio, comían lo mismo y se movían lo mismo..."},
    {"id": "reveal", "text": "y aun así, su hambre subió un veinticuatro por ciento."},
    {"id": "reveal2", "text": "¡Solo por dormir poco!", "hold": 0.1},
    {"id": "twist", "text": "La buena noticia: cuando esos mismos jóvenes durmieron diez horas, el hambre bajó."},
    {"id": "cta", "text": "¿Cuántas horas dormiste anoche?"},
]

TITLE = "Durmió 4 horas dos noches: lo más raro fue su hambre 😴 #Shorts"
DESCRIPTION = (
    "Leo durmió solo 4 horas dos noches seguidas. Lo más raro no fue el cansancio: fue su hambre.\n\n"
    "Fuente: Spiegel et al., Ann Intern Med, 2004 — ensayo cruzado con 12 hombres jóvenes sanos; 2 noches "
    "con 4 h en cama frente a 2 noches con 10 h, con la comida y la actividad controladas. Con poco sueño, "
    "la grelina (hormona del hambre) subió 28 %, la leptina (saciedad) bajó 18 % y el hambre reportada subió "
    "24 %.\nEstudio pequeño y de corto plazo; los resultados pueden variar entre personas. Contenido "
    "educativo, no es consejo médico.\nVoz: ElevenLabs.\n\n#sueño #hambre #salud #quelepasaatucuerpo #Shorts")
TAGS = ["dormir poco", "sueño y hambre", "grelina", "leptina", "qué le pasa a tu cuerpo", "salud"]


def hormone(color, mood, t, size=1.0):
    """Small hormone character (round blob with a face)."""
    S = gfx.new(36, 34)
    d = ImageDraw.Draw(S)
    w = int(math.sin(t * 5) * 1)
    d.ellipse([2, 4 + w, 33, 32 + w], fill=color)
    d.ellipse([7, 8 + w, 14, 13 + w], fill=gfx.lerpc(color, P["white"], 0.5))
    organs._face(d, 18, 16 + w, mood, t)
    out = gfx.outline(S)
    if size != 1:
        out = out.resize((max(1, int(out.width * size)), max(1, int(out.height * size))), 0)
    return out


GRE, LEP = (120, 200, 90), (110, 160, 240)


def sound_cues(tl):
    c, L = tl.cue, tl.line
    cues = [(0.0, "impact", 0.9), (0.0, "whoosh", 0.6),
            (c("hook", "cuatro"), "ding", 0.6), (c("hook2", "cansancio"), "blip", 0.6),
            (c("hook3", "hambre") - 0.05, "growl", 0.9), (c("hook3", "hambre"), "impact", 0.8),
            (L("n1").start - 0.25, "rewind", 0.9), (c("n1", "celular"), "blip", 0.6),
            (c("n1", "serie"), "pop", 0.5), (c("n1", "tres"), "alarm", 0.4),
            (c("n2", "noche"), "tick", 0.5), (c("n2", "monstruo") - 0.1, "growl", 1.0), (c("n2", "monstruo"), "impact", 0.7),
            (c("n2", "ojeras"), "thud", 0.5), (c("n2", "bostezos"), "deflate", 0.5), (c("n2", "energía"), "bar_down", 0.8),
            (L("turn").start, "scan", 0.9), (c("turn", "peleando"), "clank", 0.6),
            (c("gre", "subió"), "bar_up", 0.8), (c("gre", "veintiocho"), "babble", 0.6),
            (c("lep", "bajó"), "bar_down", 0.8), (c("lep", "dieciocho"), "deflate", 0.6),
            (c("still", "monstruo"), "growl", 0.6), (c("still", "hambre"), "chomp", 0.8),
            (c("still", "hambre") + 0.15, "chomp", 0.8),
            (c("setup", "estudio"), "ding", 0.5), (c("setup", "mismo"), "pop", 0.5),
            (c("reveal", "veinticuatro") - 0.04, "impact", 1.0), (c("reveal", "veinticuatro"), "sparkle", 0.6),
            (c("reveal2", "poco"), "boing", 0.6),
            (c("twist", "noticia"), "ding", 0.6), (c("twist", "bajó"), "bar_down", 0.8),
            (L("cta").start - 0.1, "pop", 0.6), (c("cta", "anoche"), "ding", 0.7)]
    return cues


def music_sections(tl):
    c, L = tl.cue, tl.line
    t_hit = c("reveal", "veinticuatro")
    return [(0.0, L("n1").start - 0.25, "pulse"), (L("n1").start, L("n2").start, "drive"),
            (L("n2").start, L("turn").start - 0.1, "low"), (L("turn").start, L("still").start, "drive"),
            (L("still").start, L("setup").start, "pulse"), (L("setup").start, t_hit - 0.6, "mystery"),
            (t_hit - 0.6, t_hit, "silence"), (t_hit, L("twist").start, "triumph"),
            (L("twist").start, tl.total, "hope")]


def make_director(tl):
    c, L = tl.cue, tl.line
    t_n1, t_n2, t_tw = L("n1").start, c("n2", "noche"), L("twist").start

    def hud_text(g):
        if g < t_n1 - 0.2:
            return "NOCHE 2 · 4 H"
        if g < t_n2:
            return "NOCHE 1 · 4 H"
        if g < t_tw or g > L("cta").start:
            return "NOCHE 2 · 4 H"
        return "10 H EN CAMA"

    hudl = st.Hud([(0, 2), (t_n1 - 0.2, 2), (t_n1 + 0.3, 1, 0.5), (t_n2, 2, 0.3)], 2,
                  flashes=[0.2, t_n1 + 0.3, t_n2, t_tw], text_fn=hud_text)

    def night_room(g):
        img = cast.bedroom_bg(g, dawn=0.0)
        return gfx.darken(img, 0.25)

    def phone_glow(g):
        return cv.phone(g)

    s_hook = st.hook_closeup(
        night_room, hudl,
        beats=[(0, "neutral", 0), (c("hook2", "raro"), "sad", 0), (c("hook3", "hambre") - 0.1, "shock", 0.0)],
        texts=[(c("hook", "cuatro"), c("hook2", "cansancio") - 0.2, "4 H DE SUEÑO", P["sky"], 3, 98),
               (c("hook2", "cansancio") - 0.1, c("hook3", "hambre") - 0.1, "¿EL CANSANCIO?", P["white"], 3, 98),
               (c("hook3", "hambre"), None, "¿SU HAMBRE?", P["orange"], 5, 100)],
        t_punch=c("hook3", "hambre"),
        side=(c("hook2", "cansancio") - 0.1, c("hook3", "hambre"), lambda g: cast.sleeping_head("calm"),
              c("hook2", "cansancio") + 0.15))

    s_n1 = st.context_walk(
        lambda g, s: night_room(g), hudl, t_n1, t_n1, rewind=True, walk_px=0,
        items=[(c("n1", "celular"), cv.phone(0), 60, None), (c("n1", "tres"), cast.digital_clock("03:00"), 190, False)],
        texts=[(c("n1", "tres"), None, "A DORMIR A LAS 3", P["red_l"], 3, 175)])

    s_n2 = st.villain_rise(
        night_room, hudl, "hambre", c("n2", "monstruo"), c("n2", "ojeras"),
        leo_pose=lambda g, sc: {"mouth": "o" if g > c("n2", "bostezos") and g < c("n2", "energía") else "sad",
                                "eyes": "sad" if sc else "open", "droop": 0.6 if sc else 0,
                                "arm_l": (150, 40) if c("n2", "bostezos") < g < c("n2", "energía") else (5, 5)},
        bars=[(c("n2", "energía"), "ENERGÍA", 0.8, 0.12, P["green"], -1, 12)],
        texts=[(c("n2", "monstruo") - 0.05, c("n2", "ojeras") - 0.1, "EL HAMBRE", P["orange"], 4, 112),
               (c("n2", "ojeras"), c("n2", "bostezos") - 0.1, "OJERAS", P["lav"], 4, 112),
               (c("n2", "bostezos"), c("n2", "energía") - 0.1, "BOSTEZOS", P["sky"], 4, 112),
               (c("n2", "energía"), None, "CERO ENERGÍA", P["red_l"], 3, 112)])

    def inner_bg(g):
        return cast.tissue_bg(g, hue="pink")

    def inner_fight(g):
        img = inner_bg(g)
        paste(img, hormone(GRE, "angry", g), 90 + math.sin(g * 8) * 6, 220, scale=2.2, anchor="center")
        paste(img, hormone(LEP, "angry", g), 180 - math.sin(g * 8) * 6, 220, scale=2.2, anchor="center")
        fx.burst(img, 135, 220, (g * 2) % 0.6, n=8, colors=(P["white"], P["gold"]))
        label(img, "GRELINA", 90, 270, color=GRE, scale=1)
        label(img, "LEPTINA", 180, 270, color=LEP, scale=1)
        return img

    s_turn = st.xray_turn(lambda g: gfx.darken(cast.bedroom_bg(g, dawn=0.3), 0.15), hudl, L("turn").start, inner_fight,
                          texts=[(c("turn", "hormonas"), None, "2 HORMONAS", P["gold"], 4, 108)],
                          leo_pose={"mouth": "flat", "eyes": "sad"})

    t_g, t_l = c("gre", "subió"), c("lep", "bajó")

    def draw_horm(img, g):
        kg = ease_back(prog(g, t_g, 0.5))
        kl = ease_out(prog(g, t_l, 0.5))
        paste(img, hormone(GRE, "angry" if kg > 0.5 else "happy", g, 1 + 0.28 * kg), 80, 225, scale=2.2, anchor="center")
        paste(img, hormone(LEP, "sad" if kl > 0.5 else "happy", g, 1 - 0.18 * kl), 190, 225, scale=2.2, anchor="center")
        label(img, "GRELINA", 80, 268, color=GRE, scale=2)
        label(img, "HAMBRE", 80, 286, color=P["white"])
        label(img, "LEPTINA", 190, 268, color=LEP, scale=2)
        label(img, "SACIEDAD", 190, 286, color=P["white"])
        paste(img, cv.stomach("sad" if kg > 0.5 else "happy", g, growl=kg), 135, 318, scale=0.9, anchor="center")
        if g > t_g:
            label(img, "+" + count_text(0, 28, g, t_g, 0.7, "{:.0f}") + " %", 80, 168, color=GRE, scale=3)
        if g > t_l:
            label(img, "-" + count_text(0, 18, g, t_l, 0.7, "{:.0f}") + " %", 190, 168, color=LEP, scale=3)

    s_horm = st.inner_metric(inner_bg, hudl, draw_horm, src="SPIEGEL 2004 · 12 JÓVENES · 4 H EN CAMA")

    def kitchen_night(g, s=0):
        return gfx.darken(cp.kitchen_bg(g), 0.3)

    s_still = st.lurk(kitchen_night, hudl, "hambre", L("still").start, c("still", "monstruo"),
                      texts=[(c("still", "hambre"), None, "TENÍA HAMBRE", P["orange"], 4, 108)], pages=False,
                      villain_mood="roar")

    def lab(g):
        return cast.lab_bg(g)

    t_mis = c("setup", "mismo")
    s_setup = st.slowmo(
        lab, hudl, L("setup").start, lambda k: {"mouth": "smile", "arm_r": (30, 40)},
        props=[(lambda g, k: cv.plate(True), lambda k: 70, lambda k: 140, 2.0),
               (lambda g, k: cv.plate(True), lambda k: 200, lambda k: 140, 2.0)],
        texts=[(t_mis, None, "MISMA COMIDA", P["white"], 3, 100),
               (c("setup", "movían"), None, "MISMO MOVIMIENTO", P["fat_l"], 2, 175)],
        zoom_to=(135, 230), zoom=0.25)

    t_hit = c("reveal", "veinticuatro")
    s_reveal = st.reveal_closeup(
        lambda g: gfx.darken(cp.kitchen_bg(g), 0.15), hudl, t_hit, ("HAMBRE", 0.4, 0.88, c("reveal", "hambre")),
        texts=[(t_hit - 0.05, None, "+24 %", P["orange"], 6, 104),
               (c("reveal2", "dormir"), None, "POR DORMIR POCO", P["white"], 2, 164)],
        mood_pre="sad", mood_hit="shock", tongue=0.0,
        popup=(c("reveal2", "dormir"), lambda g: cv.stomach("sad", g, 1.0), "¡COMIDA!"),
        src="SPIEGEL 2004 · HAMBRE REPORTADA")

    s_end = st.twist_loop(
        night_room, hudl, "hambre", c("twist", "noticia"), c("twist", "bajó"), L("cta").start,
        cta_lines=(("¿CUÁNTAS HORAS", P["white"]), ("DORMISTE?", P["gold"])),
        ojo_text="¡BUENA NOTICIA!", gauge_cfg=("HAMBRE", 0.88, 0.45), src="SPIEGEL 2004 · 10 H EN CAMA",
        villain_mood="sleepy")

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("n1", "n1", s_n1, "cut", 0.2, 0.3),
        ("n2", "n2", s_n2, "pixelate", 0.3, 0.2),
        ("turn", "turn", s_turn, "cut", 0.2, 0.15),
        ("horm", "gre", s_horm, "dither", 0.25, 0.2),
        ("still", "still", s_still, "whip_left", 0.25, 0.15),
        ("setup", "setup", s_setup, "iris", 0.35, 0.2),
        ("reveal", "reveal", s_reveal, "cut", 0.15, 0.1),
        ("end", "twist", s_end, "pixelate", 0.25, 0.1),
    ])
    emph = {norm(w): col for w, col in [("cuatro", P["sky"]), ("raro", P["gold"]), ("hambre", P["orange"]),
            ("tres", P["red_l"]), ("monstruo", P["orange"]), ("energía", P["red_l"]), ("hormonas", P["gold"]),
            ("grelina", GRE), ("leptina", LEP), ("veintiocho", GRE), ("dieciocho", LEP), ("mismo", P["fat_l"]),
            ("veinticuatro", P["orange"]), ("poco", P["red_l"]), ("diez", P["green"]), ("bajó", P["green"]),
            ("anoche", P["gold"])]}
    return Director(tl, scenes, SubStyle(y=356, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.25))
