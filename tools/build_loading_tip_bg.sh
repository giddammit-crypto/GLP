#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/gfx/interface/loading_tip_journal_bg.dds"

command -v convert >/dev/null 2>&1 || {
    echo "ImageMagick 'convert' is required" >&2
    exit 1
}

mkdir -p "$(dirname "$OUT")"

# Dark editorial caption card: enough contrast for the white typewriter font,
# transparent outside the rounded border so loading art remains visible.
convert -size 1024x180 xc:none \
    -fill 'rgba(12,10,8,0.78)' \
    -stroke 'rgba(230,218,190,0.62)' \
    -strokewidth 2 \
    -draw 'roundrectangle 2,2 1021,177 12,12' \
    -stroke 'rgba(230,218,190,0.36)' \
    -strokewidth 1 \
    -draw 'line 24,16 1000,16 line 24,164 1000,164' \
    -define dds:compression=dxt5 \
    "$OUT"

echo "Built ${OUT#$ROOT/} (1024x180 DXT5)"
