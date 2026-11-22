"""Builds the animated SVGs in assets/ used by the profile README.

Fonts are subset and embedded so the SVGs render the same inside GitHub's <img> sandbox.
Run: python3 scripts/build_assets.py  (needs fonttools + brotli)
"""

import base64
import io
import math
import pathlib
import urllib.request
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONT_DIR = ROOT / ".fonts"
GF = "https://github.com/google/fonts/raw/main/ofl/"
SOURCES = {
    "InstrumentSerif-Regular.ttf": GF + "instrumentserif/InstrumentSerif-Regular.ttf",
    "InstrumentSerif-Italic.ttf": GF + "instrumentserif/InstrumentSerif-Italic.ttf",
    "Geist.ttf": GF + "geist/Geist%5Bwght%5D.ttf",
    "GeistMono.ttf": GF + "geistmono/GeistMono%5Bwght%5D.ttf",
}

BG = "#141210"
CARD = "#1b1916"
LINE = "#2f2b26"
BONE = "#ede6da"
MUTED = "#9a9288"
DIM = "#5f5952"
EMBER = "#e8643c"


def font_path(name):
    FONT_DIR.mkdir(exist_ok=True)
    p = FONT_DIR / name
    if not p.exists():
        urllib.request.urlretrieve(SOURCES[name], p)
    return p


def load(name, wght=None):
    f = TTFont(font_path(name))
    if wght is not None and "fvar" in f:
        f = instancer.instantiateVariableFont(f, {"wght": wght})
    return f


FONTS = {
    "serif": ("InstrumentSerif-Regular.ttf", None, "normal"),
    "serif-i": ("InstrumentSerif-Italic.ttf", None, "italic"),
    "sans": ("Geist.ttf", 400, "normal"),
    "sans-m": ("Geist.ttf", 500, "normal"),
    "mono": ("GeistMono.ttf", 400, "normal"),
}
_cache = {}


def font(key):
    if key not in _cache:
        name, w, _ = FONTS[key]
        _cache[key] = load(name, w)
    return _cache[key]


def width(text, key, size):
    f = font(key)
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    return sum(hmtx[cmap.get(ord(c), cmap[32])][0] for c in text) * size / upm


def wrap(text, key, size, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if width(trial, key, size) > max_w and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


class Svg:
    def __init__(self, w, h, label):
        self.w, self.h, self.label = w, h, label
        self.body, self.css, self.used = [], [], {}

    def text(self, x, y, s, key, size, fill=BONE, anchor="start", cls="", extra=""):
        self.used.setdefault(key, set()).update(s)
        self.body.append(
            f'<text x="{x:.1f}" y="{y:.1f}" class="{f"f-{key} {cls}".strip()}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}"{extra}>{escape(s)}</text>'
        )

    def add(self, s):
        self.body.append(s)

    def style(self, s):
        self.css.append(s)

    def font_css(self):
        out = []
        for key, chars in self.used.items():
            name, w, style = FONTS[key]
            f = load(name, w)
            opts = subset.Options()
            opts.flavor = "woff2"
            opts.layout_features = ["kern", "liga"]
            sub = subset.Subsetter(opts)
            sub.populate(text="".join(chars) + " ")
            sub.subset(f)
            buf = io.BytesIO()
            f.flavor = "woff2"
            f.save(buf)
            b64 = base64.b64encode(buf.getvalue()).decode()
            out.append(
                f"@font-face{{font-family:'{key}';font-style:{style};"
                f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
                f".f-{key}{{font-family:'{key}'}}"
            )
        return "".join(out)

    def save(self, name):
        css = self.font_css() + "".join(self.css)
        css += "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{escape(self.label)}">'
            f"<title>{escape(self.label)}</title><style>{css}</style>"
            + "".join(self.body)
            + "</svg>"
        )
        (ASSETS / name).write_text(svg)
        print(f"{name}: {len(svg) // 1024} KB")


def frame(s, rx=18, fill=BG):
    s.add(
        f'<rect x="0.5" y="0.5" width="{s.w - 1}" height="{s.h - 1}" rx="{rx}" fill="{fill}" stroke="{LINE}"/>'
    )


def dots(s, x0, y0, x1, y1, gap=24):
    s.add(
        f'<defs><pattern id="d" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="{LINE}"/></pattern></defs>'
        f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#d)" opacity=".7"/>'
    )


