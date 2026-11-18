"""B05 v2 · "¿10 minutos después de cada comida le ganan a 30 de una vez?" — revised pilot.

Structure: HOOK (question) → PROBLEM → CONFLICT → BIOLOGY → EVIDENCE → PAYOFF → AUDIENCE QUESTION.

Evidence (checked 2026-11-18):
- Reynolds AN, Mann JI, Williams S, Venn BJ. Diabetologia 2016;59(12):2572-2578. Randomised crossover,
  41 adults with type 2 diabetes, 2 weeks each: advice to walk 30 min once a day vs 10 min after each
  main meal. Post-meal glycaemia (3 h iAUC) was 12 % lower with post-meal walks (ratio 0.88, 95 % CI
  0.78-0.99); after the evening meal the reduction was 22 % (university release).
- Buffey AJ et al. Sports Med 2022;52:1765-1787. Meta-analysis of 7 acute lab crossover studies:
  light walking breaks lowered post-meal glucose vs sitting more than standing breaks did. Break lengths
  varied (2-30 min), so no single duration (e.g. "2 minutes") is established as universally effective.
- Richter EA, Hargreaves M. Physiol Rev 2013;93:993-1017. Muscle contraction moves the glucose
  transporter GLUT4 to the cell surface, increasing glucose uptake into skeletal muscle.
The bar chart shows the real Reynolds values (100 vs 88, and the 22 % evening figure), not an illustration.
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast, hud
from engine import cast_plus as cp, cast_villains as cv, story as st
from engine.gfx import P, prog, ease_out, ease_io, ease_back, ease_in, lerp, paste
from engine.kit import label, scenes_from, impact_text, street_bg, xray, pop_scale, paste_scaled
from engine.font import draw_text
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "b05_caminar"
VERSION = 2
EXPERIMENT = {"id": "EXP-004", "arm": "test", "voice": False, "hook_type": "comparison_question"}
BPM = 112
LEAD_IN = 0.06
TAIL = 1.4
NARRATION_FILE = "episodes/b05_caminar/narration.mp3"

LINES = [
    {"id": "hook", "text": "¿Diez minutos después de cada comida… le ganan a treinta de una vez?"},
    {"id": "hook2", "text": "Leo lo comprobó.", "hold": 0.15},
    {"id": "prob", "text": "Almuerzo grande. Después: silla, pantalla… y sueño."},
    {"id": "conf", "text": "Ahí aparece el monstruo: el pico de azúcar."},
    {"id": "turn", "text": "Leo se levanta y sale a caminar."},
    {"id": "bio", "text": "Cada paso contrae sus músculos… y eso abre puertas para que entre el azúcar."},
    {"id": "ev1", "text": "Un estudio en adultos con diabetes tipo dos lo comparó."},
    {"id": "ev2", "text": "Con diez minutos tras cada comida, el azúcar fue doce por ciento más bajo.", "hold": 0.1},
    {"id": "ev3", "text": "Tras la cena, veintidós."},
    {"id": "pay", "text": "El monstruo se encoge… pero vuelve en cada comida."},
    {"id": "disc", "text": "Ojo: no cura la diabetes ni reemplaza el tratamiento."},
    {"id": "cta", "text": "Y tú, después de cenar: ¿sofá o caminata?"},
]

TITLE = "¿10 minutos después de comer le ganan a 30 de una vez? 🚶 #Shorts"
DESCRIPTION = (
    "¿Caminar 10 minutos después de cada comida le gana a caminar 30 minutos de una vez? Para el azúcar después "
    "de comer, un estudio dice que sí.\n\n"
    "Fuentes:\n"
    "· Reynolds et al., Diabetologia, 2016 — ensayo cruzado con 41 adultos con diabetes tipo 2 (2 semanas por "
    "plan): con 10 min de caminata después de cada comida, el azúcar posterior a las comidas fue 12 % más bajo "
    "que con 30 min una vez al día; después de la cena, 22 % más bajo.\n"
    "· Buffey et al., Sports Medicine, 2022 — metaanálisis de 7 estudios de laboratorio: caminar suave en "
    "pausas bajó el azúcar después de comer más que quedarse sentado o solo ponerse de pie.\n"
    "· Richter y Hargreaves, Physiological Reviews, 2013 — al contraerse, el músculo lleva el transportador "
    "GLUT4 a su superficie y absorbe más glucosa.\n"
    "Estudios de corto plazo; los resultados pueden variar. No cura la diabetes ni reemplaza el tratamiento. "
    "Contenido educativo, no es consejo médico.\n"
    "Voz: ElevenLabs.\n\n#caminar #glucosa #salud #azucarensangre #habitossaludables")
TAGS = ["caminar después de comer", "azúcar en sangre", "glucosa", "diabetes tipo 2", "qué le pasa a tu cuerpo"]


# ---------------------------------------------------------------- sound
def sound_cues(tl):
    c, L = tl.cue, tl.line
    cues = [(0.0, "impact", 0.8), (0.0, "whoosh", 0.5), (c("hook", "diez"), "blip", 0.6),
            (c("hook", "treinta"), "blip", 0.6), (c("hook", "vez"), "boing", 0.5), (c("hook2", "comprobó"), "ding", 0.7),
            (L("prob").start, "whoosh", 0.5), (c("prob", "almuerzo"), "chomp", 0.7), (c("prob", "almuerzo") + 0.35, "chomp", 0.7),
            (c("prob", "silla"), "thud", 0.5), (c("prob", "pantalla"), "blip", 0.4), (c("prob", "sueño"), "deflate", 0.6),
            (c("conf", "monstruo") - 0.1, "growl", 0.9), (c("conf", "pico"), "bar_up", 0.8),
            (c("conf", "pico") + 0.6, "chomp", 0.8), (c("conf", "pico") + 0.8, "inflate", 0.6),
            (c("turn", "levanta"), "whoosh", 0.6),
            (L("bio").start, "scan", 0.9), (c("bio", "contrae"), "clank", 0.5), (c("bio", "puertas"), "pop", 0.7),
            (c("bio", "azúcar"), "sparkle", 0.6),
            (L("ev1").start, "whoosh", 0.4), (c("ev1", "comparó"), "ding", 0.5),
            (c("ev2", "doce"), "bar_down", 0.9), (c("ev2", "doce") + 0.05, "impact", 0.7),
            (c("ev3", "veintidós"), "bar_down", 0.9), (c("ev3", "veintidós") + 0.05, "sparkle", 0.7),
            (c("pay", "encoge"), "deflate", 0.8), (c("pay", "vuelve"), "growl", 0.5), (c("pay", "comida"), "chomp", 0.6),
            (c("disc", "ojo"), "alarm", 0.35), (c("disc", "tratamiento"), "thud", 0.5),
            (L("cta").start - 0.1, "pop", 0.6), (c("cta", "sofá"), "blip", 0.6), (c("cta", "caminata"), "ding", 0.7)]
    for (a, b) in ((c("turn", "caminar"), L("bio").end), (L("pay").start, L("pay").end)):   # footsteps
        k = a
        while k < b:
            cues.append((k, "step", 0.35))
            k += 0.42
    return cues


def music_sections(tl):
    c, L = tl.cue, tl.line
    t_hit = c("ev2", "doce")
    return [(0.0, L("prob").start, "pulse"), (L("prob").start, L("conf").start, "groove"),
            (L("conf").start, L("turn").start - 0.05, "low"), (L("turn").start, L("ev1").start, "drive"),
            (L("ev1").start, t_hit - 0.5, "mystery"), (t_hit - 0.5, t_hit, "silence"),
            (t_hit, L("disc").start, "triumph"), (L("disc").start, tl.total, "pulse")]


# ---------------------------------------------------------------- props
def chair():
    S = gfx.new(40, 50)
    d = ImageDraw.Draw(S)
    d.rectangle([4, 24, 34, 30], fill=P["steel_d"])
    d.rectangle([24, 2, 32, 26], fill=P["steel_d"])
    d.line([19, 30, 19, 44], fill=P["steel"], width=3)
    d.line([8, 46, 30, 46], fill=P["steel"], width=3)
    return gfx.outline(S)


def sofa():
    S = gfx.new(60, 34)
    d = ImageDraw.Draw(S)
    d.rounded_rectangle([2, 4, 58, 22], radius=6, fill=P["red_d"])
    d.rounded_rectangle([0, 14, 60, 30], radius=6, fill=P["red"])
    d.rectangle([6, 30, 10, 33], fill=P["wood_d"])
    d.rectangle([50, 30, 54, 33], fill=P["wood_d"])
    return gfx.outline(S)


def walker(g, phase=0.0, mood="grin"):
    return st.leo({"walk": g * 12 + phase, "mouth": mood,
                   "arm_l": (20 * math.sin(g * 12 + phase), 30), "arm_r": (-20 * math.sin(g * 12 + phase), 30)}, g)


# ---------------------------------------------------------------- picture
def make_director(tl):
    c, L = tl.cue, tl.line

    # 1 + 9. HOOK and LOOP — split comparison on frame 1 (central question visible immediately)
    def split_frame(g, cta=False):
        left = street_bg(g, scroll=g * 50, tod="sunrise")
        right = street_bg(g + 3, scroll=g * 50, tod="night")
        if cta:
            paste(left, sofa(), 70, 300, scale=1.7, anchor="center")
            paste(left, st.leo({"mouth": "flat", "eyes": "closed" if (g % 3) < 2 else "open", "bob": -4}, g),
                  70, 300, scale=1.6)
        else:
            paste(left, walker(g), 70, 330, scale=2.0)
        paste(right, walker(g, 1.7), 200, 330, scale=2.0)
        if not cta:
            paste(right, cv.plate(True), 232, 250, scale=1.2, anchor="center")
        img = left.copy()
        img.paste(right.crop((W // 2, 0, W, H)), (W // 2, 0))
        ImageDraw.Draw(img).rectangle([W // 2 - 1, 0, W // 2 + 1, H], fill=P["white"])
        if cta:
            label(img, "SOFÁ", 70, 150, color=P["red_l"], scale=3)
            label(img, "CAMINATA", 200, 150, color=P["green"], scale=2)
        else:
            label(img, "30 MIN", 70, 150, color=P["gold"], scale=3)
            label(img, "1 VEZ AL DÍA", 70, 180, color=P["white"])
            label(img, "10 MIN", 200, 150, color=P["green"], scale=3)
            label(img, "TRAS CADA COMIDA", 200, 180, color=P["white"])
        return img

    def s_hook(g):
        img = split_frame(g)
        out = gfx.camera(img, lerp(1.15, 1.0, ease_out(prog(g, 0, 0.4))), 135, 240)
        if g < 0.25:
            fx.speed_lines(out, 135, 240, g, n=24)
        impact_text(out, "¿CUÁL GANA?", 135, 92, g, -0.4, color=P["white"], scale=5)   # fully visible on frame 1
        if g > c("hook2", "comprobó") - 0.1:
            impact_text(out, "LEO LO COMPROBÓ", 135, 225, g, c("hook2", "comprobó") - 0.1, color=P["gold"], scale=2)
        return out

    # 2. PROBLEM — Leo eats (arm to mouth), then slumps at the desk and dozes
    def s_prob(g):
        st_ = L("prob").start
        t_si, t_su = c("prob", "silla"), c("prob", "sueño")
        img = cv.office_bg(g, 0.1, None)
        if g < t_si:
            bite = abs(math.sin((g - st_) * 5))
            paste(img, st.leo({"arm_r": (lerp(30, 150, bite), lerp(20, 70, bite)),
                               "mouth": "o" if bite > 0.7 else "grin", "eyes": "happy"}, g), 135, 330, scale=2.6)
            paste(img, cv.plate(bite < 0.5), 178, 268, scale=1.8, anchor="center")
            impact_text(img, "ALMUERZO GRANDE", 135, 100, g, st_ + 0.05, color=P["fat_l"], scale=3)
        else:
            sl = ease_out(prog(g, t_si, 0.5))
            paste(img, chair(), 110, 342, scale=2.2, anchor="mid_bottom")
            paste(img, st.leo({"mouth": "o" if g > t_su else "flat", "eyes": "closed" if g > t_su + 0.3 else "sad",
                               "droop": sl, "arm_l": (5, 5), "arm_r": (40, 60), "bob": -4 * sl}, g), 110, 330, scale=2.4)
            if g > t_su:
                for i in range(3):
                    ph = ((g - t_su) * 0.8 + i * 0.33) % 1
                    label(img, "Z", 150 + ph * 40 + i * 4, 170 - ph * 50, color=P["lav"], scale=2)
            word = "SILLA" if g < c("prob", "pantalla") else ("PANTALLA" if g < t_su else "SUEÑO")
            t0 = t_si if word == "SILLA" else (c("prob", "pantalla") if word == "PANTALLA" else t_su)
            impact_text(img, word, 135, 100, g, t0, color=P["lav"] if word == "SUEÑO" else P["white"], scale=4)
        return img

    # 3. CONFLICT — the sugar-peak monster grows with each bite
    def s_conf(g):
        t_mon, t_pic = c("conf", "monstruo"), c("conf", "pico")
        t_boc = t_pic + 0.6   # "crece con cada bocado" is shown, not said
        img = gfx.darken(cv.office_bg(g, 0.2, None), 0.25)
        grow = ease_back(prog(g, t_mon - 0.3, 0.5)) * lerp(1.0, 1.45, ease_out(prog(g, t_boc, 0.6)))
        paste(img, chair(), 90, 342, scale=2.2, anchor="mid_bottom")
        paste(img, st.leo({"mouth": "o", "eyes": "wide" if g > t_mon else "sad", "sweat": g > t_mon, "look": 1,
                           "droop": 0.3}, g), 90, 330, scale=2.4)
        if grow > 0:
            paste(img, cv.villain("glucosa", "roar" if g < t_boc + 0.6 else "sly", g), 195,
                  215 + math.sin(g * 3) * 4, scale=1.4 * grow, anchor="center")
        hud.stat_bar(img, 12, 66, 140, "AZÚCAR EN SANGRE", lerp(0.25, 0.9, ease_out(prog(g, t_pic, 1.2))), P["red"], g,
                     delta=1, appear=prog(g, t_pic - 0.2, 0.3))
        impact_text(img, "PICO DE AZÚCAR", 135, 116, g, t_pic, color=P["white"], scale=3)
        return gfx.camera(img, 1.0 + 0.04 * prog(g, t_mon, 2.0), 150, 230, shake=2.5 if 0 <= g - t_mon < 0.4 else 0, t=g)

    # 4. TURN — stands up, walks out; the monster follows
    def s_turn(g):
        t_lev, t_cam = c("turn", "levanta"), c("turn", "caminar")
        if g < t_cam:
            img = cv.office_bg(g, 0.2, None)
            up = ease_back(prog(g, t_lev - 0.1, 0.4))
            paste(img, chair(), 90, 342, scale=2.2, anchor="mid_bottom")
            paste(img, st.leo({"mouth": "grit", "arm_l": (lerp(5, 150, up), 30), "arm_r": (lerp(5, 150, up), 30),
                               "bob": lerp(-4, 6, up)}, g), lerp(90, 140, up), 330, scale=2.6)
            impact_text(img, "¡DE PIE!", 135, 108, g, t_lev, color=P["green"], scale=5)
            return img
        img = street_bg(g, scroll=(g - t_cam) * 80, tod="sunrise")
        paste(img, walker(g), 160, 330, scale=2.4)
        paste(img, cv.villain("glucosa", "sly", g), 55, 230 + math.sin(g * 4) * 4, scale=1.1, anchor="center")
        impact_text(img, "A CAMINAR", 135, 108, g, t_cam, color=P["green"], scale=4)
        return img

    # 5. BIOLOGY — x-ray into the leg: each contraction opens GLUT4 'doors', glucose enters the fiber
    def leg_inner(g):
        img = cast.tissue_bg(g, hue="pink")
        beat = 0.5 + 0.5 * math.sin(g * 2 * math.pi / 0.84)          # synced to the 0.42 s footsteps
        thick = lerp(22, 30, beat)
        fy = 215
        paste(img, cast.muscle_fiber(150, thick, mood="happy", nuclei=5, t=g, glow=0.4), 135, fy, scale=1.6,
              anchor="center")
        d = ImageDraw.Draw(img)
        t_door = c("bio", "puertas")
        open_k = ease_out(prog(g, t_door - 0.2, 0.5)) * (0.4 + 0.6 * beat)
        half_h = thick * 1.6 / 2 + 2
        for i, (x, side) in enumerate([(70, -1), (110, 1), (150, -1), (190, 1)]):
            y = fy + side * half_h
            gap = int(2 + 5 * open_k)
            d.rectangle([x - 10, y - 3, x - gap, y + 3], fill=P["gold"])
            d.rectangle([x + gap, y - 3, x + 10, y + 3], fill=P["gold"])
            if open_k > 0.3:
                k = (g * 0.9 + i * 0.27) % 1
                if k < 0.95:
                    paste(img, cv.villain("glucosa", "sad", g, size=0.22), x, y + side * lerp(52, 0, ease_in(k)),
                          anchor="center")
        if g > c("bio", "contrae"):
            label(img, "CONTRACCIÓN", 135, 130, color=P["muscle_l"], scale=2)
        if g > t_door:
            label(img, "PUERTAS GLUT4", 135, 286, color=P["gold"], scale=2)
            label(img, "EL AZÚCAR ENTRA AL MÚSCULO", 135, 306, color=P["white"])
        label(img, "RICHTER Y HARGREAVES 2013", 135, 58, color=P["fog"])
        return img

    def s_bio(g):
        outside = street_bg(g, scroll=g * 80, tod="sunrise")
        paste(outside, walker(g), 135, 330, scale=2.6)
        return xray(outside, leg_inner(g), 128, 300, prog(g, L("bio").start, 0.9))

    # 6. EVIDENCE — real values, two bars, conditions + population + source readable
    def s_ev(g):
        img = gfx.darken(cast.lab_bg(g), 0.6)
        d = ImageDraw.Draw(img)
        t2, t3 = c("ev2", "doce"), c("ev3", "veintidós")
        base_y, max_h = 290, 130
        for (t1, t2_, val, col, x, tin) in (("30 MIN", "1 VEZ AL DÍA", 100, P["gold"], 75, L("ev1").start + 0.3),
                                            ("10 MIN", "TRAS CADA COMIDA", 88, P["green"], 195, t2 - 0.4)):
            k = ease_out(prog(g, tin, 0.6))
            h = int(max_h * val / 100 * k)
            if h > 0:
                d.rectangle([x - 26, base_y - h, x + 26, base_y], fill=col)
                d.rectangle([x - 26, base_y - h, x + 26, base_y - h + 3], fill=gfx.lerpc(col, P["white"], 0.5))
            label(img, t1, x, base_y + 8, color=col, scale=2)
            label(img, t2_, x, base_y + 28, color=P["white"])
            if k > 0.9:
                label(img, str(val), x, base_y - h - 14, color=P["white"], scale=2)
        d.line([40, base_y, 230, base_y], fill=P["fog"])
        out = gfx.camera(img, 1.0 + 0.03 * (0.5 + 0.5 * math.sin(g * 1.3)), 135, 220)
        label(out, "REYNOLDS 2016 · 41 ADULTOS CON DIABETES TIPO 2", 135, 56, color=P["fog"])
        label(out, "AZÚCAR TRAS LAS COMIDAS (3 H) · 30 MIN = 100", 135, 70, color=P["white"])
        if g > t2 - 0.05:
            impact_text(out, "-12 %", 195, 118, g, t2 - 0.05, color=P["green"], scale=4, max_w=130)
        if g > t3 - 0.05:
            impact_text(out, "CENA: -22 %", 135, 90, g, t3 - 0.05, color=P["green"], scale=3)
        return out

    # 7. PAYOFF — the monster shrinks… but comes back at every meal
    def s_pay(g):
        st_ = L("pay").start
        t_enc, t_vue = c("pay", "encoge"), c("pay", "vuelve")
        img = street_bg(g, scroll=(g - st_) * 70, tod="night")
        paste(img, walker(g), 170, 330, scale=2.4)
        k = ease_io(prog(g, t_enc - 0.2, 0.9))
        back = ease_back(prog(g, t_vue, 0.4))
        paste(img, cv.villain("glucosa", "confused" if g < t_vue else "wink", g), 70, 240,
              scale=lerp(1.4, 0.45, k) + 0.6 * back, anchor="center")
        if g > t_vue:
            paste(img, cv.plate(True), 70, 300, scale=1.4, anchor="center")
        impact_text(img, "SE ENCOGE", 135, 108, g, t_enc, color=P["green"], scale=4, out_t=t_vue - 0.15)
        if g > t_vue:
            impact_text(img, "VUELVE EN CADA COMIDA", 135, 108, g, t_vue, color=P["gold"], scale=2)
        return img

    # 8. DISCLAIMER — calm frame, readable card
    def s_disc(g):
        img = gfx.darken(street_bg(g, scroll=g * 20, tod="night"), 0.35)
        paste(img, st.leo({"mouth": "flat", "arm_r": (30, 40)}, g), 135, 330, scale=2.4)
        card = gfx.new(250, 70)
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([1, 1, 248, 68], radius=6, fill=P["ink"], outline=P["red_l"], width=2)
        draw_text(card, "NO CURA LA DIABETES", 125, 9, color=P["white"], scale=2, align="center")
        draw_text(card, "NI REEMPLAZA EL TRATAMIENTO", 125, 38, color=P["fog"], align="center")
        draw_text(card, "ESTUDIOS DE CORTO PLAZO", 125, 52, color=P["fog"], align="center")
        paste_scaled(img, gfx.outline(card), 135, 150, pop_scale(g, c("disc", "ojo")))
        impact_text(img, "OJO", 135, 100, g, c("disc", "ojo"), color=P["red_l"], scale=4)
        return gfx.camera(img, 1.0 + 0.03 * math.sin(g * 1.1), 135, 230)

    # 9. CTA — same split composition as frame 1 (loop): sofa vs walk
    def s_cta(g):
        img = split_frame(g, cta=True)
        impact_text(img, "¿SOFÁ O CAMINATA?", 135, 92, g, L("cta").start + 0.1, color=P["white"], scale=3)
        return img

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("prob", "prob", s_prob, "whip_left", 0.25, 0.15),
        ("conf", "conf", s_conf, "cut", 0.2, 0.1),
        ("turn", "turn", s_turn, "cut", 0.2, 0.1),
        ("bio", "bio", s_bio, "cut", 0.2, 0.05),
        ("ev", "ev1", s_ev, "iris", 0.35, 0.15),
        ("pay", "pay", s_pay, "whip_left", 0.25, 0.15),
        ("disc", "disc", s_disc, "dither", 0.25, 0.1),
        ("cta", "cta", s_cta, "pixelate", 0.25, 0.1),
    ])
    emph = {norm(w): col for w, col in [("diez", P["green"]), ("treinta", P["gold"]), ("comprobó", P["gold"]),
            ("sueño", P["lav"]), ("monstruo", P["white"]), ("pico", P["red_l"]), ("bocado", P["red_l"]),
            ("levanta", P["green"]), ("caminar", P["green"]), ("contrae", P["muscle_l"]), ("puertas", P["gold"]),
            ("doce", P["green"]), ("veintidós", P["green"]), ("encoge", P["green"]), ("vuelve", P["gold"]),
            ("ojo", P["red_l"]), ("cura", P["red_l"]), ("sofá", P["red_l"]), ("caminata", P["green"])]}
    return Director(tl, scenes, SubStyle(y=356, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.25))
