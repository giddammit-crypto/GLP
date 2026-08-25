#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — сборка иконок национальных духов (60×68, несжатый BGRA DDS)
#
#  Иконки строятся НА ПРОЗРАЧНОМ ФОНЕ: тематический мотив (сгенерированный
#  ИИ-эмблем на белой подложке) вырезается по маске прозрачности и ставится
#  прямо на прозрачную канву 60×68 — без заполненного диска/«печати». Углы
#  остаются прозрачными (min alpha = 0, требование аудита).
#
#  Чтобы мотив читался на тёмном фоне слота идей HOI4, эмблемы генерируются
#  заполненными (не контурным артом), в холодной сепиево-бронзовой палитре с
#  тонкой тёмно-бронзовой обводкой. Дополнительно вокруг мотива добавляется
#  узкая бронзовая кромка (расширенный силуэт под мотивом) — она даёт
#  светлую окантовку на тёмном фоне и чёткий контур на светлом.
#
#  Источники мотива:
#   (A) ИИ-мастер  tools/_icons_src/_src_<category>.png — эмблема на белом
#       фоне (белый вырезается, мотив центрируется на прозрачной канве).
#   (B) Геральдический fallback — если мастера ещё нет, мотив рисуется
#       примитивами ImageMagick в той же палитре на прозрачной канве.
#       Заменяется автоматически, как только появится _src_<category>.png.
#
#  Формат вывода — 60×68 несжатый BGRA DDS (как ванильные generic_*.dds),
#  проверяется tools/glp_audit.py. Идемпотентно. Требуется ImageMagick 6/7.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

SRC="tools/_icons_src"
OUT="gfx/interface/ideas"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

CANVAS_W=60
CANVAS_H=68
FIT_W=52
FIT_H=58
KEY_FUZZ=8          # % — порог вырезания белого фона
ALPHA_THRESH=12     # % — бинаризация маски контента при поиске bbox

# Палитра (холодная сепия — как на загрузочных экранах/портретах)
INK="#241b13"       # тёмная сепия (линии/фигуры)
INK_RED="#7e1c1c"   # тёмно-красный акцент
BRONZE="#c8b48f"    # бронза/пергамент (светлый контур)

# ---------------------------------------------------------------- построение
build_one() {
	local cat="$1"
	local s="${SRC}/_src_${cat}.png"
	local o="${OUT}/idea_GLP_${cat}.dds"

	if [ -f "$s" ]; then
		# (A) ИИ-эмблема на белом фоне
		# 1. вырезаем белый фон -> прозрачность
		convert "$s" -fuzz ${KEY_FUZZ}% -transparent white "$TMP/keyed.png"
		# 2. bbox контента по бинаризованной альфа-маске (не боится слабого
		#    ореола/виньетки: порог отсекает полупрозрачную кайму)
		convert "$TMP/keyed.png" -alpha extract -threshold ${ALPHA_THRESH}% "$TMP/mask.png"
		bb=$(convert "$TMP/mask.png" -format "%@" info:)
		# 3. кропим по bbox и вписываем в FIT_W×FIT_H
		convert "$TMP/keyed.png" -crop "$bb" +repage -resize "${FIT_W}x${FIT_H}>" "$TMP/motif.png"
		# 4. бронзовая кромка: силуэт мотива, расширенный на ~1px
		convert "$TMP/motif.png" -alpha extract -morphology Dilate Disk:1.2 \
			"$TMP/rim_alpha.png"
		mw=$(identify -format '%w' "$TMP/motif.png")
		mh=$(identify -format '%h' "$TMP/motif.png")
		convert -size "${mw}x${mh}" xc:"$BRONZE" \
			"$TMP/rim_alpha.png" -compose CopyOpacity -composite "$TMP/rim.png"
		# 5. кромка под мотивом, всё вместе — по центру прозрачной канвы
		convert "$TMP/rim.png" "$TMP/motif.png" -compose over -composite "$TMP/withrim.png"
		convert -size ${CANVAS_W}x${CANVAS_H} xc:none \
			"$TMP/withrim.png" -gravity center -composite "$TMP/out.png"
	else
		# (B) геральдический fallback (временный — пока нет ИИ-мастера)
		draw_fallback "$cat"
	fi

	convert "$TMP/out.png" -define dds:compression=none "$o"
	local mn cov
	mn=$(convert "$o" -alpha extract -format "%[fx:minima*255]" info:)
	cov=$(convert "$o" -alpha extract -format "%[fx:mean*100]" info:)
	printf "  %-32s -> %s  (minAlpha=%s, coverage=%.1f%%)\n" \
		"$cat" "$o" "$mn" "$cov"
}

# Геральдический мотив на прозрачной канве (без диска). Аргумент — категория.
draw_fallback() {
	local cat="$1"
	convert -size ${CANVAS_W}x${CANVAS_H} xc:none "$TMP/out.png"
	case "$cat" in
	insurgent_army)  # революционный факел
		convert "$TMP/out.png" -fill "$INK" -stroke "$BRONZE" -strokewidth 2 \
			-draw "rectangle 27,32 33,50" \
			-draw "rectangle 23,29 37,33" \
			-fill "$INK_RED" -stroke "$BRONZE" \
			-draw "path 'M 30,9 Q 40,22 32,31 Q 30,33 28,31 Q 20,22 30,9'" \
			"$TMP/out.png" ;;
	black_guard_legacy)  # чёрное знамя на древке + скрещённые кости
		convert "$TMP/out.png" -fill none -stroke "$INK" -strokewidth 4 \
			-draw "line 21,53 27,14" \
			-fill "#17110c" -stroke "$BRONZE" -strokewidth 2 \
			-draw "polygon 27,14 46,19 46,32 27,27" \
			-fill none -stroke "$INK" -strokewidth 3 \
			-draw "line 20,52 40,36" -draw "line 20,36 40,52" \
			"$TMP/out.png" ;;
	kontrrazvedka_surveillance)  # всевидящее око
		convert "$TMP/out.png" -fill "$BRONZE" -stroke "$INK" -strokewidth 2 \
			-draw "path 'M 12,34 Q 30,18 48,34 Q 30,50 12,34'" \
			-fill "$INK" -stroke none -draw "circle 30,34 30,42" \
			-fill "#000000" -draw "circle 30,34 30,38" \
			-fill "#ffffff" -draw "circle 27,31 27,33" \
			"$TMP/out.png" ;;
	*)
		echo "!! нет отрисовки для категории '$cat'" >&2; return 1 ;;
	esac
}

echo "Сборка иконок духов GLP (прозрачный фон):"
for cat in military industry cavalry tachanka intelligence logistics health \
           agriculture navy society insurgent_army black_guard_legacy \
           free_syndicates_and_soviets hostile_encirclement kontrrazvedka_surveillance; do
	build_one "$cat"
done
echo "Готово."
