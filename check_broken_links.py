"""
check_broken_links.py
=====================
Scans all HTML files in a directory and checks every <a href> link for:
  - Internal links  → checks if the target file exists on disk
  - External links  → makes a real HTTP request to verify the URL is live

Outputs a CSV report: broken_links_report.csv

Usage:
  python check_broken_links.py --root .

Optional flags:
  --root            Path to your site root (default: current directory)
  --out             Output CSV path (default: broken_links_report.csv)
  --skip-external   Only check internal links (faster, no network needed)
  --threads         Number of parallel threads for external checks (default: 10)
  --timeout         HTTP request timeout in seconds (default: 10)

Requirements:
  pip install beautifulsoup4 lxml requests
"""

import argparse
import csv
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_URL = "https://www.texasspecialed.com"
USER_AGENT = (
    "Mozilla/5.0 (compatible; BrokenLinkChecker/1.0; "
    "+https://www.texasspecialed.com)"
)
SKIP_SCHEMES = {"mailto", "tel", "javascript", "#"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_all_html_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.html") if ".bak" not in p.suffixes)


def extract_links(html_file: Path) -> list[str]:
    """Return all href values found in <a> tags."""
    try:
        soup = BeautifulSoup(
            html_file.read_text(encoding="utf-8", errors="replace"), "lxml"
        )
        return [
            a["href"].strip()
            for a in soup.find_all("a", href=True)
            if a["href"].strip()
        ]
    except Exception:
        return []


def html_file_to_url(file_path: Path, root: Path) -> str:
    """Convert a file path to its full URL."""
    rel = file_path.relative_to(root)
    parts = list(rel.parts)
    if parts and parts[-1].lower() in ("index.html", "index.htm"):
        parts = parts[:-1]
    elif parts and parts[-1].lower().endswith(".html"):
        parts[-1] = parts[-1][:-5]
    path = "/" + "/".join(parts) if parts else "/"
    return BASE_URL + path


def resolve_internal_url(href: str, source_url: str) -> str:
    """Resolve a relative or absolute path to a full URL."""
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return urljoin(source_url + "/", href).rstrip("/") or BASE_URL


def url_to_file(url: str, root: Path) -> Path | None:
    """
    Given a full URL, find the matching HTML file on disk.
    Strips the base URL, then tries <path>.html and <path>/index.html.
    """
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    candidates = [
        root / (path + ".html"),
        root / path / "index.html",
        root / path / "index.htm",
        root / (path.rstrip("/") + ".html"),
    ]
    # Also try the raw path in case it already has .html
    candidates.append(root / path)

    for c in candidates:
        if c.exists() and c.is_file():
            return c
    return None


# ---------------------------------------------------------------------------
# Link checkers
# ---------------------------------------------------------------------------

def check_internal(href: str, source_url: str, root: Path) -> dict | None:
    """
    Returns a result dict if the link is broken, else None.
    Only processes links that point to the same domain or are relative.
    """
    parsed = urlparse(href)

    # Skip external, anchors, mailto, tel, etc.
    if parsed.scheme in SKIP_SCHEMES:
        return None
    if parsed.scheme in ("http", "https"):
        host = parsed.netloc.replace("www.", "")
        own_host = urlparse(BASE_URL).netloc.replace("www.", "")
        if host != own_host:
            return None  # external — handled separately

    full_url = resolve_internal_url(href, source_url)
    # Strip fragment
    full_url = full_url.split("#")[0].rstrip("/")

    target_file = url_to_file(full_url, root)
    if target_file is None:
        return {
            "type": "internal",
            "status": "MISSING FILE",
            "status_code": "",
            "href": href,
            "resolved_url": full_url,
        }
    return None


def check_external(href: str, timeout: int) -> dict | None:
    """
    Makes an HTTP HEAD (fallback to GET) request.
    Returns result dict if broken, else None.
    """
    try:
        resp = requests.head(
            href,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        # Some servers reject HEAD; retry with GET
        if resp.status_code in (405, 403, 501):
            resp = requests.get(
                href,
                timeout=timeout,
                allow_redirects=True,
                headers={"User-Agent": USER_AGENT},
                stream=True,
            )
        if resp.status_code >= 400:
            return {
                "type": "external",
                "status": "HTTP ERROR",
                "status_code": resp.status_code,
                "href": href,
                "resolved_url": resp.url,
            }
    except requests.exceptions.ConnectionError:
        return {
            "type": "external",
            "status": "CONNECTION ERROR",
            "status_code": "",
            "href": href,
            "resolved_url": href,
        }
    except requests.exceptions.Timeout:
        return {
            "type": "external",
            "status": "TIMEOUT",
            "status_code": "",
            "href": href,
            "resolved_url": href,
        }
    except Exception as e:
        return {
            "type": "external",
            "status": f"ERROR: {e}",
            "status_code": "",
            "href": href,
            "resolved_url": href,
        }
    return None


# ---------------------------------------------------------------------------
# Main scan
# ---------------------------------------------------------------------------

def scan(root: Path, args) -> list[dict]:
    """
    Walk all HTML files, collect links, check them, return broken ones.
    """
    html_files = get_all_html_files(root)
    if not html_files:
        print("No HTML files found.")
        return []

    print(f"Scanning {len(html_files)} HTML file(s)...\n")

    # Collect all (source_page, href) pairs first
    all_links: list[tuple[str, str, str]] = []  # (source_file_str, source_url, href)
    for f in html_files:
        source_url = html_file_to_url(f, root)
        hrefs = extract_links(f)
        for href in hrefs:
            all_links.append((str(f.relative_to(root)), source_url, href))

    print(f"Found {len(all_links)} total link(s) across all pages.")

    broken: list[dict] = []

    # --- Internal links (fast, no network) ---
    print("Checking internal links...")
    internal_count = 0
    for source_rel, source_url, href in all_links:
        parsed = urlparse(href)
        if parsed.scheme in SKIP_SCHEMES:
            continue
        is_external = parsed.scheme in ("http", "https") and (
            parsed.netloc.replace("www.", "") != urlparse(BASE_URL).netloc.replace("www.", "")
        )
        if is_external:
            continue
        internal_count += 1
        result = check_internal(href, source_url, root)
        if result:
            result["source_file"] = source_rel
            result["source_url"] = source_url
            broken.append(result)

    print(f"  Checked {internal_count} internal link(s). "
          f"Found {sum(1 for b in broken if b['type'] == 'internal')} broken.\n")

    # --- External links (parallel HTTP checks) ---
    if not args.skip_external:
        external_links = [
            (source_rel, source_url, href)
            for source_rel, source_url, href in all_links
            if urlparse(href).scheme in ("http", "https")
            and urlparse(href).netloc.replace("www.", "") != urlparse(BASE_URL).netloc.replace("www.", "")
        ]

        # Deduplicate URLs but track all sources
        url_to_sources: dict[str, list[tuple[str, str]]] = {}
        for source_rel, source_url, href in external_links:
            url_to_sources.setdefault(href, []).append((source_rel, source_url))

        unique_external = list(url_to_sources.keys())
        print(f"Checking {len(unique_external)} unique external URL(s) "
              f"using {args.threads} thread(s)...")

        ext_broken_before = len(broken)
        done = 0

        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_url = {
                executor.submit(check_external, url, args.timeout): url
                for url in unique_external
            }
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                done += 1
                print(f"  [{done}/{len(unique_external)}] {url[:80]}", end="\r")
                result = future.result()
                if result:
                    for source_rel, source_url in url_to_sources[url]:
                        entry = dict(result)
                        entry["source_file"] = source_rel
                        entry["source_url"] = source_url
                        broken.append(entry)

        print(f"\n  Checked {len(unique_external)} external URL(s). "
              f"Found {len(broken) - ext_broken_before} broken.\n")

    return broken


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

def write_report(broken: list[dict], out_path: Path):
    fields = [
        "source_file", "source_url", "type",
        "status", "status_code", "href", "resolved_url",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in broken:
            writer.writerow({k: row.get(k, "") for k in fields})
    print(f"Report saved to: {out_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    global BASE_URL  # must be declared before any reference to BASE_URL in this function

    parser = argparse.ArgumentParser(
        description="Check for broken internal and external links in HTML files."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory of your HTML files (default: current directory)",
    )
    parser.add_argument(
        "--out",
        default="broken_links_report.csv",
        help="Output CSV file path (default: broken_links_report.csv)",
    )
    parser.add_argument(
        "--skip-external",
        action="store_true",
        help="Only check internal links — skip HTTP requests entirely",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=10,
        help="Parallel threads for external link checks (default: 10)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="HTTP request timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--base-url",
        default=BASE_URL,
        help="Base URL of your site (default: https://www.texasspecialed.com)",
    )
    args = parser.parse_args()

    BASE_URL = args.base_url.rstrip("/")

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: --root '{root}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.out).resolve()

    print(f"Site root : {root}")
    print(f"Base URL  : {BASE_URL}")
    print(f"Output    : {out_path}")
    print(f"External  : {'SKIP' if args.skip_external else f'YES ({args.threads} threads)'}\n")

    start = time.time()
    broken = scan(root, args)
    elapsed = time.time() - start

    print(f"\n{'='*60}")
    print(f"TOTAL BROKEN LINKS: {len(broken)}")
    print(f"Time taken        : {elapsed:.1f}s")
    print(f"{'='*60}\n")

    if broken:
        write_report(broken, out_path)
        # Print a quick summary to the terminal
        print(f"\n{'SOURCE FILE':<45} {'TYPE':<10} {'STATUS':<20} HREF")
        print("-" * 110)
        for b in sorted(broken, key=lambda x: (x["source_file"], x["href"])):
            print(
                f"{b['source_file']:<45} "
                f"{b['type']:<10} "
                f"{b['status']:<20} "
                f"{b['href']}"
            )
    else:
        print("No broken links found!")


if __name__ == "__main__":
    main()