"""
sync_components.py
==================
Reads navbar.html and footer.html from your site root and syncs their
content into every HTML page on the site.

Pages stay completely self-contained — nothing breaks, no JavaScript
loading tricks, no server dependencies.

Workflow
--------
1. Edit  navbar.html  in your site root  (or footer.html)
2. Run:  python sync_components.py
3. Done. All 850 pages now have the updated navbar/footer.

Usage
-----
    python sync_components.py               # sync everything
    python sync_components.py --dry-run     # preview only, no writes
    python sync_components.py --dir blog    # only one folder

Source files (edit these to update the whole site)
----------------------------------------------------
    navbar.html   — the full <header class="site-header">...</header> block
    footer.html   — the full <footer class="site-footer">...</footer> block

Optional: also put your shared <style> block in:
    shared-style.html  — the <style>...</style> block

If shared-style.html doesn't exist the style block is left as-is.
"""

import os
import re
import sys
import shutil
from pathlib import Path

# ── Folders to scan recursively for .html files ──────────────────────────────
SCAN_DIRS = [
    ".",
    "about",
    "blog",
    "contact",
    "contact-us",
    "disclaimer",
    "districts",
    "download",
    "resources",
    "store",
]

# ── Files to never touch ─────────────────────────────────────────────────────
SKIP_FILES = {
    "navbar.html",
    "footer.html",
    "shared-style.html",
    "components/navbar.html",
    "components/footer.html",
}

# ── Load source files ─────────────────────────────────────────────────────────

def load_sources(root):
    """Read navbar.html and footer.html. Extract just the relevant block from each."""

    def read(filename, pattern):
        path = root / filename
        if not path.exists():
            return None
        text = path.read_text(encoding='utf-8')
        # If the file is just the block itself, return it directly
        # If it's a full HTML page, extract the block
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else text.strip()

    navbar = read('navbar.html',
                  r'(<header\s+class="site-header">.*?</header>)')

    footer = read('footer.html',
                  r'(<footer\s+class="site-footer">.*?</footer>)')

    style = read('shared-style.html',
                 r'(<style>.*?</style>)')  # optional

    if navbar is None:
        print("ERROR: navbar.html not found in site root.")
        sys.exit(1)
    if footer is None:
        print("ERROR: footer.html not found in site root.")
        sys.exit(1)

    # The navbar.html you already have includes a footer block and scripts too
    # — extract just the header if so
    if not navbar.startswith('<header'):
        m = re.search(r'(<header\s+class="site-header">.*?</header>)',
                      navbar, re.DOTALL)
        if m:
            navbar = m.group(1).strip()

    # Same for footer.html
    if not footer.startswith('<footer'):
        m = re.search(r'(<footer\s+class="site-footer">.*?</footer>)',
                      footer, re.DOTALL)
        if m:
            footer = m.group(1).strip()

    return navbar, footer, style


# ── Per-file fix functions ────────────────────────────────────────────────────

def fix_git_conflicts(html):
    """Keep HEAD version, discard incoming."""
    new = re.sub(
        r'<{7}[^\n]*\n(.*?)={7}\n.*?>{7}[^\n]*\n?',
        r'\1', html, flags=re.DOTALL)
    return new, new != html


def fix_global_css(html):
    """Remove the /styles/global.css link that breaks styling."""
    new, n = re.subn(
        r'[ \t]*<link[^>]+/styles/global\.css[^>]*>[ \t]*\n?',
        '', html, flags=re.IGNORECASE)
    return new, n > 0


def sync_navbar(html, canonical):
    """Replace whatever <header class="site-header">...</header> is in the page."""
    new, n = re.subn(
        r'<header\s+class="site-header">.*?</header>',
        canonical, html, flags=re.DOTALL | re.IGNORECASE)
    if n == 0:
        # No header found — insert after <body>
        new = re.sub(r'(<body[^>]*>)', r'\1\n' + canonical, html,
                     count=1, flags=re.IGNORECASE)
    return new, new != html


def sync_footer(html, canonical):
    """Replace whatever <footer class="site-footer">...</footer> is in the page."""
    new, n = re.subn(
        r'<footer\s+class="site-footer">.*?</footer>',
        canonical, html, flags=re.DOTALL | re.IGNORECASE)
    if n == 0:
        # No footer found — insert before </body>
        new = html.replace('</body>', canonical + '\n</body>', 1)
    return new, new != html


def sync_style(html, canonical):
    """Replace the inline <style> block if a canonical one is provided."""
    if not canonical:
        return html, False
    new, n = re.subn(
        r'<style>.*?</style>',
        canonical, html, count=1, flags=re.DOTALL | re.IGNORECASE)
    return new, n > 0


