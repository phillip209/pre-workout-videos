"""Crystal engine core: native 1080x1920 vector rendering with glass layers and bloom.

Why 2.5D vector and not 3D: this machine has no Blender and no discrete GPU (checked 2026-11-18), and
Windows App Control blocks most native installers. Everything is drawn procedurally with Pillow + numpy:
a jointed character rig, layered anatomy, a 2D camera (dolly / track / macro) and image-space
transitions. No static image is ever "animated" by panning.

Frame model: every frame draws into a `Frame` with three RGBA layers
  base  — opaque environments
  glass — translucent fills (body shell, organs, particles)
  glow  — bright strokes that get bloomed (blurred + screen-added)
"""
from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30

C = {
    "navy": (8, 14, 32), "navy2": (14, 24, 52), "navy3": (24, 40, 80),
    "cyan": (70, 225, 255), "cyan_d": (30, 140, 190), "cyan_l": (190, 250, 255),
    "orange": (255, 150, 50), "orange_l": (255, 205, 120), "orange_d": (200, 90, 20),
    "violet": (160, 110, 255), "violet_l": (210, 180, 255),
    "red": (240, 70, 80), "red_d": (160, 30, 50), "red_l": (255, 140, 140),
    "white": (245, 250, 255), "bone": (220, 240, 255), "gold": (255, 210, 90),
    "green": (110, 230, 160), "ink": (4, 8, 18), "wood": (70, 44, 34), "wood_l": (110, 72, 52),
}


def lerp(a, b, t):
    return a + (b - a) * t


def lerpc(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1, c2))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, start, dur):
    return clamp((t - start) / dur) if dur > 0 else float(t >= start)


