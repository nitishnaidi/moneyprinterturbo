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
DURATION = 9.5

FATHER = "NITISH"
MOTHER = "SNEHANKITHA"
TODDLER = "ITIKA"
PAIRINGS = (("N", "SNE"), ("S", "HAN"), ("H", "ITH"))
FATHER_REMAINDER = "ITI"
MOTHER_REMAINDER = "KA"
TAGLINE = "A name born from two names, united by love."


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


def _draw_intro(layer: Image.Image, t: float) -> None:
    a = int(255 * _alpha(t, 0.0, 2.25))
    if not a:
        return
    d = ImageDraw.Draw(layer)
    gold = (255, 221, 158, a)
    soft = (255, 239, 218, a)
    _center(d, "FATHER", 260, _font(34, True), (gold[0], gold[1], gold[2], int(a*.8)))
    _center(d, FATHER, 310, _font(112, True), soft, 2, (170, 104, 65, a))
    _center(d, "MOTHER", 535, _font(34, True), (gold[0], gold[1], gold[2], int(a*.8)))
    _center(d, MOTHER, 585, _font(112, True), soft, 2, (170, 104, 65, a))


def _draw_pairing(layer: Image.Image, t: float, index: int, start: float) -> None:
    end = start + 1.55
    a = int(255 * _alpha(t, start, end, .22))
    if not a:
        return
    left, right = PAIRINGS[index]
    d = ImageDraw.Draw(layer)
    gold = (255, 215, 132, a)
    white = (255, 246, 229, a)
    d.text((385, 455), left, font=_font(138, True), fill=white)
    d.text((1290, 455), right, font=_font(138, True), fill=white)
    d.text((880, 474), "→", font=_font(105, True), fill=gold)
    progress = _ease((t - start) / .65)
    x1, y1, x2, y2 = 555, 535, 1260, 535
    xe = x1 + (x2 - x1) * progress
    d.line((x1, y1, xe, y2), fill=gold, width=5)
    d.ellipse((x1-9, y1-9, x1+9, y1+9), fill=gold)
    d.ellipse((xe-9, y2-9, xe+9, y2+9), fill=gold)
    _center(
        d,
        f"{left} from {FATHER}     {right} from {MOTHER}",
        690,
        _font(31),
        (255, 229, 195, int(a * 0.82)),
    )

    # Keep the accumulating leftovers visible so the derivation is understandable.
    father_left = ("ITISH", "ITIH", FATHER_REMAINDER)[index]
    mother_left = ("HANKITHA", "KITHA", MOTHER_REMAINDER)[index]
    _center(
        d,
        f"Remaining:  {father_left}  +  {mother_left}",
        765,
        _font(36, True),
        (255, 221, 168, int(a * 0.9)),
    )


def _draw_final(layer: Image.Image, t: float) -> None:
    start = 6.65
    if t < start:
        return
    d = ImageDraw.Draw(layer)
    progress = _ease((t - start) / 1.0)
    font = _font(164, True)
    widths = [d.textlength(c, font=font) for c in TODDLER]
    gap = 24
    total = sum(widths) + gap * (len(TODDLER)-1)
    target_x = (WIDTH-total)/2
    starts = [250, 600, 960, 1320, 1650]
    x = target_x
    for i, char in enumerate(TODDLER):
        tx = x
        sx = starts[i]
        px = sx + (tx-sx)*progress
        py = 450 + (i % 2 * 110 - 55)*(1-progress)
        opacity = int(255 * min((t-start)/.35, 1))
        d.text((px, py), char, font=font, fill=(255, 231, 177, opacity), stroke_width=2, stroke_fill=(173, 103, 57, opacity))
        x += widths[i] + gap
    if t >= 7.45:
        a = int(255 * min((t-7.45)/.5, 1))
        _center(d, TAGLINE, 720, _font(43), (255, 239, 221, a))


def make_frame(t: float) -> np.ndarray:
    base = _background(t)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT))
    _draw_intro(overlay, t)
    for idx, start in enumerate((2.05, 3.55, 5.05)):
        _draw_pairing(overlay, t, idx, start)
    _draw_final(overlay, t)
    composed = Image.alpha_composite(base, overlay).convert("RGB")
    return np.asarray(composed)


def render(output_path: str, fps: int = FPS) -> str:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    clip = VideoClip(make_frame, duration=DURATION)
    try:
        clip.write_videofile(str(output), fps=fps, codec="libx264", audio=False, preset="medium", pixel_format="yuv420p")
    finally:
        clip.close()
    return str(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the cinematic baby-name reveal template.")
    parser.add_argument("--output", default="baby-name-reveal.mp4")
    parser.add_argument("--fps", type=int, default=FPS)
    args = parser.parse_args()
    render(args.output, args.fps)


if __name__ == "__main__":
    main()
