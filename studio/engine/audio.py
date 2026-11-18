"""Procedural chiptune music + sound effects (all original, synthesised with numpy)."""
from __future__ import annotations

import math
import wave
from pathlib import Path

import numpy as np

from . import SR

rng = np.random.default_rng(7)


# ---------------------------------------------------------------- primitives
def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def osc(kind, freq, dur, duty=0.5):
    t = t_axis(dur)
    f = np.broadcast_to(np.asarray(freq, dtype=float), t.shape) if np.ndim(freq) else np.full(t.shape, float(freq))
    ph = np.cumsum(f) / SR
    frac = ph % 1.0
    if kind == "square":
        return np.where(frac < duty, 1.0, -1.0) * 0.6
    if kind == "tri":
        return (4 * np.abs(frac - 0.5) - 1.0)
    if kind == "saw":
        return (2 * frac - 1.0) * 0.5
    if kind == "sine":
        return np.sin(2 * np.pi * ph)
    if kind == "noise":
        return rng.uniform(-1, 1, t.shape)
    raise ValueError(kind)


def env(n, a=0.005, d=0.08, s=0.6, r=0.08):
    """ADSR envelope for n samples (times in seconds)."""
    e = np.ones(n) * s
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    A = min(A, n)
    e[:A] = np.linspace(0, 1, A, endpoint=False) if A else e[:A]
    D2 = min(D, n - A)
    if D2 > 0:
        e[A:A + D2] = np.linspace(1, s, D2, endpoint=False)
    R2 = min(R, n)
    if R2 > 0:
        e[n - R2:] *= np.linspace(1, 0, R2)
    return e


def lowpass(x, k):
    """Cheap moving-average lowpass (k samples)."""
    k = max(1, int(k))
    if k == 1:
        return x
    c = np.cumsum(np.concatenate([[0.0], x]))
    y = (c[k:] - c[:-k]) / k
    return np.concatenate([y, np.zeros(len(x) - len(y))])


def crush(x, steps=16):
    return np.round(x * steps) / steps


def place(buf, clip, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf) or i + len(clip) <= 0:
        return
    j0 = max(0, -i)
    i = max(0, i)
    n = min(len(clip) - j0, len(buf) - i)
    buf[i:i + n] += clip[j0:j0 + n] * gain


