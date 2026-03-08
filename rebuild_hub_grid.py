"""
rebuild_hub_grid.py
Completely rewrites the hub-grid on every district index page.
Replaces the broken injected version with a clean 7-card grid.

Usage:
    python rebuild_hub_grid.py --dry-run
    python rebuild_hub_grid.py --only aldine-isd
    python rebuild_hub_grid.py
"""

import os
import re
import shutil
import argparse
from datetime import datetime

SITE_ROOT     = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"
DISTRICTS_DIR = os.path.join(SITE_ROOT, "districts")
BACKUP_DIR    = os.path.join(SITE_ROOT, "_backups", datetime.now().strftime("%Y%m%d_%H%M%S"))


def slug_to_name(slug):
    name = slug.replace("-", " ").title()
    name = re.sub(r'\bIsd\b', 'ISD', name)
    name = re.sub(r'\bCisd\b', 'CISD', name)
    return name


def backup(path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    rel  = os.path.relpath(path, SITE_ROOT)
    dest = os.path.join(BACKUP_DIR, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(path, dest)


def build_hub_grid(district_slug):
    """Build a clean 7-card hub-grid for a district."""
    name = slug_to_name(district_slug)
    d    = district_slug
    fie_file = f"what-is-an-fie-{d}.html"

    return f"""<div class="hub-grid">
<a class="hub-card" href="/districts/{d}/ard-process-guide.html">
<div class="hub-card-icon">📋</div>
<h3>The ARD Meeting Guide</h3>
<p>Step-by-step preparation for your next ARD meeting, including the 10-day recess rule.</p>
</a>
<a class="hub-card" href="/districts/{d}/evaluation-child-find.html">
<div class="hub-card-icon">🔍</div>
<h3>Request an Evaluation</h3>
<p>How to secure a Full Individual Evaluation (FIE) and enforce the 45-day testing timeline.</p>
</a>
<a class="hub-card warning" href="/districts/{d}/grievance-dispute-resolution.html">
<div class="hub-card-icon">⚠️</div>
<h3>Discipline &amp; Grievances</h3>
<p>Crisis support for suspensions, Manifestation Determination Reviews (MDR), and TEA complaints.</p>
</a>
<a class="hub-card" href="/districts/{d}/dyslexia-services.html">
<div class="hub-card-icon">📖</div>
<h3>Dyslexia &amp; Reading</h3>
<p>{name} screening rights, structured literacy programs, and 504 vs. IEP paths.</p>
</a>
<a class="hub-card" href="/districts/{d}/leadership-directory.html">
<div class="hub-card-icon">📞</div>
<h3>Contact Directory</h3>
<p>Direct contact info for district special education leadership and how to escalate issues.</p>
</a>
<a class="hub-card" href="/districts/{d}/partners.html" style="border-left-color: #d4af37;">
<div class="hub-card-icon">🤝</div>
<h3>Local Advocates &amp; Tutors</h3>
<p>Connect with top-rated special education advocates, attorneys, and CALT tutors in the area.</p>
</a>
<a class="hub-card" href="/districts/{d}/{fie_file}" style="border-left-color: #1a56db;">
<div class="hub-card-icon">📄</div>
<h3>What Is an FIE?</h3>
<p>Understand your child's Full Individual Evaluation rights in {name} — timelines, what's covered, and how to request one.</p>
</a>
</div>"""


def fix_index(path, district_slug, dry_run):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Find the entire hub-grid block — from opening div to closing </div>
    # We match greedily to the </div> that's followed by section-divider
    pattern = re.compile(
        r'<div class="hub-grid">.*?</div>(?=\s*\r?\n\s*<div[^>]*section-divider)',
        re.DOTALL
    )

    match = pattern.search(html)
    if not match:
        return "hub-grid not found"

    new_grid = build_hub_grid(district_slug)
    new_html = html[:match.start()] + new_grid + html[match.end():]

    if dry_run:
        return "would rebuild"

    backup(path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    return "✓ rebuilt"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", type=str)
    args = parser.parse_args()

    districts = sorted([
        d for d in os.listdir(DISTRICTS_DIR)
        if os.path.isdir(os.path.join(DISTRICTS_DIR, d))
    ])

    if args.only:
        districts = [d for d in districts if args.only in d]

    print(f"Processing {len(districts)} districts | {'DRY RUN' if args.dry_run else 'LIVE'}\n")

    counts = {}
    for slug in districts:
        index_path = os.path.join(DISTRICTS_DIR, slug, "index.html")
        if not os.path.exists(index_path):
            continue

        result = fix_index(index_path, slug, args.dry_run)
        counts[result] = counts.get(result, 0) + 1

        if result != "hub-grid not found":
            print(f"  {result}: {slug}")

    print(f"\n── SUMMARY ──────────────────────────────")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")

    if not args.dry_run and counts.get("✓ rebuilt", 0) > 0:
        print(f"\n  Backups: {BACKUP_DIR}")
        print(f"\nNext: git add districts/ && git commit -m 'rebuild hub grids with FIE card' && git push")


if __name__ == "__main__":
    main()