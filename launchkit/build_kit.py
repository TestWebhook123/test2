#!/usr/bin/env python3
"""Build the complete Gumroad launch kit as one zip.

    python -m launchkit.build_kit            # -> launch-kit/Gumroad-Launch-Kit-2027.zip
"""

from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from html import escape
from pathlib import Path

from PIL import Image, ImageDraw

from planner.niches import ALL

from . import copy as C
from . import images as I
from .files import VARIANTS, YEAR, build_planners, quick_start, sampler

ROOT = Path(__file__).resolve().parent
KIT_NAME = f"Gumroad-Launch-Kit-{YEAR}"


def vertical_bundle(products, size, title, sub, key="cover", cta="5 planners  ·  Digital + printable"):
    W, H = size
    t = I.BUNDLE_THEME
    im = I.background(size, t, "low")
    d = ImageDraw.Draw(im)
    x = W * 0.08
    top = H * (0.10 if H / W > 1.6 else 0.07)
    I.tracked(d, (x, top), sub, I.fit_font(I.F_SEMI, 26, sub, W * 0.72), I.rgb(t.accent), 0.14)
    words = title.split()
    mid = (len(words) + 1) // 2
    lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    f1 = I.fit_font(I.F_SERIF, 100, max(lines, key=len), W * 0.84)
    y = top + 44
    for ln in lines:
        d.text((x - 3, y), ln, font=f1, fill=I.rgb(t.primary))
        y += f1.size * 1.06
    band = min(H * 0.11, 150)
    cy = y + (H - band - y) / 2
    I.fan(im, [p.pg(key) for p in products], W * 0.5, cy, round(W * 0.36), spread=0.15, max_angle=12)
    d.rectangle([0, H - band, W, H], fill=I.rgb(t.primary))
    d.text((W / 2, H - band / 2), cta, font=I.fit_font(I.F_SEMI, 34, cta, W * 0.86), fill=(255, 255, 255), anchor="mm")
    return im


