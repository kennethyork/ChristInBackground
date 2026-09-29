#!/usr/bin/env python3
"""Build src/data.json — everything the wallpaper shows — out of a checkout of
   the studytools.cc source, so that the wallpaper and the site can never drift
   apart.

   Reads the site's own files:
     data/bible/*.json          the verse text (World English Bible, Updated)
     data/interlinear/<b>/<c>.json  the Greek and Hebrew behind it
     data/catechism/*.json      Westminster Shorter and Heidelberg
     data/vocab/*.json          the top-frequency Greek and Hebrew words
     data/liturgical/*.json     the Prayer Book (1928) feast days

   Usage:
     python3 tools/make-data.py --studytools ../StudyTools --out src/data.json

   The verse pool is REFS, below.  Everything else follows from it.
"""
import argparse, json, os, re

ap = argparse.ArgumentParser()
ap.add_argument("--studytools", default=os.environ.get("STUDYTOOLS", "."),
                help="path to a studytools.cc checkout")
ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                              "src", "data.json"))
args = ap.parse_args()
BASE = os.path.abspath(args.studytools)
OUT = os.path.abspath(args.out)
if not os.path.isdir(os.path.join(BASE, "data", "bible")):
    raise SystemExit("%s does not look like a studytools.cc checkout (no data/bible)" % BASE)

# ---------------------------------------------------------------- the pool
# Every verse the wallpaper may show, in the order it will show them.  Only the
# Christian canon: this is the point of the thing.
REFS = [
 ("genesis",1,[1]),("genesis",1,[27]),("exodus",14,[14]),("deuteronomy",6,[5]),
 ("joshua",1,[9]),("i-samuel",16,[7]),("psalms",19,[1]),("psalms",23,[1]),
 ("psalms",27,[1]),("psalms",34,[8]),("psalms",46,[1]),("psalms",51,[10]),
 ("psalms",91,[1]),("psalms",119,[105]),("psalms",139,[14]),("proverbs",3,[5,6]),
 ("proverbs",4,[23]),("isaiah",9,[6]),("isaiah",40,[31]),("isaiah",41,[10]),
 ("jeremiah",29,[11]),("lamentations",3,[22,23]),("micah",6,[8]),("matthew",5,[16]),
 ("matthew",6,[33]),("matthew",11,[28]),("mark",10,[45]),("luke",1,[37]),
 ("john",1,[1]),("john",3,[16]),("john",8,[12]),("john",14,[6]),("romans",5,[8]),
 ("romans",8,[28]),("romans",12,[2]),("i-corinthians",13,[13]),("ii-corinthians",5,[17]),
 ("galatians",2,[20]),("galatians",5,[22]),("ephesians",2,[8]),("philippians",4,[6,7]),
 ("philippians",4,[13]),("colossians",3,[23]),("i-thessalonians",5,[16,17,18]),
 ("ii-timothy",1,[7]),("hebrews",4,[12]),("hebrews",11,[1]),("hebrews",12,[2]),
 ("james",1,[5]),("i-peter",5,[7]),("i-john",1,[9]),("i-john",4,[8]),
 ("revelation-of-john",3,[20]),("revelation-of-john",21,[4]),
 # --- a second helping, for the live wallpaper ---
 ("numbers",6,[24,25,26]),("deuteronomy",31,[6]),("i-chronicles",16,[11]),
 ("nehemiah",8,[10]),("job",19,[25]),("psalms",1,[1,2]),("psalms",16,[11]),
 ("psalms",37,[4]),("psalms",90,[12]),("psalms",103,[1,2]),("psalms",121,[1,2]),
 ("psalms",127,[1]),("psalms",145,[18]),("proverbs",15,[1]),("proverbs",16,[3]),
 ("proverbs",18,[10]),("proverbs",22,[6]),("ecclesiastes",3,[1]),("isaiah",6,[8]),
 ("isaiah",26,[3]),("isaiah",53,[5]),("isaiah",55,[8,9]),("jeremiah",33,[3]),
 ("daniel",3,[17]),("zephaniah",3,[17]),("malachi",3,[10]),("matthew",4,[4]),
 ("matthew",5,[14]),("matthew",7,[7]),("matthew",22,[37,38,39]),("matthew",28,[19,20]),
 ("luke",6,[38]),("john",10,[10]),("john",11,[25]),("john",15,[5]),("john",16,[33]),
 ("acts",1,[8]),("acts",4,[12]),("romans",6,[23]),("romans",10,[9]),("romans",15,[13]),
 ("i-corinthians",10,[13]),("i-corinthians",15,[57]),("ii-corinthians",4,[18]),
 ("ii-corinthians",12,[9]),("galatians",6,[9]),("ephesians",3,[20]),("ephesians",4,[32]),
 ("ephesians",6,[10,11]),("philippians",1,[6]),("philippians",4,[8]),("colossians",3,[2]),
 ("colossians",3,[16]),("i-thessalonians",5,[24]),("ii-thessalonians",3,[3]),
 ("ii-timothy",3,[16]),("hebrews",13,[5,6]),("hebrews",13,[8]),("james",4,[8]),
 ("james",5,[16]),("i-peter",2,[9]),("i-peter",3,[15]),("i-peter",4,[8]),
 ("ii-peter",3,[9]),("i-john",3,[1]),("i-john",5,[14]),
]

