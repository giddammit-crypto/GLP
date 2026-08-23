#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — сборка экранов загрузки, фона главного меню и логотипа
#
#  Спецификация (ТЗ, раздел 1):
#     * загрузочные экраны : 1920x1080, .dds DXT1, без мип-мап
#     * фон главного меню  : 1920x1080, .dds DXT1
#     * цветокоррекция     : холодные серо-коричневые и угольные тона,
#                            естественная плёночная зернистость
#     * подпись авторства  : «Сработалъ О. А. Амброзіевъ» (правый нижний уголъ)
#     * шрифтъ             : «царская» антиква Source Serif Pro (SIL OFL),
#                            дореформенная орѳографія и обороты конца 1920-хъ
#
#  Ванильные экраны загрузки перекрываются одноимёнными файлами load_1..load_16,
#  поэтому въ игрѣ показываются ТОЛЬКО фоны мода.
#
#  Источники: gfx/loadingscreens/_src_*.jpg
#  Требуется ImageMagick.
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."

LS="gfx/loadingscreens"
F="tools/fonts"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

FONT_TITLE="$F/SourceSerifPro-Black.ttf"
FONT_SUB="$F/SourceSerifPro-Bold.ttf"
FONT_TEXT="$F/SourceSerifPro-Regular.ttf"

TITLE="ГУЛЯЙ-ПОЛЕ"
SUBTITLE="ВОЛЬНАЯ ТЕРРИТОРІЯ"
CREDIT="Сработалъ О. А. Амброзіевъ"

# Девизы въ языкѣ конца 1920-хъ — по одному на каждый экранъ загрузки.
declare -A MOTTO=(
	[load_tachanka]="Тачанка — царица степи: гдѣ пулеметъ, тамъ и воля трудового народа"
	[cavalry_charge]="Шашки вонъ! За землю, за волю, за вольные совѣты!"
	[armored_train]="Стальной таранъ повстанья идетъ степною чугункою"
	[camp_council]="Вольный сходъ рѣшаетъ самъ: ни господъ, ни комиссаровъ"
	[village_storm]="Гуляй-Поле — стольный градъ вольной степи"
	[machinegun_line]="Ни шагу съ вольной земли: степь врагу не отдадимъ"
	[menu_bg]="Анархія — мать порядка"
)

# Кинематографическая цветокоррекція 1930-хъ + зерно плёнки.
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

# Наборная плашка внизу кадра: затемняющая полоса, двойная линейка,
# названіе проекта, девизъ и подпись автора «царскимъ» шрифтомъ.
plate() {  # $1 png (in place), $2 девизъ
	local motto="$2"
	convert "$1" \
		\( -size 1920x210 gradient:none-'#000000cc' \) -gravity south -compose over -composite \
		-stroke '#8e8471' -strokewidth 2 -draw "line 64,918 1856,918" \
		-stroke '#8e847155' -strokewidth 1 -draw "line 64,925 1856,925" \
		-stroke none -gravity southwest \
		-font "$FONT_TITLE" -pointsize 46 -kerning 14 \
		-fill '#000000aa' -annotate +67+69 "$TITLE" \
		-fill '#ece6d8' -annotate +64+70 "$TITLE" \
		-font "$FONT_SUB" -pointsize 22 -kerning 9 \
		-fill '#b8ac95' -annotate +68+40 "$SUBTITLE" \
		-font "$FONT_TEXT" -pointsize 27 -kerning 0 -gravity southeast \
		-fill '#000000aa' -annotate +65+99 "$motto" \
		-fill '#d8d2c2' -annotate +64+100 "$motto" \
		-font "$FONT_TEXT" -pointsize 20 \
		-fill '#000000aa' -annotate +65+59 "$CREDIT" \
		-fill '#a49d8c' -annotate +64+60 "$CREDIT" \
		"$1"
}

to_dds() {  # $1 png, $2 dds
	convert "$1" -alpha off -define dds:compression=dxt1 -define dds:mipmaps=0 "DDS:$2"
}

echo ">> загрузочные экраны 1920x1080 DXT1"
SCREENS=()
for src in "$LS"/_src_*.jpg; do
	[ -e "$src" ] || continue
	slug="$(basename "$src" .jpg)"; slug="${slug#_src_}"
	[ "$slug" = "menu_bg" ] && continue          # фонъ меню собирается отдѣльно
	png="$TMP/$slug.png"
	grade "$src" "$png"
	plate "$png" "${MOTTO[$slug]:-$SUBTITLE}"
	out="$LS/load_glp_${slug#load_}.dds"
	to_dds "$png" "$out"
	SCREENS+=("$out")
	echo "   $out"
done

if [ "${#SCREENS[@]}" -eq 0 ]; then
	echo "!! мастера загрузочныхъ экрановъ не найдены" >&2
	exit 1
fi

echo ">> перекрытіе ванильныхъ экрановъ (load_1..load_16)"
i=0
for n in $(seq 1 16); do
	cp "${SCREENS[$(( i % ${#SCREENS[@]} ))]}" "$LS/load_$n.dds"
	i=$(( i + 1 ))
done
echo "   load_1.dds .. load_16.dds"

echo ">> фонъ главнаго меню"
if [ -f "$LS/_src_menu_bg.jpg" ]; then
	png="$TMP/menu.png"
	grade "$LS/_src_menu_bg.jpg" "$png"
	# въ меню — только скромный картушъ автора справа внизу: названіе несётъ логотипъ
	convert "$png" \
		-font "$FONT_TEXT" -pointsize 25 -gravity southeast \
		-fill '#000000aa' -annotate +49+59 "${MOTTO[menu_bg]}" \
		-fill '#cdc6b4' -annotate +48+60 "${MOTTO[menu_bg]}" \
		-pointsize 20 \
		-fill '#000000aa' -annotate +49+29 "$CREDIT" \
		-fill '#a49d8c' -annotate +48+30 "$CREDIT" \
		"$png"
	to_dds "$png" "gfx/interface/frontendmainviewbg.dds"
	echo "   gfx/interface/frontendmainviewbg.dds"
fi

echo ">> логотипъ мода 800x200"
mkdir -p gfx/interface/logo
convert -size 800x200 xc:none \
	-font "$FONT_TITLE" -pointsize 82 -kerning 12 -gravity north \
	-fill '#00000099' -annotate +3+27 "$TITLE" \
	-fill '#ece6d8' -annotate +0+24 "$TITLE" \
	-stroke '#8e8471' -strokewidth 2 -draw "line 120,116 680,116" \
	-stroke '#8e847166' -strokewidth 1 -draw "line 120,122 680,122" \
	-stroke none \
	-font "$FONT_SUB" -pointsize 30 -kerning 10 \
	-fill '#00000099' -annotate +3+133 "$SUBTITLE" \
	-fill '#b4342f' -annotate +0+130 "$SUBTITLE" \
	-font "$FONT_TEXT" -pointsize 19 -kerning 1 \
	-fill '#9a958a' -annotate +0+172 "$CREDIT" \
	-alpha set -define dds:compression=dxt5 -define dds:mipmaps=0 \
	"DDS:gfx/interface/logo/game_logo.dds"
echo "   gfx/interface/logo/game_logo.dds"

echo "готово."
