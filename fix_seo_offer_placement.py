#!/usr/bin/env python3
"""
fix_seo_offer_placement.py
==========================
Ensures SEO/AEO content is above the fold on district pages by moving
offer/CTA blocks that are incorrectly placed BEFORE content paragraphs.

PROBLEM:
  <article class="content-column">
    <h2>Section Title</h2>
    [OFFER CARD]          ← pushed here by CRO patch (before any <p>)
    <p>Real content...</p>

AFTER FIX:
  <article class="content-column">
    <h2>Section Title</h2>
    <p>Real content...</p>  ← Google / AEO sees this first
    <p>More content...</p>
    [OFFER CARD]            ← flows naturally after 2 paragraphs

Usage:
  python fix_seo_offer_placement.py --dir /path/to/districts --dry-run
  python fix_seo_offer_placement.py --dir /path/to/districts

Options:
  --dir       Root directory to scan (searches recursively for .html files)
  --dry-run   Preview changes without writing files
  --after-p   Number of <p> tags to insert after (default: 2)
  --backup    Create .bak backup before modifying (default: True)
  --log       Path to write change log (default: fix_log.csv)
"""

import argparse
import csv
import os
import re
import shutil
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup, NavigableString, Tag
except ImportError:
    print("ERROR: beautifulsoup4 not installed. Run: pip install beautifulsoup4")
    sys.exit(1)


# ── OFFER DETECTION ──────────────────────────────────────────────────────────

OFFER_CLASSES = {
    "sales-card",
    "integrated-cta",
    "offers-container",
    "inline-cta",       # only flag if it's before the first <p>
}

# Inline-style fingerprints that identify offer/CTA blocks
OFFER_STYLE_PATTERNS = [
    r"linear-gradient.*0f172a",       # dark navy gradient (primary offer card)
    r"linear-gradient.*1e3a8a",       # dark blue gradient
    r"linear-gradient.*1c1917",       # dark brown/gold gradient
    r"background.*d4af37",            # gold background (button-only blocks)
]

OFFER_STYLE_REGEX = re.compile(
    "|".join(OFFER_STYLE_PATTERNS),
    re.IGNORECASE
)


def is_offer_block(tag: Tag) -> bool:
    """Return True if this tag looks like a CTA / offer card."""
    if not isinstance(tag, Tag):
        return False

    # Class-based detection
    tag_classes = set(tag.get("class") or [])
    if tag_classes & OFFER_CLASSES:
        return True

    # Inline-style detection (dark gradient cards injected without class)
    style = tag.get("style", "")
    if style and OFFER_STYLE_REGEX.search(style):
        # Make sure it's a substantial block (has a link / button inside)
        if tag.find("a") or tag.find("button"):
            return True

    return False


# ── CONTENT COLUMN DETECTION ─────────────────────────────────────────────────

def find_content_column(soup: BeautifulSoup) -> Tag | None:
    """Return the primary content article/div."""
    # 1. <article class="content-column">
    col = soup.find("article", class_="content-column")
    if col:
        return col
    # 2. <div class="content-column">
    col = soup.find("div", class_="content-column")
    if col:
        return col
    # 3. Fallback: <main> tag
    return soup.find("main")


# ── CORE FIX LOGIC ───────────────────────────────────────────────────────────

def fix_page(html: str, after_p: int = 2) -> tuple[str, list[str]]:
    """
    Parse HTML, detect misplaced offers, reorder them.

    Returns:
        (fixed_html, list_of_change_descriptions)
    """
    soup = BeautifulSoup(html, "html.parser")
    changes = []

    content_col = find_content_column(soup)
    if not content_col:
        return html, []

    # Work on direct children of content_col
    children = [c for c in content_col.children if isinstance(c, Tag)]

    # Find the FIRST <h2> in the content column
    first_h2 = content_col.find("h2")
    if not first_h2 or first_h2.parent != content_col:
        # h2 might be a deeper descendant — only act on direct-child h2
        first_h2 = next(
            (c for c in children if c.name == "h2"), None
        )

    if not first_h2:
        return html, []

    # Collect direct children AFTER the first h2
    after_h2 = list(first_h2.next_siblings)
    after_h2 = [t for t in after_h2 if isinstance(t, Tag)]

    # Find offer blocks that appear BEFORE the first real <p> tag
    first_p_index = next(
        (i for i, t in enumerate(after_h2) if t.name == "p"),
        None
    )

    if first_p_index is None:
        # No <p> found after h2 — nothing to do
        return html, []

    # Gather offer blocks that sit before the first <p>
    early_offers = [
        t for t in after_h2[:first_p_index]
        if is_offer_block(t)
    ]

    if not early_offers:
        return html, []

    # Find all <p> siblings after h2
    p_tags = [t for t in after_h2 if t.name == "p"]

    # Determine the anchor <p> after which we'll insert offers
    # Use min(after_p, len(p_tags)) to avoid going out of range
    anchor_index = min(after_p, len(p_tags)) - 1
    anchor_p = p_tags[anchor_index]

    # Move each early offer to after the anchor paragraph
    for offer in early_offers:
        offer_desc = _describe_offer(offer)
        # Detach from current position
        offer.extract()
        # Insert after anchor_p
        anchor_p.insert_after(offer)
        # Update anchor so next offer goes after the previous one
        anchor_p = offer
        changes.append(f"Moved offer [{offer_desc}] to after paragraph {anchor_index + 1}")

    return str(soup), changes


