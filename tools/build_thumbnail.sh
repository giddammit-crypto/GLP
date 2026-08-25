#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — карточка мода для лаунчера Paradox / Steam Workshop
#
#  Спецификация (официальная, HOI4 wiki «Mod structure»):
#     * файл   : thumbnail.png в корне мода (рядом с descriptor.mod)
#     * ссылка : picture = "thumbnail.png" в descriptor.mod
#     * размер : 1:1 (512x512 — принятый размер для Workshop)
#     * вес    : строго < 1 МБ (иначе ParadoxMods/Workshop не примут)
#
#  Оформление — то же, что на загрузочных экранах мода:
#     * «царская» антиква Source Serif Pro (SIL OFL, tools/fonts)
#     * дореформенная орфография, холодная сепия + зерно плёнки
#     * Батько Махно крупным планом + название мода
#
#  Требуется ImageMagick. Идемпотентно: thumbnail.png пересобирается заново.
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."

F="tools/fonts"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

SIZE=512
OUT="thumbnail.png"

FONT_TITLE="$F/SourceSerifPro-Black.ttf"
FONT_SUB="$F/SourceSerifPro-Bold.ttf"
FONT_TEXT="$F/SourceSerifPro-Regular.ttf"

SRC="gfx/leaders/GLP/_src_nestor_makhno_large.jpg"
[ -f "$SRC" ] || { echo "!! мастер портрета не найден: $SRC" >&2; exit 1; }

# ---------------------------------------------------------------- 1) портрет
# Крупный план (голова/плечи), кинематографическая сепия + виньетка + зерно —
# та же «рецептура», что и colorgrade() в tools/build_portraits.sh.
convert "$SRC" -colorspace sRGB \
	-gravity north -crop 100%x72%+0+4% +repage \
	-resize "${SIZE}x${SIZE}^" -gravity center -extent "${SIZE}x${SIZE}" \
	-modulate 118,92,100 \
	-sigmoidal-contrast 1.5x50% \
	-fill '#2a2723' -colorize 2 \
	\( -size "${SIZE}x${SIZE}" radial-gradient:white-gray82 \) -compose multiply -composite \
	\( +clone -colorspace Gray -fill gray50 -colorize 100 -attenuate 0.22 +noise Gaussian \) \
		-compose overlay -composite \
	-unsharp 0x0.6+0.45+0.01 \
	"$TMP/portrait.png"

# -------------------------------------------------- 2) плашки под надписи
# Тёмные градиенты сверху и снизу для читаемости титров поверх портрета.
convert "$TMP/portrait.png" \
	\( -size ${SIZE}x220 gradient:'#0a0806f2'-'#0a080600' \) -gravity north -composite \
	\( -size ${SIZE}x140 gradient:'#0a080600'-'#0a0806e6' \) -gravity south -composite \
	"$TMP/base.png"

# ----------------------------------------------------------- 3) титры
convert "$TMP/base.png" \
	-font "$FONT_TITLE" -pointsize 52 -kerning 12 -gravity north \
	-fill '#00000066' -annotate +0+40 "ГУЛЯЙПОЛЕ" \
	-fill '#ece6d8'   -annotate +0+37 "ГУЛЯЙПОЛЕ" \
	-font "$FONT_SUB" -pointsize 21 -kerning 8 -gravity north \
	-fill '#00000066' -annotate +0+104 "ВОЛЬНАЯ ТЕРРИТОРІЯ" \
	-fill '#c0392b'   -annotate +0+101 "ВОЛЬНАЯ ТЕРРИТОРІЯ" \
	-font "$FONT_TEXT" -pointsize 13 -kerning 5 -gravity north \
	-fill '#00000066' -annotate +0+136 "АНАРХІЯ — МАТЬ ПОРЯДКА · 1936" \
	-fill '#8d8674'   -annotate +0+133 "АНАРХІЯ — МАТЬ ПОРЯДКА · 1936" \
	-font "$FONT_TEXT" -pointsize 12 -kerning 6 -gravity south \
	-fill '#00000055' -annotate +0+20 "HEARTS OF IRON IV · TOTAL CONVERSION" \
	-fill '#9a958a'   -annotate +0+19 "HEARTS OF IRON IV · TOTAL CONVERSION" \
	"$TMP/titled.png"

# --------------------------------------------------- 4) рамка и финальный PNG
convert "$TMP/titled.png" \
	\( -size ${SIZE}x${SIZE} xc:none -fill none -stroke '#ece6d8' -strokewidth 2 \
	   -draw "rectangle 1,1 $((SIZE-2)),$((SIZE-2))" -channel A -evaluate set 18% +channel \) \
	-composite \
	-strip -define png:color-type=2 -depth 8 \
	"$OUT"

# Проверка веса (Workshop: < 1 МБ).
bytes=$(stat -c %s "$OUT" 2>/dev/null || stat -f %z "$OUT")
if [ "$bytes" -ge 1048576 ]; then
	echo "!! thumbnail.png весит ${bytes} байт (лимит 1 МБ)" >&2
	exit 1
fi
echo "thumbnail.png: ${SIZE}x${SIZE}, ${bytes} байт — готово."
