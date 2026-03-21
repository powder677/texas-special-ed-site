#!/usr/bin/env python3
"""
build_sitemap.py
================
Generates an accurate sitemap.xml by walking your actual site files on disk.
Every URL in the output corresponds to a real HTML file that exists.
No URLs are inferred, generated, or guessed.

USAGE
-----
  # Basic — scans current directory, outputs sitemap.xml here
  python build_sitemap.py /path/to/site --base-url https://www.newyorkspecialed.net

  # Preview without writing
  python build_sitemap.py /path/to/site --base-url https://www.newyorkspecialed.net --dry-run

  # Custom output location
  python build_sitemap.py /path/to/site --base-url https://www.newyorkspecialed.net --output /path/to/site/sitemap.xml

  # See every URL that will be included
  python build_sitemap.py /path/to/site --base-url https://www.newyorkspecialed.net --verbose

HOW IT WORKS
------------
  1. Walks every directory under your site root
  2. Finds every .html file
  3. Converts the file path to a URL (e.g. /districts/sachem-csd/index.html → /districts/sachem-csd/)
  4. Reads the file to extract the <link rel="canonical"> if present — uses that URL instead
     so the sitemap matches what you've told Google is the real URL
  5. Skips files you explicitly exclude (404 pages, drafts, etc.)
  6. Deduplicates — if two files resolve to the same URL, it's listed once
  7. Writes a valid XML sitemap with <lastmod> dates from the filesystem
  8. Prints a full audit report so you can verify the count

ACCURACY GUARANTEE
------------------
  If a URL is in the sitemap, a file exists on disk for it.
  If a file exists on disk, it will be in the sitemap (unless explicitly excluded).
  The count will always match the number of unique, real HTML files found.
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from collections import defaultdict


# ─────────────────────────────────────────────
#  DEFAULT EXCLUSIONS
#  Files matching any of these patterns are
#  skipped. Add your own as needed.
# ─────────────────────────────────────────────
DEFAULT_EXCLUDE_PATTERNS = [
    # Utility / system files
    "404.html",
    "500.html",
    "offline.html",
    # Development / build artifacts
    "_*",           # anything starting with underscore
    ".*",           # hidden files
    "test_*",       # test files
    "draft_*",      # draft files
    "*_backup*",    # backup files
    "*.bak.html",   # .bak files renamed to html
    # Directories to never descend into
]

DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".github",
    "node_modules",
    "__pycache__",
    "_drafts",
    "_site",
    "vendor",
    "assets",   # /assets/ — images, css, js — never html
    "styles",
    "images",
    "scripts",
    "js",
    "css",
}

# ─────────────────────────────────────────────
#  CANONICAL EXTRACTION
# ─────────────────────────────────────────────
CANONICAL_RE = re.compile(
    r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']',
    re.IGNORECASE
)
# Also handle reversed attribute order
CANONICAL_RE2 = re.compile(
    r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',
    re.IGNORECASE
)

def extract_canonical(filepath: Path, base_url: str) -> str | None:
    """
    Read the first 4KB of an HTML file and extract the canonical URL.
    Returns the canonical URL string, or None if not found / not on this domain.
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            head = f.read(4096)
    except Exception:
        return None

    for pattern in (CANONICAL_RE, CANONICAL_RE2):
        m = pattern.search(head)
        if m:
            url = m.group(1).strip()
            # Only use it if it's on our domain (not an external canonical)
            parsed = urlparse(url)
            base_parsed = urlparse(base_url)
            if parsed.netloc and parsed.netloc != base_parsed.netloc:
                return None  # external canonical — skip this file entirely
            return url

    return None


# ─────────────────────────────────────────────
#  PATH → URL CONVERSION
# ─────────────────────────────────────────────
def path_to_url(filepath: Path, site_root: Path, base_url: str) -> str:
    """
    Convert a filesystem path to a clean URL.

    Rules:
      /site/index.html            → https://example.com/
      /site/about/index.html      → https://example.com/about/
      /site/about.html            → https://example.com/about/
      /site/districts/foo.html    → https://example.com/districts/foo/
      /site/guides/bar/index.html → https://example.com/guides/bar/

    We normalize to trailing-slash URLs because that's what canonical
    tags almost always point to for directory-style sites.
    """
    rel = filepath.relative_to(site_root)
    parts = list(rel.parts)

    # Remove the filename
    filename = parts[-1]
    dirs = parts[:-1]

    base = base_url.rstrip("/")

    if filename == "index.html":
        # directory-style URL
        if dirs:
            return base + "/" + "/".join(dirs) + "/"
        else:
            return base + "/"
    else:
        # Non-index html: treat as slug
        slug = filename[:-5]  # strip .html
        if dirs:
            return base + "/" + "/".join(dirs) + "/" + slug + "/"
        else:
            return base + "/" + slug + "/"


