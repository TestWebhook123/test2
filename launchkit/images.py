"""Marketing images for Gumroad: covers, thumbnails, social posts, backgrounds.

Mockups are built from real rendered planner pages (pypdfium2) composited
with Pillow: paper pages with soft shadows and a tablet frame.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from planner.core import FONT_DIR, Theme
from planner.niches import ALL

from .files import structural_pages

YEAR = 2027
F_SERIF = str(FONT_DIR / "DMSerifDisplay-Regular.ttf")
F_SERIF_I = str(FONT_DIR / "DMSerifDisplay-Italic.ttf")
F_LIGHT = str(FONT_DIR / "Poppins-Light.ttf")
F_REG = str(FONT_DIR / "Poppins-Regular.ttf")
F_MED = str(FONT_DIR / "Poppins-Medium.ttf")
F_SEMI = str(FONT_DIR / "Poppins-SemiBold.ttf")

BUNDLE_THEME = Theme(primary="#2B2A33", accent="#D9963F", soft="#F4EFE8", line="#E4DDD3")


def rgb(c, a=None):
    t = (round(c.red * 255), round(c.green * 255), round(c.blue * 255))
    return t + (a,) if a is not None else t


@lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(path, size)


# --------------------------------------------------------------------------
# Page rendering
# --------------------------------------------------------------------------


class Pages:
    def __init__(self, pdf_path: Path, scale=2.2):
        self.pdf = pdfium.PdfDocument(str(pdf_path))
        self.scale = scale
        self._cache = {}

    def __len__(self):
        return len(self.pdf)

    def get(self, i) -> Image.Image:
        if i not in self._cache:
            self._cache[i] = self.pdf[i].render(scale=self.scale).to_pil().convert("RGB")
        return self._cache[i]


def tracker_pages(pdf_path: Path, niche) -> list[int]:
    """Index of the first page of each tracker, read from the PDF outline."""
    from pypdf import PdfReader

    r = PdfReader(str(pdf_path))
    found = {}

    def walk(items):
        for it in items:
            if isinstance(it, list):
                walk(it)
            else:
                found.setdefault(it.title, r.get_destination_page_number(it))

    walk(r.outline)
    return [found[s.title] for s in niche.trackers]


# --------------------------------------------------------------------------
# Compositing helpers
# --------------------------------------------------------------------------


def shadowed(im: Image.Image, blur=26, offset=(0, 22), alpha=80) -> Image.Image:
    im = im.convert("RGBA")
    pad = blur * 3
    W, H = im.size
    out = Image.new("RGBA", (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", im.size, (25, 22, 35, alpha)), (pad + offset[0], pad + offset[1]), im.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.alpha_composite(out, sh)
    out.alpha_composite(im, (pad, pad))
    return out


def paper(page: Image.Image, width: int, angle=0.0, shadow=True) -> Image.Image:
    h = round(width * page.height / page.width)
    im = page.resize((width, h), Image.LANCZOS).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, width - 1, h - 1], outline=(222, 220, 216, 255), width=1)
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    return shadowed(im, blur=max(10, width // 22), offset=(0, max(6, width // 30))) if shadow else im


def tablet(page: Image.Image, width: int, angle=0.0) -> Image.Image:
    bez = round(width * 0.05)
    sw = width - 2 * bez
    sh = round(sw * page.height / page.width)
    H = sh + 2 * bez
    fr = Image.new("RGBA", (width, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(fr)
    r = round(width * 0.075)
    d.rounded_rectangle([0, 0, width - 1, H - 1], radius=r, fill=(30, 30, 35, 255))
    d.rounded_rectangle([4, 4, width - 5, H - 5], radius=r - 4, outline=(78, 78, 88, 255), width=3)
    screen = page.resize((sw, sh), Image.LANCZOS)
    m = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, sw - 1, sh - 1], radius=round(width * 0.018), fill=255)
    fr.paste(screen, (bez, bez), m)
    cr = max(3, round(width * 0.006))
    d.ellipse([width / 2 - cr, bez / 2 - cr, width / 2 + cr, bez / 2 + cr], fill=(60, 60, 70, 255))
    if angle:
        fr = fr.rotate(angle, resample=Image.BICUBIC, expand=True)
    return shadowed(fr, blur=max(14, width // 18), offset=(0, max(10, width // 24)), alpha=110)


def place(canvas: Image.Image, im: Image.Image, cx, cy):
    canvas.paste(im, (round(cx - im.width / 2), round(cy - im.height / 2)), im)


def background(size, theme: Theme, style="soft", seed=0) -> Image.Image:
    W, H = size
    base = rgb(theme.primary) if style == "dark" else rgb(theme.soft)
    im = Image.new("RGB", size, base)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    s = min(W, H)
    if style == "soft":
        circ = rgb(theme.primary, 255)
        d.ellipse([W - s * 0.62, -s * 0.30, W + s * 0.30, s * 0.62], fill=rgb(theme.accent, 235))
        d.ellipse([W - s * 0.74, -s * 0.42, W + s * 0.42, s * 0.74], outline=rgb(theme.accent, 160), width=max(2, s // 300))
        d.ellipse([-s * 0.25, H - s * 0.25, s * 0.25, H + s * 0.25], outline=circ[:3] + (60,), width=max(2, s // 400))
        d.ellipse([-s * 0.33, H - s * 0.33, s * 0.33, H + s * 0.33], outline=circ[:3] + (35,), width=max(2, s // 500))
    elif style == "low":
        cx, cy, r = W * 0.78, H * 0.66, s * 0.40
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb(theme.accent, 235))
        r2 = r * 1.18
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=rgb(theme.accent, 150), width=max(2, s // 300))
        d.ellipse([-s * 0.18, -s * 0.18, s * 0.18, s * 0.18], outline=rgb(theme.primary, 45), width=max(2, s // 400))
    else:
        cx, cy, r = s * 0.10, H - s * 0.05, s * 0.40
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb(theme.accent, 255))
        r2 = r * 1.2
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=(255, 255, 255, 60), width=max(2, s // 400))
        d.ellipse([W - s * 0.22, -s * 0.22, W + s * 0.22, s * 0.22], outline=(255, 255, 255, 45), width=max(2, s // 500))
    im.paste(layer, (0, 0), layer)
    return im


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------


def tracked(d: ImageDraw.ImageDraw, xy, s, fnt, fill, space=0.12, anchor="l"):
    x, y = xy
    sp = fnt.size * space
    total = sum(fnt.getlength(ch) for ch in s) + sp * (len(s) - 1)
    if anchor == "m":
        x -= total / 2
    elif anchor == "r":
        x -= total
    for ch in s:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += fnt.getlength(ch) + sp
    return total


def fit_font(path, size, s, maxw, min_size=12):
    while size > min_size and font(path, size).getlength(s) > maxw:
        size -= 2
    return font(path, size)


def wrap(s, fnt, maxw):
    out, cur = [], ""
    for w in s.split():
        t = f"{cur} {w}".strip()
        if fnt.getlength(t) <= maxw:
            cur = t
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def pill(d, x, y, s, fnt, fg, bg, padx=None, pady=None, outline=None):
    padx = padx or fnt.size * 0.9
    pady = pady or fnt.size * 0.5
    w = fnt.getlength(s) + 2 * padx
    h = fnt.size + 2 * pady
    d.rounded_rectangle([x, y, x + w, y + h], radius=h / 2, fill=bg, outline=outline, width=2 if outline else 0)
    d.text((x + padx, y + h / 2), s, font=fnt, fill=fg, anchor="lm")
    return w


def title_lines(niche) -> tuple[str, str]:
    head = niche.title.replace(" Planner", "")
    return head, f"Planner {YEAR}"


# --------------------------------------------------------------------------
# Product images
# --------------------------------------------------------------------------


class Product:
    def __init__(self, slug, pdf: Path, tracker_idx: list[int]):
        self.slug = slug
        self.n = ALL[slug]
        self.t = self.n.theme
        self.pages = Pages(pdf)
        self.sp = structural_pages(self.n)
        self.tracker_idx = tracker_idx
        self.page_count = len(self.pages)

    # quick page handles
    def pg(self, key, k=0):
        v = self.sp[key]
        return self.pages.get(v[k] if isinstance(v, list) else v)


def badges(p: Product) -> list[str]:
    return ["Hyperlinked", "Printable", "Letter + A4", f"{p.page_count} pages"]


def cover_hero(p: Product, size=(1920, 1080)) -> Image.Image:
    W, H = size
    t = p.t
    im = background(size, t, "soft")
    d = ImageDraw.Draw(im)
    x = round(W * 0.06)
    l1, l2 = title_lines(p.n)
    tracked(d, (x, H * 0.18), p.n.audience.upper(), font(F_SEMI, 24), rgb(t.accent), 0.16)
    f1 = fit_font(F_SERIF, 118, l1, W * 0.41)
    d.text((x - 4, H * 0.23), l1, font=f1, fill=rgb(t.primary))
    d.text((x - 4, H * 0.23 + f1.size * 1.05), l2, font=f1, fill=rgb(t.primary))
    ty = H * 0.23 + f1.size * 2.3
    for ln in wrap(p.n.tagline, font(F_SERIF_I, 44), W * 0.42):
        d.text((x, ty), ln, font=font(F_SERIF_I, 44), fill=rgb(t.accent))
        ty += 56
    bx, by = x, ty + 40
    for b in badges(p):
        w = pill(d, bx, by, b, font(F_MED, 26), rgb(t.primary), (255, 255, 255), outline=rgb(t.line))
        bx += w + 14
    # mockups
    place(im, paper(p.pg("cover"), round(W * 0.24), angle=7), W * 0.68, H * 0.50)
    place(im, tablet(p.pg("jan"), round(W * 0.29), angle=-3), W * 0.83, H * 0.56)
    return im


def cover_inside(p: Product, size=(1920, 1080)) -> Image.Image:
    W, H = size
    t = p.t
    im = Image.new("RGB", size, (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 210], fill=rgb(t.soft))
    d.text((W / 2, 92), "What's inside", font=font(F_SERIF, 84), fill=rgb(t.primary), anchor="mm")
    tracked(d, (W / 2, 150), f"{p.page_count} PAGES  ·  DATED JANUARY TO DECEMBER {YEAR}  ·  FULLY HYPERLINKED",
            font(F_SEMI, 22), rgb(t.accent), 0.14, "m")
    sp = p.sp
    items = [(sp["index"], "Start Here index"), (sp["year"], "Year at a glance")]
    items += [(i, s.title) for i, s in zip(sp["year_pages"], p.n.year_pages)]
    items += [(sp["jan"], "Monthly calendars")]
    jan_specs = [fn(YEAR, 1) for fn in p.n.month_pages]
    items += [(i, s.title.replace("January ", "Monthly: ")) for i, s in zip(sp["month_pages"], jan_specs)]
    items += [(sp["week2"], "Weekly pages")]
    items += [(i, s.title) for i, s in zip(p.tracker_idx, p.n.trackers)][:10 - len(items)]
    cols, gap = 5, 40
    tw = round((W - 160 - gap * (cols - 1)) / cols)
    th = round(tw * 11 / 8.5)
    scale_w = tw * 0.80
    top = 250
    rowh = (H - top - 20) / 2
    for k, (idx, label) in enumerate(items[:10]):
        cx = 80 + (k % cols) * (tw + gap) + tw / 2
        ry = top + (k // cols) * rowh
        pp = paper(p.pages.get(idx), round(scale_w))
        place(im, pp, cx, ry + (rowh - 50) / 2)
        lab_f = fit_font(F_MED, 24, label, tw)
        d.text((cx, ry + rowh - 34), label, font=lab_f, fill=rgb(t.ink), anchor="mm")
    return im


def cover_links(p: Product, size=(1920, 1080)) -> Image.Image:
    W, H = size
    t = p.t
    im = background(size, t, "dark")
    d = ImageDraw.Draw(im)
    place(im, tablet(p.pg("week2"), round(W * 0.33)), W * 0.27, H * 0.52)
    x = W * 0.52
    tracked(d, (x, H * 0.17), "DIGITAL PLANNER", font(F_SEMI, 24), rgb(t.accent), 0.18)
    d.text((x - 3, H * 0.21), "Tap. Jump. Plan.", font=font(F_SERIF, 104), fill=(255, 255, 255))
    d.text((x, H * 0.36), "Fully hyperlinked for GoodNotes, Notability & more", font=font(F_LIGHT, 32),
           fill=rgb(t.soft))
    steps = [
        ("Side tabs on every page", "Jump to the index, the year, any month or the trackers."),
        ("Calendars link to weeks", "Tap any date to open that week's page."),
        ("Back to index everywhere", "Plus PDF bookmarks for every month and week."),
    ]
    y = H * 0.47
    for i, (head, sub) in enumerate(steps, 1):
        d.ellipse([x, y, x + 64, y + 64], fill=rgb(t.accent))
        d.text((x + 32, y + 33), str(i), font=font(F_SEMI, 30), fill=(255, 255, 255), anchor="mm")
        d.text((x + 92, y - 2), head, font=font(F_SEMI, 34), fill=(255, 255, 255))
        d.text((x + 92, y + 44), sub, font=font(F_LIGHT, 26), fill=rgb(t.soft))
        y += 140
    return im


def cover_niche(p: Product, size=(1920, 1080)) -> Image.Image:
    W, H = size
    t = p.t
    im = background(size, t, "soft")
    d = ImageDraw.Draw(im)
    x = W * 0.06
    who = p.n.audience.replace("for ", "")
    tracked(d, (x, H * 0.15), "MADE FOR ONE KIND OF PERSON", font(F_SEMI, 24), rgb(t.accent), 0.16)
    ft = fit_font(F_SERIF, 84, "Not a generic planner.", W * 0.44)
    d.text((x - 3, H * 0.19), "Not a generic planner.", font=ft, fill=rgb(t.primary))
    fs = font(F_LIGHT, 32)
    y = H * 0.19 + ft.size * 1.25
    for ln in wrap(f"Built for {who}.", fs, W * 0.42):
        d.text((x, y), ln, font=fs, fill=rgb(t.ink))
        y += 46
    y += 34
    for feat in p.n.features:
        d.ellipse([x, y + 14, x + 16, y + 30], fill=rgb(t.accent))
        d.text((x + 36, y), feat, font=font(F_MED, 32), fill=rgb(t.ink))
        y += 64
    place(im, paper(p.pg("month_pages", 0), round(W * 0.26), angle=4), W * 0.66, H * 0.52)
    place(im, paper(p.pg("month_pages", 1), round(W * 0.26), angle=-4), W * 0.83, H * 0.55)
    return im


def specs(p: Product | None, bundle=False):
    pages = p.page_count if p else None
    rows = [
        ("Format", "PDF, hyperlinked"),
        ("Pages", f"{pages} pages" if pages else "105 to 111 pages per planner"),
        ("Dates", f"January to December {YEAR}"),
        ("Sizes", "US Letter + A4 (both included)"),
        ("Week start", "Sunday or Monday (both included)"),
        ("Use it on", "GoodNotes, Notability, Xodo & more"),
        ("Print it", "At home or at any print shop"),
        ("Bonus", "Quick Start Guide"),
    ]
    if bundle:
        rows.insert(0, ("Includes", "All 5 niche planners"))
    return rows


def cover_specs(p: Product, size=(1920, 1080)) -> Image.Image:
    W, H = size
    t = p.t
    im = Image.new("RGB", size, (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([W * 0.56, 0, W, H], fill=rgb(t.soft))
    x = W * 0.06
    tracked(d, (x, H * 0.12), "INSTANT DOWNLOAD", font(F_SEMI, 24), rgb(t.accent), 0.16)
    d.text((x - 3, H * 0.16), "Everything you get", font=font(F_SERIF, 84), fill=rgb(t.primary))
    y = H * 0.33
    for k, v in specs(p):
        d.text((x, y), k.upper(), font=font(F_SEMI, 22), fill=rgb(t.muted))
        d.text((x + 230, y - 6), v, font=font(F_MED, 30), fill=rgb(t.ink))
        d.line([x, y + 52, W * 0.5, y + 52], fill=rgb(t.line), width=2)
        y += 76
    tr = p.tracker_idx
    picks = [tr[0], tr[1] if len(tr) > 1 else tr[0], p.sp["week2"]]
    for k, (idx, ang, dx, dy) in enumerate(zip(picks, [-9, 6, -1], [-0.09, 0.09, 0], [0.02, 0.0, 0.05])):
        place(im, paper(p.pages.get(idx), round(W * 0.21), angle=ang), W * (0.78 + dx), H * (0.5 + dy))
    return im


def thumbnail(p: Product, size=(1000, 1000)) -> Image.Image:
    W, H = size
    t = p.t
    im = background(size, t, "soft")
    d = ImageDraw.Draw(im)
    place(im, paper(p.pg("cover"), round(W * 0.56), angle=-4), W * 0.5, H * 0.47)
    label = "DIGITAL + PRINTABLE  ·  2027"
    f = font(F_SEMI, 30)
    w = f.getlength(label) + f.size * 0.08 * len(label) + 70
    d.rounded_rectangle([W / 2 - w / 2, H - 120, W / 2 + w / 2, H - 56], radius=32, fill=rgb(t.primary))
    tracked(d, (W / 2, H - 107), label, f, (255, 255, 255), 0.08, "m")
    return im


# --------------------------------------------------------------------------
# Social formats
# --------------------------------------------------------------------------


def vertical_post(p: Product, size, cta="Digital + printable  ·  Letter & A4") -> Image.Image:
    W, H = size
    t = p.t
    im = background(size, t, "low")
    d = ImageDraw.Draw(im)
    x = W * 0.08
    top = H * (0.10 if H / W > 1.6 else 0.07)
    tracked(d, (x, top), p.n.audience.upper(), fit_font(F_SEMI, 26, p.n.audience.upper(), W * 0.64), rgb(t.accent), 0.14)
    l1, l2 = title_lines(p.n)
    f1 = fit_font(F_SERIF, 104, l1, W * 0.84)
    d.text((x - 3, top + 44), l1, font=f1, fill=rgb(t.primary))
    d.text((x - 3, top + 44 + f1.size * 1.05), l2, font=f1, fill=rgb(t.primary))
    fy = top + 44 + f1.size * 2.25
    fi = fit_font(F_SERIF_I, 42, p.n.tagline, W * 0.84)
    d.text((x, fy), p.n.tagline, font=fi, fill=rgb(t.accent))
    band = min(H * 0.11, 150)
    mock_cy = fy + 60 + (H - band - fy - 60) / 2
    mh = H - band - fy - 120
    pw = min(round(W * (0.5 if H / W > 1.6 else 0.44)), round(mh / 1.29 * 0.95))
    place(im, paper(p.pg("cover"), pw, angle=6), W * 0.36, mock_cy)
    place(im, tablet(p.pg("jan"), round(pw * 1.12), angle=-3), W * 0.64, mock_cy + 20)
    d.rectangle([0, H - band, W, H], fill=rgb(t.primary))
    fc = fit_font(F_SEMI, 34, cta, W * 0.86)
    d.text((W / 2, H - band / 2), cta, font=fc, fill=(255, 255, 255), anchor="mm")
    return im


# --------------------------------------------------------------------------
# Bundle & sampler
# --------------------------------------------------------------------------


def fan(im, page_imgs, cx, cy, width, spread=0.16, max_angle=14):
    n = len(page_imgs)
    for k, pg in enumerate(page_imgs):
        f = (k - (n - 1) / 2) / max(1, (n - 1) / 2)
        ang = -f * max_angle
        dx = f * width * spread * (n - 1) / 2 / 1.0
        dy = abs(f) * width * 0.08
        place(im, paper(pg, width, angle=ang), cx + dx, cy + dy)


def bundle_hero(products, size=(1920, 1080), title="The 2027 Niche Planner Bundle",
                kicker="ALL 5 PLANNERS IN ONE DOWNLOAD", sub=None, pages_key="cover", tags=None) -> Image.Image:
    W, H = size
    t = BUNDLE_THEME
    im = background(size, t, "soft")
    d = ImageDraw.Draw(im)
    x = W * 0.06
    tracked(d, (x, H * 0.16), kicker, font(F_SEMI, 24), rgb(t.accent), 0.16)
    words = title.split()
    mid = len(words) // 2 + (1 if len(words) % 2 else 0)
    lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    f1 = fit_font(F_SERIF, 104, max(lines, key=len), W * 0.46)
    y = H * 0.21
    for ln in lines:
        d.text((x - 3, y), ln, font=f1, fill=rgb(t.primary))
        y += f1.size * 1.08
    total = sum(p.page_count for p in products)
    sub = sub or f"{total} dated pages for creators, freelancers, fitness, ADHD and nurses."
    fs = font(F_LIGHT, 32)
    y += 20
    for ln in wrap(sub, fs, W * 0.44):
        d.text((x, y), ln, font=fs, fill=rgb(t.ink))
        y += 46
    bx, by = x, y + 30
    for b in tags or ["5 planners", "Hyperlinked", "Printable", "Letter + A4"]:
        w = pill(d, bx, by, b, font(F_MED, 26), rgb(t.primary), (255, 255, 255), outline=rgb(t.line))
        bx += w + 14
    pages = [p.pg(pages_key) for p in products]
    fan(im, pages, W * 0.74, H * 0.52, round(W * 0.235), spread=0.14)
    return im


def bundle_lineup(products, size=(1920, 1080)) -> Image.Image:
    W, H = size
    t = BUNDLE_THEME
    im = Image.new("RGB", size, (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 210], fill=rgb(t.soft))
    d.text((W / 2, 92), "One planner per niche", font=font(F_SERIF, 84), fill=rgb(t.primary), anchor="mm")
    tracked(d, (W / 2, 150), "GET THE ONE THAT FITS, OR ALL FIVE IN THE BUNDLE", font(F_SEMI, 22), rgb(t.accent), 0.14, "m")
    n = len(products)
    gap = 36
    cw = (W - 160 - gap * (n - 1)) / n
    for k, p in enumerate(products):
        cx = 80 + k * (cw + gap) + cw / 2
        place(im, paper(p.pg("cover"), round(cw * 0.96)), cx, 575)
        name = p.n.title.replace(" Planner", "")
        d.text((cx, 900), name, font=fit_font(F_SEMI, 28, "Freelancer Business", cw), fill=rgb(p.t.primary), anchor="mm")
        for j, ln in enumerate(wrap(p.n.audience, font(F_LIGHT, 22), cw)):
            d.text((cx, 942 + j * 30), ln, font=font(F_LIGHT, 22), fill=rgb(t.ink), anchor="mm")
    return im


def bundle_specs(size=(1920, 1080)) -> Image.Image:
    W, H = size
    t = BUNDLE_THEME
    im = Image.new("RGB", size, (255, 255, 255))
    d = ImageDraw.Draw(im)
    x = W * 0.06
    d.rectangle([W * 0.56, 0, W, H], fill=rgb(t.soft))
    tracked(d, (x, H * 0.10), "INSTANT DOWNLOAD", font(F_SEMI, 24), rgb(t.accent), 0.16)
    d.text((x - 3, H * 0.14), "Everything you get", font=font(F_SERIF, 84), fill=rgb(t.primary))
    y = H * 0.30
    for k, v in specs(None, bundle=True):
        d.text((x, y), k.upper(), font=font(F_SEMI, 22), fill=rgb(t.muted))
        d.text((x + 230, y - 6), v, font=font(F_MED, 30), fill=rgb(t.ink))
        d.line([x, y + 52, W * 0.5, y + 52], fill=rgb(t.line), width=2)
        y += 72
    d.text((W * 0.78, H * 0.40), "5", font=font(F_SERIF, 320), fill=rgb(t.primary), anchor="mm")
    d.text((W * 0.78, H * 0.62), "planners", font=font(F_SERIF_I, 64), fill=rgb(t.accent), anchor="mm")
    d.text((W * 0.78, H * 0.72), "for less than the price of 3", font=font(F_MED, 32), fill=rgb(t.ink), anchor="mm")
    return im


def bundle_thumb(products, size=(1000, 1000), key="cover", label="ALL 5 PLANNERS  ·  2027") -> Image.Image:
    W, H = size
    t = BUNDLE_THEME
    im = background(size, t, "soft")
    d = ImageDraw.Draw(im)
    fan(im, [p.pg(key) for p in products], W * 0.5, H * 0.45, round(W * 0.42), spread=0.13, max_angle=12)
    f = font(F_SEMI, 30)
    w = f.getlength(label) + f.size * 0.08 * len(label) + 70
    d.rounded_rectangle([W / 2 - w / 2, H - 120, W / 2 + w / 2, H - 56], radius=32, fill=rgb(t.primary))
    tracked(d, (W / 2, H - 107), label, f, (255, 255, 255), 0.08, "m")
    return im


def header_banner(products, size=(1500, 500), title=f"{YEAR} Niche Planners",
                  sub="Digital + printable planners made for one kind of person") -> Image.Image:
    W, H = size
    t = BUNDLE_THEME
    im = background(size, t, "soft")
    d = ImageDraw.Draw(im)
    x = W * 0.06
    f1 = fit_font(F_SERIF, 92, title, W * 0.5)
    d.text((x, H * 0.30), title, font=f1, fill=rgb(t.primary))
    fs = fit_font(F_LIGHT, 30, sub, W * 0.5)
    d.text((x, H * 0.30 + f1.size * 1.25), sub, font=fs, fill=rgb(t.ink))
    fan(im, [p.pg("cover") for p in products], W * 0.77, H * 0.55, round(H * 0.52), spread=0.16, max_angle=12)
    return im


def plain_background(theme, size, style):
    return background(size, theme, style)


def save(im: Image.Image, path: Path, quality=90):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in (".jpg", ".jpeg"):
        im.convert("RGB").save(path, quality=quality, optimize=True, progressive=True)
    else:
        im.save(path, optimize=True)
    return path
