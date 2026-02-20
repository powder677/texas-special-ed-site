#!/usr/bin/env python3
"""
fix_district_links.py
=====================
Single-pass fix for all 750 Texas Special Ed district pages.

WHAT IT FIXES IN ONE RUN:
  1. Relative grid card hrefs → absolute
       href="ard-process-guide.html"         → href="/districts/{slug}/ard-process-guide.html"
       href="evaluation-child-find.html"     → href="/districts/{slug}/evaluation-child-find.html"
       href="grievance-dispute-resolution.html" → href="/districts/{slug}/grievance-dispute-resolution.html"
       href="dyslexia-services.html"         → href="/districts/{slug}/dyslexia-services.html"
       href="leadership-directory.html"      → href="/districts/{slug}/leadership-directory.html"
       href="partners.html"                  → href="/districts/{slug}/partners.html"

  2. Featured ad box button href="#" → absolute partners link
       <a href="#" class="btn-ad">  →  <a href="/districts/{slug}/partners.html" class="btn-ad">

USAGE:
  Dry run first (no files written, just shows what would change):
    python fix_district_links.py --districts-dir "C:\\Users\\elisa\\OneDrive\\Documents\\texas-special-ed-site\\districts" --dry-run

  Live run (backs up originals as .html.bak before writing):
    python fix_district_links.py --districts-dir "C:\\Users\\elisa\\OneDrive\\Documents\\texas-special-ed-site\\districts"

  Live run without backups (faster, no safety net):
    python fix_district_links.py --districts-dir "C:\\Users\\elisa\\OneDrive\\Documents\\texas-special-ed-site\\districts" --no-backup
"""

import re
import shutil
import argparse
from pathlib import Path


# ─── CONFIG ────────────────────────────────────────────────────────────────────

# Filenames that belong to district subfolders and need absolute paths.
DISTRICT_PAGES = {
    "ard-process-guide.html",
    "evaluation-child-find.html",
    "grievance-dispute-resolution.html",
    "dyslexia-services.html",
    "leadership-directory.html",
    "partners.html",
}


# ─── HELPERS ───────────────────────────────────────────────────────────────────

def get_district_slug(html_file_path: Path, districts_root: Path) -> str | None:
    """
    Derive district slug from folder structure.
      districts/alief-isd/index.html  →  'alief-isd'

    Falls back to reading the canonical <link> tag if needed.
    """
    try:
        rel   = html_file_path.relative_to(districts_root)
        parts = rel.parts
        if len(parts) >= 2:
            return parts[0]   # first folder = district slug
    except ValueError:
        pass

    # Fallback: parse canonical URL from file content
    try:
        text = html_file_path.read_text(encoding="utf-8", errors="ignore")
        for pattern in [
            r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',
        ]:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                slug_m = re.search(r'/districts/([^/]+)', m.group(1))
                if slug_m:
                    return slug_m.group(1)
    except Exception:
        pass

    return None


# ─── FIX 1: Relative grid hrefs → absolute ─────────────────────────────────

def fix_relative_links(content: str, slug: str) -> tuple[str, int]:
    """
    Rewrites bare relative hrefs for known district page filenames to
    absolute /districts/{slug}/page.html paths.
    Skips anything already absolute, external, or an anchor.
    """
    count = 0

    def replacer(match):
        nonlocal count
        quote = match.group(1)
        path  = match.group(2)

        # Skip already-absolute, external, anchors, mailto, tel
        if path.startswith(('/', 'http', '#', 'mailto:', 'tel:')):
            return match.group(0)

        filename = path.split('?')[0].split('#')[0]
        if filename not in DISTRICT_PAGES:
            return match.group(0)

        count += 1
        return f'href={quote}/districts/{slug}/{path}{quote}'

    fixed = re.sub(r'href=(["\'])([^"\']+)\1', replacer, content)
    return fixed, count


# ─── FIX 2: Featured ad btn-ad href="#" → partners.html ────────────────────