books = {b["slug"]: b for b in json.load(open(os.path.join(BASE, "data/bible/books.json"), encoding="utf-8"))}
_cache = {}

def chapters(slug, trans="WEBU"):
    key = (slug, trans)
    if key not in _cache:
        p = os.path.join(BASE, "data/bible", "%s.%s.json" % (slug, trans))
        _cache[key] = json.load(open(p, encoding="utf-8"))["chapters"] if os.path.exists(p) else None
    return _cache[key]

def tidy(t):
    """One clean line: no double spaces, no quotation mark left hanging when a
       verse is quoted on its own."""
    t = " ".join((t or "").split())
    if t.startswith("\u201c") and not t.endswith("\u201d"): t = t[1:].strip()
    if t.endswith("\u201d") and "\u201c" not in t: t = t[:-1].strip()
    return t

verses = []
for slug, chapter, vs in REFS:
    book = books[slug]
    chap = chapters(slug).get(str(chapter), {})
    parts = [chap.get(str(v)) for v in vs]
    if any(p is None for p in parts):
        raise SystemExit("missing text for %s %d:%s in %s" % (slug, chapter, vs, BASE))
    text = tidy(" ".join(parts))
    if text[:1].islower():                       # a verse quoted mid-sentence
        text = text[0].upper() + text[1:]
    name = "Psalm" if book["name"] == "Psalms" else book["name"]
    verses.append({"ref": "%s %d:%s" % (name, chapter, ",".join(str(v) for v in vs)),
                   "text": text, "slug": slug, "chapter": chapter, "verses": vs,
                   "testament": book["testament"]})

STOP = set("""a an the and or but nor for so yet of to in on at by with from into as
is are was were be been being am do does did done have has had will shall would
should may might must can could he she it they we you i his her its their our your
my me him them us this that these those there here then than also not no nor if
when while who whom which what how why any each every more most other some such
only own same too very just now up out down over under again said says say one
two three first last things thing come came go went""".split())

IRREG = {"loved":"love","loves":"love","made":"make","said":"say","came":"come",
         "went":"go","gone":"go","gave":"give","given":"give","took":"take","taken":"take",
         "seen":"see","saw":"see","known":"know","knew":"know","laid":"lay","found":"find",
         "held":"hold","kept":"keep","left":"leave","led":"lead","stood":"stand",
         "wrote":"write","spoken":"speak","spoke":"speak","children":"child",
         "men":"man","women":"woman","hearts":"heart","lives":"life","fishes":"fish"}

