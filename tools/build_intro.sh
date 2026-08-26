#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — сборка текстур кинематографической заставки (HOI4 v1.19.2)
#
#  Пересобирает ТОЛЬКО сломанные в аудите 26.08.2026 текстуры окна
#  gulyaipole_cinematic_intro_window из ПРАВИЛЬНЫХ исходников:
#
#   * gfx/interface/intro/gulyaipole_gold_inner_border.dds (900x700, DXT5)
#       <- gfx/interface/_src_gold_inner_border.png (1168x912, барочная
#          золотая рамка). Раньше строился из деградированного
#          tools/_gfx_src/gold_inner_border_clean.png (тонкая линия, 94,8 %
#          прозрачных пикселей) — кайма была невидима в игре.
#       Исходник не имеет настоящего альфа-канала: центр — «фейковая
#       шахматка» (имитация прозрачности), углы — чёрный фон. Оба региона
#       превращаются в настоящий alpha=0 через flood-fill (python3/Pillow),
#       затем кайма затухает к центру окна (28 px сплошной край + градиент
#       до 72 px), чтобы не перекрывать текст и фото.
#
#   * gfx/interface/intro/gulyaipole_portrait_frame_gold.dds (166x220, DXT5)
#       <- тот же барочный исходник, масштабированный; оставляется только
#          внешний кольцевой пояс 14 px (внутренний проём 138x192
#          прозрачный), чтобы портрет 156x210 читался. Раньше строился из
#          tools/_gfx_src/portrait_frame_gold_final.png (тонкая линия, 89,7 %
#          прозрачных) — рамка портрета была невидима.
#
#   * gfx/interface/intro/gulyaipole_intro_bg.dds (900x700, DXT1)
#       <- gfx/interface/_src_tiled_bg_dark.png (1024x1024, состаренная
#          бумага, grain, noir) с подъёмом яркости (modulate 138). Раньше
#          строился из почти чёрного intro_bg_clean.png (средняя яркость
#          ~14 %) — окно читалось как пустой чёрный квадрат («пропал фон»).
#       Файл общий с GFX_tiled_bg_dark / GFX_tiled_bg_dark_tiled
#       (политический оверрайд) — бумага светлее и там тоже.
#
#  НЕ трогает (аудитом подтверждены годными): gulyaipole_cavalry.dds,
#  gulyaipole_ukraine_map.dds, Portrait_GLP_Makhno_Intro{,_large}.dds.
#
#  Требуется: ImageMagick 6.9 (DDS-кодер DXT1/DXT5) + python3 с Pillow.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

INTRO="gfx/interface/intro"
SRC_BORDER="gfx/interface/_src_gold_inner_border.png"
SRC_BG="gfx/interface/_src_tiled_bg_dark.png"

