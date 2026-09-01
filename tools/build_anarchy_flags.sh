#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — пересборка флаговъ страны съ знакомъ анархіи (circle-A).
#
#  Раньше на полотнищѣ былъ черепъ съ костями; теперь по центру — классическій
#  анархистскій символъ Ⓐ (заглавная A, перекладина выходитъ за ножки, вписана
#  въ окружность). Надписи «СВОБОДА ИЛИ СМЕРТЬ!» сверху и «ЧОРНАЯ ГВАРДІЯ»
#  снизу сохранены безъ измѣненій.
#
#  Мастеръ полотнища: mod_page/assets/flag_upright.png (410x260, «читаемая»
#  ориентація). Игровые .tga пишутся перевёрнутыми по вертикали (bottom-left
#  origin, 32 бита) — точно какъ ванильные флаги HOI4.
#
#  Размѣры флаговъ HOI4: 82x52 (large), 41x26 (medium), 10x7 (small).
#  Требуется ImageMagick.
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."

MASTER="mod_page/assets/flag_upright.png"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# --- 1. Знакъ анархіи: окружность + A съ вылетающей перекладиной -------------
convert -size 1000x1000 xc:none \
	-fill none -stroke white -strokewidth 74 -draw 'circle 500,500 500,102' \
	-draw "stroke-linecap round stroke-width 88 line 500,232 252,806" \
	-draw "stroke-linecap round stroke-width 88 line 500,232 748,806" \
	-draw "stroke-linecap round stroke-width 78 line 92,648 908,648" \
	"$TMP/circleA.png"
convert "$TMP/circleA.png" -resize 148x148 "$TMP/circleA_148.png"
echo ">> знакъ анархіи собранъ"

# --- 2. Мастеръ полотнища ----------------------------------------------------
# Область прежняго черепа (x 141..273, y 50..203) вычищается въ чёрное,
# на её мѣсто ставится Ⓐ. Надписи не затрагиваются.
if [ ! -f "$MASTER" ]; then
	echo "!! нет мастера $MASTER" >&2
	exit 1
fi
convert "$MASTER" -fill black -draw 'rectangle 141,50 273,203' \
	"$TMP/circleA_148.png" -geometry +133+53 -compose over -composite \
	"$TMP/flag_master.png"
cp "$TMP/flag_master.png" "$MASTER"
convert "$TMP/flag_master.png" -flip mod_page/assets/flag.png
echo "   $MASTER + mod_page/assets/flag.png"

# --- 3. Игровые .tga ---------------------------------------------------------
# GLP.tga — основной; идеологическіе варіанты пока идентичны основному.
for pair in "82x52:gfx/flags" "41x26:gfx/flags/medium" "10x7:gfx/flags/small"; do
	dim="${pair%%:*}"; dir="${pair##*:}"
	convert "$TMP/flag_master.png" -flip -colorspace sRGB \
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