# Curated anchors: an English word -> the Strong's numbers it can stand for.
# Applied only when that number is actually in the verse being read.
STRONGS = {
 "lord":["H3068","G2962"], "god":["H0430","H0410","G2316"], "shepherd":["H7462","G4166"],
 "love":["G26","G25","H157"], "loved":["G25","G26"], "world":["G2889","H8398"],
 "faith":["G4102","H530"], "believe":["G4100"], "believes":["G4100"], "believing":["G4100"],
 "grace":["G5485","H2580"], "truth":["G225","H571"], "hope":["G1680","G1679","H8615"],
 "wait":["H6960","G4037"], "strength":["H3581","G2479"], "strong":["H2388","G2478"],
 "strengthens":["G1743"], "kingdom":["G932","H4438"], "glory":["G1391","H3519"],
 "holy":["G40","H6918"], "spirit":["G4151","H7307"], "word":["G3056","H1697"],
 "light":["G5457","H216"], "heart":["G2588","H3820","H3824"], "peace":["G1515","H7965"],
 "sin":["G266","H2403"], "sins":["G266","H2403"], "forgive":["G863","H5545"],
 "righteous":["G1342","H6662"], "mercy":["G1656","H2617"], "save":["G4982","H3467"],
 "saved":["G4982","H3467"], "fear":["G5399","H3372"], "joy":["G5479","H8057"],
 "serve":["G1247","H5647"], "cross":["G4716"], "life":["G2222","H2416"],
 "death":["G2288","H4194"], "rest":["G372","H4496","H5117"], "wisdom":["G4678","H2451"],
 "patience":["G3115"], "kindness":["G5544","H2617"], "goodness":["G19","H2898"],
 "faithfulness":["G4103"], "gentleness":["G4240"], "self-control":["G1466"],
 "power":["G1411","H3581"], "dwell":["H7931"], "dwells":["H7931"],
 "rejoice":["G5463","H8055"], "pray":["G4336","H6419"], "prayer":["G4335","H8605"],
 "thanks":["G2168","H3034"], "anxious":["G3309"], "cares":["G3309"], "care":["G3309"],
 "courageous":["H2388","H553"], "impossible":["G102"], "way":["G3598","H1870"],
 "door":["G2374"], "knock":["G2925"], "created":["H1254","G2936"], "beginning":["H7225","G746"],
 "image":["H6754"], "heavens":["H8064"], "earth":["H776","G1093"],
 "born":["G1080","G3439"], "only":["G3439"], "eternal":["G166"], "perish":["G622"],
 "son":["G5207","H1121"], "gave":["G1325"], "nothing":["H2637","G3762"], "lack":["H2637"],
 "wings":["H83"], "eagles":["H5404"], "run":["H7323"], "weary":["H3021","H3286"],
 "faint":["H3286"], "walk":["H3212","H1980"], "renew":["H2498"], "mount":["H5927"],
 "seek":["G2212","H1245"], "work":["G2041","H4639"], "works":["G2041"],
 "good":["G18","H2896"], "called":["G2822","H7121"], "purpose":["G4286"],
 "mind":["G3563","H3820"], "renewing":["G342"], "conformed":["G4964"],
 "shepherd":["H7462"], "still":["H7999","G2270"], "fights":["H3898"], "afraid":["H3372","G5399"],
 "dismayed":["H2865"], "commanded":["H6680"], "appearance":["H4758"], "outward":["H5869"],
 "heart":["H3824"], "trust":["H982","G1679","G4100"], "acknowledge":["H3045"],
 "paths":["H734","G5147"], "straight":["H3474"], "lamp":["H5216","G3088"], "feet":["H7272"],
 "path":["H5410"], "fearfully":["H3372"], "wonderfully":["H6395"], "made":["H6213","G4160"],
 "diligence":["H5341"], "wellspring":["H4726"], "counselor":["H3289"], "wonderful":["H6382"],
 "everlasting":["H5703"], "mighty":["G2478"], "prince":["H8269"], "peace":["H7965"],
 "mount":["H5927"], "hoped":["H6960"], "wait":["H6960"], "evil":["H7451"],
 "plans":["H4284"], "future":["H319"], "mercies":["H2617"], "morning":["H1242"],
 "faithfulness":["H530"], "walk":["H1980"], "humbly":["H6800"], "justice":["H4941"],
 "shine":["G2989"], "salt":["G217"], "earth":["G1093"], "served":["G1247"],
 "ransom":["G3083"], "many":["G4183"], "blessed":["G3107","H835"], "refuge":["H4268","G2703"],
 "shepherd":["H7462"], "taste":["H2938"], "refuge":["H2620"], "created":["H1254"],
 "spirit":["G4151"], "fear":["G5401"], "self-control":["G1466"], "knows":["G1097"],
 "wipe":["G1813"], "tear":["G1144"], "mourning":["G3997"], "crying":["G2906"],
 "pain":["G4192"], "passed":["G565"], "sins":["G266"], "unrighteousness":["G93"],
 "confess":["G3670"], "faithful":["G4103"], "door":["G2374"], "dine":["G1172"],
 "joy":["G5479"], "before":["G4295"], "endured":["G5278"], "shame":["G152"],
 "throne":["G2362"], "wisdom":["G4678"], "ask":["G154"], "liberally":["G574"],
 "reproach":["G3679"], "worries":["G3308"], "cares":["G3308"], "anxious":["G3309"],
 "peace":["G1515"], "guard":["G5432"], "surpasses":["G5242"],
 "always":["G3842"], "rejoice":["G5463"], "ceasing":["G89"], "give":["G2168"],
 "thanks":["G2168"], "will":["G2307"], "work":["G2038"],
}