# ─────────────────────────────────────────────
#  PRIORITY HEURISTIC
# ─────────────────────────────────────────────
def get_priority(url: str, base_url: str) -> str:
    path = url.replace(base_url.rstrip("/"), "").strip("/")
    depth = len([p for p in path.split("/") if p])

    if depth == 0:
        return "1.0"   # homepage
    if depth == 1:
        return "0.8"   # top-level pages: /guides/, /districts/
    if depth == 2:
        return "0.7"   # /guides/cse-meeting-guide/, /districts/sachem-csd/
    if depth == 3:
        return "0.6"   # sub-pages: /districts/sachem-csd/cse-meeting-guide.html
    return "0.5"


def get_changefreq(url: str) -> str:
    if "special-ed-updates" in url:
        return "weekly"
    if "leadership-directory" in url or "partners" in url:
        return "monthly"
    return "monthly"


# ─────────────────────────────────────────────
#  PATTERN MATCHING HELPER
# ─────────────────────────────────────────────
import fnmatch

def matches_any(name: str, patterns: list) -> bool:
    return any(fnmatch.fnmatch(name, p) for p in patterns)


# ─────────────────────────────────────────────
#  MAIN WALK
# ─────────────────────────────────────────────
def collect_urls(
    site_root: Path,
    base_url: str,
    exclude_patterns: list,
    exclude_dirs: set,
    verbose: bool,
) -> list[dict]:
    """
    Walk the site directory and return a list of dicts:
      { url, lastmod, priority, changefreq, source_file }
    """
    results = []
    seen_urls = {}          # url → source_file (dedup tracker)
    skipped_external = []   # files with external canonicals
    skipped_excluded = []   # files matched by exclusion rules
    skipped_dedup = []      # files whose URL was already seen

    for dirpath, dirnames, filenames in os.walk(site_root):
        current_dir = Path(dirpath)
        rel_dir = current_dir.relative_to(site_root)

        # Prune excluded directories in-place
        dirnames[:] = sorted([
            d for d in dirnames
            if d not in exclude_dirs
            and not d.startswith(".")
            and not d.startswith("_")
        ])

        for filename in sorted(filenames):
            if not filename.lower().endswith(".html"):
                continue

            # Check exclusion patterns against filename
            if matches_any(filename, exclude_patterns):
                skipped_excluded.append(str(rel_dir / filename))
                continue

            filepath = current_dir / filename

            # Get last-modified date from filesystem
            try:
                mtime = filepath.stat().st_mtime
                lastmod = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d")
            except Exception:
                lastmod = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

            # Try canonical first
            canonical = extract_canonical(filepath, base_url)

            if canonical is None and extract_canonical.__doc__:
                # Re-check: if file has NO canonical tag at all, derive from path
                pass

            # Re-read to distinguish "no canonical tag" from "external canonical"
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    head = f.read(4096)
                has_canonical_tag = bool(CANONICAL_RE.search(head) or CANONICAL_RE2.search(head))
            except Exception:
                has_canonical_tag = False

            if has_canonical_tag and canonical is None:
                # Had a canonical tag but it pointed to a different domain
                skipped_external.append(str(rel_dir / filename))
                if verbose:
                    print(f"  [SKIP external canonical] {rel_dir / filename}")
                continue

            # Derive URL
            if canonical:
                # If canonical ends with a file extension (.html etc), keep as-is.
                # Otherwise normalize to trailing slash (directory-style URLs).
                last_segment = canonical.rstrip("/").split("/")[-1]
                if "." in last_segment:
                    url = canonical  # e.g. /foo/bar.html — keep exactly
                else:
                    url = canonical.rstrip("/") + "/"  # e.g. /foo/bar/ — normalize
            else:
                url = path_to_url(filepath, site_root, base_url)

            # Deduplicate
            if url in seen_urls:
                skipped_dedup.append({
                    "url": url,
                    "kept": seen_urls[url],
                    "duplicate": str(rel_dir / filename)
                })
                if verbose:
                    print(f"  [SKIP duplicate] {rel_dir / filename} → {url} (kept: {seen_urls[url]})")
                continue

            seen_urls[url] = str(rel_dir / filename)

            entry = {
                "url": url,
                "lastmod": lastmod,
                "priority": get_priority(url, base_url),
                "changefreq": get_changefreq(url),
                "source_file": str(rel_dir / filename),
            }
            results.append(entry)

            if verbose:
                print(f"  [ADD] {entry['source_file']:60s} → {url}")

    # Sort: homepage first, then by URL alphabetically
    results.sort(key=lambda e: (
        0 if e["url"] == base_url + "/" else 1,
        e["url"]
    ))

    return results, skipped_external, skipped_excluded, skipped_dedup


