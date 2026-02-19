"""
migrate_to_components.py
========================
Converts every HTML page on the site from copy-pasted navbar/footer
to the shared component system.

What it does to each file
--------------------------
1. Removes the hardcoded <header class="site-header">...</header> block
2. Removes the hardcoded <footer class="site-footer">...</footer> block
3. Removes ALL inline <script> blocks (mobile menu, subscribe, duplicates)
4. Removes the inline <style> block  (styles live in /style.css already)
5. Removes the extra /styles/global.css link tag
6. Resolves any Git merge conflict markers (keeps HEAD version)
7. Collapses double <main> opening tags
8. Collapses double </main> closing tags
9. Adds  <script src="/components/loader.js" defer></script>  before </head>
   (only once, skipped if already present)

What it does NOT touch
-----------------------
- Page-specific content inside <main>
- <title>, <meta>, <link href="/style.css">, schema JSON-LD
- Anything outside the navbar/footer/script patterns

Before running
--------------
Make sure these files exist in your site root:
  /components/navbar.html
  /components/footer.html
  /components/loader.js

Usage
-----
  # From your site root:
  python migrate_to_components.py             # fix everything
  python migrate_to_components.py --dry-run   # preview only, no writes
  python migrate_to_components.py --dir blog  # only process one folder
"""

import os
import re
import sys
import shutil
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

LOADER_TAG = '<script src="/components/loader.js" defer></script>'

# Folders to scan (relative to the site root where you run this script).
# Every .html file inside these folders (recursively) will be processed.
SCAN_DIRS = [
    ".",          # root html files (index.html, etc.)
    "about",
    "blog",
    "contact",
    "contact-us",
    "disclaimer",
    "districts",  # all 850 district pages live here
    "download",
    "resources",
    "store",
]

# Files to explicitly skip (relative paths from site root)
SKIP_FILES = {
    "components/navbar.html",
    "components/footer.html",
    "components/loader.js",
    "navbar.html",
    "footer.html",
}

# ── Fix functions ─────────────────────────────────────────────────────────────

def fix_git_conflicts(html):
    """Keep HEAD version of Git merge conflict blocks, discard incoming."""
    n_before = html.count("<<<<<<<")
    html = re.sub(
        r'<{7}[^\n]*\n(.*?)={7}\n.*?>{7}[^\n]*\n?',
        r'\1', html, flags=re.DOTALL)
    return html, html.count("<<<<<<<") < n_before

def fix_global_css(html):
    """Remove the /styles/global.css link that conflicts with /style.css."""
    new, n = re.subn(
        r'[ \t]*<link[^>]+/styles/global\.css[^>]*>[ \t]*\n?',
        '', html, flags=re.IGNORECASE)
    return new, n > 0

def strip_header(html):
    """Remove the hardcoded <header class="site-header">...</header>."""
    new, n = re.subn(
        r'\n?[ \t]*<header\s+class="site-header">.*?</header>[ \t]*\n?',
        '\n', html, flags=re.DOTALL | re.IGNORECASE)
    return new, n > 0

def strip_footer(html):
    """Remove the hardcoded <footer class="site-footer">...</footer>."""
    new, n = re.subn(
        r'\n?[ \t]*<footer\s+class="site-footer">.*?</footer>[ \t]*\n?',
        '\n', html, flags=re.DOTALL | re.IGNORECASE)
    return new, n > 0

def strip_inline_style(html):
    """Remove the big copy-pasted <style>...</style> block."""
    new, n = re.subn(
        r'\n?[ \t]*<style>.*?</style>[ \t]*\n?',
        '\n', html, flags=re.DOTALL | re.IGNORECASE)
    return new, n > 0

def strip_inline_scripts(html):
    """
    Remove all inline <script> blocks.
    Keeps only:
      - <script type="application/ld+json"> (structured data, keep these)
      - <script src="..."> external scripts (keep these)
    Removes:
      - All inline JS (mobile menu, subscribe handler, duplicates, etc.)
    """
    def keep(m):
        tag = m.group(1)
        # Keep ld+json and external src= scripts
        if 'application/ld+json' in tag or 'src=' in tag:
            return m.group(0)
        return ''

    new = re.sub(
        r'(<script\b[^>]*>).*?</script>',
        keep, html, flags=re.DOTALL | re.IGNORECASE)
    changed = new != html
    # Clean up blank lines left behind
    new = re.sub(r'\n{3,}', '\n\n', new)
    return new, changed

