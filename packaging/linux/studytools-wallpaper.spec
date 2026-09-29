Name:           studytools-wallpaper
Version:        @VERSION@
Release:        1
Summary:        Scripture on the desktop, from studytools.cc
License:        MIT
URL:            https://studytools.cc
BuildArch:      noarch
Requires:       /bin/sh
Recommends:     chromium

%description
A quiet loop of Scripture for the desktop, and a playground when you touch it:
the Greek or Hebrew behind any word, a catechism question, a verse game, the
fruit of the Spirit, a candle and a challenge a day.  Every verse and every
tool it points at is free at studytools.cc.

Run "studytools-wallpaper" for the desktop, "studytools-wallpaper
--screensaver" for full screen, and "--stop" to take it down.

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_datadir}/studytools/scripture
install -d %{buildroot}%{_datadir}/applications
install -d %{buildroot}%{_datadir}/icons/hicolor/256x256/apps
install -d %{buildroot}%{_datadir}/doc/studytools-wallpaper
install -m 0755 %{stage}/usr/bin/studytools-wallpaper %{buildroot}%{_bindir}/studytools-wallpaper
cp -p %{stage}/usr/share/studytools/scripture/* %{buildroot}%{_datadir}/studytools/scripture/
cp -p %{stage}/usr/share/applications/*.desktop %{buildroot}%{_datadir}/applications/
cp -p %{stage}/usr/share/icons/hicolor/256x256/apps/*.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/
cp -p %{stage}/usr/share/doc/studytools-wallpaper/* %{buildroot}%{_datadir}/doc/studytools-wallpaper/

%files
%{_bindir}/studytools-wallpaper
%{_datadir}/studytools/scripture/
%{_datadir}/applications/studytools-wallpaper.desktop
%{_datadir}/applications/studytools-screensaver.desktop
%{_datadir}/icons/hicolor/256x256/apps/studytools-wallpaper.png
%{_datadir}/doc/studytools-wallpaper/

%changelog
* Mon Sep 28 2026 studytools.cc - @VERSION@-1
- first build
