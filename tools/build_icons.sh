#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — сборка иконок национальных духов (60×68, несжатый RGBA)
#
#  Проблема, которую решает скрипт: первая итерация кастомного GLP-пака
#  выдавала линейный арт поверх прозрачного фона со средним покрытием альфы
#  ~25–40 % — на тёмном фоне HOI4 такие иконки читались как «пустые»,
#  «не отображаются». Решение — каждый тематический мотив врезается в
#  заполненную сепиевую «печать-кружок» (parchment seal): заполненный диск
#  даёт ~55–60 % покрытия альфы (иконка явно видна), углы остаются
#  прозрачными (требование аудита: min alpha < 32), мотив остаётся узнаваемым.
#
#  Два источника мотива:
#   (A) ИИ-мастер  tools/_icons_src/_src_<category>.png  — живописный мотив
#       (вырезается белый фон, затемняется, врезается в печать).
#   (B) Геральдический fallback — для категорий без ИИ-мастера мотив
#       рисуется чистыми геометрическими примитивами ImageMagick в той же
#       палитре (тёмная сепия/чёрный/тёмно-красный на пергаменте). На размере
#       60×68 простые знаки (крест, глаз, якорь, факел, чёрное знамя) читаются
#       даже отчётливее живописных, и выдержаны в едином стиле «печати».
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

# Палитра печати (холодная сепия — как на загрузочных экранах/портретах)
RIM_DARK="#2a2018"
RIM_MID="#c8b48f"
RIM_INNER="#b9a37c"
INK="#241b13"      # тёмная сепия (линии/фигуры)
INK_RED="#7e1c1c"  # тёмно-красный акцент

make_disc() {  # -> $TMP/disc.png  (60×68, углы прозрачные)
	convert -size 60x68 xc:none \
		-fill "$RIM_DARK"  -draw "circle 30,34 30,61" \
		-fill "$RIM_MID"   -draw "circle 30,34 30,59" \
		-fill "$RIM_INNER" -draw "circle 30,34 30,57" \
		"$TMP/disc.png"
}

# Нарисовать геральдический мотив прямо на печать (поверх disc.png).
# Аргумент — категория. Координаты — относительно центра печати (30,34).
draw_motif() {
	local cat="$1"
	case "$cat" in
	health)  # красный медицинский крест
		convert "$TMP/disc.png" -fill "$INK_RED" \
			-draw "rectangle 25,17 35,51" \
			-draw "rectangle 11,27 49,41" \
			"$TMP/out.png" ;;
	navy)  # якорь
		convert "$TMP/disc.png" -fill none -stroke "$INK" -strokewidth 4 \
			-draw "circle 30,15 30,21" \
			-draw "line 30,21 30,47" \
			-draw "line 21,24 39,24" \
			-draw "path 'M 17,40 Q 30,55 43,40'" \
			"$TMP/out.png" ;;
	insurgent_army)  # революционный факел
		convert "$TMP/disc.png" -fill "$INK" \
			-draw "rectangle 27,30 33,51" \
			-draw "rectangle 23,27 37,31" \
			-fill "$INK_RED" \
			-draw "path 'M 30,7 Q 40,20 32,30 Q 30,32 28,30 Q 20,20 30,7'" \
			"$TMP/out.png" ;;
	black_guard_legacy)  # чёрное знамя на древке + скрещённые кости
		convert "$TMP/disc.png" -fill none -stroke "$INK" -strokewidth 3 \
			-draw "line 21,53 27,12" \
			-fill "#17110c" -stroke none \
			-draw "polygon 27,12 46,17 46,30 27,25" \
			-fill none -stroke "$INK" -strokewidth 4 \
			-draw "line 22,52 39,37" \
			-draw "line 22,37 39,52" \
			-fill "$INK" -stroke none \
			-draw "circle 22,52 22,55" -draw "circle 39,37 39,40" \
			-draw "circle 22,37 22,40" -draw "circle 39,52 39,55" \
			"$TMP/out.png" ;;
	kontrrazvedka_surveillance)  # всевидящее око
		convert "$TMP/disc.png" -fill "#e7dabf" -stroke "$INK" -strokewidth 2 \
			-draw "path 'M 11,34 Q 30,17 49,34 Q 30,51 11,34'" \
			-fill "$INK" -stroke none \
			-draw "circle 30,34 30,42" \
			-fill "#000000" \
			-draw "circle 30,34 30,38" \
			-fill "#ffffff" \
			-draw "circle 27,31 27,33" \
			"$TMP/out.png" ;;
	*)
		echo "!! нет отрисовки для категории '$cat'" >&2; return 1 ;;
	esac
}

build_one() {
	local cat="$1"
	local s="${SRC}/_src_${cat}.png"
	local o="${OUT}/idea_GLP_${cat}.dds"
	make_disc

	if [ -f "$s" ]; then
		# (A) живописный ИИ-мотив
		convert "$s" -fuzz 15% -transparent white \
			-modulate 72,118,100 \
			-trim +repage -resize 46x46 \
			"$TMP/em.png"
		convert "$TMP/disc.png" "$TMP/em.png" \
			-gravity center -geometry +0+1 -composite "$TMP/out.png"
	else
		# (B) геральдический fallback
		draw_motif "$cat"
	fi

	convert "$TMP/out.png" -define dds:compression=none "$o"
	local mn
	mn=$(convert "$o" -alpha extract -format "%[fx:minima*255]" info:)
	printf "  %-32s -> %s  (min alpha %s)\n" "$cat" "$o" "$mn"
}

echo "Сборка иконок духов GLP:"
for cat in military industry cavalry tachanka intelligence logistics health \
           agriculture navy society insurgent_army black_guard_legacy \
           free_syndicates_and_soviets hostile_encirclement kontrrazvedka_surveillance; do
	build_one "$cat"
done
echo "Готово."
