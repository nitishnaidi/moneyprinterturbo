"""Cinematic deterministic baby-name reveal for NITISH + SNEHANKITHA -> ITIKA."""
from __future__ import annotations
import argparse
import math
from pathlib import Path
import numpy as np
from moviepy import VideoClip
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT, FPS, DURATION = 1920, 1080, 30, 10.0
FATHER, MOTHER, TODDLER = "NITISH", "SNEHANKITHA", "ITIKA"
PAIRINGS = (("N", "SNE"), ("S", "HAN"), ("H", "ITH"))
FATHER_REMAINDER, MOTHER_REMAINDER = "ITI", "KA"
TAGLINE = "A name born from two names, united by love."
STAGES = (
    ("N", "SNE", "ITISH", "HANKITHA"),
    ("S", "HAN", "ITIH", "KITHA"),
    ("H", "ITH", "ITI", "KA"),
)

def _font(size, bold=False):
    names = ["arialbd.ttf" if bold else "arial.ttf",
             "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"]
    for name in names:
        try: return ImageFont.truetype(name, size)
        except OSError: pass
    return ImageFont.load_default()

def _ease(x):
    x=max(0.0,min(1.0,x)); return x*x*(3-2*x)

def _center(d,text,y,font,fill):
    b=d.textbbox((0,0),text,font=font); d.text(((WIDTH-(b[2]-b[0]))/2,y),text,font=font,fill=fill)

def _bg(t):
    yy,xx=np.mgrid[0:HEIGHT,0:WIDTH]; x=xx/WIDTH; y=yy/HEIGHT
    glow=np.exp(-(((x-(.5+.04*math.sin(t*.4)))/.43)**2+((y-.48)/.58)**2))
    arr=np.dstack(((68+110*glow),(27+62*glow),(48+55*glow))).clip(0,255).astype(np.uint8)
    base=Image.fromarray(arr).convert("RGBA")
    p=Image.new("RGBA",(WIDTH,HEIGHT)); d=ImageDraw.Draw(p)
    for i in range(46):
        px=int((i*263+28*math.sin(t*.5+i))%WIDTH); py=int((i*137-t*(13+i%7))%HEIGHT); r=2+i%4
        d.ellipse((px-r,py-r,px+r,py+r),fill=(255,216,145,40+(i*17)%100))
    return Image.alpha_composite(base,p.filter(ImageFilter.GaussianBlur(2)))

