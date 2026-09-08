import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

WIDTH, HEIGHT = 1920, 1080
FONT_BLACK = "tools/fonts/SourceSerifPro-Black.ttf"
FONT_BOLD = "tools/fonts/SourceSerifPro-Bold.ttf"
FONT_REG = "tools/fonts/SourceSerifPro-Regular.ttf"

# Create a deep cinematic black canvas with subtle vignette and dark gold ambient glow
im = Image.new("RGB", (WIDTH, HEIGHT), (6, 5, 5))
draw = ImageDraw.Draw(im)

# Radial gradient from center
overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
odraw = ImageDraw.Draw(overlay)

cx, cy = WIDTH // 2, HEIGHT // 2
for r in range(700, 0, -10):
    alpha = int(45 * (1.0 - r / 700))
    odraw.ellipse([cx - r, cy - int(r*0.6), cx + r, cy + int(r*0.6)], fill=(35, 25, 15, alpha))

im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
draw = ImageDraw.Draw(im)

# Gold ornate frame (double border with corner accents)
pad = 60
draw.rectangle([pad, pad, WIDTH - pad, HEIGHT - pad], outline=(90, 70, 40), width=2)
draw.rectangle([pad + 8, pad + 8, WIDTH - pad - 8, HEIGHT - pad - 8], outline=(180, 140, 75), width=1)

# Corner decorative diamonds
def draw_diamond(x, y, s, col):
    draw.polygon([(x, y - s), (x + s, y), (x, y + s), (x - s, y)], fill=col)

draw_diamond(pad + 4, pad + 4, 8, (220, 180, 100))
draw_diamond(WIDTH - pad - 4, pad + 4, 8, (220, 180, 100))
draw_diamond(pad + 4, HEIGHT - pad - 4, 8, (220, 180, 100))
draw_diamond(WIDTH - pad - 4, HEIGHT - pad - 4, 8, (220, 180, 100))

# Fonts
font_top = ImageFont.truetype(FONT_BOLD, 28)
font_title = ImageFont.truetype(FONT_BLACK, 78)
font_sub = ImageFont.truetype(FONT_BOLD, 52)
font_motto = ImageFont.truetype(FONT_BLACK, 34)
font_bottom = ImageFont.truetype(FONT_REG, 26)
font_steam = ImageFont.truetype(FONT_BOLD, 30)

# Top badge
top_text = "HEARTS OF IRON IV  •  МОДИФИКАЦИЯ 1.6.1"
bbox = draw.textbbox((0, 0), top_text, font=font_top)
tw = bbox[2] - bbox[0]
draw.text(((WIDTH - tw)//2, 210), top_text, font=font_top, fill=(185, 145, 80))

# Ornate top line
lw = 320
draw.line([(WIDTH//2 - lw, 260), (WIDTH//2 + lw, 260)], fill=(180, 140, 75), width=2)
draw_diamond(WIDTH//2, 260, 6, (230, 190, 110))

# Title Line 1: ГУЛЯЙПОЛЕ
t1 = "ГУЛЯЙПОЛЕ"
bbox1 = draw.textbbox((0, 0), t1, font=font_title)
w1 = bbox1[2] - bbox1[0]
y1 = 300
draw.text(((WIDTH - w1)//2 + 4, y1 + 4), t1, font=font_title, fill=(0, 0, 0))
draw.text(((WIDTH - w1)//2, y1), t1, font=font_title, fill=(255, 235, 205))

# Title Line 2: ВОЛЬНАЯ ТЕРРИТОРИЯ
t2 = "ВОЛЬНАЯ ТЕРРИТОРИЯ"
bbox2 = draw.textbbox((0, 0), t2, font=font_sub)
w2 = bbox2[2] - bbox2[0]
y2 = 410
draw.text(((WIDTH - w2)//2 + 3, y2 + 3), t2, font=font_sub, fill=(0, 0, 0))
draw.text(((WIDTH - w2)//2, y2), t2, font=font_sub, fill=(230, 185, 105))

# Center line
lw2 = 420
draw.line([(WIDTH//2 - lw2, 510), (WIDTH//2 + lw2, 510)], fill=(180, 140, 75), width=2)
draw_diamond(WIDTH//2 - lw2, 510, 5, (230, 190, 110))
draw_diamond(WIDTH//2 + lw2, 510, 5, (230, 190, 110))
draw_diamond(WIDTH//2, 510, 8, (240, 200, 120))

# Motto: «АНАРХИЯ — МАТЬ ПОРЯДКА!»
motto = "«АНАРХИЯ — МАТЬ ПОРЯДКА!»"
bm = draw.textbbox((0, 0), motto, font=font_motto)
wm = bm[2] - bm[0]
draw.text(((WIDTH - wm)//2 + 2, 550 + 2), motto, font=font_motto, fill=(0, 0, 0))
draw.text(((WIDTH - wm)//2, 550), motto, font=font_motto, fill=(245, 70, 70))

# Manifesto
manifesto = "Земля — крестьянам! Фабрики — рабочим! Воля — народу!"
bman = draw.textbbox((0, 0), manifesto, font=font_bottom)
wman = bman[2] - bman[0]
draw.text(((WIDTH - wman)//2, 625), manifesto, font=font_bottom, fill=(200, 195, 185))

# Steam Workshop call to action badge
steam_card = [WIDTH//2 - 280, 720, WIDTH//2 + 280, 795]
draw.rectangle(steam_card, fill=(20, 16, 12), outline=(195, 155, 85), width=2)
steam_text = "ВСТУПАЙТЕ В БОЙ В STEAM WORKSHOP"
bsteam = draw.textbbox((0, 0), steam_text, font=font_steam)
wsteam = bsteam[2] - bsteam[0]
draw.text(((WIDTH - wsteam)//2, 740), steam_text, font=font_steam, fill=(255, 220, 130))

out_path = "promo_video/slides_v2/test_outro.png"
im.save(out_path, quality=95)
print("Saved:", out_path)
