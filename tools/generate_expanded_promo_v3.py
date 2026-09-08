import os
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT = "/home/astra/.gemini/antigravity/scratch/hoi4_gulyaypole_mod_release"
OUTPUT_DIR = os.path.join(ROOT, "promo_video")
SLIDES_DIR = os.path.join(OUTPUT_DIR, "slides_v3")
os.makedirs(SLIDES_DIR, exist_ok=True)
CLIPS_DIR = os.path.join(OUTPUT_DIR, "clips_v3")
os.makedirs(CLIPS_DIR, exist_ok=True)

FONT_BOLD = os.path.join(ROOT, "tools/fonts/SourceSerifPro-Bold.ttf")
FONT_BLACK = os.path.join(ROOT, "tools/fonts/SourceSerifPro-Black.ttf")
FONT_REG = os.path.join(ROOT, "tools/fonts/SourceSerifPro-Regular.ttf")

AUDIO_TRACK = os.path.join(ROOT, "music/mongol_shuudan_lyubo.ogg")
FINAL_VIDEO = os.path.join(OUTPUT_DIR, "gulyaypole_mod_official_trailer.mp4")

WIDTH, HEIGHT = 1920, 1080

slides_data = [
    {
        "id": "slide_01",
        "bg": "mod_page/assets/banners/banner_main.jpg",
        "title": "ГУЛЯЙПОЛЕ: ВОЛЬНАЯ ТЕРРИТОРИЯ",
        "subtitle": "Hearts of Iron IV • Версия 1.19.2",
        "badge": "АЛЬТЕРНАТИВНАЯ ИСТОРИЯ • ВЕРСИЯ 1.6.1",
        "duration": 5.0
    },
    {
        "id": "slide_02",
        "bg": "mod_page/assets/makhno.jpg",
        "title": "«АНАРХИЯ — МАТЬ ПОРЯДКА!»",
        "subtitle": "Альтернативный 1936 год: Махновское движение отстояло юг",
        "badge": "БАТЬКО НЕСТОР МАХНО",
        "duration": 4.5
    },
    {
        "id": "slide_03",
        "bg": "mod_page/assets/news/black_guard_march.jpg",
        "title": "СУРОВОЕ ЭХО 1921 ГОДА",
        "subtitle": "Потери в огне Гражданской войны: армию предстоит растить заново",
        "badge": "ВЫБИТОЕ ПОКОЛЕНИЕ ВЕТЕРАНОВ",
        "duration": 4.5
    },
    {
        "id": "slide_04",
        "bg": "mod_page/assets/gallery/camp_council.jpg",
        "title": "ЗЕМЛЯ — КРЕСТЬЯНАМ, ВОЛЯ — НАРОДУ!",
        "subtitle": "Беспартийные Советы, крестьянские коммуны и вольные сходы",
        "badge": "ОБЩЕСТВО БЕЗ ВЕРТИКАЛИ ВЛАСТИ",
        "duration": 4.5
    },
    {
        "id": "slide_05",
        "bg": "mod_page/assets/gallery/cavalry_charge.jpg",
        "title": "ПОВСТАНЧЕСКАЯ КАВАЛЕРИЯ",
        "subtitle": "Молниеносные прорывы, сабельные атаки и рейды по тылам противника",
        "badge": "РЕВОЛЮЦИОННАЯ ПОВСТАНЧЕСКАЯ АРМИЯ",
        "duration": 4.5
    },
    {
        "id": "slide_06",
        "bg": "mod_page/assets/gallery/tachanka.jpg",
        "title": "ЛЕГЕНДАРНЫЕ ТАЧАНКИ И БРОНЕВИКИ",
        "subtitle": "Уникальная ветка техники со своими спрайтами: от пулемётных повозок до тяжёлых броневиков",
        "badge": "СОБСТВЕННЫЙ АРСЕНАЛ И ТЕХНОЛОГИИ",
        "duration": 5.0
    },
    {
        "id": "slide_07",
        "bg": "mod_page/assets/gallery/armored_train.jpg",
        "title": "СТАЛЬНЫЕ ТАРАНЫ РЕСПУБЛИКИ",
        "subtitle": "Бронепоезда «Свобода или Смерть», «Батько Махно» и «Гроза Степей»",
        "badge": "УНИКАЛЬНЫЕ БРОНЕПОЕЗДА С ФЛАГОМ ГУЛЯЙПОЛЯ",
        "duration": 5.0
    },
    {
        "id": "slide_08",
        "bg": "mod_page/assets/news/dnieper_electric.jpg",
        "title": "УГОЛЬНЫЙ КРИЗИС ДОНБАССА",
        "subtitle": "Шахтёры Юзовки и Луганска бастуют: налаживайте снабжение и диалог с фабзавкомами",
        "badge": "НОВАЯ МЕХАНИКА ИНТЕГРАЦИИ ПРОМЫШЛЕННОСТИ",
        "duration": 5.0
    },
    {
        "id": "slide_09",
        "bg": "mod_page/assets/news/anarchist_congress.jpg",
        "title": "ИНДУСТРИАЛИЗАЦИЯ И ДНЕПРОГЭС",
        "subtitle": "Развитие угольных синдикатов, заводов Екатеринослава и гидроэлектростанций",
        "badge": "ЭКОНОМИКА ВОЛЬНЫХ СИНДИКАТОВ",
        "duration": 4.5
    },
    {
        "id": "slide_10",
        "bg": "mod_page/assets/news/sevastopol_fleet.jpg",
        "title": "ВОЛЬНЫЙ ЧЕРНОМОРСКИЙ ФЛОТ",
        "subtitle": "Севастопольский бастион, торпедные катера и балтийские матросы Кронштадта",
        "badge": "МОРСКАЯ ОБОРОНА И ПРОЛИВЫ",
        "duration": 4.5
    },
    {
        "id": "slide_11",
        "bg": "mod_page/assets/news/madrid_international.jpg",
        "title": "ПОМОЩЬ РЕВОЛЮЦИИ В ИСПАНИИ",
        "subtitle": "Братство с CNT-FAI: спасение Каталонии, оружие и добровольческие колонны РПА",
        "badge": "МЕЖДУНАРОДНАЯ СОЛИДАРНОСТЬ",
        "duration": 5.0
    },
    {
        "id": "slide_12",
        "bg": "mod_page/assets/gallery/village_storm.jpg",
        "title": "ОСОБАЯ КОНТРРАЗВЕДКА ЛЬВА ЗАДОВА",
        "subtitle": "Чистки от шпионов НКВД, белогвардейских заговоров и спящие сети в тылу врага",
        "badge": "БЕЗОПАСНОСТЬ БЕЗ ГОСПЕРСОНАЛА",
        "duration": 4.5
    },
    {
        "id": "slide_13",
        "bg": "mod_page/assets/news/radio_tower.jpg",
        "title": "ГОРДОСТЬ ДВИЖЕНИЯ: ЛИДЕРЫ И КОМАНДИРЫ",
        "subtitle": "Белаш, Щусь, Кузьменко, Никифорова, Каретник с аутентичными портретами",
        "badge": "ИСТОРИЧЕСКИЕ ДЕЯТЕЛИ И СОВЕТНИКИ",
        "duration": 4.5
    },
    {
        "id": "slide_14",
        "bg": "mod_page/assets/banners/banner_story.jpg",
        "title": "СВЫШЕ 190 НАЦИОНАЛЬНЫХ ФОКУСОВ",
        "subtitle": "Колоссальное древо развития, союзы с мировыми державами или Чёрный Интернационал",
        "badge": "НЕБЫВАЛАЯ ГЛУБИНА И РЕИГРАБЕЛЬНОСТЬ",
        "duration": 5.0
    },
    {
        "id": "slide_15",
        "bg": "mod_page/assets/historical_makhno_berdyansk_1919.jpg",
        "title": "НЕСТОР МАХНО И ШТАБ ПОВСТАНЦЕВ",
        "subtitle": "Культовый саундтрек «Монгол Шуудан», живая история и дух вольной борьбы",
        "badge": "ИСТОРИЧЕСКАЯ ХРОНИКА • БЕРДЯНСК, 1919",
        "custom_crop_top": 20,
        "card_height_reduction": 50,
        "duration": 5.0
    },
    {
        "id": "slide_16",
        "bg": "mod_page/assets/hero.jpg",
        "title": "ВСТУПАЙТЕ В БОЙ ЗА ВОЛЬНУЮ СТЕПЬ!",
        "subtitle": "Поднимайте чёрные знамёна! Судьба мира зависит от вашей воли!",
        "badge": "СКАЧИВАЙТЕ В STEAM WORKSHOP",
        "duration": 4.5
    },
    {
        "id": "slide_17",
        "is_outro": True,
        "duration": 6.0
    }
]

