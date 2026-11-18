"""B05P · "Paco y la caminata después de comer" — Paco comedic storytelling (same style as b05c).

The narrator explains the science; Paco and the personified inner world (visual metaphors, labelled
"Ilustración") carry the comedy. Science basis unchanged from b05c (Buffey 2022, Reynolds 2016,
Richter & Hargreaves 2013). Curves are illustrative. Not a cure / not a treatment replacement.
Beat sheet: docs/entregas/b05p_paco.md
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from engine.crystal.core import W, H, C, Cam, Frame, rgba, lerp, clamp, prog, ease_io, ease_out, ease_in, text, glow_dot
from engine.crystal import skeleton as sk, worlds as wd, cells as ce
from engine.crystal.director import CineDirector, Shot
from engine.timeline import norm

SLUG = "b05p_paco"
NATIVE = True
BPM = 92
LEAD_IN = 0.1
TAIL = 1.6
NARRATION_FILE = "episodes/b05p_paco/narration.mp3"

LINES = [
    {"id": "hook", "text": "Paco acaba de comer…"},
    {"id": "hook2", "text": "y lo que haga ahora puede cambiar lo que pasa dentro de su cuerpo."},
    {"id": "prob", "text": "Después de comer, la glucosa de los alimentos pasa a la sangre."},
    {"id": "contra", "text": "Si se queda sentado, sus músculos están casi en reposo."},
    {"id": "turn", "text": "Pero cuando se levanta a caminar…"},
    {"id": "mech", "text": "sus músculos se contraen, y pueden captar glucosa de la sangre para usarla como energía."},
    {"id": "reveal", "text": "Por eso, varios estudios han visto que caminar después de comer puede reducir la subida de glucosa."},
    {"id": "pay1", "text": "Y no hace falta entrenar fuerte."},
    {"id": "pay2", "text": "Una caminata ligera es un buen comienzo."},
    {"id": "disc", "text": "Eso sí: no cura la diabetes ni reemplaza un tratamiento."},
    {"id": "cta", "text": "¿Y tú? ¿Caminas después de comer… o eres más de sofá, como Paco?"},
]

TITLE = "Paco comió y se tiró al sofá… mira lo que pasó en sus músculos 🛋️🚶 #Shorts"
DESCRIPTION = (
    "Paco acaba de comer. ¿Sofá o caminata? Lo que haga ahora cambia lo que pasa con la glucosa dentro de su "
    "cuerpo.\n\n"
    "La ciencia detrás:\n"
    "· Después de comer, la glucosa de los alimentos pasa a la sangre.\n"
    "· Al contraerse, los músculos llevan el transportador GLUT4 a su superficie y captan más glucosa "
    "(Richter y Hargreaves, Physiological Reviews, 2013).\n"
    "· Caminar suave después de comer redujo la subida de glucosa frente a quedarse sentado en estudios de "
    "laboratorio (Buffey et al., Sports Medicine, 2022, metaanálisis de 7 estudios) y en un ensayo con adultos "
    "con diabetes tipo 2 (Reynolds et al., Diabetologia, 2016).\n"
    "Las células con cara y el tobogán son metáforas visuales; las curvas son ilustrativas. No cura la "
    "diabetes ni reemplaza un tratamiento. Contenido educativo, no es consejo médico.\nVoz: ElevenLabs.\n\n"
    "#caminar #glucosa #salud #cuerpohumano #paco")
TAGS = ["caminar después de comer", "glucosa", "azúcar en sangre", "cuerpo humano", "Paco"]

EMPH = {norm(w): c for w, c in [("paco", (200, 40, 50)), ("glucosa", (210, 120, 20)), ("sangre", (200, 40, 50)),
        ("sentado", (90, 100, 130)), ("reposo", (90, 100, 130)), ("caminar", (20, 150, 110)),
        ("contraen", (200, 80, 40)), ("energía", (210, 120, 20)), ("estudios", (60, 110, 200)),
        ("subida", (200, 40, 50)), ("fuerte", (200, 80, 40)), ("ligera", (20, 150, 110)), ("cura", (200, 40, 50)),
        ("sofá", (120, 70, 50))]}


# ---------------------------------------------------------------- sound (gags get their own accents)
def sound_cues(tl):
    c, L = tl.cue, tl.line
    cues = []
    t = 0.0
    while t < c("hook", "comer") - 0.1:          # speed-eating
        cues.append((t, "chomp", 0.55))
        t += 0.18
    cues += [(0.0, "clink", 0.6), (c("hook", "comer"), "ding", 0.8), (c("hook", "comer") + 0.1, "sparkle", 0.6),
             (c("hook", "comer") + 0.45, "boing", 0.45),                                  # satisfied lean back
             (c("hook2", "dentro") - 0.3, "swell", 0.6),
             (L("prob").start - 0.25, "whoosh", 0.6), (c("prob", "glucosa"), "wiii", 0.6),
             (c("prob", "glucosa") + 0.8, "wiii", 0.5), (c("prob", "sangre"), "bubble", 0.6),
             (L("contra").start - 0.1, "slide", 0.5), (c("contra", "sentado"), "deflate", 0.6),
             (c("contra", "reposo") - 0.2, "whoosh", 0.4), (c("contra", "reposo") + 0.2, "snore", 0.7),
             (c("contra", "reposo") + 0.9, "knock", 0.7),
             (L("turn").start + 0.1, "breath", 0.8),                                       # the sigh
             (c("turn", "levanta") + 0.05, "boing", 0.4), (c("turn", "caminar"), "soft_step", 0.6),
             (L("mech").start - 0.1, "alarm", 0.55), (L("mech").start + 0.4, "alarm", 0.4),
             (c("mech", "contraen"), "clank", 0.4), (c("mech", "captar"), "pop", 0.6), (c("mech", "captar") + 0.6, "knock", 0.6),
             (c("mech", "energía"), "sparkle", 0.7),
             (L("reveal").start - 0.1, "swell", 0.5), (c("reveal", "subida"), "ding", 0.6),
             (c("pay1", "fuerte") - 0.2, "whoosh", 0.6), (c("pay1", "fuerte") + 0.5, "breath", 0.8),
             (c("pay2", "ligera"), "pop", 0.5),
             (c("disc", "cura"), "thud", 0.4),
             (L("cta").start, "clink", 0.5), (c("cta", "sofá"), "boing", 0.5)]
    for (a, b, step) in ((c("turn", "caminar"), L("turn").end + 0.4, 0.5), (L("reveal").end - 1.2, L("pay1").start, 0.5),
                         (c("pay1", "fuerte") - 0.2, c("pay1", "fuerte") + 0.4, 0.16), (L("pay2").start, L("disc").end, 0.55)):
        k = a
        while k < b:
            cues.append((k, "soft_step", 0.4))
            k += step
    return cues


def music_sections(tl):
    c, L = tl.cue, tl.line
    return [(0.0, L("prob").start, "c_wonder"), (L("prob").start, L("contra").start, "c_lift"),
            (L("contra").start, L("turn").start, "c_amb"), (L("turn").start, L("mech").start, "silence"),
            (L("mech").start, L("reveal").start - 0.3, "c_pulse"), (L("reveal").start - 0.3, L("reveal").start + 0.2, "silence"),
            (L("reveal").start + 0.2, L("disc").start, "c_resolve"), (L("disc").start, L("cta").start, "c_amb"),
            (L("cta").start, tl.total, "c_wonder")]


# ---------------------------------------------------------------- shots
def make_director(tl):
    c, L = tl.cue, tl.line
    T = {k: L(k).start for k in ("hook", "hook2", "prob", "contra", "turn", "mech", "reveal", "pay1", "pay2", "disc", "cta")}
    t_full = c("hook", "comer")

    def blink(g):
        return (g % 3.1) < 0.12 and g > 0.5

    def dining_frame(g, cam, pose, plate):
        f = Frame()
        wd.dining(f, g, dx=cam.x * 0.08, dy=(cam.y + 250) * 0.05)
        sk.draw(f, cam, pose)
        wd.table_front(f, cam, g, plate=plate, steam=plate > 0.3)
        return f

    # 1. HOOK — Paco speed-eats; spotless plate; leans back, pats belly; side-eye to camera
    def s_hook(g):
        cam = Cam.blend(Cam(30, 20, 2.6), Cam(0, -280, 1.15), ease_io(prog(g, 0.1, 1.3)))
        eating = g < t_full
        fast = abs(math.sin(g * 17))
        if eating:
            pose = dict(sk.DEFAULT, t=g, seat=1.0, expr="chew", hold_r="fork", arm_r=(30, 60 + 100 * fast),
                        arm_l=(36, 70), look=(0, 0.4))
        else:
            k = ease_out(prog(g, t_full + 0.3, 0.5))
            pat = 70 + 12 * math.sin(g * 9)
            look_cam = g > c("hook2", "dentro") - 0.6
            pose = dict(sk.DEFAULT, t=g, seat=1.0, y=lerp(0, 30, k), head=lerp(0, 8, k),
                        expr="sarcastic" if look_cam else "satisfied",
                        arm_r=(15, pat), arm_l=(lerp(36, 95, k), -15), blink=blink(g),
                        hl={"stomach": prog(g, c("hook2", "dentro") - 0.5, 0.6)} if g > c("hook2", "dentro") - 0.5 else {})
        plate = max(0.0, 1 - g / max(0.5, t_full))
        f = dining_frame(g, cam, pose, plate)
        if not eating and g - t_full < 0.8:
            px, py = cam.p(0, 30)
            for k in range(5):
                a = k * 1.25 + g
                glow_dot(f, px + math.cos(a) * 180, py - 30 + math.sin(a) * 50, 10, C["white"], 0.9 * (1 - (g - t_full) / 0.8))
        return f.compose(bloom=0.8)

    # 2. PROBLEM — dive into the belly: the glucose water slide into the blood
    def s_slide(g):
        f = Frame()
        ce.slide_world(f, g, level=ease_io(prog(g, c("prob", "sangre") - 0.5, 1.5)))
        return f.compose(bloom=0.8)

    # 3. CONTRAST — Paco melts into the sofa; inside, the muscle cells are asleep (NO MOLESTAR)
    def s_sofa(g):
        st = T["contra"]
        melt = ease_out(prog(g, st, 1.2))
        k = ease_io(prog(g, c("contra", "músculos") - 0.2, 1.2))
        cam = Cam.blend(Cam(0, -230, 1.05), Cam(40, 160, 1.9), k)
        f = Frame()
        wd.living(f, g, dx=cam.x * 0.1, dy=(cam.y + 230) * -0.06)
        wd.sofa(f, cam)
        pose = dict(sk.DEFAULT, t=g, seat=1.0, y=lerp(0, 70, melt), head=lerp(0, 14, melt), expr="tired",
                    arm_l=(lerp(30, 100, melt), -20), arm_r=(lerp(30, 100, melt), -20), blink=blink(g),
                    hl={"legs": 0.0}, look=(0.5, 0.3))
        sk.draw(f, cam, pose)
        wd.sofa(f, cam, front=True)
        return f.compose(bloom=0.7)

    def s_sleep_cells(g):
        f = Frame()
        ce.cells_world(f, g, wake=0.0)
        return f.compose(bloom=0.8)

    # 4. TURN — the sigh, the look to camera, the reluctant stand-up (anticipation + follow-through)
    def s_turn(g):
        st = T["turn"]
        t_up = c("turn", "levanta")
        sigh = math.sin(clamp((g - st) / 0.9) * math.pi)
        dip = math.sin(clamp((g - t_up + 0.25) / 0.3) * math.pi) if t_up - 0.25 < g < t_up + 0.05 else 0
        up = ease_out(prog(g, t_up, 0.6))
        cam = Cam(0, -260, 1.1)
        f = Frame()
        wd.living(f, g, dy=-20)
        wd.sofa(f, cam)
        walking = g > c("turn", "caminar")
        if walking:
            pose = sk.walk_front((g - c("turn", "caminar")) * 5.5, t=g, expr="tired", y=-150, blink=blink(g))
        else:
            pose = dict(sk.DEFAULT, t=g, seat=1 - up, y=lerp(70, -150, up) + 25 * dip,
                        expr="sarcastic" if g < t_up - 0.1 else "tired", look=(0, 0), blink=blink(g),
                        arm_l=(lerp(100, 14, up), lerp(-20, 14, up)), arm_r=(lerp(100, 14, up), lerp(-20, 14, up)),
                        bob=-14 * sigh, head=lerp(8, 0, up))
        sk.draw(f, cam, pose)
        if not walking and up < 0.5:
            wd.sofa(f, cam, front=True)
        return f.compose(bloom=0.7)

    # 5. MECHANISM — alarm inside: cells jolt awake, open the doors, pull glucose in; one keeps sleeping (bonk)
    def s_work_cells(g):
        st = T["mech"]
        wake = ease_io(prog(g, st, 1.0))
        gates = ease_io(prog(g, c("mech", "captar") - 0.4, 0.8))
        f = Frame()
        ce.cells_world(f, g, wake=wake, gates=gates, uptake=gates * 0.6, alarm=1 - prog(g, st + 1.2, 0.6),
                       sleepy_until=c("mech", "captar") + 0.6, bonk_t=c("mech", "captar") + 0.1)
        return f.compose(bloom=0.9)

    # 6. REVEAL — illustrative curves, then Paco walking, proud
    def s_viz(g):
        f = Frame()
        st = T["reveal"]
        wd.viz_world(f, g, p_sit=ease_io(prog(g, st + 0.3, 1.6)), p_walk=ease_io(prog(g, st + 1.4, 1.6)), cam_shift=g * 20)
        text(f.top, "Basado en: Buffey 2022 (metaanálisis) · Reynolds 2016", W / 2, 1180, size=30, color=(150, 170, 210), stroke=0)
        return f.compose(bloom=0.9)

    def s_proud(g):
        cam = Cam(0, -360, 1.45)
        f = Frame()
        wd.park(f, g, travel=g * 260, dy=40)
        pose = sk.walk_front(g * 6.0, t=g, expr="happy", blink=blink(g), hl={"legs": 0.6}, flex=0.5)
        sk.draw(f, cam, pose)
        return f.compose(bloom=0.8)

    # 7. PAYOFF — overconfident sprint → out of breath in 3 steps → "ligera" → nods, relaxed stroll
    def s_sprint(g):
        st = T["pay1"]
        t_f = c("pay1", "fuerte")
        cam = Cam(0, -300, 1.2)
        f = Frame()
        sprinting = t_f - 0.25 < g < t_f + 0.45
        wd.park(f, g, travel=g * (700 if sprinting else 120), dy=20)
        if g < t_f - 0.25:                     # wind-up: overconfident
            pose = dict(sk.DEFAULT, t=g, y=-150, expr="sarcastic", look=(0, 0), arm_l=(40, 120), arm_r=(40, 120),
                        blink=blink(g))
        elif sprinting:
            pose = sk.walk_front((g - st) * 18, t=g, expr="happy", y=-150, leg_l=(6, 1.0 * max(0, math.sin((g - st) * 18))),
                                 leg_r=(6, 1.0 * max(0, -math.sin((g - st) * 18))))
        else:                                  # exhausted, hands on knees, panting
            pose = dict(sk.DEFAULT, t=g, y=-110, lean=0, head=6, expr="panting", arm_l=(18, -12), arm_r=(18, -12),
                        bob=-6 * abs(math.sin(g * 8)), look=(0, 0.2))
        sk.draw(f, cam, pose)
        return f.compose(bloom=0.7)

    def s_stroll(g):
        st = T["pay2"]
        k = ease_io(prog(g, st, 3.0))
        cam = Cam.blend(Cam(0, -200, 1.0), Cam(0, -60, 0.6), k)
        f = Frame()
        wd.park(f, g, travel=g * 200, dy=-50 * k)
        nod = c("pay2", "ligera")
        pose = sk.walk_front(g * 5.0, t=g, expr="satisfied" if g < nod + 0.6 else "happy", blink=blink(g),
                             head=6 * math.sin(clamp((g - nod) / 0.5) * math.pi * 2) if nod < g < nod + 0.5 else 0)
        sk.draw(f, cam, pose)
        if g > nod - 0.2:
            text(f.top, "CAMINATA LIGERA", W / 2, 320, size=58, color=C["green"], stroke=6, alpha=ease_out(prog(g, nod - 0.2, 0.4)))
        return f.compose(bloom=0.8)

    # 8. QUALIFICATION — serious beat, clean card; Paco nods
    def s_disc(g):
        cam = Cam(0, -300, 1.25)
        f = Frame()
        wd.park(f, g, travel=g * 110, dy=20)
        pose = sk.walk_front(g * 3.4, t=g, expr="neutral", blink=blink(g))
        sk.draw(f, cam, pose)
        a = ease_out(prog(g, T["disc"] + 0.1, 0.4))
        d = ImageDraw.Draw(f.top)
        d.rounded_rectangle([110, 230, W - 110, 420], radius=30, fill=(10, 14, 30, int(210 * a)))
        text(f.top, "No cura la diabetes", W / 2, 290, size=54, color=C["white"], stroke=0, alpha=a)
        text(f.top, "ni reemplaza un tratamiento médico", W / 2, 360, size=40, color=C["cyan_l"], stroke=0, alpha=a)
        return f.compose(bloom=0.7)

    # 9. ENDING — back at the table: dessert slides in; Paco looks at it… at the sofa… at us (loop)
    def s_end(g):
        st = T["cta"]
        cam = Cam(0, -420, 1.85 + 0.2 * ease_io(prog(g, st, 3.0)))
        t_sofa = c("cta", "sofá")
        look = (0.0, 0.5) if g < st + 1.2 else ((-1.0, 0.0) if g < t_sofa + 0.2 else (0.0, 0.0))
        expr = "curious" if g < st + 1.2 else ("worried" if g < t_sofa + 0.2 else "sarcastic")
        pose = dict(sk.DEFAULT, t=g, seat=1.0, expr=expr, look=look, blink=blink(g), arm_r=(30, 60), arm_l=(30, 60))
        f = dining_frame(g, cam, pose, plate=ease_out(prog(g, st, 0.6)))
        return f.compose(bloom=0.8)

    shots = [
        Shot("hook", 0.0, s_hook),
        Shot("slide", T["prob"] - 0.15, s_slide, "dive", 0.6, (590, 1250)),
        Shot("sofa", T["contra"] - 0.1, s_sofa, "fade", 0.35),
        Shot("sleep", c("contra", "reposo") - 0.1, s_sleep_cells, "dive", 0.5, (W / 2 + 60, 1400)),
        Shot("turn", T["turn"] - 0.15, s_turn, "fade", 0.3),
        Shot("work", T["mech"] - 0.1, s_work_cells, "dive", 0.45, (W / 2, 1300)),
        Shot("viz", T["reveal"] - 0.1, s_viz, "bridge", 0.55, (W / 2, 520)),
        Shot("proud", c("reveal", "subida") - 0.4, s_proud, "cut"),
        Shot("sprint", T["pay1"] - 0.1, s_sprint, "cut"),
        Shot("stroll", T["pay2"] - 0.1, s_stroll, "fade", 0.3),
        Shot("disc", T["disc"] - 0.1, s_disc, "cut"),
        Shot("end", T["cta"] - 0.15, s_end, "fade", 0.4),
    ]
    return CineDirector(tl, shots, EMPH)
