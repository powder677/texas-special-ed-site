"""
fix_silo_links.py
=================
Injects internal silo navigation links into HTML files for texasspecialed.com.

Silo logic:
  - District pages: each district's 6 sub-pages cross-link to one another
      (ard-process-guide, dyslexia-services, evaluation-child-find,
       grievance-dispute-resolution, leadership-directory, partners)
  - Blog <-> Topic mirror pages: matching blog posts link to their
      standalone topic page and vice versa
  - Blog hub (/blog) links to all blog posts
  - Districts hub (/districts) links to all district index pages

Usage:
  python fix_silo_links.py --root /path/to/your/html/root

Optional flags:
  --dry-run          Print what would change without writing files
  --backup           Save a .bak copy of every file before editing
  --base-url         Override base URL (default: https://www.texasspecialed.com)
  --inject-before    CSS selector of element to insert nav BEFORE (default: footer)

Requirements:
  pip install beautifulsoup4 lxml
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from bs4 import BeautifulSoup, Tag

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://www.texasspecialed.com"

# The 6 sub-pages every district has
DISTRICT_SUBPAGES = [
    ("ard-process-guide",         "ARD Process Guide"),
    ("dyslexia-services",         "Dyslexia Services"),
    ("evaluation-child-find",     "Evaluation & Child Find"),
    ("grievance-dispute-resolution", "Grievance & Dispute Resolution"),
    ("leadership-directory",      "Leadership Directory"),
    ("partners",                  "Partners"),
]

# Blog slugs that have a matching top-level topic page
MIRROR_SLUGS = [
    "10-questions-to-ask-at-ard-meeting",
    "how-to-disagree-at-ard-meeting",
    "how-to-write-measurable-iep-goals",
    "independent-educational-evaluation-texas",
    "texas-parent-rights-special-education",
    "understanding-fiie-texas",
    "what-to-do-when-school-denies-evaluation",
]

# All blog post slugs (for blog hub page)
ALL_BLOG_SLUGS = [
    ("10-questions-to-ask-at-ard-meeting",     "10 Questions to Ask at an ARD Meeting"),
    ("ard-meeting-tips",                        "ARD Meeting Tips"),
    ("ard-rights-parents",                      "ARD Rights for Parents"),
    ("child-find-obligations",                  "Child Find Obligations"),
    ("due-process-texas",                       "Due Process in Texas"),
    ("dyslexia-hb3928-changes",                "Dyslexia HB3928 Changes"),
    ("fie-evaluation-timeline",                 "FIE Evaluation Timeline"),
    ("how-to-disagree-at-ard-meeting",          "How to Disagree at an ARD Meeting"),
    ("how-to-request-evaluation",               "How to Request an Evaluation"),
    ("how-to-write-measurable-iep-goals",       "How to Write Measurable IEP Goals"),
    ("iep-vs-504-texas",                        "IEP vs 504 in Texas"),
    ("independent-educational-evaluation-texas","Independent Educational Evaluation (Texas)"),
    ("manifestation-determination",             "Manifestation Determination"),
    ("prior-written-notice-texas",              "Prior Written Notice (Texas)"),
    ("special-ed-discipline-texas",             "Special Ed Discipline in Texas"),
    ("texas-parent-rights-special-education",   "Texas Parent Rights in Special Education"),
    ("understanding-fiie-texas",                "Understanding FIIE in Texas"),
    ("what-is-an-ard-meeting",                  "What Is an ARD Meeting?"),
    ("what-to-do-when-school-denies-evaluation","What to Do When School Denies Evaluation"),
]

# All district slugs (for districts hub page)
ALL_DISTRICT_SLUGS = [
    "abilene-isd", "aldine-isd", "alief-isd", "allen-isd", "alvin-isd",
    "amarillo-isd", "arlington-isd", "austin-isd", "bastrop-isd", "beaumont-isd",
    "belton-isd", "birdville-isd", "brownsville-isd", "bryan-isd", "burleson-isd",
    "carrollton-farmers-branch-isd", "channelview-isd", "clear-creek-isd",
    "clint-isd", "college-station-isd", "comal-isd", "conroe-isd", "coppell-isd",
    "copperas-cove-isd", "corpus-christi-isd", "crosby-isd", "crowley-isd",
    "cypress-fairbanks-isd", "dallas-isd", "del-valle-isd", "denton-isd",
    "dickinson-isd", "donna-isd", "eagle-mountain-saginaw-isd", "eanes-isd",
    "east-central-isd", "ector-county-isd", "edinburg-cisd", "el-paso-isd",
    "forney-isd", "fort-bend-isd", "fort-worth-isd", "friendswood-isd",
    "frisco-isd", "garland-isd", "georgetown-isd", "goose-creek-cisd",
    "grand-prairie-isd", "grapevine-colleyville-isd", "harlingen-cisd",
    "harmony-public-schools-combined", "hays-cisd", "houston-isd", "humble-isd",
    "hurst-euless-bedford-isd", "idea-public-schools", "irving-isd", "judson-isd",
    "katy-isd", "keller-isd", "killeen-isd", "klein-isd", "la-joya-isd",
    "lake-travis-isd", "lamar-cisd", "laredo-isd", "leander-isd", "lewisville-isd",
    "little-elm-isd", "longview-isd", "lubbock-isd", "magnolia-isd",
    "mansfield-isd", "mcallen-isd", "mckinney-isd", "melissa-isd", "mesquite-isd",
    "midland-isd", "midway-isd", "mission-cisd", "montgomery-isd", "new-caney-isd",
    "north-east-isd", "northside-isd", "northwest-isd", "pasadena-isd",
    "pflugerville-isd", "pharr-san-juan-alamo-isd", "plano-isd", "princeton-isd",
    "prosper-isd", "richardson-isd", "rio-grande-city-grulla-isd", "rockwall-isd",
    "round-rock-isd", "royse-city-isd", "san-angelo-isd", "san-antonio-isd",
    "san-benito-cisd", "san-marcos-cisd", "santa-fe-isd",
    "schertz-cibolo-universal-city-isd", "seguin-isd", "sherman-isd",
    "socorro-isd", "spring-branch-isd", "spring-isd", "temple-isd",
    "texarkana-isd", "texas-city-isd", "tomball-isd", "tyler-isd", "united-isd",
    "victoria-isd", "waco-isd", "waller-isd", "weslaco-isd", "wichita-falls-isd",
    "wylie-isd", "ysleta-isd",
]

NAV_ID = "silo-nav"          # id applied to injected <nav> so re-runs are idempotent

# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

STYLE = """
<style>
#silo-nav {
  margin: 2rem 0;
  padding: 1rem 1.5rem;
  background: #f4f8ff;
  border-left: 4px solid #1a56db;
  border-radius: 4px;
  font-family: inherit;
}
#silo-nav h3 {
  margin: 0 0 0.75rem;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #374151;
}
#silo-nav ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
#silo-nav ul li a {
  display: inline-block;
  padding: 0.3rem 0.75rem;
  background: #fff;
  border: 1px solid #c3dafe;
  border-radius: 999px;
  font-size: 0.875rem;
  color: #1a56db;
  text-decoration: none;
}
#silo-nav ul li a:hover { background: #1a56db; color: #fff; }
#silo-nav ul li a[aria-current="page"] {
  background: #1a56db;
  color: #fff;
  border-color: #1a56db;
  pointer-events: none;
}
</style>
""".strip()


def build_nav_html(heading: str, links: list[tuple[str, str]], current_url: str) -> str:
    """Return an HTML string for the silo nav block."""
    items = []
    for url, label in links:
        current = ' aria-current="page"' if url == current_url else ""
        items.append(f'    <li><a href="{url}"{current}>{label}</a></li>')
    items_html = "\n".join(items)
    return (
        f'\n{STYLE}\n'
        f'<nav id="{NAV_ID}" aria-label="Related pages">\n'
        f'  <h3>{heading}</h3>\n'
        f'  <ul>\n{items_html}\n  </ul>\n'
        f'</nav>\n'
    )


def slug_to_label(slug: str) -> str:
    """Convert a URL slug to a human-readable label."""
    return slug.replace("-", " ").title()


# ---------------------------------------------------------------------------
# Path / URL resolution
# ---------------------------------------------------------------------------

def html_file_to_url_path(file_path: Path, root: Path) -> str:
    """
    Convert a file system path to its URL path.
    Handles both flat (about.html) and nested (about/index.html) layouts.
    """
    rel = file_path.relative_to(root)
    parts = list(rel.parts)

    # Strip index.html at the end
    if parts and parts[-1].lower() == "index.html":
        parts = parts[:-1]
    elif parts and parts[-1].lower().endswith(".html"):
        parts[-1] = parts[-1][:-5]  # strip .html

    return "/" + "/".join(parts) if parts else "/"


def url_path_to_file(url_path: str, root: Path) -> Path | None:
    """
    Given a URL path, return the most likely HTML file on disk.
    Tries: <root><path>.html  and  <root><path>/index.html
    """
    stripped = url_path.strip("/")
    candidates = [
        root / (stripped + ".html"),
        root / stripped / "index.html",
        root / stripped / "index.htm",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


# ---------------------------------------------------------------------------
# Link injection
# ---------------------------------------------------------------------------

def inject_nav(html_file: Path, nav_html: str, inject_before: str,
               dry_run: bool, backup: bool) -> bool:
    """
    Parse an HTML file with BeautifulSoup, remove any existing silo nav,
    inject the new one, and write back.  Returns True if the file changed.
    """
    raw = html_file.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "lxml")

    # Remove stale silo nav (idempotent re-runs)
    existing = soup.find(id=NAV_ID)
    if existing:
        existing.decompose()

    # Build new nav fragment
    nav_soup = BeautifulSoup(nav_html, "lxml")
    # lxml wraps in <html><body>; grab real children
    nav_nodes = list(nav_soup.body.children) if nav_soup.body else []

    # Find insertion point
    target = soup.select_one(inject_before)
    if target is None:
        # Fall back to end of <body>
        target = soup.body
        if target is None:
            print(f"  [SKIP] no <body> found in {html_file}")
            return False
        for node in reversed(nav_nodes):
            target.append(node.__copy__() if hasattr(node, "__copy__") else node)
    else:
        for node in nav_nodes:
            target.insert_before(node.__copy__() if hasattr(node, "__copy__") else node)

    new_html = str(soup)
    if new_html == raw:
        return False

    if dry_run:
        print(f"  [DRY-RUN] would update {html_file}")
        return True

    if backup:
        shutil.copy2(html_file, html_file.with_suffix(".html.bak"))

    html_file.write_text(new_html, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Silo builders
# ---------------------------------------------------------------------------

def process_district_subpage(file_path: Path, root: Path,
                              url_path: str, args) -> bool:
    """Inject cross-links to sibling district sub-pages."""
    # url_path like /districts/austin-isd/ard-process-guide
    parts = url_path.strip("/").split("/")
    # parts = ["districts", "<district-slug>", "<subpage-slug>"]
    if len(parts) != 3:
        return False

    district_slug = parts[1]
    district_label = slug_to_label(district_slug)
    current_subpage = parts[2]

    links = []
    for subpage_slug, subpage_label in DISTRICT_SUBPAGES:
        url = f"{BASE_URL}/districts/{district_slug}/{subpage_slug}"
        links.append((url, subpage_label))

    current_full_url = f"{BASE_URL}{url_path}"
    nav_html = build_nav_html(
        f"{district_label} — Special Education Resources",
        links,
        current_full_url,
    )
    return inject_nav(file_path, nav_html, args.inject_before,
                      args.dry_run, args.backup)


def process_district_hub(file_path: Path, root: Path,
                         url_path: str, args) -> bool:
    """Inject district index links on the /districts hub page."""
    links = [
        (f"{BASE_URL}/districts/{slug}", slug_to_label(slug))
        for slug in ALL_DISTRICT_SLUGS
    ]
    nav_html = build_nav_html(
        "All Texas School Districts",
        links,
        f"{BASE_URL}{url_path}",
    )
    return inject_nav(file_path, nav_html, args.inject_before,
                      args.dry_run, args.backup)


def process_district_index(file_path: Path, root: Path,
                            url_path: str, args) -> bool:
    """Inject sub-page links on a district's own index page (/districts/<slug>)."""
    parts = url_path.strip("/").split("/")
    if len(parts) != 2:
        return False

    district_slug = parts[1]
    district_label = slug_to_label(district_slug)

    links = [
        (f"{BASE_URL}/districts/{district_slug}/{subpage_slug}", subpage_label)
        for subpage_slug, subpage_label in DISTRICT_SUBPAGES
    ]
    nav_html = build_nav_html(
        f"{district_label} — Special Education Pages",
        links,
        f"{BASE_URL}{url_path}",
    )
    return inject_nav(file_path, nav_html, args.inject_before,
                      args.dry_run, args.backup)