# ---------------------------------------------------------------- sound effects
def sfx(name: str) -> np.ndarray:
    if name == "whoosh":
        d = 0.45
        n = osc("noise", 0, d)
        out = np.zeros_like(n)
        seg = len(n) // 12
        for i in range(12):
            k = int(40 - 30 * math.sin(math.pi * i / 11))
            out[i * seg:(i + 1) * seg] = lowpass(n, k)[i * seg:(i + 1) * seg]
        return out * np.sin(np.linspace(0, np.pi, len(n))) ** 2 * 0.9
    if name == "impact":
        d = 0.6
        t = t_axis(d)
        body = np.sin(2 * np.pi * np.cumsum(np.linspace(120, 38, len(t))) / SR) * np.exp(-t * 7)
        click = lowpass(osc("noise", 0, d), 3) * np.exp(-t * 40)
        return np.tanh((body * 1.2 + click * 0.8) * 1.6) * 0.9
    if name == "thud":
        d = 0.3
        t = t_axis(d)
        return np.sin(2 * np.pi * np.cumsum(np.linspace(90, 45, len(t))) / SR) * np.exp(-t * 14) * 0.9
    if name == "pop":
        d = 0.12
        f = np.linspace(500, 1300, int(d * SR))
        return osc("square", f, d, 0.25) * env(len(f), 0.002, 0.05, 0.3, 0.04) * 0.5
    if name == "blip":
        d = 0.07
        return osc("square", 1400, d, 0.5) * env(int(d * SR), 0.001, 0.03, 0.2, 0.03) * 0.25
    if name == "drip":
        d = 0.25
        f = np.linspace(900, 220, int(d * SR)) ** 1
        return osc("sine", f, d) * env(int(d * SR), 0.002, 0.1, 0.2, 0.1) * 0.7
    if name == "melt":
        d = 1.1
        t = t_axis(d)
        f = 300 * np.exp(-t * 1.6) + 60 + 20 * np.sin(t * 40)
        return crush(osc("square", f, d, 0.3) * np.exp(-t * 1.2) * 0.45, 10)
    if name == "scratch":
        d = 0.45
        t = t_axis(d)
        f = 400 + 900 * np.abs(np.sin(t * 22))
        n = lowpass(osc("noise", 0, d), 4) * 0.6 + osc("saw", f, d) * 0.4
        return n * np.exp(-t * 3) * 0.8
    if name == "explode":
        d = 1.4
        t = t_axis(d)
        n = osc("noise", 0, d)
        rumble = lowpass(n, 60) * 6
        crack = crush(n, 6) * np.exp(-t * 8)
        return np.tanh((rumble * np.exp(-t * 2.2) + crack) * 1.5) * 0.8
    if name == "stamp":
        a = sfx("impact")
        b = np.zeros(int(0.2 * SR))
        b[:400] = osc("noise", 0, 400 / SR) * np.linspace(1, 0, 400)
        out = a.copy()
        out[:len(b)] += b * 0.6
        return out
    if name == "sparkle":
        out = np.zeros(int(0.7 * SR))
        for i, n in enumerate([84, 88, 91, 96, 100]):
            d = 0.18
            c = osc("tri", midi(n), d) * env(int(d * SR), 0.002, 0.05, 0.3, 0.1) * 0.25
            place(out, c, i * 0.07)
        return out
    if name == "deflate":
        d = 0.9
        t = t_axis(d)
        f = 520 * np.exp(-t * 2.2) + 70
        return osc("square", f, d, 0.15) * np.exp(-t * 1.5) * 0.3 + lowpass(osc("noise", 0, d), 8) * 0.15 * np.exp(-t * 2)
    if name == "inflate":
        d = 0.9
        t = t_axis(d)
        f = 90 + 500 * (t / d) ** 2
        return osc("square", f, d, 0.35) * np.minimum(1, t * 6) * np.exp(-(d - t) * 0.5) * 0.25
    if name == "heartbeat":
        out = np.zeros(int(0.8 * SR))
        place(out, sfx("thud"), 0.0, 1.0)
        place(out, sfx("thud"), 0.22, 0.7)
        return out
    if name == "glitch":
        d = 0.35
        n = crush(osc("square", 80 + rng.uniform(0, 600, 1)[0], d, 0.2) * 0.5 + osc("noise", 0, d) * 0.3, 4)
        gate = (np.floor(t_axis(d) * 40) % 2).astype(float)
        return n * gate * 0.6
    if name == "ding":
        d = 0.9
        t = t_axis(d)
        return (osc("tri", midi(88), d) * 0.5 + osc("tri", midi(95), d) * 0.3) * np.exp(-t * 4) * 0.5
    if name == "machine":
        d = 1.2
        t = t_axis(d)
        f = 60 + 8 * np.sin(t * 50)
        return crush(osc("square", f, d, 0.4) * 0.3 + lowpass(osc("noise", 0, d), 3) * 0.1, 8) * np.minimum(1, t * 4)
    if name == "alarm":
        d = 0.8
        t = t_axis(d)
        f = np.where((t * 6) % 1 < 0.5, 880, 660)
        return osc("square", f, d, 0.5) * 0.18
    if name == "boing":
        d = 0.4
        t = t_axis(d)
        f = 200 + 120 * np.sin(t * 50) * np.exp(-t * 6)
        return osc("tri", f, d) * np.exp(-t * 5) * 0.7
    if name == "rise":
        d = 1.0
        t = t_axis(d)
        f = 200 * 2 ** (t * 2.5)
        return (osc("square", f, d, 0.25) * 0.15 + lowpass(osc("noise", 0, d), 6) * 0.2 * t) * (t / d)
    if name == "chomp":
        d = 0.12
        t = t_axis(d)
        return crush(lowpass(osc("noise", 0, d), 12) * 3, 6) * np.exp(-t * 30) * 0.6
    if name == "step":
        d = 0.08
        t = t_axis(d)
        return lowpass(osc("noise", 0, d), 20) * np.exp(-t * 60) * 1.4
    if name == "clank":
        d = 0.5
        t = t_axis(d)
        return (osc("square", 330, d, 0.3) * 0.3 + osc("square", 497, d, 0.3) * 0.2) * np.exp(-t * 9)
    if name == "tick":
        d = 0.05
        t = t_axis(d)
        return osc("square", 1800, d, 0.25) * np.exp(-t * 80) * 0.35
    if name == "scan":
        d = 0.7
        t = t_axis(d)
        f = 300 + 900 * (t / d)
        return (osc("square", f, d, 0.5) * 0.12 * (0.5 + 0.5 * np.sin(t * 60)) + lowpass(osc("noise", 0, d), 4) * 0.08) * np.sin(np.pi * t / d)
    if name == "babble":
        d = 0.45
        t = t_axis(d)
        f = 520 + 180 * np.sign(np.sin(t * 2 * np.pi * 11)) + 60 * np.sin(t * 37)
        gate = (np.sin(t * 2 * np.pi * 9) > -0.2).astype(float)
        return osc("square", f, d, 0.25) * gate * np.exp(-t * 2) * 0.22
    if name == "bar_up":
        d = 0.35
        t = t_axis(d)
        return osc("square", 400 * 2 ** (t * 4), d, 0.25) * np.exp(-t * 4) * 0.22
    if name == "bar_down":
        d = 0.4
        t = t_axis(d)
        return osc("square", 700 * 2 ** (-t * 4), d, 0.5) * np.exp(-t * 4) * 0.22
    if name == "snore":
        d = 1.2
        t = t_axis(d)
        return lowpass(osc("noise", 0, d), 60) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.9 * t)) ** 3 * 1.6
    if name == "breath":
        d = 0.7
        t = t_axis(d)
        return lowpass(osc("noise", 0, d), 20) * np.sin(np.pi * t / d) ** 2 * 0.9
    if name == "knock":
        d = 0.35
        t = t_axis(d)
        k = np.zeros_like(t)
        for off in (0.0, 0.17):
            i = int(off * SR)
            n = min(len(t) - i, int(0.06 * SR))
            k[i:i + n] += (np.sin(2 * np.pi * 180 * t[:n]) + lowpass(osc("noise", 0, n / SR), 6) * 0.6) * np.exp(-t[:n] * 60)
        return k * 0.8
    if name == "wiii":
        d = 0.6
        t = t_axis(d)
        return np.sin(2 * np.pi * np.cumsum(np.linspace(500, 1400, len(t))) / SR) * np.sin(np.pi * t / d) * 0.25
    if name == "clink":
        d = 0.5
        t = t_axis(d)
        return (np.sin(2 * np.pi * 2350 * t) * 0.5 + np.sin(2 * np.pi * 3170 * t) * 0.3) * np.exp(-t * 9) * 0.5
    if name == "slide":
        d = 0.5
        t = t_axis(d)
        return lowpass(osc("noise", 0, d), 30) * np.sin(np.pi * t / d) * 1.2
    if name == "bubble":
        d = 0.18
        t = t_axis(d)
        return np.sin(2 * np.pi * np.cumsum(np.linspace(300, 900, len(t))) / SR) * np.exp(-t * 18) * 0.35
    if name == "swell":
        d = 1.2
        t = t_axis(d)
        return (lowpass(osc("noise", 0, d), 40) * 0.8 + np.sin(2 * np.pi * 220 * t) * 0.15) * (t / d) ** 2
    if name == "soft_step":
        d = 0.16
        t = t_axis(d)
        return (np.sin(2 * np.pi * 70 * t) * 0.7 + lowpass(osc("noise", 0, d), 12) * 0.5) * np.exp(-t * 30) * 0.8
    if name == "rewind":
        d = 0.6
        t = t_axis(d)
        f = 1400 * 2 ** (-t * 5) * (1 + 0.15 * np.sign(np.sin(t * 2 * np.pi * 30)))
        return (osc("square", f, d, 0.5) * 0.18 + crush(osc("noise", 0, d), 6) * 0.08) * np.sin(np.pi * t / d)
    if name == "growl":
        d = 0.9
        t = t_axis(d)
        f = 70 + 25 * np.sin(t * 2 * np.pi * 7)
        g = lowpass(osc("noise", 0, d), 25) * 1.6 + osc("saw", f, d) * 0.5
        return crush(g, 10) * np.minimum(1, t * 8) * np.exp(-t * 1.6) * 0.7
    raise ValueError(name)


