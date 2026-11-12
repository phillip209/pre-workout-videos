"""Episode 16: "¿Necesitas 10 000 pasos al día?" — PARCIALMENTE CIERTO.

Source (checked 2026-11-12): Paluch AE et al. 2022, Lancet Public Health 7(3):e219-e228 —
meta-analysis of 15 cohorts, 47 471 adults; mortality risk fell with more steps until
~6000-8000/day (age >=60) and ~8000-10000/day (<60). Observational: association, not causation.
The paper itself notes 10 000 steps/day was widely promoted with little supporting evidence.
"""
from __future__ import annotations

import math
import os

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast
from engine.gfx import P, prog, ease_out, ease_io, ease_in, lerp, paste
from engine.kit import (blinking, label, pop_scale, paste_scaled, arrow, text_sprite, stamp_slam,
                        line_chart, badge, end_card, scenes_from, hook_camera, street_bg)
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "e16_pasos"
VERDICT = "PARCIALMENTE CIERTO"
BPM = 100
LEAD_IN = 0.15
TAIL = 2.2
NARRATION_FILE = "episodes/e16_pasos/narration.mp3"

LINES = [
    {"id": "hook", "text": "Diez mil pasos al día. ¿De dónde salió ese número?", "hold": 0.2},
    {"id": "famous", "text": "Lo repiten apps, relojes y entrenadores... pero tenía poca evidencia detrás.", "hold": 0.2},
    {"id": "study", "text": "Así que un equipo juntó quince estudios, con más de cuarenta y siete mil adultos."},
    {"id": "more", "text": "Resultado: más pasos se asociaron con menos riesgo de morir."},
    {"id": "twist", "text": "Pero hay un detalle: llega un punto en que la curva se aplana.", "hold": 0.3},
    {"id": "old", "text": "En mayores de sesenta, eso pasó entre seis mil y ocho mil pasos."},
    {"id": "young", "text": "Y en menores de sesenta, entre ocho mil y diez mil.", "hold": 0.3},
    {"id": "caveat", "text": "Ojo: son estudios observacionales. Muestran una relación, no prueban la causa."},
    {"id": "resolve", "text": "Diez mil no es un número mágico. Pero moverte más, sí cuenta.", "hold": 0.7},
    {"id": "cta", "text": "¿Cuántos pasos llevas hoy?"},
]
SPOKEN = ("Diez mil pasos al día. ¿De dónde salió ese número? Lo repiten apps, relojes y entrenadores... "
          "pero tenía poca evidencia detrás. Así que un equipo juntó quince estudios, con más de cuarenta y "
          "siete mil adultos. Resultado: más pasos se asociaron con menos riesgo de morir. Pero hay un detalle: "
          "llega un punto en que la curva se aplana. En mayores de sesenta, eso pasó entre seis mil y ocho mil "
          "pasos. Y en menores de sesenta, entre ocho mil y diez mil. Ojo: son estudios observacionales. "
          "Muestran una relación, no prueban la causa. <break time=\"0.8s\" /> Diez mil no es un número mágico. "
          "Pero moverte más, sí cuenta. ¿Cuántos pasos llevas hoy?")

