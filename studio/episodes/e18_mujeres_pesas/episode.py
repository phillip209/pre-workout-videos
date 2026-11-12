"""Episode 18: "¿Las mujeres no ganan músculo con pesas?" — MITO.

Source (checked 2026-11-12): Refalo MC et al. 2025, PeerJ 13:e19042 — Bayesian systematic review and
meta-analysis, 29 studies of healthy adults doing resistance training. Relative increases in muscle
size were similar between sexes; absolute increases slightly favoured males (mainly upper body).
"""
from __future__ import annotations

import math
import os

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast
from engine.gfx import P, prog, ease_out, ease_io, lerp, paste
from engine.kit import (blinking, label, pop_scale, paste_scaled, arrow, text_sprite, stamp_slam, bar,
                        badge, end_card, scenes_from, hook_camera)
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "e18_mujeres_pesas"
VERDICT = "MITO"
BPM = 100
LEAD_IN = 0.15
TAIL = 2.2
NARRATION_FILE = "episodes/e18_mujeres_pesas/narration.mp3"

LINES = [
    {"id": "hook", "text": "Dicen que las mujeres no ganan músculo con pesas."},
    {"id": "q", "text": "O que ganan tan poquito... que no vale la pena.", "hold": 0.3},
    {"id": "study", "text": "Una revisión juntó veintinueve estudios con adultos sanos que entrenaron fuerza."},
    {"id": "compare", "text": "Y midió cuánto creció el músculo de cada persona, comparado con cómo empezó."},
    {"id": "result", "text": "El resultado: el aumento relativo fue similar en mujeres y en hombres.", "hold": 0.4},
    {"id": "kilos", "text": "En kilos, los hombres ganaron un poco más, en parte porque suelen empezar con más músculo."},
    {"id": "percent", "text": "Pero en proporción, el músculo respondió casi igual.", "hold": 0.3},
    {"id": "resolve", "text": "Las pesas funcionan. Para todos.", "hold": 0.7},
    {"id": "cta", "text": "Mándaselo a quien necesita escuchar esto."},
]
SPOKEN = ("Dicen que las mujeres no ganan músculo con pesas. O que ganan tan poquito... que no vale la pena. "
          "Una revisión juntó veintinueve estudios con adultos sanos que entrenaron fuerza. Y midió cuánto creció "
          "el músculo de cada persona, comparado con cómo empezó. El resultado: el aumento relativo fue similar "
          "en mujeres y en hombres. En kilos, los hombres ganaron un poco más, en parte porque suelen empezar con "
          "más músculo. Pero en proporción, el músculo respondió casi igual. <break time=\"0.7s\" /> Las pesas "
          "funcionan. Para todos. Mándaselo a quien necesita escuchar esto.")

