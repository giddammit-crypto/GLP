#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — сборка экрановъ загрузки, фона главнаго меню и логотипа
#
#  Спецификація (ТЗ, разделъ 1):
#     * загрузочные экраны : 1920x1080, .dds DXT1, безъ мип-мапъ, адаптивные
#     * фонъ главнаго меню : 1920x1080, .dds DXT1, растягивается на весь экранъ
#     * цветокоррекція     : холодные серо-коричневые и угольные тона + зерно
#     * титры              : «царская» антиква Source Serif Pro (SIL OFL),
#                            дореформенная орѳографія
#     * на каждомъ экранѣ  : цитата анархистовъ (Махно, Кропоткинъ, Бакунинъ,
#                            Прудонъ), помѣтка «альтернативная исторія»
#                            и строка «Разработка мода — Амброзіевъ О. А.»
#     * логотипъ           : покадровая анимація «выѣзда» сверху внизъ
#                            (frameAnimatedSpriteType, 18 кадровъ)
#
#  Ванильные экраны загрузки перекрываются файлами load_1..load_16.
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
FONT_QUOTE="$F/SourceSerifPro-Regular.ttf"   # италикъ в наборе шрифта безъ кириллицы

TITLE="ГУЛЯЙ-ПОЛЕ"
SUBTITLE="ВОЛЬНАЯ ТЕРРИТОРІЯ"
ALTHIST="АЛЬТЕРНАТИВНАЯ ИСТОРІЯ · 1936"
CREDIT="Разработка мода — Амброзіевъ О. А."

