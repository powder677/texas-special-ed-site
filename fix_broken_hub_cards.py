"""
fix_broken_hub_cards.py
Finds all district index pages where the FIE hub card was injected
in the wrong place and repairs them.

Run:
    python fix_broken_hub_cards.py --dry-run
    python fix_broken_hub_cards.py
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


def is_broken(html):
    """Detect if the FIE card was injected inside another card."""
    return '</a>\n</a>' in html or '</a>\r\n</a>' in html


def fix_hub_grid(html, district_slug):
    """
    Remove the misplaced FIE card entirely, then re-inject it
    correctly after the last properly closed hub card.
    """
    district_name = slug_to_name(district_slug)
    new_filename  = f"what-is-an-fie-{district_slug}.html"

    fie_card = f'''<a class="hub-card" href="/districts/{district_slug}/{new_filename}" style="border-left-color: #1a56db;">
<div class="hub-card-icon">📄</div>
<h3>What Is an FIE?</h3>
<p>Understand your child's Full Individual Evaluation rights in {district_name} — timelines, what's covered, and how to request one.</p>
</a>'''

    # Step 1: Strip out any existing FIE card (correctly or incorrectly placed)
    # Remove the full <a>...</a> block for the FIE card
    html = re.sub(
        r'<a[^>]*what-is-an?-fie[^>]*>.*?</a>\s*',
        '',
        html,
        flags=re.DOTALL
    )

    # Step 2: Fix any double </a> left behind
    html = html.replace('</a>\r\n</a>', '</a>')
    html = html.replace('</a>\n</a>', '</a>')

    # Step 3: Fix any broken icon divs (unclosed </div> from first card)
    # Pattern: 📋 immediately followed by \n<a (icon div was never closed)
    html = re.sub(
        r'(hub-card-icon">📋)\s*\n(<a\s)',
        r'\1</div>\n\2',
        html
    )
    html = re.sub(
        r'(hub-card-icon">📋)\s*\r\n(<a\s)',
        r'\1</div>\r\n\2',
        html
    )

    # Step 4: Re-inject FIE card correctly
    # Find the hub-grid closing pattern: </a> then </div> then section-divider
    pattern = re.compile(
        r'(</a>)(\s*\n\s*)(</div>)(\s*\n\s*<div[^>]*section-divider)',
        re.DOTALL
    )
    match = pattern.search(html)
    if match:
        replacement = (
            match.group(1) + "\n" +
            fie_card + "\n" +
            match.group(3) +
            match.group(4)
        )
        html = html[:match.start()] + replacement + html[match.end():]
        return html, True

    # Fallback: find hub-grid, insert after last </a> inside it
    hub_match = re.search(r'(<div\s+class="hub-grid">)(.*?)(</div>)', html, re.DOTALL)
    if hub_match:
        inner    = hub_match.group(2)
        last_pos = inner.rfind('</a>')
        if last_pos != -1:
            new_inner = inner[:last_pos + 4] + "\n" + fie_card + "\n" + inner[last_pos + 4:]
            html = html[:hub_match.start()] + hub_match.group(1) + new_inner + hub_match.group(3) + html[hub_match.end():]
            return html, True

    return html, False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    districts = sorted([
        d for d in os.listdir(DISTRICTS_DIR)
        if os.path.isdir(os.path.join(DISTRICTS_DIR, d))
    ])

    broken_found = 0
    fixed        = 0
    skipped      = 0

    for slug in districts:
        index_path = os.path.join(DISTRICTS_DIR, slug, "index.html")
        if not os.path.exists(index_path):
            continue

        with open(index_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Only process pages that have the FIE card already (from first run)
        if "What Is an FIE?" not in html and f"what-is-an-fie-{slug}" not in html:
            skipped += 1
            continue

        if not is_broken(html):
            print(f"  OK (already clean): {slug}")
            skipped += 1
            continue

        broken_found += 1
        new_html, success = fix_hub_grid(html, slug)

        if not success:
            print(f"  ✗ COULD NOT FIX: {slug}")
            continue

        if args.dry_run:
            print(f"  [DRY RUN] Would fix: {slug}")
        else:
            backup(index_path)
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(new_html)
            print(f"  ✓ Fixed: {slug}")
            fixed += 1

    print(f"\n── SUMMARY ──────────────────────────────")
    print(f"  Broken found:  {broken_found}")
    print(f"  Fixed:         {fixed}")
    print(f"  Already clean: {skipped}")
    if not args.dry_run and fixed > 0:
        print(f"  Backups: {BACKUP_DIR}")
        print(f"\nNext: git add districts/ && git commit -m 'fix FIE hub card injection' && git push")


if __name__ == "__main__":
    main()