def process_blog_post(file_path: Path, root: Path,
                      url_path: str, args) -> bool:
    """Inject a link to the mirrored topic page (if one exists) + blog hub."""
    slug = url_path.strip("/").split("/")[-1]

    links = [(f"{BASE_URL}/blog", "← All Blog Posts")]

    if slug in MIRROR_SLUGS:
        topic_url = f"{BASE_URL}/{slug}"
        links.append((topic_url, f"📄 Topic Page: {slug_to_label(slug)}"))

    nav_html = build_nav_html(
        "Related Resources",
        links,
        f"{BASE_URL}{url_path}",
    )
    return inject_nav(file_path, nav_html, args.inject_before,
                      args.dry_run, args.backup)


def process_topic_page(file_path: Path, root: Path,
                       url_path: str, args) -> bool:
    """Inject a link to the mirrored blog post."""
    slug = url_path.strip("/")
    if slug not in MIRROR_SLUGS:
        return False

    blog_url = f"{BASE_URL}/blog/{slug}"
    links = [(blog_url, f"📝 Read the Blog Post: {slug_to_label(slug)}")]

    nav_html = build_nav_html(
        "Related Resources",
        links,
        f"{BASE_URL}{url_path}",
    )
    return inject_nav(file_path, nav_html, args.inject_before,
                      args.dry_run, args.backup)


