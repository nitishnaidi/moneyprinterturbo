"""Deterministic cinematic baby-name reveal renderer.

Critical typography is drawn with Pillow so names are never delegated to a generative
video model. The renderer intentionally stays independent from the normal MPT task
pipeline and can be reused by a future WebUI/API template.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
from moviepy import VideoClip
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION = 10.0

FATHER = "NITISH"
MOTHER = "SNEHANKITHA"
TODDLER = "ITIKA"
PAIRINGS = (("N", "SNE"), ("S", "HAN"), ("H", "ITH"))
FATHER_REMAINDER = "ITI"
MOTHER_REMAINDER = "KA"
TAGLINE = "A name born from two names, united by love."\nSTAGES = (\n    ("N", "SNE", "ITISH", "HANKITHA"),\n    ("S", "HAN", "ITIH", "KITHA"),\n    ("H", "ITH", "ITI", "KA"),\n)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def _ease(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _alpha(t: float, start: float, end: float, fade: float = 0.28) -> float:
    if t < start or t > end:
        return 0.0
    return min(_ease((t - start) / fade), _ease((end - t) / fade), 1.0)


def _center(draw: ImageDraw.ImageDraw, text: str, y: int, font, fill, stroke_width=0, stroke_fill=None):
    box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    x = (WIDTH - (box[2] - box[0])) / 2
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


def _background(t: float) -> Image.Image:
    yy, xx = np.mgrid[0:HEIGHT, 0:WIDTH]
    x = xx / WIDTH
    y = yy / HEIGHT
    glow = np.exp(-(((x - (0.48 + 0.03 * math.sin(t * 0.45))) / 0.42) ** 2 + ((y - 0.45) / 0.55) ** 2))
    edge = np.clip(1 - 0.55 * ((x - 0.5) ** 2 + (y - 0.5) ** 2), 0.55, 1)
    r = (72 + 90 * glow) * edge
    g = (32 + 48 * glow) * edge
    b = (48 + 45 * glow) * edge
    arr = np.dstack((r, g, b)).clip(0, 255).astype(np.uint8)
    image = Image.fromarray(arr, "RGB").convert("RGBA")
    particles = Image.new("RGBA", (WIDTH, HEIGHT))
    pd = ImageDraw.Draw(particles)
    for i in range(34):
        px = int((i * 277 + 35 * math.sin(t * 0.35 + i)) % WIDTH)
        py = int((i * 149 - t * (10 + i % 6)) % HEIGHT)
        radius = 2 + i % 4
        opacity = 35 + (i * 13) % 90
        pd.ellipse((px-radius, py-radius, px+radius, py+radius), fill=(255, 218, 150, opacity))
    particles = particles.filter(ImageFilter.GaussianBlur(2.2))
    return Image.alpha_composite(image, particles)


def _glow_text(layer, xy, text, font, alpha=255, anchor=None):
    glow = Image.new("RGBA", layer.size)
    gd = ImageDraw.Draw(glow)
    for width, opacity in ((18, 32), (10, 55), (5, 90)):
        gd.text(xy, text, font=font, fill=(255, 196, 105, opacity * alpha // 255),
                stroke_width=width, stroke_fill=(255, 154, 76, opacity * alpha // 255), anchor=anchor)
    glow = glow.filter(ImageFilter.GaussianBlur(8))
    layer.alpha_composite(glow)
    ImageDraw.Draw(layer).text(xy, text, font=font, fill=(255, 244, 220, alpha),
                               stroke_width=1, stroke_fill=(255, 202, 130, alpha), anchor=anchor)


def _name_layout(draw, text, y, font):
    widths = [draw.textlength(ch, font=font) for ch in text]
    gap = 8
    total = sum(widths) + gap * (len(text) - 1)
    x = (WIDTH - total) / 2
    positions = []
    for ch, width in zip(text, widths):
        positions.append((ch, x, y, width))
        x += width + gap
    return positions


def _draw_name_chars(layer, text, y, alpha, highlights=()):
    d = ImageDraw.Draw(layer)
    font = _font(102, True)
    positions = _name_layout(d, text, y, font)
    for idx, (ch, x, py, _) in enumerate(positions):
        if idx in highlights:
            _glow_text(layer, (x, py), ch, font, alpha)
        else:
            d.text((x, py), ch, font=font, fill=(255, 239, 219, alpha))
    return positions


def _draw_intro(layer, t):
    a = int(255 * min(_ease(t / .65), 1))
    if t > 2.0:
        a = int(a * max(0, 1 - (t - 2.0) / .35))
    if a <= 0:
        return
    d = ImageDraw.Draw(layer)
    _center(d, "FATHER", 205, _font(30, True), (255, 210, 155, int(a * .8)))
    _draw_name_chars(layer, FATHER, 255, a)
    _center(d, "MOTHER", 520, _font(30, True), (255, 210, 155, int(a * .8)))
    _draw_name_chars(layer, MOTHER, 570, a)
    _center(d, "Two names. One little miracle.", 785, _font(40), (255, 229, 210, int(a * .9)))


def _bezier(p0, p1, p2, u):
    v = 1 - u
    return (v*v*p0[0] + 2*v*u*p1[0] + u*u*p2[0],
            v*v*p0[1] + 2*v*u*p1[1] + u*u*p2[1])


def _trail(layer, p0, p2, progress, alpha):
    d = ImageDraw.Draw(layer)
    p1 = ((p0[0] + p2[0]) / 2, min(p0[1], p2[1]) - 170)
    points = [_bezier(p0, p1, p2, i / 36) for i in range(max(2, int(36 * progress)))]
    if len(points) > 1:
        for width, opacity in ((18, 25), (8, 70), (3, 180)):
            d.line(points, fill=(255, 189, 100, opacity * alpha // 255), width=width)
        x, y = points[-1]
        d.ellipse((x-8, y-8, x+8, y+8), fill=(255, 239, 188, alpha))


def _draw_extraction(layer, t):
    # Each stage keeps both complete source names visible. The selected father letter
    # and mother segment glow in-place first, then a curved light path connects them.
    starts = (2.05, 3.45, 4.85)
    active = next((i for i, s in enumerate(starts) if s <= t < s + 1.45), None)
    if active is None:
        return
    s = starts[active]
    local = t - s
    a = int(255 * min(_ease(local / .18), _ease((1.45-local)/.18), 1))
    d = ImageDraw.Draw(layer)
    father_letter, mother_segment, father_left, mother_left = STAGES[active]
    f_indices = [FATHER.index(father_letter, sum(1 for j in range(active) if STAGES[j][0] == father_letter))]
    segment_start = MOTHER.find(mother_segment)
    m_indices = list(range(segment_start, segment_start + len(mother_segment)))
    _center(d, "FATHER", 150, _font(27, True), (255, 205, 150, int(a*.75)))
    fp = _draw_name_chars(layer, FATHER, 195, a, f_indices)
    _center(d, "MOTHER", 485, _font(27, True), (255, 205, 150, int(a*.75)))
    mp = _draw_name_chars(layer, MOTHER, 530, a, m_indices)
    fx = fp[f_indices[0]][1] + fp[f_indices[0]][3]/2
    mx = (mp[m_indices[0]][1] + mp[m_indices[-1]][1] + mp[m_indices[-1]][3]) / 2
    progress = _ease((local-.18)/.55)
    _trail(layer, (fx, 310), (mx, 520), progress, a)
    if local > .68:
        ra = int(a * min((local-.68)/.22, 1))
        _center(d, f"remaining  {father_left}   +   {mother_left}", 775,
                _font(48, True), (255, 224, 178, ra))


def _draw_assembly(layer, t):
    if t < 6.25:
        return
    d = ImageDraw.Draw(layer)
    local = t - 6.25
    if local < .8:
        a = int(255 * min(local/.22, 1))
        _center(d, "The letters that remained...", 230, _font(38), (255, 224, 202, a))
        _glow_text(layer, (710, 455), FATHER_REMAINDER, _font(112, True), a, "mm")
        _glow_text(layer, (1210, 455), MOTHER_REMAINDER, _font(112, True), a, "mm")
        _center(d, "+", 410, _font(92), (255, 215, 150, a))
        return

    progress = _ease((local-.8)/.9)
    font = _font(168, True)
    widths = [d.textlength(ch, font=font) for ch in TODDLER]
    gap = 18
    total = sum(widths) + gap*(len(widths)-1)
    target = (WIDTH-total)/2
    sources = [(660,430),(735,430),(810,430),(1165,430),(1245,430)]
    x = target
    for i, (ch, width) in enumerate(zip(TODDLER, widths)):
        sx, sy = sources[i]
        tx = x
        px = sx + (tx-sx)*progress
        py = sy + (430-sy)*progress
        _glow_text(layer, (px, py), ch, font, 255)
        x += width + gap


def _draw_hero(layer, t):
    if t < 8.0:
        return
    local = t - 8.0
    a = int(255 * min(local/.4, 1))
    d = ImageDraw.Draw(layer)
    pulse = 1 + .025 * math.sin(local * 3.0)
    font = _font(int(205*pulse), True)
    _glow_text(layer, (WIDTH/2, 405), TODDLER, font, a, "mm")
    _center(d, TAGLINE, 675, _font(42), (255, 238, 218, int(a*.95)))
    # A restrained halo makes the final name feel like a hero reveal rather than a title card.
    halo = Image.new("RGBA", layer.size)
    hd = ImageDraw.Draw(halo)
    r = 220 + int(15*math.sin(local*2))
    hd.ellipse((WIDTH/2-r, 515-r, WIDTH/2+r, 515+r), fill=(255,190,115,32))
    layer.alpha_composite(halo.filter(ImageFilter.GaussianBlur(75)))