def stem(w):
    if w in IRREG: return IRREG[w]
    w = re.sub(r"'s$", "", w)
    for suf, rep in (("ings",""),("ing",""),("ied","y"),("ies","y"),("ed",""),("es",""),("s",""),("ly","")):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return (w[:-len(suf)] + rep) if rep else w[:-len(suf)]
    return w

def tokens(t): return [x.lower() for x in re.findall(r"[A-Za-z][A-Za-z'\-]*", t)]

# --- morphology ------------------------------------------------------------
# Greek: Robinson/OpenGNT codes.  Hebrew: morphhb codes.  Both are positional,
# so they can be read properly rather than guessed at.  Anything that does not
# parse is shown exactly as the source has it.
GPOS = {"N":"noun","V":"verb","A":"adjective","T":"article","D":"demonstrative pronoun",
        "P":"personal pronoun","R":"relative pronoun","X":"indefinite pronoun",
        "F":"reflexive pronoun","S":"possessive pronoun","C":"reciprocal pronoun",
        "I":"interrogative pronoun","K":"correlative pronoun","CONJ":"conjunction",
        "PREP":"preposition","ADV":"adverb","PRT":"particle","INJ":"interjection",
        "HEB":"Hebrew word","ARAM":"Aramaic word"}
G_TENSE = {"P":"present","I":"imperfect","F":"future","A":"aorist","R":"perfect",
           "L":"pluperfect","X":"no tense"}
G_VOICE = {"A":"active","M":"middle","P":"passive","E":"middle or passive",
           "D":"middle deponent","O":"passive deponent","N":"middle or passive deponent"}
G_MOOD  = {"I":"indicative","S":"subjunctive","O":"optative","M":"imperative",
           "N":"infinitive","P":"participle"}
G_CASE  = {"N":"nominative","G":"genitive","D":"dative","A":"accusative","V":"vocative"}
G_NUM   = {"S":"singular","P":"plural"}
G_GEND  = {"M":"masculine","F":"feminine","N":"neuter"}
G_PERS  = {"1":"1st","2":"2nd","3":"3rd"}

