"""
Sitemap Generator for TexasSpecialEd.com
=========================================
Scans your LOCAL site folder and generates a clean sitemap.xml.
Much faster and catches every page regardless of whether it's linked.

Usage:
    python generate_sitemap.py --dir .
    python generate_sitemap.py --dir "C:/Users/elisa/OneDrive/Documents/texas-special-ed-site"
    python generate_sitemap.py --dir . --output sitemap.xml
"""

import os
import argparse
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
from urllib.parse import urljoin

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BASE_URL    = "https://www.texasspecialed.com"
OUTPUT_FILE = "sitemap.xml"

# Skip these folders entirely
SKIP_DIRS = {
    "_canonical_backups", ".git", "node_modules", "assets",
    "images", "styles", "scripts", "fonts", "css", "js"
}

# Skip these filenames
SKIP_FILES = {
    "404.html", "500.html", "offline.html"
}

# (path_contains, priority, changefreq) — first match wins
PRIORITY_RULES = [
    ("/store",                       "0.9", "monthly"),
    ("/resources",                   "0.8", "monthly"),
    ("/blog",                        "0.8", "weekly"),
    ("/about",                       "0.7", "monthly"),
    ("/contact",                     "0.7", "monthly"),
    ("/disclaimer",                  "0.6", "monthly"),
    ("ard-process-guide",            "0.8", "monthly"),
    ("evaluation-child-find",        "0.8", "monthly"),
    ("dyslexia-services",            "0.8", "monthly"),
    ("grievance-dispute-resolution", "0.7", "monthly"),
    ("leadership-directory",         "0.6", "monthly"),
    ("/districts",                   "0.8", "monthly"),
]
DEFAULT_PRIORITY   = "0.5"
DEFAULT_CHANGEFREQ = "monthly"
# ──────────────────────────────────────────────────────────────────────────────


def file_to_url(filepath, site_dir):
    """
    Convert a local file path to its clean canonical URL.
    e.g. districts/houston-isd/ard-process-guide.html
      -> https://www.texasspecialed.com/districts/houston-isd/ard-process-guide
    """
    # Get path relative to site root
    rel = os.path.relpath(filepath, site_dir)

    # Normalize to forward slashes
    rel = rel.replace("\\", "/")

    # Strip .html
    if rel.endswith(".html"):
        rel = rel[:-5]

    # index files become their parent directory URL
    if rel.endswith("/index"):
        rel = rel[:-6]  # strip /index
    elif rel == "index":
        rel = ""         # root index.html → homepage

    # Build full URL
    url = BASE_URL + ("/" + rel if rel else "/")

    return url


def get_priority_and_changefreq(url):
    path = url.replace(BASE_URL, "")
    if path in ("/", ""):
        return "1.0", "weekly"
    if path in ("/districts", "/districts/"):
        return "0.9", "monthly"
    for pattern, priority, changefreq in PRIORITY_RULES:
        if pattern in path:
            return priority, changefreq
    return DEFAULT_PRIORITY, DEFAULT_CHANGEFREQ


def scan_local_files(site_dir):
    pages = {}
    today = datetime.now().strftime("%Y-%m-%d")
    total = 0

    print(f"\nScanning: {os.path.abspath(site_dir)}\n")

    for root, dirs, files in os.walk(site_dir):
        # Skip unwanted directories in-place
        dirs[:] = [
            d for d in dirs
            if d not in SKIP_DIRS and not d.startswith(".")
        ]

        for filename in files:
            if not filename.endswith(".html"):
                continue
            if filename in SKIP_FILES:
                continue

            filepath = os.path.join(root, filename)
            url = file_to_url(filepath, site_dir)
            priority, changefreq = get_priority_and_changefreq(url)

            pages[url] = {
                "lastmod":    today,
                "changefreq": changefreq,
                "priority":   priority,
            }
            total += 1
            print(f"  FOUND  {url}")

    print(f"\n  {total} pages found")
    return pages


def build_sitemap(pages, output_file):
    urlset = ET.Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    def sort_key(url):
        path = url.replace(BASE_URL, "")
        if path in ("/", ""):
            return (0, url)
        if path == "/districts":
            return (1, url)
        depth = path.count("/")
        if depth == 1:
            return (2, url)
        if depth == 2:
            return (3, url)
        return (4, url)

    for url in sorted(pages.keys(), key=sort_key):
        meta = pages[url]
        url_el = ET.SubElement(urlset, "url")
        ET.SubElement(url_el, "loc").text        = url
        ET.SubElement(url_el, "lastmod").text     = meta["lastmod"]
        ET.SubElement(url_el, "changefreq").text  = meta["changefreq"]
        ET.SubElement(url_el, "priority").text    = meta["priority"]

    raw    = ET.tostring(urlset, encoding="unicode")
    pretty = minidom.parseString(raw).toprettyxml(indent="  ")
    lines  = pretty.split("\n")[1:]
    output = '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(lines)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"\n{'='*50}")
    print(f"  Sitemap written : {output_file}")
    print(f"  Total URLs      : {len(pages)}")
    print(f"  Generated       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate sitemap.xml from local HTML files.")
    parser.add_argument("--dir",    required=True, help="Root folder of your site")
    parser.add_argument("--output", default=OUTPUT_FILE, help="Output file (default: sitemap.xml)")
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print(f"ERROR: Directory not found: {args.dir}")
        exit(1)

    pages = scan_local_files(args.dir)
    build_sitemap(pages, args.output)