command -v convert >/dev/null || { echo "нужен ImageMagick (convert)" >&2; exit 1; }
python3 -c "import PIL" 2>/dev/null || { echo "нужен python3 с Pillow" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# ---------------------------------------------------------------------------
# 1. Барочная золотая рамка: настоящий альфа-канал из фейковой «прозрачности»
# ---------------------------------------------------------------------------
echo ">> маска прозрачности барочной рамки (flood-fill центр + углы)"
python3 - "$SRC_BORDER" "$TMP/border_alpha.png" <<'PY'
import queue, sys
from PIL import Image, ImageFilter

src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
W, H = im.size
px = im.load()

def flood(seed, tol=20):
    """Классический flood-fill от seed с допуском tol (по каждому каналу
    относительно цвета семени). Возвращает bytearray W*H (1 = достигнута)."""
    x0, y0 = seed
    r0, g0, b0 = px[x0, y0]
    seen = bytearray(W * H)
    q = queue.Queue()
    q.put((x0, y0))
    seen[y0 * W + x0] = 1
    while not q.empty():
        x, y = q.get()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < W and 0 <= ny < H and not seen[ny * W + nx]:
                nr, ng, nb = px[nx, ny]
                if abs(nr - r0) <= tol and abs(ng - g0) <= tol and abs(nb - b0) <= tol:
                    seen[ny * W + nx] = 1
                    q.put((nx, ny))
    return seen

# Прозрачные регионы: фейковая шахматка в проёме + чёрный фон в углах.
seeds = [(W // 2, H // 2), (0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1)]
transp = bytearray(W * H)
for s in seeds:
    m = flood(s)
    for i in range(W * H):
        if m[i]:
            transp[i] = 1

alpha = bytearray(W * H)
n_transp = 0
for i in range(W * H):
    if not transp[i]:
        alpha[i] = 255
    else:
        n_transp += 1
a = Image.frombytes('L', (W, H), bytes(alpha))
# Мягкий 1-px перо на границе (анти-алиасинг для DXT5).
a = a.filter(ImageFilter.GaussianBlur(1.0))
rgba = im.copy()
rgba.putalpha(a)
rgba.save(out)
print('   рамка %dx%d: прозрачно %d px (%.1f %%)'
      % (W, H, n_transp, 100.0 * n_transp / (W * H)))
PY

# ---------------------------------------------------------------------------
# 2. Кайма окна 900x700 DXT5: масштаб + затухание к центру
# ---------------------------------------------------------------------------
echo ">> кайма окна 900x700 DXT5 (затухание 28->72 px от края)"
python3 - "$TMP/border_alpha.png" "$TMP/border_900.png" <<'PY'
import sys
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGBA').resize((900, 700), Image.LANCZOS)
W, H = im.size
r, g, b, a = im.split()
# d = расстояние до ближайшего края; f(d)=1 при d<=28, 0 при d>=72.
data = bytearray(a.tobytes())
for y in range(H):
    dy = min(y, H - 1 - y)
    base = y * W
    for x in range(W):
        d = min(x, W - 1 - x, dy)
        if d <= 28:
            f = 1.0
        elif d >= 72:
            f = 0.0
        else:
            f = (72.0 - d) / 44.0
        data[base + x] = int(data[base + x] * f)
a2 = Image.frombytes('L', (W, H), bytes(data))
im.putalpha(a2)
im.save(out)
PY
convert "$TMP/border_900.png" -alpha set \
    -define dds:compression=dxt5 -define dds:mipmaps=0 \
    "DDS:$INTRO/gulyaipole_gold_inner_border.dds"

# ---------------------------------------------------------------------------
# 3. Рамка портрета 166x220 DXT5: барочный кольцевой пояс 14 px
# ---------------------------------------------------------------------------
echo ">> рамка портрета 166x220 DXT5 (пояс 14 px, проём 138x192 прозрачен)"
python3 - "$TMP/border_alpha.png" "$TMP/frame_166.png" <<'PY'
import sys
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGBA').resize((166, 220), Image.LANCZOS)
W, H = im.size
RING = 14
r, g, b, a = im.split()
data = bytearray(a.tobytes())
for y in range(H):
    in_open_y = RING <= y <= H - 1 - RING
    base = y * W
    for x in range(W):
        if in_open_y and RING <= x <= W - 1 - RING:
            data[base + x] = 0
a2 = Image.frombytes('L', (W, H), bytes(data))
im.putalpha(a2)
im.save(out)
PY
convert "$TMP/frame_166.png" -alpha set \
    -define dds:compression=dxt5 -define dds:mipmaps=0 \
    "DDS:$INTRO/gulyaipole_portrait_frame_gold.dds"

# ---------------------------------------------------------------------------
# 4. Фон окна 900x700 DXT1: состаренная бумага с подъёмом яркости
# ---------------------------------------------------------------------------
echo ">> фон окна 900x700 DXT1 (состаренная бумага, modulate 160)"
# ВАЖНО: -tint/-fill в ImageMagick 6.9 на низкой насыщенности резко
# затемняет картинку — не использовать; только подъём яркости/тёплый сдвиг.
convert "$SRC_BG" \
    -resize "900x700^" -gravity center -extent 900x700 \
    -colorspace sRGB -modulate 160,102,108 \
    -alpha off \
    -define dds:compression=dxt1 -define dds:mipmaps=0 \
    "DDS:$INTRO/gulyaipole_intro_bg.dds"

# ---------------------------------------------------------------------------
# 5. Контроль: размеры, формат, фактическое содержание
# ---------------------------------------------------------------------------
echo ">> контроль результатов"
python3 - "$INTRO" <<'PY'
import struct, sys, os
from PIL import Image

intro = sys.argv[1]
def hdr(p):
    d = open(p, 'rb').read()
    h, w = struct.unpack_from('<II', d, 12)  # в DDS сначала height, потом width
    _, _, cc, bc, rm, gm, bm, am = struct.unpack_from('<II4sIIIII', d, 76)
    return w, h, cc, bc, am, len(d) - 128

def avg_rgba(p):
    im = Image.open(p).convert('RGBA')
    w, h = im.size
    r = g = b = a = 0
    n = 0
    px = im.load()
    for y in range(0, h, 3):
        for x in range(0, w, 3):
            R, G, B, A = px[x, y]
            r += R; g += G; b += B; a += A; n += 1
    return r // n, g // n, b // n, a // n

expect = {
    'gulyaipole_gold_inner_border.dds': (900, 700, b'DXT5'),
    'gulyaipole_portrait_frame_gold.dds': (166, 220, b'DXT5'),
    'gulyaipole_intro_bg.dds': (900, 700, b'DXT1'),
}
ok = True
for name, (ew, eh, ecc) in expect.items():
    p = os.path.join(intro, name)
    w, h, cc, bc, am, data = hdr(p)
    ar, ag, ab, aa = avg_rgba(p)
    good = (w, h, cc) == (ew, eh, ecc)
    ok &= good
    print('   %-38s %dx%d %s data=%d avgRGBA=(%d,%d,%d,%d) %s'
          % (name, w, h, cc.decode(), data, ar, ag, ab, aa, 'OK' if good else 'BAD'))
if not ok:
    sys.exit(1)
print('   все текстуры заставки собраны корректно')
PY

echo "готово."