def build(out_root: Path, quick=False):
    kit = out_root / KIT_NAME
    if kit.exists():
        shutil.rmtree(kit)
    files_dir = kit / "1-Product-Files"
    img_dir = kit / "2-Gumroad-Images"
    copy_dir = kit / "3-Listing-Copy"
    plan_dir = kit / "4-Launch-Plan"
    mkt_dir = kit / "5-Marketing-Images"

    # ---------------------------------------------------------------- files
    slugs = list(C.NICHE_COPY)
    letter_pdfs, products, counts = {}, {}, {}
    for i, slug in enumerate(slugs, 1):
        n = ALL[slug]
        folder = files_dir / f"{i:02d} {n.title}"
        paths = build_planners(folder, slug)
        quick_start(folder / f"{n.title} {YEAR} - Quick Start Guide.pdf", slug)
        letter_pdfs[slug] = paths[0]
        products[slug] = I.Product(slug, paths[0], I.tracker_pages(paths[0], n))
        counts[slug] = products[slug].page_count
        print("files:", n.title, counts[slug], "pages")
    bdir = files_dir / "06 Bundle - All 5 Planners"
    bdir.mkdir(parents=True)
    (bdir / "NO FILES NEEDED.txt").write_text(
        "A Gumroad Bundle is made from your 5 published products, so there is nothing to upload here.\n"
        "Buyers automatically get every planner's files. See START-HERE.html, step 5.\n")
    sdir = files_dir / "07 Free Sampler"
    sdir.mkdir(parents=True)
    sampler_pdf = sampler(sdir / f"Free {YEAR} Planner Sampler.pdf", letter_pdfs)

    # ---------------------------------------------------------------- images
    plist = [products[s] for s in slugs]
    listings = C.listings(counts)
    by_slug = {L["slug"]: L for L in listings}
    for slug in slugs:
        p = products[slug]
        d = img_dir / by_slug[slug]["folder"]
        for k, (name, fn) in enumerate([("hero", I.cover_hero), ("whats-inside", I.cover_inside),
                                        ("hyperlinked", I.cover_links), ("made-for-you", I.cover_niche),
                                        ("everything-you-get", I.cover_specs)], 1):
            I.save(fn(p), d / f"cover-{k}-{name}.jpg")
        I.save(I.thumbnail(p), d / "thumbnail-square.jpg")
        print("images:", slug)
        if quick:
            continue
        I.save(I.vertical_post(p, (1080, 1350)), mkt_dir / "instagram-post-1080x1350" / f"{slug}.jpg")
        I.save(I.vertical_post(p, (1000, 1500)), mkt_dir / "pinterest-pin-1000x1500" / f"{slug}.jpg")
        I.save(I.vertical_post(p, (1080, 1920), cta="Link in bio  ·  Digital + printable"),
               mkt_dir / "story-reel-cover-1080x1920" / f"{slug}.jpg")
        for size, nm in [((1920, 1080), "1920x1080"), ((1080, 1920), "1080x1920")]:
            for style in ("soft", "dark"):
                I.save(I.background(size, p.t, style), mkt_dir / "backgrounds" / f"{slug}-{style}-{nm}.jpg")
        prev = mkt_dir / "page-previews" / slug
        sp = p.sp
        picks = [("01-cover", sp["cover"]), ("02-index", sp["index"]), ("03-year-at-a-glance", sp["year"])]
        picks += [(f"04-year-page-{j + 1}", v) for j, v in enumerate(sp["year_pages"])]
        picks += [("05-monthly-calendar", sp["jan"])]
        picks += [(f"06-monthly-page-{j + 1}", v) for j, v in enumerate(sp["month_pages"])]
        picks += [("07-weekly", sp["week2"])]
        picks += [(f"08-tracker-{j + 1}", v) for j, v in enumerate(p.tracker_idx[:4])]
        for nm, idx in picks:
            I.save(p.pages.get(idx), prev / f"{nm}.jpg", quality=88)

    bd = img_dir / by_slug["bundle"]["folder"]
    I.save(I.bundle_hero(plist), bd / "cover-1-hero.jpg")
    I.save(I.bundle_lineup(plist), bd / "cover-2-lineup.jpg")
    I.save(I.bundle_specs(), bd / "cover-3-everything-you-get.jpg")
    I.save(I.bundle_thumb(plist), bd / "thumbnail-square.jpg")
    sd = img_dir / by_slug["sampler"]["folder"]
    I.save(I.bundle_hero(plist, title=f"Free {YEAR} Planner Sampler", kicker="FREE DOWNLOAD",
                         sub="Real January pages from all 5 niche planners. Print them or use them in GoodNotes.",
                         pages_key="jan", tags=["Free", "22 pages", "5 planners", "Printable"]), sd / "cover-1-hero.jpg")
    I.save(I.bundle_lineup(plist), sd / "cover-2-lineup.jpg")
    I.save(I.bundle_thumb(plist, key="jan", label=f"FREE SAMPLER  ·  {YEAR}"), sd / "thumbnail-square.jpg")
    if not quick:
        I.save(vertical_bundle(plist, (1080, 1350), f"The {YEAR} Niche Planner Bundle", "ALL 5 PLANNERS"),
               mkt_dir / "instagram-post-1080x1350" / "bundle.jpg")
        I.save(vertical_bundle(plist, (1000, 1500), f"The {YEAR} Niche Planner Bundle", "ALL 5 PLANNERS"),
               mkt_dir / "pinterest-pin-1000x1500" / "bundle.jpg")
        I.save(vertical_bundle(plist, (1080, 1920), f"The {YEAR} Niche Planner Bundle", "ALL 5 PLANNERS",
                               cta="Link in bio  ·  All 5 planners"), mkt_dir / "story-reel-cover-1080x1920" / "bundle.jpg")
        I.save(vertical_bundle(plist, (1000, 1500), f"Free {YEAR} Planner Sampler", "FREE DOWNLOAD", key="jan",
                               cta="Free  ·  Try all 5 planners"), mkt_dir / "pinterest-pin-1000x1500" / "free-sampler.jpg")
        I.save(vertical_bundle(plist, (1080, 1350), f"Free {YEAR} Planner Sampler", "FREE DOWNLOAD", key="jan",
                               cta="Free  ·  Try all 5 planners"), mkt_dir / "instagram-post-1080x1350" / "free-sampler.jpg")
        for size, nm in [((1920, 1080), "1920x1080"), ((1080, 1920), "1080x1920")]:
            for style in ("soft", "dark"):
                I.save(I.background(size, I.BUNDLE_THEME, style), mkt_dir / "backgrounds" / f"bundle-{style}-{nm}.jpg")
        I.save(I.header_banner(plist), mkt_dir / "headers" / "header-1500x500.jpg")
    print("images: bundle + sampler")

    # ---------------------------------------------------------------- copy
    copy_dir.mkdir(parents=True)
    for L in listings:
        (copy_dir / f"{L['folder']}.txt").write_text(C.listing_txt(L))
    (copy_dir / "listing-copy.html").write_text(listing_html(listings))

    # ---------------------------------------------------------------- plan
    plan_dir.mkdir(parents=True)
    for f in (ROOT / "content").glob("*.txt"):
        shutil.copy(f, plan_dir / f.name)
    (kit / "START-HERE.html").write_text(start_here(listings, counts))

    # ---------------------------------------------------------------- zip
    zpath = out_root / f"{KIT_NAME}.zip"
    if zpath.exists():
        zpath.unlink()
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(kit.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(out_root))
    print(f"zip: {zpath} ({zpath.stat().st_size / 1e6:.1f} MB)")
    return zpath


