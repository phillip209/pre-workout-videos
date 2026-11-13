"""Episode 20: "¿El músculo pesa más que la grasa?" — ENGAÑOSO.

Sources (checked 2026-11-13): muscle density ~1.06 g/cm3 (Mendez & Keys 1960; Ward & Lieber 2005,
J Biomech), adipose/fat ~0.90 g/mL (Fidanza, Keys & Anderson 1953). A kilo is a kilo; muscle takes
less volume.
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

SLUG = "e20_musculo_pesa"
VERDICT = "ENGAÑOSO"
BPM = 108
LEAD_IN = 0.15
TAIL = 2.2
NARRATION_FILE = "episodes/e20_musculo_pesa/narration.mp3"

LINES = [
    {"id": "hook", "text": "¿Qué pesa más: un kilo de músculo... o un kilo de grasa?", "hold": 0.3},
    {"id": "beat", "text": "Exacto. Lo mismo: un kilo.", "hold": 0.2},
    {"id": "q", "text": "Entonces, ¿por qué todo el mundo dice que el músculo pesa más?"},
    {"id": "dense", "text": "Porque el músculo es más denso. Ocupa menos espacio."},
    {"id": "liter", "text": "Un litro de músculo pesa un kilo y sesenta gramos... y un litro de grasa, unos novecientos gramos.", "hold": 0.3},
    {"id": "people", "text": "Por eso dos personas pueden pesar lo mismo... y verse completamente distintas."},
    {"id": "scale", "text": "Y por eso la báscula no lo cuenta todo."},
    {"id": "resolve", "text": "El músculo no pesa más. Solo ocupa menos.", "hold": 0.7},
    {"id": "cta", "text": "¿A quién le vas a ganar esta discusión?"},
]

TITLE = "¿El músculo pesa más que la grasa? ENGAÑOSO #Shorts"
DESCRIPTION = (
    "¿El músculo pesa más que la grasa? ENGAÑOSO. Un kilo es un kilo: lo que cambia es el volumen. El músculo es "
    "más denso (≈1,06 kg por litro) que la grasa (≈0,90 kg por litro), así que ocupa menos espacio. Por eso la "
    "báscula no lo cuenta todo.\n\nFuentes: Ward & Lieber, J Biomech, 2005 · Fidanza, Keys & Anderson, J Appl "
    "Physiol, 1953.\nVoz: ElevenLabs.\n\n#fitness #musculo #grasa #mitosfitness #fitnesssinhumo #Shorts")
TAGS = ["músculo pesa más que la grasa", "densidad", "báscula", "mitos fitness", "fitness sin humo"]


def sound_cues(tl):
    c = tl.cue
    out = [(0.0, "impact", 0.8), (0.02, "whoosh", 0.6),
           (c("hook", "músculo"), "thud", 0.7), (c("hook", "grasa"), "boing", 0.8),
           (c("beat", "exacto"), "ding", 0.8), (c("beat", "kilo"), "impact", 0.6),
           (c("q") - 0.2, "whoosh", 0.4), (c("q", "mundo"), "pop", 0.6), (c("q", "dice"), "pop", 0.6),
           (c("q", "pesa"), "pop", 0.6),
           (c("dense") - 0.2, "whoosh", 0.5), (c("dense", "denso"), "deflate", 0.6), (c("dense", "espacio"), "inflate", 0.5),
           (c("liter", "litro"), "blip", 0.7), (c("liter", "sesenta"), "thud", 0.7),
           (c("liter", "novecientos"), "boing", 0.6),
           (c("people") - 0.2, "whoosh", 0.5), (c("people", "distintas"), "sparkle", 0.6),
           (c("scale", "báscula"), "glitch", 0.6),
           (c("resolve") - 0.2, "whoosh", 0.4), (c("resolve", "menos"), "stamp", 1.0),
           (c("resolve", "menos") + 0.05, "sparkle", 0.6),
           (c("cta") - 0.15, "pop", 0.6), (c("cta", "discusión"), "ding", 0.6)]
    return out


def music_sections(tl):
    c = tl.cue
    return [(0.0, c("beat", "exacto"), "tense"), (c("beat", "exacto"), c("dense") - 0.1, "groove"),
            (c("dense") - 0.1, c("people") - 0.1, "mystery"), (c("people") - 0.1, c("resolve") - 0.2, "groove"),
            (c("resolve") - 0.2, c("cta") - 0.1, "hope"), (c("cta") - 0.1, tl.total, "outro")]


def balance(img, cx, cy, tilt, left=None, right=None, lab_l="", lab_r=""):
    """Big pixel balance scale. tilt > 0 = left side down."""
    d = ImageDraw.Draw(img)
    d.rectangle([cx - 4, cy, cx + 4, cy + 120], fill=P["steel_d"])
    d.rectangle([cx - 30, cy + 118, cx + 30, cy + 126], fill=P["steel"])
    d.polygon([(cx - 8, cy - 6), (cx + 8, cy - 6), (cx, cy + 4)], fill=P["gold"])
    a = tilt * 0.25
    lx, ly = cx - 90 * math.cos(a), cy + 90 * math.sin(a)
    rx, ry = cx + 90 * math.cos(a), cy - 90 * math.sin(a)
    d.line([lx, ly, rx, ry], fill=P["gold"], width=4)
    for (px, py, obj, lab) in ((lx, ly, left, lab_l), (rx, ry, right, lab_r)):
        d.line([px, py, px - 22, py + 40], fill=P["fog"])
        d.line([px, py, px + 22, py + 40], fill=P["fog"])
        d.rectangle([px - 30, py + 40, px + 30, py + 44], fill=P["gold_d"])
        if obj is not None:
            paste(img, obj, px, py + 40, scale=1, anchor="mid_bottom")
        if lab:
            label(img, lab, px, py + 50, color=P["white"], scale=2)


def make_director(tl):
    c, L = tl.cue, tl.line

    def muscle_block(scale=1.0, mood="happy", g=0.0):
        return cast.muscle_fiber(int(30 * scale), int(22 * scale), mood=mood, nuclei=3, t=g)

    def fat_blob(r=18, mood="happy", g=0.0):
        return cast.fat_cell(r, mood=mood, t=g, wobble=0.4)

    # 1-2. HOOK quiz: balance wobbles, then perfectly level -> "ba dum tss"
    def s_quiz(g):
        img = cast.end_bg(g)
        d = ImageDraw.Draw(img)
        # stage lights
        for i, x in enumerate((40, 135, 230)):
            on = (int(g * 4) + i) % 3 != 0
            d.polygon([(x - 6, 0), (x + 6, 0), (x + 40, 300), (x - 40, 300)],
                      fill=(60, 50, 90) if on else (36, 30, 58))
        label(img, "QUIZ FITNESS", 135, 24, color=P["gold"], scale=2)
        t_ex = c("beat", "exacto")
        settled = g > t_ex
        tilt = 0.0 if settled else math.sin(g * 5) * 0.8
        m = muscle_block(1.2, "proud" if settled else "happy", g)
        f = fat_blob(20, "smug" if settled else "happy", g)
        balance(img, 135, 120, tilt, left=m, right=f, lab_l="1 KG" if g > c("hook", "músculo") else "",
                lab_r="1 KG" if g > c("hook", "grasa") else "")
        host = cast.hero({"arm_r": (100, 60) if not settled else (150, 140), "mouth": "o" if not settled else "flat",
                          "eyes": "closed" if settled and g < t_ex + 1.2 else "open"})
        paste(img, host, 135, 345, scale=2)
        if settled:
            paste_scaled(img, text_sprite("=", P["green"], scale=4), 135, 96, pop_scale(g, t_ex))
            if g > c("beat", "kilo"):
                paste_scaled(img, text_sprite("1 KG = 1 KG", P["white"], scale=2), 135, 70, pop_scale(g, c("beat", "kilo")))
        out = hook_camera(img, g, cx=135, cy=200)
        if settled and g - t_ex < 0.4:
            out = gfx.camera(out, 1.0, 135, 240, shake=3 * (1 - (g - t_ex) / 0.4), t=g)
        return out

    # 3. Q: crowd shouting the myth
    def s_crowd(g):
        img = cast.gym_bg("night").copy()
        st = L("q").start
        for i in range(24):
            x = 15 + (i % 12) * 22
            y = 300 + (i // 12) * 22
            hop = abs(math.sin(g * 8 + i)) * 4
            img.alpha_composite(cast.tiny_person([P["fog"], P["sky"], P["pink"], P["gold"]][i % 4]).resize((10, 18), 0),
                                (int(x), int(y - hop)))
        shouts = [("¡EL MÚSCULO PESA MÁS!", c("q", "mundo"), 135, 110), ("¡PESA MÁS!", c("q", "dice"), 70, 170),
                  ("¡TODOS LO SABEN!", c("q", "pesa"), 195, 220)]
        for i, (txt, tt, x, y) in enumerate(shouts):
            s = pop_scale(g, tt, 0.2)
            paste_scaled(img, text_sprite(txt, P["white"], scale=1), x, y + math.sin(g * 9 + i) * 2, s * 2)
        paste(img, cast.hero({"mouth": "flat", "eyes": "sad", "arm_l": (30, 120)}), 135, 300, scale=2)
        return gfx.camera(img, lerp(1.0, 1.1, prog(g, st, 3)), 135, 220, shake=1.0, t=g)

    # 4-5. DENSITY: same kilo, different size; then a litre of each on the scale
    def s_dense(g):
        img = cast.lab_bg(g)
        d = ImageDraw.Draw(img)
        t_den, t_esp = c("dense", "denso"), c("dense", "espacio")
        t_lit = L("liter").start
        if g < t_lit - 0.1:
            k = ease_out(prog(g, t_den - 0.2, 0.6))
            ke = ease_back(prog(g, t_esp - 0.2, 0.6))
            paste(img, muscle_block(lerp(1.6, 1.2, k), "proud", g), 75, 200, scale=2, anchor="center")
            paste(img, fat_blob(int(lerp(20, 28, ke)), "happy", g), 195, 200, scale=2, anchor="center")
            label(img, "1 KG", 75, 250, color=P["muscle_l"], scale=2)
            label(img, "1 KG", 195, 268, color=P["fat"], scale=2)
            if g > t_esp:
                label(img, "MISMO PESO · DISTINTO TAMAÑO", 135, 80, color=P["gold"])
            return img
        # litre jars on the balance
        t60, t900 = c("liter", "sesenta"), c("liter", "novecientos")
        tilt = lerp(0, 0.9, ease_out(prog(g, t60 - 0.2, 0.8)))
        jar = gfx.new(44, 56)
        jd = ImageDraw.Draw(jar)
        jd.rectangle([2, 4, 41, 55], outline=P["fog"], width=2)
        jm = jar.copy()
        ImageDraw.Draw(jm).rectangle([4, 10, 39, 53], fill=P["muscle"])
        jf = jar.copy()
        ImageDraw.Draw(jf).rectangle([4, 10, 39, 53], fill=P["fat"])
        balance(img, 135, 120, tilt, left=gfx.outline(jm), right=gfx.outline(jf),
                lab_l="1,06 KG" if g > t60 else "1 L", lab_r="0,90 KG" if g > t900 else "1 L")
        label(img, "1 LITRO DE CADA UNO", 135, 40, color=P["white"], scale=2)
        return img

    # 6-7. PEOPLE + SCALE: same weight, different look; bathroom scale glitches
    def s_people(g):
        img = cast.gym_bg("night").copy()
        t_dis = c("people", "distintas")
        t_bas = c("scale", "báscula")
        scan = (g * 120) % 260
        a = cast.hero({"belly": 0.9, "bicep": 0.2, "mouth": "smile"})
        b = cast.hero({"belly": 0.0, "bicep": 0.95, "mouth": "grin", "arm_l": (95, 85), "arm_r": (95, 85)})
        paste(img, a, 80, 330, scale=3)
        paste(img, b, 195, 330, scale=3)
        for x in (80, 195):
            paste(img, cast.digital_clock("70 KG", P["green"]), x, 145, scale=1, anchor="center")
        if g < t_bas:
            d = ImageDraw.Draw(img)
            d.line([0, 120 + scan, W, 120 + scan], fill=P["sky"])
        if g > t_dis:
            fx.sparkles(img, 195, 230, g, n=8, radius=40)
        out = img
        if g > t_bas:
            k = ease_out(prog(g, t_bas, 0.4))
            sc = gfx.new(90, 70)
            sd = ImageDraw.Draw(sc)
            sd.rounded_rectangle([1, 1, 88, 68], radius=8, fill=P["white"], outline=P["steel_d"], width=2)
            sd.rectangle([20, 10, 70, 30], fill=P["ink"])
            from engine.font import draw_text
            draw_text(sc, "70 ?" if (g * 6) % 1 < 0.5 else "70", 45, 14, color=P["red"], align="center")
            out = gfx.darken(out, 0.4 * k)
            paste_scaled(out, gfx.outline(sc), 135, 230, k * 2)
            if g - t_bas < 0.25:
                out = gfx.chroma_glitch(out, 6, g)
        return out

    def s_resolve(g):
        img = cast.gym_bg("sunrise").copy()
        paste(img, cast.hero({"arm_l": (95, 85), "arm_r": (95, 85), "bicep": 0.95, "mouth": "grin", "eyes": "happy"}),
              135, 342, scale=3)
        paste(img, muscle_block(1.0, "proud", g), 50, 250, scale=2, anchor="center")
        paste(img, fat_blob(14, "shock", g), 225, 250, scale=2, anchor="center")
        out = gfx.camera(img, 1.0)
        stamp_slam(out, VERDICT, g, c("resolve", "menos"), y=110)
        return out

    def s_cta(g):
        img = cast.end_bg(g)
        end_card(img, g, L("cta").start, c("cta", "discusión"), VERDICT)
        return img

    scenes = scenes_from(tl, [
        ("quiz", "hook", s_quiz, "cut", 0.3, 0),
        ("crowd", "q", s_crowd, "whip_left", 0.3, 0.2),
        ("dense", "dense", s_dense, "iris", 0.45, 0.25),
        ("people", "people", s_people, "dither", 0.3, 0.2),
        ("resolve", "resolve", s_resolve, "whip_left", 0.3, 0.25),
        ("cta", "cta", s_cta, "pixelate", 0.3, 0.15),
    ])
    emph = {norm(w): col for w, col in [("músculo", P["muscle_l"]), ("grasa", P["fat"]), ("kilo", P["gold"]),
            ("denso", P["muscle_l"]), ("espacio", P["fat"]), ("báscula", P["sky"]), ("menos", P["green"]),
            ("distintas", P["gold"])]}
    return Director(tl, scenes, SubStyle(y=352, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.3))
