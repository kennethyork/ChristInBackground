#!/usr/bin/env python3
"""The Windows packages: a Lively Wallpaper file, a Wallpaper Engine project,
   and a portable folder for anyone who would rather just have the files."""
import json, os, shutil, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
WORK = os.path.join(DIST, "work")
VERSION = os.environ.get("VERSION", "1.0.0")
PAGE = os.path.join(DIST, "index.html")
LOOP = os.path.join(DIST, "studytools-loop-1080p.mp4")
THUMB = os.path.join(DIST, "thumbnail.jpg")
GIF = os.path.join(DIST, "preview.gif")


def zip_folder(folder, out):
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(folder):
            for f in sorted(files):
                p = os.path.join(base, f)
                z.write(p, os.path.relpath(p, folder))
    print("  %s (%.0f KB)" % (os.path.basename(out), os.path.getsize(out) / 1024))


def fresh(name):
    d = os.path.join(WORK, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    return d


os.makedirs(WORK, exist_ok=True)
for needed in (PAGE, THUMB, GIF):
    if not os.path.exists(needed):
        raise SystemExit("missing %s — run make-wallpaper.py and make-video.py first" % needed)

# --- Lively Wallpaper: .zip with LivelyInfo.json, dropped straight into Lively
d = fresh("lively")
shutil.copy(PAGE, os.path.join(d, "index.html"))
shutil.copy(THUMB, os.path.join(d, "thumbnail.jpg"))
shutil.copy(GIF, os.path.join(d, "preview.gif"))
info = json.load(open(os.path.join(ROOT, "packaging", "windows", "LivelyInfo.json"), encoding="utf-8"))
info["AppVersion"] = VERSION + ".0"
json.dump(info, open(os.path.join(d, "LivelyInfo.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
zip_folder(d, os.path.join(DIST, "Scripture-studytools-Lively-%s.zip" % VERSION))

# --- Wallpaper Engine: a project folder with project.json and a web wallpaper
d = fresh("wallpaper-engine")
shutil.copy(PAGE, os.path.join(d, "index.html"))
shutil.copy(THUMB, os.path.join(d, "preview.jpg"))
proj = json.load(open(os.path.join(ROOT, "packaging", "windows", "project.json"), encoding="utf-8"))
json.dump(proj, open(os.path.join(d, "project.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
with open(os.path.join(d, "how-to.txt"), "w", encoding="utf-8") as f:
    f.write("""Scripture \u2014 studytools.cc, as a Wallpaper Engine web wallpaper

1. Put this folder somewhere you keep wallpapers, for example:
   C:\\Program Files (x86)\\Steam\\steamapps\\common\\wallpaper_engine\\projects\\myprojects\\scripture
2. Open Wallpaper Engine \u2192 Create Wallpaper \u2192 "Open from File" (or just drop the folder on
   the "Create Wallpaper" screen) and pick index.html.
3. In the wallpaper's settings, turn ON mouse input if you want the words to be tappable.
4. Save it and apply it to a monitor.

Everything it shows comes from studytools.cc; the page itself makes no network calls.
""")
zip_folder(d, os.path.join(DIST, "Scripture-wallpaper-engine-%s.zip" % VERSION))

# --- portable: the page, the video loop, and a note
d = fresh("portable")
shutil.copy(PAGE, os.path.join(d, "studytools-screensaver.html"))
if os.path.exists(LOOP):
    shutil.copy(LOOP, os.path.join(d, "studytools-loop-1080p.mp4"))
shutil.copy(THUMB, os.path.join(d, "thumbnail.jpg"))
with open(os.path.join(d, "READ-ME-FIRST.txt"), "w", encoding="utf-8") as f:
    f.write("""Scripture \u2014 a screensaver and wallpaper for studytools.cc
=====================================================

studytools-screensaver.html
    The whole thing, in one file. Double-click it, press F for full
    screen, or hand it to any wallpaper tool that can show a web page
    (Lively Wallpaper on Windows, Plash on macOS, a browser in kiosk mode
    on Linux). Move the mouse and a bar appears along the bottom: tap any
    word for the Greek or Hebrew behind it, hide the verse and test your
    memory, take a catechism question, a verse game, a candle, a
    challenge a day.

studytools-loop-1080p.mp4
    The same verses as a silent 96-second video loop, for anything that
    takes a video rather than a page: GNOME or KDE live-wallpaper tools,
    mpvpaper, Wallpaper Engine's video type, a TV, a lock screen.

thumbnail.jpg
    A still, if you want one.

Every verse, and every tool it points at, is free at studytools.cc.
The text is public domain (World English Bible, Updated).
""")
zip_folder(d, os.path.join(DIST, "Scripture-portable-%s.zip" % VERSION))
