"""B01 · "¿Qué le pasa a tu cuerpo si dejas el azúcar?" — first episode of the body-change format.

Facts (checked 2026-11-14):
- Day 3 valley: Falbe J et al., Appetite 2019;133:130-137 — 25 overweight adolescents who stopped
  sugar-sweetened beverages for 3 days reported more cravings and headache, less motivation, contentment,
  concentration and well-being (preliminary, small, uncorrected p-values).
- Day 10 liver: Schwarz JM et al., Gastroenterology 2017;153:743-752 — 41 children with obesity, sugar
  swapped for starch (same calories) for 9 days: median liver fat 7.2 % -> 3.8 % on day 10, also in those
  who did not lose weight.
- Day 90 taste: Wise PM et al., Am J Clin Nutr 2016;103:50-60 — on a low-sugar diet, by month 3 puddings
  were rated ~40 % sweeter than by controls; after returning to sugar, perception reverted quickly.
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast, hud, organs
from engine.gfx import P, prog, ease_out, ease_io, ease_back, ease_in, lerp, paste, clamp
from engine.kit import (label, pop_scale, paste_scaled, text_sprite, scenes_from, hook_camera,
                        impact_text, count_text, xray, split_before_after)
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "b01_azucar"
BPM = 112
LEAD_IN = 0.1
TAIL = 1.6
NARRATION_FILE = "episodes/b01_azucar/narration.mp3"

LINES = [
    {"id": "hook", "text": "Dejar el azúcar te va a hacer sentir peor...", "pause": 0.3},
    {"id": "hook2", "text": "al principio.", "hold": 0.15},
    {"id": "pact", "text": "Leo lo intentó. Día uno: cero azúcar añadido."},
    {"id": "d3", "text": "Día tres: lo peor. Antojos, dolor de cabeza, cero ánimo."},
    {"id": "d3src", "text": "En un estudio, a jóvenes que dejaron los refrescos les pasó justo eso."},
    {"id": "turn", "text": "Pero por dentro, algo ya estaba cambiando.", "hold": 0.1},
    {"id": "d10", "text": "Día diez. En niños con obesidad, quitar el azúcar bajó la grasa del hígado casi a la mitad."},
    {"id": "d10b", "text": "En solo nueve días."},
    {"id": "weird", "text": "Y lo más raro llega después."},
    {"id": "d90", "text": "A los tres meses, lo dulce le sabe un cuarenta por ciento más dulce.", "hold": 0.2},
    {"id": "reveal", "text": "Por fuera, el mismo Leo. Por dentro, otra historia.", "hold": 0.2},
    {"id": "twist", "text": "Pero ojo: si vuelve al azúcar, su lengua lo olvida rápido."},
    {"id": "cta", "text": "¿Cuántos días aguantarías tú?"},
]

TITLE = "¿Qué le pasa a tu cuerpo si dejas el azúcar? 🍩 #Shorts"
DESCRIPTION = (
    "¿Qué le pasa a tu cuerpo si dejas el azúcar? Los primeros días pueden ser los peores, pero por dentro "
    "los cambios empiezan pronto.\n\n"
    "Fuentes:\n"
    "· Día 3: Falbe et al., Appetite, 2019 (adolescentes que dejaron las bebidas azucaradas 3 días; estudio "
    "pequeño y preliminar).\n"
    "· Día 10: Schwarz et al., Gastroenterology, 2017 (niños con obesidad; azúcar cambiada por almidón 9 "
    "días; grasa del hígado de 7,2 % a 3,8 %).\n"
    "· 3 meses: Wise et al., Am J Clin Nutr, 2016 (con menos azúcar, lo dulce se percibió ~40 % más dulce; "
    "al volver al azúcar, se revirtió).\n"
    "Contenido educativo, no es consejo médico.\nVoz: ElevenLabs.\n\n"
    "#azucar #salud #quelepasaatucuerpo #fitness #Shorts")
TAGS = ["dejar el azúcar", "qué le pasa a tu cuerpo", "hígado graso", "antojos de azúcar", "salud"]


# ---------------------------------------------------------------- props (original pixel sprites)
def donut(bitten=0.0):
    S = gfx.new(30, 26)
    d = ImageDraw.Draw(S)
    d.ellipse([1, 4, 28, 25], fill=P["wood"])
    d.ellipse([1, 1, 28, 21], fill=P["pink"])
    d.ellipse([11, 8, 18, 14], fill=(0, 0, 0, 0))
    for (x, y, c) in ((6, 6, P["sky"]), (21, 5, P["gold"]), (24, 13, P["white"]), (5, 14, P["green"]),
                      (14, 3, P["white"]), (18, 17, P["sky"])):
        d.rectangle([x, y, x + 1, y], fill=c)
    if bitten > 0:
        r = int(4 + bitten * 4)
        for k in range(3):
            d.ellipse([22 - r + k * 3, -r + k * 2, 22 + r + k * 3, r + k * 2], fill=(0, 0, 0, 0))
    return gfx.outline(S)


def soda(crossed=False):
    S = gfx.new(18, 28)
    d = ImageDraw.Draw(S)
    d.rectangle([3, 3, 14, 26], fill=P["red"])
    d.rectangle([3, 10, 14, 15], fill=P["white"])
    d.rectangle([5, 1, 12, 3], fill=P["steel"])
    if crossed:
        d.line([0, 27, 17, 0], fill=P["ink"], width=4)
        d.line([0, 27, 17, 0], fill=P["red_l"], width=2)
    return gfx.outline(S)


def pudding():
    S = gfx.new(26, 24)
    d = ImageDraw.Draw(S)
    d.polygon([(2, 12), (23, 12), (20, 23), (5, 23)], fill=P["steel_l"])
    d.ellipse([3, 4, 22, 16], fill=P["fat"])
    d.ellipse([6, 3, 19, 9], fill=P["wood"])
    return gfx.outline(S)


def trash():
    S = gfx.new(30, 34)
    d = ImageDraw.Draw(S)
    d.polygon([(3, 6), (26, 6), (23, 33), (6, 33)], fill=P["steel_d"])
    d.rectangle([1, 3, 28, 7], fill=P["steel"])
    for x in (10, 15, 20):
        d.line([x, 10, x - 1, 30], fill=P["steel"])
    return gfx.outline(S)


def calendar_page(n):
    S = gfx.new(26, 30)
    d = ImageDraw.Draw(S)
    d.rectangle([1, 1, 24, 28], fill=P["white"])
    d.rectangle([1, 1, 24, 8], fill=P["red"])
    from engine.font import draw_text
    draw_text(S, str(n), 13, 13, color=P["ink"], scale=1, align="center")
    return gfx.outline(S)


def kitchen_bg(g, dark=0.0, warm=False):
    """Original kitchen at night: tiles, counter, fridge glow."""
    img = gfx.new(W, H, P["night"] + (255,))
    top = [(0, P["deep"]), (1, P["violet"])] if not warm else [(0, P["violet"]), (0.7, P["pink"]), (1, P["orange"])]
    gfx.vgradient(img, (0, 0, W, 300), top)
    d = ImageDraw.Draw(img)
    for y in range(120, 300, 16):
        for x in range(0 if (y // 16) % 2 else 8, W, 16):
            d.rectangle([x, y, x + 14, y + 14], outline=gfx.lerpc(P["violet"], P["lav"], 0.25))
    # window
    d.rectangle([150, 40, 240, 110], fill=P["ink"] if not warm else P["sky"])
    d.rectangle([150, 40, 240, 110], outline=P["steel_d"], width=3)
    d.line([195, 40, 195, 110], fill=P["steel_d"], width=2)
    if not warm:
        d.ellipse([210, 52, 224, 66], fill=P["cream"])
    else:
        d.ellipse([160, 80, 190, 110], fill=P["gold"])
    # fridge
    d.rectangle([14, 130, 70, 300], fill=P["steel_l"])
    d.line([14, 190, 70, 190], fill=P["steel"], width=2)
    d.rectangle([60, 150, 64, 175], fill=P["steel_d"])
    # counter
    d.rectangle([0, 300, W, 312], fill=P["wood"])
    d.rectangle([0, 312, W, H], fill=P["wood_d"])
    if dark > 0:
        img = gfx.darken(img, dark)
    return img


def leo(pose=None):
    p = {"mouth": "smile"}
    p.update(pose or {})
    return cast.hero(p)


# ---------------------------------------------------------------- audio
def sound_cues(tl):
    c, L = tl.cue, tl.line
    cues = [(0.0, "impact", 0.9), (0.02, "whoosh", 0.6),
            (c("hook", "peor"), "glitch", 0.7), (c("hook", "peor"), "thud", 0.8),
            (c("hook2", "principio") , "boing", 0.5),
            (c("pact", "intentó"), "whoosh", 0.5), (c("pact", "uno") - 0.05, "ding", 0.7),
            (c("pact", "cero") + 0.1, "clank", 0.6),
            (c("d3", "tres") - 0.25, "tick", 0.6), (c("d3", "tres") - 0.12, "tick", 0.6), (c("d3", "tres"), "ding", 0.6),
            (c("d3", "antojos"), "bar_up", 0.8), (c("d3", "cabeza"), "heartbeat", 0.8),
            (c("d3", "ánimo"), "bar_down", 0.8),
            (c("d3src", "refrescos"), "pop", 0.6),
            (L("turn").start - 0.1, "scan", 0.9),
            (c("d10", "diez") - 0.3, "tick", 0.5), (c("d10", "diez") - 0.15, "tick", 0.5), (c("d10", "diez"), "ding", 0.6),
            (c("d10", "hígado"), "babble", 0.7), (c("d10", "mitad"), "deflate", 0.8),
            (c("d10", "mitad") + 0.1, "sparkle", 0.6),
            (c("d10b", "nueve"), "stamp", 0.8),
            (L("weird").start, "rise", 0.7),
            (c("d90", "meses"), "ding", 0.7),
            (c("d90", "cuarenta"), "boing", 0.7), (c("d90", "dulce", 2), "babble", 0.8),
            (L("reveal").start - 0.2, "whoosh", 0.6), (c("reveal", "historia"), "impact", 0.9),
            (c("reveal", "historia") + 0.05, "sparkle", 0.7),
            (c("twist", "ojo"), "alarm", 0.4), (c("twist", "rápido"), "deflate", 0.6),
            (L("cta").start - 0.1, "pop", 0.6), (c("cta", "tú"), "ding", 0.7)]
    # tick-tick-tick while the counter races 10 -> 90
    w0, w1 = L("weird").start, c("d90", "meses")
    k = w0
    while k < w1 - 0.1:
        cues.append((k, "tick", 0.35))
        k += 0.09
    return cues


def music_sections(tl):
    c, L = tl.cue, tl.line
    return [(0.0, L("pact").start, "pulse"),
            (L("pact").start, L("d3").start - 0.05, "drive"),
            (L("d3").start - 0.05, L("turn").start - 0.1, "low"),
            (L("turn").start - 0.1, c("reveal", "historia") - 0.35, "drive"),
            (c("reveal", "historia") - 0.35, c("reveal", "historia"), "silence"),
            (c("reveal", "historia"), L("twist").start, "triumph"),
            (L("twist").start, tl.total, "pulse")]


# ---------------------------------------------------------------- picture
def make_director(tl):
    c, L = tl.cue, tl.line
    MAX_DAY = 90
    t_d1, t_d3, t_d10 = c("pact", "uno"), c("d3", "tres"), c("d10", "diez")
    t_d90 = c("d90", "meses")
    day_keys = [(0.0, 1), (t_d1, 1), (t_d3, 3), (t_d10, 10), (t_d90, 90, max(0.5, t_d90 - L("weird").start - 0.1))]

    def hud_layer(img, g, show=True):
        if not show:
            return
        day = hud.count_day(g, day_keys, dur=0.5)
        fl = 0.0
        for tt in (t_d1, t_d3, t_d10, t_d90):
            if 0 <= g - tt < 0.4:
                fl = 1 - (g - tt) / 0.4
        appear = ease_back(prog(g, L("pact").start, 0.35))
        if appear <= 0:
            return
        layer = gfx.new()
        hud.day_counter(layer, day, MAX_DAY, g, flash=fl)
        off = int((1 - min(appear, 1.0)) * -60)
        img.paste(layer, (0, off), layer)

    # 1. HOOK — the donut, then the twist "you'll feel WORSE"
    def s_hook(g):
        t_peor, t_pr = c("hook", "peor"), L("hook2").start
        img = kitchen_bg(g)
        bad = g > t_peor
        bob = math.sin(g * 5) * 2
        pose = {"arm_r": (120, 60), "mouth": "grin" if not bad else "o", "eyes": "happy" if not bad else "wide",
                "sweat": bad, "belly": 0.35}
        paste(img, leo(pose), 135, 330, scale=2.6)
        dn_y = 205 + bob if not bad else 205 + bob + ease_in(prog(g, t_peor, 0.4)) * 120
        paste(img, donut(), 168, dn_y, scale=2.2, anchor="center")
        if not bad:
            fx.sparkles(img, 168, dn_y, g, n=6, radius=26, color=P["pink"])
        impact_text(img, "PEOR", 135, 105, g, t_peor, color=P["red_l"], scale=6)
        if g > t_pr:
            paste_scaled(img, text_sprite("...AL PRINCIPIO", P["gold"], scale=2), 135, 150, pop_scale(g, t_pr))
        out = hook_camera(img, g, cx=150, cy=220)
        if 0 <= g - t_peor < 0.18:
            out = gfx.chroma_glitch(out, 6, g)
            out = gfx.camera(out, 1.0, shake=3, t=g)
        hud_layer(out, g)
        return out

    # 2. PACT — HUD appears, donut into the trash
    def s_pact(g):
        st, t_cero = L("pact").start, c("pact", "cero")
        img = kitchen_bg(g)
        paste(img, trash(), 222, 300, scale=2)
        throw = prog(g, st + 0.25, 0.6)
        paste(img, leo({"arm_r": (lerp(120, 170, ease_out(throw)), 20), "mouth": "grit", "eyes": "open"}), 110, 330, scale=2.6)
        if throw < 1:
            x = lerp(150, 222, throw)
            y = lerp(200, 250, throw) - math.sin(throw * math.pi) * 70
            paste(img, donut().rotate(-throw * 540, expand=True), x, y, scale=2, anchor="center")
        elif g - (st + 0.85) < 0.5:
            fx.burst(img, 222, 240, g - (st + 0.85), n=14, colors=(P["pink"], P["white"]))
        impact_text(img, "CERO AZÚCAR", 135, 112, g, t_cero, color=P["green"], scale=4)
        hud_layer(img, g)
        return img

    # 3. DAY 3 — the valley
    def s_d3(g):
        t_ant, t_cab, t_ani = c("d3", "antojos"), c("d3", "cabeza"), c("d3", "ánimo")
        t_src = L("d3src").start
        img = kitchen_bg(g, dark=0.35)
        slump = 0.5 + 0.5 * math.sin(g * 2)
        paste(img, leo({"mouth": "sad", "eyes": "sad", "sweat": True, "arm_l": (5, 5), "arm_r": (5, 5),
                        "droop": 0.6, "bob": -slump}), 85, 330, scale=2.4)
        # craving thought bubble
        if t_ant - 0.1 < g < t_src:
            s = pop_scale(g, t_ant - 0.1)
            bub = gfx.new(54, 44)
            bd = ImageDraw.Draw(bub)
            bd.ellipse([2, 2, 52, 34], fill=P["white"])
            bd.ellipse([4, 36, 10, 42], fill=P["white"])
            bub = gfx.outline(bub)
            bub.alpha_composite(donut(), (12, 6))
            paste_scaled(img, bub, 150 + math.sin(g * 3) * 3, 160, s * 1.5)
        # brain in pain
        if g > t_cab - 0.15:
            paste_scaled(img, organs.brain("pain", g), 205, 205 + math.sin(g * 9) * 2, pop_scale(g, t_cab - 0.15) * 1.6)
        # stat bars (left column under HUD)
        hud.stat_bar(img, 12, 66, 110, "ANTOJOS", lerp(0.3, 0.95, ease_out(prog(g, t_ant, 0.5))), P["red"], g,
                     delta=1, appear=prog(g, t_ant - 0.2, 0.3))
        hud.stat_bar(img, 140, 66, 110, "ÁNIMO", lerp(0.8, 0.15, ease_out(prog(g, t_ani, 0.5))), P["sky"], g,
                     delta=-1, appear=prog(g, t_ani - 0.2, 0.3))
        word = None
        for (tt, w, col) in ((t_ant, "ANTOJOS", P["red_l"]), (t_cab, "DOLOR DE CABEZA", P["orange"]),
                             (t_ani, "CERO ÁNIMO", P["sky"])):
            if g >= tt:
                word = (tt, w, col)
        if word and g < t_src:
            impact_text(img, word[1], 135, 120, g, word[0], color=word[2], scale=4)
        if g >= t_src:
            card = gfx.new(230, 58)
            cd = ImageDraw.Draw(card)
            cd.rounded_rectangle([1, 1, 228, 56], radius=6, fill=P["ink"], outline=P["fog"], width=2)
            from engine.font import draw_text
            draw_text(card, "ESTUDIO · JÓVENES", 115, 9, color=P["gold"], align="center")
            draw_text(card, "SIN REFRESCOS 3 DÍAS", 115, 22, color=P["white"], align="center")
            draw_text(card, "FALBE 2019", 115, 38, color=P["fog"], align="center")
            paste_scaled(img, gfx.outline(card), 135, 128, pop_scale(g, t_src))
            paste_scaled(img, soda(crossed=g > c("d3src", "refrescos")), 30, 128, pop_scale(g, c("d3src", "refrescos")) * 1.6)
        out = gfx.camera(img, 1.0 + 0.02 * math.sin(g * 1.5), shake=1.5 if 0 <= g - t_cab < 0.5 else 0, t=g)
        hud_layer(out, g)
        return out

    def inside_bg(g):
        return cast.tissue_bg(g, hue="pink")

    # 4. TURN — x-ray into the body
    def s_turn(g):
        st = L("turn").start
        outside = kitchen_bg(g, dark=0.2)
        paste(outside, leo({"mouth": "flat", "eyes": "open"}), 135, 330, scale=2.6)
        inner = inside_bg(g)
        paste(inner, organs.liver(1.0, "sad", g), 135, 220, scale=2.6, anchor="center")
        label(inner, "TU HÍGADO", 135, 290, color=P["white"], scale=2)
        out = xray(outside, inner, 140, 250, prog(g, st, 1.1))
        if g > c("turn", "cambiando"):
            impact_text(out, "¿QUÉ PASA?", 135, 110, g, c("turn", "cambiando"), color=P["gold"], scale=4)
        hud_layer(out, g)
        return out

    # 5. DAY 10 — liver fat halves
    def s_liver(g):
        t_nin, t_hig, t_mit = c("d10", "niños"), c("d10", "hígado"), c("d10", "mitad")
        t_9 = c("d10b", "nueve")
        img = inside_bg(g)
        k = ease_io(prog(g, t_mit - 0.4, 1.0))
        fat = lerp(1.0, 0.5, k)
        mood = "sad" if k < 0.5 else "happy"
        lv = organs.liver(fat, mood, g)
        sc = 2.6 - 0.25 * k
        paste(img, lv, 135, 215 + math.sin(g * 3) * 3, scale=sc, anchor="center")
        if k > 0.1:
            for i in range(4):  # droplets floating away
                fk = (g * 0.8 + i * 0.25) % 1
                paste(img, cast.fat_cell(5, mood="sad", t=g), 95 + i * 30, 215 - fk * 90, scale=1, anchor="center")
        pct = count_text(7.2, 3.8, g, t_mit - 0.3, 1.0) + " %"
        if g > t_hig - 0.2:
            label(img, "GRASA EN EL HÍGADO", 135, 72, color=P["fat_l"])
            impact_text(img, pct, 135, 110, g, t_hig - 0.2, color=P["fat"] if k < 0.9 else P["green"], scale=5, out_t=t_9 - 0.2)
        if g > t_nin:
            label(img, "NIÑOS CON OBESIDAD · SCHWARZ 2017", 135, 296, color=P["fog"])
        if g > t_mit:
            paste_scaled(img, organs.speech("¡QUÉ ALIVIO!"), 205, 158, pop_scale(g, t_mit + 0.2) * 1.4)
            fx.sparkles(img, 135, 215, g, n=10, radius=70, color=P["green"])
        if g > t_9:
            impact_text(img, "9 DÍAS", 135, 110, g, t_9, color=P["green"], scale=6)
        hud_layer(img, g)
        return img

    # 6. WEIRD — calendar race 10 -> 90
    def s_weird(g):
        st = L("weird").start
        img = cast.end_bg(g)
        fx.speed_lines(img, 135, 220, g, n=34, r0=40)
        for i in range(10):
            ph = (g * 2.2 + i * 0.1) % 1
            x = 135 + math.cos(i * 2.4) * ph * 160
            y = 220 + math.sin(i * 2.4) * ph * 200
            paste(img, calendar_page(10 + i * 8), x, y, scale=1.2 + ph, anchor="center")
        paste(img, leo({"mouth": "o", "eyes": "wide", "walk": g * 16, "arm_l": (60, 40), "arm_r": (-30, 40)}),
              135, 330, scale=2.2)
        impact_text(img, "¿Y DESPUÉS?", 135, 110, g, st + 0.1, color=P["lav"], scale=4)
        out = gfx.camera(img, 1.0 + 0.06 * prog(g, st, 1.2), t=g)
        hud_layer(out, g)
        return out

    # 7. DAY 90 — the tongue
    def s_tongue(g):
        t_cua, t_dulce = c("d90", "cuarenta"), c("d90", "dulce", 2)
        img = inside_bg(g)
        shock = g > t_dulce - 0.1
        paste(img, organs.tongue("shock" if shock else "happy", g), 135, 262, scale=2.6, anchor="center")
        paste(img, pudding(), 60, 300, scale=2)
        # spoon trip
        sp = prog(g, L("d90").start + 0.3, 0.6)
        if sp < 1:
            paste(img, pudding(), lerp(60, 120, sp), lerp(270, 200, sp), scale=1.2, anchor="center")
        impact_text(img, "+40 %", 135, 122, g, t_cua, color=P["pink"], scale=6)
        if g > t_cua:
            label(img, "MÁS DULCE", 135, 158, color=P["white"], scale=2)
        if shock:
            paste_scaled(img, organs.speech("¡QUÉ DULCE!", tail="left"), 205, 200, pop_scale(g, t_dulce) * 1.3)
            fx.sparkles(img, 135, 262, g, n=8, radius=60, color=P["pink"])
        hud.stat_bar(img, 12, 66, 110, "SABOR DULCE", lerp(0.4, 0.95, ease_out(prog(g, t_cua, 0.6))), P["pink"], g,
                     delta=1, appear=prog(g, t_cua - 0.2, 0.3))
        label(img, "3 MESES · WISE 2016", 135, 343, color=P["fog"])
        out = gfx.camera(img, 1.0, shake=2 if 0 <= g - t_dulce < 0.3 else 0, t=g)
        hud_layer(out, g)
        return out

    # 8. REVEAL — split day 1 vs day 90
    def s_reveal(g):
        st, t_his = L("reveal").start, c("reveal", "historia")
        left = kitchen_bg(g, dark=0.3)
        paste(left, leo({"mouth": "sad", "eyes": "sad", "sweat": True, "belly": 0.35}), 70, 330, scale=2.2)
        paste(left, organs.liver(1.0, "sad", g), 70, 150, scale=1.0, anchor="center")
        right = kitchen_bg(g, warm=True)
        paste(right, leo({"mouth": "grin", "eyes": "happy", "belly": 0.35, "arm_r": (150, 30)}), 200, 330, scale=2.2)
        paste(right, organs.liver(0.4, "happy", g), 185, 150, scale=1.0, anchor="center")
        paste(right, organs.tongue("happy", g), 238, 150, scale=0.8, anchor="center")
        out = split_before_after(left, right, prog(g, st + 0.15, 0.9))
        impact_text(out, "OTRA HISTORIA", 135, 104, g, t_his, color=P["gold"], scale=4)
        if g > t_his:
            fx.sparkles(out, 200, 220, g, n=10, radius=50)
        return out

    # 9. TWIST + CTA — back to the opening frame (loop)
    def s_end(g):
        t_ojo, t_rap = c("twist", "ojo"), c("twist", "rápido")
        t_cta = L("cta").start
        img = kitchen_bg(g)
        tempted = g > t_ojo
        paste(img, leo({"arm_r": (120, 60) if tempted else (10, 10), "mouth": "grin" if tempted else "smile",
                        "eyes": "happy" if tempted else "open", "belly": 0.35}), 135, 330, scale=2.6)
        if tempted:
            paste(img, donut(), 168, 205 + math.sin(g * 5) * 2, scale=2.2, anchor="center")
        if t_ojo < g < t_cta:
            impact_text(img, "¡OJO!", 135, 105, g, t_ojo, color=P["red_l"], scale=6)
        if t_rap - 0.3 < g < t_cta:
            paste_scaled(img, organs.tongue("sad", g), 60, 200, pop_scale(g, t_rap - 0.3) * 1.2)
            paste_scaled(img, organs.speech("¿EH? ¿QUÉ ERA?"), 70, 150, pop_scale(g, t_rap) * 1.2)
        if g > t_cta:
            impact_text(img, "¿CUÁNTOS DÍAS", 135, 98, g, t_cta, color=P["white"], scale=3)
            impact_text(img, "AGUANTAS TÚ?", 135, 128, g, t_cta + 0.15, color=P["gold"], scale=3)
        hud_layer(img, g)
        return img

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("pact", "pact", s_pact, "whip_left", 0.25, 0.15),
        ("d3", "d3", s_d3, "pixelate", 0.3, 0.2),
        ("turn", "turn", s_turn, "cut", 0.2, 0.15),
        ("liver", "d10", s_liver, "dither", 0.25, 0.2),
        ("weird", "weird", s_weird, "whip_left", 0.25, 0.1),
        ("tongue", "d90", s_tongue, "iris", 0.35, 0.15),
        ("reveal", "reveal", s_reveal, "cut", 0.2, 0.25),
        ("end", "twist", s_end, "pixelate", 0.25, 0.1),
    ])
    emph = {norm(w): col for w, col in [("azúcar", P["pink"]), ("peor", P["red_l"]), ("antojos", P["red_l"]),
            ("cabeza", P["orange"]), ("ánimo", P["sky"]), ("hígado", P["fat"]), ("mitad", P["green"]),
            ("nueve", P["green"]), ("cuarenta", P["pink"]), ("dulce", P["pink"]), ("historia", P["gold"]),
            ("ojo", P["red_l"]), ("olvida", P["red_l"]), ("tú", P["gold"])]}
    return Director(tl, scenes, SubStyle(y=356, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.25))