def process_blog_hub(file_path: Path, root: Path,
                     url_path: str, args) -> bool:
    """Inject links to all blog posts on the /blog hub page."""
    links = [
        (f"{BASE_URL}/blog/{slug}", label)
        for slug, label in ALL_BLOG_SLUGS
    ]
    nav_html = build_nav_html(
        "All Blog Posts",
        links,
        f"{BASE_URL}{url_path}",
    )
    return inject_nav(file_path, nav_html, args.inject_before,
                      args.dry_run, args.backup)


# ---------------------------------------------------------------------------
# Router: decide which processor to call for each file
# ---------------------------------------------------------------------------

def route(file_path: Path, root: Path, args) -> tuple[str, bool]:
    """
    Determine the URL path of the file and call the right processor.
    Returns (url_path, changed).
    """
    url_path = html_file_to_url_path(file_path, root)
    parts = [p for p in url_path.strip("/").split("/") if p]

    changed = False

    # /districts hub
    if url_path in ("/districts", "/districts/"):
        changed = process_district_hub(file_path, root, url_path, args)

    # /districts/<slug>  (index page)
    elif len(parts) == 2 and parts[0] == "districts":
        changed = process_district_index(file_path, root, url_path, args)

    # /districts/<slug>/<subpage>
    elif len(parts) == 3 and parts[0] == "districts":
        changed = process_district_subpage(file_path, root, url_path, args)

    # /blog hub
    elif url_path in ("/blog", "/blog/"):
        changed = process_blog_hub(file_path, root, url_path, args)

    # /blog/<slug>
    elif len(parts) == 2 and parts[0] == "blog":
        changed = process_blog_post(file_path, root, url_path, args)

    # top-level topic pages that mirror blog posts
    elif len(parts) == 1 and parts[0] in MIRROR_SLUGS:
        changed = process_topic_page(file_path, root, url_path, args)

    return url_path, changed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    global BASE_URL  # declared first before any reference to BASE_URL

    parser = argparse.ArgumentParser(
        description="Inject silo navigation links into texasspecialed.com HTML files."
    )
    parser.add_argument(
        "--root",
        required=True,
        help="Root directory of your HTML files (e.g. ./public or ./dist)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing any files",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Save a .bak copy of each file before modifying it",
    )
    parser.add_argument(
        "--base-url",
        default=BASE_URL,
        help="Base URL of the site (default: https://www.texasspecialed.com)",
    )
    parser.add_argument(
        "--inject-before",
        default="footer",
        help="CSS selector of element to insert the nav block BEFORE (default: footer)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: --root '{root}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    # Allow overriding the base URL at runtime
    BASE_URL = args.base_url.rstrip("/")

    html_files = sorted(root.rglob("*.html"))
    if not html_files:
        print(f"No .html files found under {root}")
        sys.exit(0)

    print(f"Found {len(html_files)} HTML file(s) under {root}")
    if args.dry_run:
        print("DRY-RUN mode — no files will be written.\n")

    updated = 0
    skipped = 0

    for f in html_files:
        # Skip backup files from previous runs
        if f.suffix == ".bak":
            continue
        try:
            url_path, changed = route(f, root, args)
            if changed:
                updated += 1
                if not args.dry_run:
                    print(f"  ✓  Updated  {url_path}  →  {f.relative_to(root)}")
            else:
                skipped += 1
        except Exception as exc:
            print(f"  ✗  ERROR processing {f}: {exc}", file=sys.stderr)

    print(f"\nDone.  {updated} file(s) updated, {skipped} file(s) unchanged/skipped.")


if __name__ == "__main__":
    main()