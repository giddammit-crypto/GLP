#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — сборка ИКОНОК ШАБЛОНОВ ДИВИЗИЙ (template_counter)
#
#  Механика HOI4 (hoi4.paradoxwikis.com/Division_modding + /Effect):
#    division_template { template_counter = N } берёт спрайты
#    GFX_div_templ_N_large (76x42 — дизайнер дивизий) и
#    GFX_div_templ_N_small (30x12 — фишки на карте).
#    Без template_counter движок выводит иконку под-юнита с НАИБОЛЬШИМ
#    priority в составе: light_armor = 2501, medium_armor = 2502,
#    mechanized = 610, infantry = 600, cavalry = 599, motorized = 599.
#    Отсюда и баг «у конницы иконка танка»: тачаночный курень содержит
#    один батальон light_armor, и он перекрывает коневодческую иконку.
#    Единственный штатный способ это исправить, не ломая состав дивизии, —
#    приказать движку рисовать нужную иконку через template_counter. Саму
#    иконку кавалерии (92) берём из базовой игры, см. конец этого файла;
#    здесь собираются только знамёна добровольцев (90/91) — там своего
#    силуэта в ванили просто нет.
#
#  Стиль — ванильный: плоский силуэт цвета #517151 с мягкой световой
#  растяжкой сверху и тёмной обводкой (на светлом и тёмном фоне UI).
#  Формат — несжатый BGRA/ARGB8888 DDS (тот же, что у 90/91).
#
#  Мастер-файлы: tools/_icons_src/_src_div_<name>.png (ИИ-эмблема на белом
#  фоне) и _src_div_<name>_small.png — упрощённый силуэт для 30x12.
#  Идемпотентно. Требуется ImageMagick 6/7. Сверяет tools/glp_audit.py
#  (проверка 16 — «иконка дивизии соответствует её названию»).
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

SRC="tools/_icons_src"
OUT_L="gfx/interface/counters/division_templates_large"
OUT_S="gfx/interface/counters/division_templates_small"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

INK="#517151"          # цвет ванильного силуэта дивизии
SHADE="#151d15"        # тёмная обводка/тень (читается на светлом фоне)
KEY_FUZZ=30            # % — порог вырезания белого фона мастера
ALPHA_THRESH=25        # % — бинаризация маски силуэта

# ---------------------------------------------------------------- построение
# $1 = мастер (png)  $2 = ширина  $3 = высота  $4 = радиус обводки
# $5 = световая растяжка (yes/no)  $6 = выход
# Обводка и растяжка включаются только для больших плиток: на 30x12 они
# превращают силуэт в непроваримое пятно.
build_one() {
	local s="$1" w="$2" h="$3" dil="$4" gloss="$5" o="$6"

	[ -f "$s" ] || { echo "нет мастера: $s" >&2; exit 1; }
	mkdir -p "$(dirname "$o")"

	# 1. белый фон -> прозрачность; 2. маска силуэта; 3. bbox + вписывание
	convert "$s" -alpha off -fuzz ${KEY_FUZZ}% -transparent white "$TMP/keyed.png"
	convert "$TMP/keyed.png" -alpha extract -threshold ${ALPHA_THRESH}% "$TMP/mask.png"
	bb=$(convert "$TMP/mask.png" -format "%@" info:)
	# внутри канвы оставляем безопасный зазор 1px: иконка не должна
	# обрезаться по краям плитки 76x42 / 30x12
	convert "$TMP/keyed.png" -crop "$bb" +repage \
		-resize "$((w - 2))x$((h - 2))>" +repage "$TMP/motif.png"
	mw=$(identify -format '%w' "$TMP/motif.png")
	mh=$(identify -format '%h' "$TMP/motif.png")
	x=$(( (w - mw) / 2 )); y=$(( (h - mh) / 2 ))

	# 4. силуэт = маска мотива, залитая «чернильным» цветом
	convert "$TMP/motif.png" -alpha extract "$TMP/motif_a.png"
	convert -size "${mw}x${mh}" xc:"$INK" "$TMP/motif_a.png" \
		-compose CopyOpacity -composite "$TMP/sil_motif.png"
	convert -size "${w}x${h}" xc:none "$TMP/sil_motif.png" \
		-geometry "+${x}+${y}" -compose over -composite "$TMP/sil.png"

	# 5. тёмная обводка: расширенный на $dil px силуэт под мотивом
	if [ "$dil" != "0" ]; then
		convert "$TMP/sil.png" -alpha extract -morphology Dilate "Disk:${dil}" \
			"$TMP/rim.png"
		convert -size "${w}x${h}" xc:"$SHADE" "$TMP/rim.png" \
			-compose CopyOpacity -composite "$TMP/rim_colored.png"
		convert "$TMP/rim_colored.png" "$TMP/sil.png" \
			-compose over -composite "$TMP/body.png"
	else
		cp "$TMP/sil.png" "$TMP/body.png"
	fi

	# 6. мягкая световая растяжка сверху, ограниченная формой силуэта
	if [ "$gloss" = "yes" ]; then
		convert -size "${w}x${h}" gradient:'rgba(255,255,255,90)'-'rgba(255,255,255,0)' \
			"$TMP/grad.png"
		convert "$TMP/grad.png" "$TMP/sil.png" -compose DstIn -composite "$TMP/hi.png"
		convert "$TMP/body.png" "$TMP/hi.png" -compose over -composite "$TMP/out.png"
	else
		cp "$TMP/body.png" "$TMP/out.png"
	fi

	# 7. несжатый ARGB8888 DDS ровно канвы плитки
	convert "$TMP/out.png" -define dds:compression=none -define dds:layout=standard "$o"

	local wh mn cov
	wh=$(identify -format '%wx%h' "$o")
	[ "$wh" = "${w}x${h}" ] || { echo "$o: получилось $wh, нужно ${w}x${h}" >&2; exit 1; }
	mn=$(convert "$o" -alpha extract -format '%[fx:minima*255]' info:)
	cov=$(convert "$o" -alpha extract -format '%[fx:mean*100]' info:)
	echo "$(basename "$o"): ${w}x${h}, min alpha=${mn}, покрытие=${cov}%"
}

# -- конница (counter 92) ------------------------------------------------------
# Здесь 92 намеренно НЕ собирается: у конных шаблонов должен быть силуэт
# кавалерии из базовой игры, а не наш собственный, поэтому interface/
# GLP_division_templates.gfx указывает GFX_div_templ_92_{large,small} прямо на
# gfx/interface/counters/divisions_large/unit_cavalry_icon.dds и
# gfx/interface/counters/divisions_small/onmap_unit_cavalry_icon.dds.
# Свою плитку под 92 (GLP_tachanka.dds) мы удалили: дублировать ванильный
# ресурс -- единственный источник правды для этой иконки.
