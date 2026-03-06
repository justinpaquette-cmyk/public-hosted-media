#!/usr/bin/env python3
"""
BrandedResumeScribe v10 — Single-row matching Scribe Panel reference

Matches BrandedScribePanel-v3-dual.png layout exactly:
  - Text left ~30%
  - MASSIVE detail crop center, bleeding off bottom
  - Smaller context phone right, bleeding off bottom+right
  - Canvas 2400x920 → 1200x460 (same as reference)

Hero = confirmation dialog (the payoff moment)
Context phone = swipe action (the setup)
Email body copy handles the two-step narrative.
"""

from PIL import Image, ImageDraw, ImageFont

BASE   = "/Users/justinpaquette/Documents/sales eng projects v2/client-agnostic-projects/public-hosted-media/gifs/commure-pro-release-mar-2026"
FONTS  = "/Users/justinpaquette/Documents/Commure Logos From Paul/latest/Brand Assets, Templates and Guidelines/Local Fonts"
CLASH_S    = f"{FONTS}/Clash Display/ClashDisplay-Semibold.otf"
CLASH_M    = f"{FONTS}/Clash Display/ClashDisplay-Medium.otf"
SATOSHI_R  = f"{FONTS}/Satoshi/Satoshi-Regular.otf"
LOGO       = "/Users/justinpaquette/Documents/Commure Logos From Paul/latest/Brand Assets, Templates and Guidelines/Logo/Full Horizontal Logo/PNG/Commure-logo_full-horizontal_cream.png"
SWIPE_SRC  = f"{BASE}/ResumeScribeSwipe.png"
CONF_SRC   = f"{BASE}/ResumeScribeConfirm.png"
OUT        = f"{BASE}/BrandedResumeScribe-v10.png"

# 2x canvas — same proportions as Scribe Panel reference
W, H    = 2400, 920
BG      = (22, 22, 22)
CREAM   = (253, 255, 242)
BLUE    = (51, 90, 241)
DIM     = (148, 148, 148)

canvas = Image.new("RGB", (W, H), BG)
draw   = ImageDraw.Draw(canvas)

f_hl   = ImageFont.truetype(CLASH_S, 72)
f_sub  = ImageFont.truetype(SATOSHI_R, 32)

# ── Logo ─────────────────────────────────────────────────────────────────────
logo = Image.open(LOGO).convert("RGBA")
lh = 48; lw = int(logo.width * lh / logo.height)
logo = logo.resize((lw, lh), Image.LANCZOS)
canvas.paste(logo, (72, 52), logo)

# ── Headline + subtitle ──────────────────────────────────────────────────────
draw.text((72, 130), "Pick up exactly\nwhere you left off.", font=f_hl, fill=CREAM)
draw.text((72, 340), "Resume any draft note with a single\nswipe from the Patient List.", font=f_sub, fill=DIM)

# ── Helpers ──────────────────────────────────────────────────────────────────
def rr_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0,0,size[0]-1,size[1]-1], radius=r, fill=255)
    return m

def load_crop_to_width(src, box, target_w):
    img = Image.open(src).convert("RGBA")
    c = img.crop(box)
    r = target_w / c.width
    return c.resize((target_w, int(c.height * r)), Image.LANCZOS)

def load_full_to_height(src, target_h):
    img = Image.open(src).convert("RGBA")
    r = target_h / img.height
    return img.resize((int(img.width * r), target_h), Image.LANCZOS)

def paste_rr(base_rgba, img, pos, r=50):
    m = rr_mask(img.size, r)
    tmp = img.copy(); tmp.putalpha(m)
    layer = Image.new("RGBA", base_rgba.size, (0,0,0,0))
    layer.paste(tmp, pos, tmp)
    return Image.alpha_composite(base_rgba, layer)

def paste_rr_opacity(base_rgba, img, pos, r=50, opacity=200):
    m = rr_mask(img.size, r)
    tmp = img.copy()
    alpha = m.point(lambda p: int(p * opacity / 255))
    tmp.putalpha(alpha)
    layer = Image.new("RGBA", base_rgba.size, (0,0,0,0))
    layer.paste(tmp, pos, tmp)
    return Image.alpha_composite(base_rgba, layer)

# ── Image layout — matching Scribe Panel reference ───────────────────────────
# Text occupies left ~720px (30%), images fill ~1680px (70%)

# Hero: confirmation dialog detail crop — MASSIVE, centered, bleeds off bottom
# Source: ResumeScribeConfirm.png (1419x2796)
# Crop from just below status bar through well past the modal buttons
# Shows: patient info at top → icons → modal dialog prominent in center → bleeds off
C_HERO = (0, 300, 1419, 1620)  # below status bar through modal buttons
hero = load_crop_to_width(CONF_SRC, C_HERO, 1100)

# Blue highlight on Resume button in the confirmation dialog
# In source: Resume button is at approximately x:850-1100, y:1350-1470
sx = 1100 / (C_HERO[2] - C_HERO[0])
sy = hero.height / (C_HERO[3] - C_HERO[1])
resume_btn = (850, 1350, 1100, 1470)
bx1 = int((resume_btn[0] - C_HERO[0]) * sx)
by1 = int((resume_btn[1] - C_HERO[1]) * sy)
bx2 = int((resume_btn[2] - C_HERO[0]) * sx)
by2 = int((resume_btn[3] - C_HERO[1]) * sy)

highlight = Image.new("RGBA", hero.size, (0, 0, 0, 0))
hd = ImageDraw.Draw(highlight)
hd.rounded_rectangle([bx1-6, by1-6, bx2+6, by2+6], radius=14,
                      fill=(51, 90, 241, 35), outline=(51, 90, 241, 180), width=5)
hero = Image.alpha_composite(hero, highlight)

# Context phone: swipe action — smaller, bleeds off bottom+right
PHONE_H = 840
phone = load_full_to_height(SWIPE_SRC, PHONE_H)

# Position hero: starts near top of canvas, bleeds well past bottom
hero_x = 700
hero_y = 40  # start near top — hero bleeds off bottom naturally

# Position phone: overlaps hero slightly, bleeds off bottom and right edge
phone_x = hero_x + 1100 - 60  # overlap hero by 60px
phone_y = H + 100 - PHONE_H   # bleeds off bottom

print(f"Hero: pos=({hero_x},{hero_y}) size={hero.size}")
print(f"Phone: pos=({phone_x},{phone_y}) size={phone.size}")
print(f"Phone right edge: {phone_x + phone.width} (canvas W={W})")

# ── Composite ────────────────────────────────────────────────────────────────
comp = canvas.convert("RGBA")

# Phone behind (context), hero in front (focal point)
comp = paste_rr_opacity(comp, phone, (phone_x, phone_y), 48, opacity=190)
comp = paste_rr(comp, hero, (hero_x, hero_y), 44)

canvas = comp.convert("RGB")

# ── Save at 1200x460 (matching Scribe Panel reference) ──────────────────────
out = canvas.resize((1200, 460), Image.LANCZOS)
out.save(OUT, "PNG", optimize=True)
print(f"\nSaved: {OUT} {out.size}")
