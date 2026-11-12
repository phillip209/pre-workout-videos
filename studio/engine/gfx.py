"""Pixel-art drawing helpers on top of PIL (no antialiasing anywhere)."""
from __future__ import annotations

import math
import random

import numpy as np
from PIL import Image, ImageDraw

from . import W, H

# --- Palette (original 32-colour palette for the channel) -------------------
P = {
    "ink": (18, 14, 28), "night": (30, 24, 48), "deep": (44, 34, 70),
    "violet": (78, 56, 120), "lav": (130, 110, 180), "fog": (190, 180, 220),
    "white": (246, 242, 232), "cream": (236, 222, 190),
    "skin": (232, 170, 128), "skin_d": (186, 118, 86), "skin_l": (248, 204, 160),
    "hair": (52, 34, 30), "tank": (40, 168, 160), "tank_d": (24, 112, 112),
    "shorts": (54, 58, 92), "shoe": (236, 236, 240),
    "red": (222, 58, 66), "red_d": (150, 30, 50), "red_l": (255, 120, 110),
    "muscle": (204, 64, 80), "muscle_d": (138, 34, 56), "muscle_l": (240, 120, 120),
    "fat": (250, 206, 92), "fat_d": (214, 150, 52), "fat_l": (255, 236, 160),
    "nucleus": (120, 70, 170), "nucleus_l": (190, 140, 255),
    "gold": (255, 200, 60), "gold_d": (200, 130, 30),
    "green": (90, 200, 110), "green_d": (40, 130, 80),
    "blue": (70, 140, 230), "blue_d": (40, 80, 160), "sky": (120, 190, 255),
    "steel": (150, 160, 180), "steel_d": (90, 96, 120), "steel_l": (210, 216, 230),
    "wood": (150, 96, 60), "wood_d": (100, 60, 40),
    "orange": (255, 140, 60), "pink": (255, 150, 190), "tissue": (92, 30, 56),
    "tissue_l": (130, 48, 80),
}

BAYER4 = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16.0


def new(w=W, h=H, color=(0, 0, 0, 0), mode="RGBA") -> Image.Image:
    return Image.new(mode, (w, h), color)


def lerp(a, b, t):
    return a + (b - a) * t


def lerpc(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1, c2))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


