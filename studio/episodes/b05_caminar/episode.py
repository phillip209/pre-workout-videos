"""B05 · "2 minutos caminando después de comer" — story format, EXP-001 test (outcome-first hook).

EXP-001 variable: the first frame and first sentence show the OUTCOME (lower sugar peak) instead of an
intriguing statement. Everything else follows the b01v2 template (~40 s).

Fact (checked 2026-11-14): Buffey AJ et al., Sports Med 2022;52:1765-1787 — meta-analysis of 7 acute lab
crossover studies: light-intensity walking breaks lowered post-meal glucose vs prolonged sitting (and vs
standing breaks); standing breaks lowered it less. Breaks lasted ~2-5 min. Acute, lab, short-term:
not evidence about diabetes incidence.
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from engine import W, H, gfx, fx, cast
from engine import cast_plus as cp, cast_villains as cv, story as st
from engine.gfx import P, prog, ease_out, ease_io, ease_back, lerp, paste
from engine.kit import label, scenes_from, impact_text, line_chart, street_bg, xray, text_sprite
from engine.director import Director, SubStyle
from engine.timeline import norm

SLUG = "b05_caminar"
EXPERIMENT = {"id": "EXP-001", "arm": "test", "hook_type": "outcome_first"}
BPM = 112
LEAD_IN = 0.08
TAIL = 1.4
NARRATION_FILE = "episodes/b05_caminar/narration.mp3"

LINES = [
    {"id": "hook", "text": "Dos minutos caminando después de comer... y su pico de azúcar fue más bajo."},
    {"id": "hook2", "text": "Así de poco.", "hold": 0.1},
    {"id": "ctx", "text": "Mediodía. Plato grande. Y después... horas sentado."},
    {"id": "mon", "text": "Al rato llega el monstruo: el pico de azúcar."},
    {"id": "turn", "text": "Pero esta vez, Leo se levantó."},
    {"id": "mech", "text": "Al caminar, los músculos de las piernas usan ese azúcar como combustible."},
    {"id": "data", "text": "Un análisis de siete estudios lo comparó con quedarse sentado."},
    {"id": "still", "text": "Y el monstruo... se encogía."},
    {"id": "setup", "text": "¿Y si solo se paraba?"},
    {"id": "reveal", "text": "Ayudaba un poco. ¡Pero caminar ayudaba más!", "hold": 0.1},
    {"id": "twist", "text": "Ojo: se midió en laboratorio y a corto plazo. No es una cura."},
    {"id": "cta", "text": "¿Cuántos minutos caminas tú después de comer?"},
]

TITLE = "2 minutos caminando después de comer: esto le pasó a su azúcar 🚶 #Shorts"
DESCRIPTION = (
    "Leo caminó 2 minutos después de comer… y su pico de azúcar fue más bajo que si se quedaba sentado.\n\n"
    "Fuente: Buffey et al., Sports Medicine, 2022 — metaanálisis de 7 estudios de laboratorio: hacer pausas "
    "caminando suave después de comer bajó el azúcar en sangre posterior a la comida frente a quedarse sentado, "
    "y más que solo ponerse de pie. Las pausas duraban entre 2 y 5 minutos. Son efectos a corto plazo medidos "
    "en laboratorio; no es un tratamiento ni una cura para la diabetes.\nContenido educativo, no es consejo "
    "médico.\nVoz: ElevenLabs.\n\n#caminar #glucosa #salud #azucarensangre #habitossaludables")
TAGS = ["caminar después de comer", "azúcar en sangre", "glucosa", "pausas activas", "qué le pasa a tu cuerpo"]


def sound_cues(tl):
    c, L = tl.cue, tl.line
    return [(0.0, "impact", 0.9), (0.0, "sparkle", 0.6),
            (c("hook", "minutos"), "step", 0.7), (c("hook", "minutos") + 0.25, "step", 0.7),
            (c("hook", "bajo"), "bar_down", 0.8), (c("hook2", "poco"), "ding", 0.7),
            (L("ctx").start - 0.25, "rewind", 0.9), (c("ctx", "plato"), "chomp", 0.7),
            (c("ctx", "sentado"), "thud", 0.6),
            (c("mon", "monstruo") - 0.1, "growl", 0.9), (c("mon", "monstruo"), "impact", 0.7),
            (c("mon", "pico"), "bar_up", 0.8),
            (c("turn", "levantó"), "whoosh", 0.6), (c("turn", "levantó") + 0.2, "step", 0.6),
            (L("mech").start, "scan", 0.9), (c("mech", "combustible"), "chomp", 0.7),
            (c("data", "siete"), "ding", 0.6), (c("data", "sentado"), "blip", 0.5),
            (c("still", "monstruo"), "deflate", 0.7), (c("still", "encogía"), "deflate", 0.8),
            (L("setup").start, "whoosh", 0.4),
            (c("reveal", "poco"), "blip", 0.6), (c("reveal", "caminar") - 0.04, "impact", 1.0),
            (c("reveal", "más"), "sparkle", 0.7),
            (c("twist", "ojo"), "alarm", 0.4), (c("twist", "cura"), "thud", 0.5),
            (L("cta").start - 0.1, "pop", 0.6), (c("cta", "comer"), "ding", 0.7)]


def music_sections(tl):
    c, L = tl.cue, tl.line
    t_hit = c("reveal", "caminar")
    return [(0.0, L("ctx").start - 0.25, "drive"), (L("ctx").start, L("mon").start, "groove"),
            (L("mon").start, L("turn").start - 0.1, "low"), (L("turn").start, L("still").start, "drive"),
            (L("still").start, L("setup").start, "pulse"), (L("setup").start, t_hit - 0.6, "mystery"),
            (t_hit - 0.6, t_hit, "silence"), (t_hit, L("twist").start, "triumph"),
            (L("twist").start, tl.total, "pulse")]


def half_gauge(v, g, lbl="PICO DE AZÚCAR"):
    gz = cp.gauge(v, g, lbl)
    return gz.resize((gz.width // 2, gz.height // 2), 0)


def make_director(tl):
    c, L = tl.cue, tl.line
    hudl = st.Hud([(0, 1)], 1, flashes=[0.15], text_fn=lambda g: "TRAS COMER")

    def office(g):
        return cv.office_bg(g, 0.1, None)

    # 1. HOOK — outcome first: the low sugar peak is on screen from frame 1
    s_hook = st.hook_closeup(
        office, hudl,
        beats=[(0, "happy", 0), (c("hook2", "poco") - 0.1, "shock", 0)],
        texts=[(0.0, c("hook", "bajo") - 0.15, "2 MIN CAMINANDO", P["green"], 3, 98),
               (c("hook", "bajo") - 0.1, c("hook2", "poco") - 0.15, "PICO MÁS BAJO", P["green"], 4, 98),
               (c("hook2", "poco"), None, "ASÍ DE POCO", P["gold"], 4, 100)],
        t_punch=c("hook2", "poco"),
        side=(0.0, L("ctx").start, lambda g: cp.gauge(lerp(0.75, 0.3, ease_io(prog(g, 0.2, 1.2))), g, "PICO"), 999),
        side_xy=(212, 300), side_scale=0.85)

    # 2. CONTEXT — rewind to lunch
    s_ctx = st.context_walk(
        lambda g, s: office(g), hudl, L("ctx").start, L("ctx").start, rewind=True, walk_px=0,
        items=[(c("ctx", "plato"), cv.plate(True), 70, None),
               (c("ctx", "sentado"), text_sprite("3 H", P["red_l"], scale=4), 200, None)],
        texts=[(c("ctx", "horas"), None, "HORAS SENTADO", P["red_l"], 3, 175)])

    # 3. VILLAIN — the sugar peak rises
    s_mon = st.villain_rise(
        office, hudl, "glucosa", c("mon", "monstruo"), c("mon", "pico"),
        leo_pose=lambda g, sc: {"mouth": "flat" if not sc else "o", "eyes": "sad" if sc else "open", "droop": 0.4},
        bars=[(c("mon", "pico"), "AZÚCAR EN SANGRE", 0.3, 0.9, P["red"], 1, 12)],
        texts=[(c("mon", "monstruo"), None, "EL PICO DE AZÚCAR", P["white"], 3, 112)], dark=0.15)

    # 4. TURN — he gets up and walks (street travelling)
    def s_turn(g):
        st_ = L("turn").start
        img = street_bg(g, scroll=max(0.0, g - st_) * 60, tod="sunrise")
        up = ease_back(prog(g, c("turn", "levantó") - 0.2, 0.4))
        walking = up >= 1
        paste(img, st.leo({"walk": g * 12 if walking else None, "mouth": "grin",
                           "arm_l": (20 * math.sin(g * 12), 30) if walking else (lerp(10, 160, up), 20),
                           "arm_r": (-20 * math.sin(g * 12), 30) if walking else (lerp(10, 160, up), 20)}, g),
              135, 330, scale=2.6)
        impact_text(img, "¡DE PIE!", 135, 108, g, c("turn", "levantó"), color=P["green"], scale=5)
        hudl(img, g)
        return img

    # 5. MECHANISM — x-ray: leg muscle eats the sugar
    def muscle_inner(g):
        img = cast.tissue_bg(g, hue="pink")
        fib = cast.muscle_fiber(100, 26, mood="happy", nuclei=5, t=g, glow=0.3)
        paste(img, fib, 135, 220, scale=2.0, anchor="center")
        for i in range(7):
            ph = (g * 0.9 + i * 0.14) % 1
            x = lerp(-10, 120, ph) if i % 2 else lerp(W + 10, 150, ph)
            y = 160 + i * 18
            if ph < 0.95:
                paste(img, cv.villain("glucosa", "sad", g, size=0.18), x, y, anchor="center")
        label(img, "MÚSCULO DE LA PIERNA", 135, 290, color=P["white"], scale=1)
        return img

    s_mech = st.xray_turn(lambda g: street_bg(g, scroll=g * 60, tod="sunrise"), hudl, L("mech").start, muscle_inner,
                          texts=[(c("mech", "combustible"), None, "COMBUSTIBLE", P["gold"], 4, 108)],
                          leo_pose={"walk": 0, "mouth": "grin"})

    # 6. DATA — two glucose curves
    t_7, t_sen = c("data", "siete"), c("data", "sentado")

    def draw_chart(img, g):
        box = (36, 110, 240, 280)
        sit = [(i / 20, 0.15 + 0.75 * math.exp(-((i / 20 - 0.35) ** 2) / 0.03)) for i in range(21)]
        walk = [(x, 0.15 + (y - 0.15) * 0.6) for x, y in sit]
        line_chart(img, box, sit, ease_io(prog(g, L("data").start, 1.2)), color=P["red_l"])
        if g > t_sen - 0.4:
            line_chart(img, box, walk, ease_io(prog(g, t_sen - 0.4, 1.0)), color=P["green"])
        label(img, "SENTADO", 200, 128, color=P["red_l"])
        if g > t_sen - 0.4:
            label(img, "CAMINANDO", 200, 214, color=P["green"])
        label(img, "AZÚCAR DESPUÉS DE COMER", 138, 292, color=P["fog"])
        # micro-motion once the chart is complete: a marker travels both curves (no still frame > 0.7 s)
        if g > t_sen - 0.2:
            from PIL import ImageDraw
            d = ImageDraw.Draw(img)
            u = (g * 0.7) % 1
            for pts, col in ((sit, P["red_l"]), (walk, P["green"])):
                yv = pts[int(u * 20)][1]
                x = box[0] + u * (box[2] - box[0])
                y = box[3] - yv * (box[3] - box[1])
                d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=col, outline=P["white"])

    s_data = st.inner_metric(lambda g: cast.lab_bg(g), hudl, draw_chart,
                             texts=[(t_7, t_sen - 0.5, "7 ESTUDIOS", P["gold"], 3, 84)],
                             src="BUFFEY 2022 · METAANÁLISIS · LABORATORIO")

    # 7. STILL — the monster shrinks while Leo walks
    def s_still(g):
        st_ = L("still").start
        img = street_bg(g, scroll=(g - st_) * 70, tod="sunrise")
        paste(img, st.leo({"walk": g * 12, "mouth": "smile", "arm_l": (20 * math.sin(g * 12), 30),
                           "arm_r": (-20 * math.sin(g * 12), 30)}, g), 170, 330, scale=2.4)
        k = ease_io(prog(g, c("still", "encogía") - 0.3, 1.0))
        paste(img, cv.villain("glucosa", "confused" if k > 0.3 else "sly", g), 70, 240 + 30 * k,
              scale=lerp(1.5, 0.5, k), anchor="center")
        impact_text(img, "SE ENCOGÍA", 135, 108, g, c("still", "encogía"), color=P["green"], scale=4)
        hudl(img, g)
        return img

    # 8. SETUP — standing only?
    s_setup = st.slowmo(office, hudl, L("setup").start, lambda k: {"mouth": "flat", "eyes": "open"},
                        texts=[(L("setup").start + 0.1, None, "¿SOLO DE PIE?", P["white"], 4, 100)], zoom=0.3)

    # 9. REVEAL
    t_hit = c("reveal", "caminar")
    s_reveal = st.reveal_closeup(
        office, hudl, t_hit, ("BAJA DEL PICO", 0.3, 0.85, t_hit - 0.05),
        texts=[(c("reveal", "poco") - 0.2, t_hit - 0.15, "DE PIE: UN POCO", P["fat_l"], 3, 104),
               (t_hit - 0.05, None, "CAMINAR: MÁS", P["green"], 4, 104)],
        mood_pre="neutral", mood_hit="happy", src="BUFFEY 2022 · DE PIE VS CAMINAR")

    # 10. TWIST + CTA — loops to the hook framing
    s_end = st.twist_loop(
        office, hudl, "glucosa", c("twist", "ojo"), c("twist", "cura"), L("cta").start,
        cta_lines=(("¿CUÁNTOS MINUTOS", P["white"]), ("CAMINAS TÚ?", P["green"])),
        src="BUFFEY 2022 · CORTO PLAZO", villain_mood="sly",
        extra_texts=[(c("twist", "laboratorio"), L("cta").start - 0.15, "NO ES UNA CURA", P["red_l"], 3, 150)])

    scenes = scenes_from(tl, [
        ("hook", "hook", s_hook, "cut", 0.3, 0),
        ("ctx", "ctx", s_ctx, "cut", 0.2, 0.3),
        ("mon", "mon", s_mon, "pixelate", 0.3, 0.2),
        ("turn", "turn", s_turn, "whip_left", 0.25, 0.15),
        ("mech", "mech", s_mech, "cut", 0.2, 0.1),
        ("data", "data", s_data, "dither", 0.25, 0.2),
        ("still", "still", s_still, "whip_left", 0.25, 0.15),
        ("setup", "setup", s_setup, "iris", 0.35, 0.2),
        ("reveal", "reveal", s_reveal, "cut", 0.15, 0.1),
        ("end", "twist", s_end, "pixelate", 0.25, 0.1),
    ])
    emph = {norm(w): col for w, col in [("minutos", P["green"]), ("caminando", P["green"]), ("bajo", P["green"]),
            ("poco", P["gold"]), ("sentado", P["red_l"]), ("monstruo", P["white"]), ("pico", P["red_l"]),
            ("levantó", P["green"]), ("combustible", P["gold"]), ("siete", P["gold"]), ("encogía", P["green"]),
            ("paraba", P["fat_l"]), ("caminar", P["green"]), ("ojo", P["red_l"]), ("cura", P["red_l"])]}
    return Director(tl, scenes, SubStyle(y=356, scale=2, max_chars=15, emph=emph),
                    post=lambda img, t: gfx.vignette_cached(img, 0.25))
