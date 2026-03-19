"""
fix_site.py
TexasSpecialEd.com — Link fixer + Nav standardizer
====================================================

Run from anywhere:
    python fix_site.py

Or point it at a specific root:
    python fix_site.py --root "C:/Users/elisa/OneDrive/Documents/texas-special-ed-site"

What it does:
  1. Walks every .html file under SITE_ROOT
  2. Figures out each file's depth so relative links are correct
  3. Replaces (or injects) the <nav> block with the standardized nav
  4. Fixes any broken bot/tool links to point at tools/tefa-scan/index.html
  5. Fixes any broken TEFA hub links
  6. Writes a backup (.bak) before touching each file
  7. Prints a full report of every change made
"""

import os
import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# ══════════════════════════════════════════════════════════════
#  CONFIG — edit these if your folder names differ
# ══════════════════════════════════════════════════════════════

SITE_ROOT = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"

# The standardized nav items in order.
# Each entry: (label, href_from_root, extra_classes, is_cta)
# href_from_root uses forward slashes, relative to site root.
# The script converts to the correct relative path per file depth.
NAV_ITEMS = [
    # label                  root-relative href              extra_css         is_cta
    ("Districts",            "districts/index.html",          "",               False),
    ("Spanish Districts",    "districts/es-index.html",          "",               False),
    ("Articles",             "blog/index.html",           "",               False),
    ("About",                "about/index.html",              "",               False),
    ("Contact",              "contact/index.html",            "",               False),
    ("Resources",            "resources/index.html",          "",               False),
    ("TEFA",                 "tefa/en/index.html",            "nav-tefa",       False),
    ("Get Your Letter",      "tools/tefa-scan/index.html",    "nav-cta",        True),
]

# Logo links back to site root
LOGO_TEXT = "TexasSpecialEd.com"
LOGO_HREF_FROM_ROOT = "index.html"

# The bot page (tefa-scan) — any href pointing somewhere broken
# that should resolve to this will be fixed
BOT_CANONICAL = "tools/tefa-scan/index.html"

# TEFA hub canonical
TEFA_HUB_EN = "tefa/en/index.html"
TEFA_HUB_ES = "tefa/es/index.html"

# Patterns that look like bot links gone wrong
BOT_LINK_PATTERNS = [
    r'href=["\']#tefa-bot["\']',
    r'href=["\'].*?tefa.?scan.*?["\']',
    r'href=["\'].*?readiness.?check.*?["\']',
    r'href=["\'].*?tefa.?bot.*?["\']',
    r'href=["\']#lead-magnet["\']',   # these should go to the bot page
]

# File extensions to process
HTML_EXTENSIONS = {".html", ".htm"}

# Skip these folders entirely
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "backups"}

# ══════════════════════════════════════════════════════════════
#  NAV TEMPLATE
#  Uses {{LOGO_HREF}} and {{NAV_ITEMS_HTML}} as placeholders
#  which are filled in per-file based on depth.
# ══════════════════════════════════════════════════════════════