HPOS = {"N":"noun","V":"verb","A":"adjective","P":"pronoun","R":"preposition",
        "T":"particle","C":"conjunction","D":"adverb","S":"suffix"}
H_TYPE = {"c":"common","p":"proper name","g":"gentile"}
HGEND  = {"m":"masculine","f":"feminine","b":"both","c":"common"}
HNUM   = {"s":"singular","p":"plural","d":"dual"}
HSTATE = {"a":"absolute","c":"construct","d":"determined"}
HSTEM  = {"q":"qal","N":"niphal","p":"piel","P":"pual","h":"hiphil","H":"hophal",
          "t":"hithpael","o":"polel","O":"polal","r":"hithpolel","m":"poel","M":"poal"}

def _greek(m):
    head = m.split("-")[0].upper()
    pos = GPOS.get(head, "")
    tail = m.split("-", 1)[1] if "-" in m else ""
    bits = []
    if head == "V" and len(tail) >= 3:
        second = ""
        if tail[0] in "12" and len(tail) >= 4:      # a second aorist or second perfect
            second = "second "; tail = tail[1:]
        t, v, mo = tail[0], tail[1], tail[2]
        bits = []
        if G_TENSE.get(t): bits.append(second + G_TENSE[t])
        if G_VOICE.get(v): bits.append(G_VOICE[v])
        if G_MOOD.get(mo): bits.append(G_MOOD[mo])
        rest = tail[3:].lstrip("-")
        if mo == "P":                       # a participle carries case, number, gender
            if len(rest) >= 3: bits += [G_CASE.get(rest[0]), G_NUM.get(rest[1]), G_GEND.get(rest[2])]
        elif rest:
            if rest[0] in G_PERS and len(rest) > 1: bits.append(G_PERS[rest[0]] + " person")
            if len(rest) > 1: bits.append(G_NUM.get(rest[1]))
    else:
        rest = tail
        if rest and rest[0] in G_PERS and head == "P" and len(rest) > 1 and rest[1] in G_CASE:
            bits.append(G_PERS[rest[0]] + " person"); rest = rest[1:]
        if len(rest) >= 3:
            bits = [G_CASE.get(rest[0]), G_NUM.get(rest[1]), G_GEND.get(rest[2])]
    bits = [b for b in bits if b]
    if pos and bits: return pos + " \u00b7 " + ", ".join(bits)
    return pos or m

def _hebrew(m):
    code = m[1:]
    pos = HPOS.get(code[:1], "")
    bits = []
    if code[:1] == "N" and len(code) > 1:
        bits.append(H_TYPE.get(code[1]))
        if len(code) >= 4:
            bits += [HGEND.get(code[2]), HNUM.get(code[3])]
        if len(code) >= 5: bits.append(HSTATE.get(code[4]))
    elif code[:1] == "V" and len(code) > 2:
        bits.append(HSTEM.get(code[1]))
        conj = {"p":"perfect","i":"imperfect","w":"wayyiqtol","v":"imperative",
                "j":"jussive","c":"infinitive construct","r":"participle",
                "a":"infinitive absolute","t":"infinitive construct","s":"passive participle",
                "u":"cohortative"}
        if code[2] in conj: bits.append(conj[code[2]])
        rest = code[3:]
        if rest[:1] in G_PERS: bits.append(G_PERS[rest[0]] + " person")
        if len(rest) > 1: bits.append(HGEND.get(rest[1]))
        if len(rest) > 2: bits.append(HNUM.get(rest[2]))
    if "S" in code: bits.append("with a pronoun suffix")
    bits = [b for b in bits if b]
    if pos and bits: return pos + " \u00b7 " + ", ".join(bits)
    return pos or m

def morph_label(m):
    """A short, readable decode of a Robinson (Greek) or morphhb (Hebrew) code."""
    m = (m or "").strip()
    if not m: return ""
    if m.startswith("H"):
        return _hebrew(m)
    if re.match(r"^[HV]?-?(CONJ|PREP|ADV|PRT|INJ|HEB|ARAM)$", m.upper()):
        return GPOS.get(m.upper(), m)
    if "-" in m or m[:1] in "NVATDPRXFSCIK":
        return _greek(m)
    return m

