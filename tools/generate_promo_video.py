import os
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT = "/home/astra/.gemini/antigravity/scratch/hoi4_gulyaypole_mod_release"
OUTPUT_DIR = os.path.join(ROOT, "promo_video")
os.makedirs(OUTPUT_DIR, exist_ok=True)
SLIDES_DIR = os.path.join(OUTPUT_DIR, "slides")
os.makedirs(SLIDES_DIR, exist_ok=True)

FONT_BOLD = os.path.join(ROOT, "tools/fonts/SourceSerifPro-Bold.ttf")
FONT_BLACK = os.path.join(ROOT, "tools/fonts/SourceSerifPro-Black.ttf")
FONT_REG = os.path.join(ROOT, "tools/fonts/SourceSerifPro-Regular.ttf")

WIDTH, HEIGHT = 1920, 1080

# Sequence definition (Slide definitions)
slides_data = [
    {
        "id": "slide_01",
        "bg": "mod_page/assets/banners/banner_main.jpg",
        "title": "ГУЛЯЙПОЛЕ: ВОЛЬНАЯ ТЕРРИТОРИЯ",
        "subtitle": "Hearts of Iron IV • Версия 1.19.2",
        "badge": "МАСШТАБНЫЙ ИСТОРИЧЕСКИЙ МОД v1.6.1",
        "duration": 5.0
    },
    {
        "id": "slide_02",
        "bg": "mod_page/assets/makhno.jpg",
        "title": "«АНАРХИЯ — МАТЬ ПОРЯДКА!»",
        "subtitle": "1936 год. Махновское движение отстояло южные степи",
        "badge": "БАТЬКО НЕСТОР МАХНО",
        "duration": 4.5
    },
    {
        "id": "slide_03",
        "bg": "mod_page/assets/news/black_guard_march.jpg",
        "title": "ЧЁРНАЯ ГВАРДИЯ СТЕПИ",
        "subtitle": "Земля — крестьянам, заводы — рабочим, воля — народу!",
        "badge": "ВОЛЬНЫЕ СОВЕТЫ И СИНДИКАТЫ",
        "duration": 4.5
    },
    {
        "id": "slide_04",
        "bg": "mod_page/assets/gallery/cavalry_charge.jpg",
        "title": "ТАКТИКА СТРЕМИТЕЛЬНОГО ПРОРЫВА",
        "subtitle": "Лихая конница, сабельные атаки и легендарные командиры",
        "badge": "ПОВСТАНЧЕСКАЯ АРМИЯ",
        "duration": 4.5
    },
    {
        "id": "slide_05",
        "bg": "mod_page/assets/gallery/tachanka.jpg",
        "title": "СМЕРТОНОСНЫЕ ТАЧАНКИ И БРОНЕВИКИ",
        "subtitle": "Уникальная ветка техники: от пулемётных повозок до тяжёлых броневиков",
        "badge": "СОБСТВЕННОЕ ВООРУЖЕНИЕ",
        "duration": 4.5
    },
    {
        "id": "slide_06",
        "bg": "mod_page/assets/gallery/armored_train.jpg",
        "title": "СТАЛЬНЫЕ ТАРАНЫ РЕВОЛЮЦИИ",
        "subtitle": "Бронепоезда «Свобода или Смерть», рейды по тылам и диверсии",
        "badge": "ЖЕЛЕЗНОДОРОЖНЫЕ КРЕПОСТИ",
        "duration": 4.5
    },
    {
        "id": "slide_07",
        "bg": "mod_page/assets/news/anarchist_congress.jpg",
        "title": "СВЫШЕ 190 НАЦИОНАЛЬНЫХ ФОКУСОВ",
        "subtitle": "Индустрия Донбасса, ДнепроГЭС, флот в Севастополе и Чёрный Интернационал",
        "badge": "ВАРИАТИВНОСТЬ И БАЛАНС",
        "duration": 5.0
    },
    {
        "id": "slide_08",
        "bg": "mod_page/assets/hero.jpg",
        "title": "ВЕДИТЕ ГУЛЯЙПОЛЕ К СВОБОДЕ!",
        "subtitle": "Вступайте в бой за вольную республику прямо сейчас",
        "badge": "УЖЕ ДОСТУПНО В STEAM WORKSHOP",
        "duration": 5.5
    }
]

def make_slide(slide):
    bg_path = os.path.join(ROOT, slide["bg"])
    im = Image.open(bg_path).convert("RGB")
    
    # Scale and crop to 1920x1080
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
    
    # Color grade: historical film tone with rich dark contrast
    im = ImageEnhance.Contrast(im).enhance(1.15)
    im = ImageEnhance.Color(im).enhance(0.85)
    
    # Vignette & darkening overlay for text readability
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    
    # Bottom/Center dark gradient for cinematic typography
    for y in range(HEIGHT):
        alpha = int(170 * (y / HEIGHT)**1.6)
        if y < 350:
            top_alpha = int(120 * ((350 - y) / 350)**1.8)
            alpha = max(alpha, top_alpha)
        odraw.line([(0, y), (WIDTH, y)], fill=(12, 10, 8, alpha))
        
    # Anarchist banner style dark card in lower middle
    card_top = HEIGHT - 380
    card_bot = HEIGHT - 90
    card_left = 120
    card_right = WIDTH - 120
    odraw.rectangle([card_left, card_top, card_right, card_bot], fill=(15, 13, 11, 205), outline=(195, 155, 90, 240), width=3)
    
    im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(im)
    
    # Fonts
    font_badge = ImageFont.truetype(FONT_BOLD, 26)
    font_title = ImageFont.truetype(FONT_BLACK, 54)
    font_sub = ImageFont.truetype(FONT_REG, 34)
    
    # Text rendering
    # Badge (Top of card)
    badge_text = slide["badge"]
    bbox_b = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox_b[2] - bbox_b[0]
    bx = (WIDTH - bw) // 2
    by = card_top + 35
    
    # Badge decorative lines
    draw.line([(bx - 120, by + 16), (bx - 20, by + 16)], fill=(195, 155, 90), width=2)
    draw.line([(bx + bw + 20, by + 16), (bx + bw + 120, by + 16)], fill=(195, 155, 90), width=2)
    draw.text((bx, by), badge_text, fill=(235, 195, 115), font=font_badge)
    
    # Title (Center of card)
    title_text = slide["title"]
    bbox_t = draw.textbbox((0, 0), title_text, font=font_title)
    tw = bbox_t[2] - bbox_t[0]
    tx = (WIDTH - tw) // 2
    ty = card_top + 85
    # subtle drop shadow
    draw.text((tx + 2, ty + 2), title_text, fill=(0, 0, 0), font=font_title)
    draw.text((tx, ty), title_text, fill=(255, 255, 255), font=font_title)
    
    # Subtitle (Bottom of card)
    sub_text = slide["subtitle"]
    bbox_s = draw.textbbox((0, 0), sub_text, font=font_sub)
    sw = bbox_s[2] - bbox_s[0]
    sx = (WIDTH - sw) // 2
    sy = card_top + 175
    draw.text((sx + 1, sy + 1), sub_text, fill=(0, 0, 0), font=font_sub)
    draw.text((sx, sy), sub_text, fill=(215, 210, 195), font=font_sub)
    
    # Save slide image
    out_img = os.path.join(SLIDES_DIR, f"{slide['id']}.png")
    im.save(out_img, quality=95)
    print(f"Generated {out_img}")
    return out_img

for s in slides_data:
    make_slide(s)

print("All slides successfully rendered!")
