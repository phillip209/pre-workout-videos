"""B05C · "Caminar después de comer" — Leo Cristal format (glass body + realistic skeleton), native 1080x1920.

Narrative: curiosity → discovery → contrast → explanation → revelation → practical takeaway.
Scientific basis (verified 2026-11-18, see docs/entregas/b05_caminar_v2.md):
- Buffey 2022 (Sports Med, meta-analysis of 7 acute lab studies): light walking breaks lowered post-meal
  glucose vs sitting. Reynolds 2016 (Diabetologia, RCT, 41 adults with T2D): walking after meals lowered
  post-meal glycaemia vs one daily walk. Richter & Hargreaves 2013 (Physiol Rev): contraction moves GLUT4
  to the muscle surface and increases glucose uptake.
- The curves shown are ILLUSTRATIVE (labelled on screen). No numbers are claimed in this version.
- Walking is not a cure and does not replace treatment (said and shown).
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from engine.crystal.core import (W, H, C, Cam, Frame, rgba, lerp, clamp, prog, ease_io, ease_out, ease_in, text,
                                 glow_dot)
from engine.crystal import skeleton as sk, worlds as wd
from engine.crystal.director import CineDirector, Shot
from engine.timeline import norm

SLUG = "b05c_cristal"
NATIVE = True
BPM = 92
LEAD_IN = 0.1
TAIL = 1.5
NARRATION_FILE = "episodes/b05c_cristal/narration.mp3"

LINES = [
    {"id": "hook", "text": "¿Sabías que caminar después de comer puede cambiar lo que pasa dentro de tu cuerpo?"},
    {"id": "prob", "text": "Después de comer, la glucosa de los alimentos pasa a la sangre."},
    {"id": "contra", "text": "Pero si te quedas sentado, tus músculos están casi en reposo."},
    {"id": "mech", "text": "Cuando caminas, tus músculos se contraen… y pueden captar glucosa de la sangre para usarla como energía."},
    {"id": "reveal", "text": "Por eso, varios estudios han visto que caminar después de comer puede reducir la subida de glucosa."},
    {"id": "pay", "text": "No hace falta entrenar fuerte: una caminata ligera es un buen comienzo."},
    {"id": "disc", "text": "Eso sí: no cura la diabetes ni reemplaza un tratamiento."},
    {"id": "cta", "text": "¿Tú caminas después de comer… o te quedas sentado?"},
]

TITLE = "¿Qué le pasa a tu glucosa si caminas después de comer? 🚶 #Shorts"
DESCRIPTION = (
    "Leo Cristal termina de comer… y sale a caminar. ¿Qué pasa con la glucosa dentro de su cuerpo?\n\n"
    "Lo que muestra el video:\n"
    "· Después de comer, la glucosa de los alimentos pasa a la sangre.\n"
    "· Al contraerse, los músculos llevan el transportador GLUT4 a su superficie y captan más glucosa "
    "(Richter y Hargreaves, Physiological Reviews, 2013).\n"
    "· Caminar suave después de comer bajó la subida de glucosa frente a quedarse sentado en estudios de "
    "laboratorio (Buffey et al., Sports Medicine, 2022, metaanálisis de 7 estudios) y en un ensayo con adultos "
    "con diabetes tipo 2 (Reynolds et al., Diabetologia, 2016).\n"
    "Las curvas del video son ilustrativas, no datos de un estudio. No cura la diabetes ni reemplaza un "
    "tratamiento. Contenido educativo, no es consejo médico.\nVoz: ElevenLabs.\n\n"
    "#caminar #glucosa #salud #cuerpohumano #habitossaludables")
TAGS = ["caminar después de comer", "glucosa", "azúcar en sangre", "cuerpo humano", "músculos"]

EMPH = {norm(w): c for w, c in [("glucosa", (210, 120, 20)), ("sangre", (200, 40, 50)), ("sentado", (90, 100, 130)),
        ("reposo", (90, 100, 130)), ("caminas", (20, 150, 110)), ("contraen", (200, 80, 40)),
        ("energía", (210, 120, 20)), ("estudios", (60, 110, 200)), ("subida", (200, 40, 50)),
        ("ligera", (20, 150, 110)), ("cura", (200, 40, 50))]}


# ---------------------------------------------------------------- sound
def sound_cues(tl):
    c, L = tl.cue, tl.line
    cues = [(0.0, "clink", 0.7), (0.35, "clink", 0.5), (c("hook", "caminar"), "slide", 0.6),
            (c("hook", "cuerpo") - 0.3, "swell", 0.7),
            (L("prob").start - 0.25, "whoosh", 0.6), (c("prob", "glucosa"), "bubble", 0.6),
            (c("prob", "sangre") - 0.3, "whoosh", 0.4), (c("prob", "sangre"), "heartbeat", 0.6),
            (L("contra").start - 0.1, "whoosh", 0.3), (c("contra", "sentado"), "thud", 0.4),
            (c("contra", "reposo") - 0.2, "swell", 0.5),
            (c("mech", "contraen"), "clank", 0.35), (c("mech", "captar"), "bubble", 0.6),
            (c("mech", "energía"), "sparkle", 0.7),
            (L("reveal").start - 0.1, "swell", 0.6), (c("reveal", "subida"), "ding", 0.6),
            (c("disc", "cura"), "thud", 0.4),
            (L("cta").start - 0.15, "clink", 0.5), (c("cta", "sentado"), "pop", 0.4)]
    for (a, b) in ((c("mech", "caminas"), L("mech").start + 2.0), (L("reveal").start + 2.6, L("disc").end)):
        k = a
        while k < b:
            cues.append((k, "soft_step", 0.4))
            k += 0.5
    return cues


def music_sections(tl):
    c, L = tl.cue, tl.line
    return [(0.0, L("prob").start, "c_wonder"), (L("prob").start, L("contra").start, "c_pulse"),
            (L("contra").start, L("mech").start, "c_amb"), (L("mech").start, L("reveal").start - 0.4, "c_lift"),
            (L("reveal").start - 0.4, L("reveal").start + 0.2, "silence"),
            (L("reveal").start + 0.2, L("disc").start, "c_resolve"), (L("disc").start, L("cta").start, "c_amb"),
            (L("cta").start, tl.total, "c_wonder")]


# ---------------------------------------------------------------- shots
def make_director(tl):
    c, L = tl.cue, tl.line
    T = {k: L(k).start for k in ("hook", "prob", "contra", "mech", "reveal", "pay", "disc", "cta")}
    t_blood = c("prob", "sangre") - 0.35
    t_inside_rest = c("contra", "reposo") - 0.25
    t_inside_work = c("mech", "contraen") - 0.15
    t_face = c("reveal", "subida") - 0.6

    def blink(g):
        return (g % 3.3) < 0.12 and g > 0.4

    def fr_dining(g, cam, pose):
        f = Frame()
        wd.dining(f, g, dx=(cam.x) * 0.08, dy=(cam.y + 250) * 0.05)
        sk.draw(f, cam, pose)
        wd.table_front(f, cam, g, plate=pose.pop("_plate", 1.0) if "_plate" in pose else 1.0)
        return f.compose(bloom=0.8)

    # 1. HOOK — ECU plate, crane up to Leo finishing his bite, he pushes back and starts to rise
    def s_hook(g):
        k = ease_io(prog(g, 0.25, 1.7))
        cam = Cam.blend(Cam(40, 40, 3.0), Cam(0, -260, 1.18), k)
        t_up = c("hook", "caminar")
        up = ease_io(prog(g, t_up, 1.4))
        bite = abs(math.sin(g * 3.2)) if g < t_up else 0
        pose = dict(sk.DEFAULT, t=g, seat=1 - up, y=-150 * up, expr="chew" if g < t_up - 0.2 else ("curious" if up < 0.6 else "happy"),
                    arm_r=(lerp(30, 12, up), lerp(150 * bite + 60, 14, up)), hold_r="fork" if up < 0.5 else None,
                    arm_l=(lerp(40, 12, up), lerp(80, 14, up)), look=(0.0, -0.2 if up < 0.5 else 0.0), blink=blink(g),
                    hl={"stomach": prog(g, c("hook", "dentro") - 0.5, 0.8)} if g > c("hook", "dentro") - 0.5 else {},
                    lean=-3 * up)
        pose["_plate"] = lerp(1.0, 0.25, prog(g, 0.0, t_up))
        return fr_dining(g, cam, pose)

    # 2. PROBLEM — dolly into the abdomen; inside: gut -> glucose crossing into a capillary; then the bloodstream
    def s_gut(g):
        f = Frame()
        wd.gut_world(f, g, k_absorb=ease_io(prog(g, c("prob", "glucosa") - 0.3, 1.0)))
        return f.compose(bloom=0.9)

    def s_blood(g):
        f = Frame()
        lvl = ease_io(prog(g, t_blood, 2.0)) * 0.9 + 0.1
        wd.blood_world(f, g, level=lvl)
        # clean indicator (top-left, inside safe area)
        d = ImageDraw.Draw(f.top)
        d.rounded_rectangle([70, 220, 470, 300], radius=20, fill=(10, 14, 30, 180))
        text(f.top, "Glucosa en sangre", 270, 245, size=34, color=C["white"], stroke=0)
        d.rounded_rectangle([100, 270, 440, 286], radius=8, fill=(40, 40, 60, 255))
        d.rounded_rectangle([100, 270, 100 + 340 * lvl, 286], radius=8, fill=C["orange"] + (255,))
        return f.compose(bloom=0.9)

    # 3. CONTRAST — on the sofa, still; dolly down to the legs (cool, resting muscles), then inside
    def s_sofa(g):
        st = T["contra"]
        k = ease_io(prog(g, st + 0.2, 2.2))
        cam = Cam.blend(Cam(0, -230, 1.05), Cam(40, 180, 2.0), k)
        f = Frame()
        wd.living(f, g, dx=cam.x * 0.1, dy=(cam.y + 230) * -0.06)
        wd.sofa(f, cam)
        pose = dict(sk.DEFAULT, t=g, seat=1.0, expr="tired", blink=blink(g), arm_l=(30, 40), arm_r=(30, 40),
                    lean=-4, head=4, hl={"legs": 0.0}, look=(0.6, 0.3))
        sk.draw(f, cam, pose)
        wd.sofa(f, cam, front=True)
        if g > c("contra", "músculos") - 0.2:
            text(f.top, "MÚSCULOS EN REPOSO", W / 2, 300, size=50, color=C["cyan_l"], stroke=5,
                 alpha=ease_out(prog(g, c("contra", "músculos") - 0.2, 0.4)))
        return f.compose(bloom=0.7)

    def s_rest_inside(g):
        f = Frame()
        wd.muscle_world(f, g, active=0.0, flex=0.0, gates=0.0, uptake=0.0)
        text(f.top, "En reposo: la glucosa pasa de largo", W / 2, 300, size=42, color=C["cyan_l"], stroke=4)
        return f.compose(bloom=0.8)

    # 4. MECHANISM — he walks (dolly back, then tilt down to the legs); inside the working muscle
    def walk_cam(g, t0, tilt=0.0):
        k = ease_io(prog(g, t0 + 0.6, 1.6)) * tilt
        return Cam.blend(Cam(0, -200, 0.95), Cam(30, 220, 1.9), k)

    def s_walk(g):
        st = T["mech"]
        ph = (g - st) * 6.3
        cam = walk_cam(g, st, tilt=1.0)
        f = Frame()
        wd.park(f, g, travel=(g - st) * 260, dx=cam.x * 0.2, dy=(cam.y + 200) * -0.15)
        flex = 0.5 + 0.5 * math.sin(ph)
        pose = sk.walk_front(ph, t=g, expr="happy", blink=blink(g), hl={"legs": 1.0}, flex=flex)
        sk.draw(f, cam, pose)
        return f.compose(bloom=0.9)

    def s_work_inside(g):
        f = Frame()
        flex = 0.5 + 0.5 * math.sin((g - T["mech"]) * 6.3)
        gates = ease_io(prog(g, c("mech", "captar") - 0.4, 0.8))
        wd.muscle_world(f, g, active=1.0, flex=flex, gates=gates, uptake=gates * 0.5)
        if g > c("mech", "captar") - 0.2:
            text(f.top, "Las «puertas» GLUT4 se abren", W / 2, 300, size=44, color=C["violet_l"], stroke=4,
                 alpha=ease_out(prog(g, c("mech", "captar") - 0.2, 0.4)))
        if g > c("mech", "energía") - 0.2:
            text(f.top, "Parte de la glucosa entra al músculo", W / 2, 362, size=36, color=C["orange_l"], stroke=4,
                 alpha=ease_out(prog(g, c("mech", "energía") - 0.2, 0.4)))
        return f.compose(bloom=1.0)

    # 5. REVELATION — illustrative curves, then Leo walking toward camera reacts
    def s_viz(g):
        f = Frame()
        st = T["reveal"]
        wd.viz_world(f, g, p_sit=ease_io(prog(g, st + 0.3, 1.6)), p_walk=ease_io(prog(g, st + 1.4, 1.6)),
                     cam_shift=g * 20)
        text(f.top, "Basado en: Buffey 2022 (metaanálisis) · Reynolds 2016", W / 2, 1180, size=30,
             color=(150, 170, 210), stroke=0)
        return f.compose(bloom=0.9)

    def s_react(g):
        ph = g * 6.3
        cam = Cam(0, -380, 1.55 + 0.1 * prog(g, t_face, 2.0))
        f = Frame()
        wd.park(f, g, travel=g * 260, dy=40)
        surprised = g < t_face + 0.7
        pose = sk.walk_front(ph, t=g, expr="surprised" if surprised else "happy", look=(0.0, 0.0), blink=blink(g))
        sk.draw(f, cam, pose)
        return f.compose(bloom=0.8)

    # 6. PAYOFF — wide cinematic shot, relaxed walk, crane out
    def s_wide(g):
        st = T["pay"]
        k = ease_io(prog(g, st, 3.6))
        cam = Cam.blend(Cam(0, -150, 0.9), Cam(0, -40, 0.5), k)
        f = Frame()
        wd.park(f, g, travel=g * 220, dy=-60 * k)
        pose = sk.walk_front(g * 5.2, t=g, expr="happy", blink=blink(g), hl={"legs": 0.4}, flex=0.3)
        sk.draw(f, cam, pose)
        if g > c("pay", "ligera") - 0.2:
            text(f.top, "CAMINATA LIGERA", W / 2, 320, size=58, color=C["green"], stroke=6,
                 alpha=ease_out(prog(g, c("pay", "ligera") - 0.2, 0.4)))
        return f.compose(bloom=0.8)

    # 7. QUALIFICATION — medium shot, slows down; clean card
    def s_disc(g):
        cam = Cam(0, -300, 1.25)
        f = Frame()
        wd.park(f, g, travel=g * 120, dy=20)
        pose = sk.walk_front(g * 3.5, t=g, expr="neutral", blink=blink(g), arm_r=(20, 40))
        sk.draw(f, cam, pose)
        a = ease_out(prog(g, T["disc"] + 0.1, 0.4))
        d = ImageDraw.Draw(f.top)
        d.rounded_rectangle([110, 230, W - 110, 420], radius=30, fill=(10, 14, 30, int(210 * a)))
        text(f.top, "No cura la diabetes", W / 2, 290, size=54, color=C["white"], stroke=0, alpha=a)
        text(f.top, "ni reemplaza un tratamiento médico", W / 2, 360, size=40, color=C["cyan_l"], stroke=0, alpha=a)
        return f.compose(bloom=0.7)

    # 8. ENDING — back at the table (loops to frame 1): Leo looks at the viewer and asks
    def s_end(g):
        st = T["cta"]
        cam = Cam(0, -420, 1.9 + 0.25 * ease_io(prog(g, st, 3.0)))
        pose = dict(sk.DEFAULT, t=g, seat=1.0, expr="curious" if g < c("cta", "sentado") else "happy",
                    look=(0.0, 0.0), blink=blink(g), arm_r=(30, 60), arm_l=(30, 60), head=-3)
        pose["_plate"] = 1.0
        return fr_dining(g, cam, pose)

    shots = [
        Shot("hook", 0.0, s_hook),
        Shot("gut", T["prob"] - 0.15, s_gut, "dive", 0.6, (590, 1180)),
        Shot("blood", t_blood, s_blood, "bridge", 0.5, (W / 2, 1100)),
        Shot("sofa", T["contra"] - 0.1, s_sofa, "fade", 0.35),
        Shot("rest", t_inside_rest, s_rest_inside, "dive", 0.55, (W / 2 + 60, 1400)),
        Shot("walk", T["mech"] - 0.1, s_walk, "fade", 0.3),
        Shot("work", t_inside_work, s_work_inside, "dive", 0.5, (W / 2 - 40, 1100)),
        Shot("viz", T["reveal"] - 0.1, s_viz, "bridge", 0.55, (W / 2, 520)),
        Shot("react", t_face - 0.3, s_react, "cut"),
        Shot("wide", T["pay"] - 0.1, s_wide, "fade", 0.35),
        Shot("disc", T["disc"] - 0.1, s_disc, "cut"),
        Shot("end", T["cta"] - 0.15, s_end, "fade", 0.4),
    ]
    return CineDirector(tl, shots, EMPH)