# --------------------------------------------------------------------------
# HTML pages
# --------------------------------------------------------------------------

CSS = """
:root{--ink:#2A2A2A;--muted:#6f6a64;--bg:#FBF8F4;--card:#fff;--line:#E7E1D8;--accent:#C9822F;--primary:#2B2A33;--soft:#F4EFE8}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
main{max-width:920px;margin:0 auto;padding:40px 20px 80px}
h1{font-family:Georgia,"Times New Roman",serif;font-size:40px;line-height:1.15;color:var(--primary);margin:0 0 8px}
h2{font-family:Georgia,"Times New Roman",serif;font-size:28px;color:var(--primary);margin:48px 0 12px;padding-top:12px;border-top:1px solid var(--line)}
h3{font-size:17px;margin:26px 0 8px;color:var(--primary)}
.kicker{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:700}
.lead{font-size:18px;color:var(--muted)}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:14px 0}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;font-size:15px}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--soft);font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--primary)}
code{background:var(--soft);padding:1px 6px;border-radius:5px;font-size:14px;overflow-wrap:anywhere}
td,th,li,p{overflow-wrap:anywhere}
ol li,ul li{margin:4px 0}
.steps>li{margin:10px 0}
.tip{border-left:4px solid var(--accent);background:var(--soft);padding:12px 16px;border-radius:0 10px 10px 0;margin:14px 0}
nav a{display:inline-block;margin:4px 10px 4px 0;color:var(--primary)}
.copybox{position:relative}
.copybtn{position:absolute;top:12px;right:12px;background:var(--primary);color:#fff;border:0;border-radius:8px;padding:6px 12px;font-size:13px;cursor:pointer}
.copybtn.done{background:#3b7d4f}
.field{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:700;margin-top:16px}
.val{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin-top:4px;position:relative;padding-right:80px}
.val .copybtn{top:6px;right:6px}
.desc{background:#fff;border:1px solid var(--line);border-radius:12px;padding:20px 22px;margin-top:6px}
.desc h2{border:0;margin:0 0 10px;padding:0;font-size:24px}
img.prev{width:100%;border-radius:10px;border:1px solid var(--line)}
@media (max-width:640px){h1{font-size:30px}h2{font-size:23px}th,td{padding:7px;font-size:13px}main{padding:28px 14px 60px}}
"""