# --- easing ------------------------------------------------------------------
def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def ease_io(t):
    t = clamp(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_back(t, s=1.9):
    t = clamp(t)
    return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2


def ease_elastic(t):
    t = clamp(t)
    if t in (0, 1):
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1


def prog(t, start, dur):
    """0..1 progress of a window starting at `start` lasting `dur`."""
    if dur <= 0:
        return 1.0 if t >= start else 0.0
    return clamp((t - start) / dur)


def bounce(t):
    """Little hop curve 0->1->0."""
    t = clamp(t)
    return math.sin(t * math.pi)


# --- sprites -------------------------------------------------------------------
def outline(img: Image.Image, color=P["ink"], thick=1) -> Image.Image:
    """Add a 1px pixel-art outline around the opaque area of an RGBA sprite."""
    a = np.array(img)
    alpha = a[..., 3] > 0
    grown = alpha.copy()
    for _ in range(thick):
        g = grown.copy()
        g[1:, :] |= grown[:-1, :]
        g[:-1, :] |= grown[1:, :]
        g[:, 1:] |= grown[:, :-1]
        g[:, :-1] |= grown[:, 1:]
        grown = g
    ring = grown & ~alpha
    a[ring] = (*color, 255)
    return Image.fromarray(a, "RGBA")


def paste(dst: Image.Image, sprite: Image.Image, x, y, scale=1, anchor="mid_bottom"):
    """Paste RGBA sprite scaled by integer nearest-neighbour. Anchor = where (x,y) sits."""
    if scale != 1:
        sprite = sprite.resize((max(1, int(sprite.width * scale)), max(1, int(sprite.height * scale))), Image.NEAREST)
    w, h = sprite.size
    if anchor == "mid_bottom":
        px, py = int(round(x - w / 2)), int(round(y - h))
    elif anchor == "center":
        px, py = int(round(x - w / 2)), int(round(y - h / 2))
    else:
        px, py = int(round(x)), int(round(y))
    dst.alpha_composite(sprite, (px, py)) if dst.mode == "RGBA" else dst.paste(sprite, (px, py), sprite)
    return px, py, w, h


def dither_fill(img: Image.Image, box, c1, c2, t):
    """Fill box with an ordered-dither mix of two colours (t = share of c2)."""
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(img.width, x1), min(img.height, y1)
    if x1 <= x0 or y1 <= y0:
        return
    a = np.array(img)
    hh, ww = y1 - y0, x1 - x0
    yy, xx = np.mgrid[y0:y1, x0:x1]
    th = BAYER4[yy % 4, xx % 4]
    tt = np.broadcast_to(np.asarray(t, dtype=float), (hh, ww)) if np.ndim(t) else np.full((hh, ww), t)
    use2 = th < tt
    region = a[y0:y1, x0:x1]
    region[..., :3] = np.where(use2[..., None], np.array(c2), np.array(c1))
    if a.shape[2] == 4:
        region[..., 3] = 255
    img.paste(Image.fromarray(a, img.mode))


def vgradient(img: Image.Image, box, stops):
    """Banded (dithered) vertical gradient. stops = [(pos0..1, color), ...]."""
    x0, y0, x1, y1 = [int(v) for v in box]
    a = np.array(img)
    hgt = max(1, y1 - y0)
    for y in range(max(0, y0), min(img.height, y1)):
        p = (y - y0) / hgt
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= p <= p1:
                lt = (p - p0) / max(1e-6, p1 - p0)
                break
        else:
            c0 = c1 = stops[-1][1]
            lt = 0
        xs = np.arange(max(0, x0), min(img.width, x1))
        th = BAYER4[y % 4, xs % 4]
        cols = np.where((th < lt)[:, None], np.array(c1), np.array(c0))
        a[y, xs, :3] = cols
        if a.shape[2] == 4:
            a[y, xs, 3] = 255
    img.paste(Image.fromarray(a, img.mode))


def darken(img: Image.Image, amount: float, color=(10, 6, 20)):
    if amount <= 0:
        return img
    ov = Image.new("RGBA", img.size, (*color, int(255 * clamp(amount))))
    out = img.convert("RGBA")
    out.alpha_composite(ov)
    return out


def spotlight(img: Image.Image, cx, cy, r, dark=0.85):
    """Darken everything outside a (dithered-edge) circle."""
    a = np.array(img.convert("RGBA")).astype(np.int16)
    yy, xx = np.mgrid[0:img.height, 0:img.width]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    edge = np.clip((d - r) / 10.0, 0, 1)
    th = BAYER4[yy % 4, xx % 4]
    mask = (th < edge)
    a[mask, :3] = (a[mask, :3] * (1 - dark)).astype(np.int16)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


# --- camera & post ------------------------------------------------------------
def camera(img: Image.Image, zoom=1.0, cx=W / 2, cy=H / 2, shake=0.0, rot_seed=0, t=0.0):
    """Crop around (cx,cy) by zoom and scale back with nearest neighbour."""
    if shake > 0:
        rnd = random.Random(int(t * 60) + rot_seed)
        cx += rnd.uniform(-1, 1) * shake
        cy += rnd.uniform(-1, 1) * shake
    if abs(zoom - 1.0) < 1e-3 and shake <= 0 and abs(cx - W / 2) < 0.5 and abs(cy - H / 2) < 0.5:
        return img
    w, h = img.width / zoom, img.height / zoom
    x0 = clamp(cx - w / 2, 0, img.width - w) if zoom >= 1 else cx - w / 2
    y0 = clamp(cy - h / 2, 0, img.height - h) if zoom >= 1 else cy - h / 2
    if zoom < 1 or shake > 0:
        x0, y0 = cx - w / 2, cy - h / 2
    box = (int(round(x0)), int(round(y0)), int(round(x0 + w)), int(round(y0 + h)))
    return img.crop(box).resize((img.width, img.height), Image.NEAREST)


def chroma_glitch(img: Image.Image, amount: int, t: float):
    """Horizontal slice offsets + RGB split. amount = max pixel offset."""
    if amount <= 0:
        return img
    a = np.array(img.convert("RGB"))
    rnd = random.Random(int(t * 30))
    out = a.copy()
    for _ in range(6):
        y = rnd.randrange(0, a.shape[0] - 8)
        hh = rnd.randrange(2, 14)
        dx = rnd.randint(-amount, amount)
        out[y:y + hh] = np.roll(a[y:y + hh], dx, axis=1)
    out[..., 0] = np.roll(out[..., 0], max(1, amount // 3), axis=1)
    out[..., 2] = np.roll(out[..., 2], -max(1, amount // 3), axis=1)
    return Image.fromarray(out, "RGB").convert("RGBA")


def flash(img: Image.Image, amount: float, color=(255, 255, 255)):
    if amount <= 0:
        return img
    ov = Image.new("RGBA", img.size, (*color, int(255 * clamp(amount))))
    out = img.convert("RGBA")
    out.alpha_composite(ov)
    return out


def vignette(img: Image.Image, strength=0.35):
    a = np.array(img.convert("RGBA")).astype(np.int16)
    yy, xx = np.mgrid[0:img.height, 0:img.width]
    nx = (xx - img.width / 2) / (img.width / 2)
    ny = (yy - img.height / 2) / (img.height / 2)
    d = np.clip((np.sqrt(nx ** 2 + ny ** 2) - 0.75) / 0.6, 0, 1) * strength
    th = BAYER4[yy % 4, xx % 4]
    m = th < d
    a[m, :3] = (a[m, :3] * 0.55).astype(np.int16)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


_VIG = {}


def vignette_cached(img, strength=0.35):
    key = (img.size, strength)
    if key not in _VIG:
        yy, xx = np.mgrid[0:img.height, 0:img.width]
        nx = (xx - img.width / 2) / (img.width / 2)
        ny = (yy - img.height / 2) / (img.height / 2)
        d = np.clip((np.sqrt(nx ** 2 + ny ** 2) - 0.75) / 0.6, 0, 1) * strength
        _VIG[key] = BAYER4[yy % 4, xx % 4] < d
    a = np.array(img.convert("RGBA"))
    m = _VIG[key]
    a[m, :3] = (a[m, :3] * 0.55).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


# --- transitions -------------------------------------------------------------
def transition(a: Image.Image, b: Image.Image, kind: str, p: float, cx=W / 2, cy=H / 2):
    p = clamp(p)
    if kind == "cut" or p >= 1:
        return b if p >= 0.5 else a
    if kind == "dither":
        aa, bb = np.array(a.convert("RGBA")), np.array(b.convert("RGBA"))
        yy, xx = np.mgrid[0:a.height, 0:a.width]
        # chunky 2x2 dither cells for a visible pixel dissolve
        m = BAYER4[(yy // 2) % 4, (xx // 2) % 4] < p
        aa[m] = bb[m]
        return Image.fromarray(aa, "RGBA")
    if kind == "iris":
        # close on a, then open on b
        aa = np.array((a if p < 0.5 else b).convert("RGBA"))
        q = 1 - p * 2 if p < 0.5 else (p - 0.5) * 2
        r = ease_io(q) * math.hypot(W, H) * 0.6
        yy, xx = np.mgrid[0:a.height, 0:a.width]
        m = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) > r
        aa[m, :3] = P["ink"]
        return Image.fromarray(aa, "RGBA")
    if kind in ("whip_left", "whip_right"):
        e = ease_io(p)
        sgn = -1 if kind == "whip_left" else 1
        out = Image.new("RGBA", a.size, P["ink"] + (255,))
        off = int(e * a.width) * sgn
        out.alpha_composite(a.convert("RGBA"), (off, 0)) if abs(off) < a.width else None
        out.alpha_composite(b.convert("RGBA"), (off - sgn * a.width, 0))
        # speed lines
        d = ImageDraw.Draw(out)
        rnd = random.Random(int(p * 40))
        for _ in range(int(18 * math.sin(p * math.pi))):
            y = rnd.randrange(0, a.height)
            x = rnd.randrange(0, a.width)
            d.line([(x, y), (x + rnd.randint(20, 60), y)], fill=P["white"] + (160,))
        return out
    if kind == "pixelate":
        # mosaic up then down
        q = 1 - abs(p - 0.5) * 2
        src = a if p < 0.5 else b
        blk = max(1, int(1 + q * 18))
        sm = src.resize((max(1, src.width // blk), max(1, src.height // blk)), Image.NEAREST)
        return sm.resize(src.size, Image.NEAREST).convert("RGBA")
    return b
