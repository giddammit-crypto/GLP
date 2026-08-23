#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — сборка картинокъ событій (event pictures)
#
#  Вступительный экранъ новой партіи: газетная полоса 1930-хъ,
#  портретъ Батьки Махно въ лѣвомъ верхнемъ углу, черное знамя — въ правомъ
#  нижнемъ. Заголовокъ набирается «царской» антиквой прямо въ пустую
#  заголовочную плашку макета.
#
#  Форматъ картинокъ событій: 768x432, .dds DXT1, безъ мип-мапъ.
#  Требуется ImageMagick.
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."

EP="gfx/event_pictures"
F="tools/fonts"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

FONT_TITLE="$F/SourceSerifPro-Black.ttf"
FONT_SUB="$F/SourceSerifPro-Bold.ttf"
FONT_TEXT="$F/SourceSerifPro-Regular.ttf"

echo ">> вступительная газета"
src="$EP/_src_news_intro.jpg"
if [ -f "$src" ]; then
	convert "$src" -colorspace sRGB -resize 1672x941! \
		-font "$FONT_TEXT" -pointsize 24 -kerning 5 -fill '#3a3229' \
		-annotate +545+112 "ВОЛЬНЫЙ ГОЛОСЪ ГУЛЯЙ-ПОЛЯ · 1 января 1936 г." \
		-font "$FONT_TITLE" -pointsize 45 -kerning 2 -fill '#241f19' \
		-annotate +545+185 "ГРЯДЕТЪ ГРОЗА НАДЪ ВОЛЬНОЙ СТЕПЬЮ" \
		-font "$FONT_SUB" -pointsize 27 -kerning 1 -fill '#453b30' \
		-annotate +545+228 "Вольная территорія стоитъ, а міръ снова точитъ штыкъ" \
		-resize 768x432! \
		-modulate 102,70,100 -sigmoidal-contrast 1.6x50% \
		-alpha off -define dds:compression=dxt1 -define dds:mipmaps=0 \
		"DDS:$EP/news_event_glp_intro.dds"
	echo "   $EP/news_event_glp_intro.dds (768x432 DXT1)"
else
	echo "!! нѣтъ мастера $src" >&2
	exit 1
fi

echo "готово."