COPY_JS = """
function copyText(btn, text){navigator.clipboard.writeText(text).then(()=>done(btn)).catch(()=>{const t=document.createElement('textarea');t.value=text;document.body.appendChild(t);t.select();document.execCommand('copy');t.remove();done(btn)})}
function copyRich(btn, id){const el=document.getElementById(id);const r=document.createRange();r.selectNodeContents(el);const s=window.getSelection();s.removeAllRanges();s.addRange(r);try{document.execCommand('copy');done(btn)}catch(e){};s.removeAllRanges()}
function done(btn){const o=btn.textContent;btn.textContent='Copied';btn.classList.add('done');setTimeout(()=>{btn.textContent=o;btn.classList.remove('done')},1400)}
"""


def val(label, text, uid):
    t = escape(text)
    js = escape(json.dumps(text))
    return (f'<div class="field">{escape(label)}</div><div class="val">{t}'
            f'<button class="copybtn" onclick="copyText(this,{js})">Copy</button></div>')


def listing_html(listings) -> str:
    parts = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
             f"<title>Gumroad Listing Copy</title><style>{CSS}</style><script>{COPY_JS}</script></head><body><main>",
             "<div class='kicker'>Gumroad launch kit</div><h1>Listing copy, ready to paste</h1>",
             "<p class='lead'>Each Copy button copies one field. For the description, press <b>Copy description</b> and paste "
             "straight into Gumroad's description editor: headings, bullets and bold text come along.</p><nav>"]
    parts += [f"<a href='#{L['slug']}'>{escape(L['folder'])}</a>" for L in listings]
    parts.append("</nav>")
    for L in listings:
        uid = L["slug"]
        parts.append(f"<h2 id='{uid}'>{escape(L['folder'])}</h2>")
        parts.append(val("Product type", L["kind"], uid))
        parts.append(val("Name", L["name"], uid))
        parts.append(val("Price", L["price"], uid))
        parts.append(val("Custom URL", L["url"], uid))
        parts.append(val("Summary (buy box)", L["summary"], uid))
        parts.append("<div class='field'>Additional details</div><table>" +
                     "".join(f"<tr><th style='width:30%'>{escape(k)}</th><td>{escape(v)}</td></tr>" for k, v in L["details"]) +
                     "</table>")
        parts.append(val("Category", L["category"], uid))
        parts.append(val("Tags (use these 5)", ", ".join(L["tags"]), uid))
        parts.append(val("Backup tags", ", ".join(L["extra_tags"]), uid))
        parts.append(f"<div class='field'>Description</div><div class='copybox'><button class='copybtn' "
                     f"onclick=\"copyRich(this,'d-{uid}')\">Copy description</button>"
                     f"<div class='desc' id='d-{uid}'>{L['description_html']}</div></div>")
        parts.append(val("Content page text (shown after purchase)", L["content_text"], uid).replace(
            "<div class=\"val\">", "<div class=\"val\" style=\"white-space:pre-wrap\">"))
    parts.append("</main></body></html>")
    return "\n".join(parts)


def start_here(listings, counts) -> str:
    tpl = (ROOT / "content" / "start_here.html").read_text()
    rows = []
    for L in listings:
        rows.append(f"<tr><td><b>{escape(L['folder'][3:])}</b></td><td>{escape(L['kind'])}</td><td>{escape(L['price'])}</td>"
                    f"<td><code>{escape(L['url'])}</code></td></tr>")
    total = sum(counts.values())
    return (tpl.replace("{{CSS}}", CSS)
               .replace("{{PRODUCT_ROWS}}", "\n".join(rows))
               .replace("{{TOTAL_PAGES}}", str(total))
               .replace("{{YEAR}}", str(YEAR)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "launch-kit"))
    ap.add_argument("--quick", action="store_true", help="skip marketing images (faster preview)")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    build(out, a.quick)
