#!/usr/bin/env bash
#
# Generates the Android launcher icons from assets/logo.png.
#
# android/ is generated output and is gitignored, so `npx cap add android` puts
# Capacitor's default Ionic logo back on every build. This re-applies the project
# icon afterwards, the same way apply-android-config.mjs re-applies the Gradle
# wiring.
#
# Three sets are produced, because Android picks a different one per version:
#
#   ic_launcher_foreground.png   API 26+. Composited over a solid background and
#                                then clipped by an OEM-chosen mask — circle,
#                                squircle, rounded square, teardrop. Only the
#                                centre survives, so the artwork is inset.
#   ic_launcher.png              Pre-API 26. Drawn as-is, unmasked, so it can go
#                                edge to edge.
#   ic_launcher_round.png        API 25 round-icon opt-in. Drawn as-is and
#                                expected to already be circular.
#
# The inset is the part that is easy to get wrong. An adaptive icon is 108dp but
# a mask may crop to a 66dp circle, and a *square* logo inscribed in that circle
# can only be 66/sqrt(2) = 47dp, i.e. 43% of 108. Scaling the logo to fill
# instead — which is what a naive `convert -resize` does — throws away the gold
# border and the outer text on every device with a round mask.
#
# 58% was chosen by rendering the real output under circle and squircle masks and
# looking at it: the whole badge including its gold frame stays inside both, with
# margin to spare, while still filling the tile the way a normal app icon does.
# 64% left the corners grazing the circle edge; 52% looked undersized.

set -euo pipefail

SRC="${1:-assets/logo.png}"
RES="${2:-android/app/src/main/res}"

# Matches the game's own panel colour, so the icon sits on the same navy as the
# logo's own background and the seam is invisible.
NAVY="#0B1F3A"

# Percentage of the adaptive canvas the square logo occupies. See the note above.
INSET_PCT=58
# Percentage of the round icon's diameter the square logo occupies.
ROUND_PCT=68

# ImageMagick 7 exposes one `magick` binary; ImageMagick 6 — which is what Ubuntu
# Noble still ships, and therefore what the container has — exposes `convert` and
# `identify` instead and has no `magick` at all. Resolve whichever is present so
# the same script runs on the build image and on a developer machine.
if command -v magick >/dev/null 2>&1; then
    IM=(magick); IM_IDENTIFY=(magick identify)
elif command -v convert >/dev/null 2>&1; then
    IM=(convert); IM_IDENTIFY=(identify)
else
    echo "FATAL: ImageMagick is required (need either 'magick' or 'convert')" >&2
    exit 1
fi
[ -f "$SRC" ] || { echo "FATAL: source icon $SRC not found" >&2; exit 1; }
[ -d "$RES" ] || { echo "FATAL: res directory $RES not found; run 'npx cap add android' first" >&2; exit 1; }

# density:legacy:foreground — sizes are fixed by the platform, not by us.
DENSITIES="mdpi:48:108 hdpi:72:162 xhdpi:96:216 xxhdpi:144:324 xxxhdpi:192:432"

for entry in $DENSITIES; do
    IFS=: read -r density legacy fg <<<"$entry"
    dir="$RES/mipmap-$density"
    mkdir -p "$dir"

    # --- Adaptive foreground: logo inset on a transparent canvas -------------
    inner=$(( fg * INSET_PCT / 100 ))
    "${IM[@]}" "$SRC" -resize "${inner}x${inner}" \
        -background none -gravity center -extent "${fg}x${fg}" \
        "$dir/ic_launcher_foreground.png"

    # --- Legacy square: unmasked, so the logo can fill the whole tile --------
    "${IM[@]}" "$SRC" -resize "${legacy}x${legacy}!" "$dir/ic_launcher.png"

    # --- Round: logo inset on a navy disc, already circular ------------------
    r_inner=$(( legacy * ROUND_PCT / 100 ))
    radius=$(( legacy / 2 ))
    "${IM[@]}" -size "${legacy}x${legacy}" "xc:$NAVY" \
        \( "$SRC" -resize "${r_inner}x${r_inner}" \) -gravity center -composite \
        \( -size "${legacy}x${legacy}" xc:none -fill white \
           -draw "circle $radius,$radius $radius,0" \) \
        -alpha off -compose CopyOpacity -composite \
        "$dir/ic_launcher_round.png"

    printf '  icons   %-8s legacy %sx%s  foreground %sx%s\n' "$density" "$legacy" "$legacy" "$fg" "$fg"
done

# --- Background colour behind the adaptive foreground -----------------------
# The template ships white, which would frame the navy badge in a bright ring on
# every adaptive launcher.
cat > "$RES/values/ic_launcher_background.xml" <<XML
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="ic_launcher_background">$NAVY</color>
</resources>
XML
echo "  icons   background $NAVY"

# --- Post-conditions --------------------------------------------------------
# Assert every file exists at the size the platform expects, so a silently failed
# resize cannot ship a default Ionic logo.
for entry in $DENSITIES; do
    IFS=: read -r density legacy fg <<<"$entry"
    dir="$RES/mipmap-$density"
    for pair in "ic_launcher.png:$legacy" "ic_launcher_round.png:$legacy" "ic_launcher_foreground.png:$fg"; do
        file="${pair%%:*}"; want="${pair##*:}"
        got=$("${IM_IDENTIFY[@]}" -format '%w' "$dir/$file")
        [ "$got" = "$want" ] || { echo "FATAL: $dir/$file is ${got}px, expected ${want}px" >&2; exit 1; }
    done
done

grep -q "$NAVY" "$RES/values/ic_launcher_background.xml" \
    || { echo "FATAL: launcher background colour was not applied" >&2; exit 1; }

echo "  icons   all 15 bitmaps verified at the expected sizes"
