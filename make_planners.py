#!/usr/bin/env python3
"""Generate niche New Year planners as hyperlinked, printable PDFs.

    python make_planners.py                      # all niches, 2027, Letter (Sun) + A4 (Mon)
    python make_planners.py --niche adhd-friendly --size a4 --week-starts mon
    python make_planners.py --list
"""

import argparse
from pathlib import Path

from planner.build import build
from planner.niches import ALL


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--year", type=int, default=2027)
    ap.add_argument("--niche", action="append", choices=sorted(ALL), help="repeatable; default: all")
    ap.add_argument("--size", choices=["letter", "a4", "both"], default="both")
    ap.add_argument("--week-starts", choices=["sun", "mon"], help="default: sun for Letter, mon for A4")
    ap.add_argument("--out", default="dist")
    ap.add_argument("--list", action="store_true", help="list niches and exit")
    a = ap.parse_args()

    if a.list:
        for slug, n in ALL.items():
            print(f"{slug:22} {n.title} — {n.audience}")
        return

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sizes = ["letter", "a4"] if a.size == "both" else [a.size]
    for slug in a.niche or list(ALL):
        for size in sizes:
            ws = a.week_starts or ("sun" if size == "letter" else "mon")
            path = out / f"{slug}-planner-{a.year}-{size}-{ws}.pdf"
            build(ALL[slug], a.year, str(path), size, ws)
            print(f"wrote {path} ({path.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
