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
    base=Image.fromarray(arr,"RGB").convert("RGBA")
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

def _intro(layer,t):
    if t>=2.05:return
    a=int(255*min(_ease(t/.55),_ease((2.05-t)/.25),1)); d=ImageDraw.Draw(layer)
    _center(d,"FATHER",190,_font(29,True),(255,207,155,a)); _name(layer,FATHER,240,a)
    _center(d,"MOTHER",500,_font(29,True),(255,207,155,a)); _name(layer,MOTHER,550,a)
    _center(d,"Two names. One little miracle.",790,_font(40),(255,230,211,a))

def _curve(layer,p0,p2,progress,alpha):
    d=ImageDraw.Draw(layer); p1=((p0[0]+p2[0])/2,min(p0[1],p2[1])-155); pts=[]
    for i in range(max(2,int(38*progress))):
        u=i/37; v=1-u; pts.append((v*v*p0[0]+2*v*u*p1[0]+u*u*p2[0],v*v*p0[1]+2*v*u*p1[1]+u*u*p2[1]))
    if len(pts)>1:
        d.line(pts,fill=(255,176,88,70),width=14); d.line(pts,fill=(255,229,170,alpha),width=3)

def _extract(layer,t):
    starts=(2.05,3.45,4.85); active=next((i for i,s in enumerate(starts) if s<=t<s+1.4),None)
    if active is None:return
    s=starts[active]; local=t-s; a=int(255*min(_ease(local/.18),_ease((1.4-local)/.16),1)); d=ImageDraw.Draw(layer)
    fl,ms,fr,mr=STAGES[active]; fi=[FATHER.index(fl)]; mi=list(range(MOTHER.find(ms),MOTHER.find(ms)+len(ms)))
    _center(d,"FATHER",130,_font(27,True),(255,205,150,a)); fp=_name(layer,FATHER,175,a,fi)
    _center(d,"MOTHER",455,_font(27,True),(255,205,150,a)); mp=_name(layer,MOTHER,500,a,mi)
    fx=fp[fi[0]][0]+fp[fi[0]][1]/2; mx=(mp[mi[0]][0]+mp[mi[-1]][0]+mp[mi[-1]][1])/2
    _curve(layer,(fx,295),(mx,495),_ease((local-.15)/.55),a)
    if local>.62:_center(d,f"remaining   {fr}   +   {mr}",770,_font(48,True),(255,224,178,int(a*min(1,(local-.62)/.2))))

def _assemble(layer,t):
    if t<6.25 or t>=8.0:return
    local=t-6.25; d=ImageDraw.Draw(layer)
    if local<.72:
        a=int(255*min(local/.2,1)); _center(d,"The letters that remained...",235,_font(38),(255,225,205,a))
        _glow(layer,(710,500),FATHER_REMAINDER,_font(112,True),a,"mm"); _glow(layer,(1210,500),MOTHER_REMAINDER,_font(112,True),a,"mm")
        _center(d,"+",445,_font(80,True),(255,216,155,a)); return
    p=_ease((local-.72)/.85); font=_font(168,True); widths=[d.textlength(ch,font=font) for ch in TODDLER]; gap=18
    x=(WIDTH-(sum(widths)+gap*4))/2; src=[(660,470),(735,470),(810,470),(1160,470),(1240,470)]
    for i,(ch,w) in enumerate(zip(TODDLER,widths)):
        sx,sy=src[i]; px=sx+(x-sx)*p; _glow(layer,(px,430),ch,font,255); x+=w+gap

def _hero(layer,t):
    if t<8:return
    local=t-8; a=int(255*min(local/.35,1)); d=ImageDraw.Draw(layer)
    halo=Image.new("RGBA",layer.size); hd=ImageDraw.Draw(halo); r=250+int(18*math.sin(local*2))
    hd.ellipse((WIDTH/2-r,500-r,WIDTH/2+r,500+r),fill=(255,188,105,38)); layer.alpha_composite(halo.filter(ImageFilter.GaussianBlur(80)))
    _glow(layer,(WIDTH/2,430),TODDLER,_font(205,True),a,"mm"); _center(d,TAGLINE,675,_font(42),(255,239,220,a))

def make_frame(t):
    base=_bg(t); layer=Image.new("RGBA",(WIDTH,HEIGHT)); _intro(layer,t); _extract(layer,t); _assemble(layer,t); _hero(layer,t)
    return np.asarray(Image.alpha_composite(base,layer).convert("RGB"))

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
