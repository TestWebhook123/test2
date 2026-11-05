"""Assemble a full planner PDF for one niche."""

from __future__ import annotations

import calendar
import datetime as dt

from reportlab.lib.colors import white

from .core import (LIGHT, MED, MON_ABBR, MONTHS, REG, SEMI, SERIF, SERIF_I, Box, Cols, PageSpec, Planner, week_key,
                   weekday_labels)


# --------------------------------------------------------------------------
# Shared pages
# --------------------------------------------------------------------------


def cover(p: Planner):
    t, c, W, H = p.t, p.c, p.W, p.H
    n = p.niche
    with p.page(tabs=False):
        c.setFillColor(t.soft)
        c.rect(0, 0, W, H, stroke=0, fill=1)
        block_h = H * 0.6
        c.setFillColor(t.primary)
        c.rect(0, H - block_h, W, block_h, stroke=0, fill=1)
        # decorative circles
        c.saveState()
        p_ = c.beginPath()
        p_.rect(0, H - block_h, W, block_h)
        c.clipPath(p_, stroke=0, fill=0)
        c.setFillColor(t.accent)
        c.circle(W - 40, H - 30, 96, stroke=0, fill=1)
        c.setStrokeColor(t.accent)
        c.setLineWidth(1)
        c.circle(W - 40, H - 30, 118, stroke=1, fill=0)
        c.setStrokeColor(white)
        c.setLineWidth(0.6)
        c.circle(W - 40, H - 30, 140, stroke=1, fill=0)
        c.restoreState()

        p.text(56, H - 80, n.audience.upper(), SEMI, 8, white, space=1.6)
        size = 190 if W < 600 else 200
        p.text(48, H - block_h + 44, str(p.year), SERIF, size, white)
        p.text(56, H - block_h + 22, "JANUARY — DECEMBER", SEMI, 8, t.accent, space=2)

        y = H - block_h - 70
        tsize = p.fit(n.title, SERIF, 40, W - 112, 20)
        p.text(56, y, n.title, SERIF, tsize, t.primary)
        p.text(56, y - 30, n.tagline, SERIF_I, 16, t.accent)

        y -= 74
        cols = 2
        colw = (W - 112) / cols
        for i, feat in enumerate(n.features):
            fx = 56 + (i % cols) * colw
            fy = y - (i // cols) * 20
            p.circle(fx + 3, fy + 3, 2.4, fill=t.accent)
            p.text(fx + 12, fy, feat, REG, 9, t.ink)

        p.text(56, 92, "THIS PLANNER BELONGS TO", SEMI, 7, t.primary, space=1.4)
        p.hline(56, W - 56, 66, t.primary, 0.8)
        p.text(W - 56, 42, "Dated · Hyperlinked · Printable", LIGHT, 8, t.muted, "right")


def button(p: Planner, x, y, w, h, label, key, filled=False, size=8.5, font=MED, align="center"):
    t = p.t
    p.rrect(x, y, w, h, r=6, fill=t.primary if filled else t.soft)
    color = white if filled else t.primary
    size = p.fit(label, font, size, w - 12, 5)
    if align == "center":
        p.text(x + w / 2, y + h / 2 - size * 0.35, label, font, size, color, "center")
    else:
        p.text(x + 10, y + h / 2 - size * 0.35, label, font, size, color)
    p.link(key, x, y, x + w, y + h)


def index_page(p: Planner):
    n, t = p.niche, p.t
    with p.page("index", tab="INDEX", outline="Start here", level=0):
        y = p.header("Start Here", right=n.tagline)
        y = p.paragraph(p.x0, y - 6, n.intro, p.cw, LIGHT, 9.5, t.ink, 1.55) - 10

        # months
        p.text(p.x0, y, "MONTHS", SEMI, 7.2, t.accent, space=1.2)
        y -= 10
        gap = 8
        bw = (p.cw - gap * 5) / 6
        bh = 30
        for i in range(12):
            bx = p.x0 + (i % 6) * (bw + gap)
            by = y - bh - (i // 6) * (bh + gap)
            button(p, bx, by, bw, bh, MONTHS[i], f"m{i + 1}", size=9)
        y -= 2 * bh + gap + 26

        # two columns: plan + trackers
        colw = (p.cw - 16) / 2
        plan = [("Year at a glance", "year")] + [(s.title, f"y{i}") for i, s in enumerate(n.year_pages)] + [("Notes", "notes")]
        tracks = [(s.title + (f"  ×{s.copies}" if s.copies > 1 else ""), f"t{i}") for i, s in enumerate(n.trackers)]
        for col, (head, items) in enumerate([("YOUR YEAR", plan), (n.tracker_tab, tracks)]):
            cx = p.x0 + col * (colw + 16)
            p.text(cx, y, head, SEMI, 7.2, t.accent, space=1.2)
            yy = y - 10
            for lab, key in items:
                button(p, cx, yy - 24, colw, 24, lab, key, size=8.5, align="left")
                yy -= 30
        rows = max(len(plan), len(tracks))
        y -= 10 + rows * 30 + 18

        # how to use
        tips = [
            "Tap the tabs on the right edge to jump to any month, the index or your " + n.tracker_tab.lower() + ".",
            "Tap a date or week on a monthly calendar to open that week's page.",
            f"Weeks start on {calendar.day_name[p.fwd]}. Each month has its calendar, two planning pages, then its weeks.",
            "Digital: import into GoodNotes, Notability, Noteshelf or Xodo; links work there. Print: use 'actual size' / 100%.",
        ]
        lines = sum(len(p.wrap(tip, REG, 8.2, p.cw - 40)) for tip in tips)
        box_h = 40 + lines * 8.2 * 1.4 + 4 * len(tips)
        p.rrect(p.x0, y - box_h, p.cw, box_h, r=8, stroke=t.line, width=0.8)
        p.text(p.x0 + 12, y - 16, "HOW TO USE", SEMI, 7.2, t.primary, space=1.2)
        ty = y - 32
        for tip in tips:
            p.circle(p.x0 + 15, ty + 3, 1.8, fill=t.accent)
            ty = p.paragraph(p.x0 + 24, ty, tip, p.cw - 40, REG, 8.2, t.ink, 1.4) - 4
        y -= box_h + 10
        if y - p.bottom > 60:
            p.box(Box(f"My word for {p.year}", "lines", hint="and why I chose it"), p.x0, y, p.cw, y - p.bottom)


def year_glance(p: Planner):
    t = p.t
    with p.page("year", tab="YEAR", outline="Year at a glance", level=0):
        y = p.header(f"{p.year} at a Glance", right="tap a month or week to jump")
        cols, rows, gap = 3, 4, 12
        cw = (p.cw - gap * (cols - 1)) / cols
        ch = (y - p.bottom - gap * (rows - 1)) / rows
        for i in range(12):
            cx = p.x0 + (i % cols) * (cw + gap)
            cy = y - (i // cols) * (ch + gap)
            p.rrect(cx, cy - ch, cw, ch, r=8, stroke=t.line, width=0.8)
            p.mini_month(cx + 12, cy - 10, cw - 24, i + 1, title_size=12)


def spec_page(p: Planner, spec: PageSpec, key, tab, outline, level, ctx=None):
    with p.page(key, tab=tab, outline=outline, level=level):
        y = p.header(spec.title, right=spec.right)
        p.render(spec.body, p.x0, y, p.cw, y - p.bottom, ctx)


def month_calendar(p: Planner, m: int):
    t, n = p.t, p.niche
    weeks = p.cal.monthdatescalendar(p.year, m)
    with p.page(f"m{m}", tab=MON_ABBR[m - 1], outline=MONTHS[m - 1], level=0):
        y = p.header(MONTHS[m - 1], right=n.cal_legend or f"{len(weeks)} weeks  ·  tap a day to open its week")
        footer_h = 118 if n.cal_footer else 0
        grid_bot = p.bottom + footer_h + (12 if footer_h else 0)
        wk_w = 20
        gx0 = p.x0 + wk_w
        cw = (p.x1 - gx0) / 7
        hh = 18
        p.rrect(gx0, y - hh, p.x1 - gx0, hh, r=4, fill=t.soft)
        for i, lab in enumerate(weekday_labels(p.fwd, 3)):
            p.text(gx0 + cw * (i + 0.5), y - hh + 6, lab, SEMI, 7, t.primary, "center", 1)
        top = y - hh - 4
        rh = (top - grid_bot) / len(weeks)
        today_week_idx = {w: i for i, w in enumerate(p.weeks)}
        for r, wk in enumerate(weeks):
            ry = top - rh * r
            # week number column
            wi = today_week_idx[wk[0]] + 1
            p.c.saveState()
            p.c.translate(p.x0 + 8, ry - rh / 2)
            p.c.rotate(90)
            p.text(0, -2.5, f"WEEK {wi:02d}", SEMI, 6, t.accent, "center", 0.8)
            p.c.restoreState()
            p.link(week_key(wk[0]), p.x0, ry - rh, gx0, ry)
            for i, d in enumerate(wk):
                cx = gx0 + cw * i
                inmonth = d.month == m
                p.rrect(cx + 1.5, ry - rh + 1.5, cw - 3, rh - 3, r=4, stroke=t.line, width=0.7,
                        fill=None if inmonth else None)
                p.text(cx + 7, ry - 15, str(d.day), SERIF, 12, t.primary if inmonth else t.line)
                if n.cal_cell_tag and inmonth:
                    tw, th = 30, 12
                    p.rrect(cx + cw - tw - 6, ry - 6 - th, tw, th, r=3, stroke=t.accent, width=0.6)
                p.link(week_key(wk[0]), cx, ry - rh, cx + cw, ry)
        if n.cal_footer:
            p.render(n.cal_footer, p.x0, p.bottom + footer_h, p.cw, footer_h)


def weekly(p: Planner, start: dt.date, tab: str):
    t, n = p.t, p.niche
    end = start + dt.timedelta(days=6)
    idx = p.weeks.index(start) + 1
    if start.month == end.month:
        title = f"{start:%B} {start.day} – {end.day}"
    else:
        title = f"{start:%b} {start.day} – {end:%b} {end.day}"
    with p.page(week_key(start), tab=tab, outline=f"Week {idx:02d}  ·  {start:%b} {start.day}", level=1):
        y = p.header(title, right=f"Week {idx:02d} of {len(p.weeks)}")
        h = y - p.bottom
        gap = 8
        left_w = p.cw * 0.62
        dh = (h - gap * 6) / 7
        for i in range(7):
            d = start + dt.timedelta(days=i)
            by = y - i * (dh + gap)
            out = d.year != p.year
            p.rrect(p.x0, by - dh, left_w, dh, r=7, stroke=t.line, width=0.8)
            # date block
            p.rrect(p.x0 + 6, by - dh + 6, 38, dh - 12, r=5, fill=t.soft)
            p.text(p.x0 + 25, by - 26, str(d.day), SERIF, 18, t.muted if out else t.primary, "center")
            p.text(p.x0 + 25, by - 38, f"{d:%a}".upper(), SEMI, 6.2, t.accent, "center", 0.8)
            if dh > 70:
                p.text(p.x0 + 25, by - 48, f"{d:%b}".upper(), SEMI, 5.6, t.muted, "center", 0.6)
            p.link(f"m{d.month}" if not out else ("m1" if d.year < p.year else "m12"), p.x0 + 6, by - dh + 6, p.x0 + 44, by - 6)
            sp = 17
            ly = by - sp - 2
            while ly > by - dh + 6:
                p.hline(p.x0 + 52, p.x0 + left_w - 10, ly)
                ly -= sp
        p.render(n.weekly_sidebar, p.x0 + left_w + 10, y, p.cw - left_w - 10, h, gap=gap)


def notes(p: Planner, copies=3):
    for i in range(copies):
        key = "notes" if i == 0 else None
        with p.page(key, tab=None, outline="Notes" if i == 0 else None, level=0):
            y = p.header("Notes")
            p.box(Box("", "dots", sp=14), p.x0, y, p.cw, y - p.bottom)


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------


def week_month(p: Planner, start: dt.date) -> int:
    return 1 if start.year < p.year else start.month


def build(niche, year: int, out: str, size="letter", week_starts="sun") -> str:
    p = Planner(out, niche, year, size, week_starts)
    cover(p)
    index_page(p)
    year_glance(p)
    for i, spec in enumerate(niche.year_pages):
        spec_page(p, spec, f"y{i}", "YEAR", spec.title, 1)

    by_month = {m: [] for m in range(1, 13)}
    for w in p.weeks:
        by_month[week_month(p, w)].append(w)

    for m in range(1, 13):
        tab = MON_ABBR[m - 1]
        month_calendar(p, m)
        for j, fn in enumerate(niche.month_pages):
            spec = fn(year, m)
            spec_page(p, spec, f"m{m}p{j}", tab, spec.title.replace(MONTHS[m - 1] + " ", ""), 1,
                      ctx={"year": year, "month": m})
        for w in by_month[m]:
            weekly(p, w, tab)

    for i, spec in enumerate(niche.trackers):
        for k in range(spec.copies):
            if i == 0 and k == 0:
                p.c.bookmarkPage("trackers")
                p.c.addOutlineEntry(niche.tracker_tab.title(), "trackers", level=0, closed=True)
                p._outline_level = 0
            key = f"t{i}" if k == 0 else None
            title = spec.title + (f"  ({k + 1}/{spec.copies})" if spec.copies > 1 else "")
            with p.page(key, tab=niche.tracker_tab, outline=spec.title if k == 0 else None, level=1):
                y = p.header(title, right=spec.right)
                p.render(spec.body, p.x0, y, p.cw, y - p.bottom)
    notes(p)
    p.save()
    return out
