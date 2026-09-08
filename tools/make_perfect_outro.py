from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1920, 1080
FONT_BLACK = "tools/fonts/SourceSerifPro-Black.ttf"
FONT_BOLD = "tools/fonts/SourceSerifPro-Bold.ttf"
FONT_REG = "tools/fonts/SourceSerifPro-Regular.ttf"

im = Image.new("RGB", (WIDTH, HEIGHT), (8, 6, 6))

overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
odraw = ImageDraw.Draw(overlay)

cx, cy = WIDTH // 2, HEIGHT // 2
for r in range(800, 0, -10):
    alpha = int(55 * (1.0 - r / 800))
    odraw.ellipse([cx - r, cy - int(r*0.62), cx + r, cy + int(r*0.62)], fill=(45, 30, 18, alpha))

im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
draw = ImageDraw.Draw(im)

pad = 70
draw.rectangle([pad, pad, WIDTH - pad, HEIGHT - pad], outline=(75, 58, 35), width=2)
draw.rectangle([pad + 10, pad + 10, WIDTH - pad - 10, HEIGHT - pad - 10], outline=(175, 135, 70), width=1)

def draw_diamond(x, y, s, col):
    draw.polygon([(x, y - s), (x + s, y), (x, y + s), (x - s, y)], fill=col)

draw_diamond(pad + 5, pad + 5, 8, (225, 185, 105))
draw_diamond(WIDTH - pad - 5, pad + 5, 8, (225, 185, 105))
draw_diamond(pad + 5, HEIGHT - pad - 5, 8, (225, 185, 105))
draw_diamond(WIDTH - pad - 5, HEIGHT - pad - 5, 8, (225, 185, 105))

font_top = ImageFont.truetype(FONT_BOLD, 26)
font_title = ImageFont.truetype(FONT_BLACK, 84)
font_sub = ImageFont.truetype(FONT_BOLD, 50)
font_motto = ImageFont.truetype(FONT_BLACK, 36)
font_bottom = ImageFont.truetype(FONT_REG, 26)
font_steam = ImageFont.truetype(FONT_BOLD, 26)

# Top badge
top_text = "HEARTS OF IRON IV  •  МОДИФИКАЦИЯ 1.6.1"
bbox = draw.textbbox((0, 0), top_text, font=font_top)
tw = bbox[2] - bbox[0]
draw.text(((WIDTH - tw)//2, 190), top_text, font=font_top, fill=(195, 155, 90))

# Ornate top line
lw = 320
draw.line([(WIDTH//2 - lw, 240), (WIDTH//2 + lw, 240)], fill=(180, 140, 75), width=2)
draw_diamond(WIDTH//2, 240, 6, (230, 190, 110))

# Title Line 1: ГУЛЯЙПОЛЕ
t1 = "ГУЛЯЙПОЛЕ"
bbox1 = draw.textbbox((0, 0), t1, font=font_title)
w1 = bbox1[2] - bbox1[0]
y1 = 275
draw.text(((WIDTH - w1)//2 + 4, y1 + 4), t1, font=font_title, fill=(0, 0, 0))
draw.text(((WIDTH - w1)//2, y1), t1, font=font_title, fill=(255, 240, 215))

# Title Line 2: ВОЛЬНАЯ ТЕРРИТОРИЯ
t2 = "ВОЛЬНАЯ ТЕРРИТОРИЯ"
bbox2 = draw.textbbox((0, 0), t2, font=font_sub)
w2 = bbox2[2] - bbox2[0]
y2 = 390
draw.text(((WIDTH - w2)//2 + 3, y2 + 3), t2, font=font_sub, fill=(0, 0, 0))
draw.text(((WIDTH - w2)//2, y2), t2, font=font_sub, fill=(235, 190, 110))

# Center line
lw2 = 450
draw.line([(WIDTH//2 - lw2, 490), (WIDTH//2 + lw2, 490)], fill=(180, 140, 75), width=2)
draw_diamond(WIDTH//2 - lw2, 490, 6, (230, 190, 110))
draw_diamond(WIDTH//2 + lw2, 490, 6, (230, 190, 110))
draw_diamond(WIDTH//2, 490, 9, (245, 205, 125))

# Motto: «АНАРХИЯ — МАТЬ ПОРЯДКА!»
motto = "«АНАРХИЯ — МАТЬ ПОРЯДКА!»"
bm = draw.textbbox((0, 0), motto, font=font_motto)
wm = bm[2] - bm[0]
draw.text(((WIDTH - wm)//2 + 2, 530 + 2), motto, font=font_motto, fill=(0, 0, 0))
draw.text(((WIDTH - wm)//2, 530), motto, font=font_motto, fill=(235, 60, 60))

# Manifesto
manifesto = "Земля — крестьянам! Фабрики — рабочим! Воля — народу!"
bman = draw.textbbox((0, 0), manifesto, font=font_bottom)
wman = bman[2] - bman[0]
draw.text(((WIDTH - wman)//2, 605), manifesto, font=font_bottom, fill=(210, 205, 195))

# Steam call to action
steam_text = "ВСТУПАЙТЕ В БОЙ В STEAM WORKSHOP"
bsteam = draw.textbbox((0, 0), steam_text, font=font_steam)
wsteam = bsteam[2] - bsteam[0]
hsteam = bsteam[3] - bsteam[1]
card_w = wsteam + 90
card_h = hsteam + 36
card_x1 = (WIDTH - card_w) // 2
card_y1 = 705
draw.rectangle([card_x1, card_y1, card_x1 + card_w, card_y1 + card_h], fill=(22, 17, 13), outline=(195, 155, 85), width=2)
draw.text(((WIDTH - wsteam)//2, card_y1 + 18), steam_text, font=font_steam, fill=(255, 220, 130))

out_path = "promo_video/slides_v2/final_outro.png"
im.save(out_path, quality=95)
print("Saved:", out_path)