COMMON = (
    "@keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}"
    "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}"
    ".up{animation:up .9s cubic-bezier(.2,.7,.2,1) both}"
    ".pulse{animation:pulse 1.6s ease-in-out infinite}"
)


def hero():
    s = Svg(
        1200,
        440,
        "Yasir Ziyaudeen Ahamed, AI engineer: agents that are checked before they act",
    )
    s.style(COMMON)
    frame(s)
    dots(s, 1, 1, 1199, 439)
    s.add(
        f'<rect x="1" y="1" width="640" height="438" rx="18" fill="{BG}" opacity=".82"/>'
    )

    s.add(f'<circle cx="70" cy="86" r="4.5" fill="{EMBER}" class="pulse"/>')
    s.text(
        84,
        91,
        "AI ENGINEER  ·  ABU DHABI, UAE  ·  OPEN TO ROLES",
        "mono",
        13,
        MUTED,
        cls="up",
    )
    s.text(
        62,
        186,
        "Yasir Ziyaudeen",
        "serif",
        76,
        BONE,
        cls="up",
        extra=' style="animation-delay:.1s"',
    )
    s.text(
        62,
        262,
        "Ahamed",
        "serif-i",
        76,
        EMBER,
        cls="up",
        extra=' style="animation-delay:.2s"',
    )
    for i, line in enumerate(
        [
            "I build LLM agents, then the checks that stop",
            "them doing what they shouldn't.",
        ]
    ):
        s.text(
            64,
            322 + i * 30,
            line,
            "sans",
            21,
            MUTED,
            cls="up",
            extra=f' style="animation-delay:{0.35 + i * 0.08:.2f}s"',
        )
    s.text(
        64,
        392,
        "Grounding  ·  policy gates  ·  evals  ·  shipped to production",
        "mono",
        12.5,
        DIM,
        cls="up",
        extra=' style="animation-delay:.55s"',
    )

    px, py, pw, ph = 680, 56, 460, 328
    s.add(
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="14" fill="{CARD}" stroke="{LINE}"/>'
    )
    s.text(px + 22, py + 34, "marcus  ·  checkout-flow", "mono", 13, MUTED)
    s.add(
        f'<circle cx="{px + pw - 62}" cy="{py + 30}" r="4" fill="{EMBER}" class="pulse"/>'
    )
    s.text(px + pw - 22, py + 34, "live", "mono", 13, MUTED, anchor="end")
    s.add(
        f'<line x1="{px}" y1="{py + 52}" x2="{px + pw}" y2="{py + 52}" stroke="{LINE}"/>'
    )

    rows = [
        ("Crawl", "214 real elements on /cart", "read", False),
        ("Draft", "LLM proposes 9 test steps", "llm", False),
        ("Ground", "\u201cApply coupon\u201d isn\u2019t on the page", "rejected", True),
        ("Policy", "\u201cPay now\u201d is a risky action", "blocked", True),
        ("Run", "7 verified steps, 1 real bug", "passed", False),
    ]
    period = 11
    s.style(
        "@keyframes row{0%{opacity:0;transform:translateX(-10px)}3%{opacity:1;transform:none}"
        "86%{opacity:1}92%,100%{opacity:0}}"
        f".row{{animation:row {period}s cubic-bezier(.2,.7,.2,1) infinite both}}"
        "@keyframes scan{0%{transform:translateY(0);opacity:0}5%{opacity:1}55%{opacity:1}"
        "62%,100%{transform:translateY(260px);opacity:0}}"
        f".scan{{animation:scan {period}s linear infinite}}"
    )
    for i, (step, desc, chip, bad) in enumerate(rows):
        y = py + 92 + i * 50
        d = 0.4 + i * 1.1
        g = [f'<g class="row" style="animation-delay:{d:.1f}s">']
        s.add("".join(g))
        s.add(
            f'<circle cx="{px + 30}" cy="{y - 5}" r="3.5" fill="{EMBER if bad else MUTED}"/>'
        )
        s.text(px + 46, y, step, "sans-m", 16, BONE)
        s.text(px + 118, y, desc, "sans", 14.5, MUTED)
        cw = width(chip, "mono", 11.5) + 20
        cx = px + pw - 22 - cw
        color = EMBER if bad else MUTED
        s.add(
            f'<rect x="{cx:.1f}" y="{y - 17}" width="{cw:.1f}" height="22" rx="11" fill="none" stroke="{color}"/>'
        )
        s.text(cx + cw / 2, y - 2, chip, "mono", 11.5, color, anchor="middle")
        s.add("</g>")
    s.add(
        f'<g class="scan"><rect x="{px + 1}" y="{py + 46}" width="{pw - 2}" height="16" fill="{EMBER}" opacity=".05"/>'
        f'<rect x="{px + 1}" y="{py + 62}" width="{pw - 2}" height="1" fill="{EMBER}" opacity=".35"/></g>'
    )
    s.save("hero.svg")


