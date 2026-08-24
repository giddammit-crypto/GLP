#!/usr/bin/env bash
# =============================================================================
<<<<<<< HEAD
#  ГУЛЯЙ-ПОЛЕ — сборка картинокъ событій (event pictures)
#
#  Форматъ картинокъ событій HOI4 — 768x432 (16:9), .dds DXT1, безъ мип-мапъ.
#
#  Вступительная новость (glp_news.100) больше НЕ имитируетъ газетную полосу:
#  игра и такъ показываетъ новость въ газетной рамкѣ, поэтому запечённый
#  «двойной» фонъ выгляделъ ужасно. Теперь это чистый портретъ Батьки Махно
#  (изъ мастеръ-файла лидерскаго портрета), обработанный въ единомъ стилѣ.
#
#  Требуется ImageMagick.
=======
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
>>>>>>> origin/main
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."

EP="gfx/event_pictures"
<<<<<<< HEAD
LEADERS="gfx/leaders/GLP"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Общая кинематографичная обработка для сюжетныхъ картинокъ: чуть свѣтлѣе,
# чѣмъ раньше, холодная сѣро-охристая гамма, контрастность, зерно.
grade() {  # $1 in(jpg/png), $2 out(png)
	convert "$1" -colorspace sRGB \
		-resize "768x432^" -gravity center -extent 768x432 \
		-modulate 120,82,100 \
		-sigmoidal-contrast 1.5x50% \
		-fill '#252220' -colorize 3 \
		\( -size 768x432 radial-gradient:white-gray80 \) -compose multiply -composite \
		\( +clone -colorspace Gray -fill gray50 -colorize 100 -attenuate 0.28 +noise Gaussian \) \
			-compose overlay -composite \
		-unsharp 0x0.7+0.45+0.01 \
		"$2"
}

to_dds() {  # $1 png, $2 dds
	convert "$1" -alpha off -define dds:compression=dxt1 -define dds:mipmaps=0 "DDS:$2"
}

echo ">> вступительная новость — чистый портрет Батьки Махно"
src="$LEADERS/_src_nestor_makhno_large.jpg"
if [ ! -f "$src" ]; then
	echo "!! нет мастера $src" >&2
	exit 1
fi
# Портрет-лидер квадратный/вертикальный; подъ 16:9 центрируемъ лицо и
# добираемъ размытое продолженіе по бокамъ, чтобы не было искаженія.
convert "$src" -colorspace sRGB -resize 768x432^ -gravity center -extent 768x432 \
	-modulate 118,90,100 -sigmoidal-contrast 1.6x50% "$TMP/intro_hero.png"
convert "$src" -colorspace sRGB -resize 768x432^ -gravity center -extent 768x432 \
	-blur 0x30 -modulate 80,100,100 "$TMP/intro_bg.png"
convert -size 768x432 xc:black \
	\( -size 560x432 xc:white \) -gravity center -composite \
	-blur 0x30 -level 0x40% "$TMP/intro_mask.png"
convert "$TMP/intro_bg.png" "$TMP/intro_hero.png" "$TMP/intro_mask.png" \
	-gravity center -compose over -composite "$TMP/intro.png"
to_dds "$TMP/intro.png" "$EP/news_event_glp_intro.dds"
echo "   $EP/news_event_glp_intro.dds (768x432 DXT1)"

# Прочія сюжетныя картинки новостейъ (если есть png-мастера) — пересобираемъ
# въ единомъ стилѣ, чуть свѣтлѣе.
shopt -s nullglob
for src in "$EP"/news_event_glp_*.png; do
	case "$(basename "$src")" in
		news_event_glp_intro.png) continue ;;
	esac
	out="$EP/$(basename "${src%.png}").dds"
	grade "$src" "$TMP/n.png"
	to_dds "$TMP/n.png" "$out"
	echo "   $out"
done
shopt -u nullglob
=======
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
>>>>>>> origin/main

echo "готово."
