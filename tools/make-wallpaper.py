#!/usr/bin/env python3
"""Assemble the single-file wallpaper from src/template.html + src/data.json
   + src/year.js.  Output: the whole screensaver in one .html file."""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "dist", "index.html")

tpl = io.open(os.path.join(ROOT, "src", "template.html"), encoding="utf-8").read()
data = io.open(os.path.join(ROOT, "src", "data.json"), encoding="utf-8").read()
year = io.open(os.path.join(ROOT, "src", "year.js"), encoding="utf-8").read()

html = tpl.replace("/*__YEAR__*/", year).replace("__DATA__", data)
for token in ("__YEAR__", "__DATA__"):
    if token in html:
        raise SystemExit("placeholder %s left in the output" % token)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, "w", encoding="utf-8").write(html)
print("wrote %s (%.0f KB)" % (OUT, len(html.encode()) / 1024))
