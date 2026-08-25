#!/usr/bin/env python3
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — генератор текстур кинематографической заставки (HOI4 1.19.x)
#
#  Пересобирает:
#    gfx/interface/intro/gulyaipole_text_crawl.dds  — лента титров 310x4096,
#        текст берётся ИЗ ЛОКАЛИЗАЦИИ (GULYAIPOLE_EPIC_INTRO_TEXT, RU),
#        поэтому лента всегда соответствует тексту в игре. Лента заполняется
#        от верхнего края (движок показывает верх ленты первым), без пустой
#        верхней половины, из-за которой «не было кинематографического текста».
#    gfx/interface/intro/gulyaipole_text_mask.dds   — маска 310x525.
#        ВАЖНО: движок Clausewitz маскирует анимацию по ЯРКОСТИ RGB-каналов
#        (белый = видно, чёрный = скрыто), альфа маски игнорируется. Маска
#        обязана быть БЕЛЫМ градиентом в RGB с непрозрачной альфой.
#        Прежняя маска (чёрный RGB + градиент в альфе) делала текст
#        полностью невидимым.
#
#  Зависимости: Pillow (pip install pillow), ImageMagick 6/7 (convert).
#  Источники сохраняются в tools/_gfx_src/*_v3.png (воспроизводимость).
# =============================================================================
import os
import re
import subprocess
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Нужен Pillow: pip install pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "_gfx_src")
FONT_BOLD = os.path.join(ROOT, "tools", "fonts", "SourceSerifPro-Bold.ttf")
FONT_BLACK = os.path.join(ROOT, "tools", "fonts", "SourceSerifPro-Black.ttf")

W, H = 310, 4096          # лента титров
MASK_W, MASK_H = 310, 525  # маска окна прокрутки
MARGIN_X = 16
TEXT_W = W - 2 * MARGIN_X
TOP_PAD = 64
BOTTOM_PAD = 48

CREAM = (238, 224, 182)    # основной цвет текста (кремовый, режим blend=add)
GOLD = (246, 227, 166)     # заголовок


def read_epic_text():
    """Текст из русской локализации — единственный источник правды."""
    p = os.path.join(ROOT, "localisation/russian/gulyaipole_intro_text_l_russian.yml")
    raw = open(p, encoding="utf-8-sig").read()
    m = re.search(r'GULYAIPOLE_EPIC_INTRO_TEXT:0\s+"(.*?)"\s*$', raw, re.S | re.M)
    if not m:
        sys.exit("Ключ GULYAIPOLE_EPIC_INTRO_TEXT не найден в локализации")
    val = m.group(1)
    val = val.replace("\\n", "\n")
    val = re.sub("\u00a7[A-Za-z!]", "", val)  # убрать коды цвета §Y/§! и т.п.
    return [blk.strip() for blk in val.split("\n\n") if blk.strip()]


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_crawl():
    blocks = read_epic_text()
    # Подбор размера шрифта: заполнить ленту от TOP_PAD до H-BOTTOM_PAD.
    for size, leading, para_gap in ((21, 30, 16), (20, 29, 15), (19, 27, 14),
                                    (18, 26, 13), (17, 25, 12), (16, 23, 11),
                                    (15, 22, 10)):
        font = ImageFont.truetype(FONT_BOLD, size)
        font_head = ImageFont.truetype(FONT_BLACK, size + 3)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        laid, y = [], TOP_PAD
        for bi, block in enumerate(blocks):
            f = font_head if bi == 0 else font
            lines = wrap(d, block.replace("\n", " "), f, TEXT_W)
            for ln in lines:
                laid.append((ln, f, y))
                y += leading
            y += para_gap
        if TOP_PAD < y <= H - BOTTOM_PAD:
            for ln, f, yy in laid:
                d.text((MARGIN_X, yy), ln, font=f, fill=CREAM + (255,))
            if bi == 0:
                pass
            print(f"crawl: font={size}px leading={leading} lines={len(laid)} "
                  f"text_span={TOP_PAD}..{y} of {H}")
            return img
    sys.exit("Текст не влезает в ленту 4096px даже при 15px — сократите текст")


def render_mask():
    """Белый градиент в RGB (движок маскирует по яркости!), альфа непрозрачная."""
    img = Image.new("RGBA", (MASK_W, MASK_H), (255, 255, 255, 255))
    px = img.load()
    fade_top, fade_bottom = 56, 56
    for yy in range(MASK_H):
        if yy < fade_top:
            v = int(255 * (yy / fade_top) ** 1.5)
        elif yy >= MASK_H - fade_bottom:
            v = int(255 * ((MASK_H - yy) / fade_bottom) ** 1.5)
        else:
            v = 255
        for xx in range(MASK_W):
            px[xx, yy] = (v, v, v, 255)
    print(f"mask: {MASK_W}x{MASK_H} white RGB gradient, opaque alpha")
    return img


def to_dds(png_path, dds_path, compression):
    subprocess.run(
        ["convert", png_path,
         "-define", f"dds:compression={compression}",
         "-define", "dds:mipmaps=0",
         "DDS:" + dds_path],
        check=True)
    print(f"dds: {os.path.relpath(dds_path, ROOT)} ({compression})")


if __name__ == "__main__":
    os.makedirs(SRC, exist_ok=True)
    crawl = render_crawl()
    crawl_png = os.path.join(SRC, "gulyaipole_text_crawl_v3.png")
    crawl.save(crawl_png)
    to_dds(crawl_png, os.path.join(ROOT, "gfx/interface/intro/gulyaipole_text_crawl.dds"), "dxt5")

    mask = render_mask()
    mask_png = os.path.join(SRC, "gulyaipole_text_mask_v3.png")
    mask.save(mask_png)
    to_dds(mask_png, os.path.join(ROOT, "gfx/interface/intro/gulyaipole_text_mask.dds"), "dxt5")
    print("OK")
