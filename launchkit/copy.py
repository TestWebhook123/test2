"""Gumroad listing copy for every product.

``listings()`` returns one dict per product with every field Gumroad asks
for. The "What's inside" lists are generated from the planner definitions
so they always match the PDFs.
"""

from __future__ import annotations

from html import escape

from planner.niches import ALL

YEAR = 2027
PRICE = 14
BUNDLE_PRICE = 34

NICHE_COPY = {
    "content-creator": dict(
        name=f"{YEAR} Content Creator Planner | Digital & Printable",
        url="content-creator-planner-2027",
        hook="Plan a full year of content without the chaos.",
        promise=("Most planners give you a blank box and wish you luck. This one is built around how creators actually "
                 "work: pick your content pillars, set growth targets for every platform, plan each month's posts from "
                 "idea to published, and see what's working with a monthly stats and revenue review."),
        for_you=["You post on Instagram, TikTok, YouTube, Pinterest or a newsletter (or all of them)",
                 "You keep losing ideas in your notes app and DMs",
                 "You're landing brand deals and need one place to track deliverables and payments"],
        tags=["content creator planner", "digital planner 2027", "social media planner", "goodnotes planner", "influencer planner"],
        extra_tags=["content calendar", "youtube planner", "instagram planner", "ugc creator", "notability planner"],
        category="Business & Money (or Self Improvement > Productivity)",
    ),
    "freelancer": dict(
        name=f"{YEAR} Freelancer Business Planner | Digital & Printable",
        url="freelancer-planner-2027",
        hook="Run your one-person business like a pro in 2027.",
        promise=("Freelancing means being the CEO, the accountant and the talent at the same time. This planner keeps all "
                 "three in one place: turn an income goal into the number of clients you need each quarter, track projects "
                 "and leads every month, log invoices and expenses, count billable hours every week and keep quarterly taxes "
                 "ready for your accountant."),
        for_you=["You're a freelancer, consultant, VA, designer, developer or writer",
                 "You've lost track of an unpaid invoice (or three)",
                 "You want predictable income instead of feast-or-famine months"],
        tags=["freelancer planner", "business planner 2027", "small business planner", "digital planner", "solopreneur"],
        extra_tags=["income tracker", "invoice tracker", "goodnotes planner", "client tracker", "self employed"],
        category="Business & Money",
    ),
    "fitness-wellness": dict(
        name=f"{YEAR} Fitness & Wellness Planner | Digital & Printable",
        url="fitness-planner-2027",
        hook="Your strongest, healthiest year, planned one week at a time.",
        promise=("Motivation fades by February. Systems don't. Set real benchmarks, plan a monthly training split, tick off "
                 "daily habits, check in on your measurements every month and log every workout, personal record and meal "
                 "plan in one place, so you can see your progress instead of guessing."),
        for_you=["You lift, run, do classes or are just getting started",
                 "You want to build habits that last past January",
                 "You like seeing your progress on paper (or on your iPad)"],
        tags=["fitness planner", "workout planner 2027", "wellness planner", "habit tracker", "digital planner"],
        extra_tags=["meal planner", "gym log", "health journal", "goodnotes planner", "printable planner"],
        category="Fitness & Health",
    ),
    "adhd-friendly": dict(
        name=f"{YEAR} ADHD-Friendly Planner | Digital & Printable",
        url="adhd-planner-2027",
        hook="A planner that works with your brain, not against it.",
        promise=("If you've abandoned every planner by mid-January, the problem probably wasn't you. This one is built for "
                 "busy, wandering, brilliant brains: dump everything out first and sort it later, pick only three priorities "
                 "a week, use a dopamine menu instead of doom-scrolling, and break big scary projects into tiny next steps. "
                 "Lots of white space, no guilt."),
        for_you=["You have ADHD, think you might, or just have a very busy brain",
                 "Traditional planners feel overwhelming or make you feel behind",
                 "You need structure that's flexible enough to survive a bad week"],
        tags=["adhd planner", "adhd digital planner", "neurodivergent planner", "digital planner 2027", "goodnotes planner"],
        extra_tags=["brain dump", "dopamine menu", "executive function", "focus planner", "printable planner"],
        category="Self Improvement > Productivity",
    ),
    "nurse-shift-worker": dict(
        name=f"{YEAR} Nurse Shift Planner | Digital & Printable",
        url="nurse-planner-2027",
        hook="Built for rotating schedules and 12-hour shifts.",
        promise=("Regular planners assume a 9-to-5. This one gives you a shift box on every calendar day, a monthly hours "
                 "and overtime log, rest and recovery habits for after nights, license and CE credit tracking, PTO planning, "
                 "a paycheck tracker and undated 4-patient brain sheets for your shift."),
        for_you=["You're an RN, LPN, nursing student, CNA, tech or any shift worker",
                 "Your schedule changes every week and you're tired of piecing it together",
                 "You want to protect your sleep, your PTO and your paycheck"],
        tags=["nurse planner", "shift planner 2027", "nursing planner", "digital planner", "nurse gift"],
        extra_tags=["nurse brain sheet", "shift work", "healthcare worker", "goodnotes planner", "printable planner"],
        category="Self Improvement > Productivity (or Fitness & Health)",
    ),
}

