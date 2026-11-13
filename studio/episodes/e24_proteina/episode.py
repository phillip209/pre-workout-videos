"""Episode 24: "¿Más proteína = más músculo, sin límite?" — MITO.

Source: Morton RW et al. 2018, Br J Sports Med 52:376-384 — meta-analysis of 49 RCTs (1 863
participants) doing resistance training: protein supplementation increased gains in lean mass, but
the benefit plateaued beyond ~1.6 g/kg/day of total protein intake (95% CI 1.03-2.20).
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast
from engine.gfx import P, prog, ease_out, ease_io, ease_back, lerp, paste
from engine.kit import (blinking, label, pop_scale, paste_scaled, arrow, text_sprite, stamp_slam, bar,
                        line_chart, end_card, scenes_from, hook_camera)
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "e24_proteina"
VERDICT = "MITO"
BPM = 104
LEAD_IN = 0.15
TAIL = 2.2
NARRATION_FILE = "episodes/e24_proteina/narration.mp3"

LINES = [
    {"id": "hook", "text": "Si un batido de proteína es bueno... ¿tres batidos son tres veces mejor?", "hold": 0.2},
    {"id": "myth", "text": "Muchos creen que más proteína es igual a más músculo. Sin límite.", "hold": 0.5},
    {"id": "study", "text": "Un análisis de cuarenta y nueve estudios, con casi dos mil personas que entrenaban fuerza, lo puso a prueba."},
    {"id": "helped", "text": "La proteína extra sí ayudó a ganar músculo... hasta cierto punto."},
    {"id": "plateau", "text": "Por encima de unos uno coma seis gramos por kilo de peso al día, el beneficio dejó de crecer.", "hold": 0.3},
    {"id": "example", "text": "Para alguien de setenta kilos, eso es más o menos ciento doce gramos al día."},
    {"id": "resolve", "text": "Más proteína no es músculo infinito. El que manda es el entrenamiento.", "hold": 0.7},
    {"id": "cta", "text": "¿Cuánta proteína comes tú?"},
]

TITLE = "¿Más proteína = más músculo sin límite? MITO #Shorts"
DESCRIPTION = (
    "¿Más proteína es más músculo, sin límite? MITO. Un metaanálisis de 49 ensayos con 1 863 personas que "
    "entrenaban fuerza encontró que la proteína extra ayudó a ganar masa magra, pero el beneficio dejó de crecer "
    "por encima de ~1,6 g por kg de peso al día (≈112 g para 70 kg).\n\n"
    "Fuentes: Morton et al., Br J Sports Med, 2018.\nVoz: ElevenLabs.\n\n"
    "#fitness #proteina #musculo #mitosfitness #fitnesssinhumo #Shorts")
TAGS = ["proteína", "batido de proteína", "músculo", "mitos fitness", "fitness sin humo"]


def sound_cues(tl):
    c = tl.cue
    return [(0.0, "impact", 0.8), (0.02, "whoosh", 0.6), (c("hook", "bueno"), "pop", 0.6),
            (c("hook", "tres"), "pop", 0.6), (c("hook", "tres") + 0.15, "pop", 0.6), (c("hook", "tres") + 0.3, "pop", 0.6),
            (c("hook", "mejor"), "boing", 0.7),
            (c("myth") - 0.2, "whoosh", 0.4), (c("myth", "límite"), "rise", 0.7),
            (c("study") - 0.2, "whoosh", 0.5), (c("study", "cuarenta"), "sparkle", 0.5), (c("study", "dos"), "rise", 0.5),
            (c("helped", "ayudó"), "ding", 0.6), (c("helped", "punto"), "thud", 0.7),
            (c("plateau", "uno"), "blip", 0.8), (c("plateau", "dejó"), "impact", 0.7),
            (c("example", "setenta"), "blip", 0.7), (c("example", "ciento"), "ding", 0.7),
            (c("resolve") - 0.2, "whoosh", 0.4), (c("resolve", "infinito"), "stamp", 1.0),
            (c("resolve", "entrenamiento"), "clank", 0.6),
            (c("cta") - 0.15, "pop", 0.6), (c("cta", "tú"), "ding", 0.6)]


def music_sections(tl):
    c = tl.cue
    return [(0.0, c("study") - 0.2, "groove"), (c("study") - 0.2, c("plateau") - 0.05, "mystery"),
            (c("plateau") - 0.05, c("plateau", "dejó"), "silence"),
            (c("plateau", "dejó"), c("resolve") - 0.2, "groove"),
            (c("resolve") - 0.2, c("cta") - 0.1, "hope"), (c("cta") - 0.1, tl.total, "outro")]


def shaker(color=P["sky"], face=True, mood="happy"):
    S = gfx.new(22, 36)
    d = ImageDraw.Draw(S)
    d.rectangle([5, 1, 16, 6], fill=P["ink"])
    d.polygon([(3, 7), (18, 7), (16, 34), (5, 34)], fill=color)
    d.rectangle([5, 14, 16, 20], fill=P["white"])
    if face:
        d.point((8, 24), fill=P["ink"]); d.point((13, 24), fill=P["ink"])
        if mood == "happy":
            d.line([8, 28, 10, 29, 11, 29, 13, 28], fill=P["ink"])
        else:
            d.line([8, 29, 13, 28], fill=P["ink"])
    return gfx.outline(S)


def make_director(tl):
    c, L = tl.cue, tl.line

    def s_hook(g):
        img = cast.gym_bg("night").copy()
        t3, t_mej = c("hook", "tres"), c("hook", "mejor")
        paste(img, cast.hero({"mouth": "grin" if g < t_mej else "o", "arm_l": (120, 60), "arm_r": (120, 60),
                              "eyes": "happy" if g < t3 else "wide"}), 135, 342, scale=3)
        n = 1 if g < t3 else min(3, 1 + int((g - t3) / 0.15) + 1)
        cols = [P["sky"], P["pink"], P["gold"]]
        for i in range(n):
            # juggling arc
            a = g * 6 + i * 2.1
            x = 135 + math.cos(a) * 45
            y = 150 - abs(math.sin(a)) * 40
            paste(img, shaker(cols[i]), x, y, scale=2, anchor="center")
        if g > t_mej:
            paste_scaled(img, text_sprite("×3 = ×3?", P["gold"], scale=2), 135, 70, pop_scale(g, t_mej))
        return hook_camera(img, g, cx=135, cy=220)

    def s_myth(g):
        img = cast.end_bg(g)
        t_lim = c("myth", "límite")
        st = L("myth").start
        k = prog(g, st, 3.0)
        scoops = 1 + int(k * 8)
        for i in range(scoops):
            paste(img, shaker([P["sky"], P["pink"], P["gold"]][i % 3], face=False), 30 + i * 26, 300, scale=1)
        h = int(lerp(20, 240, ease_io(k)))
        fib_t = lerp(10, 30, ease_io(k))
        fib = cast.muscle_fiber(100, fib_t, mood="proud", nuclei=6, t=g)
        paste(img, fib, 135, 190, scale=2, anchor="center")
        if g > t_lim:
            label(img, "¿SIN LÍMITE?", 135, 50, color=P["gold"], scale=2)
            arrow(img, 240, 120, up=True, color=P["gold"], size=10)
        return img

    def s_lab(g):
        img = cast.lab_bg(g)
        t49, t2k = c("study", "cuarenta"), c("study", "dos")
        n = int(lerp(1, 49, ease_out(prog(g, t49 - 0.2, 0.9))))
        paste(img, cast.doc_stack(min(n, 18)), 80, 300, scale=2, anchor="mid_bottom")
        label(img, f"{n} ESTUDIOS", 80, 60, color=P["gold"], scale=2)
        if g > t2k - 0.2:
            k = ease_out(prog(g, t2k - 0.2, 0.9))
            for i in range(int(k * 70)):
                img.alpha_composite(cast.tiny_person([P["fog"], P["sky"], P["pink"]][i % 3]),
                                    (160 + (i % 10) * 9, 140 + (i // 10) * 13))
            label(img, f"{int(k * 1863):,}".replace(",", " ") + " PERSONAS", 205, 240, color=P["gold"])
        return img

    def s_chart(g):
        img = cast.end_bg(g)
        d = ImageDraw.Draw(img)
        box = (40, 80, 240, 270)
        label(img, "MÚSCULO GANADO", 40, 62, color=P["muscle_l"], center=False)
        label(img, "PROTEÍNA (G/KG/DÍA)", 140, 290, color=P["fog"])
        for xv in (0.8, 1.2, 1.6, 2.0, 2.4):
            x = box[0] + (xv - 0.6) / 2.0 * (box[2] - box[0])
            d.line([x, box[3], x, box[3] + 3], fill=P["fog"])
            label(img, f"{xv:.1f}".replace(".", ","), x, box[3] + 6, color=P["steel"])
        pts = []
        for i in range(21):
            xv = 0.6 + i * 0.1
            yv = min(xv, 1.6) - 0.6
            pts.append(((xv - 0.6) / 2.0, 0.1 + yv * 0.8))
        st = L("helped").start
        t_pt, t_dej = c("helped", "punto"), c("plateau", "dejó")
        pr = ease_io(prog(g, st, max(0.5, t_pt - st))) * 0.5
        if g > t_pt:
            pr = 0.5 + 0.5 * ease_io(prog(g, t_pt, max(0.5, t_dej - t_pt + 0.4)))
        line_chart(img, box, pts, pr, color=P["gold"])
        t16 = c("plateau", "uno")
        if g > t16:
            x16 = box[0] + 1.0 / 2.0 * (box[2] - box[0])
            for y in range(box[1], box[3], 6):
                d.line([x16, y, x16, y + 3], fill=P["green"])
            label(img, "1,6", x16, box[1] - 12, color=P["green"], scale=2)
        if g > t_dej:
            label(img, "MESETA", 200, 120, color=P["gold"], scale=2)
        t_ex = L("example").start
        if g > t_ex:
            img = gfx.darken(img, 0.55)
            t70, t112 = c("example", "setenta"), c("example", "ciento")
            card = gfx.new(220, 70)
            cd = ImageDraw.Draw(card)
            cd.rounded_rectangle([1, 1, 218, 68], radius=8, fill=P["ink"], outline=P["gold"], width=2)
            from engine.font import draw_text
            draw_text(card, "70 KG × 1,6", 110, 10, color=P["white"], scale=2, align="center")
            if g > t112:
                draw_text(card, "≈ 112 G/DÍA", 110, 40, color=P["gold"], scale=2, align="center")
            paste_scaled(img, card, 135, 180, pop_scale(g, t70, 0.25))
        return img

    def s_resolve(g):
        img = cast.gym_bg("sunrise").copy()
        t_inf, t_ent = c("resolve", "infinito"), c("resolve", "entrenamiento")
        lifting = g > t_ent - 0.2
        rep = math.sin(g * 6) ** 2
        paste(img, cast.hero({"arm_r": (5, 10 + 140 * rep) if lifting else (40, 20), "holding": "dumbbell" if lifting else None,
                              "mouth": "grin", "bicep": 0.9, "eyes": "happy"}), 150, 342, scale=3)
        # two extra shakers pushed aside, one stays
        push = ease_out(prog(g, L("resolve").start, 0.6))
        paste(img, shaker(P["sky"]), 60, 330, scale=2)
        paste(img, shaker(P["pink"], mood="sad"), lerp(80, 290, push), 330, scale=2)
        paste(img, shaker(P["gold"], mood="sad"), lerp(100, 320, push), 330, scale=2)
        out = gfx.camera(img, 1.0)
        stamp_slam(out, VERDICT, g, t_inf, y=110)
        return out

    def s_cta(g):
        img = cast.end_bg(g)
        end_card(img, g, L("cta").start, c("cta", "tú"), VERDICT)
        return img

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("myth", "myth", s_myth, "whip_left", 0.3, 0.2),
        ("lab", "study", s_lab, "pixelate", 0.3, 0.2),
        ("chart", "helped", s_chart, "iris", 0.45, 0.25),
        ("resolve", "resolve", s_resolve, "dither", 0.35, 0.25),
        ("cta", "cta", s_cta, "pixelate", 0.3, 0.15),
    ])
    emph = {norm(w): col for w, col in [("proteína", P["sky"]), ("tres", P["gold"]), ("límite", P["gold"]),
            ("músculo", P["muscle_l"]), ("punto", P["gold"]), ("seis", P["green"]), ("ciento", P["gold"]),
            ("doce", P["gold"]), ("infinito", P["lav"]), ("entrenamiento", P["green"])]}
    return Director(tl, scenes, SubStyle(y=352, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.3))
