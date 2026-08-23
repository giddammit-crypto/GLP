#!/usr/bin/env bash
# =============================================================================
#  GLP portrait pipeline  --  HOI4 1.19.2 art spec compliance
#
#  Спецификация (ТЗ, раздел 2):
#     * большие портреты лидеров/генералов : 156 x 224, ARGB 8888, контраст +15%,
#       виньетирование
#     * малые портреты советников/министров: 156 x 210, DXT5, сепия/монохром
#       с глубокими тенями
#     * иконки советников в gfx/interface/ideas: 156 x 210, DXT5 (тот же кадр)
#
#  Источники — «мастера» фотореалистичных портретов:
#     gfx/leaders/GLP/_src_<person>_large.jpg
#
#  Скрипт идемпотентен: .dds всегда пересобираются из мастеров, а не из .dds,
#  поэтому повторные запуски не накапливают артефакты сжатия.
#  Требуется ImageMagick.
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
)

# Большой портрет: 156x224, ARGB8888, контраст +15%, лёгкая виньетка.
make_large() {
	convert "$1" -colorspace sRGB \
		-resize "156x224^" -gravity north -extent 156x224 \
		-sigmoidal-contrast 2.2x50% -modulate 100,88,100 \
		-fill '#0d0d0f' -colorize 6 \
		\( -size 156x224 radial-gradient:white-gray45 \) -compose multiply -composite \
		-unsharp 0x0.7+0.6+0.01 \
		-alpha set -define dds:compression=none -define dds:mipmaps=0 \
		"DDS:$2"
}

# Малый портрет/иконка советника: 156x210, DXT5, сепия с глубокими тенями.
make_small() {
	convert "$1" -colorspace sRGB \
		-resize "156x210^" -gravity north -extent 156x210 \
		-colorspace Gray -sigmoidal-contrast 3x48% \
		-fill '#6b563c' -tint 55 \
		\( -size 156x210 radial-gradient:white-gray50 \) -compose multiply -composite \
		-unsharp 0x0.6+0.55+0.01 \
		-alpha set -define dds:compression=dxt5 -define dds:mipmaps=0 \
		"DDS:$2"
}

for slug in "${!PEOPLE[@]}"; do
	name="${PEOPLE[$slug]}"
	src="$LEADERS/_src_${slug}_large.jpg"
	if [ ! -f "$src" ]; then
		echo "!! мастер отсутствует: $src" >&2
		continue
	fi
	make_large "$src" "$TMP/l.dds" && mv "$TMP/l.dds" "$LEADERS/Portrait_GLP_${name}_large.dds"
	make_small "$src" "$TMP/s.dds" && mv "$TMP/s.dds" "$LEADERS/Portrait_GLP_${name}.dds"
	cp "$LEADERS/Portrait_GLP_${name}.dds" "$IDEAS/idea_GLP_${name}.dds"
	echo "   $name: large 156x224 ARGB8888 + small 156x210 DXT5 + advisor icon"
done

echo "готово."