FAQ_COMMON = [
    ("Is this a physical product?", "No. It's an instant digital download (PDF). Nothing will be shipped."),
    ("Which apps does it work with?", "GoodNotes, Notability, Noteshelf, Xodo, Samsung Notes, Adobe Acrobat and any app that "
                                      "opens PDFs. The hyperlinks work in all of these. You can also print it."),
    ("Can I print it?", "Yes. US Letter and A4 versions are both included. Print at 100% / actual size at home or at a print shop."),
    ("Is it dated?", f"Yes, January 1 to December 31, {YEAR}. The trackers at the back are undated so you can reuse them."),
    ("Sunday or Monday start?", "Both are included, in both paper sizes. That's four PDFs in one download."),
    ("Can I share it?", "It's for your personal use. Please don't share or resell the files. Want to buy for a team? Message me."),
]


def pages_of(slug) -> dict:
    """Page counts per section for the 'What's inside' list (from niche definitions)."""
    n = ALL[slug]
    return {
        "year": [s.title for s in n.year_pages],
        "month": [fn(YEAR, 1).title.replace("January ", "") for fn in n.month_pages],
        "trackers": [(s.title, s.copies) for s in n.trackers],
    }


def inside_list(slug, page_count) -> list[str]:
    n = ALL[slug]
    p = pages_of(slug)
    items = [
        "Start Here index page with links to everything",
        f"{YEAR} year at a glance",
        "Year planning pages: " + " and ".join(p["year"]),
        "12 monthly calendars (tap any day to open its week)",
        "Every month: " + " + ".join(p["month"]) + " pages",
        "53 weekly pages with a sidebar made for " + n.audience.replace("for ", ""),
    ]
    tr = ", ".join(f"{t} (x{c})" if c > 1 else t for t, c in p["trackers"])
    items.append(f"{n.tracker_tab.title()}: {tr}")
    items.append("Dot-grid notes pages")
    return items


def html_desc(hook, promise, inside, for_you, extra_blocks=()):
    out = [f"<h2>{escape(hook)}</h2>", f"<p>{escape(promise)}</p>"]
    out.append("<h3>This is for you if…</h3><ul>" + "".join(f"<li>{escape(x)}</li>" for x in for_you) + "</ul>")
    out.append("<h3>What's inside</h3><ul>" + "".join(f"<li>{escape(x)}</li>" for x in inside) + "</ul>")
    for title, items in extra_blocks:
        out.append(f"<h3>{escape(title)}</h3><ul>" + "".join(f"<li>{escape(x)}</li>" for x in items) + "</ul>")
    return "\n".join(out)


def faq_html(faqs):
    out = ["<h3>FAQ</h3>"]
    for q, a in faqs:
        out.append(f"<p><strong>{escape(q)}</strong><br>{escape(a)}</p>")
    return "\n".join(out)


WHY = ["Fully hyperlinked: side tabs on every page, calendars that link to weeks, back to index from anywhere",
       "Works in GoodNotes, Notability, Noteshelf, Xodo and any PDF app, or print it",
       "US Letter AND A4, Sunday AND Monday start, all included",
       "Clean, minimal design with lots of writing space",
       "Instant download plus a Quick Start Guide"]