def _describe_offer(tag: Tag) -> str:
    """Short human-readable description of an offer block."""
    h3 = tag.find("h3")
    if h3:
        return h3.get_text(strip=True)[:60]
    a = tag.find("a")
    if a:
        return (a.get_text(strip=True) or a.get("href", ""))[:60]
    classes = " ".join(tag.get("class") or [])
    return classes or tag.name


# ── FILE PROCESSING ───────────────────────────────────────────────────────────

def process_file(
    path: Path,
    after_p: int,
    dry_run: bool,
    backup: bool,
) -> dict:
    """Process a single HTML file. Returns a result dict."""
    result = {
        "file": str(path),
        "status": "unchanged",
        "changes": [],
        "error": None,
    }

    try:
        original = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        return result

    fixed, changes = fix_page(original, after_p=after_p)

    if not changes:
        return result

    result["status"] = "dry-run" if dry_run else "fixed"
    result["changes"] = changes

    if not dry_run:
        if backup:
            shutil.copy2(path, path.with_suffix(".html.bak"))
        path.write_text(fixed, encoding="utf-8")

    return result


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fix SEO/AEO offer placement on district HTML pages."
    )
    parser.add_argument(
        "--dir", required=True,
        help="Root directory to scan recursively for .html files"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--after-p", type=int, default=2,
        help="Insert offer after this many <p> tags (default: 2)"
    )
    parser.add_argument(
        "--no-backup", action="store_true",
        help="Skip creating .bak backup files"
    )
    parser.add_argument(
        "--log", default="fix_log.csv",
        help="CSV log file path (default: fix_log.csv)"
    )
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.exists():
        print(f"ERROR: Directory not found: {root}")
        sys.exit(1)

    html_files = sorted(root.rglob("*.html"))
    total = len(html_files)
    print(f"Found {total} HTML files in {root}")
    if args.dry_run:
        print("DRY RUN — no files will be modified\n")

    results = []
    fixed_count = 0
    error_count = 0

    for i, path in enumerate(html_files, 1):
        # Skip backup files
        if path.suffix == ".bak" or ".bak" in path.suffixes:
            continue

        result = process_file(
            path,
            after_p=args.after_p,
            dry_run=args.dry_run,
            backup=not args.no_backup,
        )
        results.append(result)

        if result["status"] in ("fixed", "dry-run"):
            fixed_count += 1
            label = "[DRY-RUN]" if args.dry_run else "[FIXED]"
            print(f"{label} {path.relative_to(root)}")
            for change in result["changes"]:
                print(f"         → {change}")
        elif result["status"] == "error":
            error_count += 1
            print(f"[ERROR]   {path.relative_to(root)}: {result['error']}")

        # Progress every 100 files
        if i % 100 == 0:
            print(f"  … processed {i}/{total}")

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"  Total files scanned : {total}")
    print(f"  Files {'(would be) ' if args.dry_run else ''}fixed : {fixed_count}")
    print(f"  Already correct     : {total - fixed_count - error_count}")
    print(f"  Errors              : {error_count}")
    print(f"{'='*60}")

    # ── Write CSV log ─────────────────────────────────────────────────────────
    log_path = Path(args.log)
    with log_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "status", "changes", "error"])
        for r in results:
            writer.writerow([
                r["file"],
                r["status"],
                " | ".join(r["changes"]),
                r["error"] or "",
            ])
    print(f"\nLog written to: {log_path}")


if __name__ == "__main__":
    main()