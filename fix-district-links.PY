"""
fix_district_links.py
----------------------
Replaces broken district-specific page links with their correct /blog/ equivalents.

Usage:
    python3 fix_district_links.py /path/to/your/project

Add --dry-run to preview changes without writing anything.
"""

import os
import re
import sys

# Map of district page slugs → correct /blog/ destination
SLUG_REDIRECTS = {
    "how-to-request-evaluation":    "/blog/how-to-request-evaluation",
    "grievance-dispute-resolution": "/blog/grievance-dispute-resolution",
    "evaluation-child-find":        "/blog/evaluation-child-find",
    "ard-process-guide":            "/blog/ard-process-guide",
    "what-is-an-fie":               "/blog/what-is-an-fie",
}

# File extensions to search
EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mdx", ".md", ".html", ".json"}

# Regex: matches /districts/{any-isd}/{slug}-{isd-name}.html  or  /{slug}.html
PATTERN = re.compile(
    r"/districts/[^/\"'\s]+/(" + "|".join(re.escape(s) for s in SLUG_REDIRECTS) + r")[^\"'\s]*\.html"
)

def fix_line(line):
    def replacer(match):
        slug = match.group(1)
        return SLUG_REDIRECTS[slug] + ".html"
    return PATTERN.sub(replacer, line)

def process_file(filepath, dry_run):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        original = f.read()

    fixed = PATTERN.sub(lambda m: SLUG_REDIRECTS[m.group(1)] + ".html", original)

    if fixed == original:
        return False  # no changes

    if dry_run:
        print(f"  [DRY RUN] Would update: {filepath}")
        for i, (orig, new) in enumerate(zip(original.splitlines(), fixed.splitlines()), 1):
            if orig != new:
                print(f"    line {i}:")
                print(f"      - {orig.strip()}")
                print(f"      + {new.strip()}")
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(fixed)
        print(f"  ✅ Updated: {filepath}")

    return True

def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    dirs = [a for a in args if not a.startswith("--")]
    root = dirs[0] if dirs else "."

    print(f"{'[DRY RUN] ' if dry_run else ''}Scanning: {os.path.abspath(root)}\n")

    changed = 0
    for dirpath, _, filenames in os.walk(root):
        # Skip node_modules and .next
        if any(skip in dirpath for skip in ["node_modules", ".next", ".git"]):
            continue
        for filename in filenames:
            if os.path.splitext(filename)[1] in EXTENSIONS:
                filepath = os.path.join(dirpath, filename)
                if process_file(filepath, dry_run):
                    changed += 1

    print(f"\n{'Would update' if dry_run else 'Updated'} {changed} file(s).")
    if dry_run:
        print("Run without --dry-run to apply changes.")

if __name__ == "__main__":
    main()