def make_standard_slide(slide):
    bg_path = os.path.join(ROOT, slide["bg"])
    im = Image.open(bg_path).convert("RGB")
    
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
    if "custom_crop_top" in slide:
        top = slide["custom_crop_top"]
    else:
        top = (im.height - HEIGHT) // 2
    im = im.crop((left, top, left + WIDTH, top + HEIGHT))
    
    im = ImageEnhance.Contrast(im).enhance(1.18)
    im = ImageEnhance.Color(im).enhance(0.85)
    
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    
    for y in range(HEIGHT):
        alpha = int(175 * (y / HEIGHT)**1.6)
        if y < 350:
            top_alpha = int(120 * ((350 - y) / 350)**1.8)
            alpha = max(alpha, top_alpha)
        odraw.line([(0, y), (WIDTH, y)], fill=(12, 10, 8, alpha))
        
    reduction = slide.get("card_height_reduction", 0)
    card_top = HEIGHT - 380 + reduction
    card_bot = HEIGHT - 90
    card_left = 120
    card_right = WIDTH - 120
    odraw.rectangle([card_left, card_top, card_right, card_bot], fill=(15, 13, 11, 215), outline=(195, 155, 90, 240), width=3)
    
    im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(im)
    
    font_badge = ImageFont.truetype(FONT_BOLD, 24)
    font_title = ImageFont.truetype(FONT_BLACK, 46 if reduction else 50)
    font_sub = ImageFont.truetype(FONT_REG, 28 if reduction else 32)
    
    # Badge
    badge_text = slide["badge"]
    bbox_b = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox_b[2] - bbox_b[0]
    bx = (WIDTH - bw) // 2
    by = card_top + (26 if reduction else 32)
    
    draw.line([(bx - 120, by + 14), (bx - 20, by + 14)], fill=(195, 155, 90), width=2)
    draw.line([(bx + bw + 20, by + 14), (bx + bw + 120, by + 14)], fill=(195, 155, 90), width=2)
    draw.text((bx, by), badge_text, fill=(235, 195, 115), font=font_badge)
    
    # Title
    title_text = slide["title"]
    bbox_t = draw.textbbox((0, 0), title_text, font=font_title)
    tw = bbox_t[2] - bbox_t[0]
    tx = (WIDTH - tw) // 2
    ty = card_top + (72 if reduction else 85)
    draw.text((tx + 2, ty + 2), title_text, fill=(0, 0, 0), font=font_title)
    draw.text((tx, ty), title_text, fill=(255, 255, 255), font=font_title)
    
    # Subtitle
    sub_text = slide["subtitle"]
    bbox_s = draw.textbbox((0, 0), sub_text, font=font_sub)
    sw = bbox_s[2] - bbox_s[0]
    sx = (WIDTH - sw) // 2
    sy = card_top + (155 if reduction else 175)
    draw.text((sx + 1, sy + 1), sub_text, fill=(0, 0, 0), font=font_sub)
    draw.text((sx, sy), sub_text, fill=(215, 210, 195), font=font_sub)
    
    out_img = os.path.join(SLIDES_DIR, f"{slide['id']}.png")
    im.save(out_img, quality=95)
    return out_img