def tidy(t):
    """One clean line: no double spaces, no quotation mark left hanging when a
       verse is quoted on its own."""
    t = " ".join((t or "").split())
    if t.startswith("\u201c") and not t.endswith("\u201d"): t = t[1:].strip()
    if t.endswith("\u201d") and "\u201c" not in t: t = t[:-1].strip()
    return t

# ------------------------------------------------------------------ any passage
def passage(slug, chapter, vs):
    p = os.path.join(BASE, "data/bible", "%s.WEBU.json" % slug)
    ch = json.load(open(p, encoding="utf-8"))["chapters"].get(str(chapter), {})
    parts = [ch.get(str(v)) for v in vs]
    if any(x is None for x in parts): return "", False
    text = tidy(" ".join(parts))
    if text[:1].islower(): text = text[0].upper() + text[1:]
    return text, True

# ------------------------------------------------------------------ what to grow in
FRUIT = [
  ("Love", "1 Corinthians 13:13", "i-corinthians", 13, [13],
   "Say it out loud to someone today, in words, not only in feeling."),
  ("Joy", "Psalm 16:11", "psalms", 16, [11],
   "Name one thing today that made you glad, and thank God for it."),
  ("Peace", "John 14:27", "john", 14, [27],
   "Where are you anxious? Put it into a sentence and hand it over."),
  ("Patience", "Romans 12:12", "romans", 12, [12],
   "Who is testing your patience? Pray for them by name, slowly."),
  ("Kindness", "Ephesians 4:32", "ephesians", 4, [32],
   "Do one small kindness today that nobody asked you for."),
  ("Goodness", "Micah 6:8", "micah", 6, [8],
   "Do justly in the small thing in front of you, and don’t announce it."),
  ("Faithfulness", "Lamentations 3:22,23", "lamentations", 3, [22, 23],
   "Keep one promise today that you would rather not keep."),
  ("Gentleness", "Proverbs 15:1", "proverbs", 15, [1],
   "Answer softly the next hard word that comes at you."),
  ("Self-control", "Proverbs 25:28", "proverbs", 25, [28],
   "Skip one thing you want today, and tell nobody."),
]
ARMOR = [
  ("The belt of truth", "Ephesians 6:14", "ephesians", 6, [14],
   "Tell the truth today in the place you are tempted to shade it."),
  ("The breastplate of righteousness", "Ephesians 6:14", "ephesians", 6, [14],
   "Guard what you look at and what you say."),
  ("Shoes for the gospel of peace", "Ephesians 6:15", "ephesians", 6, [15],
   "Be ready to speak peace to someone who expects a fight."),
  ("The shield of faith", "Ephesians 6:16", "ephesians", 6, [16],
   "Name the dart that is aimed at you today, and hold the shield up."),
  ("The helmet of salvation", "Ephesians 6:17", "ephesians", 6, [17],
   "Think about what is true of you in Christ, not what you fear."),
  ("The sword of the Spirit", "Ephesians 6:17", "ephesians", 6, [17],
   "Learn one verse well enough to use it when it is needed."),
]

def grow_set(items):
    out = []
    for name, ref, slug, ch, vs, line in items:
        text, ok = passage(slug, ch, vs)
        if not ok: continue
        out.append({"n": name, "ref": ref, "text": text, "line": line})
    return out