def stats():
    s = Svg(
        1200,
        150,
        "5,000+ agent test runs, about 20 web apps tested, 10,000+ RAG assistant users, 4 hackathon wins",
    )
    s.style(
        COMMON + "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
        ".bar{transform-box:fill-box;transform-origin:left;animation:grow 1.2s cubic-bezier(.2,.7,.2,1) both}"
    )
    frame(s)
    items = [
        ("5,000+", "agent test runs, Marcus"),
        ("~20", "web apps tested"),
        ("10,000+", "students on a RAG assistant I shipped"),
        ("4", "hackathon wins"),
    ]
    colw = 1200 / 4
    for i, (num, label) in enumerate(items):
        x = 44 + i * colw
        d = f' style="animation-delay:{i * 0.12:.2f}s"'
        if i:
            s.add(
                f'<line x1="{i * colw}" y1="28" x2="{i * colw}" y2="122" stroke="{LINE}"/>'
            )
        s.text(x, 80, num, "serif", 54, BONE, cls="up", extra=d)
        s.add(
            f'<rect x="{x}" y="96" width="40" height="2" fill="{EMBER}" class="bar"'
            f' style="animation-delay:{0.3 + i * 0.12:.2f}s"/>'
        )
        s.text(x, 122, label.upper(), "mono", 11, MUTED, cls="up", extra=d)
    s.save("stats.svg")


def motif_android(s, x, y):
    s.style(
        "@keyframes bub{0%,8%{opacity:0;transform:translateY(6px)}14%,84%{opacity:1;transform:none}92%,100%{opacity:0}}"
        ".bub{animation:bub 6s ease-out infinite both}"
    )
    s.add(
        f'<rect x="{x + 62}" y="{y}" width="72" height="128" rx="14" fill="none" stroke="{MUTED}" stroke-width="1.5"/>'
    )
    s.add(
        f'<rect x="{x + 88}" y="{y + 8}" width="20" height="4" rx="2" fill="{LINE}"/>'
    )
    bubbles = [
        (70, 26, 40, LINE),
        (92, 46, 34, EMBER),
        (70, 66, 46, LINE),
        (96, 86, 30, EMBER),
    ]
    for i, (bx, by, bw, c) in enumerate(bubbles):
        s.add(
            f'<rect class="bub" style="animation-delay:{i * 0.9:.1f}s" x="{x + bx}" y="{y + by}" width="{bw}" '
            f'height="14" rx="7" fill="{c}"/>'
        )


def motif_gate(s, x, y):
    s.style(
        "@keyframes sweep{0%{transform:translateY(0)}70%,100%{transform:translateY(118px)}}"
        ".sweep{animation:sweep 4s cubic-bezier(.5,0,.5,1) infinite}"
        "@keyframes flag{0%,62%{opacity:0}66%,96%{opacity:1}100%{opacity:0}}.flag{animation:flag 4s infinite both}"
    )
    rows = [
        ("GET /invoices/{id}", "403"),
        ("GET /users/{id}", "404"),
        ("GET /files/{id}", "401"),
        ("GET /orders/{id}", "200"),
    ]
    for i, (ep, code) in enumerate(rows):
        yy = y + 18 + i * 30
        s.text(x, yy, ep, "mono", 11, MUTED)
        s.text(x + 196, yy, code, "mono", 11, MUTED, anchor="end")
    s.add(
        f'<g class="flag"><rect x="{x - 8}" y="{y + 92}" width="212" height="24" rx="6" fill="none" stroke="{EMBER}"/>'
    )
    s.text(x + 196, y + 132 + 8, "LEAK  ·  FAIL PR", "mono", 11, EMBER, anchor="end")
    s.add("</g>")
    s.add(
        f'<rect x="{x - 8}" y="{y}" width="212" height="1" fill="{EMBER}" opacity=".4" class="sweep"/>'
    )


