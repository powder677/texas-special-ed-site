"""
Trailing Slash Remover for Canonical Tags
==========================================
Removes trailing slashes from canonical URLs in all HTML files.

BEFORE: <link rel="canonical" href="https://www.texasspecialed.com/districts/houston-isd/">
AFTER:  <link rel="canonical" href="https://www.texasspecialed.com/districts/houston-isd">

Homepage is left untouched:
KEEP:   <link rel="canonical" href="https://www.texasspecialed.com/">

Usage:
    python fix_trailing_slash.py --dir . --dry-run
    python fix_trailing_slash.py --dir .
"""

import os
import re
import shutil
import argparse
from datetime import datetime

BACKUP_DIR = "_trailing_slash_backups"

CANONICAL_RE = re.compile(
    r'(<link[^>]+rel=["\']canonical["\'][^>]+href=["\'])([^"\']+)(["\'][^>]*>)',
    re.IGNORECASE
)
CANONICAL_RE2 = re.compile(
    r'(<link[^>]+href=["\'])([^"\']+)(["\'][^>]+rel=["\']canonical["\'][^>]*>)',
    re.IGNORECASE
)

HOMEPAGE_URLS = {
    "https://www.texasspecialed.com/",
    "https://texasspecialed.com/",
}


def fix_url(url):
    """Remove trailing slash unless it's the homepage."""
    url = url.strip()
    if url in HOMEPAGE_URLS:
        return url  # leave homepage alone
    if url.endswith("/"):
        url = url.rstrip("/")
    return url


def process_file(filepath, dry_run=False):
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        original = f.read()

    changes = []
    modified = original

    def replacer(match):
        prefix  = match.group(1)
        old_url = match.group(2)
        suffix  = match.group(3)
        new_url = fix_url(old_url)
        if new_url != old_url:
            changes.append((old_url, new_url))
        return prefix + new_url + suffix

    modified = CANONICAL_RE.sub(replacer, modified)
    modified = CANONICAL_RE2.sub(replacer, modified)

    if changes and not dry_run:
        # Backup first
        rel      = os.path.relpath(filepath)
        backup   = os.path.join(BACKUP_DIR, rel)
        os.makedirs(os.path.dirname(backup), exist_ok=True)
        shutil.copy2(filepath, backup)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(modified)

    return changes


def main():
    parser = argparse.ArgumentParser(description="Remove trailing slashes from canonical URLs.")
    parser.add_argument("--dir",     required=True, help="Root folder of your site")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no files changed")
    args = parser.parse_args()

    site_dir = os.path.abspath(args.dir)
    dry_run  = args.dry_run

    if not os.path.isdir(site_dir):
        print(f"ERROR: Directory not found: {site_dir}")
        return

    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"\n{'='*55}")
    print(f"  Trailing Slash Fixer — {mode}")
    print(f"  Folder  : {site_dir}")
    print(f"  Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}\n")

    total_files   = 0
    changed_files = 0
    total_changes = 0

    for root, dirs, files in os.walk(site_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != BACKUP_DIR]

        for filename in files:
            if not filename.endswith(".html"):
                continue

            filepath = os.path.join(root, filename)
            total_files += 1

            try:
                changes = process_file(filepath, dry_run=dry_run)
                if changes:
                    changed_files += 1
                    total_changes += len(changes)
                    rel    = os.path.relpath(filepath, site_dir)
                    status = "WOULD FIX" if dry_run else "FIXED"
                    print(f"  [{status}] {rel}")
                    for old, new in changes:
                        print(f"    - OLD: {old}")
                        print(f"      NEW: {new}")
            except Exception as e:
                print(f"  [ERROR] {filepath}: {e}")

    print(f"\n{'='*55}")
    print(f"  HTML files scanned  : {total_files}")
    print(f"  Files {'to update' if dry_run else 'updated'}    : {changed_files}")
    print(f"  Slashes removed     : {total_changes}")
    if not dry_run and changed_files > 0:
        print(f"  Backups saved to    : {BACKUP_DIR}/")
    print(f"{'='*55}\n")

    if dry_run and changed_files > 0:
        print("  Run without --dry-run to apply changes.\n")
    elif not dry_run and changed_files > 0:
        print("  Done. All trailing slashes removed.\n")
    else:
        print("  Nothing to change — all canonicals already clean.\n")


if __name__ == "__main__":
    main()