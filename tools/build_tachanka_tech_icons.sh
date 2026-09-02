#!/usr/bin/env bash
# =============================================================================
#  ГУЛЯЙ-ПОЛЕ — сборка технологических иконок тачанок (180x80 DDS)
#
#  Задача:
#   * убрать подложку/тени под техникой;
#   * держать мастер-арт на прозрачном фоне;
#   * собирать одинаково читаемые 180x80 иконки для ветки исследований HOI4.
#
#  Источники:
#     tools/_icons_src/_src_tachanka_tech_1.png
#     tools/_icons_src/_src_tachanka_tech_2.png
#     tools/_icons_src/_src_tachanka_tech_3.png
#     tools/_icons_src/_src_tachanka_tech_4.png
#
#  Вывод:
#     gfx/interface/technologies/GLP_tachanka_tech_<n>.dds
#
#  Требования движка:
#   * transparent background;
#   * единая канва 180x80, как у существующих tech-иконок мода;
#   * DDS с альфой (DXT5) для мягких краёв без белых ореолов.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

SRC="tools/_icons_src"
OUT="gfx/interface/technologies"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

CANVAS_W=180
CANVAS_H=80
FIT_W=168
FIT_H=68

build_one() {
	local idx="$1"
	local src="${SRC}/_src_tachanka_tech_${idx}.png"
	local out="${OUT}/GLP_tachanka_tech_${idx}.dds"

	[ -f "$src" ] || {
		echo "Нет исходника: $src" >&2
		exit 1
	}

	convert "$src" \
		-alpha on \
		-trim +repage \
		-resize "${FIT_W}x${FIT_H}>" \
		-unsharp 0x0.6+0.8+0.02 \
		-background none -gravity center -extent ${CANVAS_W}x${CANVAS_H} \
		-define dds:compression=dxt5 \
		"$out"

	printf '  %-24s -> ' "$(basename "$out")"
	identify -format '%wx%h %m\n' "$out"
}

echo "Сборка tech-иконок тачанок:"
mkdir -p "$OUT"
for idx in 1 2 3 4; do
	build_one "$idx"
done
echo "Готово."