def motif_resolve(s, x, y):
    s.style(
        "@keyframes seg{0%,5%{fill:"
        + LINE
        + "}10%,88%{fill:"
        + EMBER
        + "}96%,100%{fill:"
        + LINE
        + "}}"
        ".seg{animation:seg 7s infinite both}"
        "@keyframes rej{0%,55%{opacity:0}60%,88%{opacity:1}96%,100%{opacity:0}}.rej{animation:rej 7s infinite both}"
    )
    s.text(x, y + 14, "TOOL BUDGET", "mono", 11, MUTED)
    for i in range(10):
        cls = ' class="seg"' if i < 6 else ""
        delay = f' style="animation-delay:{i * 0.45:.2f}s"' if i < 6 else ""
        s.add(
            f'<rect{cls}{delay} x="{x + i * 20}" y="{y + 26}" width="15" height="26" rx="3" fill="{LINE}"/>'
        )
    s.text(x + 196, y + 72, "6 / 10", "mono", 11, MUTED, anchor="end")
    s.add('<g class="rej">')
    s.text(x, y + 104, "RED-TEAM PLANNER", "mono", 11, MUTED)
    s.text(x, y + 124, "7 attempts  ·  7 rejected", "mono", 11, EMBER)
    s.add("</g>")


def motif_unprompted(s, x, y):
    s.style(
        "@keyframes wave{0%,100%{transform:scaleY(.35)}50%{transform:scaleY(1)}}"
        ".wv{transform-box:fill-box;transform-origin:center;animation:wave 1.4s ease-in-out infinite}"
    )
    heights = [
        18,
        34,
        52,
        30,
        60,
        42,
        24,
        48,
        64,
        38,
        20,
        44,
        56,
        28,
        40,
        22,
        50,
        34,
        18,
        30,
    ]
    for i, h in enumerate(heights):
        c = EMBER if 7 <= i <= 12 else MUTED
        s.add(
            f'<rect class="wv" style="animation-delay:{(i * 0.13) % 1.4:.2f}s" x="{x + i * 10}" '
            f'y="{y + 46 - h / 2}" width="5" height="{h}" rx="2.5" fill="{c}"/>'
        )
    s.add(f'<path d="M{x + 66} {y + 86} v6 h58 v-6" fill="none" stroke="{EMBER}"/>')
    s.text(
        x + 95,
        y + 112,
        "00:14  \u201cI use it daily\u201d",
        "mono",
        11,
        BONE,
        anchor="middle",
    )


def motif_furprint(s, x, y):
    s.style(
        "@keyframes ring{0%,100%{opacity:.18}40%{opacity:1}}.ring{animation:ring 3s ease-in-out infinite both}"
    )
    cx, cy, r = x + 98, y + 62, 13

    def hexp(hx, hy):
        pts = " ".join(
            f"{hx + r * math.cos(math.radians(60 * k + 30)):.1f},{hy + r * math.sin(math.radians(60 * k + 30)):.1f}"
            for k in range(6)
        )
        return pts

    dirs = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

    def axial(q, rr):
        return cx + r * math.sqrt(3) * (q + rr / 2), cy + r * 1.5 * rr

    for ring in range(3):
        cells = [(0, 0)] if ring == 0 else []
        if ring:
            q, rr = -ring, ring
            for d in dirs:
                for _ in range(ring):
                    cells.append((q, rr))
                    q, rr = q + d[0], rr + d[1]
        for q, rr in cells:
            hx, hy = axial(q, rr)
            fill = EMBER if ring == 0 else "none"
            stroke = EMBER if ring == 1 else MUTED
            s.add(
                f'<polygon class="ring" style="animation-delay:{ring * 0.45:.2f}s" points="{hexp(hx, hy)}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
            )


def motif_mobile(s, x, y):
    s.style(
        "@keyframes tap{0%{transform:translate(0,0)}30%{transform:translate(28px,26px)}60%{transform:translate(0,52px)}"
        "100%{transform:translate(0,0)}}.tap{animation:tap 6s cubic-bezier(.6,0,.3,1) infinite}"
        "@keyframes rip{0%{r:3;opacity:1}100%{r:14;opacity:0}}.rip{animation:rip 1s ease-out infinite}"
    )
    s.add(
        f'<rect x="{x + 62}" y="{y}" width="72" height="128" rx="14" fill="none" stroke="{MUTED}" stroke-width="1.5"/>'
    )
    for row in range(3):
        for col in range(3):
            s.add(
                f'<rect x="{x + 72 + col * 19}" y="{y + 22 + row * 26}" width="13" height="13" rx="3" fill="{LINE}"/>'
            )
    s.add(
        f'<g class="tap"><circle cx="{x + 78.5}" cy="{y + 28.5}" r="4" fill="{EMBER}"/>'
        f'<circle class="rip" cx="{x + 78.5}" cy="{y + 28.5}" r="3" fill="none" stroke="{EMBER}"/></g>'
    )


