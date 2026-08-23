#!/usr/bin/env bash
# =============================================================================
#  GLP portrait pipeline  --  HOI4 1.19.2 art spec compliance
#
#  Spec (dev brief, section 2B):
#     * large character portraits : 156 x 224, DXT5 (or ARGB8888)
#     * small / advisor icons     : 156 x 210, DXT5 (or ARGB8888)
#
#  Sources:
#     gfx/leaders/GLP/_src_*.png|.jpg       -- painterly masters (if present)
#     gfx/leaders/GLP/Portrait_*_large.dds  -- existing painterly portraits
#     gfx/leaders/GLP/Portrait_*.dds        -- archival small portraits
#     gfx/interface/ideas/idea_GLP_*.dds    -- advisor / minister icons
#
#  Re-running is idempotent.  Requires ImageMagick (convert).
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."

LEADERS="gfx/leaders/GLP"
IDEAS="gfx/interface/ideas"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

large() {  # $1 = source image, $2 = destination dds
	convert "$1" -colorspace sRGB \
		-resize "156x224^" -gravity north -extent 156x224 \
		-unsharp 0x0.75+0.55+0.008 \
		-define dds:compression=dxt5 -define dds:mipmaps=0 \
		-alpha set "DDS:$2"
}

small() {  # $1 = source image, $2 = destination dds
	convert "$1" -colorspace sRGB \
		-resize "156x210^" -gravity north -extent 156x210 \
		-define dds:compression=dxt5 -define dds:mipmaps=0 \
		-alpha set "DDS:$2"
}

echo ">> large portraits (156x224, DXT5)"
for dds in "$LEADERS"/Portrait_GLP_*_large.dds; do
	base="$(basename "$dds" .dds)"
	name="${base%_large}"
	stem="$(echo "${name#Portrait_GLP_}" | tr '[:upper:]' '[:lower:]')"
	src_master=""
	for ext in png jpg jpeg; do
		[ -f "$LEADERS/_src_${stem}_large.$ext" ] && src_master="$LEADERS/_src_${stem}_large.$ext"
	done
	if [ -n "$src_master" ]; then
		src="$src_master"
	else
		src="$TMP/$base.png"
		convert "$dds" "$src"
	fi
	large "$src" "$TMP/$base.out.dds"
	mv "$TMP/$base.out.dds" "$dds"
	echo "   $dds  <-  $(basename "$src")"
done

# portraits that only exist as a painterly master (no _large.dds yet)
for src_png in "$LEADERS"/_src_*.png "$LEADERS"/_src_*.jpg; do
	[ -e "$src_png" ] || continue
	stem="$(basename "$src_png")"; stem="${stem%.*}"   # _src_vsevolod_volin_large
	stem="${stem#_src_}"                      # volin_large
	case "$stem" in *_large) ;; *) continue ;; esac
	person="${stem%_large}"
	# map short name -> existing archival portrait file
	match="$(ls "$LEADERS"/Portrait_GLP_*.dds 2>/dev/null \
		| grep -iv '_large' | grep -i "_${person}\.dds" || true)"
	[ -n "$match" ] || continue
	dest="${match%.dds}_large.dds"
	[ -f "$dest" ] && continue
	large "$src_png" "$dest"
	echo "   $dest  <-  $(basename "$src_png")"
done

echo ">> small portraits (156x210, DXT5)"
for dds in "$LEADERS"/Portrait_GLP_*.dds; do
	case "$dds" in *_large.dds) continue ;; esac
	base="$(basename "$dds" .dds)"
	convert "$dds" "$TMP/$base.png"
	small "$TMP/$base.png" "$TMP/$base.out.dds"
	mv "$TMP/$base.out.dds" "$dds"
	echo "   $dds"
done

echo ">> advisor icons (156x210, DXT5)"
for dds in "$IDEAS"/idea_GLP_[A-Z]*.dds; do
	[ -e "$dds" ] || continue
	base="$(basename "$dds" .dds)"
	convert "$dds" "$TMP/$base.png"
	small "$TMP/$base.png" "$TMP/$base.out.dds"
	mv "$TMP/$base.out.dds" "$dds"
	echo "   $dds"
done

echo "done."