NAV_CSS = """
<style id="nav-std-css">
/* ── Standardized TexasSpecialEd Nav ── */
.site-nav{
  background:#0E2340;
  position:sticky;top:0;z-index:200;
  box-shadow:0 2px 12px rgba(0,0,0,.25);
  font-family:'DM Sans',system-ui,sans-serif;
}
.site-nav__inner{
  display:flex;align-items:stretch;
  justify-content:space-between;
  height:56px;
  max-width:1100px;margin:0 auto;padding:0 24px;
}
.site-nav__logo{
  font-family:'DM Serif Display',Georgia,serif;
  font-size:1.1rem;color:#fff;
  display:flex;align-items:center;
  text-decoration:none;white-space:nowrap;
  flex-shrink:0;padding-right:12px;
}
.site-nav__links{display:flex;align-items:stretch;gap:0}
.site-nav__link{
  display:flex;align-items:center;padding:0 14px;
  color:rgba(255,255,255,.7);font-size:.85rem;font-weight:500;
  border-bottom:3px solid transparent;
  text-decoration:none;white-space:nowrap;
  transition:color .18s,background .18s;
}
.site-nav__link:hover{
  color:#fff;background:rgba(255,255,255,.06);
  text-decoration:none;
}
/* TEFA — pulsing amber tab */
.site-nav__link.nav-tefa{
  background:rgba(201,99,10,.18);
  color:#FFB366 !important;
  border-bottom-color:#C9630A;
  font-weight:600;gap:7px;
}
.site-nav__link.nav-tefa:hover{
  background:rgba(201,99,10,.32)!important;
  color:#FFD0A0!important;
}
.nav-pulse{
  width:7px;height:7px;border-radius:50%;
  background:#C9630A;flex-shrink:0;
  position:relative;display:inline-block;
}
.nav-pulse::before{
  content:'';position:absolute;top:50%;left:50%;
  transform:translate(-50%,-50%);
  width:7px;height:7px;border-radius:50%;
  background:#C9630A;
  animation:nav-pulse 1.8s ease-out infinite;
}
@keyframes nav-pulse{
  0%{transform:translate(-50%,-50%) scale(1);opacity:.9}
  70%{transform:translate(-50%,-50%) scale(3.2);opacity:0}
  100%{transform:translate(-50%,-50%) scale(1);opacity:0}
}
/* Get Your Letter — CTA button */
.site-nav__link.nav-cta{
  background:#0D7A6B;color:#fff!important;
  font-weight:600;border-radius:0;
  padding:0 18px;
  border-bottom:3px solid transparent;
}
.site-nav__link.nav-cta:hover{background:#084F46!important}
/* Hamburger (mobile) */
.site-nav__hamburger{
  display:none;flex-direction:column;justify-content:center;
  gap:5px;padding:0 12px;cursor:pointer;background:none;border:none;
}
.site-nav__hamburger span{
  display:block;width:22px;height:2px;background:rgba(255,255,255,.8);
  border-radius:2px;transition:all .2s;
}
@media(max-width:768px){
  .site-nav__links{display:none;flex-direction:column;position:absolute;
    top:56px;left:0;right:0;background:#0E2340;padding:8px 0;z-index:300;
    box-shadow:0 8px 20px rgba(0,0,0,.3);}
  .site-nav__links.open{display:flex}
  .site-nav__link{padding:12px 24px;border-bottom:none;border-left:3px solid transparent;}
  .site-nav__link.nav-tefa{border-left-color:#C9630A}
  .site-nav__link.nav-cta{margin:8px 16px;border-radius:6px;justify-content:center}
  .site-nav__hamburger{display:flex}
  .site-nav__inner{position:relative}
}
</style>
"""

NAV_HTML_TEMPLATE = """<nav class="site-nav" role="navigation" aria-label="Main navigation">
  <div class="site-nav__inner">
    <a href="{logo_href}" class="site-nav__logo">{logo_text}</a>
    <button class="site-nav__hamburger" aria-label="Toggle menu" onclick="(function(){{var l=document.querySelector('.site-nav__links');l.classList.toggle('open')}})()">
      <span></span><span></span><span></span>
    </button>
    <div class="site-nav__links">
{nav_items}
    </div>
  </div>
</nav>"""

# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════

def relative_path(from_file: Path, to_root_relative: str, root: Path) -> str:
    """
    Given a file's absolute path and a root-relative target path,
    return the correct relative href.

    E.g.  from  root/tefa/en/post.html
          to    root/tools/tefa-scan/index.html
          →     ../../tools/tefa-scan/index.html
    """
    from_dir = from_file.parent
    target   = root / to_root_relative.replace("/", os.sep)
    try:
        rel = os.path.relpath(target, from_dir)
        # Always use forward slashes in HTML
        return rel.replace(os.sep, "/")
    except ValueError:
        # Different drive on Windows — fall back to root-relative
        return "/" + to_root_relative


