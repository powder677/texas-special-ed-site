"""
update_iep_links.py

Scans all HTML files in the blog/es folder and replaces any links
pointing to an IEP letter page with the Spanish version.

Run with:  python update_iep_links.py
Add --dry-run to preview changes without saving them.
"""

import os
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────

BLOG_ES_FOLDER   = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\blog\es"
SPANISH_BOT_PATH = "/resources/iep-letter-spanish/index.html"

# Any href containing these strings will be replaced with SPANISH_BOT_PATH.
# Add more patterns here if needed.
PATTERNS_TO_REPLACE = [
    r"/resources/iep-letter(?!-spanish)[^\"']*",   # /resources/iep-letter (not already spanish)
    r"/fie-letter[^\"']*",                          # /fie-letter/...
    r"/get-your-letter[^\"']*",                     # /get-your-letter/...
    r"texas-fie-bot-831148457361\.us-central1\.run\.app(?!/es)[^\"']*",  # English Cloud Run URL
]

DRY_RUN = "--dry-run" in sys.argv

# ── HELPERS ───────────────────────────────────────────────────────────────────

def backup_file(path: Path):
    """Create a timestamped .bak copy before modifying."""
    stamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_suffix(f".bak_{stamp}")
    shutil.copy2(path, backup)
    return backup


def replace_links_in_file(html_path: Path) -> tuple[int, list[str]]:
    """
    Replace matching href values in one file.
    Returns (number_of_replacements, list_of_change_descriptions).
    """
    original = html_path.read_text(encoding="utf-8", errors="replace")
    updated  = original
    changes  = []

    for pattern in PATTERNS_TO_REPLACE:
        # Match inside href="..." or href='...'
        full_pattern = rf'(href=["\'])({pattern})(["\'])'
        matches = re.findall(full_pattern, updated)
        if matches:
            for quote_open, old_url, quote_close in matches:
                changes.append(f"  {old_url}  →  {SPANISH_BOT_PATH}")
            updated = re.sub(
                full_pattern,
                rf'\g<1>{SPANISH_BOT_PATH}\g<3>',
                updated
            )

    if changes and not DRY_RUN:
        backup_file(html_path)
        html_path.write_text(updated, encoding="utf-8")

    return len(changes), changes


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    folder = Path(BLOG_ES_FOLDER)

    if not folder.exists():
        print(f"ERROR: Folder not found:\n  {folder}")
        sys.exit(1)

    html_files = list(folder.rglob("*.html"))

    if not html_files:
        print(f"No HTML files found in:\n  {folder}")
        sys.exit(0)

    mode = "DRY RUN — no files will be changed" if DRY_RUN else "LIVE — files will be updated + backed up"
    print(f"\n{'='*60}")
    print(f"  update_iep_links.py  [{mode}]")
    print(f"  Scanning: {folder}")
    print(f"  Target link: {SPANISH_BOT_PATH}")
    print(f"{'='*60}\n")

    total_files   = 0
    total_changes = 0

    for html_file in sorted(html_files):
        count, changes = replace_links_in_file(html_file)
        if count:
            total_files   += 1
            total_changes += count
            rel = html_file.relative_to(folder)
            print(f"✅  {rel}  ({count} replacement{'s' if count != 1 else ''})")
            for c in changes:
                print(c)
            print()

    if total_changes == 0:
        print("No matching links found. Nothing to update.")
        print("\nIf your links use a different path, add it to PATTERNS_TO_REPLACE in this script.")
    else:
        action = "Would update" if DRY_RUN else "Updated"
        print(f"\n{action} {total_changes} link{'s' if total_changes != 1 else ''} across {total_files} file{'s' if total_files != 1 else ''}.")
        if not DRY_RUN:
            print("Original files backed up as .bak_<timestamp> in the same folder.")

    print()


if __name__ == "__main__":
    main()