PROJECTS = [
    (
        "devin-android",
        "KOTLIN  ·  JETPACK COMPOSE",
        "Native Android client for Devin (unofficial): sessions, chat, attachments and notifications with inline reply.",
        motif_android,
    ),
    (
        "marcus-gate",
        "PYTHON  ·  GITHUB ACTIONS",
        "Fails the PR when one tenant can read another tenant\u2019s data. Redacted evidence, agent-readable handoff.",
        motif_gate,
    ),
    (
        "resolve-",
        "FASTAPI  ·  OPENAI TOOL CALLING",
        "Accounts-payable agent with a tool budget, allow-listed tools, a red-team planner and a 40-case eval.",
        motif_resolve,
    ),
    (
        "unprompted",
        "PYTHON  ·  POSTGRES  ·  ORIANE",
        "Finds creators who mention a brand on camera, with quote, timestamp and frame as proof. 3rd at Replit x Oriane.",
        motif_unprompted,
    ),
    (
        "FurPrint",
        "FASTAPI  ·  POSTGIS  ·  H3  ·  REACT",
        "Lost-cat search parties, with search zones from a study of 1,210 missing cats.",
        motif_furprint,
    ),
    (
        "mobile-use",
        "OPEN SOURCE  ·  PYTHON",
        "Upstream PRs to Minitap\u2019s agent framework for real Android and iOS apps: strict app lock, Poco for games.",
        motif_mobile,
    ),
]


def card(i, name, tags, desc, motif):
    s = Svg(600, 340, f"{name}: {desc}")
    s.style(COMMON)
    frame(s, fill=CARD)
    s.text(32, 50, f"{i + 1:02d}", "mono", 13, EMBER)
    s.text(64, 50, tags, "mono", 13, MUTED)
    motif(s, 372, 34)
    s.text(30, 222, name, "serif", 54, BONE)
    for j, line in enumerate(wrap(desc, "sans", 19, 536)[:3]):
        s.text(32, 260 + j * 27, line, "sans", 19, MUTED)
    s.save(f"card-{name.lower().rstrip('-')}.svg")


def principles():
    s = Svg(
        1200,
        210,
        "How I build agents: the model proposes, code decides, a human approves anything with side effects",
    )
    period = 6
    s.style(
        COMMON
        + "@keyframes travel{0%{transform:translateX(0)}100%{transform:translateX(800px)}}"
        f".dot{{animation:travel {period}s cubic-bezier(.45,0,.55,1) infinite}}"
        "@keyframes lit{0%,100%{stroke:" + LINE + "}8%,30%{stroke:" + EMBER + "}}"
        f".node{{animation:lit {period}s infinite both}}"
    )
    frame(s)
    s.text(44, 50, "HOW I BUILD AGENTS", "mono", 12, MUTED)
    nodes = [
        ("The model proposes", "LLM  ·  TOOL CALLS"),
        ("Code decides", "GROUNDING  ·  POLICY  ·  EVALS"),
        ("A human approves", "ANYTHING WITH SIDE EFFECTS"),
    ]
    xs = [200, 600, 1000]
    s.add(
        f'<line x1="{xs[0]}" y1="104" x2="{xs[-1]}" y2="104" stroke="{LINE}" stroke-dasharray="3 5"/>'
    )
    for k, (x, (title, sub)) in enumerate(zip(xs, nodes)):
        s.add(
            f'<circle class="node" style="animation-delay:{k * period / 2.2:.2f}s" cx="{x}" cy="104" r="11" '
            f'fill="{BG}" stroke="{LINE}" stroke-width="2"/>'
        )
        s.add(f'<circle cx="{x}" cy="104" r="3" fill="{MUTED}"/>')
        s.text(x, 154, title, "serif", 30, BONE, anchor="middle")
        s.text(x, 182, sub, "mono", 11, MUTED, anchor="middle")
    s.add(f'<circle class="dot" cx="{xs[0]}" cy="104" r="5" fill="{EMBER}"/>')
    s.save("principles.svg")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    hero()
    stats()
    for i, p in enumerate(PROJECTS):
        card(i, *p)
    principles()
