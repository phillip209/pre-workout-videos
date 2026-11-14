"""B01 v2 · "90 días sin azúcar: lo más raro le pasó a su lengua" — cinematic rebuild of b01.

Story: Leo goes 90 days without ADDED sugar (fruit allowed). Conflict = "el Antojo", a candy monster
(metaphor for cravings). Open loop in the hook ("it happened to his tongue") is paid off at day 90.

Facts (checked 2026-11-14):
- Day 3: Falbe J et al., Appetite 2019;133:130-137 — 25 overweight adolescents stopping sugary drinks for
  3 days reported more cravings and headache, less motivation/contentment (small, preliminary).
- Liver: Schwarz JM et al., Gastroenterology 2017;153:743-752 — 41 children with obesity, sugar swapped
  for starch at equal calories for 9 days: median liver fat 7.2 % -> 3.8 %.
- Taste: Wise PM et al., Am J Clin Nutr 2016;103:50-60 — low-sugar diet: by month 3 puddings rated ~40 %
  sweeter vs controls (intensity, not liking); after returning to sugar, perception reverted quickly.
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast, hud, organs
from engine import cast_plus as cp
from engine.gfx import P, prog, ease_out, ease_io, ease_back, ease_in, lerp, paste, clamp
from engine.kit import (label, pop_scale, paste_scaled, text_sprite, scenes_from, impact_text, count_text, xray,
                        blinking)
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "b01v2_azucar"
BPM = 112
LEAD_IN = 0.08
TAIL = 1.4
NARRATION_FILE = "episodes/b01v2_azucar/narration.mp3"

LINES = [
    {"id": "hook", "text": "Leo pasó noventa días sin azúcar añadido."},
    {"id": "hook2", "text": "Y lo más raro... no le pasó a su cuerpo."},
    {"id": "hook3", "text": "Le pasó a su lengua.", "hold": 0.1},
    {"id": "d1", "text": "Día uno. Cero dulces, cero refrescos. La fruta, sí."},
    {"id": "d3", "text": "Día tres: llega el monstruo. Antojos, dolor de cabeza, cero ánimo."},
    {"id": "turn", "text": "Pero por dentro, algo ya estaba cambiando."},
    {"id": "d10", "text": "En niños con obesidad, cambiar el azúcar por almidón redujo casi a la mitad la grasa del hígado."},
    {"id": "d10b", "text": "En nueve días."},
    {"id": "still", "text": "Y el monstruo... seguía ahí."},
    {"id": "d90", "text": "Día noventa. Leo prueba el mismo postre de siempre..."},
    {"id": "reveal", "text": "y le sabe un cuarenta por ciento más dulce."},
    {"id": "reveal2", "text": "¡Su lengua se recalibró!", "hold": 0.1},
    {"id": "twist", "text": "Pero ojo: en el estudio, quien volvió al azúcar, lo perdió rápido."},
    {"id": "cta", "text": "¿Tú aguantarías el día tres?"},
]

TITLE = "90 días sin azúcar: lo más raro le pasó a su lengua 👅 #Shorts"
DESCRIPTION = (
    "Leo pasó 90 días sin azúcar añadido (la fruta sí). Lo más raro no le pasó al cuerpo: le pasó a la "
    "lengua.\n\n"
    "Fuentes:\n"
    "· Día 3 — Falbe et al., Appetite, 2019: adolescentes que dejaron las bebidas azucaradas 3 días "
    "reportaron más antojos y dolor de cabeza y menos ánimo (estudio pequeño y preliminar).\n"
    "· Hígado — Schwarz et al., Gastroenterology, 2017: niños con obesidad; cambiar azúcar por almidón con "
    "las mismas calorías durante 9 días bajó la grasa del hígado de 7,2 % a 3,8 % (mediana).\n"
    "· Lengua — Wise et al., Am J Clin Nutr, 2016: con una dieta baja en azúcar, a los 3 meses un postre "
    "se percibió ~40 % más dulce; al volver al azúcar, el efecto se revirtió rápido.\n"
    "Los resultados son de estudios y pueden variar entre personas. Contenido educativo, no es consejo "
    "médico.\nVoz: ElevenLabs.\n\n"
    "#azucar #salud #quelepasaatucuerpo #fitness #Shorts")
TAGS = ["dejar el azúcar", "90 días sin azúcar", "qué le pasa a tu cuerpo", "antojos de azúcar",
        "hígado graso", "salud"]


def leo(pose=None, t=0.0):
    p = {"mouth": "smile", "bob": math.sin(t * 2.4) * 0.8, "eyes": "blink" if blinking(t, 3.1) else "open"}
    p.update(pose or {})
    if blinking(t, 3.1) and p.get("eyes") in ("open",):
        p["eyes"] = "blink"
    return cast.hero(p)


# ---------------------------------------------------------------- audio
def sound_cues(tl):
    c, L = tl.cue, tl.line
    cues = [(0.0, "impact", 0.9), (0.0, "whoosh", 0.6),
            (c("hook", "noventa"), "ding", 0.6), (c("hook", "azúcar"), "pop", 0.5),
            (c("hook2", "raro"), "glitch", 0.4), (c("hook2", "cuerpo"), "blip", 0.6),
            (c("hook3", "lengua") - 0.05, "boing", 0.8), (c("hook3", "lengua"), "impact", 0.8),
            (L("d1").start - 0.25, "rewind", 0.9),
            (c("d1", "dulces"), "thud", 0.6), (c("d1", "refrescos"), "thud", 0.6), (c("d1", "fruta"), "ding", 0.7),
            (c("d1", "sí"), "chomp", 0.7),
            (c("d3", "tres") - 0.1, "tick", 0.5), (c("d3", "monstruo") - 0.1, "growl", 1.0),
            (c("d3", "monstruo"), "impact", 0.7),
            (c("d3", "antojos"), "bar_up", 0.8), (c("d3", "cabeza"), "heartbeat", 0.8), (c("d3", "ánimo"), "bar_down", 0.8),
            (L("turn").start, "scan", 0.9),
            (L("d10").start, "ding", 0.5), (c("d10", "hígado"), "babble", 0.7), (c("d10", "mitad"), "deflate", 0.8),
            (c("d10", "mitad") + 0.15, "sparkle", 0.6), (c("d10b", "nueve"), "stamp", 0.8),
            (c("still", "monstruo"), "growl", 0.6), (c("still", "ahí"), "glitch", 0.5),
            (c("d90", "noventa"), "ding", 0.8), (c("d90", "postre"), "whoosh", 0.4),
            (c("reveal", "dulce") - 0.04, "impact", 1.0), (c("reveal", "dulce"), "sparkle", 0.8),
            (c("reveal", "cuarenta"), "rise", 0.5),
            (c("reveal2", "recalibró"), "ding", 0.8), (c("reveal2", "recalibró") + 0.1, "babble", 0.6),
            (c("twist", "ojo"), "alarm", 0.4), (c("twist", "ojo") + 0.1, "growl", 0.5),
            (c("twist", "rápido"), "bar_down", 0.8),
            (L("cta").start - 0.1, "pop", 0.6), (c("cta", "tres"), "ding", 0.7)]
    w0, w1 = c("still", "ahí") + 0.2, c("d90", "noventa")
    k = w0
    while k < w1 - 0.1:
        cues.append((k, "tick", 0.3))
        k += 0.08
    return cues


def music_sections(tl):
    c, L = tl.cue, tl.line
    t_dul = c("reveal", "dulce")
    return [(0.0, L("d1").start - 0.25, "pulse"),
            (L("d1").start, L("d3").start, "drive"),
            (L("d3").start, L("turn").start - 0.1, "low"),
            (L("turn").start, L("still").start, "drive"),
            (L("still").start, L("d90").start, "pulse"),
            (L("d90").start, t_dul - 0.6, "mystery"),
            (t_dul - 0.6, t_dul, "silence"),
            (t_dul, L("twist").start, "triumph"),
            (L("twist").start, tl.total, "pulse")]


# ---------------------------------------------------------------- picture
def make_director(tl):
    c, L = tl.cue, tl.line
    t_rw = L("d1").start
    t_d3 = c("d3", "tres")
    t_d10 = L("d10").start
    t_d90 = c("d90", "noventa")
    # counter: 90 during the hook (the end state), rewinds to 1, then 3, 10, races to 90
    day_keys = [(0.0, 90), (t_rw - 0.3, 90), (t_rw + 0.35, 1, 0.6), (t_d3, 3, 0.35), (t_d10 + 0.1, 10, 0.45),
                (t_d90, 90, max(0.5, t_d90 - c("still", "ahí") - 0.2))]
    flashes = [c("hook", "noventa"), t_rw + 0.35, t_d3, t_d10 + 0.1, t_d90]

    def hud_layer(img, g):
        day = hud.count_day(g, day_keys)
        fl = 0.0
        for tt in flashes:
            if 0 <= g - tt < 0.4:
                fl = 1 - (g - tt) / 0.4
        layer = gfx.new()
        hud.day_counter(layer, day, 90, g, flash=fl)
        img.alpha_composite(layer)

    def source(img, text):
        label(img, text, 135, 58, color=P["fog"])

    # ---------------- S1 HOOK: close-up in the sweets aisle, open loop "his tongue"
    def s_hook(g):
        t_90, t_cue = c("hook", "noventa"), c("hook2", "cuerpo")
        t_len = c("hook3", "lengua")
        img = cp.candy_aisle_bg(g, scroll=g * 6)
        look = math.sin(g * 1.3) * 0.6 if g < t_cue else (-1 if g < t_len else 0)
        mood = "neutral" if g < t_cue else ("sly" if g < t_len - 0.1 else "shock")
        tongue = ease_back(prog(g, t_len - 0.1, 0.3)) if g > t_len - 0.1 else 0
        face = cp.leo_face(mood, g, blink=blinking(g, 2.7, 1.3), look=look, tongue_out=tongue,
                           sweat=g > t_len)
        paste(img, face, 135, 345, scale=2.0)
        # body icon "?" next to him at 'cuerpo' (it did NOT happen to his body)
        if t_cue - 0.1 < g < t_len:
            s = pop_scale(g, t_cue - 0.1)
            body = cast.hero({"mouth": "flat", "eyes": "open"})
            paste_scaled(img, body, 236, 250, s * 1.5)
            d = ImageDraw.Draw(img)
            if g > t_cue + 0.15:
                d.line([214, 200, 258, 262], fill=P["ink"], width=7)
                d.line([258, 200, 214, 262], fill=P["ink"], width=7)
                d.line([214, 200, 258, 262], fill=P["red"], width=4)
                d.line([258, 200, 214, 262], fill=P["red"], width=4)
        # camera: punch-in on frame 1, slow push, snap-zoom to the mouth on 'lengua'
        z = lerp(1.25, 1.0, ease_out(prog(g, 0, 0.45))) + 0.04 * prog(g, 0.5, 5.0)
        cy = 240
        if g > t_len - 0.1:
            k = ease_out(prog(g, t_len - 0.1, 0.25))
            z += 0.35 * k
            cy = lerp(240, 300, k)
        out = gfx.camera(img, z, 135, cy, shake=2.5 if 0 <= g - t_len < 0.25 else 0, t=g)
        if g - 0 < 0.3:
            fx.speed_lines(out, 135, 240, g, n=30)
        if 0 <= g - t_len < 0.15:
            out = gfx.chroma_glitch(out, 6, g)
        impact_text(out, "90 DÍAS SIN AZÚCAR", 135, 98, g, t_90, color=P["pink"], scale=3, out_t=t_cue - 0.2)
        if g > t_cue - 0.1 and g < t_len:
            impact_text(out, "¿Y SU CUERPO?", 135, 98, g, t_cue - 0.1, color=P["white"], scale=3)
        impact_text(out, "¿SU LENGUA?", 135, 100, g, t_len, color=P["pink"], scale=5)
        hud_layer(out, g)
        return out

    # ---------------- S2 DAY 1: rewind, then a walk through the aisle saying no
    def s_d1(g):
        st = L("d1").start
        t_dul, t_ref, t_fru, t_si = c("d1", "dulces"), c("d1", "refrescos"), c("d1", "fruta"), c("d1", "sí")
        walk_end = t_fru - 0.15
        scroll = 30 + 140 * ease_io(prog(g, st, max(0.5, walk_end - st)))
        img = cp.candy_aisle_bg(g, scroll=scroll)
        walking = g < walk_end
        grab = ease_back(prog(g, t_si - 0.25, 0.3))
        pose = {"walk": g * 12 if walking else None, "mouth": "grit" if g < t_fru else "grin",
                "arm_l": (20 * math.sin(g * 12), 30) if walking else (10, 10),
                "arm_r": (-20 * math.sin(g * 12), 30) if walking else (lerp(10, 150, grab), lerp(10, 30, grab))}
        paste(img, leo(pose, g), 120, 336, scale=2.6)
        # items pop above the shelf: donut X, soda X, apple ✓
        for (tt, spr, x, ok) in ((t_dul, cp.donut(), 60, False), (t_ref, cp.soda(), 135, False),
                                 (t_fru, cp.apple(), 210, True)):
            s = pop_scale(g, tt)
            if s <= 0:
                continue
            yy = 120 + math.sin(g * 4 + x) * 3
            if ok and g > t_si - 0.25:   # apple flies to Leo's hand
                k = ease_in(prog(g, t_si - 0.25, 0.3))
                if k >= 1:
                    continue
                paste_scaled(img, spr, lerp(x, 150, k), lerp(yy, 190, k), s * 2.2)
                continue
            paste_scaled(img, spr, x, yy, s * 2.2)
            d = ImageDraw.Draw(img)
            if not ok and g > tt + 0.12:
                d.line([x - 18, yy - 18, x + 18, yy + 18], fill=P["ink"], width=7)
                d.line([x + 18, yy - 18, x - 18, yy + 18], fill=P["ink"], width=7)
                d.line([x - 18, yy - 18, x + 18, yy + 18], fill=P["red"], width=4)
                d.line([x + 18, yy - 18, x - 18, yy + 18], fill=P["red"], width=4)
            if ok and g > tt + 0.12:
                d.line([x - 14, yy + 2, x - 4, yy + 12, x + 16, yy - 14], fill=P["ink"], width=7)
                d.line([x - 14, yy + 2, x - 4, yy + 12, x + 16, yy - 14], fill=P["green"], width=4)
        if g > t_dul - 0.1:
            impact_text(img, "CERO AZÚCAR AÑADIDO", 135, 172, g, t_dul - 0.1, color=P["white"], scale=2,
                        out_t=t_fru - 0.1)
        if g > t_fru:
            impact_text(img, "LA FRUTA SÍ", 135, 172, g, t_fru, color=P["green"], scale=3)
        out = img
        rw = 1 - prog(g, st - 0.3, 0.75)
        if rw > 0:
            out = cp.vhs_rewind(out, rw, g)
        hud_layer(out, g)
        return out

    # ---------------- S3 DAY 3: the Craving monster rises in the bedroom
    def s_d3(g):
        t_mon, t_ant, t_cab, t_ani = c("d3", "monstruo"), c("d3", "antojos"), c("d3", "cabeza"), c("d3", "ánimo")
        img = cast.bedroom_bg(g, dawn=0.0)
        img = gfx.darken(img, 0.35)
        grow = ease_back(prog(g, t_mon - 0.35, 0.5))
        if grow > 0:
            mood = "roar" if g < t_mon + 0.7 else "sly"
            m = cp.antojo(mood, g, glow=0.7 + 0.3 * math.sin(g * 6))
            # shadow on the wall first, then the monster
            sh = m.copy()
            sh.putdata([(10, 6, 20, a // 2) for (_, _, _, a) in sh.getdata()])
            paste(img, sh, 190, 150, scale=2.6 * grow, anchor="center")
            paste(img, m, 180 + math.sin(g * 2) * 4, 175, scale=1.9 * grow, anchor="center")
        scared = g > t_mon
        paste(img, leo({"mouth": "o" if g < t_ant else "sad", "eyes": "wide" if scared and g < t_ant else
                        ("sad" if scared else "open"), "sweat": scared, "droop": 0.5 if g > t_ani else 0,
                        "arm_l": (40, 90) if scared and g < t_ant else (5, 5), "arm_r": (5, 5),
                        "look": 1 if scared else 0}, g), 80, 336, scale=2.5)
        if g > t_cab - 0.15:
            paste_scaled(img, organs.brain("pain", g), 70, 150 + math.sin(g * 9) * 2, pop_scale(g, t_cab - 0.15) * 1.25)
        hud.stat_bar(img, 12, 70, 110, "ANTOJOS", lerp(0.3, 0.95, ease_out(prog(g, t_ant, 0.5))), P["red"], g,
                     delta=1, appear=prog(g, t_ant - 0.2, 0.3))
        hud.stat_bar(img, 140, 70, 110, "ÁNIMO", lerp(0.8, 0.15, ease_out(prog(g, t_ani, 0.5))), P["sky"], g,
                     delta=-1, appear=prog(g, t_ani - 0.2, 0.3))
        if t_mon - 0.1 < g < t_ant:
            impact_text(img, "EL ANTOJO", 135, 108, g, t_mon - 0.05, color=P["pink"], scale=4)
        source(img, "FALBE 2019 · JÓVENES SIN REFRESCOS 3 DÍAS")
        z = 1.0 + 0.05 * prog(g, L("d3").start, 3.0)
        out = gfx.camera(img, z, 135, 230, shake=3 if 0 <= g - t_mon < 0.45 else (1.5 if 0 <= g - t_cab < 0.4 else 0), t=g)
        hud_layer(out, g)
        return out

    # ---------------- S4 TURN: x-ray into the body
    def inside_bg(g):
        return cast.tissue_bg(g, hue="pink")

    def s_turn(g):
        st = L("turn").start
        outside = gfx.darken(cast.bedroom_bg(g, dawn=0.2), 0.2)
        paste(outside, leo({"mouth": "flat", "eyes": "open"}, g), 135, 336, scale=2.6)
        inner = inside_bg(g)
        paste(inner, organs.liver(1.0, "sad", g), 135, 215 + math.sin(g * 3) * 3, scale=2.6, anchor="center")
        label(inner, "SU HÍGADO", 135, 285, color=P["white"], scale=2)
        out = xray(outside, inner, 140, 255, prog(g, st, 1.0))
        if g > c("turn", "cambiando"):
            impact_text(out, "¿QUÉ CAMBIA?", 135, 108, g, c("turn", "cambiando"), color=P["gold"], scale=4)
        hud_layer(out, g)
        return out

    # ---------------- S5 LIVER (day 10)
    def s_liver(g):
        t_nin, t_hig, t_mit = c("d10", "niños"), c("d10", "hígado"), c("d10", "mitad")
        t_9 = c("d10b", "nueve")
        img = inside_bg(g)
        k = ease_io(prog(g, t_mit - 0.4, 1.0))
        fat = lerp(1.0, 0.5, k)
        mood = "sad" if k < 0.5 else "happy"
        paste(img, organs.liver(fat, mood, g), 135, 215 + math.sin(g * 3) * 3, scale=2.6 - 0.25 * k, anchor="center")
        if k > 0.1:
            for i in range(5):
                fk = (g * 0.8 + i * 0.2) % 1
                paste(img, cast.fat_cell(5, mood="sad", t=g), 85 + i * 25, 215 - fk * 95, scale=1, anchor="center")
        pct = count_text(7.2, 3.8, g, t_mit - 0.3, 1.0) + " %"
        if g > t_nin:
            label(img, "GRASA EN EL HÍGADO", 135, 74, color=P["fat_l"])
            impact_text(img, pct, 135, 116, g, t_nin, color=P["fat"] if k < 0.9 else P["green"], scale=5,
                        out_t=t_9 - 0.2)
        if g > t_mit:
            paste_scaled(img, organs.speech("¡QUÉ ALIVIO!"), 205, 158, pop_scale(g, t_mit + 0.2) * 1.4)
            fx.sparkles(img, 135, 215, g, n=10, radius=70, color=P["green"])
        if g > t_9:
            impact_text(img, "9 DÍAS", 135, 108, g, t_9, color=P["green"], scale=6)
        source(img, "NIÑOS CON OBESIDAD · SCHWARZ 2017")
        hud_layer(img, g)
        return img

    # ---------------- S6 STILL THERE: weeks fly by, the monster follows
    def s_still(g):
        st, t_ahi = L("still").start, c("still", "ahí")
        scroll = (g - st) * 70
        from engine.kit import street_bg
        img = street_bg(g, scroll=scroll, tod="sunrise")
        paste(img, leo({"walk": g * 12, "mouth": "smile", "arm_l": (20 * math.sin(g * 12), 30),
                        "arm_r": (-20 * math.sin(g * 12), 30), "look": -1 if g > t_ahi else 0}, g), 160, 330, scale=2.4)
        # monster lurking behind (left), peeks out on 'ahí'
        peek = ease_back(prog(g, t_ahi - 0.1, 0.3))
        mx = lerp(-40, 60, peek) if g < t_ahi + 1.2 else lerp(60, -60, ease_in(prog(g, t_ahi + 1.2, 0.4)))
        paste(img, cp.antojo("wink" if g > t_ahi + 0.3 else "sly", g, glow=1.0), mx, 230, scale=1.3, anchor="center")
        for i in range(8):  # calendar pages blowing past
            ph = ((g - st) * 1.6 + i * 0.13) % 1
            if g > t_ahi:
                paste(img, cp.calendar_page(10 + i * 10), W + 20 - ph * (W + 60), 70 + (i * 37) % 200,
                      scale=1.2, anchor="center")
        if g > c("still", "monstruo") - 0.1:
            impact_text(img, "SEGUÍA AHÍ", 135, 108, g, t_ahi, color=P["pink"], scale=4)
        hud_layer(img, g)
        return img

    # ---------------- S7 DAY 90: same dessert as always (slow-mo approach)
    def s_d90(g):
        st, t_pos = L("d90").start, c("d90", "postre")
        img = cp.kitchen_bg(g, warm=True)
        k = ease_io(prog(g, t_pos - 0.2, 1.2))
        paste(img, leo({"arm_r": (lerp(30, 120, k), lerp(40, 70, k)), "mouth": "o" if k > 0.6 else "smile",
                        "eyes": "open"}, g), 135, 336, scale=2.6)
        paste(img, cp.pudding(), 85, 300, scale=2)
        paste(img, cp.spoon(), lerp(120, 150, k), lerp(270, 200, k), scale=2, anchor="center")
        if g > t_pos - 0.2:
            impact_text(img, "EL MISMO POSTRE", 135, 108, g, t_pos - 0.2, color=P["fat_l"], scale=3)
        z = 1.0 + 0.4 * ease_in(prog(g, t_pos, 1.3))
        out = gfx.camera(img, z, 140, 215)
        hud_layer(out, g)
        return out

    # ---------------- S8 REVEAL: the tongue (pays off the hook)
    def s_reveal(g):
        st, t_cua, t_dul = L("reveal").start, c("reveal", "cuarenta"), c("reveal", "dulce")
        t_rec = c("reveal2", "recalibró")
        img = cp.kitchen_bg(g, warm=True)
        hit = g > t_dul - 0.05
        face = cp.leo_face("taste" if not hit else "shock", g, tongue_out=ease_back(prog(g, t_dul - 0.05, 0.3)) if hit else 0,
                           sweat=False)
        paste(img, face, 95, 336, scale=2.0)
        val = lerp(0.35, 0.95, ease_back(prog(g, t_cua, 1.2))) if g > t_cua else 0.35
        paste(img, cp.gauge(val, g), 205, 300, scale=1.15, anchor="center")
        if hit:
            impact_text(img, "+40 %", 135, 112, g, t_dul - 0.05, color=P["pink"], scale=7)
            if g < t_rec - 0.1:
                label(img, "MÁS DULCE", 135, 154, color=P["white"], scale=2)
            fx.sparkles(img, 95, 280, g, n=10, radius=60, color=P["pink"])
        if g > t_rec - 0.1:
            paste_scaled(img, organs.tongue("happy", g), 222, 205, pop_scale(g, t_rec - 0.1) * 1.1)
            paste_scaled(img, organs.speech("¡RECALIBRADA!", tail="right"), 180, 150, pop_scale(g, t_rec) * 1.2)
        source(img, "WISE 2016 · DIETA BAJA EN AZÚCAR, 3 MESES")
        out = gfx.camera(img, 1.0 + (0.08 if 0 <= g - t_dul < 0.2 else 0), 135, 240,
                         shake=3 if 0 <= g - t_dul < 0.3 else 0, t=g)
        if 0 <= g - t_dul < 0.08:
            out = gfx.flash(out, 0.6, (255, 220, 240))
        hud_layer(out, g)
        return out

    # ---------------- S9 TWIST + CTA: the monster is back -> loop to frame 1
    def s_end(g):
        t_ojo, t_rap, t_cta = c("twist", "ojo"), c("twist", "rápido"), L("cta").start
        img = cp.candy_aisle_bg(g, scroll=g * 6)
        mood = "sly" if g < t_cta else "neutral"
        face = cp.leo_face("shock" if t_ojo < g < t_rap + 0.3 else mood, g, blink=blinking(g, 2.7, 1.3),
                           look=-1 if t_ojo < g < t_cta else 0)
        slide = ease_io(prog(g, t_ojo - 0.1, 0.3)) * (1 - ease_io(prog(g, t_cta, 0.35)))
        paste(img, face, 135 + 22 * slide, 345, scale=2.0)
        if g < t_cta + 0.4:
            pk = ease_back(prog(g, t_ojo - 0.1, 0.35))
            out_k = ease_in(prog(g, t_cta, 0.35))
            mx = lerp(-60, 55, pk) - 140 * out_k
            paste(img, cp.antojo("wink", g, glow=1.0), mx, 168, scale=1.3, anchor="center")
        if t_ojo < g < t_cta:
            impact_text(img, "¡OJO!", 135, 96, g, t_ojo, color=P["red_l"], scale=6)
            gv = lerp(0.95, 0.35, ease_io(prog(g, t_rap - 0.2, 0.6)))
            paste(img, cp.gauge(gv, g), 52, 300, scale=0.8, anchor="center")
            source(img, "WISE 2016 · AL VOLVER AL AZÚCAR")
        if g > t_cta:
            impact_text(img, "¿AGUANTARÍAS", 135, 88, g, t_cta, color=P["white"], scale=3)
            impact_text(img, "EL DÍA 3?", 135, 122, g, t_cta + 0.12, color=P["gold"], scale=4)
        z = 1.0 + 0.04 * prog(g, t_ojo, 3.0)
        out = gfx.camera(img, z, 135, 240, t=g)
        hud_layer(out, g)
        return out

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("d1", "d1", s_d1, "cut", 0.2, 0.3),
        ("d3", "d3", s_d3, "pixelate", 0.3, 0.2),
        ("turn", "turn", s_turn, "cut", 0.2, 0.15),
        ("liver", "d10", s_liver, "dither", 0.25, 0.2),
        ("still", "still", s_still, "whip_left", 0.25, 0.15),
        ("d90", "d90", s_d90, "iris", 0.35, 0.2),
        ("reveal", "reveal", s_reveal, "cut", 0.15, 0.1),
        ("end", "twist", s_end, "pixelate", 0.25, 0.1),
    ])
    emph = {norm(w): col for w, col in [("noventa", P["gold"]), ("azúcar", P["pink"]), ("raro", P["gold"]),
            ("lengua", P["pink"]), ("fruta", P["green"]), ("monstruo", P["pink"]), ("antojos", P["red_l"]),
            ("cabeza", P["orange"]), ("ánimo", P["sky"]), ("hígado", P["fat"]), ("mitad", P["green"]),
            ("nueve", P["green"]), ("ahí", P["pink"]), ("postre", P["fat_l"]), ("cuarenta", P["pink"]),
            ("dulce", P["pink"]), ("recalibró", P["green"]), ("ojo", P["red_l"]), ("rápido", P["red_l"]),
            ("tres", P["gold"])]}
    return Director(tl, scenes, SubStyle(y=356, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.25))