def listings(page_counts: dict[str, int]) -> list[dict]:
    out = []
    for slug, c in NICHE_COPY.items():
        n = ALL[slug]
        pc = page_counts[slug]
        inside = inside_list(slug, pc)
        files = [f"{n.title} {YEAR}, US Letter, Sunday start (PDF)", f"{n.title} {YEAR}, US Letter, Monday start (PDF)",
                 f"{n.title} {YEAR}, A4, Monday start (PDF)", f"{n.title} {YEAR}, A4, Sunday start (PDF)",
                 "Quick Start Guide (PDF)"]
        desc = html_desc(c["hook"], c["promise"], inside, c["for_you"],
                         [("Why you'll love it", WHY), ("What you'll download", files)])
        desc += "\n" + faq_html(FAQ_COMMON)
        desc += ("\n<p><em>Personal use only. This is a digital product; no physical item will be shipped. "
                 "Colors may look slightly different on screen and in print.</em></p>")
        out.append(dict(
            slug=slug, folder=f"{list(NICHE_COPY).index(slug) + 1:02d} {n.title}", kind="Digital product",
            name=c["name"], url=c["url"], price=f"${PRICE}",
            summary=f"You'll get a {pc}-page hyperlinked {YEAR} planner in 4 versions (Letter + A4, Sunday + Monday start) plus a quick start guide.",
            details=[("Format", "PDF (hyperlinked)"), ("Pages", str(pc)), ("Dates", f"Jan to Dec {YEAR}"),
                     ("Sizes", "US Letter + A4"), ("Week start", "Sunday + Monday"),
                     ("Works with", "GoodNotes, Notability, Xodo & more")],
            description_html=desc, tags=c["tags"], extra_tags=c["extra_tags"], category=c["category"],
            content_text=content_page(n.title, slug),
            audience=n.audience, title=n.title,
        ))

    total = sum(page_counts.values())
    bundle_inside = [f"{ALL[s].title}: {page_counts[s]} pages, {ALL[s].audience}" for s in NICHE_COPY]
    bundle_desc = html_desc(
        "All five niche planners. One download.",
        ("Can't pick just one? Run a business, make content and train for a 10K? Shopping for a friend who's a nurse? "
         f"Get every planner in the collection for less than the price of three: {total} dated, hyperlinked pages for {YEAR}."),
        bundle_inside,
        ["You wear more than one hat (creator + freelancer is a classic combo)",
         "You want to gift planners to friends or family",
         "You like having the right planner for each part of your life"],
        [("Why you'll love it", WHY), ("What you'll download", [
            "All 5 planners, each in 4 versions (Letter + A4, Sunday + Monday start)", "A Quick Start Guide for each planner"])],
    ) + "\n" + faq_html(FAQ_COMMON) + "\n<p><em>Personal use only. Digital product; nothing will be shipped.</em></p>"
    out.append(dict(
        slug="bundle", folder="06 Bundle - All 5 Planners", kind="Bundle",
        name=f"The {YEAR} Niche Planner Bundle | All 5 Digital Planners", url="planner-bundle-2027",
        price=f"${BUNDLE_PRICE}",
        summary=f"You'll get all 5 hyperlinked {YEAR} planners ({total} pages), each in Letter + A4 and Sunday + Monday start.",
        details=[("Includes", "5 planners"), ("Pages", f"{total} total"), ("Dates", f"Jan to Dec {YEAR}"),
                 ("Sizes", "US Letter + A4"), ("Week start", "Sunday + Monday"), ("Format", "PDF (hyperlinked)")],
        description_html=bundle_desc,
        tags=["planner bundle", "digital planner 2027", "goodnotes planner", "printable planner", "2027 planner"],
        extra_tags=["adhd planner", "nurse planner", "fitness planner", "freelancer planner", "content creator planner"],
        category="Self Improvement > Productivity",
        content_text="(A Gumroad bundle delivers each planner's own content automatically. No files to upload here.)",
        audience="", title="Bundle",
    ))

    sampler_desc = html_desc(
        f"Try every {YEAR} planner free.",
        ("Not sure which planner fits you? Download real pages from all five: the cover, the January calendar, one "
         "planning page made for that niche and a weekly page. Print them or open them in GoodNotes or Notability. "
         "Enter $0 to get it free, or tip if you'd like to."),
        [f"{ALL[s].title}: cover, January calendar, niche planning page, weekly page" for s in NICHE_COPY],
        ["You want to see the quality before you buy",
         "You're deciding between niches",
         "You want a few free planning pages to start January"],
        [("Good to know", ["Links are turned off in the sampler. The full planners are fully hyperlinked.",
                           "US Letter size, Sunday start. The full planners include A4 and Monday start too."])],
    )
    out.append(dict(
        slug="sampler", folder="07 Free Sampler", kind="Digital product",
        name=f"FREE {YEAR} Planner Sampler | Try All 5 Niche Planners", url="free-planner-sampler-2027",
        price="$0+ (pay what you want, minimum $0, suggested $3)",
        summary="You'll get a 22-page PDF with real January pages from all 5 planners. Free.",
        details=[("Format", "PDF"), ("Pages", "22"), ("Size", "US Letter"), ("Price", "Free")],
        description_html=sampler_desc,
        tags=["free planner", "free printable", "2027 planner", "digital planner", "planner sampler"],
        extra_tags=["free goodnotes planner", "adhd planner", "nurse planner", "fitness planner", "freebie"],
        category="Self Improvement > Productivity",
        content_text=sampler_content(),
        audience="", title="Free Sampler",
    ))
    return out


