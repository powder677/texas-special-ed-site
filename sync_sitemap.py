"""
sync_sitemap.py
===============
Compares your sitemap.xml against the current file structure, then:
  1. Detects URLs in the sitemap that no longer exist as files (renamed/moved)
  2. Fuzzy-matches each missing URL to the closest existing file
  3. Writes 301 redirects into vercel.json
  4. Generates a fresh sitemap.xml from the current file structure

USAGE
-----
  python sync_sitemap.py --dir "C:/Users/elisa/OneDrive/Documents/texas-special-ed-site"

OPTIONS
  --dir          Root folder of your site (must contain sitemap.xml)
  --base-url     Your site's base URL (default: https://www.texasspecialed.com)
  --dry-run      Preview matches without writing any files
  --threshold    Fuzzy match confidence 0-100, lower = more lenient (default: 55)

REQUIREMENTS
  pip install beautifulsoup4 thefuzz python-Levenshtein lxml
"""

import re
import json
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import date
from difflib import SequenceMatcher

try:
    from thefuzz import process as fuzz_process, fuzz
    FUZZ_AVAILABLE = True
except ImportError:
    FUZZ_AVAILABLE = False
    print("⚠️  thefuzz not found — falling back to difflib (less accurate).")
    print("    For better matching run: pip install thefuzz python-Levenshtein\n")

BASE_URL     = "https://www.texasspecialed.com"
SITEMAP_NS   = "http://www.sitemaps.org/schemas/sitemap/0.9"
TODAY        = date.today().isoformat()

