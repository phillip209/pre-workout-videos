"""PACO — official channel character v1 (2026-11-18; first drafted as "Leo Cristal").

A realistic bone-white skeleton inside a clear glass human body. Original design for PRE-WORKOUT:
big round eyes with amber irises, red headband with "PW" (channel signature), glass shell with soft
specular highlights. Organs and muscles appear only when the story explains them (`hl`).

Front-view rig (the only view, by design: frontal staging keeps the identity readable on a phone).
World units: pelvis centre at (x, y); full height ≈ 1000. Pose keys:
  x, y, lean, head (tilt deg), arm_l/arm_r = (abduction deg, elbow flex deg), leg_l/leg_r = (spread deg,
  knee lift 0..1), seat (0 standing, 1 seated, thighs toward camera), jaw (0..1), expr, look (dx, dy),
  blink, hold_r (prop drawn in the right hand: "fork"), hl (lit structures), glucose (0..1), flex (0..1), t.
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from .core import C, Cam, Frame, rgba, lerp, lerpc, clamp, capsule_poly, text

BONE = (234, 222, 198)
BONE_D = (150, 132, 108)
BONE_L = (253, 248, 236)
GLASS = (225, 240, 255)
IRIS = (176, 112, 52)
HEADBAND = (205, 38, 48)

DEFAULT = {"x": 0.0, "y": 0.0, "lean": 0.0, "head": 0.0, "arm_l": (12, 10), "arm_r": (12, 10),
           "leg_l": (3, 0.0), "leg_r": (3, 0.0), "seat": 0.0, "jaw": 0.0, "expr": "neutral", "look": (0.0, 0.0),
           "blink": False, "hold_r": None, "hl": {}, "glucose": 0.0, "flex": 0.0, "t": 0.0, "bob": 0.0}

SPINE, SH_W, UARM, FARM, HIP_W, THIGH, SHIN = 300, 128, 168, 158, 62, 232, 222


def walk_front(phase, **over):
    """Walking toward camera: alternating knee lift, counter-swinging arms, hip bob."""
    s = math.sin(phase)
    p = dict(DEFAULT)
    p.update({"leg_l": (4, max(0.0, s)), "leg_r": (4, max(0.0, -s)),
              "arm_l": (10 + 6 * s, 18 + 22 * max(0.0, -s)), "arm_r": (10 - 6 * s, 18 + 22 * max(0.0, s)),
              "bob": -10 * abs(math.cos(phase)), "lean": 1.5 * s})
    p.update(over)
    return p


def _rot(v, ang):
    r = math.radians(ang)
    return v[0] * math.cos(r) - v[1] * math.sin(r), v[0] * math.sin(r) + v[1] * math.cos(r)


def joints(pose):
    x, y = pose["x"], pose["y"] + pose.get("bob", 0.0)
    lean = pose["lean"]
    P = (x, y)
    N = (x + math.sin(math.radians(lean)) * SPINE, y - math.cos(math.radians(lean)) * SPINE)
    J = {"P": P, "N": N}
    for side, s in (("l", -1), ("r", 1)):
        sh = (N[0] + s * SH_W, N[1] + 18)
        a, e = pose["arm_" + side]
        ve = (s * math.sin(math.radians(a)), math.cos(math.radians(a)))
        elb = (sh[0] + ve[0] * UARM, sh[1] + ve[1] * UARM)
        a2 = a - e
        vw = (s * math.sin(math.radians(a2)), math.cos(math.radians(a2)))
        fl = FARM * (1 - 0.25 * clamp(e / 150))           # forearm foreshortens as it comes forward
        wri = (elb[0] + vw[0] * fl, elb[1] + vw[1] * fl)
        hip = (x + s * HIP_W, y + 12)
        spread, lift = pose["leg_" + side]
        seat = pose.get("seat", 0.0)
        tl = THIGH * (1 - 0.38 * lift) * (1 - 0.72 * seat)
        knee = (hip[0] + s * math.sin(math.radians(spread + 10 * seat)) * tl, hip[1] + math.cos(math.radians(spread)) * tl)
        sl = SHIN * (1 - 0.1 * lift)
        ank = (knee[0] + s * 4, knee[1] + sl)
        J.update({f"sh_{side}": sh, f"elb_{side}": elb, f"wri_{side}": wri, f"hip_{side}": hip,
                  f"knee_{side}": knee, f"ank_{side}": ank})
    hr = math.radians(pose["head"] + lean * 0.4)
    J["head"] = (N[0] + math.sin(hr) * 150, N[1] - math.cos(hr) * 150)
    J["head_ang"] = pose["head"] + lean * 0.4
    return J


# ---------------------------------------------------------------- bone painting (3-tone volume)
def _bone(d, cam, a, b, w, knob=0.0):
    pa, pb = cam.p(*a), cam.p(*b)
    ww = max(2, cam.s(w))
    d.line([pa, pb], fill=BONE_D + (255,), width=int(ww + max(2, cam.s(4))))
    d.line([pa, pb], fill=BONE + (255,), width=int(ww))
    off = ww * 0.22
    d.line([(pa[0] - off, pa[1] - off * 0.3), (pb[0] - off, pb[1] - off * 0.3)], fill=BONE_L + (255,),
           width=max(1, int(ww * 0.28)))
    if knob:
        for p in (pa, pb):
            _knob(d, p, cam.s(knob))


def _knob(d, p, r):
    x, y = p
    d.ellipse([x - r - 2, y - r - 2, x + r + 2, y + r + 2], fill=BONE_D + (255,))
    d.ellipse([x - r, y - r, x + r, y + r], fill=BONE + (255,))
    d.ellipse([x - r * 0.6, y - r * 0.75, x + r * 0.15, y - r * 0.1], fill=BONE_L + (255,))


def _poly_bone(d, pts, outline_w=3):
    d.polygon(pts, fill=BONE + (255,), outline=BONE_D + (255,))
    d.line(pts + [pts[0]], fill=BONE_D + (255,), width=outline_w)


# ---------------------------------------------------------------- glass shell
def _glass_shell(frame, cam, J, pose):
    lay = frame.layer()
    d = ImageDraw.Draw(lay)
    hl = frame.layer()
    hd = ImageDraw.Draw(hl)
    fill = rgba(GLASS, 0.13)
    edge = rgba((200, 225, 245), 0.55)
    shapes = []
    N, P = J["N"], J["P"]
    s = cam.s
    # torso
    tor = [(N[0] - 70, N[1] - 30), (N[0] - 150, N[1] + 15), (N[0] - 140, N[1] + 120), (P[0] - 112, P[1] - 120),
           (P[0] - 104, P[1] - 50), (P[0] - 128, P[1] + 20), (P[0] - 90, P[1] + 70), (P[0], P[1] + 60),
           (P[0] + 90, P[1] + 70), (P[0] + 128, P[1] + 20), (P[0] + 104, P[1] - 50), (P[0] + 112, P[1] - 120),
           (N[0] + 140, N[1] + 120), (N[0] + 150, N[1] + 15), (N[0] + 70, N[1] - 30)]
    shapes.append([cam.p(*q) for q in tor])
    # neck + head bubble
    hx, hy = J["head"]
    shapes.append(capsule_poly(cam.p(N[0], N[1] - 10), cam.p(hx, hy + 60), s(46), s(44)))
    head = []
    for k in range(36):
        a = k / 36 * math.tau
        rx, ry = 112, 128
        px, py = math.cos(a) * rx, math.sin(a) * ry - 8
        if py > 50:
            px *= 1 - 0.28 * (py - 50) / 70
        head.append(cam.p(hx + px, hy + py))
    shapes.append(head)
    for side in ("l", "r"):
        shapes.append(capsule_poly(cam.p(*J[f"sh_{side}"]), cam.p(*J[f"elb_{side}"]), s(44), s(36)))
        shapes.append(capsule_poly(cam.p(*J[f"elb_{side}"]), cam.p(*J[f"wri_{side}"]), s(36), s(28)))
        shapes.append(capsule_poly(cam.p(*J[f"hip_{side}"]), cam.p(*J[f"knee_{side}"]), s(66), s(46)))
        shapes.append(capsule_poly(cam.p(*J[f"knee_{side}"]), cam.p(*J[f"ank_{side}"]), s(46), s(32)))
        ax, ay = cam.p(*J[f"ank_{side}"])
        shapes.append([(ax - s(34), ay - s(6)), (ax + s(34), ay - s(6)), (ax + s(40), ay + s(30)), (ax - s(40), ay + s(30))])
        wx, wy = cam.p(*J[f"wri_{side}"])
        shapes.append([(wx - s(30), wy - s(10)), (wx + s(30), wy - s(10)), (wx + s(26), wy + s(62)), (wx - s(26), wy + s(62))])
    for sh in shapes:
        d.polygon(sh, fill=fill)
    head_hl = frame.layer()
    for i, sh in enumerate(shapes):
        if i == 1:      # neck: fill only, its rim would cross the face
            continue
        target = ImageDraw.Draw(head_hl) if i == 2 else hd
        target.line(sh + [sh[0]], fill=edge, width=max(2, int(s(4))))
        # specular: a brighter thin rim on the upper-left of each shape
        n = len(sh)
        seg = [sh[i] for i in range(n) if sh[i][0] <= sum(p[0] for p in sh) / n and sh[i][1] <= sum(p[1] for p in sh) / n]
        if len(seg) > 2 and i != 1:
            target.line([(px + s(5), py + s(5)) for px, py in seg], fill=rgba(C["white"], 0.45), width=max(1, int(s(3))))
    return lay, hl, head_hl


# ---------------------------------------------------------------- organs (only when lit)
def _organs(frame, cam, J, pose):
    hl = pose.get("hl", {})
    if not hl:
        return
    lay = frame.layer()
    d = ImageDraw.Draw(lay)
    P, N = J["P"], J["N"]
    t = pose.get("t", 0.0)
    s = cam.s
    st = hl.get("stomach", 0.0)
    if st:
        cx, cy = cam.p(P[0] + 38, P[1] - 168)
        d.ellipse([cx - s(58), cy - s(38), cx + s(48), cy + s(40)], fill=rgba(C["orange"], 0.35 + 0.35 * st))
        ImageDraw.Draw(frame.glow).ellipse([cx - s(40), cy - s(25), cx + s(30), cy + s(25)], fill=rgba(C["orange_l"], 0.3 * st))
    gut = hl.get("gut", 0.0)
    if gut:
        coil = [cam.p(P[0] + math.sin(k * 0.55) * (60 - k * 0.6), P[1] - 110 + k * 2.1) for k in range(60)]
        d.line(coil, fill=rgba(C["orange"], 0.3 + 0.4 * gut), width=max(2, int(s(16))), joint="curve")
    bl = hl.get("blood", 0.0)
    if bl:
        paths = []
        for side, sg in (("l", -1), ("r", 1)):
            paths.append([cam.p(N[0] + sg * 6, N[1] + 120), cam.p(P[0] + sg * 10, P[1] - 30), cam.p(*J[f"hip_{side}"]),
                          cam.p(J[f"knee_{side}"][0] + sg * 14, J[f"knee_{side}"][1]),
                          cam.p(J[f"ank_{side}"][0] + sg * 10, J[f"ank_{side}"][1] - 20)])
        for pth in paths:
            d.line(pth, fill=rgba(C["red"], 0.35 + 0.45 * bl), width=max(2, int(s(9))), joint="curve")
            ImageDraw.Draw(frame.glow).line(pth, fill=rgba(C["red_l"], 0.25 * bl), width=max(1, int(s(4))))
            n = int(3 + 9 * pose.get("glucose", 0.0))
            for i in range(n):
                k = (t * 0.3 + i / max(1, n)) % 1
                seg = k * (len(pth) - 1)
                j = min(int(seg), len(pth) - 2)
                fr = seg - j
                x = lerp(pth[j][0], pth[j + 1][0], fr)
                y = lerp(pth[j][1], pth[j + 1][1], fr)
                r = max(3, s(9))
                ImageDraw.Draw(frame.glow).ellipse([x - r, y - r, x + r, y + r], fill=rgba(C["orange_l"], 0.95))
    lg = hl.get("legs", None)
    if lg is not None:
        flex = pose.get("flex", 0.0)
        col = lerpc((110, 140, 190), C["orange"], lg)
        col = lerpc(col, C["red"], lg * flex * 0.5)
        for side in ("l", "r"):
            h, k_, a = J[f"hip_{side}"], J[f"knee_{side}"], J[f"ank_{side}"]
            bulge = 1 + 0.12 * flex * lg
            d.polygon(capsule_poly(cam.p(*h), cam.p(*k_), s(50) * bulge, s(34) * bulge), fill=rgba(col, 0.28 + 0.35 * lg))
            d.polygon(capsule_poly(cam.p(*k_), cam.p(*a), s(36) * bulge, s(20)), fill=rgba(col, 0.25 + 0.3 * lg))
            if lg > 0.2:
                ImageDraw.Draw(frame.glow).line([cam.p(*h), cam.p(*k_)], fill=rgba(C["orange_l"], 0.25 * lg * (0.5 + flex)),
                                                width=max(2, int(s(26))))
    frame.add_glass(lay)


# ---------------------------------------------------------------- skeleton
def _skeleton(frame, cam, J, pose):
    lay = frame.layer()
    d = ImageDraw.Draw(lay)
    s = cam.s
    N, P = J["N"], J["P"]
    # legs (behind pelvis visually first)
    for side in ("l", "r"):
        _bone(d, cam, J[f"hip_{side}"], J[f"knee_{side}"], 26, knob=0)
        knee, ank = J[f"knee_{side}"], J[f"ank_{side}"]
        _bone(d, cam, (knee[0] - 7, knee[1] + 10), (ank[0] - 7, ank[1]), 20)
        _bone(d, cam, (knee[0] + 13, knee[1] + 14), (ank[0] + 11, ank[1] - 4), 9)
        _knob(d, cam.p(*knee), s(22))
        ax, ay = cam.p(*ank)
        sg = -1 if side == "l" else 1
        foot = [(ax - s(26), ay), (ax + s(26), ay), (ax + s(30 + 6 * sg), ay + s(26)), (ax - s(30 - 6 * sg), ay + s(26))]
        _poly_bone(d, foot)
        for k in range(4):
            fx = ax - s(22) + k * s(14)
            d.line([(fx, ay + s(20)), (fx, ay + s(32))], fill=BONE_D + (255,), width=max(1, int(s(5))))
    # pelvis
    for sg in (-1, 1):
        wing = [cam.p(P[0] + sg * 18, P[1] - 50), cam.p(P[0] + sg * 92, P[1] - 82), cam.p(P[0] + sg * 116, P[1] - 30),
                cam.p(P[0] + sg * 82, P[1] + 20), cam.p(P[0] + sg * 64, P[1] + 44), cam.p(P[0] + sg * 22, P[1] + 30)]
        _poly_bone(d, wing)
        hx, hy = cam.p(P[0] + sg * 70, P[1] - 30)
        d.ellipse([hx - s(22), hy - s(26), hx + s(22), hy + s(26)], fill=BONE_D + (255,))
        _knob(d, cam.p(*J["hip_" + ("l" if sg < 0 else "r")]), s(20))
    sac = [cam.p(P[0] - 22, P[1] - 50), cam.p(P[0] + 22, P[1] - 50), cam.p(P[0] + 12, P[1] + 22), cam.p(P[0] - 12, P[1] + 22)]
    _poly_bone(d, sac)
    # spine (lumbar) between pelvis and ribcage
    for k in range(6):
        tt = k / 6
        vx, vy = cam.p(lerp(P[0], N[0], 0.18 + tt * 0.45), lerp(P[1] - 50, N[1], tt * 0.62))
        d.rounded_rectangle([vx - s(17), vy - s(12), vx + s(17), vy + s(12)], radius=int(s(6)), fill=BONE + (255,),
                            outline=BONE_D + (255,), width=max(1, int(s(3))))
    # ribcage
    sx, sy = N
    for i in range(7):
        y0 = sy + 34 + i * 23
        wid = 92 + min(i, 3) * 10 - max(0, i - 4) * 8
        for sg in (-1, 1):
            rib = [cam.p(sx + sg * 14, y0), cam.p(sx + sg * wid * 0.55, y0 - 8), cam.p(sx + sg * wid, y0 + 14),
                   cam.p(sx + sg * (wid + 4), y0 + 40 + i * 2)]
            d.line(rib, fill=BONE_D + (255,), width=max(2, int(s(12))), joint="curve")
            d.line(rib, fill=BONE + (255,), width=max(2, int(s(8))), joint="curve")
            d.line(rib[:3], fill=BONE_L + (255,), width=max(1, int(s(2.5))), joint="curve")
    _bone(d, cam, (sx, sy + 20), (sx, sy + 168), 20)
    # clavicles + shoulders
    for side, sg in (("l", -1), ("r", 1)):
        _bone(d, cam, (sx + sg * 12, sy + 14), J[f"sh_{side}"], 13)
        _knob(d, cam.p(*J[f"sh_{side}"]), s(22))
    # arms
    for side, sg in (("l", -1), ("r", 1)):
        _bone(d, cam, J[f"sh_{side}"], J[f"elb_{side}"], 18)
        e, w = J[f"elb_{side}"], J[f"wri_{side}"]
        _bone(d, cam, (e[0] - 5, e[1]), (w[0] - 6, w[1]), 11)
        _bone(d, cam, (e[0] + 6, e[1] + 4), (w[0] + 6, w[1]), 9)
        _knob(d, cam.p(*e), s(16))
        wx, wy = cam.p(*w)
        palm = [(wx - s(20), wy), (wx + s(20), wy), (wx + s(18), wy + s(30)), (wx - s(18), wy + s(30))]
        _poly_bone(d, palm)
        for k in range(4):   # fingers
            fx = wx - s(15) + k * s(10)
            d.line([(fx, wy + s(30)), (fx + sg * s(2), wy + s(56))], fill=BONE_D + (255,), width=max(2, int(s(8))))
            d.line([(fx, wy + s(30)), (fx + sg * s(2), wy + s(56))], fill=BONE + (255,), width=max(1, int(s(5))))
        if side == "r" and pose.get("hold_r") == "fork":
            d.line([(wx + s(4), wy + s(30)), (wx + s(4), wy - s(70))], fill=(200, 205, 215, 255), width=max(2, int(s(6))))
            for k in range(3):
                d.line([(wx - s(6) + k * s(8), wy - s(70)), (wx - s(6) + k * s(8), wy - s(96))], fill=(200, 205, 215, 255),
                       width=max(1, int(s(3))))
    frame.add_glass(lay)


# ---------------------------------------------------------------- skull + face
def _skull(frame, cam, J, pose):
    lay = frame.layer()
    d = ImageDraw.Draw(lay)
    s = cam.s
    hx, hy = J["head"]
    ang = J["head_ang"]

    def p(x, y):
        rx, ry = _rot((x, y), ang)
        return cam.p(hx + rx, hy + ry)

    jaw = pose.get("jaw", 0.0)
    expr = pose.get("expr", "neutral")
    jaw = max(jaw, {"surprised": 0.55, "happy": 0.18, "tired": 0.12, "satisfied": 0.08}.get(expr, 0.0))
    if expr == "panting":
        jaw = 0.35 + 0.25 * abs(math.sin(pose.get("t", 0.0) * 8))
    if expr == "chew":
        jaw = 0.25 + 0.35 * abs(math.sin(pose.get("t", 0.0) * 9))
    # neck vertebrae
    N = J["N"]
    for k in range(3):
        vx, vy = cam.p(lerp(N[0], hx, 0.2 + k * 0.22), lerp(N[1], hy + 96, 0.2 + k * 0.22))
        d.rounded_rectangle([vx - s(14), vy - s(10), vx + s(14), vy + s(10)], radius=int(s(5)), fill=BONE + (255,),
                            outline=BONE_D + (255,), width=max(1, int(s(3))))
    # cranium
    cran = [p(math.cos(a) * 92, math.sin(a) * 96 - 10) for a in [k / 40 * math.tau for k in range(40)]]
    d.polygon(cran, fill=BONE + (255,), outline=BONE_D + (255,))
    d.line(cran + [cran[0]], fill=BONE_D + (255,), width=max(2, int(s(4))))
    d.ellipse([*p(-58, -92), *p(-22, -62)], fill=BONE_L + (255,))   # specular dome
    # cheek / maxilla
    face = [p(-78, 10), p(78, 10), p(66, 70), p(40, 86), p(-40, 86), p(-66, 70)]
    d.polygon(face, fill=BONE + (255,))
    # nasal cavity
    d.polygon([p(0, 22), p(-12, 50), p(0, 56), p(12, 50)], fill=(60, 44, 36, 255))
    # upper teeth
    for k in range(8):
        tx = -42 + k * 12
        d.rounded_rectangle([*p(tx, 64), *p(tx + 10, 84)], radius=int(s(3)), fill=(250, 246, 236, 255),
                            outline=BONE_D + (255,), width=1)
    # mandible (opens with jaw)
    jo = jaw * 26
    mand = [p(-70, 70 + jo * 0.6), p(-56, 112 + jo), p(-24, 128 + jo), p(24, 128 + jo), p(56, 112 + jo), p(70, 70 + jo * 0.6)]
    d.polygon(mand, fill=BONE + (255,), outline=BONE_D + (255,))
    d.line(mand, fill=BONE_D + (255,), width=max(2, int(s(4))))
    for k in range(8):
        tx = -42 + k * 12
        d.rounded_rectangle([*p(tx, 88 + jo), *p(tx + 10, 104 + jo)], radius=int(s(3)), fill=(250, 246, 236, 255),
                            outline=BONE_D + (255,), width=1)
    if jaw > 0.1:
        d.polygon([p(-44, 86), p(44, 86), p(44, 88 + jo), p(-44, 88 + jo)], fill=(40, 20, 20, 255))
    # eyes: big round glass-ball eyes in the orbits. A skull has no lips, so emotion is carried by
    # eyelids (upper/lower), brow ridges, pupil size and the jaw.
    look = pose.get("look", (0.0, 0.0))
    LIDS = {"neutral": (0.12, 0.0), "happy": (0.04, 0.3), "tired": (0.5, 0.08), "discomfort": (0.3, 0.25),
            "curious": (0.1, 0.0), "surprised": (0.0, 0.0), "chew": (0.15, 0.1), "sarcastic": (0.46, 0.06),
            "satisfied": (0.38, 0.22), "panting": (0.22, 0.0), "worried": (0.05, 0.0)}
    BROW = {"neutral": (0, 0), "happy": (-6, 0), "surprised": (-22, 0), "tired": (8, -6), "discomfort": (10, 12),
            "curious": (-16, 0), "chew": (0, 0), "sarcastic": (6, 0), "satisfied": (-4, 0), "panting": (-8, 10),
            "worried": (-10, 12)}
    up_lid, lo_lid = LIDS.get(expr, (0.12, 0.0))
    for sg in (-1, 1):
        ex, ey = p(sg * 36, -2)
        r = s(31 + (5 if expr == "surprised" else 0))
        d.ellipse([ex - r - s(4), ey - r - s(4), ex + r + s(4), ey + r + s(4)], fill=(70, 52, 42, 255))   # orbit
        if pose.get("blink"):
            d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=BONE + (255,))
            d.line([(ex - r, ey), (ex + r, ey)], fill=BONE_D + (255,), width=max(2, int(s(4))))
        else:
            d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(248, 248, 250, 255))
            ir = s({"surprised": 11, "happy": 15, "tired": 14}.get(expr, 15))
            ix, iy = ex + look[0] * s(10), ey + look[1] * s(8) + (s(4) if expr == "tired" else 0)
            d.ellipse([ix - ir, iy - ir, ix + ir, iy + ir], fill=IRIS + (255,))
            d.ellipse([ix - ir * 0.5, iy - ir * 0.5, ix + ir * 0.5, iy + ir * 0.5], fill=(20, 14, 12, 255))
            d.ellipse([ix + ir * 0.15, iy - ir * 0.75, ix + ir * 0.6, iy - ir * 0.3], fill=(255, 255, 255, 255))
            box = [ex - r, ey - r, ex + r, ey + r]
            for frac, centre in ((up_lid, 270), (lo_lid, 90)):     # eyelids as bone-coloured segments
                if frac > 0.01:
                    th = math.degrees(math.acos(max(-1.0, 1 - 2 * frac)))
                    d.chord(box, centre - th, centre + th, fill=BONE + (255,))
                    yline = ey - r + 2 * r * frac if centre == 270 else ey + r - 2 * r * frac
                    half = math.sqrt(max(0.0, r * r - (yline - ey) ** 2))
                    d.line([(ex - half, yline), (ex + half, yline)], fill=BONE_D + (255,), width=max(2, int(s(4))))
        lift, inner = BROW.get(expr, (0, 0))
        if expr == "curious" and sg > 0:
            lift = 6                                                   # one brow up, the other down
        if expr == "sarcastic" and sg > 0:
            lift = -20                                                 # the signature Paco look to camera
        d.line([p(sg * 10, -40 + lift * 0.6 + inner), p(sg * 66, -42 + lift * 0.6)], fill=(110, 90, 72, 255),
               width=max(3, int(s(10))))
    # headband (channel signature)
    band = [p(-90, -76), p(-40, -90), p(40, -90), p(90, -76), p(92, -52), p(40, -64), p(-40, -64), p(-92, -52)]
    d.polygon(band, fill=HEADBAND + (255,))
    d.line([p(-90, -74), p(-40, -86), p(40, -86), p(90, -74)], fill=(240, 90, 90, 255), width=max(1, int(s(3))))
    frame.add_glass(lay)
    bx, by = p(0, -76)
    text(frame.glass, "PW", bx, by, size=max(10, int(s(26))), color=(250, 245, 235), stroke=max(1, int(s(2))),
         stroke_color=(120, 20, 26))


def draw(frame: Frame, cam: Cam, pose: dict):
    pose = {**DEFAULT, **pose}
    J = joints(pose)
    shell, highlights, head_hl = _glass_shell(frame, cam, J, pose)
    frame.add_glass(shell)
    _organs(frame, cam, J, pose)
    frame.add_glass(highlights)
    _skeleton(frame, cam, J, pose)
    _skull(frame, cam, J, pose)
    frame.add_glass(head_hl)
    return J