# ------------------------------------------------------------------ quizzes
vocab = []
for lang, fn, want in (("greek", "greek.json", 140), ("hebrew", "hebrew.json", 140)):
    d = json.load(open(os.path.join(BASE, "data/vocab", fn), encoding="utf-8"))
    got = 0
    for w in d["words"]:
        g = (w.get("gloss") or "").strip()
        m = (w.get("morph") or "")
        if not g or len(g) > 20 or any(c in g for c in "/,;()[]"): continue
        if len(w.get("lemma", "")) < 3: continue
        if m.endswith((":T", ":CONJ", ":PREP", ":PRT", ":Art", ":Conj", ":Prep", ":Part", ":Intj")):
            continue
        vocab.append({"l": w["lemma"], "t": w["translit"], "g": g, "s": w["strongs"], "k": lang[:1]})
        got += 1
        if got >= want: break

# other public-domain translations of the same verses, for "which translation?"
alt = {}
for vi, v in enumerate(verses):
    got = {}
    for tr in ("KJV", "YLT"):
        p = os.path.join(BASE, "data/bible", "%s.%s.json" % (v["slug"], tr))
        if not os.path.exists(p): continue
        ch = json.load(open(p, encoding="utf-8"))["chapters"].get(str(v["chapter"]), {})
        parts = [ch.get(str(x)) for x in v["verses"]]
        if any(x is None for x in parts): continue
        got[tr] = tidy(" ".join(parts))
    alt[str(vi)] = got

# ------------------------------------------------------------------ verses + words
words_by_verse, map_by_verse = {}, {}
for vi, v in enumerate(verses):
    p = os.path.join(BASE, "data/interlinear", v["slug"], "%d.json" % v["chapter"])
    chap = json.load(open(p, encoding="utf-8"))["verses"]
    ws = []
    for num in v["verses"]:
        for w in chap.get(str(num), []):
            lemma = w.get("l","") if w.get("l","") != w.get("g","") else ""
            ws.append({"g": w.get("g",""), "l": lemma, "t": w.get("t",""),
                       "s": w.get("s",""), "e": (w.get("e") or "").strip(),
                       "m": morph_label(w.get("m",""))})
    words_by_verse[str(vi)] = ws

    idx = {}
    def add(tok, i):
        idx.setdefault(tok, [])
        if i not in idx[tok]: idx[tok].append(i)
    for tok in dict.fromkeys(tokens(v["text"])):
        if tok in STOP or len(tok) < 3: continue
        for s in STRONGS.get(tok, []):                       # curated anchors first
            for i, w in enumerate(ws):
                if w["s"] == s: add(tok, i)
        if tok not in idx:                                   # then a tight gloss match
            st = stem(tok)
            for i, w in enumerate(ws):
                parts = [x for x in re.split(r"[/|,;()\s]+", w["e"].lower()) if len(x) > 2 and x != "to"]
                for p2 in parts:
                    if stem(p2) == st or (len(st) >= 5 and len(p2) >= 5 and (p2.startswith(st) or st.startswith(p2))):
                        add(tok, i); break
    map_by_verse[str(vi)] = {k: v2[:3] for k, v2 in idx.items() if v2 and k not in STOP}

# ------------------------------------------------------------------ catechisms
cat = {}
for key, fn in (("westminster", "westminster-shorter.json"), ("heidelberg", "heidelberg.json")):
    d = json.load(open(os.path.join(BASE, "data/catechism", fn), encoding="utf-8"))
    cat[key] = {"title": d["title"], "items": [{"n": i["number"], "q": i["question"],
                 "a": re.sub(r"\s+", " ", i["answer"]).strip()} for i in d["items"]]}

