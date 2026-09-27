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
TAGLINE = "A name born from two names, united by love."
STAGES = (
    ("N", "SNE", "ITISH", "HANKITHA"),
    ("S", "HAN", "ITIH", "KITHA"),
    ("H", "ITH", "ITI", "KA"),
)
