"""Episode 22: "¿El cardio te quita músculo?" — MITO.

Source (checked 2026-11-13): Schumann M et al. 2022, Sports Med 52:601-612 — 43 studies, 1090
participants: concurrent aerobic + strength training did not compromise hypertrophy or maximal
strength vs strength alone; explosive strength gains were attenuated, mainly when both were done in
the same session (less so with >= 3 h between).
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast
from engine.gfx import P, prog, ease_out, ease_io, lerp, paste
from engine.kit import (blinking, label, pop_scale, paste_scaled, arrow, text_sprite, stamp_slam, bar,
                        end_card, scenes_from, hook_camera, street_bg)
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "e22_cardio"
VERDICT = "MITO"
BPM = 108
LEAD_IN = 0.15
TAIL = 2.2
NARRATION_FILE = "episodes/e22_cardio/narration.mp3"

LINES = [
    {"id": "hook", "text": "¿Hacer cardio te come las ganancias?"},
    {"id": "fear", "text": "Muchos en el gym le tienen pánico: correr... y adiós músculo.", "hold": 0.2},
    {"id": "study", "text": "Un análisis juntó cuarenta y tres estudios, con más de mil personas."},
    {"id": "compare", "text": "Compararon entrenar solo fuerza... contra fuerza más cardio."},
    {"id": "result", "text": "El crecimiento del músculo fue prácticamente igual. Y la fuerza máxima, también.", "hold": 0.3},
    {"id": "detail", "text": "La única diferencia: la fuerza explosiva mejoró un poco menos, sobre todo al hacer los dos en la misma sesión."},
    {"id": "tip", "text": "Así que, si quieres saltar más alto, sepáralos unas horas."},
    {"id": "resolve", "text": "El cardio no se come tu músculo.", "hold": 0.7},
    {"id": "cta", "text": "¿Team cardio, o team pesas?"},
]

TITLE = "¿El cardio te quita músculo? MITO #Shorts"
DESCRIPTION = (
    "¿El cardio te quita músculo? MITO. Un metaanálisis de 43 estudios con 1 090 personas encontró que combinar "
    "cardio y fuerza no redujo el crecimiento muscular ni la fuerza máxima frente a entrenar solo fuerza. La "
    "fuerza explosiva mejoró algo menos, sobre todo al hacer ambos en la misma sesión.\n\n"
    "Fuentes: Schumann et al., Sports Med, 2022.\nVoz: ElevenLabs.\n\n"
    "#fitness #cardio #musculo #mitosfitness #fitnesssinhumo #Shorts")
TAGS = ["cardio", "músculo", "entrenamiento concurrente", "mitos fitness", "fitness sin humo"]


def sound_cues(tl):
    c = tl.cue
    return [(0.0, "impact", 0.8), (0.02, "whoosh", 0.6), (c("hook", "ganancias"), "chomp", 0.9),
            (c("hook", "ganancias") + 0.2, "chomp", 0.9),
            (c("fear", "pánico"), "alarm", 0.5), (c("fear", "adiós"), "whoosh", 0.6),
            (c("study") - 0.2, "whoosh", 0.4), (c("study", "cuarenta"), "sparkle", 0.5), (c("study", "mil"), "rise", 0.5),
            (c("compare", "fuerza"), "clank", 0.6), (c("compare", "cardio"), "step", 0.7),
            (c("result", "igual"), "ding", 0.8), (c("result", "también"), "ding", 0.6),
            (c("detail", "explosiva"), "boing", 0.6), (c("detail", "sesión"), "blip", 0.6),
            (c("tip", "horas"), "pop", 0.7),
            (c("resolve") - 0.2, "whoosh", 0.4), (c("resolve", "músculo"), "stamp", 1.0),
            (c("resolve", "músculo") + 0.05, "sparkle", 0.6),
            (c("cta") - 0.15, "impact", 0.6), (c("cta", "pesas"), "ding", 0.6)]


def music_sections(tl):
    c = tl.cue
    return [(0.0, c("study") - 0.2, "tense"), (c("study") - 0.2, c("result") - 0.05, "mystery"),
            (c("result") - 0.05, c("result", "igual"), "silence"),
            (c("result", "igual"), c("resolve") - 0.2, "groove"),
            (c("resolve") - 0.2, c("cta") - 0.1, "hope"), (c("cta") - 0.1, tl.total, "outro")]


def treadmill_monster(g, open_mouth=0.0):
    """Original gag: a treadmill with angry eyes and a mouth that 'eats gains'."""
    S = gfx.new(110, 80)
    d = ImageDraw.Draw(S)
    d.polygon([(4, 70), (106, 70), (96, 52), (14, 52)], fill=P["steel_d"])
    off = int(g * 30) % 8
    for x in range(14 + off, 96, 8):
        d.line([x, 54, x - 4, 68], fill=P["ink"])
    d.rectangle([84, 8, 90, 54], fill=P["steel"])
    d.rounded_rectangle([66, 4, 104, 24], radius=3, fill=P["ink"], outline=P["steel"])
    # eyes on the console
    d.rectangle([72, 10, 77, 14], fill=P["red"]); d.rectangle([90, 10, 95, 14], fill=P["red"])
    d.line([71, 8, 78, 11], fill=P["red_l"]); d.line([89, 11, 96, 8], fill=P["red_l"])
    # mouth at the front of the belt
    m = int(open_mouth * 12)
    d.rectangle([6, 70 - m, 30, 74], fill=P["ink"])
    for x in range(8, 30, 5):
        d.polygon([(x, 70 - m), (x + 2, 74 - m), (x + 4, 70 - m)], fill=P["white"])
    return gfx.outline(S)


def make_director(tl):
    c, L = tl.cue, tl.line

    def s_hook(g):
        img = cast.gym_bg("night").copy()
        t_gan = c("hook", "ganancias")
        chomp = abs(math.sin((g - t_gan) * 14)) if g > t_gan else 0.2
        paste(img, treadmill_monster(g, chomp), 160, 342, scale=2)
        scared = g > t_gan
        paste(img, cast.hero({"mouth": "o" if scared else "smile", "eyes": "wide" if scared else "open",
                              "sweat": scared, "arm_l": (40, 120) if scared else (10, 10)}), 60, 342, scale=3)
        if scared:
            # tiny protein blocks being sucked into the mouth
            for i in range(5):
                k = ((g - t_gan) * 1.5 + i * 0.2) % 1
                img.alpha_composite(cast.protein_block(), (int(lerp(90, 120, k)), int(lerp(230, 320, k))))
        return hook_camera(img, g, cx=135, cy=240)

    def s_fear(g):
        img = street_bg(g, scroll=g * 40)
        t_adi = c("fear", "adiós")
        paste(img, cast.hero({"walk": g * 12, "mouth": "sad", "eyes": "sad", "arm_l": (20 * math.sin(g * 12), 40),
                              "arm_r": (-20 * math.sin(g * 12), 40)}), 90, 330, scale=3)
        if g > t_adi:
            k = ease_out(prog(g, t_adi, 1.2))
            fib = cast.muscle_fiber(40, 14, mood="happy", nuclei=3, t=g)
            paste(img, fib, lerp(120, 300, k), 200 - math.sin(k * math.pi) * 40, scale=2, anchor="center")
            paste(img, text_sprite("¡CHAO!", P["white"], scale=2), lerp(130, 310, k), 150, anchor="center")
        return img

    def s_lab(g):
        img = cast.lab_bg(g)
        d = ImageDraw.Draw(img)
        t43, tmil = c("study", "cuarenta"), c("study", "mil")
        t_cmp = L("compare").start
        if g < t_cmp - 0.1:
            n = int(lerp(1, 43, ease_out(prog(g, t43 - 0.2, 0.9))))
            paste(img, cast.doc_stack(min(n, 18)), 80, 300, scale=2, anchor="mid_bottom")
            label(img, f"{n} ESTUDIOS", 80, 60, color=P["gold"], scale=2)
            if g > tmil - 0.2:
                k = ease_out(prog(g, tmil - 0.2, 0.8))
                for i in range(int(k * 60)):
                    img.alpha_composite(cast.tiny_person([P["fog"], P["sky"], P["pink"]][i % 3]),
                                        (160 + (i % 10) * 9, 150 + (i // 10) * 13))
                label(img, f"{int(k * 1090):,}".replace(",", " ") + " PERSONAS", 205, 240, color=P["gold"])
            return img
        # two lanes
        t_res, t_tam = c("result", "igual"), c("result", "también")
        t_det, t_ses = L("detail").start, c("detail", "sesión")
        t_tip = L("tip").start
        grow = ease_out(prog(g, t_cmp + 0.6, 2.0))
        for i, (name, x, col) in enumerate((("SOLO FUERZA", 70, P["red_l"]), ("FUERZA + CARDIO", 200, P["sky"]))):
            label(img, name, x, 50, color=col)
            paste(img, cast.hero({"arm_r": (5, 10 + 140 * math.sin(g * 6 + i) ** 2), "holding": "dumbbell",
                                  "mouth": "grit", "bicep": 0.4 + 0.5 * grow}), x, 170, scale=1.5)
            if i == 1:
                paste(img, cast.shoe(), x + 30, 160, scale=1)
            fib = cast.muscle_fiber(36, lerp(10, 18, grow), mood="proud" if grow > 0.6 else "happy", nuclei=3, t=g)
            paste(img, fib, x, 200, scale=2, anchor="center")
            if g > t_res - 0.3:
                label(img, "MÚSCULO", x - 40, 236, color=P["fog"], center=False)
                bar(img, x - 50, 248, 100, 6, 0.8 * ease_out(prog(g, t_res - 0.3, 0.5)), P["muscle"])
            if g > t_tam - 0.3:
                label(img, "FUERZA MÁX.", x - 40, 262, color=P["fog"], center=False)
                bar(img, x - 50, 274, 100, 6, 0.75 * ease_out(prog(g, t_tam - 0.3, 0.5)), P["gold"])
            if g > t_det:
                val = 0.7 if i == 0 else lerp(0.7, 0.55, ease_out(prog(g, c("detail", "menos"), 0.5)))
                label(img, "EXPLOSIVA", x - 40, 288, color=P["fog"], center=False)
                bar(img, x - 50, 300, 100, 6, val * ease_out(prog(g, t_det, 0.4)), P["green"])
        if g > t_res:
            paste_scaled(img, text_sprite("=", P["green"], scale=3), 135, 210, pop_scale(g, t_res))
        if g > t_ses and g < t_tip:
            label(img, "MISMA SESIÓN", 200, 316, color=P["red_l"])
        if g > t_tip:
            paste_scaled(img, cast.digital_clock("+3 H", P["green"]), 200, 140, pop_scale(g, c("tip", "horas")) * 1.2)
        return img

    def s_resolve(g):
        img = street_bg(g, scroll=g * 60, tod="sunrise")
        paste(img, cast.hero({"walk": g * 12, "mouth": "grin", "bicep": 0.95, "arm_l": (20 * math.sin(g * 12), 40),
                              "arm_r": (-20 * math.sin(g * 12), 40)}), 120, 330, scale=3)
        fib = cast.muscle_fiber(40, 18, mood="proud", nuclei=3, t=g, glow=0.5)
        paste(img, fib, 215, 230 + math.sin(g * 6) * 4, scale=2, anchor="center")
        out = gfx.camera(img, 1.0)
        stamp_slam(out, VERDICT, g, c("resolve", "músculo"), y=110)
        return out

    def s_cta(g):
        img = cast.end_bg(g)
        d = ImageDraw.Draw(img)
        # versus screen
        d.polygon([(0, 120), (150, 120), (120, 300), (0, 300)], fill=P["blue_d"])
        d.polygon([(150, 120), (W, 120), (W, 300), (120, 300)], fill=P["red_d"])
        paste(img, cast.shoe(), 60, 210, scale=3, anchor="center")
        paste(img, cast.dumbbell(), 210, 210, scale=3, anchor="center")
        label(img, "TEAM CARDIO", 60, 260, color=P["sky"], scale=1)
        label(img, "TEAM PESAS", 210, 260, color=P["red_l"], scale=1)
        paste_scaled(img, text_sprite("VS", P["gold"], scale=3), 135, 210, pop_scale(g, L("cta").start) * (1 + 0.1 * math.sin(g * 8)))
        label(img, "PRE-WORKOUT · FITNESS SIN HUMO", 135, 80, color=P["gold"])
        return img

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("fear", "fear", s_fear, "whip_left", 0.3, 0.2),
        ("lab", "study", s_lab, "pixelate", 0.3, 0.2),
        ("resolve", "resolve", s_resolve, "dither", 0.35, 0.25),
        ("cta", "cta", s_cta, "whip_left", 0.3, 0.15),
    ])
    emph = {norm(w): col for w, col in [("cardio", P["sky"]), ("ganancias", P["gold"]), ("pánico", P["red_l"]),
            ("igual", P["green"]), ("explosiva", P["green"]), ("horas", P["gold"]), ("músculo", P["muscle_l"]),
            ("fuerza", P["red_l"]), ("pesas", P["red_l"])]}
    return Director(tl, scenes, SubStyle(y=352, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.3))
