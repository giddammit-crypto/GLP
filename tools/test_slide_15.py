import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT = "/home/astra/.gemini/antigravity/scratch/hoi4_gulyaypole_mod_release"
WIDTH, HEIGHT = 1920, 1080
FONT_BLACK = "tools/fonts/SourceSerifPro-Black.ttf"
FONT_BOLD = "tools/fonts/SourceSerifPro-Bold.ttf"
FONT_REG = "tools/fonts/SourceSerifPro-Regular.ttf"

im = Image.open(os.path.join(ROOT, "mod_page/assets/historical_makhno_berdyansk_1919.jpg")).convert("RGB")

im_ratio = im.width / im.height
target_ratio = WIDTH / HEIGHT
if im_ratio > target_ratio:
    new_height = HEIGHT
    new_width = int(new_height * im_ratio)
else:
    new_width = WIDTH
    new_height = int(new_width / im_ratio)
    
im = im.resize((new_width, new_height), Image.Resampling.LANCZOS)
left = (im.width - WIDTH) // 2
top = (im.height - HEIGHT) // 2
im = im.crop((left, top, left + WIDTH, top + HEIGHT))

im = ImageEnhance.Contrast(im).enhance(1.20)
im = ImageEnhance.Color(im).enhance(0.70)

overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
odraw = ImageDraw.Draw(overlay)

for y in range(HEIGHT):
    alpha = int(185 * (y / HEIGHT)**1.6)
    if y < 350:
        top_alpha = int(120 * ((350 - y) / 350)**1.8)
        alpha = max(alpha, top_alpha)
    odraw.line([(0, y), (WIDTH, y)], fill=(12, 10, 8, alpha))

card_top = HEIGHT - 380
card_bot = HEIGHT - 90
card_left = 120
card_right = WIDTH - 120
odraw.rectangle([card_left, card_top, card_right, card_bot], fill=(15, 13, 11, 215), outline=(195, 155, 90, 240), width=3)

im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
draw = ImageDraw.Draw(im)

font_badge = ImageFont.truetype(FONT_BOLD, 25)
font_title = ImageFont.truetype(FONT_BLACK, 46)
font_sub = ImageFont.truetype(FONT_REG, 30)

badge_text = "ИСТОРИЧЕСКАЯ ХРОНИКА • БЕРДЯНСК, 1919"
bbox_b = draw.textbbox((0, 0), badge_text, font=font_badge)
bw = bbox_b[2] - bbox_b[0]
bx = (WIDTH - bw) // 2
by = card_top + 32
draw.line([(bx - 120, by + 16), (bx - 20, by + 16)], fill=(195, 155, 90), width=2)
draw.line([(bx + bw + 20, by + 16), (bx + bw + 120, by + 16)], fill=(195, 155, 90), width=2)
draw.text((bx, by), badge_text, fill=(235, 195, 115), font=font_badge)

title_text = "НЕСТОР МАХНО И ШТАБ ПОВСТАНЦЕВ"
bbox_t = draw.textbbox((0, 0), title_text, font=font_title)
tw = bbox_t[2] - bbox_t[0]
tx = (WIDTH - tw) // 2
ty = card_top + 85
draw.text((tx + 2, ty + 2), title_text, fill=(0, 0, 0), font=font_title)
draw.text((tx, ty), title_text, fill=(255, 255, 255), font=font_title)

sub_text = "Культовый саундтрек «Монгол Шуудан», живая история и дух вольной борьбы"
bbox_s = draw.textbbox((0, 0), sub_text, font=font_sub)
sw = bbox_s[2] - bbox_s[0]
sx = (WIDTH - sw) // 2
sy = card_top + 175
draw.text((sx + 1, sy + 1), sub_text, fill=(0, 0, 0), font=font_sub)
draw.text((sx, sy), sub_text, fill=(215, 210, 195), font=font_sub)

im.save("promo_video/slides_v2/test_slide_15.png", quality=95)
print("Slide 15 created successfully")
