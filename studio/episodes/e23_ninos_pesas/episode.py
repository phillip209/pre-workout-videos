"""Episode 23: "¿Las pesas frenan el crecimiento de los niños?" — MITO.

Source (checked 2026-11-13): Lloyd RS, Faigenbaum AD, Stone MH et al. 2014, Br J Sports Med 48:498-505 —
international consensus position statement on youth resistance training: safe and beneficial when
properly supervised; childhood/adolescence are key periods for bone development; emphasises
qualified supervision, technique and appropriate progression.
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast
from engine.gfx import P, prog, ease_out, ease_io, ease_back, lerp, paste
from engine.kit import (blinking, label, pop_scale, paste_scaled, arrow, text_sprite, stamp_slam,
                        end_card, scenes_from, hook_camera)
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "e23_ninos_pesas"
VERDICT = "MITO"
BPM = 104
LEAD_IN = 0.15
TAIL = 2.2
NARRATION_FILE = "episodes/e23_ninos_pesas/narration.mp3"

LINES = [
    {"id": "hook", "text": "No dejes que el niño levante pesas... ¡se va a quedar chiquito!"},
    {"id": "q", "text": "¿Te lo dijeron alguna vez?", "hold": 0.2},
    {"id": "consensus", "text": "En dos mil catorce, expertos de todo el mundo publicaron un consenso sobre el entrenamiento de fuerza en niños y adolescentes."},
    {"id": "result", "text": "Y concluyeron que, bien supervisado, es seguro... y beneficioso.", "hold": 0.2},
    {"id": "bones", "text": "De hecho, la infancia y la adolescencia son etapas clave para construir huesos fuertes."},
    {"id": "key", "text": "La clave: buena técnica, supervisión, y cargas adecuadas para su edad."},
    {"id": "resolve", "text": "Las pesas no frenan el crecimiento.", "hold": 0.7},
    {"id": "cta", "text": "Mándaselo a ese tío que siempre lo dice."},
]

TITLE = "¿Las pesas frenan el crecimiento de los niños? MITO #Shorts"
DESCRIPTION = (
    "¿Las pesas frenan el crecimiento de los niños? MITO. El consenso internacional de 2014 sobre entrenamiento "
    "de fuerza en jóvenes concluyó que, bien supervisado, es seguro y beneficioso, y que la infancia y la "
    "adolescencia son etapas clave para desarrollar huesos fuertes. La clave: técnica, supervisión y cargas "
    "adecuadas.\n\nFuentes: Lloyd et al., Br J Sports Med, 2014.\nVoz: ElevenLabs.\n\n"
    "#fitness #niños #pesas #mitosfitness #fitnesssinhumo #Shorts")
TAGS = ["niños y pesas", "crecimiento", "entrenamiento de fuerza", "mitos fitness", "fitness sin humo"]


def sound_cues(tl):
    c = tl.cue
    return [(0.0, "impact", 0.8), (0.02, "whoosh", 0.6), (c("hook", "pesas"), "clank", 0.6),
            (c("hook", "chiquito"), "deflate", 0.8), (c("hook", "chiquito") + 0.5, "boing", 0.7),
            (c("q", "alguna"), "pop", 0.6),
            (c("consensus") - 0.2, "whoosh", 0.5), (c("consensus", "expertos"), "sparkle", 0.5),
            (c("consensus", "consenso"), "stamp", 0.6),
            (c("result", "seguro"), "ding", 0.7), (c("result", "beneficioso"), "ding", 0.7),
            (c("bones") - 0.2, "whoosh", 0.4), (c("bones", "huesos"), "rise", 0.6),
            (c("key", "técnica"), "pop", 0.7), (c("key", "supervisión"), "pop", 0.7), (c("key", "cargas"), "pop", 0.7),
            (c("resolve") - 0.2, "whoosh", 0.4), (c("resolve", "crecimiento"), "stamp", 1.0),
            (c("resolve", "crecimiento") + 0.05, "sparkle", 0.6),
            (c("cta") - 0.15, "pop", 0.6), (c("cta", "dice"), "ding", 0.6)]


def music_sections(tl):
    c = tl.cue
    return [(0.0, c("consensus") - 0.2, "tense"), (c("consensus") - 0.2, c("result") - 0.1, "mystery"),
            (c("result") - 0.1, c("resolve") - 0.2, "groove"),
            (c("resolve") - 0.2, c("cta") - 0.1, "hope"), (c("cta") - 0.1, tl.total, "outro")]


def make_director(tl):
    c, L = tl.cue, tl.line

    def kid(pose=None):
        p = {"mouth": "smile"}
        p.update(pose or {})
        return cast.hero(p)

    def bubble(text):
        from engine.font import draw_text, text_width
        w = text_width(text, 1) + 14
        b = gfx.new(w, 30)
        d = ImageDraw.Draw(b)
        d.rounded_rectangle([1, 1, w - 2, 20], radius=5, fill=P["white"])
        d.polygon([(10, 20), (18, 20), (6, 28)], fill=P["white"])
        draw_text(b, text, 7, 7, color=P["ink"])
        return gfx.outline(b)

    def s_hook(g):
        img = cast.gym_bg("night").copy()
        t_ch = c("hook", "chiquito")
        shrink = ease_out(prog(g, t_ch, 0.5))
        uncle = cast.hero({"belly": 0.9, "mouth": "o", "arm_r": (100, 20), "eyes": "open"})
        paste(img, uncle, 70, 342, scale=3)
        paste_scaled(img, bubble("¡SE VA A QUEDAR CHIQUITO!"), 120, 120, pop_scale(g, 0.2, 0.3) * 1.3)
        k = kid({"holding": "dumbbell", "arm_r": (5, 10 + 130 * math.sin(g * 6) ** 2),
                 "eyes": "wide" if g > t_ch else "open", "mouth": "o" if g > t_ch else "smile"})
        s = lerp(2.0, 1.0, shrink) if g < t_ch + 0.5 else lerp(1.0, 2.0, ease_back(prog(g, t_ch + 0.5, 0.4)))
        paste(img, k, 200, 342, scale=s)
        if g > t_ch + 0.5:
            paste_scaled(img, text_sprite("¿?", P["gold"], scale=3), 215, 180, pop_scale(g, t_ch + 0.5))
        out = hook_camera(img, g, cx=150, cy=240)
        if 0 < g - t_ch < 0.2:
            out = gfx.chroma_glitch(out, 6, g)
        return out

    def s_globe(g):
        img = cast.end_bg(g)
        d = ImageDraw.Draw(img)
        t_exp, t_con = c("consensus", "expertos"), c("consensus", "consenso")
        t_res = L("result").start
        cx, cy, r = 135, 170, 70
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=P["blue"])
        rot = g * 20
        for i in range(6):
            a = (i * 60 + rot) % 360
            x = cx + math.cos(math.radians(a)) * r * 0.6
            if math.sin(math.radians(a)) > -0.2:
                d.ellipse([x - 18, cy - 30 + i * 8, x + 12, cy - 6 + i * 8], fill=P["green_d"])
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 300, fill=P["sky"])
        if g > t_exp:
            for i in range(8):
                a = i / 8 * math.tau + g * 0.5
                pk = pop_scale(g, t_exp + i * 0.08, 0.2)
                px, py = cx + math.cos(a) * (r + 22), cy + math.sin(a) * (r + 22)
                paste_scaled(img, cast.tiny_person([P["fog"], P["pink"], P["gold"], P["sky"]][i % 4]), px, py, pk * 2)
        label(img, "2014", 135, 40, color=P["gold"], scale=3)
        if g > t_con:
            doc = gfx.new(90, 60)
            dd = ImageDraw.Draw(doc)
            dd.rectangle([1, 1, 88, 58], fill=P["white"])
            from engine.font import draw_text
            draw_text(doc, "CONSENSO", 45, 8, color=P["ink"], align="center")
            draw_text(doc, "FUERZA EN", 45, 22, color=P["steel_d"], align="center")
            draw_text(doc, "JÓVENES", 45, 34, color=P["steel_d"], align="center")
            paste_scaled(img, gfx.outline(doc), 135, 290, pop_scale(g, t_con) * 1.5)
        if g > t_res:
            t_seg, t_ben = c("result", "seguro"), c("result", "beneficioso")
            img = gfx.darken(img, 0.5)
            for i, (txt, tt, y) in enumerate((("SEGURO", t_seg, 140), ("BENEFICIOSO", t_ben, 200))):
                s = pop_scale(g, tt, 0.25)
                if s > 0:
                    badge = gfx.new(200, 40)
                    bd = ImageDraw.Draw(badge)
                    bd.rounded_rectangle([1, 1, 198, 38], radius=6, fill=P["green_d"], outline=P["green"], width=2)
                    bd.line([14, 20, 22, 28, 36, 10], fill=P["white"], width=4)
                    from engine.font import draw_text
                    draw_text(badge, txt, 115, 12, color=P["white"], scale=2, align="center")
                    paste_scaled(img, badge, 135, y, s)
            label(img, "BIEN SUPERVISADO", 135, 250, color=P["gold"])
        return img

    def bone(thick=1.0, glow=0.0):
        S = gfx.new(90, 34)
        d = ImageDraw.Draw(S)
        t = int(4 + 6 * thick)
        col = gfx.lerpc(P["cream"], P["white"], glow)
        d.rectangle([16, 17 - t // 2, 74, 17 + t // 2], fill=col)
        for x in (12, 78):
            d.ellipse([x - 9, 4, x + 3, 16], fill=col)
            d.ellipse([x - 9, 18, x + 3, 30], fill=col)
        return gfx.outline(S)

    def s_bones(g):
        img = cast.tissue_bg(g)
        t_hue, t_key = c("bones", "huesos"), L("key").start
        if g < t_key - 0.1:
            k = ease_out(prog(g, t_hue - 0.3, 1.2))
            paste(img, bone(lerp(0.3, 1.0, k), k), 135, 190, scale=2, anchor="center")
            label(img, "INFANCIA · ADOLESCENCIA", 135, 100, color=P["fog"])
            if g > t_hue:
                label(img, "HUESOS FUERTES", 135, 250, color=P["white"], scale=2)
                fx.sparkles(img, 135, 190, g, n=10, radius=70)
            return img
        img = cast.gym_bg("night").copy()
        items = [("TÉCNICA", c("key", "técnica"), 55), ("SUPERVISIÓN", c("key", "supervisión"), 135),
                 ("BUENA CARGA", c("key", "cargas"), 215)]
        for i, (txt, tt, x) in enumerate(items):
            s = pop_scale(g, tt, 0.25)
            if s <= 0:
                continue
            if i == 0:
                spr = kid({"arm_l": (95, 85), "arm_r": (95, 85)})
            elif i == 1:
                spr = cast.hero({"mouth": "smile", "arm_r": (100, 120)})
            else:
                spr = cast.dumbbell()
            paste_scaled(img, spr, x, 220, s * (1.5 if i < 2 else 2), anchor="mid_bottom")
            label(img, txt, x, 236 + (12 if i == 1 else 0), color=P["gold"])
        return img

    def s_resolve(g):
        img = cast.gym_bg("sunrise").copy()
        d = ImageDraw.Draw(img)
        # height chart on the wall
        d.rectangle([20, 150, 34, 330], fill=P["cream"])
        for y in range(160, 330, 15):
            d.line([20, y, 30, y], fill=P["wood_d"])
        st = L("resolve").start
        grow = ease_out(prog(g, st, 1.8))
        k = kid({"holding": "dumbbell", "arm_r": (5, 10 + 120 * math.sin(g * 6) ** 2), "mouth": "grin",
                 "eyes": "happy"})
        paste(img, k, 90, 342, scale=lerp(1.5, 2.5, grow))
        mark_y = int(lerp(260, 190, grow))
        d.rectangle([18, mark_y, 40, mark_y + 2], fill=P["red"])
        out = gfx.camera(img, 1.0)
        stamp_slam(out, VERDICT, g, c("resolve", "crecimiento"), x=170, y=110)
        return out

    def s_cta(g):
        img = cast.end_bg(g)
        end_card(img, g, L("cta").start, c("cta", "dice"), VERDICT)
        return img

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("globe", "consensus", s_globe, "iris", 0.45, 0.25),
        ("bones", "bones", s_bones, "dither", 0.3, 0.2),
        ("resolve", "resolve", s_resolve, "whip_left", 0.3, 0.25),
        ("cta", "cta", s_cta, "pixelate", 0.3, 0.15),
    ])
    emph = {norm(w): col for w, col in [("chiquito", P["gold"]), ("consenso", P["gold"]), ("seguro", P["green"]),
            ("beneficioso", P["green"]), ("huesos", P["white"]), ("técnica", P["gold"]),
            ("supervisión", P["gold"]), ("crecimiento", P["green"]), ("tío", P["gold"])]}
    return Director(tl, scenes, SubStyle(y=352, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.3))