def make_outro_slide(slide):
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

    out_img = os.path.join(SLIDES_DIR, f"{slide['id']}.png")
    im.save(out_img, quality=95)
    return out_img

print("Generating slide images...")
for s in slides_data:
    if s.get("is_outro"):
        make_outro_slide(s)
    else:
        make_standard_slide(s)

print("Encoding video clips...")
clip_files = []
for idx, s in enumerate(slides_data):
    img_path = os.path.join(SLIDES_DIR, f"{s['id']}.png")
    out_clip = os.path.join(CLIPS_DIR, f"clip_{idx:02d}.mp4")
    clip_files.append(out_clip)
    
    dur = s["duration"]
    if s.get("is_outro"):
        # Long cinematic fade out to black at the end
        vf = f"fade=t=in:st=0:d=0.8,fade=t=out:st={dur-2.0}:d=2.0"
    else:
        vf = f"fade=t=in:st=0:d=0.4,fade=t=out:st={dur-0.4}:d=0.4"
        
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-t", str(dur),
        "-i", img_path,
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        out_clip
    ]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Encoded clip {idx+1}/{len(slides_data)}")

# Concat
concat_list_path = os.path.join(CLIPS_DIR, "concat.txt")
with open(concat_list_path, "w") as f:
    for cf in clip_files:
        f.write(f"file '{cf}'\n")

raw_video = os.path.join(OUTPUT_DIR, "raw_video_v3.mp4")
cmd_concat = [
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", concat_list_path,
    "-c", "copy",
    raw_video
]
subprocess.check_call(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

total_dur = sum(s["duration"] for s in slides_data)
print(f"Total video duration: {total_dur}s")

# Audio fade out synchronized with final blackout
cmd_final = [
    "ffmpeg", "-y",
    "-i", raw_video,
    "-ss", "0",
    "-t", str(total_dur),
    "-i", AUDIO_TRACK,
    "-map", "0:v",
    "-map", "1:a",
    "-af", f"afade=t=in:st=0:d=1.0,afade=t=out:st={total_dur-3.0}:d=3.0",
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "256k",
    "-shortest",
    FINAL_VIDEO
]
subprocess.check_call(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Copy to brain for instant artifact preview
BRAIN_PROMO = "/home/astra/.gemini/antigravity/brain/cbfb705e-7ae6-4c0e-9385-273c0ec0cce5/gulyaypole_mod_official_trailer.mp4"
subprocess.check_call(["cp", FINAL_VIDEO, BRAIN_PROMO])

print(f"SUCCESS! New promo video compiled to {FINAL_VIDEO} and {BRAIN_PROMO}")
