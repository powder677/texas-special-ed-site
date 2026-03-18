"""
fix_broken_pages.py
--------------------
Analyzes broken 404 URLs from broken_pages.csv and:
  1. Categorizes them by pattern
  2. Detects duplicate Spanish-language paths
  3. Suggests canonical redirect targets
  4. Outputs:
     - redirect_map.csv   — source → suggested redirect
     - redirects.htaccess — Apache redirect rules (ready to paste)
     - broken_summary.txt — grouped breakdown of issues
"""

import csv
import re
from collections import defaultdict
from urllib.parse import urlparse
from pathlib import Path

INPUT_FILE = "broken_pages.csv"
BASE_DOMAIN = "https://www.texasspecialed.com"

# ── helpers ──────────────────────────────────────────────────────────────────

def parse_url(url):
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    parts = path.strip("/").split("/")
    return path, parts

def detect_pattern(path, parts):
    """Return a short label describing the URL category."""
    if "/es-districts/" in path:
        return "es-districts (duplicate candidate)"
    if len(parts) >= 3 and parts[0] == "districts" and parts[2] == "es":
        return "districts/{isd}/es/ (duplicate candidate)"
    if len(parts) >= 2 and parts[0] == "districts":
        return "district page (EN)"
    if path.startswith("/blog/es/"):
        return "blog ES"
    if path.startswith("/blog/"):
        return "blog EN"
    if path.startswith("/es/"):
        return "top-level ES"
    if path.startswith("/files/"):
        return "file/download"
    if path.startswith("/resources/"):
        return "resource page"
    return "other"

def suggest_redirect(path, parts):
    """
    Try to produce a plausible canonical URL for the broken page.
    Main fix: unify the two duplicate Spanish path schemes:
      /districts/{isd}/es/{slug}      →  /es-districts/{isd}/{slug}
      /es-districts/{isd}/{slug}      →  /districts/{isd}/es/{slug}

    We canonicalise on /es-districts/ because that scheme is used more
    consistently across the dataset — flip this if your CMS prefers the other.
    """
    # Pattern A: /districts/{isd}/es/{slug}  →  /es-districts/{isd}/{slug}
    m = re.match(r"^/districts/([^/]+)/es/(.+)$", path)
    if m:
        isd, slug = m.groups()
        return f"/es-districts/{isd}/{slug}", "canonicalise to /es-districts/"

    # Pattern B: /es-districts/{isd}/{slug}  →  /districts/{isd}/es/{slug}
    m = re.match(r"^/es-districts/([^/]+)/(.+)$", path)
    if m:
        isd, slug = m.groups()
        # keep /es-districts/ as canonical — suggest /districts/ path as fallback
        return f"/districts/{isd}/es/{slug}", "canonicalise to /districts/{isd}/es/"

    # /resources/iep-letter/ → top-level resources (manual check)
    if path.startswith("/resources/"):
        return "/resources/", "check resources index"

    # /blog/es/ → /es/ blog hub
    if path.startswith("/blog/es/"):
        slug = parts[-1]
        return f"/es/{slug}", "try top-level /es/ equivalent"

    # /files/ → offer a manual review note
    if path.startswith("/files/"):
        return None, "manual check — file may have moved or been removed"

    return None, "no automatic redirect found — manual review needed"


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    urls = []
    with open(INPUT_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            urls.append(row["URL"].strip())

    categories = defaultdict(list)
    redirect_rows = []
    htaccess_lines = [
        "# Auto-generated redirects from fix_broken_pages.py",
        "# Review each rule before deploying!\n",
        "RewriteEngine On\n",
    ]

    for url in urls:
        path, parts = parse_url(url)
        category = detect_pattern(path, parts)
        categories[category].append(url)

        target_path, note = suggest_redirect(path, parts)
        target_url = (BASE_DOMAIN + target_path) if target_path else ""

        redirect_rows.append({
            "broken_url": url,
            "category": category,
            "suggested_redirect": target_url,
            "note": note,
        })

        if target_path:
            htaccess_lines.append(
                f"Redirect 301 {path} {BASE_DOMAIN}{target_path}"
            )

    # ── write redirect_map.csv ────────────────────────────────────────────────
    with open("redirect_map.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["broken_url", "category", "suggested_redirect", "note"]
        )
        writer.writeheader()
        writer.writerows(redirect_rows)
    print(f"✅ redirect_map.csv  — {len(redirect_rows)} rows")

    # ── write redirects.htaccess ──────────────────────────────────────────────
    with open("redirects.htaccess", "w", encoding="utf-8") as f:
        f.write("\n".join(htaccess_lines))
    redirect_count = sum(1 for r in redirect_rows if r["suggested_redirect"])
    print(f"✅ redirects.htaccess — {redirect_count} rules written")

    # ── write broken_summary.txt ──────────────────────────────────────────────
    with open("broken_summary.txt", "w", encoding="utf-8") as f:
        f.write("BROKEN PAGE SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total broken URLs: {len(urls)}\n\n")
        f.write("BY CATEGORY:\n")
        for cat, items in sorted(categories.items(), key=lambda x: -len(x[1])):
            f.write(f"  [{len(items):>3}]  {cat}\n")
        f.write("\nDETAILS BY CATEGORY:\n")
        for cat, items in sorted(categories.items(), key=lambda x: -len(x[1])):
            f.write(f"\n{'─'*60}\n{cat}  ({len(items)} URLs)\n{'─'*60}\n")
            for item in items:
                f.write(f"  {item}\n")

    print(f"✅ broken_summary.txt — {len(categories)} categories")


if __name__ == "__main__":
    main()