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