VOICE = {"voice_id": os.environ.get("PW_VOICE_ID", "qRUgOhnxGASxirG4fKjv"), "model": "eleven_multilingual_v2",
         "settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True}}

TITLE = "¿Las mujeres no ganan músculo con pesas? MITO #Shorts"
DESCRIPTION = (
    "¿Las mujeres no ganan músculo con pesas? MITO. Una revisión sistemática con metaanálisis de 29 estudios "
    "en adultos sanos encontró que los aumentos relativos de tamaño muscular fueron similares entre hombres y "
    "mujeres; en valores absolutos, los hombres ganaron ligeramente más.\n\n"
    "Fuentes: Refalo et al., PeerJ, 2025.\nVoz: ElevenLabs.\n\n"
    "#fitness #mujeres #pesas #mitosfitness #fitnesssinhumo #Shorts")
TAGS = ["mujeres", "pesas", "músculo", "fitness", "fitness sin humo"]


def sound_cues(tl):
    c = tl.cue
    return [(0.0, "impact", 0.8), (0.02, "whoosh", 0.6),
            (c("hook", "dicen"), "pop", 0.6), (c("hook", "músculo"), "pop", 0.6), (c("hook", "pesas"), "boing", 0.6),
            (c("q", "poquito"), "pop", 0.6), (c("q", "pena"), "explode", 0.5),
            (c("study") - 0.2, "whoosh", 0.5), (c("study", "veintinueve"), "sparkle", 0.6),
            (c("compare") - 0.2, "whoosh", 0.4), (c("compare", "creció"), "inflate", 0.6),
            (c("result", "similar"), "impact", 0.8), (c("result", "similar") + 0.05, "ding", 0.6),
            (c("kilos") - 0.1, "blip", 0.7), (c("percent") - 0.05, "blip", 0.7),
            (c("percent", "igual"), "ding", 0.6),
            (c("resolve") - 0.2, "whoosh", 0.4), (c("resolve", "todos"), "stamp", 1.0),
            (c("resolve", "todos") + 0.05, "sparkle", 0.6),
            (c("cta") - 0.15, "pop", 0.6), (c("cta", "esto"), "ding", 0.6)]


def music_sections(tl):
    c = tl.cue
    return [(0.0, c("study") - 0.2, "tense"), (c("study") - 0.2, c("result") - 0.1, "mystery"),
            (c("result") - 0.1, c("result", "similar"), "silence"),
            (c("result", "similar"), c("resolve") - 0.2, "groove"),
            (c("resolve") - 0.2, c("cta") - 0.1, "hope"), (c("cta") - 0.1, tl.total, "outro")]


def make_director(tl):
    c, L = tl.cue, tl.line

    def speech(text, color=P["white"]):
        from engine.font import draw_text, text_width
        w = text_width(text, 1) + 14
        b = gfx.new(w, 30)
        d = ImageDraw.Draw(b)
        d.rounded_rectangle([1, 1, w - 2, 20], radius=5, fill=color)
        d.polygon([(w // 2 - 3, 20), (w // 2 + 4, 20), (w // 2 - 6, 28)], fill=color)
        draw_text(b, text, 7, 7, color=P["ink"])
        return gfx.outline(b)

    # 1-2. HOOK: Ana lifts while doubts pile up, then she pops them
    def s_hook(g):
        img = cast.gym_bg("night").copy()
        t_pena = c("q", "pena")
        flexed = g > t_pena
        rep = math.sin(g * 6) ** 2
        pose = {"style": "ana", "arm_r": (5, 10 + 140 * rep) if not flexed else (95, 85),
                "arm_l": (5, 10) if not flexed else (95, 85), "bicep": 0.75, "holding": None if flexed else "dumbbell",
                "mouth": "grit" if not flexed else "grin", "eyes": "happy" if flexed else "open"}
        if not flexed and g > c("hook", "pesas"):
            pose["eyes"] = "sad"
            pose["mouth"] = "flat"
        paste(img, cast.hero(pose), 135, 342, scale=3)
        bubbles = [("NO VAS A GANAR NADA", c("hook", "dicen"), 80, 70), ("¿MÚSCULO? IMPOSIBLE", c("hook", "músculo"), 180, 110),
                   ("ES MUY POQUITO", c("q", "poquito"), 85, 150), ("NO VALE LA PENA", c("q", "vale"), 190, 185)]
        for i, (txt, tt, x, y) in enumerate(bubbles):
            if flexed:
                fx.burst(img, x, y, g - t_pena, n=14, speed=70, gravity=80, life=0.6,
                         colors=(P["white"], P["fog"]), seed=i + 2)
                continue
            s = pop_scale(g, tt, 0.25)
            paste_scaled(img, speech(txt), x, y + math.sin(g * 3 + i) * 2, s)
        if flexed:
            fx.sparkles(img, 135, 230, g, n=10, radius=50)
        out = hook_camera(img, g, cx=135, cy=230)
        if flexed and g - t_pena < 0.25:
            out = gfx.flash(out, 0.5 * (1 - (g - t_pena) / 0.25))
        return out

    # 3. STUDY: 29 studies
    def s_study(g):
        img = cast.lab_bg(g)
        t29 = c("study", "veintinueve")
        n = int(lerp(1, 29, ease_out(prog(g, t29 - 0.3, 1.0))))
        paste(img, cast.doc_stack(min(n, 18)), 135, 300, scale=2, anchor="mid_bottom")
        if g > t29 - 0.1:
            label(img, f"{n} ESTUDIOS", 135, 60, color=P["gold"], scale=2)
        if g > c("study", "fuerza"):
            label(img, "ADULTOS SANOS · ENTRENAMIENTO DE FUERZA", 135, 86, color=P["fog"])
        return img

    # 4-7. COMPARE: relative vs absolute
    def s_compare(g):
        img = cast.end_bg(g)
        d = ImageDraw.Draw(img)
        t_cre = c("compare", "creció")
        t_sim = c("result", "similar")
        t_kil, t_pct = L("kilos").start, L("percent").start
        grow = ease_out(prog(g, t_cre, 1.6))
        # two fibers: women start smaller, men start bigger; same relative growth
        base_w, base_m = 14, 20
        rel = 1 + 0.35 * grow
        ana = cast.hero({"style": "ana", "mouth": "smile", "eyes": "blink" if blinking(g, 2.4) else "open"})
        leo = cast.hero({"mouth": "smile", "eyes": "blink" if blinking(g, 2.8, 1) else "open"})
        paste(img, ana, 70, 120, scale=1.5)
        paste(img, leo, 200, 120, scale=1.5)
        label(img, "MUJERES", 70, 126, color=P["pink"])
        label(img, "HOMBRES", 200, 126, color=P["tank"])
        fw = cast.muscle_fiber(40, base_w * rel, mood="proud" if grow > 0.5 else "happy", nuclei=3, t=g)
        fm = cast.muscle_fiber(40, base_m * rel, mood="proud" if grow > 0.5 else "happy", nuclei=3, t=g)
        paste(img, fw, 70, 175, scale=2, anchor="center")
        paste(img, fm, 200, 175, scale=2, anchor="center")
        if grow > 0.05:
            label(img, f"+{int(35 * grow)}%", 70, 212, color=P["green"], scale=2)
            label(img, f"+{int(35 * grow)}%", 200, 212, color=P["green"], scale=2)
        if g > t_sim:
            paste_scaled(img, text_sprite("≈", P["gold"], scale=4), 135, 180, pop_scale(g, t_sim, 0.3))
            label(img, "AUMENTO RELATIVO SIMILAR", 135, 244, color=P["gold"])
        # kilos vs percent toggle
        if g > t_kil - 0.1:
            mode_pct = g > t_pct - 0.05
            tab_y = 264
            for i, (name, active) in enumerate((("EN KILOS", not mode_pct), ("EN %", mode_pct))):
                x0 = 60 + i * 80
                d.rounded_rectangle([x0, tab_y, x0 + 70, tab_y + 16], radius=4,
                                    fill=P["gold"] if active else P["deep"], outline=P["fog"])
                label(img, name, x0 + 35, tab_y + 5, color=P["ink"] if active else P["fog"], outline=None)
            kf = ease_out(prog(g, t_kil, 0.6))
            if not mode_pct:
                bar(img, 50, 292, 160, 7, 0.55 * kf, P["pink"])
                bar(img, 50, 306, 160, 7, 0.75 * kf, P["tank"])
            else:
                kp = ease_out(prog(g, t_pct, 0.6))
                bar(img, 50, 292, 160, 7, lerp(0.55, 0.7, kp), P["pink"])
                bar(img, 50, 306, 160, 7, lerp(0.75, 0.72, kp), P["tank"])
        return img

    # 8. RESOLVE: both flex, stamp MITO
    def s_resolve(g):
        img = cast.gym_bg("sunrise").copy()
        flex = 0.9 + 0.1 * math.sin(g * 8)
        paste(img, cast.hero({"style": "ana", "arm_l": (95, 85), "arm_r": (95, 85), "bicep": flex, "mouth": "grin",
                              "eyes": "happy"}), 90, 342, scale=3)
        paste(img, cast.hero({"arm_l": (95, 85), "arm_r": (95, 85), "bicep": flex, "mouth": "grin",
                              "eyes": "happy"}), 190, 342, scale=3)
        fx.sparkles(img, 140, 230, g, n=12, radius=70)
        out = gfx.camera(img, 1.0)
        stamp_slam(out, VERDICT, g, c("resolve", "todos"), y=110)
        return out

    def s_cta(g):
        img = cast.end_bg(g)
        end_card(img, g, L("cta").start, c("cta", "esto"), VERDICT)
        return img

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("study", "study", s_study, "whip_left", 0.3, 0.2),
        ("compare", "compare", s_compare, "iris", 0.45, 0.25),
        ("resolve", "resolve", s_resolve, "dither", 0.35, 0.25),
        ("cta", "cta", s_cta, "pixelate", 0.3, 0.15),
    ])
    emph = {norm(w): col for w, col in [("mujeres", P["pink"]), ("hombres", P["tank"]), ("similar", P["gold"]),
            ("veintinueve", P["gold"]), ("relativo", P["gold"]), ("kilos", P["fog"]), ("proporción", P["green"]),
            ("todos", P["green"]), ("pesas", P["gold"])]}
    return Director(tl, scenes, SubStyle(y=352, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.3))
