#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — сборка флага Вольной Территоріи.
#
#  Полотнище чёрное; по центру — знакъ анархіи Ⓐ (заглавная A, перекладина
#  выходитъ за ножки, вписана въ окружность). Сверху дугою «СВОБОДА ИЛИ
#  СМЕРТЬ!», снизу «ЧОРНАЯ ГВАРДІЯ».
#
#  Флагъ строится ВЕКТОРНО съ нуля въ разрешеніи 1640x1040 (20-кратный
#  игровой large), поэтому ужимка до 82x52 остаётся чистой. Никакихъ
#  растровыхъ мастеровъ съ артефактами.
#
#  Размѣры флаговъ HOI4: 82x52 (large), 41x26 (medium), 10x7 (small).
#  .tga пишутся перевёрнутыми (bottom-left origin, 32 бита) — какъ ваниль.
#
#  Требуется ImageMagick и шрифтъ DejaVu Sans Bold (кириллица + «І»).
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."

FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if [ ! -f "$FONT" ]; then
	echo "!! нет шрифта $FONT" >&2
	exit 1
fi

# --- 1. Знакъ анархіи --------------------------------------------------------
convert -size 1400x1400 xc:none \
	-fill none -stroke white -strokewidth 96 -draw 'circle 700,700 700,146' \
	-draw "stroke-linecap round stroke-width 118 line 700,318 366,1108" \
	-draw "stroke-linecap round stroke-width 118 line 700,318 1034,1108" \
	-draw "stroke-linecap round stroke-width 104 line 132,896 1268,896" \
	"$TMP/ca.png"

# --- 2. Надписи --------------------------------------------------------------
# Верхняя изгибается дугою (-distort Arc), нижняя — прямая.
convert -background none -fill white -font "$FONT" -pointsize 150 -kerning 10 \
	label:"СВОБОДА ИЛИ СМЕРТЬ!" -trim +repage "$TMP/top_flat.png"
convert "$TMP/top_flat.png" -background none -virtual-pixel none \
	-distort Arc '42' +repage "$TMP/top_arc.png"
convert -background none -fill white -font "$FONT" -pointsize 190 -kerning 14 \
	label:"ЧОРНАЯ ГВАРДІЯ" -trim +repage "$TMP/bot.png"

# --- 3. Полотнище ------------------------------------------------------------
convert -size 1640x1040 xc:black \
	\( "$TMP/top_arc.png" -resize 1290x \) -gravity north -geometry +0+34 -composite \
	\( "$TMP/ca.png"      -resize 560x560 \) -gravity center -geometry +0-4 -composite \
	\( "$TMP/bot.png"     -resize 1210x \) -gravity south -geometry +0+46 -composite \
	"$TMP/master.png"
echo ">> полотнище собрано (1640x1040)"

# --- 4. Витрина мод-страницы -------------------------------------------------
convert "$TMP/master.png" -colorspace sRGB -type TrueColor -resize 410x260! \
	mod_page/assets/flag_upright.png
convert mod_page/assets/flag_upright.png -flip mod_page/assets/flag.png
echo "   mod_page/assets/flag_upright.png + flag.png"

# --- 5. Игровые .tga ---------------------------------------------------------
for pair in "82x52:gfx/flags" "41x26:gfx/flags/medium" "10x7:gfx/flags/small"; do
	dim="${pair%%:*}"; dir="${pair##*:}"
	convert "$TMP/master.png" -flip -colorspace sRGB \
		-filter Lanczos -resize "${dim}!" \
		-alpha set -channel A -evaluate set 100% +channel \
		-define tga:image-origin=bottom-left -compress none \
		"TGA:$dir/GLP.tga"
	for v in anarchism communism democratic fascism neutrality; do
		cp "$dir/GLP.tga" "$dir/GLP_$v.tga"
	done
	echo "   $dir/GLP*.tga ($dim, 32-bit TGA)"
done

echo "готово."