# Цитаты вольной мысли: текстъ | авторъ
declare -A QUOTE=(
	[load_tachanka]="Свобода или смерть!|Девизъ Революціонной Повстанческой Арміи Украины"
	[cavalry_charge]="Страсть къ разрушенію есть вмѣстѣ съ тѣмъ и страсть творческая.|М. А. Бакунинъ"
	[armored_train]="Взаимная помощь — такой же законъ природы, какъ и взаимная борьба.|П. А. Кропоткинъ"
	[camp_council]="Земля — крестьянамъ, фабрики — рабочимъ!|Н. И. Махно"
	[village_storm]="Свобода — не дочь, а мать порядка.|П.-Ж. Прудонъ"
	[machinegun_line]="Свобода безъ соціализма — привилегія и несправедливость; соціализмъ безъ свободы — рабство.|М. А. Бакунинъ"
	[menu_bg]="Анархія — мать порядка.|П.-Ж. Прудонъ"
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

# Наборная плашка внизу кадра.
plate() {  # $1 png (in place), $2 "цитата|авторъ"
	local quote="${2%%|*}"
	local author="${2##*|}"
	convert "$1" \
		\( -size 1920x230 gradient:none-'#000000d0' \) -gravity south -compose over -composite \
		-stroke '#8e8471' -strokewidth 2 -draw "line 64,912 1856,912" \
		-stroke '#8e847155' -strokewidth 1 -draw "line 64,919 1856,919" \
		-stroke none -gravity southwest \
		-font "$FONT_TITLE" -pointsize 46 -kerning 14 \
		-fill '#000000aa' -annotate +67+95 "$TITLE" \
		-fill '#ece6d8' -annotate +64+96 "$TITLE" \
		-font "$FONT_SUB" -pointsize 21 -kerning 9 \
		-fill '#b8ac95' -annotate +68+66 "$SUBTITLE" \
		-font "$FONT_TEXT" -pointsize 17 -kerning 5 \
		-fill '#8d8674' -annotate +68+38 "$ALTHIST" \
		-gravity southeast \
		-font "$FONT_QUOTE" -pointsize 30 -kerning 0 \
		-fill '#000000aa' -annotate +65+109 "«$quote»" \
		-fill '#e2dccb' -annotate +64+110 "«$quote»" \
		-font "$FONT_TEXT" -pointsize 22 \
		-fill '#000000aa' -annotate +65+73 "— $author" \
		-fill '#b3ab98' -annotate +64+74 "— $author" \
		-font "$FONT_TEXT" -pointsize 18 \
		-fill '#000000aa' -annotate +65+37 "$CREDIT" \
		-fill '#9a927f' -annotate +64+38 "$CREDIT" \
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
	[ "$slug" = "menu_bg" ] && continue
	png="$TMP/$slug.png"
	grade "$src" "$png"
	plate "$png" "${QUOTE[$slug]:-$SUBTITLE|Гуляй-Поле}"
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

echo ">> фонъ главнаго меню (адаптивный, растягивается на весь экранъ)"
if [ -f "$LS/_src_menu_bg.jpg" ]; then
	png="$TMP/menu.png"
	grade "$LS/_src_menu_bg.jpg" "$png"
	q="${QUOTE[menu_bg]}"
	convert "$png" \
		-gravity southeast \
		-font "$FONT_QUOTE" -pointsize 26 \
		-fill '#000000aa' -annotate +49+89 "«${q%%|*}»" \
		-fill '#d5cfbd' -annotate +48+90 "«${q%%|*}»" \
		-font "$FONT_TEXT" -pointsize 20 \
		-fill '#000000aa' -annotate +49+59 "— ${q##*|}" \
		-fill '#a9a18e' -annotate +48+60 "— ${q##*|}" \
		-pointsize 18 \
		-fill '#000000aa' -annotate +49+29 "$CREDIT · альтернативная исторія" \
		-fill '#9a927f' -annotate +48+30 "$CREDIT · альтернативная исторія" \
		"$png"
	to_dds "$png" "gfx/interface/frontendmainviewbg.dds"
	echo "   gfx/interface/frontendmainviewbg.dds"
fi

echo ">> логотипъ мода: статическій кадръ + анимація выѣзда сверху внизъ"
mkdir -p gfx/interface/logo

# Одинъ кадръ логотипа: $1 — смѣщеніе по вертикали (px), $2 — прозрачность 0..1,
# $3 — файлъ-приёмникъ.
logo_frame() {
	local dy="$1" alpha="$2" out="$3"
	convert -size 800x200 xc:none \
		-font "$FONT_TITLE" -pointsize 74 -kerning 12 -gravity north \
		-fill '#00000099' -annotate +3+$(( 21 + dy )) "$TITLE" \
		-fill '#ece6d8' -annotate +0+$(( 18 + dy )) "$TITLE" \
		-stroke '#8e8471' -strokewidth 2 -draw "line 118,$(( 100 + dy )) 682,$(( 100 + dy ))" \
		-stroke '#8e847166' -strokewidth 1 -draw "line 118,$(( 106 + dy )) 682,$(( 106 + dy ))" \
		-stroke none \
		-font "$FONT_SUB" -pointsize 27 -kerning 9 \
		-fill '#00000099' -annotate +3+$(( 119 + dy )) "$SUBTITLE" \
		-fill '#b4342f' -annotate +0+$(( 116 + dy )) "$SUBTITLE" \
		-font "$FONT_TEXT" -pointsize 17 -kerning 4 \
		-fill '#8d8674' -annotate +0+$(( 152 + dy )) "АЛЬТЕРНАТИВНАЯ ИСТОРІЯ" \
		-font "$FONT_TEXT" -pointsize 17 -kerning 1 \
		-fill '#9a958a' -annotate +0+$(( 176 + dy )) "$CREDIT" \
		-channel A -evaluate multiply "$alpha" +channel \
		-background none -extent 800x200 \
		"$out"
}

FRAMES=18
rm -f "$TMP"/logo_*.png
for n in $(seq 0 $(( FRAMES - 1 ))); do
	# ease-out: смѣщеніе съ -70 px до 0, прозрачность съ 0.35 до 1.0
	t=$(python3 -c "print(f'{1-(1-$n/($FRAMES-1))**3:.4f}')")
	dy=$(python3 -c "print(int(round(-70*(1-$t))))")
	al=$(python3 -c "print(f'{0.35+0.65*$t:.3f}')")
	logo_frame "$dy" "$al" "$(printf "$TMP/logo_%02d.png" "$n")"
done

# статическій кадръ (на случай, если анимація отключена)
cp "$(printf "$TMP/logo_%02d.png" $(( FRAMES - 1 )))" "$TMP/logo_static.png"
convert "$TMP/logo_static.png" -alpha set \
	-define dds:compression=dxt5 -define dds:mipmaps=0 \
	"DDS:gfx/interface/logo/game_logo.dds"

# лента кадровъ для frameAnimatedSpriteType (кадры идутъ по горизонтали)
convert "$TMP"/logo_[0-9][0-9].png +append -alpha set \
	-define dds:compression=dxt5 -define dds:mipmaps=0 \
	"DDS:gfx/interface/logo/game_logo_anim.dds"
echo "   gfx/interface/logo/game_logo.dds (800x200)"
echo "   gfx/interface/logo/game_logo_anim.dds ($(( 800 * FRAMES ))x200, $FRAMES кадровъ)"

echo "готово."