def fix_featured_ad_href(content: str, slug: str) -> tuple[str, int]:
    """
    Swaps href="#" to the partners page URL, but ONLY on anchors
    that have the class 'btn-ad'. Leaves all other href="#" alone.
    """
    partners_url = f'/districts/{slug}/partners.html'
    count = 0

    # Pattern: href="#" appearing on an <a> tag that also has class="btn-ad"
    # Handle both orderings: href before class, class before href

    def swap_if_hash(m):
        nonlocal count
        full  = m.group(0)
        href  = m.group(1)
        if href == '#' and 'btn-ad' in full:
            count += 1
            return full.replace(f'href="{href}"', f'href="{partners_url}"').replace(
                                f"href='{href}'", f"href='{partners_url}'")
        return full

    # Match entire opening <a ...> tag and check for btn-ad class + href="#"
    fixed = re.sub(
        r'<a\s[^>]*href=(["\'])#\1[^>]*>',
        lambda m: m.group(0).replace('href="#"', f'href="{partners_url}"').replace(
                                     "href='#'",  f"href='{partners_url}'"  )
                  if 'btn-ad' in m.group(0) else m.group(0),
        content
    )

    if fixed != content:
        count = content.count('href="#"') - fixed.count('href="#"')
        count += content.count("href='#'") - fixed.count("href='#'")

    return fixed, count


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def run(districts_dir: str, dry_run: bool, no_backup: bool):
    root = Path(districts_dir).resolve()

    if not root.exists():
        print(f"\nERROR: Directory not found:\n  {root}")
        print("\nTip: Copy the full path from File Explorer's address bar and wrap it in quotes.")
        return

    print(f"\n{'='*64}")
    print(f"  Texas Special Ed — District Link Fixer (Single Pass)")
    print(f"{'='*64}")
    print(f"  Root  : {root}")
    print(f"  Mode  : {'DRY RUN — no files written' if dry_run else 'LIVE'}")
    print(f"  Backup: {'OFF' if no_backup else 'ON — originals saved as .html.bak'}")
    print(f"{'='*64}\n")

    all_html  = sorted(root.rglob("*.html"))
    index_set = set(root.rglob("index.html"))   # ad-fix only on hub pages

    if not all_html:
        print("  No HTML files found. Double-check your --districts-dir path.\n")
        return

    print(f"  Scanning {len(all_html)} HTML files...\n")

    total       = 0
    fixed_count = 0
    link_total  = 0
    ad_total    = 0
    no_slug     = []
    errors      = []

    for html_file in all_html:
        total += 1
        slug = get_district_slug(html_file, root)

        if not slug:
            no_slug.append(str(html_file.relative_to(root)))
            continue

        try:
            original = html_file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            errors.append(f"{html_file.name}: {e}")
            continue

        content    = original
        link_fixes = 0
        ad_fixes   = 0

        # Fix 1 — relative links on every page
        content, link_fixes = fix_relative_links(content, slug)

        # Fix 2 — featured ad href only on index.html hub pages
        if html_file in index_set:
            content, ad_fixes = fix_featured_ad_href(content, slug)

        total_fixes = link_fixes + ad_fixes
        if total_fixes == 0:
            continue

        fixed_count += 1
        link_total  += link_fixes
        ad_total    += ad_fixes

        parts = []
        if link_fixes: parts.append(f"{link_fixes} link(s)")
        if ad_fixes:   parts.append("ad href → partners")
        print(f"  [{slug}]  {html_file.name}  →  {', '.join(parts)}")

        if dry_run:
            # Show first changed line as a preview
            for a, b in zip(original.splitlines(), content.splitlines()):
                if a.strip() != b.strip():
                    print(f"    BEFORE: {a.strip()[:100]}")
                    print(f"    AFTER:  {b.strip()[:100]}")
                    break
            continue

        # Write file (with optional backup)
        if not no_backup:
            shutil.copy2(html_file, html_file.with_suffix(".html.bak"))

        html_file.write_text(content, encoding="utf-8")

    # ─── SUMMARY ─────────────────────────────────────────────────────────────
    print(f"\n{'='*64}")
    print(f"  SUMMARY")
    print(f"{'='*64}")
    print(f"  Files scanned          : {total}")
    print(f"  Files updated          : {fixed_count}")
    print(f"  Grid links fixed       : {link_total}")
    print(f"  Ad box hrefs fixed     : {ad_total}")

    if no_slug:
        print(f"\n  ⚠️  Skipped {len(no_slug)} file(s) — could not detect district slug:")
        for f in no_slug[:10]:
            print(f"     {f}")
        if len(no_slug) > 10:
            print(f"     ... and {len(no_slug)-10} more")

    if errors:
        print(f"\n  ❌ Errors:")
        for e in errors:
            print(f"     {e}")

    print()
    if dry_run:
        print("  ℹ️  Dry run complete. Run without --dry-run to apply changes.")
    elif fixed_count:
        print(f"  ✅ Done. {fixed_count} files updated.")
        if not no_backup:
            print("  💾 Originals backed up as .html.bak files.")
            print("  To restore everything:  for %f in (.\\districts\\*.html.bak) do move \"%f\" \"%~dpnf\"")
    print(f"{'='*64}\n")


# ─── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fix all district page links for texasspecialed.com in one pass."
    )
    parser.add_argument(
        "--districts-dir", required=True,
        help='Full path to your districts/ folder'
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview changes without writing any files"
    )
    parser.add_argument(
        "--no-backup", action="store_true",
        help="Skip .bak backups (faster but no rollback)"
    )
    args = parser.parse_args()
    run(args.districts_dir, args.dry_run, args.no_backup)