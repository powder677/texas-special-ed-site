#!/usr/bin/env python3
"""
fix_district_links.py
=====================
Fixes relative internal links in all district hub pages (index.html + sub-pages).

WHAT IT FIXES:
  href="ard-process-guide.html"          → href="/districts/alief-isd/ard-process-guide.html"
  href="evaluation-child-find.html"      → href="/districts/alief-isd/evaluation-child-find.html"
  href="grievance-dispute-resolution.html" → href="/districts/alief-isd/grievance-dispute-resolution.html"
  href="dyslexia-services.html"          → href="/districts/alief-isd/dyslexia-services.html"
  href="leadership-directory.html"       → href="/districts/alief-isd/leadership-directory.html"

HOW IT WORKS:
  1. Walks your districts/ folder recursively
  2. For each .html file, detects the district slug from the folder path
  3. Finds all relative href links that point to known page filenames
  4. Rewrites them to absolute /districts/{slug}/{page}.html paths
  5. Writes the fixed file back in place (backs up originals first)

USAGE:
  python fix_district_links.py --districts-dir /path/to/your/districts

  Dry run (see what would change without writing):
  python fix_district_links.py --districts-dir /path/to/your/districts --dry-run

  Skip backup (not recommended first time):
  python fix_district_links.py --districts-dir /path/to/your/districts --no-backup
"""

import os
import re
import shutil
import argparse
from pathlib import Path

# ─── CONFIG ────────────────────────────────────────────────────────────────────

# All page filenames that should be linked with absolute district paths.
# Add any new page types here if you expand the site.
DISTRICT_PAGES = {
    "ard-process-guide.html",
    "evaluation-child-find.html",
    "grievance-dispute-resolution.html",
    "dyslexia-services.html",
    "leadership-directory.html",
    "index.html",  # self-referential links
}

# ─── CORE LOGIC ────────────────────────────────────────────────────────────────

def get_district_slug(html_file_path: Path, districts_root: Path) -> str | None:
    """
    Extract district slug from the file's folder path.
    e.g. /sites/districts/alief-isd/index.html → 'alief-isd'
    
    Falls back to parsing the canonical <link> tag if folder structure is flat.
    """
    try:
        # Get relative path from districts root
        rel = html_file_path.relative_to(districts_root)
        parts = rel.parts
        if len(parts) >= 1:
            return parts[0]  # First folder = district slug
    except ValueError:
        pass
    
    # Fallback: parse canonical URL from the HTML
    try:
        content = html_file_path.read_text(encoding="utf-8", errors="ignore")
        canonical_match = re.search(
            r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']',
            content, re.IGNORECASE
        )
        if not canonical_match:
            canonical_match = re.search(
                r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',
                content, re.IGNORECASE
            )
        if canonical_match:
            url = canonical_match.group(1)
            # Extract slug from URL like https://texasspecialed.com/districts/alief-isd/
            slug_match = re.search(r'/districts/([^/]+)', url)
            if slug_match:
                return slug_match.group(1)
    except Exception:
        pass
    
    return None


def fix_links_in_content(content: str, district_slug: str) -> tuple[str, int]:
    """
    Replace bare relative hrefs with absolute district-prefixed paths.
    Returns (fixed_content, number_of_replacements).
    
    Handles these patterns:
      href="page.html"
      href='page.html'
    
    Does NOT touch:
      href="/"           (absolute root links)
      href="/districts/" (already absolute)
      href="http..."     (external links)
      href="#..."        (anchors)
    """
    replacements = 0
    
    def replace_href(match):
        nonlocal replacements
        quote = match.group(1)  # ' or "
        path = match.group(2)
        
        # Skip if already absolute or external or anchor
        if (path.startswith('/') or 
            path.startswith('http') or 
            path.startswith('#') or
            path.startswith('mailto:') or
            path.startswith('tel:')):
            return match.group(0)
        
        # Only fix known district page filenames
        filename = path.split('?')[0].split('#')[0]  # strip query/anchor
        if filename not in DISTRICT_PAGES:
            return match.group(0)
        
        # Build absolute path
        new_path = f"/districts/{district_slug}/{path}"
        replacements += 1
        return f'href={quote}{new_path}{quote}'
    
    fixed = re.sub(r'href=(["\'])([^"\']+)\1', replace_href, content)
    return fixed, replacements


