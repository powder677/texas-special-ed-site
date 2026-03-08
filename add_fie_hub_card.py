"""
add_fie_hub_card.py
Adds a "What Is an FIE?" hub card to the hub-grid on every district
index.html that has a corresponding what-is-an-fie-{district}.html page.

Usage:
    python add_fie_hub_card.py --dry-run
    python add_fie_hub_card.py
    python add_fie_hub_card.py --only dallas-isd
"""

import os
import re
import shutil
import argparse
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────

SITE_ROOT     = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"
DISTRICTS_DIR = os.path.join(SITE_ROOT, "districts")
BACKUP_DIR    = os.path.join(SITE_ROOT, "_backups", datetime.now().strftime("%Y%m%d_%H%M%S"))

# ── HELPERS ───────────────────────────────────────────────────────────────────

def backup(path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    rel  = os.path.relpath(path, SITE_ROOT)
    dest = os.path.join(BACKUP_DIR, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(path, dest)

def slug_to_name(slug):
    name = slug.replace("-", " ").title()
    name = re.sub(r'\bIsd\b', 'ISD', name)
    name = re.sub(r'\bCisd\b', 'CISD', name)
    return name

def fie_card(district_slug):
    """Build the hub card HTML for the FIE page."""
    district_name = slug_to_name(district_slug)
    filename = f"what-is-an-fie-{district_slug}.html"
    return f'''<a class="hub-card" href="/districts/{district_slug}/{filename}" style="border-left-color: #1a56db;">
<div class="hub-card-icon">📄</div>
<h3>What Is an FIE?</h3>
<p>Understand your child's Full Individual Evaluation rights in {district_name} — timelines, what's covered, and how to request one.</p>
</a>'''

# ── MAIN PROCESSING ───────────────────────────────────────────────────────────

def process_district(district_slug, dry_run):
    district_dir = os.path.join(DISTRICTS_DIR, district_slug)
    index_path   = os.path.join(district_dir, "index.html")
    fie_filename = f"what-is-an-fie-{district_slug}.html"
    fie_path     = os.path.join(district_dir, fie_filename)

    # Only proceed if both index.html and the renamed FIE page exist
    if not os.path.exists(index_path):
        return "no index"
    if not os.path.exists(fie_path):
        # Also check old name just in case rename hasn't run yet
        old_fie = os.path.join(district_dir, "what-is-fie.html")
        if not os.path.exists(old_fie):
            return "no fie page"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Skip if card already exists
    if fie_filename in html or "What Is an FIE?" in html:
        return "already done"

    # Build the card
    card = fie_card(district_slug)

    # Find the hub-grid block and append card after the LAST </a> inside it
    # We look for the closing </div> that immediately follows </a> and precedes
    # the section-divider — this is the hub-grid's closing tag
    hub_close_pattern = re.compile(
        r'(</a>)\s*\n(</div>)\s*\n(<div[^>]*section-divider[^>]*>)',
        re.DOTALL
    )
    match = hub_close_pattern.search(html)
    if not match:
        # Fallback: try without section-divider check
        hub_pattern = re.compile(r'(<div\s+class="hub-grid">)(.*?)(</div>)', re.DOTALL)
        m2 = hub_pattern.search(html)
        if not m2:
            return "hub-grid not found"
        # Insert after last </a> within hub-grid
        inner = m2.group(2)
        last_a = inner.rfind('</a>')
        if last_a == -1:
            return "hub-grid not found"
        new_inner = inner[:last_a + 4] + "\n" + card + "\n" + inner[last_a + 4:]
        new_html = html[:m2.start()] + m2.group(1) + new_inner + m2.group(3) + html[m2.end():]
    else:
        # Insert new card between last </a> and closing </div>
        insert = match.group(1) + "\n" + card + "\n" + match.group(2) + "\n" + match.group(3)
        new_html = html[:match.start()] + insert + html[match.end():]

    if dry_run:
        return "would add card"

    backup(index_path)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_html)
    return "✓ done"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", type=str, help="Single district slug e.g. dallas-isd")
    args = parser.parse_args()

    if not os.path.exists(DISTRICTS_DIR):
        print(f"ERROR: {DISTRICTS_DIR} not found")
        return

    districts = sorted([
        d for d in os.listdir(DISTRICTS_DIR)
        if os.path.isdir(os.path.join(DISTRICTS_DIR, d))
    ])

    if args.only:
        districts = [d for d in districts if args.only in d]

    print(f"Processing {len(districts)} districts | {'DRY RUN' if args.dry_run else 'LIVE'}\n")

    counts = {"✓ done": 0, "would add card": 0, "already done": 0,
              "no fie page": 0, "no index": 0, "hub-grid not found": 0}

    for slug in districts:
        result = process_district(slug, args.dry_run)
        counts[result] = counts.get(result, 0) + 1
        if result not in ("no fie page", "no index", "already done"):
            print(f"  {result}: {slug}")

    print(f"\n── SUMMARY ──────────────────────────────")
    for k, v in counts.items():
        if v: print(f"  {k}: {v}")

    if not args.dry_run and counts.get("✓ done", 0) > 0:
        print(f"\n  Backups: {BACKUP_DIR}")
        print(f"\nNext: git add districts/ && git commit -m 'add FIE hub card to district index pages' && git push")


if __name__ == "__main__":
    main()