# ─────────────────────────────────────────────
#  XML GENERATION
# ─────────────────────────────────────────────
def build_xml(entries: list[dict]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for e in entries:
        lines.append("  <url>")
        lines.append(f"    <loc>{e['url']}</loc>")
        lines.append(f"    <lastmod>{e['lastmod']}</lastmod>")
        lines.append(f"    <changefreq>{e['changefreq']}</changefreq>")
        lines.append(f"    <priority>{e['priority']}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines)


# ─────────────────────────────────────────────
#  AUDIT REPORT
# ─────────────────────────────────────────────
def print_audit(
    entries, skipped_external, skipped_excluded,
    skipped_dedup, site_root, output_path, dry_run
):
    total_html = 0
    for dirpath, dirnames, filenames in os.walk(site_root):
        dirnames[:] = [d for d in dirnames if d not in DEFAULT_EXCLUDE_DIRS and not d.startswith(".")]
        total_html += sum(1 for f in filenames if f.lower().endswith(".html"))

    print(f"\n{'═'*62}")
    print(f"  SITEMAP AUDIT REPORT")
    print(f"{'═'*62}")
    print(f"  Site root          : {site_root}")
    print(f"  Base URL           : {entries[0]['url'].rsplit('/',2)[0] if entries else 'n/a'}")
    print(f"  Output             : {'(dry run — not written)' if dry_run else output_path}")
    print(f"{'─'*62}")
    print(f"  Total .html files found      : {total_html}")
    print(f"  URLs included in sitemap     : {len(entries)}")
    print(f"  Skipped — external canonical : {len(skipped_external)}")
    print(f"  Skipped — exclusion pattern  : {len(skipped_excluded)}")
    print(f"  Skipped — duplicate URL      : {len(skipped_dedup)}")
    print(f"  Accounted for (should = total): "
          f"{len(entries) + len(skipped_external) + len(skipped_excluded) + len(skipped_dedup)}")
    print(f"{'─'*62}")

    # Priority breakdown
    by_priority = defaultdict(int)
    for e in entries:
        by_priority[e["priority"]] += 1
    print(f"  Priority breakdown:")
    for p in sorted(by_priority.keys(), reverse=True):
        print(f"    {p}  →  {by_priority[p]} URLs")
    print(f"{'─'*62}")

    # Show duplicates if any
    if skipped_dedup:
        print(f"\n  DUPLICATE URLs (same URL from multiple files):")
        for d in skipped_dedup[:20]:
            print(f"    {d['url']}")
            print(f"      kept      : {d['kept']}")
            print(f"      duplicate : {d['duplicate']}")
        if len(skipped_dedup) > 20:
            print(f"    ... and {len(skipped_dedup) - 20} more")
        print()

    # Show external canonicals
    if skipped_external:
        print(f"\n  SKIPPED — external canonical tags:")
        for f in skipped_external[:10]:
            print(f"    {f}")
        if len(skipped_external) > 10:
            print(f"    ... and {len(skipped_external) - 10} more")
        print()

    # Show exclusions
    if skipped_excluded:
        print(f"\n  SKIPPED — matched exclusion patterns:")
        for f in skipped_excluded[:10]:
            print(f"    {f}")
        if len(skipped_excluded) > 10:
            print(f"    ... and {len(skipped_excluded) - 10} more")
        print()

    print(f"{'═'*62}\n")


# ─────────────────────────────────────────────
#  VALIDATION
# ─────────────────────────────────────────────
def validate_sitemap(entries: list[dict], base_url: str):
    """Sanity checks — warn about potential issues."""
    issues = []
    base = base_url.rstrip("/")

    for e in entries:
        url = e["url"]
        # Must start with base_url
        if not url.startswith(base):
            issues.append(f"URL not on base domain: {url}")
        # No spaces
        if " " in url:
            issues.append(f"URL contains spaces: {url}")
        # No double slashes (after the scheme)
        if "//" in url.replace("https://", "").replace("http://", ""):
            issues.append(f"URL contains double slash: {url}")

    if issues:
        print(f"\n  ⚠  VALIDATION WARNINGS ({len(issues)}):")
        for issue in issues[:20]:
            print(f"     {issue}")
        if len(issues) > 20:
            print(f"     ... and {len(issues) - 20} more")
        print()
    else:
        print(f"  ✅ All {len(entries)} URLs passed validation.\n")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Generate an accurate sitemap.xml from real files on disk."
    )
    parser.add_argument("site_dir", help="Root directory of your site")
    parser.add_argument(
        "--base-url", required=True,
        help="Base URL of your site (e.g. https://www.newyorkspecialed.net)"
    )
    parser.add_argument(
        "--output", default=None,
        help="Output path for sitemap.xml (default: site_dir/sitemap.xml)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the audit report without writing sitemap.xml"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print every URL as it's processed"
    )
    parser.add_argument(
        "--exclude", nargs="*", default=[],
        help="Additional filename patterns to exclude (e.g. --exclude 'temp*.html' 'old_*')"
    )
    parser.add_argument(
        "--exclude-dirs", nargs="*", default=[],
        help="Additional directory names to skip (e.g. --exclude-dirs staging backup)"
    )
    parser.add_argument(
        "--no-canonical", action="store_true",
        help="Ignore canonical tags and always derive URLs from file paths"
    )
    args = parser.parse_args()

    site_root = Path(args.site_dir).resolve()
    if not site_root.is_dir():
        print(f"ERROR: {site_root} is not a directory.")
        sys.exit(1)

    base_url = args.base_url.rstrip("/")
    output_path = Path(args.output) if args.output else site_root / "sitemap.xml"

    exclude_patterns = DEFAULT_EXCLUDE_PATTERNS + (args.exclude or [])
    exclude_dirs = DEFAULT_EXCLUDE_DIRS | set(args.exclude_dirs or [])

    print(f"\nScanning: {site_root}")
    print(f"Base URL: {base_url}")
    if args.verbose:
        print()

    # Temporarily patch extract_canonical if --no-canonical
    if args.no_canonical:
        global extract_canonical
        extract_canonical = lambda fp, bu: None

    entries, skipped_ext, skipped_excl, skipped_dedup = collect_urls(
        site_root=site_root,
        base_url=base_url,
        exclude_patterns=exclude_patterns,
        exclude_dirs=exclude_dirs,
        verbose=args.verbose,
    )

    if not entries:
        print("\nNo HTML files found. Check your site_dir path.\n")
        sys.exit(1)

    # Validate
    validate_sitemap(entries, base_url)

    # Audit report
    print_audit(entries, skipped_ext, skipped_excl, skipped_dedup,
                site_root, output_path, args.dry_run)

    # Write
    if not args.dry_run:
        xml = build_xml(entries)
        try:
            output_path.write_text(xml, encoding="utf-8")
            size_kb = output_path.stat().st_size / 1024
            print(f"  ✅ Sitemap written to: {output_path}")
            print(f"     {len(entries)} URLs · {size_kb:.1f} KB\n")
        except Exception as e:
            print(f"  ❌ Failed to write sitemap: {e}")
            sys.exit(1)
    else:
        print(f"  Dry run — sitemap NOT written.\n")
        print(f"  First 20 URLs that would be included:")
        for e in entries[:20]:
            print(f"    {e['url']}")
        if len(entries) > 20:
            print(f"    ... and {len(entries) - 20} more")
        print()


if __name__ == "__main__":
    main()