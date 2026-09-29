#!/usr/bin/env bash
# Build every package from dist/: .deb, .rpm, .AppImage and the Windows zips.
# Needs: python3, dpkg-deb (deb), rpmbuild (rpm), curl (to fetch appimagetool).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${VERSION:-1.0.0}"
DIST="$ROOT/dist"
WORK="$DIST/work"
STAGE="$DIST/stage"
APPDIR="$DIST/AppDir"
PAGE="$DIST/index.html"
LOOP="$DIST/studytools-loop-1080p.mp4"
ICON="$DIST/studytools-wallpaper.png"
THUMB="$DIST/thumbnail.jpg"
GIF="$DIST/preview.gif"

say() { printf '  %s\n' "$*"; }
[ -f "$PAGE" ] || { echo "run tools/make-wallpaper.py first" >&2; exit 1; }
[ -f "$ICON" ] || python3 "$ROOT/tools/make-icon.py" >/dev/null
mkdir -p "$DIST" "$WORK"

# ---------------------------------------------------------------- staging tree
# What a system install looks like.  Everything else is cut from this.
rm -rf "$STAGE"
install -d "$STAGE/usr/bin" "$STAGE/usr/share/studytools/scripture" \
           "$STAGE/usr/share/applications" "$STAGE/usr/share/icons/hicolor/256x256/apps" \
           "$STAGE/usr/share/doc/studytools-wallpaper"
install -m 0755 "$ROOT/packaging/linux/studytools-wallpaper" "$STAGE/usr/bin/studytools-wallpaper"
install -m 0644 "$PAGE" "$STAGE/usr/share/studytools/scripture/index.html"
[ -f "$LOOP" ] && install -m 0644 "$LOOP" "$STAGE/usr/share/studytools/scripture/studytools-loop-1080p.mp4" || true
install -m 0644 "$ROOT"/packaging/linux/*.desktop "$STAGE/usr/share/applications/"
install -m 0644 "$ICON" "$STAGE/usr/share/icons/hicolor/256x256/apps/studytools-wallpaper.png"
install -m 0644 "$ROOT/packaging/linux/copyright" "$STAGE/usr/share/doc/studytools-wallpaper/copyright"
sed "s/^# Scripture.*/&/" "$ROOT/README.md" > "$STAGE/usr/share/doc/studytools-wallpaper/README.md" || true
say "staged $(du -sh "$STAGE" | cut -f1) in dist/stage"

# ---------------------------------------------------------------- .deb
if command -v dpkg-deb >/dev/null 2>&1; then
  install -d "$STAGE/DEBIAN"
  SIZE="$(du -sk "$STAGE/usr" | cut -f1)"
  cat > "$STAGE/DEBIAN/control" <<EOF
Package: studytools-wallpaper
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Installed-Size: $SIZE
Depends: dash | bash
Recommends: chromium | chromium-browser | firefox-esr | firefox | google-chrome-stable
Maintainer: studytools.cc <hello@studytools.cc>
Homepage: https://studytools.cc
Description: Scripture on the desktop, from studytools.cc
 A quiet loop of Scripture for the desktop, and a playground when you touch
 it: the Greek or Hebrew behind any word, a catechism question, a verse game,
 the fruit of the Spirit, a candle and a challenge a day.  Every verse and
 every tool it points at is free at studytools.cc.
 .
 Run "studytools-wallpaper" for the desktop, "--screensaver" for full screen,
 and "--stop" to take it down.
EOF
  cat > "$STAGE/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi
exit 0
EOF
  chmod 0755 "$STAGE/DEBIAN/postinst"
  dpkg-deb --root-owner-group --build "$STAGE" "$DIST/studytools-wallpaper_${VERSION}_all.deb" >/dev/null
  rm -rf "$STAGE/DEBIAN"
  say "dist/studytools-wallpaper_${VERSION}_all.deb ($(du -h "$DIST/studytools-wallpaper_${VERSION}_all.deb" | cut -f1))"
else
  say "dpkg-deb not found — no .deb"
fi

# ---------------------------------------------------------------- .rpm
if command -v rpmbuild >/dev/null 2>&1; then
  sed "s/@VERSION@/$VERSION/g" "$ROOT/packaging/linux/studytools-wallpaper.spec" > "$WORK/studytools-wallpaper.spec"
  rpmbuild -bb --quiet \
    --define "stage $STAGE" \
    --define "_topdir $WORK/rpm" \
    --define "_rpmdir $DIST/rpm-out" \
    "$WORK/studytools-wallpaper.spec" >/dev/null
  find "$DIST/rpm-out" -name '*.rpm' -exec mv -f {} "$DIST/studytools-wallpaper-${VERSION}-1.noarch.rpm" \;
  rm -rf "$DIST/rpm-out"
  say "dist/studytools-wallpaper-${VERSION}-1.noarch.rpm ($(du -h "$DIST/studytools-wallpaper-${VERSION}-1.noarch.rpm" | cut -f1))"
else
  say "rpmbuild not found — no .rpm"
fi

# ---------------------------------------------------------------- .AppImage
TOOL="$WORK/appimagetool"
if [ ! -x "$TOOL" ]; then
  for url in \
    "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage" \
    "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" ; do
    if curl -fsSL --retry 2 -o "$TOOL" "$url"; then break; fi
  done
  chmod +x "$TOOL" 2>/dev/null || true
fi
if [ -x "$TOOL" ]; then
  rm -rf "$APPDIR"
  install -d "$APPDIR"
  cp -r "$STAGE/usr" "$APPDIR/usr"
  install -m 0755 "$ROOT/packaging/linux/AppRun" "$APPDIR/AppRun"
  install -m 0644 "$ICON" "$APPDIR/studytools-wallpaper.png"
  install -m 0644 "$ROOT/packaging/linux/studytools-wallpaper.desktop" "$APPDIR/studytools-wallpaper.desktop"
  ln -sf studytools-wallpaper.png "$APPDIR/.DirIcon"
  ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 "$TOOL" --no-appstream "$APPDIR" \
      "$DIST/StudyTools-Wallpaper-${VERSION}-x86_64.AppImage" >/dev/null
  say "dist/StudyTools-Wallpaper-${VERSION}-x86_64.AppImage ($(du -h "$DIST/StudyTools-Wallpaper-${VERSION}-x86_64.AppImage" | cut -f1))"
else
  say "appimagetool could not be fetched — no .AppImage"
fi

# ---------------------------------------------------------------- Windows
VERSION="$VERSION" python3 "$ROOT/tools/make-zips.py"

# ---------------------------------------------------------------- checksums
if command -v sha256sum >/dev/null 2>&1; then
  ( cd "$DIST" && sha256sum *.deb *.rpm *.AppImage *.zip index.html *.mp4 2>/dev/null > SHA256SUMS || true )
  say "dist/SHA256SUMS"
fi

rm -rf "$WORK"
say "done — everything is in dist/"
