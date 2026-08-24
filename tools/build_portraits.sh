#!/usr/bin/env bash
# =============================================================================
#  GLP portrait pipeline  --  HOI4 official dimensions
#
#  Спецификація (по оффиціальной документаціи Paradox):
#     * large (портретъ лидера/генерала) : 156 x 210, ARGB 8888
#     * medium (портретъ въ спискѣ генераловъ) : 88 x 119, DXT5
#     * small  (совѣтникъ/иконка идеи)  :  65 x  67, DXT5
#
#  Прежнія размѣры 156x224 (large) и 156x210 (small) были НЕВѢРНЫ:
#  large-кадръ тянуло по высотѣ въ окнѣ выбора генераловъ, а иконки
#  совѣтниковъ выглядѣли гигантскими и не вписывались въ ячейку 65x67.
#
#  Источники — «мастера» фотореалистичныхъ портретовъ:
#     gfx/leaders/GLP/_src_<person>_large.jpg
#
#  Идемпотентно: .dds всегда пересобираются изъ мастеровъ. Требуется ImageMagick.
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."

LEADERS="gfx/leaders/GLP"
IDEAS="gfx/interface/ideas"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# _src_<slug>_large.jpg  ->  Portrait_GLP_<Name>
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

# Большой портрет лидера/генерала: 156x210, ARGB8888 (безсжатый).
make_large() {
	colorgrade "$1" "$TMP/l.png" 156 210 north
	convert "$TMP/l.png" -alpha set \
		-define dds:compression=none -define dds:mipmaps=0 "DDS:$2"
}

# Средній портрет (списокъ генераловъ): 88x119, DXT5 — точная оффиціальная
# геометрія, чтобы кадры не тянуло по высотѣ.
make_medium() {
	colorgrade "$1" "$TMP/m.png" 88 119 north
	convert "$TMP/m.png" -alpha set \
		-define dds:compression=dxt5 -define dds:mipmaps=0 "DDS:$2"
}

# Малый портрет/иконка совѣтника: 65x67, DXT5 — квадратная ячейка идеи.
# Лицо центрируется и кропится подъ почти квадратный кадръ.
make_small() {
	colorgrade "$1" "$TMP/s.png" 65 67 center
	convert "$TMP/s.png" -alpha set \
		-define dds:compression=dxt5 -define dds:mipmaps=0 "DDS:$2"
}

for slug in "${!PEOPLE[@]}"; do
	name="${PEOPLE[$slug]}"
	src="$LEADERS/_src_${slug}_large.jpg"
	if [ ! -f "$src" ]; then
		echo "!! мастер отсутствует: $src" >&2
		continue
	fi
	make_large  "$src" "$TMP/l.dds" && mv "$TMP/l.dds" "$LEADERS/Portrait_GLP_${name}_large.dds"
	make_medium "$src" "$TMP/m.dds" && mv "$TMP/m.dds" "$LEADERS/Portrait_GLP_${name}.dds"
	make_small  "$src" "$TMP/s.dds" && mv "$TMP/s.dds" "$IDEAS/idea_GLP_${name}.dds"
	echo "   $name: large 156x210 ARGB8888 + medium 88x119 DXT5 + advisor 65x67 DXT5"
done

echo "готово."
