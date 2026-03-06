"""
inject_district_content.py
Reads generated_content.json and injects the local HTML content block
into each district page on texasspecialed.com.

Injection point: just before </article> in the content-column,
which puts it right before the premium offers — consistent across all page types.

Usage:
    python inject_district_content.py

    # Dry run (preview changes without writing files):
    python inject_district_content.py --dry-run

    # Inject a single page only:
    python inject_district_content.py --only "lubbock-isd/evaluation-child-find"
"""

import json
import os
import re
import shutil
import argparse
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────

# Root of your local site repo — update this path if needed
SITE_ROOT = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"

# Path to the generated content JSON
JSON_PATH = os.path.join(SITE_ROOT, "generated_content.json")

# Where to save backup files before modifying
BACKUP_DIR = os.path.join(SITE_ROOT, "_backups", datetime.now().strftime("%Y%m%d_%H%M%S"))

# The HTML wrapper for the injected block — makes it easy to find/remove later
INJECT_START = "<!-- LOCAL_CONTENT_BLOCK:START -->"
INJECT_END   = "<!-- LOCAL_CONTENT_BLOCK:END -->"

# ── INJECTION TARGET ──────────────────────────────────────────────────────────
# We inject just before </article> inside .content-column
INJECTION_MARKER = "</article>"

# ── HELPERS ───────────────────────────────────────────────────────────────────

def build_html_block(generated_html: str, district_name: str, page_type: str) -> str:
    """Wrap the generated content in a styled, labelled div."""
    return f"""
{INJECT_START}
<div class="local-district-context" style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #1a56db;border-radius:6px;padding:28px 32px;margin:2.5rem 0;font-family:'Source Sans 3',sans-serif;font-size:17px;line-height:1.75;color:#1a1a2e;">
{generated_html}
</div>
{INJECT_END}
"""


def get_html_path(district_slug: str, page_type: str) -> str:
    """Build the full path to the target HTML file."""
    filename = f"{page_type}.html"
    return os.path.join(SITE_ROOT, "districts", district_slug, filename)


def already_injected(html: str) -> bool:
    """Check if we already injected content into this file."""
    return INJECT_START in html


def inject_content(html: str, block: str) -> str:
    """Insert the content block just before </article>."""
    # Find the LAST </article> to target the content-column (not any nested ones)
    last_pos = html.rfind(INJECTION_MARKER)
    if last_pos == -1:
        return None  # marker not found
    return html[:last_pos] + block + html[last_pos:]


def backup_file(filepath: str):
    """Copy original file to backup directory."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    rel = os.path.relpath(filepath, SITE_ROOT)
    dest = os.path.join(BACKUP_DIR, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(filepath, dest)


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument("--only", type=str, help="Process a single slug e.g. lubbock-isd/evaluation-child-find")
    args = parser.parse_args()

    # Load generated content
    if not os.path.exists(JSON_PATH):
        print(f"ERROR: Cannot find {JSON_PATH}")
        print("Make sure generated_content.json is in your site root.")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        entries = json.load(f)

    print(f"Loaded {len(entries)} entries from generated_content.json")
    if args.dry_run:
        print("DRY RUN — no files will be modified\n")

    success, skipped, failed, already_done = 0, 0, 0, 0

    for entry in entries:
        district_slug = entry["district"]
        page_type     = entry["page_type"]
        district_name = entry["district_name"]
        generated_html = entry["generated_html"]

        path_key = f"{district_slug}/{page_type}"

        # Filter to single page if --only flag used
        if args.only and path_key != args.only:
            continue

        html_path = get_html_path(district_slug, page_type)

        # Check file exists
        if not os.path.exists(html_path):
            print(f"  SKIP (file not found): {html_path}")
            skipped += 1
            continue

        # Read file
        with open(html_path, "r", encoding="utf-8") as f:
            original_html = f.read()

        # Skip if already injected
        if already_injected(original_html):
            print(f"  SKIP (already injected): {path_key}")
            already_done += 1
            continue

        # Build the HTML block
        block = build_html_block(generated_html, district_name, page_type)

        # Inject
        new_html = inject_content(original_html, block)
        if new_html is None:
            print(f"  FAIL (</article> not found): {path_key}")
            failed += 1
            continue

        if args.dry_run:
            # Just show a snippet of what would be injected
            print(f"  [DRY RUN] Would inject into: {path_key}")
            snippet = generated_html[:120].replace("\n", " ")
            print(f"            Preview: {snippet}...")
            success += 1
            continue

        # Backup original
        backup_file(html_path)

        # Write updated file
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(new_html)

        print(f"  ✓ Injected: {path_key}")
        success += 1

    print(f"\n── SUMMARY ──────────────────────────────")
    print(f"  ✓ Injected:        {success}")
    print(f"  ↩ Already done:    {already_done}")
    print(f"  ⚠ File not found:  {skipped}")
    print(f"  ✗ Failed:          {failed}")

    if not args.dry_run and success > 0:
        print(f"\n  Backups saved to: {BACKUP_DIR}")
        print(f"\nNext step: git add . && git commit -m 'inject local district content blocks'")
        print(f"           git push  (Vercel will auto-deploy)")


if __name__ == "__main__":
    main()