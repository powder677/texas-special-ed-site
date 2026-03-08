"""
update_fie_pages.py

For every district folder that contains what-is-fie.html:
  1. Rename it to what-is-an-fie-{district-slug}.html
  2. Update title, meta description, canonical URL, h1, schema, and breadcrumb for local SEO
  3. Add/update the silo nav link on the district index page
  4. Add/update the silo nav link on ALL other district sub-pages
  5. Uses Claude API to generate a unique, locally-optimized meta description per district

Usage:
    pip install anthropic beautifulsoup4
    set ANTHROPIC_API_KEY=your_key

    python update_fie_pages.py --dry-run        # preview only
    python update_fie_pages.py                  # run everything
    python update_fie_pages.py --only allen-isd # single district
    python update_fie_pages.py --skip-meta      # skip Claude API calls, use template meta
"""

import os
import re
import json
import shutil
import time
import argparse
from datetime import datetime
from bs4 import BeautifulSoup

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# ── CONFIG ────────────────────────────────────────────────────────────────────

SITE_ROOT    = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"
DISTRICTS_DIR = os.path.join(SITE_ROOT, "districts")
BACKUP_DIR   = os.path.join(SITE_ROOT, "_backups", datetime.now().strftime("%Y%m%d_%H%M%S"))
BASE_URL     = "https://www.texasspecialed.com"

# Sub-page types that have silo navs
SILO_PAGE_TYPES = [
    "index.html",
    "ard-process-guide.html",
    "evaluation-child-find.html",
    "dyslexia-services.html",
    "grievance-dispute-resolution.html",
    "leadership-directory.html",
    "partners.html",
    "special-ed-updates.html",
]

# ── HELPERS ───────────────────────────────────────────────────────────────────

def slug_to_name(slug: str) -> str:
    name = slug.replace("-", " ").title()
    name = re.sub(r'\bIsd\b', 'ISD', name)
    name = re.sub(r'\bCisd\b', 'CISD', name)
    return name

