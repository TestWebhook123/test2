"""Niche definitions: palette, copy and page layouts for each planner.

Each niche reuses the shared skeleton (cover, index, year at a glance,
monthly calendars, weekly spreads, notes) and adds its own year pages,
monthly pages, weekly sidebar and trackers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .core import MONTHS, Box, Cols, PageSpec, Row, Theme

MON3 = [m[:3] for m in MONTHS]
QUARTERS = ["Q1", "Q2", "Q3", "Q4", "Total"]


@dataclass
class Niche:
    slug: str
    title: str
    tagline: str
    audience: str
    intro: str
    theme: Theme
    year_pages: list[PageSpec]
    month_pages: list[Callable[[int, int], PageSpec]]
    weekly_sidebar: list
    trackers: list[PageSpec]
    cal_footer: list = field(default_factory=list)
    cal_cell_tag: str | None = None
    cal_legend: str = ""
    tracker_tab: str = "TRACKERS"
    features: list[str] = field(default_factory=list)


# ==========================================================================
# 1. Content creators
# ==========================================================================

PLATFORMS = ["Instagram", "TikTok", "YouTube", "Pinterest", "Newsletter", "Other"]


def creator() -> Niche:
    year_pages = [
        PageSpec("Creator Vision", [
            Box("My niche in one sentence", "lines", weight=0.55),
            Row([Box("Who I create for", "lines"), Box("What keeps them up at night", "lines")], weight=1.1),
            Box("2027 creator goals", "numbered", n=5, weight=1.1),
            Box("Content pillars", "table", weight=1.3, cols=[("Pillar", 1), ("Why my audience cares", 2), ("Go-to formats", 1.4)], row_h=26),
        ]),
        PageSpec("Growth Targets", [
            Box("Followers / subscribers", "table", weight=1.5, rowlabels=PLATFORMS,
                cols=[("Platform", 1.3), ("Jan 1", 1), ("Q1", 1), ("Q2", 1), ("Q3", 1), ("Q4", 1), ("Dec 31", 1)]),
            Row([
                Box("Income goal", "table", rowlabels=QUARTERS, cols=[("Quarter", 1), ("Goal", 1.2), ("Actual", 1.2)]),
                Box("Brands I'd love to work with", "numbered", n=6),
            ], weight=1.2),
            Row([Box("Creators to collab with", "numbered", n=5), Box("Skills to level up", "checks")], weight=1),
        ]),
    ]

    def content_plan(y, m):
        return PageSpec(f"{MONTHS[m - 1]} Content Plan", [
            Row([Box("Pillars to focus on", "lines", hint="this month"), Box("Launch / promo / collab", "lines")], weight=0.75),
            Box("Post schedule", "table", weight=3.2, checks=(4, 5, 6, 7), row_h=19,
                cols=[("Date", 0.6), ("Platform", 0.9), ("Format", 0.8), ("Hook / idea", 2.6),
                      ("Script", 0.55), ("Film", 0.55), ("Edit", 0.55), ("Posted", 0.6)]),
        ], right="Plan  ·  Script  ·  Film  ·  Edit  ·  Post")

    def growth_review(y, m):
        return PageSpec(f"{MONTHS[m - 1]} Growth & Review", [
            Box("Platform stats", "table", weight=1.35, rowlabels=PLATFORMS,
                cols=[("Platform", 1.2), ("Start", 0.8), ("End", 0.8), ("Growth", 0.8), ("Best post", 2)]),
            Row([
                Box("Revenue", "table", w=1, rowlabels=["Brand deals", "Affiliate", "Ads / creator fund", "Digital products", "Other", "Total"],
                    cols=[("Source", 1.4), ("Amount", 1)]),
                Box("Top 3 posts & why they worked", "numbered", w=1.2, n=3),
            ], weight=1.25),
            Row([Box("What worked", "lines"), Box("Try next month", "lines")], weight=0.9),
            Box("Rate the month", "circles", weight=0.7, labels=["Consistency", "Quality", "Community / engagement", "Energy & balance"]),
        ])

    trackers = [
        PageSpec("Brand Deal Tracker", [Box("", "table", row_h=22,
                 cols=[("Brand", 1.2), ("Contact", 1.1), ("Deliverables", 1.8), ("Rate", 0.7), ("Due", 0.7), ("Invoiced", 0.65), ("Paid", 0.55)],
                 checks=(5, 6))], copies=2),
        PageSpec("Content Idea Bank", [Box("", "table", row_h=20,
                 cols=[("Idea / hook", 3), ("Pillar", 1), ("Format", 0.9), ("Platform", 0.9), ("Used", 0.5)], checks=(4,))], copies=3),
        PageSpec("Hooks & Caption Swipe File", Cols([
            [Box("Hooks that stop the scroll", "numbered", weight=1.2), Box("Calls to action", "lines", weight=0.8)],
            [Box("Caption starters", "lines"), Box("Phrases my audience uses", "lines")],
        ])),
        PageSpec("Hashtag & Keyword Bank", [
            Row([Box("Instagram", "lines"), Box("TikTok", "lines")]),
            Row([Box("YouTube / SEO keywords", "lines"), Box("Pinterest", "lines")]),
            Row([Box("Niche-specific", "lines"), Box("Branded / campaign", "lines")]),
        ]),
        PageSpec("Yearly Income Tracker", [Box("", "table", weight=1, rowlabels=MON3 + ["Total"],
                 cols=[("Month", 0.8), ("Brand deals", 1), ("Affiliate", 1), ("Ads", 1), ("Products", 1), ("Other", 1), ("Total", 1)])]),
        PageSpec("Gear, Apps & Subscriptions", [
            Box("Subscriptions", "table", weight=1.2, cols=[("Tool / app", 1.6), ("Cost", 0.7), ("Billing", 0.8), ("Renews", 0.8), ("Keep?", 0.6)], checks=(4,)),
            Box("Gear wishlist", "table", cols=[("Item", 2), ("Why", 2), ("Price", 0.8), ("Bought", 0.6)], checks=(3,)),
        ]),
    ]

    return Niche(
        slug="content-creator",
        title="Content Creator Planner",
        tagline="Plan it. Film it. Post it. Grow it.",
        audience="for creators, influencers & UGC makers",
        intro=("Built for people who make content for a living (or want to). Map your pillars and growth targets, "
               "batch-plan every month's posts from idea to published, track brand deals and income, and run a "
               "monthly review that tells you what to make more of."),
        theme=Theme(primary="#3D2B56", accent="#E8694A", soft="#FBEDE8", line="#E2D8E4"),
        year_pages=year_pages,
        month_pages=[content_plan, growth_review],
        weekly_sidebar=[
            Box("Posts this week", "checks", weight=1.3),
            Box("Batch day", "checks", weight=1, hint="script / film / edit"),
            Box("Engage & network", "checks", weight=0.9),
            Box("Idea parking lot", "lines", weight=1),
        ],
        cal_footer=[Row([Box("Monthly theme", "lines", w=1), Box("Key launches & deadlines", "lines", w=1.3), Box("Goal", "lines", w=1)])],
        trackers=trackers,
        features=["Content pillars & growth targets", "Monthly post planner (idea to posted)", "Platform stats & revenue review",
                  "Brand deal tracker", "Idea bank, hooks & hashtag banks", "Yearly income tracker"],
    )


# ==========================================================================
# 2. Freelancers & solopreneurs
# ==========================================================================


def freelancer() -> Niche:
    year_pages = [
        PageSpec("Business Vision", [
            Box("The business", "fields", weight=1, labels=["Business name", "What I do", "Who I serve", "What makes me different"]),
            Box("2027 business goals", "numbered", n=5, weight=1.1),
            Row([
                Box("Services & pricing", "table", w=1.4, cols=[("Service", 1.6), ("Price", 0.8), ("Turnaround", 0.9)], row_h=22),
                Box("Ideal client", "lines", w=1),
            ], weight=1.4),
            Box("Boundaries", "lines", weight=0.6, hint="hours, response times, what I say no to"),
        ]),
        PageSpec("Income Plan", [
            Box("Annual income goal", "table", weight=1.1, rowlabels=QUARTERS,
                cols=[("Quarter", 0.8), ("Goal", 1), ("Clients needed", 1), ("Actual", 1), ("Difference", 1)]),
            Row([
                Box("My monthly numbers", "fields", labels=["Business expenses", "Owner's pay", "Tax set-aside %", "Savings buffer", "Minimum monthly revenue", "Target day rate"]),
                Box("Ways to hit the goal", "checks", items=["Raise rates", "Retainers / packages", "Upsell existing clients", "Referral ask", "New offer"]),
            ], weight=1.25),
            Box("Marketing plan", "table", weight=1, rowlabels=QUARTERS[:4], cols=[("Quarter", 0.7), ("Focus channel", 1.3), ("Actions", 2.6)]),
        ]),
    ]

    def projects(y, m):
        return PageSpec(f"{MONTHS[m - 1]} Projects & Pipeline", [
            Box("Active projects", "table", weight=1.6, row_h=20,
                cols=[("Client", 1.1), ("Project", 1.6), ("Deadline", 0.8), ("Fee", 0.7), ("Status", 0.9), ("Done", 0.5)], checks=(5,)),
            Box("Leads & follow-ups", "table", weight=1.15, row_h=20,
                cols=[("Name", 1.1), ("Source", 0.9), ("Last contact", 0.9), ("Next step", 1.8), ("Won", 0.5)], checks=(4,)),
            Box("Marketing this month", "checks", weight=0.6),
        ])

    def money(y, m):
        return PageSpec(f"{MONTHS[m - 1]} Money", [
            Box("Invoices", "table", weight=1.3, row_h=19,
                cols=[("Invoice #", 0.8), ("Client", 1.4), ("Amount", 0.8), ("Sent", 0.7), ("Due", 0.7), ("Paid", 0.5)], checks=(5,)),
            Box("Expenses", "table", weight=1, row_h=19, cols=[("Date", 0.6), ("Item", 2), ("Category", 1.1), ("Amount", 0.8)]),
            Row([
                Box("Month summary", "fields", labels=["Revenue", "Expenses", "Profit", "Tax set aside", "Hours billed", "Effective hourly rate"]),
                Box("Review", "lines", hint="wins, lessons, what to change"),
            ], weight=1.05),
        ])

    trackers = [
        PageSpec("Client Directory", [Box("", "table", row_h=26,
                 cols=[("Client", 1.2), ("Contact", 1.1), ("Email / phone", 1.6), ("Rate", 0.6), ("Notes", 1.5)])], copies=2),
        PageSpec("Invoice Log", [Box("", "table", row_h=19,
                 cols=[("Invoice #", 0.8), ("Date", 0.7), ("Client", 1.4), ("Amount", 0.8), ("Due", 0.7), ("Paid on", 0.8)])], copies=2),
        PageSpec("Quarterly Tax Tracker", [
            Box("Estimated taxes", "table", weight=1.1, rowlabels=QUARTERS,
                cols=[("Quarter", 0.7), ("Income", 1), ("Expenses", 1), ("Est. tax", 1), ("Due date", 0.9), ("Paid on", 0.9)]),
            Row([
                Box("Deductible categories", "checks", items=["Software & subscriptions", "Equipment", "Home office", "Internet & phone",
                                                            "Education & courses", "Travel", "Marketing & ads", "Professional fees"]),
                Box("Notes for my accountant", "lines"),
            ], weight=1.4),
        ]),
        PageSpec("Annual Summary", [Box("", "table", rowlabels=MON3 + ["Total"],
                 cols=[("Month", 0.8), ("Revenue", 1), ("Expenses", 1), ("Profit", 1), ("Hours", 0.8), ("Clients", 0.8), ("$/hour", 0.8)])]),
        PageSpec("Portfolio & Testimonials", [Box("", "table", row_h=34,
                 cols=[("Client", 1), ("Project", 1.3), ("Result", 1.4), ("Testimonial", 0.8), ("Link", 1)], checks=(3,))]),
        PageSpec("Tools & Subscriptions", [Box("", "table", row_h=20,
                 cols=[("Tool", 1.5), ("Used for", 1.6), ("Cost", 0.6), ("Billing", 0.7), ("Renews", 0.7)])]),
    ]

    return Niche(
        slug="freelancer",
        title="Freelancer Business Planner",
        tagline="Fewer spreadsheets. More booked months.",
        audience="for freelancers, consultants & solopreneurs",
        intro=("Built for one-person businesses. Set an income goal and break it into clients per quarter, run "
               "projects and a lead pipeline every month, log invoices and expenses, and keep taxes and the annual "
               "summary ready for your accountant."),
        theme=Theme(primary="#1F4E5A", accent="#D9963F", soft="#EBF3F2", line="#D3E1E0"),
        year_pages=year_pages,
        month_pages=[projects, money],
        weekly_sidebar=[
            Box("Top 3 priorities", "numbered", n=3, weight=0.8),
            Box("Billable hours", "table", weight=1.5, rowlabels="@weekdays", cols=[("Day", 0.8), ("Client", 1.5), ("Hrs", 0.6)]),
            Box("Invoices & follow-ups", "checks", weight=1),
            Box("Notes", "lines", weight=0.8),
        ],
        cal_footer=[Row([Box("Revenue goal", "lines", w=0.8), Box("Deadlines", "lines", w=1.4), Box("Marketing focus", "lines", w=1)])],
        trackers=trackers,
        features=["Income plan broken into quarters", "Monthly projects & lead pipeline", "Invoice & expense logs",
                  "Billable hours on every week", "Quarterly tax tracker", "Client directory & annual summary"],
    )


# ==========================================================================
# 3. Fitness & wellness
# ==========================================================================


def fitness() -> Niche:
    measures = ["Weight", "Body fat %", "Waist", "Hips", "Chest", "Arms", "Thighs"]
    year_pages = [
        PageSpec("Wellness Vision", [
            Box("Why I'm doing this", "lines", weight=0.8),
            Box("2027 health & fitness goals", "numbered", n=5, weight=1.1),
            Row([
                Box("Starting point", "fields", labels=["Date", "Resting heart rate", "Avg. sleep", "Avg. steps"] + measures),
                Box("Progress photo dates", "table", rowlabels=MON3, cols=[("Month", 1), ("Date", 1.2), ("Done", 0.7)], checks=(2,)),
            ], weight=2.1),
            Box("Non-scale victories I'm chasing", "lines", weight=0.7),
        ]),
        PageSpec("Strength & Fitness Benchmarks", [
            Box("Benchmarks", "table", weight=1.8,
                rowlabels=["Squat", "Bench press", "Deadlift", "Overhead press", "Pull-ups", "Push-ups", "Plank", "1 mile", "5K", "", ""],
                cols=[("Lift / test", 1.3), ("Jan", 1), ("Mar", 1), ("Jun", 1), ("Sep", 1), ("Dec", 1)]),
            Row([Box("My training style", "checks", items=["Strength", "Hypertrophy", "Running", "HIIT", "Yoga / mobility", "Sport"]),
                 Box("Events & challenges", "table", cols=[("Event", 1.6), ("Date", 0.8)], row_h=20)], weight=1),
        ]),
    ]

    def training(y, m):
        return PageSpec(f"{MONTHS[m - 1]} Training & Habits", [
            Box("Monthly goal", "lines", weight=0.45),
            Box("Training split", "table", weight=1.2, rowlabels=["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"],
                cols=[("", 0.8), ("@weekdays", 1)]),
            Box("Habit tracker", "habit", weight=1.9,
                labels=["Workout", "Steps", "Water", "Protein", "Sleep 7h+", "Stretch / mobility", "Veggies", "Alcohol-free", "", ""]),
        ])

    def checkin(y, m):
        return PageSpec(f"{MONTHS[m - 1]} Check-In", [
            Row([
                Box("Measurements", "table", w=1.2, rowlabels=measures, cols=[("Measure", 1.2), ("Start", 1), ("End", 1), ("Change", 1)]),
                Box("PRs & milestones", "lines", w=1),
            ], weight=1.4),
            Row([Box("Wins", "lines"), Box("Adjust next month", "lines")], weight=1),
            Box("How did it feel?", "circles", weight=0.8, labels=["Energy", "Sleep", "Nutrition", "Consistency", "Mood"]),
        ])

    trackers = [
        PageSpec("Workout Log", Cols([
            [Box("Session", "fields", weight=0.45, labels=["Date", "Focus", "Duration"]),
             Box("", "table", weight=2, cols=[("Exercise", 1.6), ("Set 1", 0.6), ("Set 2", 0.6), ("Set 3", 0.6), ("Set 4", 0.6)], row_h=24)],
            [Box("Session", "fields", weight=0.45, labels=["Date", "Focus", "Duration"]),
             Box("", "table", weight=2, cols=[("Exercise", 1.6), ("Set 1", 0.6), ("Set 2", 0.6), ("Set 3", 0.6), ("Set 4", 0.6)], row_h=24)],
        ]), right="weight x reps", copies=4),
        PageSpec("Personal Records", [Box("", "table", row_h=22, cols=[("Exercise", 1.6), ("Weight / time", 1), ("Reps", 0.6), ("Date", 0.8), ("Notes", 1.4)])]),
        PageSpec("Cardio & Running Log", [Box("", "table", row_h=20,
                 cols=[("Date", 0.7), ("Type", 1), ("Distance", 0.8), ("Time", 0.7), ("Pace", 0.7), ("Feel 1-5", 0.7)])], copies=2),
        PageSpec("Meal Planner", [
            Box("This week", "table", weight=2, rowlabels="@weekdays", cols=[("Day", 0.6), ("Breakfast", 1), ("Lunch", 1), ("Dinner", 1), ("Snacks", 0.9)]),
            Row([Box("Prep list", "checks"), Box("Notes", "lines")], weight=1),
        ], copies=2),
        PageSpec("Grocery List", [
            Row([Box("Produce", "checks"), Box("Protein", "checks"), Box("Dairy & eggs", "checks")]),
            Row([Box("Pantry & grains", "checks"), Box("Frozen", "checks"), Box("Other", "checks")]),
        ], copies=2),
    ]

    return Niche(
        slug="fitness-wellness",
        title="Fitness & Wellness Planner",
        tagline="Train smart. Eat well. Show up for you.",
        audience="for gym-goers, runners & anyone building healthy habits",
        intro=("Built for people building a stronger, healthier year. Set benchmarks, plan a monthly training "
               "split, track daily habits, check in on measurements, and log every workout, PR and meal plan in "
               "one place."),
        theme=Theme(primary="#2F4A3A", accent="#C4703B", soft="#ECF2E8", line="#D6E1D1"),
        year_pages=year_pages,
        month_pages=[training, checkin],
        weekly_sidebar=[
            Box("Workouts", "table", weight=1.5, rowlabels="@weekdays", cols=[("Day", 0.7), ("Session", 1.6), ("Done", 0.6)], checks=(2,)),
            Box("Water", "circles", weight=1.4, labels="@weekdays", n=8),
            Box("Meal prep", "checks", weight=0.9),
            Box("Notes", "lines", weight=0.6),
        ],
        cal_footer=[Row([Box("Fitness goal", "lines"), Box("Nutrition focus", "lines"), Box("Reward when I hit it", "lines")])],
        trackers=trackers,
        features=["Benchmarks & starting stats", "Monthly training split + habit tracker", "Measurement check-ins",
                  "Workout, PR & cardio logs", "Meal planner & grocery lists", "Water tracker every week"],
    )


# ==========================================================================
# 4. ADHD-friendly
# ==========================================================================


def adhd() -> Niche:
    year_pages = [
        PageSpec("My Brain Manual", [
            Row([Box("I focus best when…", "lines"), Box("I get stuck when…", "lines")]),
            Row([Box("Things that reset me", "lines"), Box("Signs I'm overloaded", "lines")]),
            Box("Three things that matter most in 2027", "numbered", n=3, weight=0.75),
            Box("Systems I'm trying", "checks", weight=0.8, hint="keep it to a few"),
        ], right="know your brain, plan with it"),
        PageSpec("Dopamine Menu", [
            Row([Box("Starters", "lines", hint="quick 5-minute boosts"), Box("Mains", "lines", hint="bigger, truly fulfilling")]),
            Row([Box("Sides", "lines", hint="pair with boring tasks"), Box("Desserts", "lines", hint="fun, but set a timer")]),
            Box("Specials", "lines", weight=0.6, hint="rare treats for big wins"),
        ], right="pick from here instead of doom-scrolling"),
    ]

    def dump(y, m):
        return PageSpec(f"{MONTHS[m - 1]} Brain Dump", [
            Box("Get it all out of your head", "dots", weight=1.7),
            Row([Box("Must do", "checks"), Box("Want to do", "checks")], weight=1.2),
            Row([Box("Can wait", "checks"), Box("Ask for help / delegate", "checks")], weight=0.8),
        ], right="dump first, sort second")

    def reflect(y, m):
        return PageSpec(f"{MONTHS[m - 1]} Habits & Reflection", [
            Box("Tiny habits", "habit", weight=1.35, labels=["Water", "Move my body", "Outside", "Meds / vitamins", "Bed on time", "Tidy 10 min",
                                                             "Energy (1-5)", "Mood (1-5)"]),
            Row([Box("Wins, big & tiny", "lines"), Box("What got in the way", "lines")], weight=1.1),
            Box("Next month I'll try", "lines", weight=0.6),
        ], right="progress, not perfection")

    daily = PageSpec("Daily Focus", Cols([
        [Box("Today", "fields", weight=0.5, labels=["Date", "Must happen today"]),
         Box("Energy", "circles", weight=0.35, labels=["Energy level"], n=5),
         Box("Top 3", "numbered", n=3, weight=0.7),
         Box("Brain dump", "dots", weight=1.4),
         Box("One tiny win", "lines", weight=0.45)],
        [Box("Time blocks", "schedule", hours=(7, 22))],
    ], weights=[1.15, 1]), right="undated, use any day", copies=7)

    trackers = [
        daily,
        PageSpec("Task Triage", [
            Row([Box("Do now", "checks", hint="urgent + important"), Box("Schedule it", "checks", hint="important, not urgent")]),
            Row([Box("Hand it off", "checks", hint="urgent, not important"), Box("Let it go", "checks", hint="neither")]),
        ], right="sort the chaos", copies=2),
        PageSpec("Project Breakdown", [
            Box("The project", "fields", weight=0.7, labels=["Project", "Why I care", "Deadline", "Done looks like"]),
            Box("Break it into tiny steps", "checks", weight=2.2, hint="smaller than you think"),
            Row([Box("Body double / accountability", "lines"), Box("Reward when done", "lines")], weight=0.6),
        ], copies=3),
        PageSpec("Routine Builder", [
            Row([Box("Morning routine", "checks"), Box("Evening routine", "checks")], weight=1.3),
            Row([Box("Launch pad", "checks", hint="before I leave the house"), Box("Weekly reset", "checks")], weight=1),
        ]),
        PageSpec("Important Dates & Bills", [
            Box("Bills & renewals", "table", weight=1.3, cols=[("What", 1.6), ("Amount", 0.7), ("Due", 0.7), ("Autopay", 0.6)], checks=(3,), row_h=20),
            Box("Birthdays & appointments", "table", weight=1, cols=[("Date", 0.7), ("What / who", 2.2), ("Reminder set", 0.8)], checks=(2,), row_h=20),
        ]),
    ]

    return Niche(
        slug="adhd-friendly",
        title="ADHD-Friendly Planner",
        tagline="A planner that works with your brain, not against it.",
        audience="for neurodivergent minds & busy brains",
        intro=("Built for busy, wandering, brilliant brains. Monthly brain dumps that you sort after, three "
               "priorities a week (not thirty), a dopamine menu, tiny habits, undated daily focus pages and "
               "project breakdowns that turn big scary things into small next steps."),
        theme=Theme(primary="#3B3A6B", accent="#E6A21F", soft="#F0EEFA", line="#DCD8EE"),
        year_pages=year_pages,
        month_pages=[dump, reflect],
        weekly_sidebar=[
            Box("Top 3 (only 3!)", "numbered", n=3, weight=0.8),
            Box("Brain dump", "dots", weight=1.4),
            Box("Energy check", "circles", weight=1.2, labels="@weekdays", n=5),
            Box("Rewards I earned", "lines", weight=0.7),
        ],
        cal_footer=[Row([Box("One big thing this month", "lines", w=1.2), Box("Don't forget", "checks", w=1), Box("Fun plans", "lines", w=1)])],
        trackers=trackers,
        tracker_tab="TOOLS",
        features=["Brain manual & dopamine menu", "Monthly brain dump + sorting", "Only 3 priorities a week",
                  "7 undated daily focus pages", "Task triage & project breakdown", "Routines, bills & dates"],
    )


# ==========================================================================
# 5. Nurses & shift workers
# ==========================================================================


def nurse() -> Niche:
    year_pages = [
        PageSpec("Licenses & Certifications", [
            Box("Credentials", "table", weight=1.6, rowlabels=["RN / LPN license", "BLS", "ACLS", "PALS", "Specialty cert", "", ""],
                cols=[("Credential", 1.3), ("Number", 1.1), ("Issued", 0.8), ("Expires", 0.8), ("Renewed", 0.7)], checks=(4,)),
            Row([
                Box("CE requirements", "fields", labels=["Hours required", "Renewal date", "Hours completed", "Hours remaining"]),
                Box("2027 career goals", "numbered", n=4),
            ], weight=1.1),
            Box("Skills, units or roles to explore", "lines", weight=0.8),
        ]),
        PageSpec("PTO & Time-Off Planner", [
            Box("Time off", "table", weight=2, rowlabels=MON3,
                cols=[("Month", 0.7), ("Requested", 1), ("Dates", 1.5), ("Approved", 0.7), ("Hours used", 0.8)], checks=(3,)),
            Row([
                Box("My balance", "fields", labels=["PTO on Jan 1", "Accrual per period", "Holiday rotation", "Planned total"]),
                Box("Trips & big days", "lines"),
            ], weight=0.9),
        ]),
    ]

    def shifts(y, m):
        return PageSpec(f"{MONTHS[m - 1]} Shifts & Hours", [
            Box("Shift log", "table", weight=3, row_h=19,
                cols=[("Date", 0.6), ("Unit", 0.8), ("Shift", 0.6), ("Start", 0.6), ("End", 0.6), ("Hours", 0.6), ("OT", 0.5), ("Notes", 1.7)]),
            Row([
                Box("Month totals", "fields", labels=["Total hours", "Overtime", "Shifts picked up", "Shifts swapped"]),
                Box("Requests to put in", "checks"),
            ], weight=0.85),
        ], right="D = day  ·  N = night  ·  E = evening")

    def recovery(y, m):
        return PageSpec(f"{MONTHS[m - 1]} Rest & Recovery", [
            Box("Recovery habits", "habit", weight=1.35,
                labels=["Slept 7h+", "Water", "Real meal on shift", "Movement", "Decompress", "Meal prep", "Time with people", ""]),
            Row([Box("Shift wins & good moments", "lines"), Box("Tough moments to let go", "lines")], weight=1.1),
            Box("Self-care plan for next month", "checks", weight=0.65),
        ])

    patient = Box("Patient", "fields", labels=["Room", "Name / age", "Dx", "Allergies", "Code status", "Vitals", "Meds / times", "Labs", "To do", "Notes"])
    trackers = [
        PageSpec("Shift Brain Sheet", [Row([patient, patient]), Row([patient, patient])], right="undated, 4 patients", copies=4),
        PageSpec("CE Credit Log", [Box("", "table", row_h=20,
                 cols=[("Date", 0.7), ("Course", 2.2), ("Provider", 1.1), ("Hours", 0.6), ("Cert saved", 0.7)], checks=(4,))]),
        PageSpec("Paycheck Tracker", [Box("", "table", row_h=19,
                 cols=[("Pay date", 0.8), ("Hours", 0.6), ("OT", 0.6), ("Diff / bonus", 0.9), ("Gross", 0.8), ("Net", 0.8), ("Checked", 0.6)], checks=(6,))], copies=2),
        PageSpec("Shift Swap Log", [Box("", "table", row_h=20,
                 cols=[("Date", 0.7), ("Swapped with", 1.4), ("Their shift", 1), ("My shift", 1), ("Approved", 0.7)], checks=(4,))]),
        PageSpec("Night Shift Sleep Plan", Cols([
            [Box("My plan", "fields", weight=0.9, labels=["Sleep before 1st night", "Sleep after nights", "Caffeine cut-off", "Days off reset"]),
             Box("Wind-down routine", "checks", weight=1.1, items=["Blackout curtains", "Phone away", "Shower", "Light snack"]),
             Box("What helps me sleep", "lines", weight=0.8)],
            [Box("Ideal day after a night shift", "schedule", hours=(6, 23))],
        ])),
        PageSpec("Unit Contacts", [Box("", "table", row_h=22, cols=[("Name", 1.3), ("Role", 1), ("Phone / ext.", 1.1), ("Notes", 1.6)])]),
    ]

    return Niche(
        slug="nurse-shift-worker",
        title="Nurse Shift Planner",
        tagline="Rotating schedule. Steady you.",
        audience="for nurses, healthcare & shift workers",
        intro=("Built for rotating schedules. A shift box on every calendar day, monthly hours and overtime "
               "logs, rest & recovery habits, license and CE tracking, PTO planning, paycheck checks and "
               "undated brain sheets for your shift."),
        theme=Theme(primary="#1C3D6E", accent="#2E9C98", soft="#E8F1F8", line="#D1DEEB"),
        year_pages=year_pages,
        month_pages=[shifts, recovery],
        weekly_sidebar=[
            Box("Shifts", "table", weight=1.5, rowlabels="@weekdays", cols=[("Day", 0.7), ("Shift", 0.9), ("Hours", 0.7)]),
            Box("Meal prep", "checks", weight=0.9),
            Box("Recovery", "checks", weight=0.9, items=["Sleep plan", "Movement", "Something fun"]),
            Box("Notes", "lines", weight=0.8),
        ],
        cal_footer=[Row([Box("Hours goal", "lines", w=0.8), Box("Days off plans", "lines", w=1.3), Box("Reminders", "checks", w=1)])],
        cal_cell_tag="SHIFT",
        cal_legend="Write D / N / E / OFF in each shift box",
        trackers=trackers,
        features=["Shift box on every calendar day", "Monthly hours & overtime log", "License, cert & CE tracking",
                  "PTO planner & paycheck tracker", "Rest & recovery habits", "Undated 4-patient brain sheets"],
    )


ALL = {n.slug: n for n in (creator(), freelancer(), fitness(), adhd(), nurse())}
