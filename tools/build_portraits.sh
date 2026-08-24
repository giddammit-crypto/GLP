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
#  Мастера новаго поколенія (GREY_BG_MASTERS) сняты наъ ровномъ
#  свѣтло-сѣромъ фонѣ: примѣняется градація съ приподнятой радіальной
#  виньеткой (центръ къ лицу, края въ тень), имитирующая тёмную студійную
#  подложку HOI4. Тупая вырезка по серому фону «съѣдаетъ» мехъ папахъ и
#  волосы, поэтому отъ нея отказались.
#
#  ВАЖНО: въ этомъ проходѣ иконки совѣтниковъ (idea_GLP_*.dds, 65x67,
#  съ вырезнымъ фономъ) НЕ пересобираются — сохраняются существующие
#  файлы съ прозрачностью (аудитъ ихъ требуетъ). Новые иконки будутъ
#  собраны послѣ перегенераціи всѣхъ мастеровъ наъ хромакей-фонѣ.
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
	[bogdan_dybets]=Bogdan_Dybets
	[aleksey_dybets]=Aleksey_Dybets
	[feodosiy_kozhin]=Feodosiy_Kozhin
	[lavr_kornilov]=Lavr_Kornilov
	[mikhail_drozdovsky]=Mikhail_Drozdovsky
)

# Мастера новаго поколенія (сняты наъ ровномъ свѣтло-сѣромъ фонѣ).
# Перегенерированные лица добавляются сюда; мастера не изъ списка
# обрабатываются по-старому (тёмный фотофонъ).
GREY_BG_MASTERS=(
	nestor_makhno viktor_belash semen_karetnik feodosiy_shchus lev_zadov
	halyna_kuzmenko vsevolod_volin ataman_grigoriev
	nikolai_skoblin anton_turkul grigory_semyonov
	bogdan_dybets aleksey_dybets feodosiy_kozhin
	lavr_kornilov mikhail_drozdovsky
)

# 1 -- мастер на сером фоне (новое поколение), 0 -- старый студийный.
is_grey_bg() {  # $1 = image path (_src_<slug>_large.jpg)
	local base slug
	base="$(basename "$1")"; slug="${base#_src_}"; slug="${slug%_large.jpg}"
	printf '%s\n' "${GREY_BG_MASTERS[@]}" | grep -qx "$slug"
}

# --- helpers ------------------------------------------------------------------

# Общая обработка (старые мастера): лёгкое освѣтленіе, холодная
# сѣро-охристая гамма, умѣренная виньетка и зерно.
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

# Градація новаго мастера (свѣтло-сѣрый фонъ): центръ виньетки приподнятъ
# къ лицу, края уходятъ въ тень — имитація тёмной студійной подложки HOI4.
colorgrade_vignette() {  # $1 in, $2 out, $W, $H, $gravity
	local W="$3" H="$4" grav="$5"
	convert "$1" -colorspace sRGB \
		-resize "${W}x${H}^" -gravity "$grav" -extent "${W}x${H}" \
		-modulate 100,90,100 \
		\( -size "${W}x$((H*2))" radial-gradient:white-gray74 \
		   -gravity center -crop "${W}x${H}+0+$((H*75/210))" \) \
		-compose multiply -composite \
		-sigmoidal-contrast 1.8x45% \
		-fill '#2a2723' -colorize 4 \
		\( +clone -colorspace Gray -fill gray50 -colorize 100 -attenuate 0.22 +noise Gaussian \) \
			-compose overlay -composite \
		-unsharp 0x0.6+0.45+0.01 \
		"$2"
}

# Большой портрет лидера/генерала: 156x210, ARGB8888 (безсжатый).
make_large() {  # $1 in, $2 out.dds, $3 grey?0/1
	if [ "$3" = 1 ]; then
		colorgrade_vignette "$1" "$TMP/l.png" 156 210 north
	else
		colorgrade "$1" "$TMP/l.png" 156 210 north
	fi
	convert "$TMP/l.png" -alpha set \
		-define dds:compression=none -define dds:mipmaps=0 "DDS:$2"
}

# Средній портрет (списокъ генераловъ): 88x119, DXT5 — точная оффиціальная
# геометрія, чтобы кадры не тянуло по высотѣ.
make_medium() {  # $1 in, $2 out.dds, $3 grey?0/1
	if [ "$3" = 1 ]; then
		colorgrade_vignette "$1" "$TMP/m.png" 88 119 north
	else
		colorgrade "$1" "$TMP/m.png" 88 119 north
	fi
	convert "$TMP/m.png" -alpha set \
		-define dds:compression=dxt5 -define dds:mipmaps=0 "DDS:$2"
}

for slug in "${!PEOPLE[@]}"; do
	name="${PEOPLE[$slug]}"
	src="$LEADERS/_src_${slug}_large.jpg"
	if [ ! -f "$src" ]; then
		echo "!! мастер отсутствует: $src" >&2
		continue
	fi
	grey=0; is_grey_bg "$src" && grey=1
	make_large  "$src" "$TMP/l.dds" "$grey" && mv "$TMP/l.dds" "$LEADERS/Portrait_GLP_${name}_large.dds"
	make_medium "$src" "$TMP/m.dds" "$grey" && mv "$TMP/m.dds" "$LEADERS/Portrait_GLP_${name}.dds"
	# idea_GLP_${name}.dds (65x67) намеренно не трогаем: пересборка съ
	# чистой вырезкой будет послѣ перегенераціи мастеровъ на хромакѣ.
	if [ "$grey" = 1 ]; then
		echo "   $name: 156x210 + 88x119 (новый мастер, виньетка)"
	else
		echo "   $name: 156x210 + 88x119 (старый мастер)"
	fi
done

echo "готово."