VOICE = {"voice_id": os.environ.get("PW_VOICE_ID", "qRUgOhnxGASxirG4fKjv"), "model": "eleven_multilingual_v2",
         "settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True}}

TITLE = "¿Necesitas 10 000 pasos al día? PARCIALMENTE CIERTO #Shorts"
DESCRIPTION = (
    "¿Necesitas 10 000 pasos al día? PARCIALMENTE CIERTO. Un metaanálisis de 15 estudios con más de 47 000 "
    "adultos asoció más pasos con menor riesgo de muerte, con una meseta de 6 000-8 000 pasos en mayores de 60 "
    "y de 8 000-10 000 en menores de 60 (estudios observacionales: asociación, no causa).\n\n"
    "Fuentes: Paluch et al., Lancet Public Health, 2022.\nVoz: ElevenLabs.\n\n"
    "#fitness #pasos #caminar #mitosfitness #fitnesssinhumo #Shorts")
TAGS = ["10000 pasos", "caminar", "salud", "fitness", "fitness sin humo"]


def sound_cues(tl):
    c = tl.cue
    out = [(0.0, "impact", 0.8), (0.02, "whoosh", 0.6),
           (c("hook", "número"), "glitch", 0.6), (c("hook", "número") + 0.05, "pop", 0.7),
           (c("famous") - 0.2, "whoosh", 0.5),
           (c("famous", "apps"), "pop", 0.7), (c("famous", "relojes"), "pop", 0.7),
           (c("famous", "entrenadores"), "pop", 0.7), (c("famous", "poca"), "deflate", 0.6),
           (c("study") - 0.2, "whoosh", 0.5), (c("study", "quince"), "sparkle", 0.6),
           (c("study", "cuarenta"), "rise", 0.6),
           (c("more") - 0.2, "whoosh", 0.4), (c("more", "menos"), "ding", 0.5),
           (c("twist", "aplana"), "impact", 0.7),
           (c("old", "seis"), "blip", 0.8), (c("old", "ocho"), "blip", 0.8),
           (c("young", "ocho"), "blip", 0.8), (c("young", "diez"), "blip", 0.8),
           (c("caveat") - 0.2, "whoosh", 0.5), (c("caveat", "causa"), "glitch", 0.5),
           (c("resolve") - 0.25, "whoosh", 0.4), (c("resolve", "cuenta"), "stamp", 1.0),
           (c("resolve", "cuenta") + 0.05, "sparkle", 0.6),
           (c("cta") - 0.15, "pop", 0.6), (c("cta", "pasos"), "ding", 0.6)]
    st = c("hook")
    for i in range(int((c("famous") - st) / 0.3)):
        out.append((st + i * 0.3, "step", 0.35))
    st = c("resolve")
    for i in range(int((c("cta") - st) / 0.3)):
        out.append((st + i * 0.3, "step", 0.35))
    return out


def music_sections(tl):
    c = tl.cue
    return [(0.0, c("study") - 0.2, "tense"), (c("study") - 0.2, c("twist") - 0.1, "groove"),
            (c("twist") - 0.1, c("twist", "aplana"), "silence"),
            (c("twist", "aplana"), c("caveat") - 0.1, "mystery"),
            (c("caveat") - 0.1, c("resolve") - 0.2, "mystery"),
            (c("resolve") - 0.2, c("cta") - 0.1, "hope"), (c("cta") - 0.1, tl.total, "outro")]


def make_director(tl):
    c, L = tl.cue, tl.line

    def walker(g, speed=11, mood="smile"):
        return cast.hero({"walk": g * speed, "bob": 1 if (g * speed / 2) % 1 < 0.5 else 0, "mouth": mood,
                          "arm_l": (15 * math.sin(g * speed), 10), "arm_r": (-15 * math.sin(g * speed), 10),
                          "eyes": "blink" if blinking(g, 2.6) else "open"})

    # 1. HOOK: walking, watch counting towards 10 000
    def s_hook(g):
        img = street_bg(g, scroll=g * 70)
        paste(img, walker(g), 120, 330, scale=3)
        t_num = c("hook", "número")
        steps = int(lerp(0, 10000, ease_out(prog(g, 0, max(0.5, t_num - 0.1)))))
        froze = g > t_num
        txt = f"{steps:,}".replace(",", " ")
        w = cast.smartwatch(txt)
        if froze and (g * 8) % 1 < 0.5:
            w = gfx.flash(w, 0.35, P["white"])
        paste(img, w, 135, 70, scale=2, anchor="center")
        if froze:
            paste_scaled(img, text_sprite("?", P["gold"], scale=4), 220, 150 + math.sin(g * 5) * 3,
                         pop_scale(g, t_num, 0.25))
        out = hook_camera(img, g, cx=135, cy=220)
        if froze and g - t_num < 0.2:
            out = gfx.chroma_glitch(out, 6, g)
        return out

    # 2. FAMOUS: apps, watches, coaches all say 10 000; evidence meter empty
    def s_famous(g):
        img = cast.end_bg(g)
        items = [("APPS", c("famous", "apps"), 55), ("RELOJES", c("famous", "relojes"), 135),
                 ("COACHES", c("famous", "entrenadores"), 215)]
        t_poca = c("famous", "poca")
        dim = ease_out(prog(g, t_poca, 0.4))
        for i, (name, tt, x) in enumerate(items):
            s = pop_scale(g, tt, 0.25)
            if s <= 0:
                continue
            card = gfx.new(70, 92)
            d = ImageDraw.Draw(card)
            d.rounded_rectangle([1, 1, 68, 90], radius=6, fill=P["deep"], outline=P["lav"])
            if i == 0:  # phone
                d.rounded_rectangle([22, 8, 48, 52], radius=3, fill=P["ink"])
                d.rectangle([25, 12, 45, 46], fill=P["green_d"])
            elif i == 1:
                card.alpha_composite(cast.smartwatch("10K"), (11, 6))
            else:  # whistle coach
                card.alpha_composite(cast.hero({"mouth": "o", "arm_r": (100, 120)}).crop((8, 0, 48, 50)), (15, 4))
            from engine.font import draw_text
            draw_text(card, "10 000", 35, 60, color=P["gold"], align="center", outline=P["ink"])
            draw_text(card, name, 35, 74, color=P["fog"], align="center")
            if dim > 0:
                card = gfx.darken(card, 0.55 * dim)
            paste_scaled(img, card, x, 170 + math.sin(g * 3 + i) * 2, s)
        # evidence meter
        if g > t_poca:
            d = ImageDraw.Draw(img)
            label(img, "EVIDENCIA", 135, 248, color=P["white"], scale=2)
            d.rectangle([60, 276, 210, 290], outline=P["white"], width=2)
            fill = int(150 * 0.12 * ease_out(prog(g, t_poca, 0.6)))
            d.rectangle([62, 278, 62 + fill, 288], fill=P["red"])
            if (g * 3) % 1 < 0.6:
                label(img, "POCA", 135, 298, color=P["red_l"])
        return img

    # 3. STUDY: 15 studies + 47 000 adults crowd
    def s_study(g):
        img = cast.lab_bg(g)
        t15, t47 = c("study", "quince"), c("study", "cuarenta")
        n = int(lerp(1, 15, ease_out(prog(g, t15 - 0.3, 0.8))))
        paste(img, cast.doc_stack(n), 75, 250, scale=2, anchor="mid_bottom")
        if g > t15:
            label(img, f"{n} ESTUDIOS", 75, 262, color=P["gold"], scale=2)
        if g > t47 - 0.2:
            k = ease_out(prog(g, t47 - 0.2, 1.4))
            per = cast.tiny_person()
            cols = [P["fog"], P["sky"], P["pink"], P["gold"], P["green"]]
            count = int(k * 120)
            for i in range(count):
                x = 150 + (i % 12) * 9
                y = 120 + (i // 12) * 13
                p_ = cast.tiny_person(cols[i % 5]) if i % 7 else per
                img.alpha_composite(p_, (x, y))
            num = int(lerp(0, 47471, k))
            label(img, f"{num:,}".replace(",", " "), 205, 262, color=P["gold"], scale=2)
            label(img, "ADULTOS", 205, 284, color=P["fog"])
        return img

    # 4. CHART: risk vs steps, flattens; age plateaus
    def s_chart(g):
        img = cast.end_bg(g)
        box = (40, 70, 240, 280)
        d = ImageDraw.Draw(img)
        label(img, "RIESGO", 40, 52, color=P["fog"], center=False)
        label(img, "PASOS AL DÍA", 140, 300, color=P["fog"], center=True)
        for i, xv in enumerate((2, 4, 6, 8, 10, 12)):
            x = box[0] + (xv / 12) * (box[2] - box[0])
            d.line([x, box[3], x, box[3] + 3], fill=P["fog"])
            label(img, f"{xv}K", x, box[3] + 6, color=P["steel"])
        t_more, t_apl = L("more").start, c("twist", "aplana")
        t_old, t_young = L("old").start, L("young").start
        # two curves: >=60 (lav) flattens ~7k, <60 (gold) flattens ~9k
        old = [(x / 12, 0.92 * math.exp(-max(0, min(x, 7) - 1) / 2.4) + 0.06) for x in range(1, 13)]
        young = [(x / 12, 0.92 * math.exp(-max(0, min(x, 9) - 1) / 3.0) + 0.05) for x in range(1, 13)]
        first = ease_io(prog(g, t_more, 2.2)) * 0.55
        full = ease_io(prog(g, t_apl - 0.4, 0.9))
        pr = max(first, 0.55 + 0.45 * full) if g > t_apl - 0.4 else first
        if g < t_old:
            line_chart(img, box, young, pr, color=P["gold"])
        if g > t_apl:
            k = (g * 2) % 1 < 0.7
            if k and g < t_old:
                label(img, "MESETA", 200, 220, color=P["gold"], scale=2)
        if g >= t_old:
            ko = ease_out(prog(g, t_old, 0.6))
            line_chart(img, box, old, 1.0, color=P["lav"], dot=False)
            x6, x8 = box[0] + 6 / 12 * 200, box[0] + 8 / 12 * 200
            gfx.dither_fill(img, (x6, 90, x8, box[3] - 1), P["night"], P["lav"], 0.35 * ko)
            line_chart(img, box, old, 1.0, color=P["lav"], dot=False)
            label(img, "+60 AÑOS", (x6 + x8) / 2, 76, color=P["lav"])
        if g >= t_young:
            ky = ease_out(prog(g, t_young, 0.6))
            line_chart(img, box, young, 1.0, color=P["gold"], dot=False)
            x8, x10 = box[0] + 8 / 12 * 200, box[0] + 10 / 12 * 200
            gfx.dither_fill(img, (x8 + 1, 110, x10, box[3] - 1), P["night"], P["gold_d"], 0.35 * ky)
            line_chart(img, box, young, 1.0, color=P["gold"], dot=False)
            label(img, "-60 AÑOS", (x8 + x10) / 2 + 6, 96, color=P["gold"])
        if g > c("more", "menos"):
            arrow(img, 28, 150, up=False, color=P["green"], size=6)
        return gfx.camera(img, lerp(1.0, 1.08, prog(g, t_old, 3)), 150, 180)

    # 5. CAVEAT: correlation is not causation
    def s_caveat(g):
        img = cast.end_bg(g)
        t_rel, t_ca = c("caveat", "relación"), c("caveat", "causa")
        s1 = pop_scale(g, L("caveat").start, 0.3)
        paste_scaled(img, cast.shoe(), 70, 160, s1 * 3)
        heart = gfx.new(16, 14)
        hd = ImageDraw.Draw(heart)
        hd.ellipse([0, 0, 8, 8], fill=P["red"]); hd.ellipse([7, 0, 15, 8], fill=P["red"])
        hd.polygon([(0, 5), (15, 5), (8, 13)], fill=P["red"])
        paste_scaled(img, gfx.outline(heart), 200, 160, s1 * 3)
        if g > t_rel:
            d = ImageDraw.Draw(img)
            k = ease_out(prog(g, t_rel, 0.5))
            for x in range(100, int(lerp(100, 170, k)), 6):
                d.rectangle([x, 160, x + 2, 162], fill=P["fog"])
            label(img, "RELACIÓN", 135, 130, color=P["fog"])
        if g > t_ca:
            paste_scaled(img, text_sprite("≠ CAUSA", P["red_l"], scale=2), 135, 220, pop_scale(g, t_ca, 0.25))
        # magnifier sweep
        mx = 135 + math.sin(g * 1.6) * 70
        d = ImageDraw.Draw(img)
        d.ellipse([mx - 18, 280, mx + 18, 316], outline=P["steel_l"], width=3)
        d.line([mx + 13, 311, mx + 26, 326], fill=P["wood"], width=4)
        label(img, "OBSERVACIONALES", 135, 92, color=P["lav"])
        return img

    # 6. RESOLVE: sunrise walk + stamp
    def s_resolve(g):
        img = street_bg(g, scroll=g * 55, tod="sunrise")
        paste(img, walker(g, speed=10, mood="grin"), 120, 330, scale=3)
        steps = int(lerp(6200, 8300, prog(g, L("resolve").start, 3.5)))
        paste(img, cast.smartwatch(f"{steps:,}".replace(",", " ")), 210, 230, scale=1, anchor="center")
        out = gfx.camera(img, 1.0)
        stamp_slam(out, VERDICT, g, c("resolve", "cuenta"), y=110)
        return out

    def s_cta(g):
        img = cast.end_bg(g)
        end_card(img, g, L("cta").start, c("cta", "pasos"), VERDICT)
        return img

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("famous", "famous", s_famous, "whip_left", 0.3, 0.2),
        ("study", "study", s_study, "pixelate", 0.3, 0.2),
        ("chart", "more", s_chart, "iris", 0.45, 0.25),
        ("caveat", "caveat", s_caveat, "dither", 0.3, 0.2),
        ("resolve", "resolve", s_resolve, "whip_left", 0.3, 0.25),
        ("cta", "cta", s_cta, "pixelate", 0.3, 0.15),
    ])
    emph = {norm(w): col for w, col in [("diez", P["gold"]), ("mil", P["gold"]), ("evidencia", P["red_l"]),
            ("quince", P["gold"]), ("aplana", P["gold"]), ("sesenta", P["lav"]), ("causa", P["red_l"]),
            ("mágico", P["lav"]), ("cuenta", P["green"]), ("observacionales", P["lav"])]}
    return Director(tl, scenes, SubStyle(y=352, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.3))