# ------------------------------------------------------------------ challenges
CH = [
 ("Send the verse","Text or email today's verse to one person who would be glad of it."),
 ("Pray three names","Pray for three people by name: one you love, one you owe, one you forget."),
 ("Read the chapter","Open the whole chapter at studytools.cc and read it slowly, all of it."),
 ("Say it aloud","Read the verse out loud, twice. Scripture heard is Scripture kept."),
 ("Hide it","Learn today's verse by heart — use the memory game in this screensaver."),
 ("Thank someone","Write a note of thanks to someone who shaped your faith."),
 ("Ask forgiveness","Ask forgiveness of someone you have wronged — today, not someday."),
 ("Forgive one","Name one grudge before you sleep, and let it go."),
 ("Give quietly","Give one thing away today that you would rather keep."),
 ("Serve unseen","Do one good thing for someone who will never know it was you."),
 ("Phone the lonely","Call someone who would be surprised to hear from you."),
 ("Sing something","Sing a hymn or a psalm. Badly is fine."),
 ("Be still","Sit still for two minutes and let the verse sit with you."),
 ("Ask a question","Write down one question you have about the Bible, then look it up."),
 ("Study one word","Take one word from the verse and see every place it appears, at studytools.cc."),
 ("Explain it","Explain the verse to a child — or to the child in you."),
 ("Pray the Psalms","Pray Psalm 23 slowly, one line at a time."),
 ("Walk and pray","Ten minutes outside, no phone, just talking to God."),
 ("Give thanks","List ten things you are thankful for, out loud, before you stop."),
 ("Tell someone","Tell someone the good you see in them."),
 ("Open the door","Ask one person how you can pray for them — then pray it."),
 ("Read it twice","Read the verse again in a different translation at studytools.cc."),
 ("Put it down","Put the phone down for one hour and read Scripture instead."),
 ("Look up","Read Psalm 19:1 outside, and actually look up."),
 ("Write it out","Write the verse on a card and put it where you will see it tomorrow."),
 ("Pray the news","Take one headline today and pray over it."),
 ("Thank God small","Thank God for one small, specific thing from today."),
 ("Keep the feast","Find out what season the church is in this week and read its readings."),
 ("Welcome one","Speak to someone new at church this Sunday."),
 ("Fast something","Skip one thing today — a meal, a feed, a habit — and pray in its place."),
 ("Ask one","Ask someone, 'How is your soul?' and wait for the real answer."),
 ("Rest an hour","Keep a Sabbath hour: no work, no screens, only thanks."),
 ("Amen, and stop","Pray one honest sentence, say Amen, and stop. Don't fill the silence."),
 ("Show the tools","Show one person studytools.cc this week."),
 ("Keep the day","Note the day of the week the church is keeping, and pray its collect."),
]

# English word over each original word, so the panel can say which English word
# stands over which Greek or Hebrew one.
rev_by_verse = {}
for k, mp in map_by_verse.items():
    r = {}
    for tok, idxs in mp.items():
        for i in idxs:
            r.setdefault(str(i), tok)
    rev_by_verse[k] = r

# the Prayer Book's feast days, for naming the day in the corner
lit = json.load(open(os.path.join(BASE, "data/liturgical/bcp1928-daily.json"), encoding="utf-8"))
feasts = {"fixed": {f["date"]: f["name"] for f in lit["fixed"] if f.get("name")},
          "movable": [{"o": m["offset"], "n": m["name"]} for m in lit["movable"] if m.get("name")]}

data = {"site": "https://studytools.cc/", "verses": verses, "words": words_by_verse,
        "map": map_by_verse, "rev": rev_by_verse, "catechism": cat, "challenges": CH,
        "grow": {"fruit": grow_set(FRUIT), "armor": grow_set(ARMOR)},
        "vocab": vocab, "alt": alt, "feasts": feasts}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("grow %d fruit + %d armour | vocab %d | alt translations %d verses"
      % (len(data["grow"]["fruit"]), len(data["grow"]["armor"]), len(vocab),
         sum(1 for v in alt.values() if v)))
print("verses %d | words %d | tappable %d | catechism %d+%d | challenges %d | feasts %d"
      % (len(verses), sum(len(w) for w in words_by_verse.values()),
         sum(len(m) for m in map_by_verse.values()),
         len(cat["westminster"]["items"]), len(cat["heidelberg"]["items"]), len(CH),
         len(feasts["fixed"]) + len(feasts["movable"])))
print("wrote %s (%.0f KB)" % (OUT, os.path.getsize(OUT) / 1024))