def build_nav_html(file_path: Path, root: Path) -> str:
    """Build the full nav HTML for a specific file."""
    logo_href = relative_path(file_path, LOGO_HREF_FROM_ROOT, root)

    items_html = []
    for (label, href_root, css_class, is_cta) in NAV_ITEMS:
        href = relative_path(file_path, href_root, root)
        classes = "site-nav__link"
        if css_class:
            classes += " " + css_class

        if css_class == "nav-tefa":
            # Add pulse dot for TEFA
            inner = f'<span class="nav-pulse" aria-hidden="true"></span>{label}'
        else:
            inner = label

        items_html.append(
            f'      <a href="{href}" class="{classes}">{inner}</a>'
        )

    nav = NAV_HTML_TEMPLATE.format(
        logo_href=logo_href,
        logo_text=LOGO_TEXT,
        nav_items="\n".join(items_html),
    )
    return nav


def build_full_nav_block(file_path: Path, root: Path) -> str:
    """CSS + nav element combined."""
    return NAV_CSS + "\n" + build_nav_html(file_path, root)


def has_nav(html: str) -> bool:
    return bool(re.search(r'<nav\b', html, re.IGNORECASE))


def replace_nav(html: str, new_nav: str) -> tuple[str, bool]:
    """
    Replace existing <nav ...>...</nav> block with new_nav.
    Returns (new_html, changed).
    Also removes any existing #nav-std-css <style> to avoid duplicates.
    """
    # Remove old nav CSS if present
    html = re.sub(
        r'<style\s+id=["\']nav-std-css["\'].*?</style>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )
    # Replace the nav block
    new_html, count = re.subn(
        r'<nav\b[^>]*>.*?</nav>',
        new_nav,
        html,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return new_html, count > 0


def inject_nav_after_body(html: str, new_nav: str) -> str:
    """If no <nav> exists, inject right after <body> tag."""
    new_html, count = re.subn(
        r'(<body[^>]*>)',
        r'\1\n' + new_nav.replace('\\', '\\\\'),
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    if count == 0:
        # No <body> tag — prepend
        new_html = new_nav + "\n" + html
    return new_html


def fix_bot_links(html: str, file_path: Path, root: Path) -> tuple[str, int]:
    """Replace any broken bot/tefa-scan hrefs with the correct relative path."""
    correct_href = relative_path(file_path, BOT_CANONICAL, root)
    changes = 0
    for pattern in BOT_LINK_PATTERNS:
        new_html, n = re.subn(
            pattern,
            f'href="{correct_href}"',
            html,
            flags=re.IGNORECASE,
        )
        if n:
            html = new_html
            changes += n
    return html, changes


def fix_tefa_hub_links(html: str, file_path: Path, root: Path) -> tuple[str, int]:
    """Fix links that should point to the TEFA hub pages."""
    changes = 0
    # Patterns that are probably meant to be the TEFA hub
    broken_tefa_patterns = [
        (r'href=["\']#tefa-hub["\']',           TEFA_HUB_EN),
        (r'href=["\'].*?/tefa/?["\']',          TEFA_HUB_EN),
        (r'href=["\'].*?esa-texas-espanol["\']', TEFA_HUB_ES),
        (r'href=["\'].*?/es/tefa/?["\']',        TEFA_HUB_ES),
    ]
    for pattern, target in broken_tefa_patterns:
        correct = relative_path(file_path, target, root)
        new_html, n = re.subn(pattern, f'href="{correct}"', html, flags=re.IGNORECASE)
        if n:
            html = new_html
            changes += n
    return html, changes


def fix_generic_relative_links(html: str, file_path: Path, root: Path) -> tuple[str, int]:
    """
    Fix href="index.html" and href="/" style links that may be wrong
    depending on file depth — converts them to proper relative paths.
    """
    changes = 0
    # href="/" → relative path to root index
    root_href = relative_path(file_path, LOGO_HREF_FROM_ROOT, root)
    new_html, n = re.subn(
        r'href=["\']/?index\.html["\']',
        f'href="{root_href}"',
        html,
        flags=re.IGNORECASE,
    )
    if n:
        html = new_html
        changes += n
    return html, changes


def backup_file(file_path: Path, backup_dir: Path) -> None:
    """Copy original to backup_dir preserving relative structure."""
    rel = file_path.relative_to(file_path.anchor) if file_path.is_absolute() else file_path
    dest = backup_dir / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file_path, dest)


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Fix links and standardize nav for TexasSpecialEd.com")
    parser.add_argument("--root",    default=SITE_ROOT,  help="Path to site root")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files")
    parser.add_argument("--no-backup", action="store_true", help="Skip .bak backups (not recommended)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"❌  Root not found: {root}")
        print("    Check the --root path or update SITE_ROOT in this script.")
        sys.exit(1)

    dry_run   = args.dry_run
    do_backup = not args.no_backup

    # Backup folder: root/../site_backups/YYYY-MM-DD_HH-MM
    timestamp  = datetime.now().strftime("%Y-%m-%d_%H-%M")
    backup_dir = root.parent / "site_backups" / timestamp

    print(f"\n{'='*60}")
    print(f"  TexasSpecialEd.com — Link Fixer + Nav Standardizer")
    print(f"{'='*60}")
    print(f"  Root:      {root}")
    print(f"  Dry run:   {dry_run}")
    print(f"  Backup to: {backup_dir if do_backup else 'DISABLED'}")
    print(f"{'='*60}\n")

    # Collect all HTML files
    html_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skip dirs in-place
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if Path(fname).suffix.lower() in HTML_EXTENSIONS:
                html_files.append(Path(dirpath) / fname)

    if not html_files:
        print("⚠️  No HTML files found. Check your --root path.")
        sys.exit(0)

    print(f"  Found {len(html_files)} HTML files\n")

    # Counters
    total_nav_replaced  = 0
    total_nav_injected  = 0
    total_bot_fixes     = 0
    total_tefa_fixes    = 0
    total_link_fixes    = 0
    files_changed       = 0

    for file_path in sorted(html_files):
        rel_display = str(file_path.relative_to(root))

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            original_html = f.read()

        html = original_html
        file_changes = []

        # 1. Build the correct nav for this file
        new_nav_block = build_full_nav_block(file_path, root)

        # 2. Replace or inject nav
        if has_nav(html):
            html, replaced = replace_nav(html, new_nav_block)
            if replaced:
                total_nav_replaced += 1
                file_changes.append("  ✎  Nav replaced")
        else:
            html = inject_nav_after_body(html, new_nav_block)
            total_nav_injected += 1
            file_changes.append("  ✚  Nav injected")

        # 3. Fix bot links
        html, n = fix_bot_links(html, file_path, root)
        if n:
            total_bot_fixes += n
            file_changes.append(f"  🔗  {n} bot link(s) fixed → {relative_path(file_path, BOT_CANONICAL, root)}")

        # 4. Fix TEFA hub links
        html, n = fix_tefa_hub_links(html, file_path, root)
        if n:
            total_tefa_fixes += n
            file_changes.append(f"  🔗  {n} TEFA hub link(s) fixed")

        # 5. Fix generic root links
        html, n = fix_generic_relative_links(html, file_path, root)
        if n:
            total_link_fixes += n
            file_changes.append(f"  🔗  {n} root link(s) corrected")

        # Write if changed
        if html != original_html:
            files_changed += 1
            print(f"  📄  {rel_display}")
            for msg in file_changes:
                print(f"      {msg}")

            if not dry_run:
                if do_backup:
                    backup_file(file_path, backup_dir)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html)
        else:
            print(f"  ✓   {rel_display}  (no changes needed)")

    # ── SUMMARY ──
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Files scanned:         {len(html_files)}")
    print(f"  Files changed:         {files_changed}")
    print(f"  Nav blocks replaced:   {total_nav_replaced}")
    print(f"  Nav blocks injected:   {total_nav_injected}")
    print(f"  Bot links fixed:       {total_bot_fixes}")
    print(f"  TEFA hub links fixed:  {total_tefa_fixes}")
    print(f"  Root links corrected:  {total_link_fixes}")
    if do_backup and not dry_run and files_changed > 0:
        print(f"  Backups saved to:      {backup_dir}")
    if dry_run:
        print(f"\n  ⚠️  DRY RUN — no files were written.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()