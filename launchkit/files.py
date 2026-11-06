"""Buyer-facing files: planner PDFs in 4 variants, quick start guide, free sampler."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import white
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from planner.build import build
from planner.core import LIGHT, MED, REG, SEMI, SERIF, SERIF_I, register_fonts
from planner.niches import ALL

YEAR = 2027
VARIANTS = [
    ("letter", "sun", "US Letter - Sunday start"),
    ("letter", "mon", "US Letter - Monday start"),
    ("a4", "mon", "A4 - Monday start"),
    ("a4", "sun", "A4 - Sunday start"),
]


def planner_filename(niche, label) -> str:
    return f"{niche.title} {YEAR} ({label}).pdf"


def build_planners(out_dir: Path, slug: str) -> list[Path]:
    niche = ALL[slug]
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for size, ws, label in VARIANTS:
        path = out_dir / planner_filename(niche, label)
        build(niche, YEAR, str(path), size, ws)
        paths.append(path)
    return paths


# --------------------------------------------------------------------------
# Small reportlab helpers for the guide & sampler pages
# --------------------------------------------------------------------------


class Doc:
    def __init__(self, path, theme):
        register_fonts()
        self.c = canvas.Canvas(str(path), pagesize=letter)
        self.W, self.H = letter
        self.t = theme
        self.x0, self.x1 = 56, self.W - 56

    def text(self, x, y, s, font=REG, size=10, color=None, align="left"):
        self.c.setFont(font, size)
        self.c.setFillColor(color if color is not None else self.t.ink)
        {"left": self.c.drawString, "center": self.c.drawCentredString, "right": self.c.drawRightString}[align](x, y, s)

    def wrap(self, s, font, size, maxw):
        from reportlab.pdfbase.pdfmetrics import stringWidth
        out, cur = [], ""
        for w in s.split():
            t = f"{cur} {w}".strip()
            if stringWidth(t, font, size) <= maxw:
                cur = t
            else:
                out.append(cur)
                cur = w
        if cur:
            out.append(cur)
        return out

    def para(self, x, y, s, maxw, font=REG, size=10, color=None, lead=1.5):
        for ln in self.wrap(s, font, size, maxw):
            self.text(x, y, ln, font, size, color)
            y -= size * lead
        return y

    def band(self, h=150):
        c = self.c
        c.setFillColor(self.t.primary)
        c.rect(0, self.H - h, self.W, h, stroke=0, fill=1)
        c.setFillColor(self.t.accent)
        c.circle(self.W - 50, self.H - 20, 70, stroke=0, fill=1)

    def section(self, y, title):
        self.text(self.x0, y, title.upper(), SEMI, 8.5, self.t.accent)
        self.c.setStrokeColor(self.t.line)
        self.c.setLineWidth(0.8)
        self.c.line(self.x0, y - 6, self.x1, y - 6)
        return y - 24

    def bullets(self, y, items, maxw=None, size=9.6):
        maxw = maxw or (self.x1 - self.x0 - 16)
        for it in items:
            self.c.setFillColor(self.t.accent)
            self.c.circle(self.x0 + 4, y + 3.2, 2.2, stroke=0, fill=1)
            if ": " in it:
                head, rest = it.split(": ", 1)
                from reportlab.pdfbase.pdfmetrics import stringWidth
                self.text(self.x0 + 14, y, head + ":", SEMI, size, self.t.primary)
                hw = stringWidth(head + ": ", SEMI, size)
                lines = self.wrap(rest, REG, size, maxw - hw)
                first = lines[0] if lines else ""
                self.text(self.x0 + 14 + hw, y, first, REG, size)
                rest_text = " ".join(lines[1:])
                y -= size * 1.5
                if rest_text:
                    y = self.para(self.x0 + 14, y, rest_text, maxw, REG, size)
            else:
                y = self.para(self.x0 + 14, y, it, maxw, REG, size)
            y -= 5
        return y

    def footer(self, s):
        self.text(self.W / 2, 30, s, LIGHT, 8, self.t.muted, "center")

    def show(self):
        self.c.showPage()

    def save(self):
        self.c.save()


def quick_start(out: Path, slug: str) -> Path:
    n = ALL[slug]
    d = Doc(out, n.theme)
    c = d.c
    d.c.setTitle(f"{n.title} {YEAR} - Quick Start Guide")

    # page 1
    d.band()
    d.text(d.x0, d.H - 58, "QUICK START GUIDE", SEMI, 9, white)
    d.text(d.x0, d.H - 100, f"Welcome to your {n.title}", SERIF, 26, white)
    d.text(d.x0, d.H - 124, n.tagline, SERIF_I, 13, n.theme.soft)
    y = d.H - 186
    y = d.para(d.x0, y, ("Thank you for your purchase! This page takes two minutes to read and covers which file to "
                         "pick, how to use it on a tablet or print it, and a few tips to get the most out of it."),
               d.x1 - d.x0, LIGHT, 10.5, lead=1.55) - 14

    y = d.section(y, "1. Pick your file")
    y = d.para(d.x0, y, "You get the same planner in four versions. Use whichever fits you; they are all included.",
               d.x1 - d.x0, REG, 9.6) - 6
    y = d.bullets(y, [f"{label}: {planner_filename(n, label)}" for _, _, label in VARIANTS], size=8.8)
    y = d.para(d.x0, y, "Not sure? In the US or Canada pick US Letter. Everywhere else pick A4. "
                        "Sunday or Monday start is personal preference.", d.x1 - d.x0, LIGHT, 9.2) - 14

    y = d.section(y, "2. Use it digitally (iPad, Android tablet, computer)")
    y = d.bullets(y, [
        "GoodNotes: tap + then Import, choose the PDF and import it as a new notebook.",
        "Notability: tap Import, choose the PDF and it opens as a new note.",
        "Noteshelf, Xodo, Samsung Notes, Adobe Acrobat: open the PDF directly.",
        "Links: tap the tabs on the right edge to jump to any month. Tap a date on a monthly calendar to open its week. "
        "Every page has a Back to Index link. In GoodNotes, if a link does not respond, switch to Read-only mode or tap with your finger.",
        "Need more pages? Duplicate any tracker or notes page from your app's page menu.",
    ])
    y -= 8
    y = d.section(y, "3. Print it")
    d.bullets(y, [
        "Print at Actual size / 100% (not Fit to page) on the paper size you picked.",
        "Print only the months you need, or the whole year at once. Single- or double-sided both work.",
        "Hole-punch for a binder or disc-bound system, or have a print shop spiral-bind it.",
    ])
    d.footer(f"{n.title} {YEAR}  ·  Quick Start Guide  ·  page 1 of 2")
    d.show()

    # page 2
    y = d.H - 70
    d.text(d.x0, y, "Get the most out of it", SERIF, 24, n.theme.primary)
    y -= 36
    y = d.section(y, "A simple routine")
    y = d.bullets(y, [
        "Once now: fill in the year pages (vision, goals, targets). Ten honest minutes here steers the whole year.",
        "Once a month: set up the monthly calendar and the two planning pages, then review last month.",
        "Once a week: plan the week page on Sunday or Monday. Keep it light so you actually come back to it.",
        "Anytime: use the trackers at the back. They are undated, so print or duplicate as many as you need.",
    ])
    y -= 8
    y = d.section(y, "What's inside")
    y = d.bullets(y, [f"{f}" for f in n.features] + [
        "Dated January to December 2027, with clickable tabs and PDF bookmarks.",
    ])
    y -= 8
    y = d.section(y, "Your license")
    y = d.para(d.x0, y, ("This planner is for your personal use. You can print it and use it on as many of your own "
                         "devices as you like. Please do not share, resell or redistribute the files, digitally or in print. "
                         "Buying for a team or a client? Get in touch for a multi-user license."),
               d.x1 - d.x0, REG, 9.6) - 14
    y = d.section(y, "Need help?")
    d.para(d.x0, y, ("Reply to your Gumroad receipt email and I will help you out. If you love the planner, a quick rating "
                     "on Gumroad really helps a small shop. Thank you!"), d.x1 - d.x0, REG, 9.6)
    d.footer(f"{n.title} {YEAR}  ·  Quick Start Guide  ·  page 2 of 2")
    d.show()
    d.save()
    return out


# --------------------------------------------------------------------------
# Free sampler (lead magnet)
# --------------------------------------------------------------------------


def structural_pages(niche) -> dict:
    ny = len(niche.year_pages)
    jan = 3 + ny
    return {"cover": 0, "index": 1, "year": 2, "year_pages": list(range(3, 3 + ny)), "jan": jan,
            "month_pages": [jan + 1, jan + 2], "week1": jan + 3, "week2": jan + 4}


def sampler(out: Path, letter_pdfs: dict[str, Path]) -> Path:
    from planner.core import Theme

    theme = Theme(primary="#2B2A33", accent="#D9963F", soft="#F4EFE8", line="#E4DDD3")
    tmp_front = out.with_suffix(".front.pdf")
    tmp_back = out.with_suffix(".back.pdf")

    d = Doc(tmp_front, theme)
    d.c.setFillColor(theme.soft)
    d.c.rect(0, 0, d.W, d.H, stroke=0, fill=1)
    d.band(330)
    d.text(d.x0, d.H - 70, "FREE SAMPLER", SEMI, 10, theme.accent)
    d.text(d.x0 - 4, d.H - 230, str(YEAR), SERIF, 150, white)
    d.text(d.x0, d.H - 290, "Five planners. Find the one that fits you.", SERIF_I, 18, theme.soft)
    y = d.H - 390
    d.text(d.x0, y, "Try January from every planner", SERIF, 26, theme.primary)
    y -= 34
    y = d.para(d.x0, y, ("Each planner is made for one kind of person instead of everyone. This sampler has real "
                         "pages from all five: the cover, the January calendar, one planning page made for that group and a "
                         "weekly page. Print them or use them in your favorite notes app."),
               d.x1 - d.x0, LIGHT, 10.5, lead=1.55) - 16
    for slug, n in ALL.items():
        d.c.setFillColor(n.theme.primary)
        d.c.roundRect(d.x0, y - 30, d.x1 - d.x0, 34, 6, stroke=0, fill=1)
        d.text(d.x0 + 14, y - 17, n.title, SEMI, 11, white)
        d.text(d.x1 - 14, y - 17, n.audience, LIGHT, 9, n.theme.soft, "right")
        y -= 42
    d.footer("Sample pages only. Links are turned off in this sampler; the full planners are fully hyperlinked.")
    d.show()
    d.save()

    d = Doc(tmp_back, theme)
    d.band(150)
    d.text(d.x0, d.H - 96, "Liked what you saw?", SERIF, 30, white)
    y = d.H - 200
    y = d.para(d.x0, y, "The full planners are dated for all of 2027 and include:", d.x1 - d.x0, REG, 11) - 10
    y = d.bullets(y, [
        "Around 105 to 111 pages each, January to December 2027",
        "Clickable tabs to every month, week pages linked from every calendar, PDF bookmarks",
        "Year planning pages, two monthly pages and a weekly page made for your niche",
        "Trackers, logs and undated tools you can duplicate or reprint",
        "4 versions in every download: US Letter or A4, Sunday or Monday start",
        "A quick start guide for GoodNotes, Notability and printing",
    ], size=10.5)
    y -= 16
    d.text(d.x0, y, "Get yours from the same Gumroad store where you downloaded this sampler.", SEMI, 11, theme.primary)
    y -= 20
    d.para(d.x0, y, "Tip: the bundle includes all five planners for less than the price of three.", d.x1 - d.x0, LIGHT, 10.5)
    d.footer("Personal use only. Please do not resell or redistribute.")
    d.show()
    d.save()

    w = PdfWriter()
    for page in PdfReader(tmp_front).pages:
        w.add_page(page)
    for slug in ALL:
        r = PdfReader(letter_pdfs[slug])
        sp = structural_pages(ALL[slug])
        for i in [sp["cover"], sp["jan"], sp["month_pages"][0], sp["week2"]]:
            page = r.pages[i]
            if "/Annots" in page:
                del page["/Annots"]
            w.add_page(page)
    for page in PdfReader(tmp_back).pages:
        w.add_page(page)
    w.add_metadata({"/Title": f"Free {YEAR} Planner Sampler"})
    with open(out, "wb") as f:
        w.write(f)
    tmp_front.unlink()
    tmp_back.unlink()
    return out
