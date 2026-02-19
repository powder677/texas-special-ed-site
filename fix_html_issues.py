"""
fix_html_issues.py
==================
Fixes two issues across all specified HTML files:

1. Removes the duplicate/conflicting stylesheet:
      <link href="/styles/global.css" rel="stylesheet"/>

2. Fixes the broken double <main> tag:
      <main class="main-container"><main>  →  <main class="main-container">
   And the corresponding double closing tag:
      </main></main>  →  </main>

Usage:
    Place this script in the ROOT of your website folder and run:
        python fix_html_issues.py

    Dry-run (preview changes without writing):
        python fix_html_issues.py --dry-run
"""

import os
import re
import sys
import shutil
from pathlib import Path

# ── Files to process ────────────────────────────────────────────────────────
TARGET_FILES = [
    r"footer.html",
    r"index.html",
    r"navbar.html",
    r"texas-specialed-shop.html",
    r"about\index.html",
    r"blog\10-questions-to-ask-at-ard-meeting.html",
    r"blog\how-to-disagree-at-ard-meeting.html",
    r"blog\how-to-write-measurable-iep-goals.html",
    r"blog\independent-educational-evaluation-texas.html",
    r"blog\index.html",
    r"blog\texas-parent-rights-special-education.html",
    r"blog\understanding-fiie-texas.html",
    r"blog\what-to-do-when-school-denies-evaluation.html",
    r"contact\index.html",
    r"contact-us\index.html",
    r"disclaimer\index.html",
    r"resources\index.html",
    r"store\index.html",
    r"download\accom-enc-2j7f.html",
    r"download\all-access-8d4z.html",
    r"download\ard-prep-3n8w.html",
    r"download\autism-ard-6r3v.html",
    r"download\bx-defense-5t1q.html",
    r"download\dys-toolkit-7m2p.html",
    r"download\ef-mastery-9k4x.html",
]

# ── Fixes ────────────────────────────────────────────────────────────────────

def fix_content(content: str, filepath: str) -> tuple[str, list[str]]:
    """Apply all fixes to the file content. Returns (new_content, list_of_changes)."""
    changes = []
    original = content

    # Fix 1: Remove the conflicting global.css stylesheet link
    # Matches the line with optional whitespace/newline
    pattern_css = re.compile(
        r'[ \t]*<link\s+href=["\']\/styles\/global\.css["\']\s+rel=["\']stylesheet["\']\s*\/?>[ \t]*\n?',
        re.IGNORECASE
    )
    new_content, count = pattern_css.subn("", content)
    if count:
        changes.append(f"  [Fix 1] Removed {count} instance(s) of /styles/global.css <link>")
        content = new_content

    # Fix 2a: Fix double opening <main> tag
    # Handles: <main class="main-container"><main> (with optional whitespace/attrs on inner tag)
    pattern_main_open = re.compile(
        r'(<main\s[^>]*>)\s*<main\s*>',
        re.IGNORECASE
    )
    new_content, count = pattern_main_open.subn(r'\1', content)
    if count:
        changes.append(f"  [Fix 2a] Fixed {count} double opening <main> tag(s)")
        content = new_content

    # Fix 2b: Fix double closing </main></main> → </main>
    # Only collapse if they appear directly adjacent (no content between)
    pattern_main_close = re.compile(
        r'<\/main>\s*<\/main>',
        re.IGNORECASE
    )
    new_content, count = pattern_main_close.subn('</main>', content)
    if count:
        changes.append(f"  [Fix 2b] Fixed {count} double closing </main> tag(s)")
        content = new_content

    return content, changes


def process_file(filepath: Path, dry_run: bool = False) -> bool:
    """Read, fix, and optionally write a single file. Returns True if changes were made."""
    if not filepath.exists():
        print(f"  [SKIP] File not found: {filepath}")
        return False

    try:
        original_content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [ERROR] Could not read {filepath}: {e}")
        return False

    fixed_content, changes = fix_content(original_content, str(filepath))

    if not changes:
        print(f"  [OK] No changes needed: {filepath}")
        return False

    print(f"\nUpdating {filepath}...")
    for change in changes:
        print(change)

    if not dry_run:
        # Back up original
        backup_path = filepath.with_suffix(filepath.suffix + ".bak")
        shutil.copy2(filepath, backup_path)

        try:
            filepath.write_text(fixed_content, encoding="utf-8")
            print(f"  [SAVED] (backup at {backup_path.name})")
        except Exception as e:
            print(f"  [ERROR] Could not write {filepath}: {e}")
            return False
    else:
        print(f"  [DRY RUN] No file written.")

    return True


def main():
    dry_run = "--dry-run" in sys.argv
    root = Path(".")  # Run from the website root folder

    if dry_run:
        print("=" * 60)
        print("DRY RUN MODE — no files will be modified")
        print("=" * 60)

    total_files = len(TARGET_FILES)
    changed = 0
    skipped = 0

    for rel_path in TARGET_FILES:
        # Normalise path separators for the current OS
        filepath = root / Path(rel_path.replace("\\", os.sep))
        was_changed = process_file(filepath, dry_run=dry_run)
        if was_changed:
            changed += 1
        else:
            skipped += 1

    print("\n" + "=" * 60)
    print(f"Done. {changed} file(s) updated, {skipped} file(s) skipped.")
    if not dry_run and changed:
        print("Backup copies saved with .bak extension next to each changed file.")
    print("=" * 60)


if __name__ == "__main__":
    main()