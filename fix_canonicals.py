"""
Canonical URL Cleaner for TexasSpecialEd.com
=============================================
Scans all .html files in your site folder and rewrites canonical tags
from .html URLs to clean URLs.

BEFORE: <link rel="canonical" href="https://www.texasspecialed.com/districts/houston-isd/ard-process-guide.html">
AFTER:  <link rel="canonical" href="https://www.texasspecialed.com/districts/houston-isd/ard-process-guide">

Usage:
    python fix_canonicals.py --dir /path/to/your/site
    python fix_canonicals.py --dir /path/to/your/site --dry-run   (preview only, no changes)
"""

import os
import re
import argparse
import shutil
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BASE_URL    = "https://www.texasspecialed.com"
BACKUP_DIR  = "_canonical_backups"   # created next to your site folder
# ──────────────────────────────────────────────────────────────────────────────

CANONICAL_RE = re.compile(
    r'(<link\s[^>]*rel=["\']canonical["\'][^>]*href=["\'])([^"\']+)(["\'][^>]*>)',
    re.IGNORECASE
)
# Also catch href-before-rel order
CANONICAL_RE2 = re.compile(
    r'(<link\s[^>]*href=["\'])([^"\']+)(["\'][^>]*rel=["\']canonical["\'][^>]*>)',
    re.IGNORECASE
)


def clean_canonical_url(url):
    """
    Convert a URL to its canonical clean form:
    - Strip .html extension
    - Ensure www
    - No trailing slash (except homepage)
    - Strip query strings and fragments
    """
    # Strip fragment and query
    url = url.split("#")[0].split("?")[0].strip()

    # Ensure www
    url = re.sub(r'https?://(www\.)?texasspecialed\.com',
                 'https://www.texasspecialed.com', url)

    # Strip .html
    if url.endswith(".html"):
        url = url[:-5]

    # Strip trailing slash unless it's the homepage
    path = url.replace("https://www.texasspecialed.com", "")
    if path != "/" and url.endswith("/"):
        url = url.rstrip("/")

    return url


def fix_canonicals_in_file(filepath, dry_run=False):
    """Read a file, fix canonical tags, write back. Returns change summary."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        original = f.read()

    modified = original
    changes = []

    def replace_canonical(match):
        prefix  = match.group(1)
        old_url = match.group(2)
        suffix  = match.group(3)
        new_url = clean_canonical_url(old_url)
        if new_url != old_url:
            changes.append((old_url, new_url))
        return prefix + new_url + suffix

    modified = CANONICAL_RE.sub(replace_canonical, modified)
    modified = CANONICAL_RE2.sub(replace_canonical, modified)

    if changes and not dry_run:
        # Backup original first
        rel_path = os.path.relpath(filepath)
        backup_path = os.path.join(BACKUP_DIR, rel_path)
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(filepath, backup_path)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(modified)

    return changes


def main():
    parser = argparse.ArgumentParser(description="Fix canonical URLs in HTML files.")
    parser.add_argument("--dir",     required=True, help="Root directory of your site")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing files")
    args = parser.parse_args()

    site_dir = os.path.abspath(args.dir)
    dry_run  = args.dry_run

    if not os.path.isdir(site_dir):
        print(f"❌ Directory not found: {site_dir}")
        return

    mode = "DRY RUN (no files changed)" if dry_run else "LIVE (files will be modified)"
    print(f"\n{'='*60}")
    print(f"  Canonical URL Fixer — {mode}")
    print(f"  Site dir : {site_dir}")
    print(f"  Started  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    total_files   = 0
    changed_files = 0
    total_changes = 0
    skipped_files = 0

    for root, dirs, files in os.walk(site_dir):
        # Skip hidden folders and backup dir
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != BACKUP_DIR]

        for filename in files:
            if not filename.endswith(".html"):
                continue

            filepath = os.path.join(root, filename)
            total_files += 1

            try:
                changes = fix_canonicals_in_file(filepath, dry_run=dry_run)
                if changes:
                    changed_files += 1
                    total_changes += len(changes)
                    rel = os.path.relpath(filepath, site_dir)
                    status = "WOULD UPDATE" if dry_run else "UPDATED"
                    print(f"  [{status}] {rel}")
                    for old, new in changes:
                        print(f"    - OLD: {old}")
                        print(f"      NEW: {new}")
            except Exception as e:
                print(f"  [ERROR] {filepath}: {e}")
                skipped_files += 1

    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  HTML files scanned : {total_files}")
    print(f"  Files {'to update' if dry_run else 'updated'}   : {changed_files}")
    print(f"  Canonicals fixed   : {total_changes}")
    print(f"  Errors skipped     : {skipped_files}")
    if not dry_run and changed_files > 0:
        print(f"  Backups saved to   : {os.path.abspath(BACKUP_DIR)}/")
    print(f"{'='*60}\n")

    if dry_run and changed_files > 0:
        print("  ✅ Dry run complete. Run without --dry-run to apply changes.\n")
    elif not dry_run and changed_files > 0:
        print("  ✅ All canonicals updated. Originals backed up.\n")
    else:
        print("  ✅ No canonical changes needed — all URLs already clean.\n")


if __name__ == "__main__":
    main()