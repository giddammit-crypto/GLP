#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — иконки национальных духов на тематическом фоне (60×68, DXT5)
#
#  По ТЗ «как в ванили»: национальный дух = тематическая подложка (щит/пламя/
#  солнце/…) + символ. Подложки взяты из репозитория-источника
#  Globvs/Ultimate-HOI4-GFX (папка «National Spirit Backgrounds», все 60×68,
#  свободны к использованию — см. CREDITS.txt и THIRD_PARTY_ASSETS.md) и лежат
#  в tools/_gfx_src/bg_*.png. Символ — существующий ИИ-мастер
#  tools/_icons_src/_src_<category>.png (белый фон вырезается), вписывается
#  внутрь подложки и кладётся поверх.
#
#  Углы остаются прозрачными (мин. альфа = 0, требование аудита).
#  Идемпотентно. Требуется ImageMagick 6/7.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

SRC="tools/_icons_src"
BG="tools/_gfx_src"
OUT="gfx/interface/ideas"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

CANVAS_W=60
CANVAS_H=68
FIT_W=42      # символ вписывается ВНУТРЬ подложки
FIT_H=46
KEY_FUZZ=8
ALPHA_THRESH=12

# категория -> подложка из Ultimate-HOI4-GFX
declare -A BACKGROUND=(
	[agriculture]=bg_Sun.png
	[black_guard_legacy]=bg_Shield.png
	[cavalry]=bg_Army.png
	[free_syndicates_and_soviets]=bg_Soviet.png
	[health]=bg_Circle.png
	[hostile_encirclement]=bg_Stop_Sign.png
	[industry]=bg_Bars.png
	[insurgent_army]=bg_Fire.png
	[intelligence]=bg_Intrigue.png
	[kontrrazvedka_surveillance]=bg_Military_Police.png
	[logistics]=bg_Upgrade.png
	[military]=bg_Pentagon.png
	[navy]=bg_Naval.png
	[society]=bg_Tiles.png
	[tachanka]=bg_Ring.png
)

build_one() {
	local cat="$1" bg="${BACKGROUND[$cat]}"
	local s="${SRC}/_src_${cat}.png"
	local b="${BG}/${bg}"
	local o="${OUT}/idea_GLP_${cat}.dds"
	[ -f "$s" ] || { echo "!! нет мастера для $cat" >&2; return 1; }
	[ -f "$b" ] || { echo "!! нет подложки $bg для $cat" >&2; return 1; }

	# подложка -> ровно 60×68 по центру прозрачной канвы
	convert "$b" -background none -gravity center -extent "${CANVAS_W}x${CANVAS_H}" "$TMP/bg.png"

	# символ: вырезать белый, кроп по bbox, вписать
	convert "$s" -fuzz ${KEY_FUZZ}% -transparent white "$TMP/keyed.png"
	convert "$TMP/keyed.png" -alpha extract -threshold ${ALPHA_THRESH}% "$TMP/mask.png"
	local bb; bb=$(convert "$TMP/mask.png" -format "%@" info:)
	convert "$TMP/keyed.png" -crop "$bb" +repage -resize "${FIT_W}x${FIT_H}>" "$TMP/motif.png"

	# лёгкая тёмная обводка, чтобы символ читался на цветной подложке
	convert "$TMP/motif.png" -alpha extract -morphology Dilate Disk:1.0 "$TMP/rim_a.png"
	local mw mh
	mw=$(identify -format '%w' "$TMP/motif.png"); mh=$(identify -format '%h' "$TMP/motif.png")
	convert -size "${mw}x${mh}" xc:"#1a140d" "$TMP/rim_a.png" -compose CopyOpacity -composite "$TMP/rim.png"
	convert "$TMP/rim.png" "$TMP/motif.png" -compose over -composite "$TMP/sym.png"

	# символ по центру подложки
	convert "$TMP/bg.png" "$TMP/sym.png" -gravity center -compose over -composite "$TMP/final.png"

	convert "$TMP/final.png" \
		-define dds:compression=dxt5 -define dds:mipmaps=0 "DDS:$o"
	echo "   $cat: фон $bg + символ -> $(basename "$o")"
}

for cat in "${!BACKGROUND[@]}"; do
	build_one "$cat"
done
echo "готово."
