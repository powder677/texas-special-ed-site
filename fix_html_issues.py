"""
fix_html_issues.py  (v2)
========================
Fixes ALL known issues across TexasSpecialEd HTML files:

  Fix 1 : Remove conflicting  <link href="/styles/global.css" ...>  stylesheet
  Fix 2 : Resolve Git merge conflict markers (keeps HEAD version, drops other)
  Fix 3 : Collapse double opening <main> tags (handles any class combinations)
  Fix 4 : Collapse double closing </main></main> -> </main>
  Fix 5 : Remove duplicate <script> blocks (identical content appearing twice)

Usage
-----
  Place this script in the ROOT of your website folder, then run:

      python fix_html_issues.py           # apply fixes (writes .bak backups)
      python fix_html_issues.py --dry-run # preview only, no files written
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

# ── Individual fix functions ─────────────────────────────────────────────────

def fix_global_css(content):
    """Remove the conflicting /styles/global.css <link> tag."""
    pattern = re.compile(
        r'[ \t]*<link\s+href=["\']\/styles\/global\.css["\']\s+rel=["\']stylesheet["\']\s*\/?>[ \t]*\n?',
        re.IGNORECASE,
    )
    result, n = pattern.subn("", content)
    return result, n


def fix_git_conflicts(content):
    """
    Resolve Git merge conflict markers.
    Keeps the HEAD section (between <<<<<<< and =======).
    Discards the incoming section (between ======= and >>>>>>>).
    """
    pattern = re.compile(
        r'<{7}[^\n]*\n'   # <<<<<<< HEAD  (any branch label)
        r'(.*?)'           # HEAD content  (captured, keep this)
        r'={7}\n'          # =======
        r'.*?'             # incoming content (discarded)
        r'>{7}[^\n]*\n?',  # >>>>>>> hash
        re.DOTALL,
    )
    result, n = pattern.subn(r'\1', content)
    return result, n


def fix_double_main_open(content):
    """
    Collapse two consecutive opening <main> tags into one.

    Handles all variants:
      <main class="main-container"><main>
      <main class="main-container"><main class="store-page">
      <main class="X">  <main class="Y">   (with whitespace between)

    Strategy: when two <main ...> tags appear back-to-back (optional
    whitespace allowed), keep only the INNER tag so the page-specific
    class is preserved.
    """
    pattern = re.compile(
        r'<main(?:\s[^>]*)?>[ \t]*\n?[ \t]*(<main(?:\s[^>]*)?>)',
        re.IGNORECASE,
    )
    result, n = pattern.subn(r'\1', content)
    return result, n


def fix_double_main_close(content):
    """Collapse </main>  </main> -> </main>."""
    pattern = re.compile(r'<\/main>[ \t]*\n?[ \t]*<\/main>', re.IGNORECASE)
    result, n = pattern.subn('</main>', content)
    return result, n


def fix_duplicate_scripts(content):
    """
    Remove exact duplicate <script>...</script> blocks.
    The first occurrence is kept; subsequent identical copies are removed.
    """
    pattern = re.compile(r'(<script\b[^>]*>)(.*?)(</script>)', re.DOTALL | re.IGNORECASE)
    seen = set()
    removed = [0]   # use list so nested fn can mutate

    def replace(m):
        key = m.group(2).strip()   # normalised inner text as the identity key
        if key in seen:
            removed[0] += 1
            return ""              # drop duplicate
        seen.add(key)
        return m.group(0)          # keep first occurrence

    result = pattern.sub(replace, content)
    return result, removed[0]


# ── Orchestrator ─────────────────────────────────────────────────────────────

def apply_all_fixes(content):
    """Run every fix in order. Returns (fixed_content, list_of_change_descriptions)."""
    changes = []

    content, n = fix_global_css(content)
    if n:
        changes.append(f"  [Fix 1] Removed {n} /styles/global.css <link> tag(s)")

    content, n = fix_git_conflicts(content)
    if n:
        changes.append(f"  [Fix 2] Resolved {n} Git merge conflict block(s) (kept HEAD version)")

    content, n = fix_double_main_open(content)
    if n:
        changes.append(f"  [Fix 3] Collapsed {n} double opening <main> tag(s)")

    content, n = fix_double_main_close(content)
    if n:
        changes.append(f"  [Fix 4] Collapsed {n} double closing </main> tag(s)")

    content, n = fix_duplicate_scripts(content)
    if n:
        changes.append(f"  [Fix 5] Removed {n} duplicate <script> block(s)")

    return content, changes


def process_file(filepath, dry_run=False):
    if not filepath.exists():
        print(f"  [SKIP] Not found: {filepath}")
        return False

    try:
        original = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [ERROR] Cannot read {filepath}: {e}")
        return False

    fixed, changes = apply_all_fixes(original)

    if not changes:
        print(f"  [OK]   No changes needed: {filepath}")
        return False

    print(f"\nUpdating {filepath}...")
    for c in changes:
        print(c)

    if not dry_run:
        backup = filepath.with_suffix(filepath.suffix + ".bak")
        shutil.copy2(filepath, backup)
        try:
            filepath.write_text(fixed, encoding="utf-8")
            print(f"  [SAVED] Backup -> {backup.name}")
        except Exception as e:
            print(f"  [ERROR] Cannot write {filepath}: {e}")
            return False
    else:
        print("  [DRY RUN] No file written.")

    return True


def main():
    dry_run = "--dry-run" in sys.argv
    root = Path(".")

    if dry_run:
        print("=" * 60)
        print("DRY RUN MODE - no files will be modified")
        print("=" * 60)

    changed = skipped = 0

    for rel in TARGET_FILES:
        path = root / Path(rel.replace("\\", os.sep))
        if process_file(path, dry_run):
            changed += 1
        else:
            skipped += 1

    print("\n" + "=" * 60)
    print(f"Done.  {changed} file(s) updated,  {skipped} unchanged/skipped.")
    if not dry_run and changed:
        print("Original files backed up as <filename>.bak")
    print("=" * 60)


if __name__ == "__main__":
    main()