# Files/dirs to ignore when building the new sitemap
IGNORE_PATTERNS = {
    "_redirects", "node_modules", ".git", ".vercel",
    "404.html", "500.html",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def url_to_path(url: str, base_url: str) -> str:
    """Strip base URL and return a clean relative path string."""
    path = url.replace(base_url, "").strip("/")
    return path


def file_to_url(filepath: Path, root: Path, base_url: str) -> str:
    """Convert an absolute file path to its public URL."""
    rel = filepath.relative_to(root).as_posix()
    # index.html → drop the filename, keep the directory
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")].rstrip("/")
    elif rel == "index.html":
        rel = ""
    # Non-index html files keep their name but drop .html for clean URLs
    elif rel.endswith(".html"):
        rel = rel[: -len(".html")]
    return f"{base_url}/{rel}".rstrip("/") or base_url


def similarity(a: str, b: str) -> int:
    """Return a 0-100 similarity score between two strings."""
    if FUZZ_AVAILABLE:
        return fuzz.token_sort_ratio(a, b)
    return int(SequenceMatcher(None, a, b).ratio() * 100)


def best_match(missing_path: str, candidates: list[str], threshold: int):
    """
    Find the best matching candidate path for a missing URL path.
    Returns (best_match_path, score) or (None, 0) if below threshold.
    """
    if not candidates:
        return None, 0

    if FUZZ_AVAILABLE:
        result = fuzz_process.extractOne(
            missing_path, candidates,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=threshold
        )
        if result:
            return result[0], result[1]
        return None, 0

    # difflib fallback
    best, best_score = None, 0
    for c in candidates:
        score = similarity(missing_path, c)
        if score > best_score:
            best, best_score = c, score
    return (best, best_score) if best_score >= threshold else (None, 0)


# ── Core logic ─────────────────────────────────────────────────────────────────

def parse_sitemap(sitemap_path: Path, base_url: str) -> list[str]:
    """Return list of relative path strings from the sitemap."""
    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    urls = []
    for loc in root.iter(f"{{{SITEMAP_NS}}}loc"):
        path = url_to_path(loc.text.strip(), base_url)
        urls.append(path)
    return urls


def get_current_files(root: Path) -> list[Path]:
    """Return all HTML files in the site, excluding ignored patterns."""
    files = []
    for f in root.rglob("*.html"):
        parts = set(f.parts)
        if any(ig in parts or ig in f.name for ig in IGNORE_PATTERNS):
            continue
        # Skip .bak files accidentally named .html
        if ".bak" in f.name:
            continue
        files.append(f)
    return files


def build_path_index(files: list[Path], root: Path, base_url: str) -> dict[str, Path]:
    """Map relative URL path → file Path for all current files."""
    index = {}
    for f in files:
        url = file_to_url(f, root, base_url)
        rel = url_to_path(url, base_url)
        index[rel] = f
    return index


def load_existing_vercel_json(root: Path) -> dict:
    """Load existing vercel.json or return a blank template."""
    vpath = root / "vercel.json"
    if vpath.exists():
        try:
            with open(vpath, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as e:
            print(f"  ⚠️  Could not parse existing vercel.json ({e}) — starting fresh.")
    return {}


def write_vercel_json(root: Path, new_redirects: list[dict], dry_run: bool):
    """Merge new 301 redirects into vercel.json without clobbering existing config."""
    config = load_existing_vercel_json(root)

    existing = config.get("redirects", [])
    # Build a set of existing source paths so we don't duplicate
    existing_sources = {r.get("source") for r in existing}

    added = []
    for r in new_redirects:
        if r["source"] not in existing_sources:
            existing.append(r)
            added.append(r)

    config["redirects"] = existing

    if dry_run:
        print(f"\n  [DRY RUN] Would write {len(added)} new redirect(s) to vercel.json")
        for r in added[:10]:
            print(f"    {r['source']}  →  {r['destination']}")
        if len(added) > 10:
            print(f"    ... and {len(added) - 10} more")
        return len(added)

    vpath = root / "vercel.json"
    with open(vpath, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
    print(f"\n  ✅ vercel.json written with {len(added)} new redirect(s)  →  {vpath}")
    return len(added)


def write_sitemap(root: Path, files: list[Path], base_url: str, dry_run: bool):
    """Generate a fresh sitemap.xml from the current file set."""
    urls = sorted(set(file_to_url(f, root, base_url) for f in files))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for url in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append(f"    <lastmod>{TODAY}</lastmod>")
        lines.append("    <changefreq>monthly</changefreq>")
        lines.append("    <priority>0.7</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")

    xml_str = "\n".join(lines)

    if dry_run:
        print(f"\n  [DRY RUN] Would write sitemap.xml with {len(urls)} URLs")
        return len(urls)

    out = root / "sitemap_new.xml"
    out.write_text(xml_str, encoding="utf-8")
    print(f"  ✅ New sitemap written ({len(urls)} URLs)  →  {out}")
    print(f"     Review it, then rename to sitemap.xml when ready.")
    return len(urls)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Sync sitemap → vercel.json redirects + new sitemap.")
    parser.add_argument("--dir",       required=True,         help="Root directory of your site")
    parser.add_argument("--base-url",  default=BASE_URL,      help="Site base URL")
    parser.add_argument("--dry-run",   action="store_true",   help="Preview without writing files")
    parser.add_argument("--threshold", type=int, default=55,  help="Fuzzy match threshold 0-100 (default 55)")
    args = parser.parse_args()

    root     = Path(args.dir)
    base_url = args.base_url.rstrip("/")

    if not root.exists():
        print(f"ERROR: Directory not found: {root}")
        exit(1)

    sitemap_path = root / "sitemap.xml"
    if not sitemap_path.exists():
        print(f"ERROR: sitemap.xml not found in {root}")
        exit(1)

    print(f"\n{'═'*60}")
    print(f"  Site root  : {root}")
    print(f"  Base URL   : {base_url}")
    print(f"  Threshold  : {args.threshold}%")
    if args.dry_run:
        print("  Mode       : DRY RUN (no files will be changed)")
    print(f"{'═'*60}\n")

    # 1. Parse sitemap
    sitemap_paths = parse_sitemap(sitemap_path, base_url)
    print(f"📄 Sitemap URLs      : {len(sitemap_paths)}")

    # 2. Get current files
    current_files = get_current_files(root)
    path_index    = build_path_index(current_files, root, base_url)
    current_paths = list(path_index.keys())
    print(f"📁 Current HTML files: {len(current_files)}")

    # 3. Find missing (old) paths
    sitemap_set  = set(sitemap_paths)
    current_set  = set(current_paths)
    missing      = sorted(sitemap_set - current_set)
    still_exists = sorted(sitemap_set & current_set)

    print(f"\n✅ Still exist       : {len(still_exists)}")
    print(f"❌ Missing (renamed?): {len(missing)}")

    if not missing:
        print("\n🎉 Nothing missing — sitemap matches file structure perfectly!")
    else:
        print(f"\n{'─'*60}")
        print("  Fuzzy-matching missing URLs to current files...\n")

    # 4. Match missing → current
    redirects        = []
    unmatched        = []
    match_candidates = [p for p in current_paths if p not in sitemap_set]  # prefer new paths

    for old_path in missing:
        matched, score = best_match(old_path, match_candidates, args.threshold)
        if matched:
            old_url = f"/{old_path}" if old_path else "/"
            new_url = f"/{matched}" if matched else "/"
            redirects.append({
                "source":      old_url,
                "destination": new_url,
                "permanent":   True      # Vercel treats this as 301
            })
            print(f"  {score:3d}%  {old_url}")
            print(f"        → {new_url}\n")
        else:
            unmatched.append(old_path)

    if unmatched:
        print(f"\n⚠️  Could not auto-match {len(unmatched)} URL(s) — review manually:")
        for u in unmatched:
            print(f"    /{u}")
        print(f"\n  Tip: re-run with --threshold 40 to catch more, or add these")
        print(f"  redirects manually to vercel.json pointing to /404 or a new URL.")

    # 5. Write vercel.json
    if redirects:
        write_vercel_json(root, redirects, dry_run=args.dry_run)

    # 6. Write new sitemap
    write_sitemap(root, current_files, base_url, dry_run=args.dry_run)

    # 7. Summary
    print(f"\n{'═'*60}")
    print(f"  Sitemap URLs    : {len(sitemap_paths)}")
    print(f"  Still exist     : {len(still_exists)}")
    print(f"  Auto-redirected : {len(redirects)}")
    print(f"  Unmatched       : {len(unmatched)}")
    print(f"  New sitemap URLs: {len(current_files)}")
    print(f"{'═'*60}\n")

    if not args.dry_run and (redirects or unmatched):
        print("Next steps:")
        print("  1. Review vercel.json redirects")
        print("  2. Manually add any unmatched URLs above")
        print("  3. Rename sitemap_new.xml → sitemap.xml")
        print("  4. Deploy to Vercel")
        print("  5. Submit new sitemap in Google Search Console\n")


if __name__ == "__main__":
    main()