def add_loader(html):
    """Add the loader.js script tag before </head> if not already present."""
    if LOADER_TAG in html:
        return html, False
    html = html.replace('</head>', f'  {LOADER_TAG}\n</head>', 1)
    return html, True

def fix_double_main_open(html):
    """Collapse <main X><main Y> → keep the inner tag only."""
    new, n = re.subn(
        r'<main(?:\s[^>]*)?>\s*(<main(?:\s[^>]*)?>)',
        r'\1', html, flags=re.IGNORECASE)
    return new, n > 0

def fix_double_main_close(html):
    """Collapse </main></main> → </main>."""
    new, n = re.subn(
        r'</main>\s*</main>',
        '</main>', html, flags=re.IGNORECASE)
    return new, n > 0

# ── Orchestrator ──────────────────────────────────────────────────────────────

def process(html):
    """Apply all fixes. Returns (fixed_html, list_of_change_labels)."""
    changes = []

    html, changed = fix_git_conflicts(html)
    if changed: changes.append("resolved git conflicts")

    html, changed = fix_global_css(html)
    if changed: changes.append("removed /styles/global.css link")

    html, changed = strip_header(html)
    if changed: changes.append("stripped hardcoded <header>")

    html, changed = strip_footer(html)
    if changed: changes.append("stripped hardcoded <footer>")

    html, changed = strip_inline_style(html)
    if changed: changes.append("stripped inline <style>")

    html, changed = strip_inline_scripts(html)
    if changed: changes.append("stripped inline <script> blocks")

    html, changed = add_loader(html)
    if changed: changes.append("added loader.js tag")

    html, changed = fix_double_main_open(html)
    if changed: changes.append("fixed double <main>")

    html, changed = fix_double_main_close(html)
    if changed: changes.append("fixed double </main>")

    return html, changes

# ── File walker ───────────────────────────────────────────────────────────────

def should_skip(path, root):
    rel = str(path.relative_to(root)).replace("\\", "/")
    if rel in SKIP_FILES:
        return True
    # Skip backup files
    if path.suffix in ('.bak', '.orig'):
        return True
    return False

def process_file(path, root, dry_run):
    try:
        original = path.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        print(f"  ERROR reading {path}: {e}")
        return False

    fixed, changes = process(original)

    if not changes:
        return False

    rel = path.relative_to(root)
    print(f"\n  {rel}")
    for c in changes:
        print(f"    • {c}")

    if not dry_run:
        bak = path.with_suffix(path.suffix + '.bak')
        shutil.copy2(path, bak)
        path.write_text(fixed, encoding='utf-8')

    return True

def collect_files(root, only_dir=None):
    files = []
    dirs = [only_dir] if only_dir else SCAN_DIRS
    for d in dirs:
        target = root / d
        if not target.exists():
            continue
        if target.is_file() and target.suffix == '.html':
            files.append(target)
        else:
            files.extend(sorted(target.rglob('*.html')))
    return files

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    dry_run  = '--dry-run'  in sys.argv
    only_dir = None

    # Support:  python migrate_to_components.py --dir blog
    if '--dir' in sys.argv:
        idx = sys.argv.index('--dir')
        if idx + 1 < len(sys.argv):
            only_dir = sys.argv[idx + 1]

    root = Path('.')

    # Sanity check — make sure components exist
    missing = []
    for f in ['components/navbar.html', 'components/footer.html', 'components/loader.js']:
        if not (root / f).exists():
            missing.append(f)
    if missing:
        print("ERROR — these files are missing from your site root:")
        for f in missing:
            print(f"  {f}")
        print("\nCreate them before running this script.")
        sys.exit(1)

    mode = "DRY RUN — no files will be written" if dry_run else "LIVE — files will be updated"
    print(f"\n{'='*60}")
    print(f"migrate_to_components.py  ({mode})")
    print(f"{'='*60}")

    files = collect_files(root, only_dir)
    files = [f for f in files if not should_skip(f, root)]
    print(f"Found {len(files)} HTML files to check")

    updated = skipped = 0
    for f in files:
        if process_file(f, root, dry_run):
            updated += 1
        else:
            skipped += 1

    print(f"\n{'='*60}")
    print(f"Done.  {updated} updated,  {skipped} already clean / skipped.")
    if not dry_run and updated:
        print("Backups saved as .bak files alongside each changed file.")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()