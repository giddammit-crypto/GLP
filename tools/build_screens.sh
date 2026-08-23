#!/usr/bin/env bash
# =============================================================================
#  GLP: сборка загрузочных экранов, фона главного меню и логотипа
#
#  Спецификация (ТЗ, раздел 1):
#     * загрузочные экраны : 1920x1080, .dds DXT1, без мип-мап
#     * фон главного меню  : 1920x1080, .dds DXT1
#     * цветокоррекция     : холодные серо-коричневые и угольные тона,
#                            естественная плёночная зернистость
#     * подпись авторства  : «Разработчик — Амброзиев О.А.» (правый нижний угол)
#     * название проекта   : «ГУЛЯЙ-ПОЛЕ: ВОЛЬНАЯ ТЕРРИТОРИЯ»
#
#  Ванильные экраны загрузки перекрываются одноимёнными файлами load_1..load_16,
#  поэтому в игре показываются ТОЛЬКО фоны мода.
#
#  Источники: gfx/loadingscreens/_src_*.jpg (или .png)
#  Требуется ImageMagick.
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."

LS="gfx/loadingscreens"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

FONT="DejaVu-Sans-Bold"
TITLE="ГУЛЯЙ-ПОЛЕ: ВОЛЬНАЯ ТЕРРИТОРИЯ"
CREDIT="Разработчик — Амброзиев О.А."

# Кинематографическая цветокоррекция 1930-х + зерно плёнки.
grade() {  # $1 in, $2 out(png)
	convert "$1" -colorspace sRGB \
		-resize "1920x1080^" -gravity center -extent 1920x1080 \
		-modulate 116,74,98 \
		-sigmoidal-contrast 2x52% \
		-fill '#20242b' -colorize 5 \
		-fill '#3a2f22' -tint 10 \
		\( -size 1920x1080 radial-gradient:white-gray72 \) -compose multiply -composite \
		\( +clone -colorspace Gray -fill gray50 -colorize 100 -attenuate 0.40 +noise Gaussian \) \
			-compose overlay -composite \
		-unsharp 0x0.8+0.5+0.01 \
		"$2"
}

stamp_title() {  # $1 in/out png
	convert "$1" \
		-font "$FONT" -kerning 6 -pointsize 34 \
		-fill '#0000009a' -annotate +63+1005 "$TITLE" \
		-fill '#e6e2d8' -annotate +61+1003 "$TITLE" \
		-kerning 1 -pointsize 20 \
		-gravity southeast \
		-fill '#000000a0' -annotate +47+37 "$CREDIT" \
		-fill '#c8c3b6' -annotate +48+38 "$CREDIT" \
		"$1"
}

to_dds() {  # $1 png, $2 dds
	convert "$1" -alpha off -define dds:compression=dxt1 -define dds:mipmaps=0 "DDS:$2"
}

echo ">> загрузочные экраны 1920x1080 DXT1"
SCREENS=()
for src in "$LS"/_src_*.jpg "$LS"/_src_*.png; do
	[ -e "$src" ] || continue
	slug="$(basename "$src")"; slug="${slug%.*}"; slug="${slug#_src_}"
	case "$slug" in menu_bg) continue ;; esac      # фон меню собирается отдельно
	png="$TMP/$slug.png"
	grade "$src" "$png"
	stamp_title "$png"
	out="$LS/load_glp_${slug#load_}.dds"
	to_dds "$png" "$out"
	SCREENS+=("$out")
	echo "   $out"
done

if [ "${#SCREENS[@]}" -eq 0 ]; then
	echo "!! мастера загрузочных экранов не найдены" >&2
	exit 1
fi

echo ">> перекрытие ванильных экранов (load_1..load_16)"
i=0
for n in $(seq 1 16); do
	cp "${SCREENS[$(( i % ${#SCREENS[@]} ))]}" "$LS/load_$n.dds"
	i=$(( i + 1 ))
done
echo "   load_1.dds .. load_16.dds"

echo ">> фон главного меню"
if [ -f "$LS/_src_menu_bg.jpg" ]; then
	png="$TMP/menu.png"
	grade "$LS/_src_menu_bg.jpg" "$png"
	# только подпись автора, без названия — название выводит логотип
	convert "$png" -font "$FONT" -kerning 1 -pointsize 21 -gravity southeast \
		-fill '#000000b0' -annotate +33+25 "$CREDIT" \
		-fill '#d5d0c2' -annotate +34+26 "$CREDIT" \
		"$png"
	to_dds "$png" "gfx/interface/frontendmainviewbg.dds"
	echo "   gfx/interface/frontendmainviewbg.dds"
fi

echo ">> логотип мода 800x200"
mkdir -p gfx/interface/logo
convert -size 800x200 xc:none \
	-font "$FONT" -kerning 10 -pointsize 76 -gravity north \
	-fill '#00000090' -annotate +3+31 "ГУЛЯЙ-ПОЛЕ" \
	-fill '#e8e4d9' -annotate +0+28 "ГУЛЯЙ-ПОЛЕ" \
	-kerning 12 -pointsize 30 \
	-fill '#00000090' -annotate +3+121 "ВОЛЬНАЯ ТЕРРИТОРИЯ" \
	-fill '#b4342f' -annotate +0+118 "ВОЛЬНАЯ ТЕРРИТОРИЯ" \
	-kerning 2 -pointsize 18 \
	-fill '#9a958a' -annotate +0+165 "Разработчик — Амброзиев О.А." \
	-alpha set -define dds:compression=dxt5 -define dds:mipmaps=0 \
	"DDS:gfx/interface/logo/game_logo.dds"
echo "   gfx/interface/logo/game_logo.dds"

echo "готово."
