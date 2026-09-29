#!/usr/bin/env python3
"""Render the quiet loop as a video, for the desktops that want a video
   wallpaper rather than a web page: GNOME/Wayland with an mpv extension,
   mpvpaper, a KDE video wallpaper, Wallpaper Engine, and so on.

   Frames are drawn with Pillow and piped straight into ffmpeg — no temporary
   files.  The look is the wallpaper's own: warm near-black, a slow glow, the
   verse in a serif, the reference in gold, and the site's name in the corner.

   Usage:  make-video.py [--width 1920] [--height 1080] [--fps 24]
                         [--seconds 8] [--count 12] [--out dist/loop.mp4]
"""
import argparse, json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(ROOT, "dist", "studytools-loop-1080p.mp4")

SERIF = ["/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
         "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"]
SANS = ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf"]
SANS_B = ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
          "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"]

INK = (247, 241, 232); GOLD = (232, 180, 116); FAINT = (158, 146, 133)
BG_TOP = (23, 18, 14); BG_BOT = (10, 8, 8)

TAGLINES = [
    "Every verse here is free to read at studytools.cc",
    "The whole Bible in seven translations \u00b7 studytools.cc",
    "Tap any word for the Greek or Hebrew behind it \u00b7 studytools.cc",
    "23 study tools, no account, no tracking \u00b7 studytools.cc",
    "Commentary, cross-references and the original text \u00b7 studytools.cc",
]


def font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    raise SystemExit("no usable font found in %s" % paths)


def wrap(draw, text, fnt, max_w):
    words, lines, line = text.split(), [], ""
    for w in words:
        trial = (line + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not line:
            line = trial
        else:
            lines.append(line); line = w
    if line: lines.append(line)
    return lines


def spaced(draw, xy, text, fnt, spacing, fill, anchor="ls"):
    """Draw text with letter-spacing, centred on x."""
    widths = [draw.textlength(c, font=fnt) for c in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x, y = xy
    if anchor.startswith("m"):
        x -= total / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=fnt, fill=fill)
        x += w + spacing
    return total


def background(w, h):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)))
    glow = Image.new("L", (w, h), 0)
    g = ImageDraw.Draw(glow)
    cx, cy, r = w * 0.5, h * 0.40, max(w, h) * 0.55
    for i in range(60):
        rad = r * (1 - i / 60.0)
        g.ellipse([cx - rad, cy - rad * 0.72, cx + rad, cy + rad * 0.72], fill=int(3 + i * 2.2))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.composite(Image.new("RGB", (w, h), (104, 72, 40)), img, glow)
    return img


def vignette(w, h):
    v = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(v)
    for i in range(40):
        k = i / 40.0
        d.rectangle([-w * k * 0.5 + (w * 0.5) * 0, 0, w, h], outline=None)
    # a radial darkening towards the corners
    small = Image.new("L", (64, 36), 0)
    ds = ImageDraw.Draw(small)
    for y in range(36):
        for x in range(64):
            dx, dy = (x - 32) / 32.0, (y - 18) / 18.0
            r = math.sqrt(dx * dx + dy * dy) / 1.5
            ds.point((x, y), fill=int(min(1.0, max(0.0, (r - 0.45) / 0.55)) * 120))
    return small.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))