# ---------------------------------------------------------------- music
PROG = {
    "minor": [(57, [0, 3, 7]), (53, [0, 4, 7]), (50, [0, 3, 7]), (52, [0, 4, 7])],   # Am F Dm E
    "major": [(48, [0, 4, 7]), (55, [0, 4, 7]), (57, [0, 3, 7]), (53, [0, 4, 7])],   # C G Am F
}


def _drum(kind):
    if kind == "kick":
        d = 0.18
        t = t_axis(d)
        return np.sin(2 * np.pi * np.cumsum(np.linspace(150, 45, len(t))) / SR) * np.exp(-t * 18) * 0.9
    if kind == "snare":
        d = 0.16
        t = t_axis(d)
        return (crush(osc("noise", 0, d), 8) * 0.5 + osc("tri", 190, d) * 0.3) * np.exp(-t * 22)
    if kind == "hat":
        d = 0.04
        t = t_axis(d)
        n = osc("noise", 0, d)
        return (n - lowpass(n, 3)) * np.exp(-t * 90) * 0.35


def music(total: float, sections: list[tuple[float, float, str]], bpm=96) -> np.ndarray:
    """sections = [(start, end, mood)] mood in tense|mystery|groove|silence|hope|outro."""
    buf = np.zeros(int((total + 1) * SR))
    beat = 60.0 / bpm
    kick, snare, hat = _drum("kick"), _drum("snare"), _drum("hat")
    for (s, e, mood) in sections:
        if mood == "silence":
            continue
        if mood in ("pulse", "drive", "low", "triumph"):
            _music_v2(buf, s, e, mood, bpm, kick, snare, hat)
            continue
        if mood.startswith("c_"):
            _music_cine(buf, s, e, mood, bpm)
            continue
        scale = "major" if mood in ("hope", "outro") else "minor"
        prog = PROG[scale]
        nbeats = int((e - s) / beat) + 1
        for b in range(nbeats):
            tb = s + b * beat
            if tb >= e:
                break
            bar = b // 4
            root, chord = prog[bar % 4]
            # fade the last half-beat of the section
            g = min(1.0, (e - tb) / (beat * 0.75))
            if mood == "tense":
                for h in range(2):
                    n = osc("square", midi(root - 24), beat / 2 * 0.9, 0.5) * env(int(beat / 2 * 0.9 * SR), 0.003, 0.05, 0.5, 0.05)
                    place(buf, n * 0.16 * g, tb + h * beat / 2)
                if b % 2 == 0:
                    place(buf, kick * 0.55 * g, tb)
                place(buf, hat * 0.35 * g, tb + beat / 2)
                if b % 4 == 3:
                    n = osc("tri", midi(root + 12 + chord[2]), beat, ) * env(int(beat * SR), 0.01, 0.2, 0.3, 0.2)
                    place(buf, n * 0.12 * g, tb)
            elif mood == "mystery":
                if b % 4 == 0:
                    d = beat * 4
                    pad = sum(osc("tri", midi(root + 12 + c), d) for c in chord) / 3
                    place(buf, pad * env(len(pad), 0.4, 0.5, 0.6, 0.8) * 0.13 * g, tb)
                n = midi(root + 24 + chord[b % 3])
                c = osc("square", n, beat * 0.4, 0.125) * env(int(beat * 0.4 * SR), 0.002, 0.08, 0.2, 0.1)
                place(buf, c * 0.06 * g, tb + beat / 2)
            elif mood in ("groove", "hope", "outro"):
                lvl = 0.7 if mood == "outro" else 1.0
                # bass: root eighths with octave jumps
                for h in range(2):
                    nn = root - 24 + (12 if (h == 1 and b % 2 == 1) else 0)
                    d = beat / 2 * 0.85
                    nb = osc("square", midi(nn), d, 0.5) * env(int(d * SR), 0.003, 0.06, 0.6, 0.05)
                    place(buf, nb * 0.13 * g * lvl, tb + h * beat / 2)
                # arpeggio 16ths
                for q in range(4):
                    nn = root + 12 + chord[(b * 4 + q) % 3] + (12 if mood == "hope" and q == 3 else 0)
                    d = beat / 4 * 0.8
                    na = osc("square", midi(nn), d, 0.25) * env(int(d * SR), 0.002, 0.04, 0.3, 0.03)
                    place(buf, na * (0.055 if mood == "groove" else 0.065) * g * lvl, tb + q * beat / 4)
                # drums
                place(buf, kick * 0.6 * g * lvl, tb) if b % 2 == 0 else place(buf, snare * 0.45 * g * lvl, tb)
                place(buf, hat * 0.4 * g * lvl, tb + beat / 2)
                if mood == "hope" and b % 4 == 0:
                    d = beat * 4
                    lead = osc("tri", midi(root + 24 + chord[2]), d) * env(int(d * SR), 0.05, 0.3, 0.5, 0.6)
                    place(buf, lead * 0.07 * g, tb)
    return buf


