"""Drawing engine for the niche planners.

Everything is drawn with ReportLab. Pages are described declaratively with
``Box`` / ``Row`` / ``Cols`` specs (see ``niches.py``) and rendered by
``Planner.render``. Every page gets clickable side tabs, PDF bookmarks and a
footer link back to the index, so the same file works printed or in a
note-taking app (GoodNotes, Notability, Xodo, ...).
"""

from __future__ import annotations

import calendar
import datetime as dt
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Sequence, Union

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"

SERIF = "DMSerif"
SERIF_I = "DMSerif-Italic"
LIGHT = "Poppins-Light"
REG = "Poppins"
MED = "Poppins-Medium"
SEMI = "Poppins-SemiBold"

_FONTS = {
    SERIF: "DMSerifDisplay-Regular.ttf",
    SERIF_I: "DMSerifDisplay-Italic.ttf",
    LIGHT: "Poppins-Light.ttf",
    REG: "Poppins-Regular.ttf",
    MED: "Poppins-Medium.ttf",
    SEMI: "Poppins-SemiBold.ttf",
}


def register_fonts() -> None:
    for name, file in _FONTS.items():
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / file)))


PAGE_SIZES = {"letter": letter, "a4": A4}
MONTHS = [calendar.month_name[i] for i in range(1, 13)]
MON_ABBR = [calendar.month_abbr[i].upper() for i in range(1, 13)]


# --------------------------------------------------------------------------
# Specs
# --------------------------------------------------------------------------


@dataclass
class Theme:
    primary: str
    accent: str
    soft: str
    line: str
    ink: str = "#2A2A2A"
    muted: str = "#8C8C8C"

    def __post_init__(self):
        for k in ("primary", "accent", "soft", "line", "ink", "muted"):
            setattr(self, k, HexColor(getattr(self, k)))


@dataclass
class Box:
    """A titled panel. ``kind`` picks what is drawn inside it.

    kinds: lines, checks, numbered, dots, blank, table, habit, circles,
    fields, schedule
    """

    title: str = ""
    kind: str = "lines"
    weight: float = 1.0  # vertical share inside a stack
    w: float = 1.0  # horizontal share inside a Row
    hint: str = ""
    opts: dict = field(default_factory=dict)

    def __init__(self, title="", kind="lines", weight=1.0, w=1.0, hint="", **opts):
        self.title, self.kind, self.weight, self.w, self.hint = title, kind, weight, w, hint
        self.opts = opts


@dataclass
class Row:
    boxes: list
    weight: float = 1.0


@dataclass
class Cols:
    stacks: list  # list of stacks (each a list of Box/Row)
    weights: Sequence[float] | None = None


Body = Union[list, Cols]


@dataclass
class PageSpec:
    title: str
    body: Body
    right: str = ""
    copies: int = 1


# --------------------------------------------------------------------------
# Calendar helpers
# --------------------------------------------------------------------------


def week_start(d: dt.date, first_weekday: int) -> dt.date:
    return d - dt.timedelta(days=(d.weekday() - first_weekday) % 7)


def planner_weeks(year: int, first_weekday: int) -> list[dt.date]:
    """Start dates of every week touching ``year``."""
    start = week_start(dt.date(year, 1, 1), first_weekday)
    end = dt.date(year, 12, 31)
    weeks = []
    while start <= end:
        weeks.append(start)
        start += dt.timedelta(days=7)
    return weeks


def week_key(start: dt.date) -> str:
    return f"w{start.isoformat()}"


def weekday_labels(first_weekday: int, n: int = 3) -> list[str]:
    return [calendar.day_abbr[(first_weekday + i) % 7][:n].upper() for i in range(7)]


# --------------------------------------------------------------------------
# Planner
# --------------------------------------------------------------------------