def fix_mobile_script(html):
    """
    Deduplicate mobile-menu scripts. Keep only ONE copy of the
    DOMContentLoaded / mobile-menu-toggle handler.
    """
    pattern = re.compile(
        r'<script[^>]*>\s*document\.addEventListener\s*\(\s*[\'"]DOMContentLoaded.*?</script>',
        re.DOTALL | re.IGNORECASE)

    matches = pattern.findall(html)
    if len(matches) <= 1:
        return html, False

    # Remove all copies, then put one back before </body>
    html = pattern.sub('', html)
    html = html.replace('</body>', matches[0] + '\n</body>', 1)
    return html, True


def fix_subscribe_script(html):
    """Remove duplicate Google Script / subscribe handler blocks."""
    pattern = re.compile(
        r'<script[^>]*>.*?GOOGLE_SCRIPT_URL.*?</script>',
        re.DOTALL | re.IGNORECASE)
    matches = pattern.findall(html)
    if len(matches) <= 1:
        return html, False
    html = pattern.sub('', html)
    html = html.replace('</body>', matches[0] + '\n</body>', 1)
    return html, True


def fix_double_main(html):
    """Fix double <main> open and close tags."""
    new = re.sub(
        r'<main(?:\s[^>]*)?>\s*(<main(?:\s[^>]*)?>)',
        r'\1', html, flags=re.IGNORECASE)
    new = re.sub(r'</main>\s*</main>', '</main>', new, flags=re.IGNORECASE)
    return new, new != html


# ── Orchestrator ──────────────────────────────────────────────────────────────

def process(html, navbar, footer, style):
    changes = []

    html, c = fix_git_conflicts(html)
    if c: changes.append("resolved git conflicts")

    html, c = fix_global_css(html)
    if c: changes.append("removed /styles/global.css link")

    html, c = sync_navbar(html, navbar)
    if c: changes.append("synced navbar")

    html, c = sync_footer(html, footer)
    if c: changes.append("synced footer")

    html, c = sync_style(html, style)
    if c: changes.append("synced shared style")

    html, c = fix_mobile_script(html)
    if c: changes.append("deduplicated mobile-menu script")

    html, c = fix_subscribe_script(html)
    if c: changes.append("deduplicated subscribe script")

    html, c = fix_double_main(html)
    if c: changes.append("fixed double <main> tags")

    return html, changes


# ── File handling ─────────────────────────────────────────────────────────────

def collect_files(root, only_dir=None):
    dirs = [only_dir] if only_dir else SCAN_DIRS
    files = []
    for d in dirs:
        target = root / d
        if not target.exists():
            continue
        files.extend(sorted(target.rglob('*.html')))
    return files


def should_skip(path, root):
    rel = str(path.relative_to(root)).replace('\\', '/')
    if rel in SKIP_FILES:
        return True
    if path.suffix in ('.bak', '.orig'):
        return True
    return False


def process_file(path, root, navbar, footer, style, dry_run):
    try:
        original = path.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        print(f"  ERROR reading {path}: {e}")
        return False

    fixed, changes = process(original, navbar, footer, style)

    if not changes:
        return False

    rel = path.relative_to(root)
    print(f"  {rel}")
    for c in changes:
        print(f"    • {c}")

    if not dry_run:
        bak = path.with_suffix(path.suffix + '.bak')
        shutil.copy2(path, bak)
        path.write_text(fixed, encoding='utf-8')

    return True


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    dry_run  = '--dry-run' in sys.argv
    only_dir = None
    if '--dir' in sys.argv:
        i = sys.argv.index('--dir')
        if i + 1 < len(sys.argv):
            only_dir = sys.argv[i + 1]

    root = Path('.')
    navbar, footer, style = load_sources(root)

    print(f"\n{'='*60}")
    print("sync_components.py")
    print("  navbar.html  →", "loaded" if navbar else "MISSING")
    print("  footer.html  →", "loaded" if footer else "MISSING")
    print("  shared-style →", "loaded" if style else "not found (skipping style sync)")
    if dry_run:
        print("  MODE: DRY RUN — no files will be written")
    print(f"{'='*60}\n")

    files   = collect_files(root, only_dir)
    files   = [f for f in files if not should_skip(f, root)]
    print(f"Scanning {len(files)} HTML files...\n")

    updated = skipped = 0
    for f in files:
        if process_file(f, root, navbar, footer, style, dry_run):
            updated += 1
        else:
            skipped += 1

    print(f"\n{'='*60}")
    print(f"Done.  {updated} updated,  {skipped} already in sync.")
    if not dry_run and updated:
        print("Originals backed up as .bak files.")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()