def fix_district_links(districts_dir: str, dry_run: bool = False, no_backup: bool = False):
    """Main function: walk all HTML files and fix links."""
    
    districts_root = Path(districts_dir).resolve()
    
    if not districts_root.exists():
        print(f"ERROR: Directory not found: {districts_root}")
        return
    
    print(f"\n{'='*60}")
    print(f"  Texas Special Ed — District Link Fixer")
    print(f"{'='*60}")
    print(f"  Root:    {districts_root}")
    print(f"  Mode:    {'DRY RUN (no files written)' if dry_run else 'LIVE'}")
    print(f"  Backup:  {'OFF' if no_backup else 'ON (.bak files)'}")
    print(f"{'='*60}\n")
    
    # Stats
    total_files = 0
    fixed_files = 0
    skipped_files = 0
    total_replacements = 0
    errors = []
    no_slug_files = []
    
    # Walk all HTML files
    html_files = sorted(districts_root.rglob("*.html"))
    
    if not html_files:
        print("  No HTML files found. Check your --districts-dir path.")
        return
    
    print(f"  Found {len(html_files)} HTML files to process...\n")
    
    for html_file in html_files:
        total_files += 1
        
        # Get district slug
        slug = get_district_slug(html_file, districts_root)
        
        if not slug:
            no_slug_files.append(str(html_file))
            skipped_files += 1
            continue
        
        # Read file
        try:
            original = html_file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            errors.append(f"{html_file}: {e}")
            skipped_files += 1
            continue
        
        # Fix links
        fixed, count = fix_links_in_content(original, slug)
        
        if count == 0:
            # Nothing to fix
            continue
        
        fixed_files += 1
        total_replacements += count
        
        # Print what changed
        rel_path = html_file.relative_to(districts_root.parent)
        print(f"  [{slug}] {rel_path.name} → {count} link(s) fixed")
        
        if dry_run:
            # Show a preview of first change
            orig_lines = original.splitlines()
            fixed_lines = fixed.splitlines()
            for i, (a, b) in enumerate(zip(orig_lines, fixed_lines)):
                if a != b:
                    print(f"    Line {i+1}:")
                    print(f"      BEFORE: {a.strip()[:100]}")
                    print(f"      AFTER:  {b.strip()[:100]}")
                    break  # Just show first diff per file
            continue
        
        # Backup original
        if not no_backup:
            backup_path = html_file.with_suffix(".html.bak")
            shutil.copy2(html_file, backup_path)
        
        # Write fixed file
        try:
            html_file.write_text(fixed, encoding="utf-8")
        except Exception as e:
            errors.append(f"{html_file}: {e}")
    
    # ─── SUMMARY ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"{'='*60}")
    print(f"  Files scanned:        {total_files}")
    print(f"  Files fixed:          {fixed_files}")
    print(f"  Files skipped:        {skipped_files}")
    print(f"  Total links fixed:    {total_replacements}")
    
    if no_slug_files:
        print(f"\n  ⚠️  Could not detect district slug for {len(no_slug_files)} file(s):")
        for f in no_slug_files[:10]:
            print(f"     {f}")
        if len(no_slug_files) > 10:
            print(f"     ... and {len(no_slug_files) - 10} more")
    
    if errors:
        print(f"\n  ❌ Errors ({len(errors)}):")
        for e in errors:
            print(f"     {e}")
    
    if not dry_run and fixed_files > 0:
        print(f"\n  ✅ Done. {fixed_files} files updated.")
        if not no_backup:
            print(f"  💾 Originals backed up as .html.bak files.")
            print(f"  To restore: find . -name '*.html.bak' | while read f; do mv \"$f\" \"${{f%.bak}}\"; done")
    elif dry_run:
        print(f"\n  ℹ️  Dry run complete. Run without --dry-run to apply changes.")
    
    print(f"{'='*60}\n")


# ─── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fix relative internal links in Texas Special Ed district pages."
    )
    parser.add_argument(
        "--districts-dir",
        required=True,
        help="Path to your districts/ folder (e.g. /var/www/texasspecialed.com/districts)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing any files"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating .bak backup files (faster but no safety net)"
    )
    
    args = parser.parse_args()
    fix_district_links(
        districts_dir=args.districts_dir,
        dry_run=args.dry_run,
        no_backup=args.no_backup
    )