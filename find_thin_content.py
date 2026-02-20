#!/usr/bin/env python3
"""
find_thin_content.py
====================
Scans all district HTML pages and reports pages with less than 900 words
of visible content (HTML tags stripped). Also flags placeholder Stripe links.

OUTPUT:
  - Console report sorted by word count (thinnest first)
  - CSV report saved to thin_content_report.csv

USAGE:
  python find_thin_content.py --districts-dir "C:\\...\\districts"
  python find_thin_content.py --districts-dir "C:\\...\\districts" --threshold 1200
  python find_thin_content.py --districts-dir "C:\\...\\districts" --csv-out my_report.csv
"""

import re
import csv
import argparse
from pathlib import Path


# ─── CONFIG ────────────────────────────────────────────────────────────────────

DEFAULT_THRESHOLD = 900   # words — flag anything below this

# Placeholder patterns that indicate unfinished links
PLACEHOLDER_PATTERNS = [
    r'YOUR_[A-Z_]+_LINK',
    r'href="#"(?!.*btn-ad)',        # bare # hrefs not on btn-ad (those are intentional stubs)
    r'buy\.stripe\.com/YOUR_',
    r'example\.com',
    r'PLACEHOLDER',
    r'INSERT_LINK',
]


# ─── HELPERS ───────────────────────────────────────────────────────────────────

def strip_html(html: str) -> str:
    """Remove tags, scripts, styles, and collapse whitespace."""
    # Remove <script> and <style> blocks entirely
    html = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove all remaining tags
    html = re.sub(r'<[^>]+>', ' ', html)
    # Decode common entities
    html = html.replace('&amp;', '&').replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    # Collapse whitespace
    html = re.sub(r'\s+', ' ', html).strip()
    return html


def count_words(html: str) -> int:
    text = strip_html(html)
    return len(text.split())


def find_placeholders(html: str) -> list[str]:
    found = []
    for pattern in PLACEHOLDER_PATTERNS:
        matches = re.findall(pattern, html)
        if matches:
            found.extend(set(matches))
    return found


def get_page_title(html: str) -> str:
    m = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
    return m.group(1).strip() if m else '—'


def get_district_slug(html_file: Path, root: Path) -> str:
    try:
        parts = html_file.relative_to(root).parts
        return parts[0] if len(parts) >= 2 else '(root)'
    except ValueError:
        return '?'


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def run(districts_dir: str, threshold: int, csv_out: str):
    root = Path(districts_dir).resolve()

    if not root.exists():
        print(f"\nERROR: Directory not found: {root}\n")
        return

    print(f"\n{'='*70}")
    print(f"  Thin Content Scanner")
    print(f"{'='*70}")
    print(f"  Root      : {root}")
    print(f"  Threshold : < {threshold} words flagged as thin")
    print(f"{'='*70}\n")

    html_files = sorted(root.rglob("*.html"))
    if not html_files:
        print("  No HTML files found.\n")
        return

    print(f"  Scanning {len(html_files)} files...\n")

    results = []
    errors  = []

    for f in html_files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            errors.append(f"{f}: {e}")
            continue

        word_count   = count_words(content)
        placeholders = find_placeholders(content)
        slug         = get_district_slug(f, root)
        title        = get_page_title(content)
        is_thin      = word_count < threshold

        results.append({
            "file"        : str(f.relative_to(root)),
            "slug"        : slug,
            "filename"    : f.name,
            "title"       : title,
            "words"       : word_count,
            "thin"        : is_thin,
            "placeholders": ", ".join(placeholders) if placeholders else "",
        })

    # Sort: thin first, then by word count ascending
    results.sort(key=lambda r: (not r["thin"], r["words"]))

    # ─── CONSOLE REPORT ────────────────────────────────────────────────────────
    thin_pages  = [r for r in results if r["thin"]]
    placeholder_pages = [r for r in results if r["placeholders"]]

    print(f"  {'DISTRICT':<30} {'FILE':<35} {'WORDS':>6}  FLAGS")
    print(f"  {'-'*30} {'-'*35} {'-'*6}  {'-'*30}")

    for r in results:
        flags = []
        if r["thin"]:
            flags.append("⚠️  THIN")
        if r["placeholders"]:
            flags.append(f"🔗 PLACEHOLDER: {r['placeholders'][:40]}")

        if flags:
            print(f"  {r['slug']:<30} {r['filename']:<35} {r['words']:>6}  {'  |  '.join(flags)}")

    # ─── SUMMARY ───────────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  Total pages scanned    : {len(results)}")
    print(f"  Thin pages (< {threshold}w)  : {len(thin_pages)}")
    print(f"  Placeholder link pages : {len(placeholder_pages)}")

    if thin_pages:
        avg = sum(r["words"] for r in thin_pages) // len(thin_pages)
        print(f"  Avg words (thin only)  : {avg}")
        print(f"\n  Thinnest pages:")
        for r in thin_pages[:10]:
            print(f"    {r['words']:>5}w  {r['slug']}/{r['filename']}")

    if placeholder_pages:
        print(f"\n  Pages with placeholder links:")
        for r in placeholder_pages:
            print(f"    {r['slug']}/{r['filename']}")
            print(f"      → {r['placeholders']}")

    if errors:
        print(f"\n  Errors:")
        for e in errors:
            print(f"    {e}")

    # ─── CSV EXPORT ────────────────────────────────────────────────────────────
    csv_path = Path(csv_out)
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            "file", "slug", "filename", "title", "words", "thin", "placeholders"
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n  📄 Full report saved to: {csv_path.resolve()}")
    print(f"{'='*70}\n")
    print("  Next steps:")
    print("  1. Open the CSV — sort by 'words' column to prioritize rewrites")
    print("  2. Fix placeholder links first (quick wins, affects revenue)")
    print("  3. Use Vertex AI credits to bulk-expand thin pages to 1,200+ words")
    print()


# ─── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find thin content pages and placeholder links across district pages."
    )
    parser.add_argument(
        "--districts-dir", required=True,
        help='Full path to your districts/ folder'
    )
    parser.add_argument(
        "--threshold", type=int, default=DEFAULT_THRESHOLD,
        help=f"Word count threshold (default: {DEFAULT_THRESHOLD})"
    )
    parser.add_argument(
        "--csv-out", default="thin_content_report.csv",
        help="Output CSV filename (default: thin_content_report.csv)"
    )
    args = parser.parse_args()
    run(args.districts_dir, args.threshold, args.csv_out)