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

TITLE="ГУЛЯЙПОЛЕ"
SUBTITLE="ВОЛЬНАЯ ТЕРРИТОРІЯ"
ALTHIST="АЛЬТЕРНАТИВНАЯ ИСТОРІЯ · 1936"
CREDIT="Разработка мода — Амброзіевъ О. А."

# Цитаты БОЛЬШЕ не запекаются в арт загрузочных экранов: их выводит
# текстбокс "tip" нашего override interface/load_screen.gui (15 px от
# нижней кромки экрана, ключи LOADING_TIP_* из localisation).
# «Свобода или смерть!» исключена из набора цитат по требованию.
declare -A QUOTE=(
	[cavalry_charge]=""
	[armored_train]=""
	[camp_council]=""
	[village_storm]=""
	[machinegun_line]=""
	[load_tachanka]=""
	[menu_bg]="Анархія — мать порядка.|П.-Ж. Прудонъ"
)

# Кинематографическая цветокоррекція 1930-хъ + зерно плёнки.
grade() {  # $1 in, $2 out(png)
	# Чуть свѣтлѣе прежняго (ТЗ: «слишкомъ темно»), но контрастность сохранена:
	# modulate Brightness 124 вмѣсто 116, виньетка слабѣе (gray78 вмѣсто gray72),
	# цвѣтной лойкрутъ 8 % вмѣсто 10, сигмоидальный контраст 1.7x вмѣсто 2x.
	convert "$1" -colorspace sRGB \
		-resize "1920x1080^" -gravity center -extent 1920x1080 \
		-modulate 124,80,100 \
		-sigmoidal-contrast 1.7x50% \
		-fill '#1c2026' -colorize 3 \
		-fill '#3a2f22' -tint 8 \
		\( -size 1920x1080 radial-gradient:white-gray78 \) -compose multiply -composite \
		\( +clone -colorspace Gray -fill gray50 -colorize 100 -attenuate 0.34 +noise Gaussian \) \
			-compose overlay -composite \
		-unsharp 0x0.8+0.5+0.01 \
		"$2"
}

# Наборная плашка:
#   * въ верхнемъ ЛѢВОМЪ углу — клеймо мода «ГУЛЯЙ-ПОЛЕ / ВОЛЬНАЯ ТЕРРИТОРІЯ /
#     АЛЬТЕРНАТИВНАЯ ИСТОРІЯ · 1936» (по ТЗ);
#   * въ нижнемъ правомъ — цитата съ атрибуціей и подписью автора.
# Сверху и снизу подложены градіентныя плашки, чтобы титры читались на любомъ фонѣ.
plate() {  # $1 png (in place), $2 "цитата|авторъ"
	local quote="${2%%|*}"
	local author="${2##*|}"
	convert "$1" \
		\( -size 1920x220 gradient:'#000000d8'-none \) -gravity north    -compose over -composite \
		-stroke '#8e8471' -strokewidth 2 -draw "line 64,152 1856,152" \
		-stroke '#8e847155' -strokewidth 1 -draw "line 64,159 1856,159" \
		-stroke none \
		-gravity northwest \
		-font "$FONT_TITLE" -pointsize 46 -kerning 14 \
		-fill '#000000aa' -annotate +67+62 "$TITLE" \
		-fill '#ece6d8' -annotate +64+60 "$TITLE" \
		-font "$FONT_SUB" -pointsize 21 -kerning 9 \
		-fill '#b8ac95' -annotate +68+109 "$SUBTITLE" \
		-font "$FONT_TEXT" -pointsize 17 -kerning 5 \
		-fill '#d8cfba' -annotate +68+129 "$ALTHIST" \
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
	plate "$png" "${QUOTE[$slug]:-$SUBTITLE|Гуляйполе}"
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

echo ">> фонъ главнаго меню (1920x1440 — эталонное 4:3 разрѣшеніе UI HOI4)"
# Эталонное разрѣшеніе интерфейса HOI4 — 1920x1440 (4:3). Прежній фонъ
# 1920x1080 corneredTile-спрайтъ растягивалъ по вертикали на экранахъ
# 16:10/4:3 и въ самой 4:3-сценѣ главнаго меню. Теперь фонъ собирается
# подъ 4:3: кинематографичная 16:9-сцена центрируется, а верхняя и нижняя
# полосы добираются сильно размытымъ продолженіемъ того же кадра —
# изображеніе не искажается и заполняетъ весь экранъ.
# Отдельный мастер главного меню хранится в tools/_gfx_src: у него уже
# предусмотрена тёмная свободная правая половина под кнопки меню. Если мастер
# отсутствует, сохраняем совместимый fallback на старый loading-screen source.
MENU_MASTER="tools/_gfx_src/frontend_menu_imperial_noir.png"
[ -f "$MENU_MASTER" ] || MENU_MASTER="$LS/_src_menu_bg.jpg"
if [ -f "$MENU_MASTER" ]; then
	convert "$MENU_MASTER" -resize 1920x1440! -alpha off \
		-define dds:compression=dxt1 -define dds:mipmaps=0 \
		"DDS:gfx/interface/frontendmainviewbg.dds"
	echo "   gfx/interface/frontendmainviewbg.dds (1920x1440)"
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
