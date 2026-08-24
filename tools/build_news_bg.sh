#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — сборка оформленія окна новостей (EventWindow_News):
#     * GFX_GLP_event_news_bg   — собственный тёмный фонъ газеты 1056x595
#                                 (RGBA безъ сжатія, какъ ванильная газета).
#     * GFX_GLP_news_pic_frame  — рамка снимка 405x161 (DXT5): чёрный
#                                 металлическій бордюръ, золотая нить, тень.
#
#  Мастеръ фона: gfx/interface/_src_event_news_bg.png (генерированный,
#  собственный). Рамка собирается процедурно. Требуется ImageMagick.
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."

SRC="gfx/interface/_src_event_news_bg.png"
BG="gfx/interface/GLP_event_news_bg.dds"
FRAME="gfx/interface/GLP_news_pic_frame.dds"

convert "$SRC" -resize 1056x595! -alpha set \
	-define dds:compression=none -define dds:mipmaps=0 "DDS:$BG"
echo "   $BG (1056x595 RGBA)"

W=405; H=161
convert -size "${W}x${H}" xc:none \
	\( -size "${W}x${H}" xc:none -fill 'rgba(0,0,0,0.55)' \
	   -draw 'roundrectangle 5,7 401,157 8,8' -blur 0x3 \) \
	-compose over -composite \
	-fill none -stroke '#0b0a08' -strokewidth 4 -draw 'roundrectangle 2,2 402,158 7,7' \
	-fill none -stroke '#3a3127' -strokewidth 2 -draw 'roundrectangle 4,4 400,156 6,6' \
	-fill none -stroke 'rgba(158,120,52,0.9)' -strokewidth 1 -draw 'rectangle 7,7 397,153' \
	-alpha on -define dds:compression=dxt5 -define dds:mipmaps=0 "DDS:$FRAME"
echo "   $FRAME (405x161 DXT5)"

echo "готово."
