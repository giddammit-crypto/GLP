#!/usr/bin/env bash
# =============================================================================
#  GLP portrait pipeline  --  HOI4 official dimensions
#
#  Спецификація (по оффиціальной документаціи Paradox):
#     * large (портретъ лидера/генерала) : 156 x 210, ARGB 8888 (полный кадръ)
#     * medium (портретъ въ спискѣ генераловъ) : 88 x 119, DXT5 (полный кадръ)
#     * small  (совѣтникъ/иконка идеи)  :  65 x  67, DXT5 (полный непрозрачный портретъ)
#
#  Портреты людей во всѣхъ трёхъ размѣрахъ НЕ имѣютъ прозрачныхъ вырѣзокъ,
#  чтобы въ ячейкахъ военнаго и политическаго руководства не возникало
#  полупрозрачныхъ «плавающихъ головъ».
#
#  Источники — «мастера» фотореалистичныхъ портретовъ:
#     gfx/leaders/GLP/_src_<person>[_large].jpg
#
#  Идемпотентно: .dds всегда пересобираются изъ мастеровъ. Требуется ImageMagick.
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."

LEADERS="gfx/leaders/GLP"
IDEAS="gfx/interface/ideas"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# _src_<slug>[_large].jpg  ->  Portrait_GLP_<Name>
declare -A PEOPLE=(
	[nestor_makhno]=Nestor_Makhno
	[viktor_belash]=Viktor_Belash
	[semen_karetnik]=Semen_Karetnik
	[feodosiy_shchus]=Feodosiy_Shchus
	[lev_zadov]=Lev_Zadov
	[halyna_kuzmenko]=Halyna_Kuzmenko
	[vsevolod_volin]=Vsevolod_Volin
	[ataman_grigoriev]=Ataman_Grigoriev
	[nikolai_skoblin]=Nikolai_Skoblin
	[anton_turkul]=Anton_Turkul
	[grigory_semyonov]=Grigory_Semyonov
	[aleksey_dybets]=Aleksey_Dybets
	[bogdan_dybets]=Bogdan_Dybets
	[feodosiy_kozhin]=Feodosiy_Kozhin
	[trofim_vdovychenko]=Trofim_Vdovychenko
	[aleksey_marchenko]=Aleksey_Marchenko
	[platon_petrenko]=Platon_Petrenko
	[vasily_kurylenko]=Vasily_Kurylenko
	[petr_gavrilenko]=Petr_Gavrilenko
)

# Общая обработка: лёгкое освѣтленіе (ТЗ: «чуть осветли», контрастъ сохранёнъ),
# холодная сѣро-охристая гамма, умѣренная виньетка и зерно.
colorgrade() {  # $1 in, $2 out, $W, $H, $gravity
	local W="$3" H="$4" grav="$5"
	convert "$1" -colorspace sRGB \
		-resize "${W}x${H}^" -gravity "$grav" -extent "${W}x${H}" \
		-modulate 118,92,100 \
		-sigmoidal-contrast 1.5x50% \
		-fill '#2a2723' -colorize 2 \
		\( -size "${W}x${H}" radial-gradient:white-gray82 \) -compose multiply -composite \
		\( +clone -colorspace Gray -fill gray50 -colorize 100 -attenuate 0.22 +noise Gaussian \) \
			-compose overlay -composite \
		-unsharp 0x0.6+0.45+0.01 \
		"$2"
}

# Большой портрет лидера/генерала: 156x210, ARGB8888 (полный непрозрачный кадр).
make_large() {
	colorgrade "$1" "$TMP/l.png" 156 210 north
	convert "$TMP/l.png" -alpha set -channel A -evaluate set 100% +channel \
		-define dds:compression=none -define dds:mipmaps=0 "DDS:$2"
}

# Средній портрет (списокъ генераловъ): 88x119, DXT5.
make_medium() {
	colorgrade "$1" "$TMP/m.png" 88 119 north
	convert "$TMP/m.png" -alpha set -channel A -evaluate set 100% +channel \
		-define dds:compression=dxt5 -define dds:mipmaps=0 "DDS:$2"
}

# Малый портрет совѣтника: 65x67, DXT5 — квадратная ячейка совѣтника.
# Полный непрозрачный портретъ съ фономъ.
make_small() {
	colorgrade "$1" "$TMP/s.png" 65 67 north
	convert "$TMP/s.png" -alpha set -channel A -evaluate set 100% +channel \
		-define dds:compression=dxt5 -define dds:mipmaps=0 "DDS:$2"
}

for slug in "${!PEOPLE[@]}"; do
	name="${PEOPLE[$slug]}"
	src1="$LEADERS/_src_${slug}_large.jpg"
	src2="$LEADERS/_src_${slug}.jpg"
	if [ -f "$src1" ]; then
		src="$src1"
	elif [ -f "$src2" ]; then
		src="$src2"
	else
		echo "!! мастер отсутствует: $slug" >&2
		continue
	fi
	make_large  "$src" "$TMP/l.dds" && mv "$TMP/l.dds" "$LEADERS/Portrait_GLP_${name}_large.dds"
	make_medium "$src" "$TMP/m.dds" && mv "$TMP/m.dds" "$LEADERS/Portrait_GLP_${name}.dds"
	make_small  "$src" "$TMP/s.dds" && mv "$TMP/s.dds" "$IDEAS/idea_GLP_${name}.dds"
	echo "   $name: large 156x210 ARGB8888 + medium 88x119 DXT5 + advisor 65x67 DXT5 (solid)"
done

echo "готово."
