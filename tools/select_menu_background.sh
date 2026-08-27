#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — выбор фонового изображения главного меню (HOI4 1.19.2)
#
#  Использование:
#       tools/select_menu_background.sh 1|2|3|4|5|6|7|8|9
#
#  Варианты (4:3, 1920x1440, DXT1):
#     1 — Степь, конная колонна махновцев и чёрные знамёна на закате
#     2 — Рваный чёрный флаг с «весёлым Роджером» над деревней
#     3 — Тачанка с пулемётом «Максим» на полном скаку
#     4 — Ночной совет командиров в освещённой керосинкой избе
#   Новая серия (2026-08, превью — tools/MENU_BACKGROUND_NEW_OPTIONS.png):
#     5 — Бронепоезд на рассвете
#     6 — Тачанка в степной пыли
#     7 — Сход в волости
#     8 — Зимний поход
#     9 — Ночной рейд
#
#  Скрипт копирует выбранный DDS в gfx/interface/frontendmainviewbg.dds,
#  на который ссылается спрайт GFX_frontend_bg
#  (interface/frontendmainviewbg.gfx). Бэкап текущего фона сохраняется рядом.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ $# -ne 1 || ! $1 =~ ^[1-9]$ ]]; then
    echo "Usage: $0 1|2|3|4|5|6|7|8|9" >&2
    exit 1
fi

OPT=$1
SRC="gfx/interface/menu_options/frontendmenu_bg_option_${OPT}.dds"
DST="gfx/interface/frontendmainviewbg.dds"

if [[ ! -f "$SRC" ]]; then
    echo "Missing $SRC — generate menu backgrounds first." >&2
    exit 1
fi

if [[ -f "$DST" && ! -f "${DST%.dds}.previous.dds" ]]; then
    cp "$DST" "${DST%.dds}.previous.dds"
fi
cp "$SRC" "$DST"
echo "Установлен фон главного меню — вариант $OPT."
echo "Источник JPG: tools/_gfx_src/menu_bg_option_${OPT}_*.jpg"