def ease_io(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def rgba(c, a):
    return (c[0], c[1], c[2], int(clamp(a) * 255))


class Cam:
    """World -> screen. (x, y) is the world point shown at screen centre (cx, cy); z = zoom."""

    def __init__(self, x=0.0, y=0.0, z=1.0, cx=W / 2, cy=H / 2):
        self.x, self.y, self.z, self.cx, self.cy = x, y, z, cx, cy

    def p(self, x, y):
        return ((x - self.x) * self.z + self.cx, (y - self.y) * self.z + self.cy)

    def s(self, v):
        return v * self.z

    @staticmethod
    def blend(a: "Cam", b: "Cam", t: float) -> "Cam":
        t = ease_io(t)
        return Cam(lerp(a.x, b.x, t), lerp(a.y, b.y, t), math.exp(lerp(math.log(a.z), math.log(b.z), t)))


class Frame:
    def __init__(self, bg=C["navy"]):
        self.base = Image.new("RGBA", (W, H), bg + (255,))
        self.glass = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.top = Image.new("RGBA", (W, H), (0, 0, 0, 0))   # UI / labels, not bloomed

    def layer(self):
        """A fresh transparent layer; composite it with `add_glass`."""
        return Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def add_glass(self, lay):
        self.glass.alpha_composite(lay)

    def add_base(self, lay):
        self.base.alpha_composite(lay)

    def compose(self, bloom=1.0, bloom_radius=14) -> Image.Image:
        img = self.base.copy()
        img.alpha_composite(self.glass)
        img.alpha_composite(self.glow)
        rgb = img.convert("RGB")
        if bloom > 0:
            small = self.glow.resize((W // 4, H // 4), Image.BILINEAR)
            blur = small.filter(ImageFilter.GaussianBlur(bloom_radius / 4)).resize((W, H), Image.BILINEAR)
            arr = np.asarray(blur, dtype=np.float32)
            rgbb = arr[..., :3] * (arr[..., 3:4] / 255.0) * bloom
            out = np.asarray(rgb, dtype=np.float32)
            out = 255 - (255 - out) * (255 - np.clip(rgbb, 0, 255)) / 255   # screen blend
            rgb = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
        rgb = rgb.convert("RGBA")
        rgb.alpha_composite(self.top)
        return rgb.convert("RGB")


# ---------------------------------------------------------------- primitives
def capsule_poly(a, b, ra, rb, n=10):
    """Polygon of a tapered capsule from point a (radius ra) to b (radius rb)."""
    ax, ay = a
    bx, by = b
    ang = math.atan2(by - ay, bx - ax)
    pts = []
    for i in range(n + 1):
        t = math.pi / 2 + math.pi * i / n
        pts.append((bx + math.cos(ang + t - math.pi) * rb, by + math.sin(ang + t - math.pi) * rb))
    for i in range(n + 1):
        t = math.pi / 2 + math.pi * i / n
        pts.append((ax + math.cos(ang + t) * ra, ay + math.sin(ang + t) * ra))
    return pts


def glass_shape(frame: Frame, pts, fill=C["cyan"], fill_a=0.16, edge=C["cyan"], edge_a=0.9, width=4,
                glow_a=0.55, inner=True):
    """Translucent fill + bright rim (+ bloom) + inner rim highlight."""
    lay = frame.layer()
    d = ImageDraw.Draw(lay)
    d.polygon(pts, fill=rgba(fill, fill_a))
    frame.add_glass(lay)
    gd = ImageDraw.Draw(frame.glow)
    gd.line(pts + [pts[0]], fill=rgba(edge, edge_a), width=width, joint="curve")
    if inner and glow_a > 0:
        gd.line(pts + [pts[0]], fill=rgba(C["cyan_l"], glow_a * 0.5), width=max(1, width // 2))


def glow_line(frame: Frame, pts, color, a=0.9, width=4):
    ImageDraw.Draw(frame.glow).line(pts, fill=rgba(color, a), width=width, joint="curve")


def glow_dot(frame: Frame, x, y, r, color, a=0.9):
    ImageDraw.Draw(frame.glow).ellipse([x - r, y - r, x + r, y + r], fill=rgba(color, a))


def soft_light(frame: Frame, x, y, r, color, a=0.35):
    """Radial light pool on the base layer (environment lighting)."""
    lay = frame.layer()
    d = ImageDraw.Draw(lay)
    steps = 10
    for i in range(steps, 0, -1):
        rr = r * i / steps
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=rgba(color, a * (1 - i / steps) ** 1.4 / 1.2 + 0.0))
    frame.add_base(lay)


def vgradient(img, box, stops):
    x0, y0, x1, y1 = [int(v) for v in box]
    d = ImageDraw.Draw(img)
    hgt = max(1, y1 - y0)
    for y in range(y0, y1):
        t = (y - y0) / hgt
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                k = (t - p0) / max(1e-6, p1 - p0)
                d.line([x0, y, x1, y], fill=lerpc(c0, c1, k) + (255,))
                break


@lru_cache(maxsize=None)
def gradient_bg(key: tuple) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    vgradient(img, (0, 0, W, H), list(key))
    return img


# ---------------------------------------------------------------- text
FONT_DIR = Path("C:/Windows/Fonts")


@lru_cache(maxsize=None)
def font(size: int, weight: str = "bold"):
    name = {"bold": "segoeuib.ttf", "semibold": "seguisb.ttf", "regular": "segoeui.ttf",
            "black": "segoeuib.ttf", "light": "segoeuil.ttf"}[weight]
    return ImageFont.truetype(str(FONT_DIR / name), size)


def text(img, s, x, y, size=48, color=C["white"], weight="bold", anchor="mm", stroke=4, stroke_color=C["ink"],
         alpha=1.0):
    d = ImageDraw.Draw(img)
    d.text((x, y), s, font=font(size, weight), fill=rgba(color, alpha), anchor=anchor, stroke_width=stroke,
           stroke_fill=rgba(stroke_color, alpha))


def text_width(s, size, weight="bold"):
    return font(size, weight).getlength(s)


def vignette(img: Image.Image, strength=0.45) -> Image.Image:
    return ImageChops.multiply(img, _vig(strength))


@lru_cache(maxsize=4)
def _vig(strength):
    yy, xx = np.mgrid[0:H, 0:W]
    dx, dy = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
    r = np.sqrt(dx * dx * 0.9 + dy * dy * 0.7)
    v = 1 - strength * np.clip(r - 0.45, 0, 1) ** 1.6
    a = (np.clip(v, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(np.stack([a, a, a], -1))


def film_grade(img: Image.Image, t: float) -> Image.Image:
    """Subtle cinematic grade: vignette + very light animated grain."""
    img = vignette(img, 0.5)
    rng = np.random.default_rng(int(t * 30) % 997)
    noise = rng.normal(0, 3.0, (H // 4, W // 4)).astype(np.float32)
    n = Image.fromarray(np.clip(noise + 128, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    arr = np.asarray(img, dtype=np.int16) + (np.asarray(n, dtype=np.int16)[..., None] - 128)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