def _music_v2(buf, s, e, mood, bpm, kick, snare, hat):
    """Phase moods for the body-change format.
    pulse: heartbeat kick + ticking hat + low drone (hook mystery)
    drive: bass eighths + snare backbeat + 16th arps, tempo-feel rises across the section (milestones)
    low: filtered minor pad, half-time, no hats (the 'valley')
    triumph: major, full drums, lead melody (reveal)"""
    beat = 60.0 / bpm
    nb = int((e - s) / beat) + 1
    scale = "major" if mood == "triumph" else "minor"
    prog_ = PROG[scale]
    for b in range(nb):
        tb = s + b * beat
        if tb >= e:
            break
        g = min(1.0, (e - tb) / (beat * 0.75))
        root, chord = prog_[(b // 4) % 4]
        if mood == "pulse":
            place(buf, kick * 0.7 * g, tb)
            place(buf, kick * 0.45 * g, tb + beat * 0.28)
            place(buf, hat * 0.3 * g, tb + beat / 2)
            if b % 4 == 0:
                d = min(beat * 4, e - tb)
                dr = osc("saw", midi(root - 24), d) * env(int(d * SR), 0.3, 0.3, 0.7, 0.4)
                place(buf, lowpass(dr, 30) * 0.22 * g, tb)
        elif mood == "low":
            if b % 4 == 0:
                d = min(beat * 4, e - tb)
                pad = sum(osc("saw", midi(root + c), d) for c in chord) / 3
                place(buf, lowpass(pad, 60) * env(len(pad), 0.2, 0.4, 0.6, 0.5) * 0.25 * g, tb)
            if b % 2 == 0:
                place(buf, kick * 0.5 * g, tb)
        elif mood == "drive":
            frac = (tb - s) / max(0.01, e - s)
            for h in range(2):
                d = beat / 2 * 0.85
                nb_ = osc("square", midi(root - 24 + (12 if h else 0)), d, 0.5) * env(int(d * SR), 0.003, 0.06, 0.6, 0.05)
                place(buf, nb_ * 0.13 * g, tb + h * beat / 2)
            subdiv = 4 if frac > 0.5 else 2
            for q in range(subdiv):
                d = beat / subdiv * 0.8
                na = osc("square", midi(root + 12 + chord[(b * subdiv + q) % 3]), d, 0.25) * env(int(d * SR), 0.002, 0.04, 0.3, 0.03)
                place(buf, na * 0.06 * g, tb + q * beat / subdiv)
            place(buf, kick * 0.6 * g, tb) if b % 2 == 0 else place(buf, snare * 0.45 * g, tb)
            place(buf, hat * 0.35 * g, tb + beat / 2)
        elif mood == "triumph":
            for h in range(2):
                d = beat / 2 * 0.85
                nb_ = osc("square", midi(root - 24 + (12 if h else 0)), d, 0.5) * env(int(d * SR), 0.003, 0.06, 0.6, 0.05)
                place(buf, nb_ * 0.14 * g, tb + h * beat / 2)
            mel = [12, 16, 19, 24, 19, 16, 19, 24]
            d = beat * 0.9
            ld = osc("square", midi(root + 12 + mel[b % 8] - (0 if 4 in chord else 1)), d, 0.5) * env(int(d * SR), 0.005, 0.1, 0.5, 0.1)
            place(buf, ld * 0.07 * g, tb)
            place(buf, kick * 0.65 * g, tb)
            if b % 2 == 1:
                place(buf, snare * 0.5 * g, tb)
            place(buf, hat * 0.4 * g, tb + beat / 2)


def _pad(freqs, d, a=0.6, r=0.8):
    t = t_axis(d)
    x = sum(np.sin(2 * np.pi * f * t + i) * (0.6 if i else 1.0) + 0.25 * np.sin(2 * np.pi * f * 2.003 * t)
            for i, f in enumerate(freqs)) / len(freqs)
    x *= 1 + 0.08 * np.sin(2 * np.pi * 4.5 * t)
    return x * env(len(t), a, 0.3, 0.85, r)


def _soft_kick(d=0.35):
    t = t_axis(d)
    return np.sin(2 * np.pi * np.cumsum(np.linspace(110, 42, len(t))) / SR) * np.exp(-t * 11)


def _music_cine(buf, s, e, mood, bpm):
    """Soft cinematic moods for the Leo Cristal format (sine pads, plucks, soft kicks; no chiptune).
    c_amb: low pad + drone · c_wonder: pad + plucked arpeggio · c_pulse: heartbeat kick + pad
    c_lift: pad + steady soft beat + arp · c_resolve: bright major pad + bells"""
    beat = 60.0 / bpm
    nb = int((e - s) / beat) + 1
    major = mood in ("c_resolve", "c_lift", "c_wonder")
    prog_ = PROG["major" if major else "minor"]
    kick = _soft_kick()
    for b in range(nb):
        tb = s + b * beat
        if tb >= e:
            break
        g = min(1.0, (e - tb) / (beat * 1.5))
        root, chord = prog_[(b // 8) % 4]
        if b % 8 == 0:
            d = min(beat * 8, e - tb) + 0.6
            freqs = [midi(root + 12 + c) for c in chord] + [midi(root)]
            lvl = {"c_amb": 0.16, "c_pulse": 0.13, "c_wonder": 0.12, "c_lift": 0.11, "c_resolve": 0.15}[mood]
            place(buf, _pad(freqs, d) * lvl * g, tb)
        if mood in ("c_wonder", "c_lift", "c_resolve"):
            for q in range(2):
                n = root + 24 + chord[(b * 2 + q) % 3] + (12 if mood == "c_resolve" and q else 0)
                d = beat * 0.9
                t = t_axis(d)
                pl = np.sin(2 * np.pi * midi(n) * t) * np.exp(-t * 7)
                place(buf, pl * (0.05 if mood != "c_resolve" else 0.06) * g, tb + q * beat / 2)
        if mood == "c_pulse":
            place(buf, kick * 0.35 * g, tb)
            place(buf, kick * 0.22 * g, tb + beat * 0.3)
        if mood == "c_lift":
            place(buf, kick * 0.3 * g, tb)
            n = osc("noise", 0, 0.03)
            place(buf, (n - lowpass(n, 3)) * np.exp(-t_axis(0.03) * 120) * 0.08 * g, tb + beat / 2)


# ---------------------------------------------------------------- mix
def duck(music_buf, voice_buf, depth=0.65, attack=0.03, release=0.25):
    n = min(len(music_buf), len(voice_buf))
    v = np.abs(voice_buf[:n])
    win = int(0.02 * SR)
    envv = lowpass(v, win)
    envv = envv / (envv.max() + 1e-9)
    # smooth with asymmetric follower (vectorised approximation: attack via max filter)
    hold = int(release * SR)
    c = np.maximum.accumulate  # noqa: F841  (kept simple below)
    sm = lowpass(np.clip(envv * 4, 0, 1), hold)
    sm = np.maximum(sm, lowpass(np.clip(envv * 4, 0, 1), int(attack * SR)))
    g = 1 - depth * np.clip(sm, 0, 1)
    out = music_buf.copy()
    out[:n] *= g
    return out


def write_wav(path: Path, x: np.ndarray):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