def verse_layer(v, w, h, scale):
    """The verse, its reference and the rule above it, drawn once per verse."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    max_w = int(w * 0.74)
    sizes = [int(w * 0.036), int(w * 0.033), int(w * 0.030), int(w * 0.027), int(w * 0.024), int(w * 0.021)]
    chosen, lines = None, None
    for s in sizes:
        f = font(SERIF, s)
        ls = wrap(d, v["text"], f, max_w)
        if len(ls) <= 4:
            chosen, lines = f, ls
            break
    if chosen is None:
        chosen = font(SERIF, sizes[-1]); lines = wrap(d, v["text"], chosen, max_w)

    lh = int(chosen.size * 1.34)
    block_h = lh * len(lines)
    top = int(h * 0.40) - block_h // 2
    for i, line in enumerate(lines):
        spaced(d, (w / 2, top + i * lh), line, chosen, 0, INK, anchor="ms")

    # the rule, then the reference in gold
    y = top + block_h + int(h * 0.045)
    half = int(w * 0.036)
    for i in range(half * 2):
        a = int(215 * (1 - abs(i - half) / float(half)) ** 1.6)
        if a > 0:
            d.point((w / 2 - half + i, y), fill=GOLD + (a,))
    rf = font(SANS_B, int(w * 0.0105))
    spaced(d, (w / 2, y + int(h * 0.030)), v["ref"].upper(), rf, int(w * 0.0035), GOLD, anchor="ms")
    sf = font(SANS, int(w * 0.0085))
    spaced(d, (w / 2, y + int(h * 0.058)), "WORLD ENGLISH BIBLE (UPDATED) \u00b7 PUBLIC DOMAIN",
           sf, int(w * 0.0028), FAINT, anchor="ms")
    if scale != 1.0:
        layer = layer.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        off = ((layer.width - w) // 2, (layer.height - h) // 2)
        layer = layer.crop((off[0], off[1], off[0] + w, off[1] + h))
    return layer


def chrome(w, h, tagline):
    """The corner: the site's mark, and a line of what is there."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pad = int(w * 0.028)
    # a cross
    cw, ch, t = int(w * 0.0090), int(w * 0.0125), max(2, int(w * 0.0016))
    x0, y0 = pad, pad + int(h * 0.012)
    d.rectangle([x0, y0, x0 + t - 1, y0 + ch], fill=GOLD)
    d.rectangle([x0, y0 + int(ch * 0.30), x0 + cw, y0 + int(ch * 0.30) + t], fill=GOLD)
    wf = font(SERIF, int(w * 0.0125))
    d.text((x0 + cw + int(w * 0.008), y0 + int(ch * 0.05)), "studytools.cc", font=wf, fill=INK)
    tf = font(SANS, int(w * 0.0095))
    d.text((pad, h - pad - int(h * 0.02)), tagline, font=tf, fill=FAINT)
    cf = font(SERIF, int(w * 0.0125))
    txt = "Read the whole Bible free \u2192"
    tw = d.textlength(txt, font=cf)
    d.text((w - pad - tw, h - pad - int(h * 0.02)), txt, font=cf, fill=GOLD)
    return layer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--seconds", type=float, default=8.0, help="seconds each verse stays")
    ap.add_argument("--count", type=int, default=12, help="how many verses in the loop")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--gif", default=os.path.join(ROOT, "dist", "preview.gif"))
    ap.add_argument("--thumbnail", default=os.path.join(ROOT, "dist", "thumbnail.jpg"))
    ap.add_argument("--test", type=int, default=0, help="render only N frames, to check the look")
    args = ap.parse_args()

    w, h = args.width, args.height
    data = json.load(open(os.path.join(ROOT, "src", "data.json"), encoding="utf-8"))
    pool = data["verses"]
    step = max(1, len(pool) // max(1, args.count))
    verses = pool[::step][:args.count]

    bg = background(w, h)
    vig = vignette(w, h)
    layers = [verse_layer(v, w, h, 1.0) for v in verses]
    chromes = [chrome(w, h, TAGLINES[i % len(TAGLINES)]) for i in range(len(verses))]

    rnd = random.Random(7)
    motes = [{"x": rnd.random() * w, "y": rnd.random() * h, "r": rnd.uniform(0.5, 1.5),
              "v": rnd.uniform(3, 12), "a": rnd.uniform(8, 34)} for _ in range(int(w * h / 34000))]

    fade = 0.9                                   # seconds of fade at each end
    per = max(1, int(args.seconds * args.fps))
    fades = max(1, int(fade * args.fps))
    total = per * len(verses)
    if args.test:
        total = min(total, args.test)

    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (w, h), "-r", str(args.fps), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "26", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", args.out]
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    if args.test:
        print("test render: %d frames -> %s" % (total, args.out))
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    shots = []
    try:
        for n in range(total):
            vi = (n // per) % len(verses)
            t = (n % per) / args.fps
            a = min(1.0, t / fade) * min(1.0, max(0.0, (args.seconds - t) / fade))
            frame = bg.copy()
            d = ImageDraw.Draw(frame, "RGBA")
            for m in motes:                  # the drift of small warm motes
                m["y"] -= m["v"] / args.fps
                if m["y"] < -4: m["y"] = h + 4; m["x"] = rnd.random() * w
                d.ellipse([m["x"] - m["r"], m["y"] - m["r"], m["x"] + m["r"], m["y"] + m["r"]],
                          fill=(255, 242, 222, int(m["a"] * 0.55)))
            if a > 0.01:
                lay = layers[vi]
                lay = lay.point(lambda p: p) if a >= 0.999 else lay.point(lambda p: int(p * a))
                frame = Image.alpha_composite(frame.convert("RGBA"), lay).convert("RGB")
                ch = chromes[vi].point(lambda p: int(p * min(1.0, a * 2)))
                frame = Image.alpha_composite(frame.convert("RGBA"), ch).convert("RGB")
            frame = Image.composite(Image.new("RGB", (w, h), (0, 0, 0)), frame,
                                    vig.point(lambda p: int(p * 0.42)))
            proc.stdin.write(frame.tobytes())
            if n % max(1, total // 10) == 0 and a > 0.9:
                shots.append(frame.copy())
            if n % 240 == 0:
                print("  frame %d/%d" % (n, total), flush=True)
    finally:
        proc.stdin.close()
        proc.wait()

    if shots:
        try:
            shots[len(shots) // 2].save(args.thumbnail, quality=86)
            small = [s.resize((480, int(480 * h / w)), Image.LANCZOS).convert("P", palette=Image.ADAPTIVE, colors=128)
                     for s in shots[:8]]
            small[0].save(args.gif, save_all=True, append_images=small[1:], duration=700, loop=0, optimize=True)
            print("wrote %s and %s" % (args.thumbnail, args.gif))
        except Exception as e:
            print("thumbnail/gif skipped:", e)
    print("wrote %s (%.1f MB, %.0fs)" % (args.out, os.path.getsize(args.out) / 1e6, total / args.fps))


if __name__ == "__main__":
    main()
