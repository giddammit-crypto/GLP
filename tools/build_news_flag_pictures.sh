#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — пересборка новостныхъ картинокъ, на которыхъ виденъ флагъ
#  Вольной Территоріи: полотнище чёрное со знакомъ анархіи Ⓐ.
#
#  Мастера (gfx/event_pictures/_src_news_*.jpg) уже содержатъ Ⓐ; этотъ скриптъ
#  лишь пересобираетъ игровые .dds — ванильный форматъ врѣзки новостей
#  397x153, DXT5, безъ мип-мапъ (какъ news_event_001.dds).
#
#  Полоса вырѣзается не по центру, а вокругъ флага: точка кадрированія для
#  каждой картинки задана въ tools/news_flag_crops.tsv.
#
#  Требуется ImageMagick.
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."

EP="gfx/event_pictures"
TSV="tools/news_flag_crops.tsv"

while IFS=$'\t' read -r key frac; do
	case "$key" in ''|\#*) continue ;; esac

	src="$EP/_src_news_${key}.jpg"
	case "$key" in
		rebirth) out="$EP/news_event_GLP_rebirth.dds" ;;
		*)       out="$EP/news_event_glp_${key}.dds" ;;
	esac

	if [ ! -f "$src" ]; then
		echo "!! нет мастера $src" >&2
		exit 1
	fi

	w=$(identify -format "%w" "$src")
	h=$(identify -format "%h" "$src")
	sh=$(python3 -c "print(max(153, round($h * 397 / $w)))")
	off=$(python3 -c "print(max(0, min($sh - 153, round($sh * $frac - 76))))")

	convert "$src" -colorspace sRGB -resize 397x \
		-crop "397x153+0+$off" +repage \
		-alpha set -channel A -evaluate set 100% +channel \
		-define dds:compression=dxt5 -define dds:mipmaps=0 "DDS:$out"
	echo "   $out (397x153 DXT5, y=$off)"
done < "$TSV"

echo "готово."