def content_page(title, slug) -> str:
    return f"""Thank you for buying the {title} {YEAR}!

Your files are below. Which one should you download?
- In the US or Canada: US Letter. Everywhere else: A4.
- Sunday or Monday start: whichever you prefer.
You can download all four; they're all yours.

New to digital planners? Open the Quick Start Guide first (2 minutes). It shows how to import into GoodNotes or Notability and how to print.

Tip: in GoodNotes, if a link doesn't respond, switch to Read-only mode or tap with your finger.

Questions or a problem with a file? Reply to your receipt email and I'll help.

Enjoying it? A rating on Gumroad helps a small shop more than you'd think. Thank you!"""


def sampler_content() -> str:
    return f"""Here's your free {YEAR} Planner Sampler. Enjoy!

Found your favorite? Get the full planner (dated Jan to Dec {YEAR}, fully hyperlinked, Letter + A4, Sunday + Monday start):

- Content Creator Planner: [paste product link]
- Freelancer Business Planner: [paste product link]
- Fitness & Wellness Planner: [paste product link]
- ADHD-Friendly Planner: [paste product link]
- Nurse Shift Planner: [paste product link]
- All 5 in the Bundle (best value): [paste bundle link]

As a thank-you, use code SAMPLER20 for 20% off any planner."""


def plain_text(desc_html: str) -> str:
    import re

    s = desc_html
    s = re.sub(r"<h2>(.*?)</h2>", lambda m: m.group(1).upper() + "\n", s)
    s = re.sub(r"<h3>(.*?)</h3>", lambda m: "\n" + m.group(1).upper() + "\n", s)
    s = s.replace("<ul>", "").replace("</ul>", "\n")
    s = re.sub(r"<li>(.*?)</li>", lambda m: "- " + m.group(1) + "\n", s)
    s = s.replace("<br>", "\n")
    s = re.sub(r"<p>(.*?)</p>", lambda m: m.group(1) + "\n\n", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    import html as _h

    s = _h.unescape(s)
    return re.sub(r"\n{3,}", "\n\n", s).strip() + "\n"


def listing_txt(L: dict) -> str:
    lines = [
        f"PRODUCT TYPE: {L['kind']}",
        f"NAME: {L['name']}",
        f"PRICE: {L['price']}",
        f"CUSTOM URL (slug): {L['url']}",
        "",
        "SUMMARY (the line in the buy box):",
        L["summary"],
        "",
        "ADDITIONAL DETAILS (key / value pairs under the summary):",
        *[f"  {k}: {v}" for k, v in L["details"]],
        "",
        f"CATEGORY (Share tab > Discover): {L['category']}",
        "TAGS (use these 5): " + ", ".join(L["tags"]),
        "BACKUP TAGS: " + ", ".join(L["extra_tags"]),
        "",
        "=" * 60,
        "DESCRIPTION",
        "=" * 60,
        "Tip: for formatted text, copy it from listing-copy.html instead of this file.",
        "",
        plain_text(L["description_html"]),
        "=" * 60,
        "CONTENT PAGE TEXT (Content tab, shown to buyers after purchase)",
        "=" * 60,
        L["content_text"],
        "",
    ]
    return "\n".join(lines)
