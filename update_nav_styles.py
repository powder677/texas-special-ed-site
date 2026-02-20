#!/usr/bin/env python3
"""
update_nav_styles.py
====================
Updates all district HTML pages to match the homepage nav styling:
  - White navbar (professional look)
  - Sticky positioning (locks to top on scroll)
  - Dark text on white background
  - Fixes dropdown gap bug (mouse falling off)
  - Fixes floating footer (sticky footer via flexbox)
  - Removes min-height: 50vh from .container (no longer needed)

USAGE:
  Dry run first:
    python update_nav_styles.py --districts-dir "C:\\...\\districts" --dry-run

  Live run:
    python update_nav_styles.py --districts-dir "C:\\...\\districts"
"""

import re
import shutil
import argparse
from pathlib import Path


# ─── CSS REPLACEMENTS ──────────────────────────────────────────────────────────
# Each tuple: (description, old_pattern, new_string)
# Using regex patterns so minor whitespace variations don't break matches.

CSS_FIXES = [

    # 1. Site header — dark bg + relative → white bg + sticky
    (
        "site-header: dark→white sticky",
        r'\.site-header\s*\{[^}]+\}',
        """.site-header { background: #ffffff; box-shadow: 0 2px 10px rgba(0,0,0,0.07); padding: 14px 0; position: sticky; top: 0; z-index: 9999; }"""
    ),

    # 2. Nav links — white text → dark text
    (
        "nav-link: white→dark text",
        r'\.nav-link\s*\{[^}]+\}',
        """.nav-link { color: #1e2530; text-decoration: none; font-size: 0.95rem; font-weight: 500; transition: color 0.2s; }"""
    ),

    # 3. Nav link hover — opacity→color change
    (
        "nav-link hover",
        r'\.nav-link:hover\s*\{[^}]+\}',
        """.nav-link:hover { color: #1560a8; }"""
    ),

    # 4. Hamburger icon — white→dark (for mobile toggle on white bg)
    (
        "hamburger: white→dark",
        r'\.hamburger\s*\{[^}]+\}',
        """.hamburger { display: block; width: 25px; height: 3px; background: #0a3d6b; margin: 5px 0; border-radius: 2px; }"""
    ),

    # 5. Dropdown gap fix — remove the 8px gap that causes mouse falloff
    (
        "dropdown-menu: fix gap bug",
        r'\.dropdown-menu\s*\{[^}]+\}',
        """.dropdown-menu { display: none; position: absolute; background: #fff; padding: 10px 0; border-radius: 6px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); top: 100%; left: 0; min-width: 220px; list-style: none; border: 1px solid #dde3eb; }"""
    ),

    # 6. Sticky footer — body needs flex column
    (
        "body: add flex for sticky footer",
        r'body\s*\{([^}]+)\}',
        lambda m: 'body {' + m.group(1).rstrip() + ' display: flex; flex-direction: column; min-height: 100vh; }'
                  if 'flex' not in m.group(1) else m.group(0)
    ),

    # 7. Remove min-height: 50vh from .container (flex: 1 on main handles it)
    (
        ".container: remove min-height",
        r'(\.container\s*\{[^}]+?)min-height:\s*50vh;\s*',
        r'\1'
    ),

    # 8. Mobile nav — update to white background version
    (
        "mobile nav-menu: dark→white bg",
        r'(@media[^{]*max-width:\s*900px[^{]*\{.*?\.nav-menu\s*\{)[^}]+(\})',
        lambda m: m.group(1) + ' display: none; flex-direction: column; width: 100%; position: absolute; top: 100%; left: 0; background: #ffffff; box-shadow: 0 6px 16px rgba(0,0,0,0.1); padding: 20px 0; border-top: 1px solid #dde3eb; ' + m.group(2)
    ),

    # 9. Mobile nav link — update border color
    (
        "mobile nav-link border",
        r'(\.nav-cta\s*\{[^}]+\})',
        '.nav-cta { margin-top: 15px; }'
    ),
]

