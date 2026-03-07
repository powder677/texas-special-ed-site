"""
gsc_page_updater.py
Reads Google Search Console export data and uses Claude API to generate
targeted improvements for underperforming district pages.

Three types of updates based on GSC signals:
  1. TITLE/META  — high impressions, low CTR (page 1 but not getting clicked)
  2. CONTENT     — position 5-20, needs a targeted content section to rank higher
  3. FIE SILO    — district pages missing the /what-is-fie silo link (you added these this week)

Usage:
    pip install anthropic beautifulsoup4
    set ANTHROPIC_API_KEY=your_key

    # Analyze only — show recommendations, write nothing
    python gsc_page_updater.py --dry-run

    # Run all update types
    python gsc_page_updater.py

    # Run only one type
    python gsc_page_updater.py --type title
    python gsc_page_updater.py --type content
    python gsc_page_updater.py --type fie-silo

    # Single page
    python gsc_page_updater.py --only "districts/frisco-isd/leadership-directory"
"""

import anthropic
import csv
import json
import os
import re
import shutil
import time
import argparse
from datetime import datetime
from bs4 import BeautifulSoup

# ── CONFIG ────────────────────────────────────────────────────────────────────

SITE_ROOT   = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"
GSC_DIR     = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\gsc_exports"  # drop new GSC zips here
BACKUP_DIR  = os.path.join(SITE_ROOT, "_backups", datetime.now().strftime("%Y%m%d_%H%M%S"))
RESULTS_LOG = os.path.join(SITE_ROOT, "gsc_update_log.json")

BASE_URL    = "https://www.texasspecialed.com"

# ── THRESHOLDS FOR EACH UPDATE TYPE ──────────────────────────────────────────

# Pages with impressions >= this AND CTR <= this % → fix title/meta
TITLE_MIN_IMPRESSIONS = 30
TITLE_MAX_CTR         = 2.0   # percent

# Pages with position between these → generate content section
CONTENT_POS_MIN = 5.0
CONTENT_POS_MAX = 25.0
CONTENT_MIN_IMP = 20

# Districts that should have what-is-fie in their silo nav
# The script auto-detects if the link is missing
FIE_SILO_LINK_PATTERN = "what-is-fie"

client = anthropic.Anthropic()

# ── GSC DATA LOADING ──────────────────────────────────────────────────────────

def load_gsc_pages(path: str) -> list[dict]:
    """Load Pages.csv from GSC export."""
    pages = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                url      = row["Top pages"].strip()
                clicks   = int(row["Clicks"] or 0)
                impr     = int(row["Impressions"] or 0)
                ctr_raw  = row["CTR"].replace("%", "").strip()
                ctr      = float(ctr_raw) if ctr_raw else 0.0
                pos_raw  = row["Position"].strip()
                position = float(pos_raw) if pos_raw else 0.0
                pages.append({
                    "url": url, "clicks": clicks,
                    "impressions": impr, "ctr": ctr, "position": position
                })
            except (ValueError, KeyError):
                continue
    return pages


def load_gsc_queries(path: str) -> list[dict]:
    """Load Queries.csv from GSC export."""
    queries = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                query    = row["Top queries"].strip()
                clicks   = int(row["Clicks"] or 0)
                impr     = int(row["Impressions"] or 0)
                ctr_raw  = row["CTR"].replace("%", "").strip()
                ctr      = float(ctr_raw) if ctr_raw else 0.0
                pos_raw  = row["Position"].strip()
                position = float(pos_raw) if pos_raw else 0.0
                queries.append({
                    "query": query, "clicks": clicks,
                    "impressions": impr, "ctr": ctr, "position": position
                })
            except (ValueError, KeyError):
                continue
    return queries