def backup(path: str):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    rel  = os.path.relpath(path, SITE_ROOT)
    dest = os.path.join(BACKUP_DIR, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(path, dest)

def read_html(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_html(path: str, html: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


# ── META DESCRIPTION GENERATION ──────────────────────────────────────────────

def generate_meta(district_slug: str, district_name: str, skip_meta: bool) -> dict:
    """Generate SEO-optimized title and meta description via Claude."""
    if skip_meta or not HAS_ANTHROPIC:
        # Template fallback
        return {
            "title": f"What Is an FIE in {district_name}? Full Individual Evaluation Guide",
            "meta": f"Learn how to request a Full Individual Evaluation (FIE) from {district_name}. Texas parents have the legal right to request an FIE in writing — the district must respond within 15 school days.",
            "h1": f"What Is an FIE in {district_name}?",
        }

    client = anthropic.Anthropic()
    prompt = f"""You are an SEO specialist for texasspecialed.com, a Texas special education parent resource site.

Write LOCAL SEO-optimized title tag, meta description, and H1 for this page:

Page: What Is an FIE (Full Individual Evaluation) in {district_name}?
URL: /districts/{district_slug}/what-is-an-fie-{district_slug}

Rules:
- Title: 55-60 chars, include "{district_name}" and "FIE" and "Texas"
- Meta: 148-155 chars, include district name, mention the 45-day timeline or 15-day response, end with action
- H1: Similar to title but can be slightly longer, natural reading
- Write for a stressed parent searching "[district name] FIE evaluation" or "request special education evaluation {district_name}"
- Do NOT invent facts about the district

Respond ONLY with valid JSON, no markdown:
{{"title": "...", "meta": "...", "h1": "..."}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        text = re.sub(r"```json|```", "", text).strip()
        return json.loads(text)
    except Exception as e:
        print(f"    API error for {district_slug}: {e} — using template")
        return {
            "title": f"What Is an FIE in {district_name}? Full Individual Evaluation Guide",
            "meta": f"Learn how to request a Full Individual Evaluation (FIE) from {district_name}. Texas parents have the legal right to request an FIE in writing — the district must respond within 15 school days.",
            "h1": f"What Is an FIE in {district_name}?",
        }


# ── PAGE CONTENT UPDATES ──────────────────────────────────────────────────────

def update_fie_page(html: str, district_slug: str, district_name: str, seo: dict) -> str:
    """Update title, meta, canonical, h1, schema, breadcrumb in the FIE page."""
    new_filename = f"what-is-an-fie-{district_slug}.html"
    new_url      = f"{BASE_URL}/districts/{district_slug}/what-is-an-fie-{district_slug}"

    # Title
    html = re.sub(r"<title>.*?</title>", f"<title>{seo['title']}</title>", html, flags=re.DOTALL)

    # Meta description (both attribute orderings)
    html = re.sub(
        r'(<meta\s+content=")[^"]*("\s+name="description"[^/]*/?>)',
        f'\\g<1>{seo["meta"]}\\2', html
    )
    html = re.sub(
        r'(<meta\s+name="description"\s+content=")[^"]*("[^/]*/?>)',
        f'\\g<1>{seo["meta"]}\\2', html
    )

    # Canonical
    html = re.sub(
        r'(<link\s+href=")[^"]*("\s+rel="canonical"[^/]*/?>)',
        f'\\g<1>{new_url}\\2', html
    )
    html = re.sub(
        r'(<link\s+rel="canonical"\s+href=")[^"]*("[^/]*/?>)',
        f'\\g<1>{new_url}\\2', html
    )

    # H1 — replace the existing What Is an FIE heading
    html = re.sub(
        r'<h1[^>]*>What Is an FIE in [^<]*\?</h1>',
        f'<h1>{seo["h1"]}</h1>', html
    )
    # Also catch generic h1 patterns on these pages
    html = re.sub(
        r'<h1[^>]*>What Is a FIE in [^<]*\?</h1>',
        f'<h1>{seo["h1"]}</h1>', html
    )

    # Update internal silo nav links — rename what-is-fie refs to new filename
    html = html.replace(
        f"/districts/{district_slug}/what-is-fie.html",
        f"/districts/{district_slug}/{new_filename}"
    )
    html = html.replace(
        f"/districts/{district_slug}/what-is-fie\"",
        f"/districts/{district_slug}/what-is-an-fie-{district_slug}\""
    )

    # Update schema URLs if present
    html = re.sub(
        r'"@id":\s*"[^"]*what-is-fie[^"]*"',
        f'"@id": "{new_url}"', html
    )
    html = re.sub(
        r'"item":\s*"[^"]*what-is-fie[^"]*"',
        f'"item": "{new_url}"', html
    )
    html = re.sub(
        r'"url":\s*"[^"]*what-is-fie[^"]*"',
        f'"url": "{new_url}"', html
    )

    # Update breadcrumb text
    html = re.sub(
        r'"name":\s*"What Is an? FIE\?"',
        f'"name": "What Is an FIE in {district_name}?"', html
    )

    # Update OG tags if present
    html = re.sub(
        r'(<meta\s+property="og:title"\s+content=")[^"]*(")',
        f'\\g<1>{seo["title"]}\\2', html
    )
    html = re.sub(
        r'(<meta\s+property="og:description"\s+content=")[^"]*(")',
        f'\\g<1>{seo["meta"]}\\2', html
    )
    html = re.sub(
        r'(<meta\s+property="og:url"\s+content=")[^"]*(")',
        f'\\g<1>{new_url}\\2', html
    )

    return html


# ── SILO NAV INJECTION ────────────────────────────────────────────────────────

def build_fie_nav_link(district_slug: str) -> str:
    new_filename = f"what-is-an-fie-{district_slug}.html"
    return f'<a href="/districts/{district_slug}/{new_filename}" style="text-decoration: none; color: #2563eb; font-weight: 500;">What Is an FIE?</a>'


def add_fie_to_silo_nav(html: str, district_slug: str) -> tuple[str, bool]:
    """
    Add/update the What Is an FIE? link in the silo nav.
    Returns (updated_html, was_changed).
    """
    new_filename = f"what-is-an-fie-{district_slug}.html"
    fie_link     = build_fie_nav_link(district_slug)

    # If already pointing to the renamed file, nothing to do
    if new_filename in html:
        return html, False

    # If old what-is-fie link exists, replace it with the renamed version
    old_patterns = [
        f'/districts/{district_slug}/what-is-fie.html',
        f'/districts/{district_slug}/what-is-fie"',
    ]
    for old in old_patterns:
        if old in html:
            html = html.replace(old, f'/districts/{district_slug}/{new_filename}')
            return html, True

    # Link doesn't exist at all — inject after ARD Guide link in silo nav
    # Pattern: find the ARD Guide anchor and insert after it
    ard_pattern = re.compile(
        r'(<a[^>]+ard-process-guide[^>]+>[^<]*ARD Guide[^<]*</a>\s*•)',
        re.IGNORECASE
    )
    match = ard_pattern.search(html)
    if match:
        insert = match.group(0) + f'\n    {fie_link} •'
        html = html[:match.start()] + insert + html[match.end():]
        return html, True

    # Fallback: inject before Evaluations (FIE) link
    eval_pattern = re.compile(
        r'(•\s*\n?\s*<a[^>]+evaluation-child-find[^>]+>)',
        re.IGNORECASE
    )
    match = eval_pattern.search(html)
    if match:
        insert = f'• \n    {fie_link} \n    '
        html = html[:match.start()] + insert + html[match.end():]
        return html, True

    # Fallback 2: inject before Dyslexia link
    dys_pattern = re.compile(
        r'(•\s*\n?\s*<a[^>]+dyslexia-services[^>]+>)',
        re.IGNORECASE
    )
    match = dys_pattern.search(html)
    if match:
        insert = f'• \n    {fie_link} \n    '
        html = html[:match.start()] + insert + html[match.end():]
        return html, True

    return html, False


# ── MAIN PROCESSING ───────────────────────────────────────────────────────────

def process_district(district_slug: str, dry_run: bool, skip_meta: bool) -> dict:
    district_dir  = os.path.join(DISTRICTS_DIR, district_slug)
    district_name = slug_to_name(district_slug)
    result        = {
        "district": district_slug,
        "fie_renamed": False,
        "fie_seo_updated": False,
        "silo_nav_updated": [],
        "errors": []
    }

    old_fie_path = os.path.join(district_dir, "what-is-fie.html")
    new_filename = f"what-is-an-fie-{district_slug}.html"
    new_fie_path = os.path.join(district_dir, new_filename)

    # ── Does this district have a what-is-fie page? ──
    has_fie = os.path.exists(old_fie_path) or os.path.exists(new_fie_path)
    if not has_fie:
        return result  # nothing to do

    # ── Generate SEO content ──
    print(f"  Generating SEO for {district_name}...")
    seo = generate_meta(district_slug, district_name, skip_meta)
    if not skip_meta:
        time.sleep(0.3)  # rate limit

    # ── Update FIE page content ──
    source_path = old_fie_path if os.path.exists(old_fie_path) else new_fie_path
    try:
        fie_html = read_html(source_path)
        updated_fie = update_fie_page(fie_html, district_slug, district_name, seo)
        result["fie_seo_updated"] = True

        if not dry_run:
            backup(source_path)
            # Write to new filename
            write_html(new_fie_path, updated_fie)
            # Remove old file if it was named differently
            if source_path != new_fie_path and os.path.exists(source_path):
                os.remove(source_path)
            result["fie_renamed"] = True
        else:
            result["fie_renamed"] = True  # would rename
            print(f"    [DRY RUN] Would rename → {new_filename}")
            print(f"    Title: {seo['title'][:70]}")
            print(f"    Meta:  {seo['meta'][:80]}...")

    except Exception as e:
        result["errors"].append(f"FIE page error: {e}")
        print(f"    ✗ FIE page error: {e}")

    # ── Update silo nav on all sub-pages ──
    for page_file in SILO_PAGE_TYPES:
        page_path = os.path.join(district_dir, page_file)
        if not os.path.exists(page_path):
            continue
        try:
            page_html = read_html(page_path)
            updated_html, changed = add_fie_to_silo_nav(page_html, district_slug)

            if changed:
                if not dry_run:
                    backup(page_path)
                    write_html(page_path, updated_html)
                result["silo_nav_updated"].append(page_file)
                status = "[DRY RUN] Would update" if dry_run else "Updated"
                print(f"    {status} silo nav: {page_file}")
        except Exception as e:
            result["errors"].append(f"Silo nav error ({page_file}): {e}")

    return result


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no file writes")
    parser.add_argument("--only", type=str, help="Process single district slug e.g. allen-isd")
    parser.add_argument("--skip-meta", action="store_true", help="Skip Claude API, use template meta descriptions")
    args = parser.parse_args()

    if not HAS_ANTHROPIC and not args.skip_meta:
        print("WARNING: anthropic package not found. Using template meta descriptions.")
        print("         Install with: pip install anthropic\n")
        args.skip_meta = True

    if not os.path.exists(DISTRICTS_DIR):
        print(f"ERROR: Districts directory not found: {DISTRICTS_DIR}")
        return

    # Get all district slugs
    all_districts = [
        d for d in os.listdir(DISTRICTS_DIR)
        if os.path.isdir(os.path.join(DISTRICTS_DIR, d))
    ]

    if args.only:
        all_districts = [d for d in all_districts if args.only in d]
        if not all_districts:
            print(f"No district found matching: {args.only}")
            return

    # Filter to only districts that have a what-is-fie page
    has_fie = []
    for d in sorted(all_districts):
        dist_dir = os.path.join(DISTRICTS_DIR, d)
        old_path = os.path.join(dist_dir, "what-is-fie.html")
        new_path = os.path.join(dist_dir, f"what-is-an-fie-{d}.html")
        if os.path.exists(old_path) or os.path.exists(new_path):
            has_fie.append(d)

    print(f"Found {len(has_fie)} districts with what-is-fie pages")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'} | Meta: {'Template' if args.skip_meta else 'Claude API'}\n")

    results   = []
    renamed   = 0
    seo_done  = 0
    nav_total = 0
    errors    = 0

    for district_slug in has_fie:
        print(f"── {slug_to_name(district_slug)} ({district_slug})")
        result = process_district(district_slug, args.dry_run, args.skip_meta)
        results.append(result)

        if result["fie_renamed"]:   renamed += 1
        if result["fie_seo_updated"]: seo_done += 1
        nav_total += len(result["silo_nav_updated"])
        if result["errors"]:        errors += 1

    # Summary
    print(f"\n── SUMMARY ───────────────────────────────")
    print(f"  FIE pages renamed/updated: {renamed}")
    print(f"  SEO metadata updated:      {seo_done}")
    print(f"  Silo nav links added:      {nav_total}")
    print(f"  Errors:                    {errors}")

    if not args.dry_run and renamed > 0:
        print(f"  Backups: {BACKUP_DIR}")
        print(f"\nIMPORTANT: Add 301 redirects for renamed pages.")
        print(f"  In vercel.json add:")
        print(f'  {{"source": "/districts/:district/what-is-fie", "destination": "/districts/:district/what-is-an-fie-:district", "permanent": true}}')
        print(f"\nNext: git add districts/ && git commit -m 'rename and optimize what-is-fie pages for local SEO' && git push")

    # Save log
    log_path = os.path.join(SITE_ROOT, "fie_rename_log.json")
    with open(log_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nLog saved: {log_path}")


if __name__ == "__main__":
    main()