#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — сборка картинок событий (event pictures)
#
#  Формат картинок новостного окна HOI4: 397x153 (ваниль news_event_*.dds),
#  DDS без сжатия (ARGB8888), без мип-мап. Файл большего размера окно новости
#  растягивает/сжимает — поэтому строго 397x153, «идеально в лист новости».
#
#  Стилистика: чёрно-белая газетная фотография 1930-х — ровный полутон,
#  поднятый контраст, зерно, лёгкая виньетка, чуть тёплая бумажная тонировка.
#
#  Мастера: gfx/event_pictures/_src_news_<slug>.jpg
#  Пары «событие → картинка» фиксируются в tools/event_pictures.tsv
#  (сверяет tools/glp_audit.py). Требуется ImageMagick.
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."

EP="gfx/event_pictures"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# _src_news_<slug>.jpg -> news_event_glp_<slug>.dds
SLUGS=(
	intro rebirth tachanka sevastopol_fleet makhno_inspection air_squadron
	autumn_fair alliance_treaty volunteers_arrival triumph war_council
	armored_train dnieper_electric cavalry_raid anarchist_congress
	black_guard_march donbass_syndicates counter_intel peasant_communes
	radio_tower madrid_international
)

# Ч/б газетная градация: полутон, контраст, зерно, виньетка, бумажный тон.
grade() {  # $1 in(jpg/png), $2 out(png)
	convert "$1" -colorspace sRGB \
		-resize "397x153^" -gravity center -extent 397x153 \
		-colorspace Gray \
		-modulate 104,100,100 \
		-sigmoidal-contrast 2.2x52% \
		-fill '#26221d' -colorize 4 \
		\( -size 397x153 radial-gradient:white-gray88 \) -compose multiply -composite \
		\( +clone -fill gray50 -colorize 100 -attenuate 0.30 +noise Gaussian \) \
			-compose overlay -composite \
		-unsharp 0x0.6+0.5+0.01 \
		"$2"
}

to_dds() {  # $1 png, $2 dds  -> ARGB8888, без мипов
	convert "$1" -alpha off \
		-define dds:compression=none -define dds:mipmaps=0 "DDS:$2"
}

for slug in "${SLUGS[@]}"; do
	src="$EP/_src_news_${slug}.jpg"
	dds="$EP/news_event_glp_${slug}.dds"
	[ "$slug" = rebirth ] && dds="$EP/news_event_GLP_rebirth.dds"   # историческое имя файла
	if [ ! -f "$src" ]; then
		echo "-- $slug: мастер отсутствует, пропуск (dds не трогаем)" >&2
		continue
	fi
	grade "$src" "$TMP/${slug}.png"
	to_dds "$TMP/${slug}.png" "$dds"
	echo "   $slug -> $dds"
done

echo "готово."