class Planner:
    TAB_LABELS = ["INDEX", "YEAR"] + MON_ABBR

    def __init__(self, path: str, niche, year: int, size: str = "letter", week_starts: str = "sun"):
        register_fonts()
        self.niche = niche
        self.t: Theme = niche.theme
        self.year = year
        self.pagesize = PAGE_SIZES[size]
        self.W, self.H = self.pagesize
        self.fwd = 6 if week_starts == "sun" else 0
        self.cal = calendar.Calendar(firstweekday=self.fwd)
        self.weeks = planner_weeks(year, self.fwd)
        self.c = canvas.Canvas(path, pagesize=self.pagesize)
        self.c.setTitle(f"{niche.title} {year}")
        self.c.setAuthor(niche.title)
        self.c.setSubject(niche.tagline)
        self.c.setCreator("niche-planners")

        # geometry
        self.tab_x1 = self.W - 14
        self.tab_x0 = self.tab_x1 - 24
        self.x0 = 40
        self.x1 = self.tab_x0 - 16
        self.top = self.H - 40
        self.bottom = 46
        self._outline_level = 0

    # ------------------------------------------------------------- primitives
    @property
    def cw(self):
        return self.x1 - self.x0

    def font(self, name, size, color=None):
        self.c.setFont(name, size)
        self.c.setFillColor(color if color is not None else self.t.ink)

    def text(self, x, y, s, font=REG, size=9, color=None, align="left", space=0.0):
        self.font(font, size, color)
        if space:
            w = pdfmetrics.stringWidth(s, font, size) + space * (len(s) - 1)
            if align == "center":
                x -= w / 2
            elif align == "right":
                x -= w
            to = self.c.beginText(x, y)
            to.setFont(font, size)
            to.setCharSpace(space)
            to.textOut(s)
            to.setCharSpace(0)
            self.c.drawText(to)
            return
        if align == "center":
            self.c.drawCentredString(x, y, s)
        elif align == "right":
            self.c.drawRightString(x, y, s)
        else:
            self.c.drawString(x, y, s)

    @staticmethod
    def sw(s, font, size, space=0.0):
        return pdfmetrics.stringWidth(s, font, size) + space * max(len(s) - 1, 0)

    def fit(self, s, font, size, maxw, min_size=5.0):
        while size > min_size and self.sw(s, font, size) > maxw:
            size -= 0.25
        return size

    def wrap(self, s, font, size, maxw):
        words, lines, cur = s.split(), [], ""
        for wd in words:
            trial = f"{cur} {wd}".strip()
            if self.sw(trial, font, size) <= maxw:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def hline(self, x0, x1, y, color=None, width=0.5, dash=None):
        c = self.c
        c.setStrokeColor(color if color is not None else self.t.line)
        c.setLineWidth(width)
        c.setDash(*(dash or ()))
        c.line(x0, y, x1, y)
        c.setDash()

    def vline(self, x, y0, y1, color=None, width=0.5):
        c = self.c
        c.setStrokeColor(color if color is not None else self.t.line)
        c.setLineWidth(width)
        c.line(x, y0, x, y1)

    def rrect(self, x, y, w, h, r=6, stroke=None, fill=None, width=0.6):
        c = self.c
        c.setLineWidth(width)
        if stroke is not None:
            c.setStrokeColor(stroke)
        if fill is not None:
            c.setFillColor(fill)
        c.roundRect(x, y, w, h, r, stroke=1 if stroke is not None else 0, fill=1 if fill is not None else 0)

    def checkbox(self, x, y, s=7):
        self.rrect(x, y, s, s, r=1.5, stroke=self.t.primary, width=0.6)

    def circle(self, x, y, r, stroke=None, fill=None, width=0.6):
        c = self.c
        c.setLineWidth(width)
        if stroke is not None:
            c.setStrokeColor(stroke)
        if fill is not None:
            c.setFillColor(fill)
        c.circle(x, y, r, stroke=1 if stroke is not None else 0, fill=1 if fill is not None else 0)

    def link(self, key, x0, y0, x1, y1):
        self.c.linkRect("", key, (x0, y0, x1, y1), relative=0, thickness=0)

    # ------------------------------------------------------------- page frame
    @contextmanager
    def page(self, key=None, tab=None, outline=None, level=None, tabs=True):
        c = self.c
        if key:
            c.bookmarkPage(key)
            if outline:
                lvl = 0 if level is None else level
                lvl = min(lvl, self._outline_level + 1)
                c.addOutlineEntry(outline, key, level=lvl, closed=lvl == 0)
                self._outline_level = lvl
        yield
        if tabs:
            self.draw_tabs(tab)
            self.footer()
        c.showPage()

    def draw_tabs(self, active):
        labels = self.TAB_LABELS + [self.niche.tracker_tab]
        keys = ["index", "year"] + [f"m{i}" for i in range(1, 13)] + ["trackers"]
        n = len(labels)
        gap = 3
        y_top, y_bot = self.H - 36, 36
        th = (y_top - y_bot - gap * (n - 1)) / n
        for i, (lab, key) in enumerate(zip(labels, keys)):
            y1 = y_top - i * (th + gap)
            y0 = y1 - th
            on = lab == active
            fill = self.t.primary if on else self.t.soft
            self.rrect(self.tab_x0, y0, self.tab_x1 - self.tab_x0, th, r=4, fill=fill)
            c = self.c
            c.saveState()
            cx, cy = (self.tab_x0 + self.tab_x1) / 2, (y0 + y1) / 2
            c.translate(cx, cy)
            c.rotate(90)
            size = self.fit(lab, SEMI, 6.4, th - 8, 4.5)
            self.text(0, -size * 0.35, lab, SEMI, size, white if on else self.t.primary, "center", 0.6)
            c.restoreState()
            self.link(key, self.tab_x0, y0, self.tab_x1, y1)

    def footer(self):
        y = 24
        self.text(self.x0, y, f"{self.niche.title.upper()}  ·  {self.year}", SEMI, 6, self.t.muted, space=0.8)
        lab = "BACK TO INDEX"
        self.text(self.x1, y, lab, SEMI, 6, self.t.primary, "right", 0.8)
        w = self.sw(lab, SEMI, 6, 0.8)
        self.link("index", self.x1 - w - 4, y - 4, self.x1 + 2, y + 9)

    def header(self, title, right="", kicker=None):
        kicker = kicker or f"{self.niche.title}  ·  {self.year}".upper()
        self.text(self.x0, self.top, kicker, SEMI, 7, self.t.accent, space=1.2)
        size = self.fit(title, SERIF, 27, self.cw - (self.sw(right, LIGHT, 9) + 20 if right else 0), 16)
        self.text(self.x0, self.top - 30, title, SERIF, size, self.t.primary)
        if right:
            self.text(self.x1, self.top - 28, right, LIGHT, 9, self.t.muted, "right")
        y = self.top - 42
        self.hline(self.x0, self.x1, y, self.t.line, 0.7)
        self.hline(self.x0, self.x0 + 44, y, self.t.accent, 2)
        return y - 14

    # ------------------------------------------------------------- layouts
    def render(self, body: Body, x, y_top, w, h, ctx=None, gap=10):
        if isinstance(body, Cols):
            weights = body.weights or [1] * len(body.stacks)
            tot = sum(weights)
            avail = w - gap * (len(body.stacks) - 1)
            cx = x
            for stack, wt in zip(body.stacks, weights):
                cw = avail * wt / tot
                self.stack(stack, cx, y_top, cw, h, ctx, gap)
                cx += cw + gap
        else:
            self.stack(body, x, y_top, w, h, ctx, gap)

    def stack(self, items, x, y_top, w, h, ctx=None, gap=10):
        tot = sum(it.weight for it in items)
        avail = h - gap * (len(items) - 1)
        y = y_top
        for it in items:
            ih = avail * it.weight / tot
            if isinstance(it, Row):
                wt = sum(b.w for b in it.boxes)
                aw = w - gap * (len(it.boxes) - 1)
                bx = x
                for b in it.boxes:
                    bw = aw * b.w / wt
                    self.box(b, bx, y, bw, ih, ctx)
                    bx += bw + gap
            elif isinstance(it, Cols):
                self.render(it, x, y, w, ih, ctx, gap)
            else:
                self.box(it, x, y, w, ih, ctx)
            y -= ih + gap

    def box(self, b: Box, x, y_top, w, h, ctx=None):
        ctx = ctx or {}
        y0 = y_top - h
        if b.opts.get("frame", True):
            self.rrect(x, y0, w, h, r=7, stroke=self.t.line, width=0.8)
        inner_top = y_top - 8
        if b.title:
            size = self.fit(b.title.upper(), SEMI, 7.2, w - 20, 5.5)
            self.text(x + 10, y_top - 15, b.title.upper(), SEMI, size, self.t.primary, space=0.9)
            if b.hint:
                hx = x + 10 + self.sw(b.title.upper(), SEMI, size, 0.9) + 8
                hs = self.fit(b.hint, LIGHT, 7, x + w - 10 - hx, 4.5)
                if hx < x + w - 30:
                    self.text(hx, y_top - 15, b.hint, LIGHT, hs, self.t.muted)
            inner_top = y_top - 24
        ix0, ix1, iy0 = x + 10, x + w - 10, y0 + 8
        draw = getattr(self, f"k_{b.kind}")
        draw(b, ix0, ix1, inner_top, iy0, ctx)

    # ------------------------------------------------------------- box kinds
    def k_blank(self, b, x0, x1, top, bot, ctx):
        pass

    def k_lines(self, b, x0, x1, top, bot, ctx):
        sp = b.opts.get("sp", 18)
        y = top - sp
        while y >= bot:
            self.hline(x0, x1, y)
            y -= sp

    def k_dots(self, b, x0, x1, top, bot, ctx):
        sp = b.opts.get("sp", 14)
        c = self.c
        c.setFillColor(self.t.line)
        nx = int((x1 - x0) // sp)
        ox = x0 + ((x1 - x0) - nx * sp) / 2
        y = top - sp / 2
        while y >= bot:
            for i in range(nx + 1):
                c.circle(ox + i * sp, y, 0.75, stroke=0, fill=1)
            y -= sp

    def k_checks(self, b, x0, x1, top, bot, ctx):
        sp = b.opts.get("sp", 18)
        items = b.opts.get("items", [])
        y = top - sp
        i = 0
        while y >= bot:
            self.checkbox(x0, y + 1.5)
            self.hline(x0 + 13, x1, y)
            if i < len(items):
                self.text(x0 + 15, y + 3, items[i], REG, 7.8)
            i += 1
            y -= sp

    def k_numbered(self, b, x0, x1, top, bot, ctx):
        n = b.opts.get("n")
        if n:
            sp = min((top - bot) / n, 26)
        else:
            sp = b.opts.get("sp", 18)
            n = int((top - bot) // sp)
        for i in range(n):
            y = top - sp * (i + 1)
            self.text(x0, y + 3, f"{i + 1:02d}", SEMI, 7.5, self.t.accent)
            self.hline(x0 + 16, x1, y)

    def k_fields(self, b, x0, x1, top, bot, ctx):
        labels = b.opts["labels"]
        sp = min((top - bot) / len(labels), 26)
        for i, lab in enumerate(labels):
            y = top - sp * (i + 1) + 2
            self.text(x0, y + 3, lab.upper(), SEMI, 6.6, self.t.muted, space=0.6)
            lx = x0 + self.sw(lab.upper(), SEMI, 6.6, 0.6) + 6
            self.hline(lx, x1, y)

    def k_circles(self, b, x0, x1, top, bot, ctx):
        labels = b.opts["labels"]
        if labels == "@weekdays":
            labels = [d.title() for d in weekday_labels(self.fwd, 3)]
        n = b.opts.get("n", 5)
        sp = min((top - bot) / len(labels), 24)
        r = min(4.2, sp * 0.28)
        span = (x1 - x0) * 0.55
        step = min(span / n, 18)
        for i, lab in enumerate(labels):
            y = top - sp * (i + 0.5)
            size = self.fit(lab, REG, 7.8, x1 - x0 - step * n - 8, 5)
            self.text(x0, y - 2.7, lab, REG, size)
            for j in range(n):
                cx = x1 - r - (n - 1 - j) * step
                self.circle(cx, y, r, stroke=self.t.primary)
            if i < len(labels) - 1:
                self.hline(x0, x1, y - sp / 2, self.t.line, 0.3, (1, 2))

    def k_schedule(self, b, x0, x1, top, bot, ctx):
        h0, h1 = b.opts.get("hours", (6, 22))
        n = h1 - h0 + 1
        sp = (top - bot) / n
        for i in range(n):
            hr = h0 + i
            y = top - sp * i
            lab = f"{(hr - 1) % 12 + 1}{'a' if hr % 24 < 12 else 'p'}"
            self.text(x0, y - 9, lab, SEMI, 6.8, self.t.accent)
            self.hline(x0 + 20, x1, y - sp, self.t.line, 0.5)
            if sp > 14:
                self.hline(x0 + 20, x1, y - sp / 2, self.t.line, 0.3, (1, 2))

    def k_table(self, b, x0, x1, top, bot, ctx):
        cols = []
        for lab, cw in b.opts["cols"]:
            if lab == "@weekdays":
                cols += [(d, cw) for d in weekday_labels(self.fwd, 3)]
            else:
                cols.append((lab, cw))
        rowlabels = b.opts.get("rowlabels")
        if rowlabels == "@weekdays":
            rowlabels = [d.title() for d in weekday_labels(self.fwd, 3)]
        checks = set(b.opts.get("checks", ()))
        hh = 16
        tot = sum(cw for _, cw in cols)
        widths = [(x1 - x0) * cw / tot for _, cw in cols]
        # header
        self.rrect(x0, top - hh, x1 - x0, hh, r=3, fill=self.t.soft)
        cx = x0
        for (lab, _), cw in zip(cols, widths):
            size = self.fit(lab.upper(), SEMI, 6.5, cw - 6, 4.5)
            self.text(cx + cw / 2, top - hh + 5.3, lab.upper(), SEMI, size, self.t.primary, "center", 0.4)
            cx += cw
        body_top = top - hh
        if rowlabels:
            n = len(rowlabels)
            rh = min((body_top - bot) / n, b.opts.get("max_row", 64))
        else:
            rh = b.opts.get("row_h", 18)
            n = int((body_top - bot) // rh)
        for r in range(n):
            y = body_top - rh * (r + 1)
            last = r == n - 1
            self.hline(x0, x1, y, self.t.line, 0.6 if not last else 0.8)
            if rowlabels:
                lab = rowlabels[r]
                bold = lab.upper() in ("TOTAL", "TOTALS")
                size = self.fit(lab, SEMI if bold else MED, 7.4, widths[0] - 8, 5)
                self.text(x0 + 4, y + rh / 2 - 2.6, lab, SEMI if bold else MED, size, self.t.primary if bold else self.t.ink)
            for ci in checks:
                ccx = x0 + sum(widths[:ci]) + widths[ci] / 2
                self.checkbox(ccx - 3.5, y + rh / 2 - 3.5)
        y_end = body_top - rh * n
        cx = x0
        for cw in widths[:-1]:
            cx += cw
            self.vline(cx, y_end, body_top, self.t.line, 0.5)

    def k_habit(self, b, x0, x1, top, bot, ctx):
        year, month = ctx["year"], ctx["month"]
        days = calendar.monthrange(year, month)[1]
        labels = list(b.opts.get("labels", []))
        rows = max(len(labels), b.opts.get("rows", len(labels)))
        labels += [""] * (rows - len(labels))
        lw = b.opts.get("label_w", 78)
        cw = (x1 - x0 - lw) / days
        hh = 20
        rh = min((top - hh - bot) / rows, 30)
        # header
        for d in range(1, days + 1):
            date = dt.date(year, month, d)
            cx = x0 + lw + cw * (d - 1)
            weekend = date.weekday() >= 5
            if weekend:
                self.c.setFillColor(self.t.soft)
                self.c.rect(cx, top - hh - rh * rows, cw, hh + rh * rows, stroke=0, fill=1)
            self.text(cx + cw / 2, top - 8, calendar.day_abbr[date.weekday()][0], SEMI, 5.2, self.t.muted, "center")
            self.text(cx + cw / 2, top - 16.5, str(d), SEMI, 6, self.t.primary, "center")
        y = top - hh
        self.hline(x0, x1, y, self.t.primary, 0.6)
        for i, lab in enumerate(labels):
            yy = y - rh * (i + 1)
            if lab:
                size = self.fit(lab, MED, 7.2, lw - 6, 5)
                self.text(x0, yy + rh / 2 - 2.5, lab, MED, size)
            self.hline(x0, x1, yy, self.t.line, 0.5)
        for d in range(days + 1):
            cx = x0 + lw + cw * d
            self.vline(cx, y - rh * rows, y, self.t.line, 0.4)

    # ------------------------------------------------------------- composites
    def mini_month(self, x, y_top, w, month, link=True, title_size=10, highlight_week=None):
        """Small month calendar; returns height used."""
        year = self.year
        self.text(x, y_top - title_size, MONTHS[month - 1], SERIF, title_size, self.t.primary)
        if link:
            self.link(f"m{month}", x, y_top - title_size - 3, x + w, y_top + 2)
        cw = w / 7
        rh = cw * 0.78
        y = y_top - title_size - 12
        for i, lab in enumerate(weekday_labels(self.fwd, 1)):
            self.text(x + cw * (i + 0.5), y, lab, SEMI, 5.6, self.t.accent, "center")
        weeks = self.cal.monthdatescalendar(year, month)
        for r, wk in enumerate(weeks):
            yy = y - rh * (r + 1)
            if highlight_week and wk[0] == highlight_week:
                self.rrect(x, yy - rh * 0.3, w, rh, r=3, fill=self.t.soft)
            for i, d in enumerate(wk):
                if d.month != month:
                    continue
                self.text(x + cw * (i + 0.5), yy, str(d.day), REG, 6.4, self.t.ink, "center")
            if link:
                self.link(week_key(wk[0]), x, yy - rh * 0.3, x + w, yy + rh * 0.7)
        return title_size + 12 + rh * 6

    def paragraph(self, x, y, s, maxw, font=REG, size=8.5, color=None, lead=1.45):
        for ln in self.wrap(s, font, size, maxw):
            self.text(x, y, ln, font, size, color)
            y -= size * lead
        return y

    def save(self):
        self.c.save()