# Separate fix for <main> tag — needs to be in HTML, not CSS
MAIN_TAG_FIX = (
    "main tag: add flex:1",
    r'<main\b([^>]*)>',
    lambda m: f'<main{m.group(1)} style="flex:1">'
              if 'flex' not in m.group(1) else m.group(0)
)


def apply_css_fixes(content: str) -> tuple[str, list[str]]:
    """Apply all CSS fixes to the inline <style> block."""
    applied = []

    # Extract the <style> block
    style_match = re.search(r'(<style>)(.*?)(</style>)', content, re.DOTALL)
    if not style_match:
        return content, []

    style_content = style_match.group(2)
    original_style = style_content

    for desc, pattern, replacement in CSS_FIXES:
        if callable(replacement):
            new_style = re.sub(pattern, replacement, style_content, flags=re.DOTALL)
        else:
            new_style = re.sub(pattern, replacement, style_content, flags=re.DOTALL)

        if new_style != style_content:
            applied.append(desc)
            style_content = new_style

    if style_content != original_style:
        content = content[:style_match.start(2)] + style_content + content[style_match.end(2):]

    return content, applied


def apply_main_tag_fix(content: str) -> tuple[str, bool]:
    """Add flex:1 to <main> tag so it pushes footer down."""
    # Only add if not already there
    if 'flex:1' in content or 'flex: 1' in content:
        return content, False

    desc, pattern, replacement = MAIN_TAG_FIX
    new_content = re.sub(pattern, replacement, content)
    return new_content, new_content != content


def get_district_slug(html_file: Path, root: Path) -> str | None:
    try:
        parts = html_file.relative_to(root).parts
        if len(parts) >= 2:
            return parts[0]
    except ValueError:
        pass
    return None


def run(districts_dir: str, dry_run: bool, no_backup: bool):
    root = Path(districts_dir).resolve()

    if not root.exists():
        print(f"\nERROR: Directory not found: {root}\n")
        return

    print(f"\n{'='*64}")
    print(f"  Texas Special Ed — Nav Style Updater")
    print(f"{'='*64}")
    print(f"  Root  : {root}")
    print(f"  Mode  : {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"  Backup: {'OFF' if no_backup else 'ON (.html.bak)'}")
    print(f"{'='*64}\n")

    all_html = sorted(root.rglob("*.html"))
    if not all_html:
        print("  No HTML files found.\n")
        return

    print(f"  Scanning {len(all_html)} files...\n")

    total = fixed = skipped = 0
    errors = []

    for html_file in all_html:
        total += 1

        try:
            original = html_file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            errors.append(f"{html_file.name}: {e}")
            continue

        content = original

        # Apply CSS fixes
        content, css_applied = apply_css_fixes(content)

        # Apply main tag fix
        content, main_fixed = apply_main_tag_fix(content)

        changes = css_applied + (["main flex:1"] if main_fixed else [])

        if not changes:
            skipped += 1
            continue

        fixed += 1
        rel = html_file.relative_to(root)
        print(f"  {rel}")
        for c in changes:
            print(f"    ✓ {c}")

        if dry_run:
            continue

        if not no_backup:
            shutil.copy2(html_file, html_file.with_suffix(".html.bak"))

        html_file.write_text(content, encoding="utf-8")

    print(f"\n{'='*64}")
    print(f"  SUMMARY")
    print(f"{'='*64}")
    print(f"  Files scanned : {total}")
    print(f"  Files updated : {fixed}")
    print(f"  Already ok    : {skipped}")

    if errors:
        print(f"\n  Errors:")
        for e in errors:
            print(f"    {e}")

    print()
    if dry_run:
        print("  ℹ️  Dry run complete. Run without --dry-run to apply.")
    elif fixed:
        print(f"  ✅ Done. {fixed} files updated.")
        if not no_backup:
            print("  💾 Originals backed up as .html.bak")
    print(f"{'='*64}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upgrade district nav to white sticky style.")
    parser.add_argument("--districts-dir", required=True, help="Path to districts/ folder")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no writes")
    parser.add_argument("--no-backup", action="store_true", help="Skip .bak files")
    args = parser.parse_args()
    run(args.districts_dir, args.dry_run, args.no_backup)