def _glow(layer,xy,text,font,alpha=255,anchor=None):
    g=Image.new("RGBA",layer.size); gd=ImageDraw.Draw(g)
    gd.text(xy,text,font=font,fill=(255,205,125,alpha//2),stroke_width=10,stroke_fill=(255,150,75,alpha//3),anchor=anchor)
    layer.alpha_composite(g.filter(ImageFilter.GaussianBlur(9)))
    ImageDraw.Draw(layer).text(xy,text,font=font,fill=(255,244,220,alpha),stroke_width=1,stroke_fill=(255,190,110,alpha),anchor=anchor)

def _name(layer,text,y,alpha,hi=()):
    d=ImageDraw.Draw(layer); font=_font(102,True)
    widths=[d.textlength(ch,font=font) for ch in text]; x=(WIDTH-(sum(widths)+8*(len(text)-1)))/2; pos=[]
    for i,(ch,w) in enumerate(zip(text,widths)):
        pos.append((x,w))
        if i in hi: _glow(layer,(x,y),ch,font,alpha)
        else: d.text((x,y),ch,font=font,fill=(255,239,219,alpha))
        x+=w+8
    return pos

def _draw_continuous_story(layer, t):
    """Single continuous shot: names persist and selected glyphs dissolve in place."""
    d = ImageDraw.Draw(layer)
    # Gentle fade-in only. No scene-level fade-outs or card refreshes.
    alpha = int(255 * min(_ease(t / .55), 1.0))
    # Fade all source-scene chrome away as convergence begins.
    chrome_alpha = alpha
    if t >= 6.9:
        chrome_alpha = int(alpha * (1 - _ease((t - 6.9) / .45)))
    _center(d, "FATHER", 145, _font(27, True), (255, 205, 150, int(chrome_alpha * .82)))
    _center(d, "MOTHER", 485, _font(27, True), (255, 205, 150, int(chrome_alpha * .82)))

    # Removal windows. A mapped glyph glows, then dissolves while every other glyph
    # stays anchored to its original location. This makes the derivation readable.
    events = (
        (2.0, "father", (0,)),       # N
        (2.0, "mother", (0, 1, 2)), # SNE
        (3.45, "father", (4,)),      # S
        (3.45, "mother", (3, 4, 5)), # HAN
        (4.9, "father", (5,)),       # H
        (4.9, "mother", (7, 8, 9)),  # ITH
    )

    def glyph_alpha(group, idx):
        a = alpha
        glow = False
        for start, event_group, indices in events:
            if group != event_group or idx not in indices:
                continue
            if t < start:
                return a, False
            if start <= t < start + .42:
                return a, True
            if start + .42 <= t < start + .88:
                p = _ease((t - start - .42) / .46)
                return int(a * (1 - p)), True
            return 0, False
        return a, glow

    def persistent_name(text, y, group):
        font = _font(102, True)
        widths = [d.textlength(ch, font=font) for ch in text]
        gap = 8
        x = (WIDTH - (sum(widths) + gap * (len(text)-1))) / 2
        father_survivors = {1, 2, 3}
        mother_survivors = {6, 10}
        survivor_set = father_survivors if group == "father" else mother_survivors
        # Once convergence starts, the source copies disappear so each survivor
        # exists only once as it travels toward the final name.
        source_alpha = alpha if t < 7.15 else 0
        for i, (ch, width) in enumerate(zip(text, widths)):
            ga, glowing = glyph_alpha(group, i)
            ga = min(ga, source_alpha)
            if ga > 0:
                if glowing:
                    _glow(layer, (x, y), ch, font, ga)
                elif i in survivor_set and t >= 5.78:
                    # Cool ivory/rose accent distinguishes the five survivors.
                    d.text((x, y), ch, font=font, fill=(245, 205, 220, ga),
                           stroke_width=2, stroke_fill=(185, 105, 135, ga))
                else:
                    d.text((x, y), ch, font=font, fill=(255, 239, 219, ga))
            x += width + gap

    persistent_name(FATHER, 195, "father")
    persistent_name(MOTHER, 535, "mother")

    # Mapping arrow is an overlay only. Source letters remain anchored.
    active = None
    starts = (2.0, 3.45, 4.9)
    for i, start in enumerate(starts):
        if start <= t < start + .9:
            active = i
            break
    if active is not None:
        left, right = PAIRINGS[active]
        local = t - starts[active]
        cue_alpha = int(235 * min(_ease(local/.14), _ease((.9-local)/.14), 1))
        # Strong central arrow with compact labels, readable without looking like a slide.
        _center(d, f"{left}     →     {right}", 750, _font(52, True),
                (255, 220, 150, cue_alpha))

    # Once all mapped characters are gone, the original positions visibly contain
    # only ITI and KA. Hold that state before convergence.
    if 5.78 <= t < 7.15:
        hold = int(255 * min(_ease((t-5.78)/.25), 1))
        if t >= 6.9:
            hold = int(hold * (1 - _ease((t-6.9)/.25)))
        _center(d, "The letters that remain", 790, _font(35), (255, 224, 196, hold))


def _draw_final_convergence(layer, t):
    if t < 7.15:
        return
    d = ImageDraw.Draw(layer)
    local = t - 7.15
    move = _ease(min(local / 1.0, 1.0))
    font = _font(170, True)
    widths = [d.textlength(ch, font=font) for ch in TODDLER]
    gap = 18
    target_x = (WIDTH - (sum(widths) + gap * 4)) / 2

    # Approximate centers of the five visible survivors: I T I from father, K A from mother.
    sources = [(785, 250), (865, 250), (945, 250), (820, 590), (1110, 590)]
    x = target_x
    for i, (ch, width) in enumerate(zip(TODDLER, widths)):
        sx, sy = sources[i]
        tx, ty = x, 405
        px = sx + (tx - sx) * move
        py = sy + (ty - sy) * move
        # Blend survivor accent into final warm gold while the letters travel.
        rose = (245, 205, 220)
        gold = (255, 232, 170)
        color = tuple(int(rose[j] + (gold[j]-rose[j])*move) for j in range(3))
        glow = Image.new("RGBA", layer.size)
        gd = ImageDraw.Draw(glow)
        gd.text((px, py), ch, font=font, fill=(*color, 180),
                stroke_width=9, stroke_fill=(255, 174, 82, int(120*move)))
        layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(8)))
        d.text((px, py), ch, font=font, fill=(*color, 255),
               stroke_width=1, stroke_fill=(255, 194, 110, 255))
        x += width + gap

    # The moving letters themselves ARE the hero name. No second ITIKA layer.
    if local >= 1.0:
        hero_a = int(255 * min((local-1.0)/.35, 1))
        # Subtle halo behind the completed word, not over it.
        halo = Image.new("RGBA", layer.size)
        hd = ImageDraw.Draw(halo)
        hd.ellipse((650, 280, 1270, 690), fill=(255, 185, 95, int(28*hero_a/255)))
        layer.alpha_composite(halo.filter(ImageFilter.GaussianBlur(75)))
        _center(d, TAGLINE, 665, _font(42), (255, 239, 220, hero_a))

def make_frame(t):
    base = _bg(t)
    layer = Image.new("RGBA", (WIDTH, HEIGHT))
    _draw_continuous_story(layer, t)
    _draw_final_convergence(layer, t)
    return np.asarray(Image.alpha_composite(base, layer).convert("RGB"))

def render(output_path,fps=FPS):
    out=Path(output_path).resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    print(f"Rendering {DURATION:.1f}s video to: {out}")
    clip=VideoClip(make_frame,duration=DURATION)
    try: clip.write_videofile(str(out),fps=fps,codec="libx264",audio=False,preset="medium",pixel_format="yuv420p")
    finally: clip.close()
    if not out.exists(): raise RuntimeError(f"MoviePy finished but output was not created: {out}")
    print(f"Created: {out} ({out.stat().st_size/1024/1024:.1f} MB)")
    return str(out)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",default="baby-name-reveal-v2.mp4"); p.add_argument("--fps",type=int,default=FPS)
    args=p.parse_args(); render(args.output,args.fps)

if __name__=="__main__":
    main()
