#!/usr/bin/env bash
# Everything, in order: the page, the icon, the video loop, all the packages.
set -euo pipefail
cd "$(dirname "$0")"
VERSION="${VERSION:-1.0.0}"
COUNT="${COUNT:-12}"        # verses in the video loop
HOLD="${HOLD:-8}"           # seconds each verse stays, in the loop

python3 tools/make-wallpaper.py dist/index.html
python3 tools/make-icon.py dist/studytools-wallpaper.png
python3 tools/make-video.py --count "$COUNT" --seconds "$HOLD"
VERSION="$VERSION" bash tools/make-packages.sh
echo
echo "everything is in dist/ — the wallpaper itself is dist/index.html"