def url_to_path(url: str) -> str:
    """Convert a GSC URL to a local HTML file path."""
    rel = url.replace(BASE_URL, "").lstrip("/")
    # Try with .html extension first, then as directory index
    candidates = [
        os.path.join(SITE_ROOT, rel + ".html"),
        os.path.join(SITE_ROOT, rel, "index.html"),
        os.path.join(SITE_ROOT, rel),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def url_to_rel(url: str) -> str:
    return url.replace(BASE_URL, "").lstrip("/")


# ── IDENTIFY OPPORTUNITIES ────────────────────────────────────────────────────

def find_title_opportunities(pages: list[dict]) -> list[dict]:
    """High impressions, low CTR — title/meta needs work."""
    results = []
    for p in pages:
        if p["impressions"] >= TITLE_MIN_IMPRESSIONS and p["ctr"] <= TITLE_MAX_CTR and p["position"] <= 20:
            path = url_to_path(p["url"])
            if path:
                results.append({**p, "local_path": path, "update_type": "title"})
    return sorted(results, key=lambda x: x["impressions"], reverse=True)


def find_content_opportunities(pages: list[dict], queries: list[dict]) -> list[dict]:
    """Position 5-25, decent impressions — needs better content to rank higher."""
    # Build a query→page mapping from URL patterns
    results = []
    for p in pages:
        if (CONTENT_POS_MIN <= p["position"] <= CONTENT_POS_MAX
                and p["impressions"] >= CONTENT_MIN_IMP):
            path = url_to_path(p["url"])
            if not path:
                continue
            # Find queries likely associated with this page (by URL slug matching)
            rel = url_to_rel(p["url"])
            slug_words = set(rel.replace("/", " ").replace("-", " ").split())
            related_queries = [
                q for q in queries
                if any(w in q["query"] for w in slug_words if len(w) > 3)
            ]
            related_queries = sorted(related_queries, key=lambda x: x["impressions"], reverse=True)[:5]
            results.append({
                **p,
                "local_path": path,
                "update_type": "content",
                "related_queries": related_queries
            })
    return sorted(results, key=lambda x: x["impressions"], reverse=True)


def find_fie_silo_gaps(pages: list[dict]) -> list[dict]:
    """District pages missing the what-is-fie silo nav link."""
    results = []
    # Only look at district pages (not blog/resources)
    district_pages = [p for p in pages if "/districts/" in p["url"] and "what-is-fie" not in p["url"]]

    for p in district_pages:
        path = url_to_path(p["url"])
        if not path:
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                html = f.read()
            if FIE_SILO_LINK_PATTERN not in html:
                # Extract district slug from URL
                match = re.search(r"/districts/([^/]+)", p["url"])
                district_slug = match.group(1) if match else None
                results.append({
                    **p,
                    "local_path": path,
                    "update_type": "fie-silo",
                    "district_slug": district_slug
                })
        except Exception:
            continue
    return results


# ── CLAUDE API CALLS ──────────────────────────────────────────────────────────

def generate_title_update(page: dict) -> dict:
    """Ask Claude to rewrite title tag and meta description."""
    path = page["local_path"]
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    current_title = soup.title.string if soup.title else ""
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    current_meta  = meta_desc_tag["content"] if meta_desc_tag else ""

    url = page["url"]
    rel = url_to_rel(url)

    prompt = f"""You are an SEO specialist for texasspecialed.com, a Texas special education parent resource site.

This page has {page['impressions']} impressions at position {page['position']:.1f} but only {page['ctr']:.1f}% CTR.
That means people see it but aren't clicking. The title or meta description isn't compelling enough.

Page URL: {url}
Current title: {current_title}
Current meta description: {current_meta}

Rewrite both to maximize clicks from Texas parents searching for special education help.
Rules:
- Title: 50-60 characters, include district name and specific topic, make it urgent/useful
- Meta: 140-155 characters, include a specific benefit or legal fact, end with a call to action
- Do NOT make up facts or invent staff names
- Write for a stressed parent, not for Google bots

Respond ONLY with valid JSON, no markdown:
{{"title": "...", "meta_description": "..."}}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    text = re.sub(r"```json|```", "", text).strip()
    return json.loads(text)


def generate_content_section(page: dict) -> str:
    """Ask Claude to write a targeted content section to improve ranking."""
    url = page["url"]
    rel = url_to_rel(url)
    queries_text = "\n".join([
        f"  - \"{q['query']}\" ({q['impressions']} impressions, pos {q['position']:.1f})"
        for q in page.get("related_queries", [])
    ])

    # Read current H1 for context
    path = page["local_path"]
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    h1_text = h1.get_text(strip=True) if h1 else rel

    prompt = f"""You are a Texas special education content writer for texasspecialed.com.

This page is ranking at position {page['position']:.1f} with {page['impressions']} impressions 
but needs stronger content to reach the top 3.

Page: {url}
Page H1: {h1_text}

Top queries this page is appearing for:
{queries_text if queries_text else "  (no query data available)"}

Write a SHORT supplemental content section (120-160 words) that:
1. Naturally targets the queries listed above
2. Adds a specific, useful fact about Texas special education law relevant to this page type
3. Uses the district name naturally in context
4. Is written for a stressed parent — plain English, warm, direct
5. Ends with one sentence linking the parent to take action (no URLs needed)

Output ONLY plain HTML <p> and <h3> tags. No markdown, no preamble, no explanation."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()


# ── HTML PATCHING ─────────────────────────────────────────────────────────────

def patch_title_meta(html: str, new_title: str, new_meta: str) -> str:
    """Replace title tag and meta description in HTML."""
    # Replace title
    html = re.sub(r"<title>.*?</title>", f"<title>{new_title}</title>", html, flags=re.DOTALL)
    # Replace meta description
    html = re.sub(
        r'(<meta\s+content=")[^"]*("\s+name="description"[^/]*/?>)',
        f'\\g<1>{new_meta}\\2',
        html
    )
    # Also handle reversed attribute order
    html = re.sub(
        r'(<meta\s+name="description"\s+content=")[^"]*("[^/]*/?>)',
        f'\\g<1>{new_meta}\\2',
        html
    )
    return html


def patch_content_section(html: str, new_section: str) -> str:
    """Inject content section just before </article>."""
    marker = "<!-- GSC_CONTENT_SECTION:START -->"
    if marker in html:
        return html  # already patched
    block = f"""
<!-- GSC_CONTENT_SECTION:START -->
<div class="gsc-content-supplement" style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #1a56db;border-radius:6px;padding:24px 28px;margin:2rem 0;font-family:'Source Sans 3',sans-serif;font-size:17px;line-height:1.75;color:#1a1a2e;">
{new_section}
</div>
<!-- GSC_CONTENT_SECTION:END -->
"""
    last_article = html.rfind("</article>")
    if last_article == -1:
        return None
    return html[:last_article] + block + html[last_article:]


def patch_fie_silo_link(html: str, district_slug: str) -> str:
    """Add what-is-fie link to the silo nav bar."""
    # Find the silo-nav div and insert the FIE link
    fie_link = f'<a href="/districts/{district_slug}/what-is-fie.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">What Is an FIE?</a>'

    # Look for the silo nav pattern and inject after "ARD Guide" link
    pattern = r'(ARD Guide</a>\s*•)'
    replacement = f'\\1\n    {fie_link} •'

    new_html = re.sub(pattern, replacement, html)
    if new_html == html:
        # Try alternate pattern — inject before Evaluations link
        pattern2 = r'(•\s*\n?\s*<a[^>]+>Evaluations)'
        replacement2 = f'• \n    {fie_link} •\n    <a'
        new_html = re.sub(pattern2, r'• \n    ' + fie_link + r' •\n    <a', html, count=1)

    return new_html


# ── BACKUP + WRITE ────────────────────────────────────────────────────────────

def backup_and_write(path: str, new_html: str, dry_run: bool) -> bool:
    if dry_run:
        return True
    os.makedirs(BACKUP_DIR, exist_ok=True)
    rel = os.path.relpath(path, SITE_ROOT)
    dest = os.path.join(BACKUP_DIR, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(path, dest)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    return True


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--type", choices=["title", "content", "fie-silo", "all"], default="all")
    parser.add_argument("--only", type=str, help="URL path fragment to match e.g. frisco-isd/leadership")
    args = parser.parse_args()

    # Load GSC data — look for CSV files in GSC_DIR or SITE_ROOT
    def find_csv(name):
        for d in [GSC_DIR, SITE_ROOT]:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
        return None

    pages_csv   = find_csv("Pages.csv")
    queries_csv = find_csv("Queries.csv")

    if not pages_csv:
        print("ERROR: Pages.csv not found. Drop your GSC export CSVs into the site root or gsc_exports folder.")
        return

    pages   = load_gsc_pages(pages_csv)
    queries = load_gsc_queries(queries_csv) if queries_csv else []
    print(f"Loaded {len(pages)} pages, {len(queries)} queries from GSC\n")

    log = []
    run_types = [args.type] if args.type != "all" else ["title", "content", "fie-silo"]

    # ── TITLE / META UPDATES ──
    if "title" in run_types:
        opportunities = find_title_opportunities(pages)
        print(f"── TITLE/META ({len(opportunities)} candidates) ──────────────")
        for page in opportunities[:20]:  # cap at 20 per run
            url = page["url"]
            if args.only and args.only not in url:
                continue
            print(f"  Processing: {url_to_rel(url)}")
            print(f"    Impressions: {page['impressions']}  CTR: {page['ctr']}%  Pos: {page['position']:.1f}")
            try:
                updates = generate_title_update(page)
                print(f"    New title: {updates['title']}")
                print(f"    New meta:  {updates['meta_description'][:80]}...")

                if not args.dry_run:
                    with open(page["local_path"], "r", encoding="utf-8") as f:
                        html = f.read()
                    new_html = patch_title_meta(html, updates["title"], updates["meta_description"])
                    backup_and_write(page["local_path"], new_html, dry_run=False)
                    print(f"    ✓ Written")

                log.append({"url": url, "type": "title", "updates": updates, "dry_run": args.dry_run})
                time.sleep(0.3)
            except Exception as e:
                print(f"    ✗ ERROR: {e}")
        print()

    # ── CONTENT SECTION UPDATES ──
    if "content" in run_types:
        opportunities = find_content_opportunities(pages, queries)
        print(f"── CONTENT SECTIONS ({len(opportunities)} candidates) ──────────")
        for page in opportunities[:15]:
            url = page["url"]
            if args.only and args.only not in url:
                continue
            print(f"  Processing: {url_to_rel(url)}")
            print(f"    Impressions: {page['impressions']}  Pos: {page['position']:.1f}")
            try:
                section_html = generate_content_section(page)

                if not args.dry_run:
                    with open(page["local_path"], "r", encoding="utf-8") as f:
                        html = f.read()
                    new_html = patch_content_section(html, section_html)
                    if new_html:
                        backup_and_write(page["local_path"], new_html, dry_run=False)
                        print(f"    ✓ Written")
                    else:
                        print(f"    ✗ Could not find injection point")
                else:
                    snippet = section_html[:100].replace("\n", " ")
                    print(f"    [DRY RUN] Preview: {snippet}...")

                log.append({"url": url, "type": "content", "dry_run": args.dry_run})
                time.sleep(0.3)
            except Exception as e:
                print(f"    ✗ ERROR: {e}")
        print()

    # ── FIE SILO LINK GAPS ──
    if "fie-silo" in run_types:
        gaps = find_fie_silo_gaps(pages)
        print(f"── FIE SILO GAPS ({len(gaps)} pages missing what-is-fie link) ──")
        for page in gaps:
            url = page["url"]
            if args.only and args.only not in url:
                continue
            district_slug = page.get("district_slug")
            if not district_slug:
                continue

            # Only add FIE link if that district actually has a what-is-fie.html page
            fie_page_path = os.path.join(SITE_ROOT, "districts", district_slug, "what-is-fie.html")
            if not os.path.exists(fie_page_path):
                print(f"  SKIP (no FIE page exists yet): {district_slug}")
                continue

            print(f"  Adding FIE silo link: {url_to_rel(url)}")
            try:
                with open(page["local_path"], "r", encoding="utf-8") as f:
                    html = f.read()
                new_html = patch_fie_silo_link(html, district_slug)

                if new_html != html:
                    if not args.dry_run:
                        backup_and_write(page["local_path"], new_html, dry_run=False)
                        print(f"    ✓ Written")
                    else:
                        print(f"    [DRY RUN] Would add FIE link")
                else:
                    print(f"    ⚠ Pattern not matched — check silo nav format")

                log.append({"url": url, "type": "fie-silo", "district": district_slug, "dry_run": args.dry_run})
            except Exception as e:
                print(f"    ✗ ERROR: {e}")
        print()

    # ── SAVE LOG ──
    if log:
        existing = []
        if os.path.exists(RESULTS_LOG):
            with open(RESULTS_LOG, "r") as f:
                existing = json.load(f)
        existing.extend(log)
        with open(RESULTS_LOG, "w") as f:
            json.dump(existing, f, indent=2)

    print(f"── DONE ────────────────────────────────────")
    print(f"  Processed: {len(log)} pages")
    if not args.dry_run and log:
        print(f"  Backups:   {BACKUP_DIR}")
        print(f"  Log:       {RESULTS_LOG}")
        print(f"\nNext: git add . && git commit -m 'gsc-driven page updates' && git push")


if __name__ == "__main__":
    main()