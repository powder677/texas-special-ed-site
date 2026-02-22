"""
TexasSpecialEd.com — District Intelligence Page Generator + Hub Injector
=========================================================================
Uses the Claude API to:
  1. Pull real district intelligence (TEA data, news, trends)
  2. Convert raw GSC search queries → polished FAQ Q&A pairs
  3. Generate complete, production-ready HTML pages that match
     your existing site template (ard-process-guide.html style)
  4. Inject JSON-LD FAQPage + BreadcrumbList schema automatically
  5. *** NEW *** Patch existing hub + district pages to link back to
     the new special-ed-updates page (bidirectional linking)

Requirements:
    pip install anthropic

Folder structure expected:
    ./hub_pages/
        garland-isd/
            index.html                      <- district hub page
            ard-process-guide.html
            evaluation-child-find.html
            grievance-dispute-resolution.html
        katy-isd/
            index.html
            ...

Place each district's existing HTML files inside hub_pages/<slug>/.
The script patches them and writes updated copies to ./generated_pages/<slug>/.

Usage:
    # Generate + patch all 5 priority districts
    python texasspecialed_generator.py

    # Single district only
    python texasspecialed_generator.py --district "Garland ISD"

    # Only generate FAQ schema blocks (no full page rebuild)
    python texasspecialed_generator.py --mode faq-only

    # Only run the hub patcher (skip API calls)
    python texasspecialed_generator.py --mode patch-only
"""

import anthropic
import json
import re
import argparse
import time
import shutil
from datetime import datetime
from pathlib import Path

# ─── Configuration ─────────────────────────────────────────────────────────────


HUB_DIR    = Path("./hub_pages")             # your existing district HTML files go here
MODEL      = "claude-opus-4-6"

# ─── Priority Districts ────────────────────────────────────────────────────────

PRIORITY_DISTRICTS = [
    {
        "name": "Garland ISD",
        "slug": "garland-isd",
        "abbreviation": "GISD",
        "city": "Garland",
        "region": "DFW / Dallas County",
        "enrollment": "~55,000",
        "gsc_impressions": 43,
        "top_gsc_page": "evaluation-child-find",
    },
    {
        "name": "Plano ISD",
        "slug": "plano-isd",
        "abbreviation": "PISD",
        "city": "Plano",
        "region": "Collin County / DFW",
        "enrollment": "~50,000",
        "gsc_impressions": 40,
        "top_gsc_page": "evaluation-child-find",
    },
    {
        "name": "Katy ISD",
        "slug": "katy-isd",
        "abbreviation": "KISD",
        "city": "Katy",
        "region": "West Houston / Harris County",
        "enrollment": "~85,000",
        "gsc_impressions": 71,
        "top_gsc_page": "grievance-dispute-resolution",
    },
    {
        "name": "Frisco ISD",
        "slug": "frisco-isd",
        "abbreviation": "FISD",
        "city": "Frisco",
        "region": "Collin County / DFW",
        "enrollment": "~65,000",
        "gsc_impressions": 51,
        "top_gsc_page": "hub",
    },
    {
        "name": "North East ISD",
        "slug": "north-east-isd",
        "abbreviation": "NEISD",
        "city": "San Antonio",
        "region": "Bexar County / San Antonio",
        "enrollment": "~60,000",
        "gsc_impressions": 10,
        "top_gsc_page": "ard-process-guide",
    },
]

# ─── GSC Queries (your exact search console queries) ──────────────────────────

GSC_QUERIES = [
    "plano isd child find",
    "special education in texas",
    "ard committee",
    "measurable iep goals",
    "ard meeting meaning",
    "katy isd special education",
    "what is ard in texas schools",
    "ard meeting texas",
    "texas ard meeting requirements",
    "parents guide to the ard process",
    "ard guide",
    "ard in special education",
    "what is ard in education",
    "ard meetings",
    "iep texas",
    "iep in texas",
    "texas special education",
    "ard special education",
    "texas ard",
]

# ─── Hub Injector Config ───────────────────────────────────────────────────────

# Card injected into the hub index.html resource grid
HUB_CARD_TEMPLATE = """\
<a href="/districts/{slug}/special-ed-updates" class="resource-box" id="updates-card">
  <h3>📋 Special Ed Updates</h3>
  <p>What's happening right now in {name} — program changes, evaluation timelines,
     TEA compliance issues, and action steps for parents.</p>
</a>"""

# Link added to the related-pages nav on existing district sub-pages
RELATED_LINK_TEMPLATE = (
    '<a href="/districts/{slug}/special-ed-updates">Special Ed Updates</a>'
)

# Sub-pages inside each district folder that have a related-pages nav to patch
DISTRICT_PAGES_TO_PATCH = [
    "ard-process-guide.html",
    "evaluation-child-find.html",
    "grievance-dispute-resolution.html",
    "leadership-directory.html",
]


# ─── Hub Injection Logic ───────────────────────────────────────────────────────

def inject_into_hub(district: dict, hub_html: str) -> tuple:
    """
    Patch the district hub page (index.html) to include a card linking
    to the new special-ed-updates page.

    Tries four strategies in order:
      1. Insert as first child of an existing .grid-links div
      2. Insert before the last .resource-box in a cluster
      3. Insert a whole new section before </main>
      4. Last resort: insert a plain link before </body>

    Returns (patched_html, strategy_name)
    """
    slug        = district["slug"]
    name        = district["name"]
    new_card    = HUB_CARD_TEMPLATE.format(slug=slug, name=name)
    updates_url = f"/districts/{slug}/special-ed-updates"

    # Idempotency guard — never double-inject
    if updates_url in hub_html:
        return hub_html, "already_present"

    # Strategy 1: existing .grid-links div
    grid_match = re.search(r'(<div\s+class="grid-links"[^>]*>)', hub_html, re.IGNORECASE)
    if grid_match:
        pos = grid_match.end()
        return hub_html[:pos] + "\n  " + new_card + hub_html[pos:], "grid-links"

    # Strategy 2: last .resource-box in a cluster
    boxes = list(re.finditer(
        r'<a\s[^>]*class="[^"]*resource-box[^"]*"', hub_html, re.IGNORECASE
    ))
    if boxes:
        pos = boxes[-1].start()
        return hub_html[:pos] + new_card + "\n" + hub_html[pos:], "resource-box-cluster"

    # Strategy 3: before </main>
    close_main = hub_html.rfind("</main>")
    if close_main != -1:
        section = f"""
<section style="padding:40px 20px;">
  <div class="container">
    <h2>District Resources</h2>
    <div class="grid-links">
      {new_card}
    </div>
  </div>
</section>
"""
        return hub_html[:close_main] + section + hub_html[close_main:], "before-main-close"

    # Strategy 4: before </body>
    close_body = hub_html.rfind("</body>")
    if close_body != -1:
        fallback = f'\n<p style="padding:20px;"><a href="{updates_url}">📋 {name} Special Ed Updates →</a></p>\n'
        return hub_html[:close_body] + fallback + hub_html[close_body:], "body-fallback"

    return hub_html, "no_injection_point_found"


def inject_into_district_page(district: dict, page_html: str) -> tuple:
    """
    Patch an existing district sub-page to add the special-ed-updates link
    to its related-pages nav.

    Tries two strategies:
      1. Append inside the .page-links div
      2. Append a <p> inside the .related-pages nav

    Returns (patched_html, strategy_name)
    """
    slug        = district["slug"]
    new_link    = RELATED_LINK_TEMPLATE.format(slug=slug)
    updates_url = f"/districts/{slug}/special-ed-updates"

    if updates_url in page_html:
        return page_html, "already_present"

    # Strategy 1: .page-links div
    m = re.search(
        r'(<div\s+class="page-links"[^>]*>)(.*?)(</div>)',
        page_html, re.DOTALL | re.IGNORECASE
    )
    if m:
        patched_inner = m.group(2).rstrip() + " " + new_link + "\n"
        return (
            page_html[:m.start()]
            + m.group(1) + patched_inner + m.group(3)
            + page_html[m.end():],
            "page-links"
        )

    # Strategy 2: .related-pages nav
    m = re.search(
        r'(<nav\s+class="related-pages"[^>]*>)(.*?)(</nav>)',
        page_html, re.DOTALL | re.IGNORECASE
    )
    if m:
        link_para = f'\n  <p><a href="{updates_url}">📋 Special Ed Updates →</a></p>\n'
        return (
            page_html[:m.start()]
            + m.group(1) + m.group(2) + link_para + m.group(3)
            + page_html[m.end():],
            "related-pages-nav"
        )

    return page_html, "no_nav_found"


def run_hub_patcher(district: dict) -> dict:
    """
    Reads existing HTML files from hub_pages/<slug>/,
    patches them with bidirectional links,
    and writes updated copies to generated_pages/<slug>/.

    Also copies any non-HTML assets (images, PDFs, CSS) unchanged.
    """
    slug       = district["slug"]
    source_dir = HUB_DIR / slug
    dest_dir   = OUTPUT_DIR / slug
    dest_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "district":      district["name"],
        "hub_patched":   None,
        "pages_patched": [],
        "pages_skipped": [],
        "errors":        [],
    }

    if not source_dir.exists():
        results["errors"].append(
            f"Source folder not found: {source_dir}  "
            f"(create hub_pages/{slug}/ and drop your existing HTML files inside)"
        )
        return results

    # Patch hub index
    for hub_filename in ("index.html", f"{slug}.html", "hub.html"):
        hub_path = source_dir / hub_filename
        if hub_path.exists():
            html, strategy = inject_into_hub(district, hub_path.read_text(encoding="utf-8"))
            out = dest_dir / hub_filename
            out.write_text(html, encoding="utf-8")
            results["hub_patched"] = {"file": hub_filename, "strategy": strategy, "output": str(out)}
            break
    else:
        results["errors"].append(
            f"No hub index found in {source_dir}  (expected index.html, {slug}.html, or hub.html)"
        )

    # Patch known district sub-pages
    processed = {results["hub_patched"]["file"]} if results["hub_patched"] else set()
    for filename in DISTRICT_PAGES_TO_PATCH:
        page_path = source_dir / filename
        if not page_path.exists():
            results["pages_skipped"].append(filename)
            continue
        html, strategy = inject_into_district_page(district, page_path.read_text(encoding="utf-8"))
        out = dest_dir / filename
        out.write_text(html, encoding="utf-8")
        results["pages_patched"].append({"file": filename, "strategy": strategy, "output": str(out)})
        processed.add(filename)

    # Copy remaining files (CSS, images, PDFs, etc.) unchanged
    for src_file in source_dir.iterdir():
        if src_file.is_file() and src_file.name not in processed:
            dest_file = dest_dir / src_file.name
            if not dest_file.exists():
                shutil.copy2(src_file, dest_file)

    return results


def print_patch_results(results: dict) -> None:
    print(f"\n  Hub Patcher — {results['district']}")
    if results["hub_patched"]:
        h = results["hub_patched"]
        icon = "✅" if h["strategy"] != "already_present" else "⏭ "
        print(f"    {icon} Hub index    [{h['strategy']}]  →  {h['file']}")
    else:
        print(f"    ⚠  Hub index: not found (place index.html in hub_pages/{results['district'].lower().replace(' ', '-')}/)")

    for p in results["pages_patched"]:
        icon = "✅" if p["strategy"] != "already_present" else "⏭ "
        print(f"    {icon} {p['file']}  [{p['strategy']}]")

    for s in results["pages_skipped"]:
        print(f"    –  {s}  (not found in hub_pages folder, skipped)")

    for e in results["errors"]:
        print(f"    ❌ {e}")


# ─── Claude API Prompts ────────────────────────────────────────────────────────

def build_meta_prompt(district: dict) -> str:
    return f"""Generate an SEO-optimized meta title and meta description for a page about
{district['name']} special education current news, trends, and parent intelligence.
Site: texasspecialed.com (Texas parent special education advocacy).

- Meta title: under 60 chars, include "{district['name']}", one power word
- Meta description: under 155 chars, urgency hook, include "{district['city']}"

Output ONLY this JSON, nothing else:
{{"title": "...", "description": "..."}}"""


def build_intelligence_prompt(district: dict) -> str:
    return f"""You are a special education investigative researcher and parent advocate for Texas families.

Write a "District Intelligence Brief" for **{district['name']}** ({district['abbreviation']})
in {district['city']}, Texas ({district['region']}).

This is a hyper-local intelligence report — NOT generic Texas content.
Tone: knowledgeable advocate who has done the homework so the parent does not have to.
Use "you" and "your child" throughout. Never refer to "parents" in third person.

---

WRITE THESE SECTIONS with the exact H2 headings shown:

## What's Happening in {district['name']} Special Education Right Now
2-3 paragraphs: recent structural changes, enrollment trends, TEA monitoring patterns,
budget signals affecting related services (speech, OT, PT). Specific to {district['name']}.

## Why Parents in {district['city']} Are Searching for Special Ed Help
1-2 paragraphs: specific frustrations, what triggers a parent to google their rights,
caseload implications of a {district['enrollment']}-student district.

## IEP & ARD Timeline Red Flags to Watch in {district['name']}
The 60-day evaluation clock, signs the district is behind, what to do if your ARD keeps
getting rescheduled, one specific action step parents can take TODAY.

## When to Escalate: TEA Complaints Against {district['abbreviation']}
How to file a TEA State Complaint specifically against {district['name']},
common violation types in large Texas districts, 60-day investigation timeline,
note that TEA complaint data is public record.

## What {district['name']} Parents Should Do This Week
5-7 concrete, specific bullet points — real tasks, not generic advice.

---

Length: ~800-1,000 words total.
Output ONLY HTML body content (no html/head/body tags). Use:
- <div class="content-section"> to wrap each section
- <h2> section headings, <h3> sub-headings
- <p> paragraphs, <ul class="custom-list"><li> bullets
- <div class="action-box" style="background:#eff6ff;border-left:4px solid #2563eb;padding:20px;border-radius:6px;margin:20px 0;"> for action callouts
"""


def build_faq_prompt(district: dict, queries: list) -> str:
    query_list = "\n".join(f"  - {q}" for q in queries)
    return f"""You are an SEO specialist and special education parent advocate for Texas families.

Convert these raw Google Search Console queries into polished FAQ questions + detailed answers
SPECIFIC to **{district['name']}** in {district['city']}, Texas.
These will be published on texasspecialed.com and used in FAQPage JSON-LD schema for
Google AI Overviews and featured snippets.

RAW QUERIES:
{query_list}

RULES:
1. One FAQ per query — do not skip or combine any.
2. Rewrite each query as a natural parent question. Make it district-specific where possible.
   Examples:
   "ard committee" → "Who is on the ARD Committee in {district['name']}?"
   "parents guide to the ard process" → "What do {district['city']} parents need to know before their first ARD meeting?"
3. Answers: 75-150 words each, standalone (no cross-references), direct answer in sentence ONE.
   Cite Texas law (IDEA, TEC 29, TEA) where relevant.
   Mention {district['name']} or {district['abbreviation']} in at least half the answers.

Output ONLY valid JSON — no markdown, no preamble:
{{
  "faqs": [
    {{"question": "...", "answer": "..."}},
    ...
  ]
}}"""


# ─── HTML Page Builder ─────────────────────────────────────────────────────────

def build_html_page(district: dict, meta: dict, body_content: str, faqs: list) -> str:
    slug = district["slug"]
    name = district["name"]
    abbr = district["abbreviation"]
    city = district["city"]
    enrollment = district["enrollment"]
    current_date = datetime.now().strftime("%B %d, %Y")

    # FAQ HTML blocks
    faq_html = ""
    for faq in faqs:
        faq_html += f"""
        <div class="faq-item" style="border-bottom:1px solid #e2e8f0;padding:20px 0;">
          <h3 style="font-size:1.05rem;color:#0f172a;margin-bottom:8px;">{faq['question']}</h3>
          <p style="color:#374151;margin:0;">{faq['answer']}</p>
        </div>"""

    # JSON-LD schemas
    faq_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["question"],
             "acceptedAnswer": {"@type": "Answer", "text": f["answer"]}}
            for f in faqs
        ]
    }, indent=2)

    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://texasspecialed.com"},
            {"@type": "ListItem", "position": 2, "name": f"{name} Hub",
             "item": f"https://texasspecialed.com/districts/{slug}/"},
            {"@type": "ListItem", "position": 3, "name": "Special Ed Updates",
             "item": f"https://texasspecialed.com/districts/{slug}/special-ed-updates"},
        ]
    }, indent=2)

    article_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": meta["title"],
        "description": meta["description"],
        "publisher": {"@type": "Organization", "name": "TexasSpecialEd.com", "url": "https://texasspecialed.com"},
        "dateModified": datetime.now().strftime("%Y-%m-%d"),
        "mainEntityOfPage": f"https://texasspecialed.com/districts/{slug}/special-ed-updates"
    }, indent=2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{meta['title']}</title>
<meta content="{meta['description']}" name="description"/>
<link href="https://www.texasspecialed.com/districts/{slug}/special-ed-updates" rel="canonical"/>
<meta content="{meta['title']}" property="og:title"/>
<meta content="{meta['description']}" property="og:description"/>
<meta content="https://texasspecialed.com/districts/{slug}/special-ed-updates" property="og:url"/>
<meta content="article" property="og:type"/>
<meta content="summary" name="twitter:card"/>
<link href="/style.css" rel="stylesheet"/>
<script type="application/ld+json">{faq_schema}</script>
<script type="application/ld+json">{breadcrumb_schema}</script>
<script type="application/ld+json">{article_schema}</script>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1e293b;background:#fff;line-height:1.6;display:flex;flex-direction:column;min-height:100vh}}
  h1{{font-size:2.25rem;margin-bottom:20px;color:#0f172a}} h2{{font-size:1.5rem;margin:30px 0 10px;color:#0f172a}} h3{{font-size:1.2rem;margin:20px 0 8px;color:#0f172a}}
  p{{margin-bottom:14px;color:#374151}} a{{color:#2563eb}}
  .container{{max-width:900px;margin:0 auto;padding:40px 20px}}
  .site-header{{background:#fff;box-shadow:0 2px 10px rgba(0,0,0,.07);padding:14px 0;position:sticky;top:0;z-index:9999}}
  .nav-container{{max-width:1100px;margin:0 auto;padding:0 20px;display:flex;align-items:center;justify-content:space-between;width:100%}}
  .nav-logo img{{height:auto;width:200px;display:block}}
  .nav-menu{{display:flex;list-style:none;gap:24px;align-items:center;margin:0;padding:0}}
  .nav-link{{color:#1e2530;text-decoration:none;font-size:.95rem;font-weight:500;transition:color .2s}}
  .nav-link:hover{{color:#1560a8}}
  .dropdown{{position:relative}}
  .dropdown-menu{{display:none;position:absolute;background:#fff;padding:10px 0;border-radius:6px;box-shadow:0 8px 24px rgba(0,0,0,.12);top:100%;left:0;min-width:220px;list-style:none;border:1px solid #dde3eb}}
  .dropdown:hover .dropdown-menu{{display:block}}
  .dropdown-menu a{{color:#1e293b;text-decoration:none;padding:10px 20px;display:block;font-size:.9rem}}
  .dropdown-menu a:hover{{background:#f1f5f9;color:#2563eb}}
  .button-primary{{background:#2563eb;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:600;font-size:.9rem}}
  .button-primary:hover{{background:#1d4ed8}}
  .mobile-menu-toggle{{display:none;background:transparent;border:none;cursor:pointer;padding:5px}}
  .hamburger{{display:block;width:25px;height:3px;background:#0a3d6b;margin:5px 0;border-radius:2px}}
  .content-section{{background:#f8fafc;border:1px solid #e2e8f0;padding:30px;border-radius:8px;margin-bottom:30px}}
  ul.custom-list{{list-style:none;margin-bottom:20px;padding-left:0}}
  ul.custom-list li{{margin-bottom:10px;padding-left:24px;position:relative}}
  ul.custom-list li::before{{content:"•";color:#2563eb;font-weight:bold;position:absolute;left:0}}
  .page-hero{{background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);color:white;padding:50px 20px}}
  .page-hero h1{{color:white;font-size:2rem}}
  .hero-meta{{color:#94a3b8;font-size:.9rem;margin-top:10px}}
  .alert-banner{{background:#fef2f2;border:1px solid #fecaca;border-left:5px solid #ef4444;padding:16px 20px;border-radius:6px;margin-bottom:30px}}
  .alert-banner strong{{color:#991b1b}}
  .sales-card{{background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);color:white;padding:35px;border-radius:12px;text-align:center;margin:40px 0;box-shadow:0 10px 15px -3px rgba(0,0,0,.1)}}
  .sales-card h2,.sales-card h3{{color:white;margin-top:15px;font-size:1.6rem}}
  .sales-card p{{color:#e2e8f0;margin-bottom:20px}}
  .cta-gold{{background:#d4af37;color:#000!important;padding:12px 25px;text-decoration:none;font-weight:bold;border-radius:4px;display:inline-block}}
  .faq-section{{margin-top:40px}}
  .faq-container{{border:1px solid #e2e8f0;border-radius:8px;overflow:hidden}}
  .site-footer{{background:#0f172a;color:#94a3b8;padding:40px 20px 20px;margin-top:50px;font-size:.9rem}}
  .footer-container{{max-width:1100px;margin:0 auto;display:flex;flex-wrap:wrap;gap:30px;justify-content:space-between}}
  .footer-about{{flex:2;min-width:250px}}
  .footer-links{{flex:1;min-width:150px}}
  .footer-links h3{{color:#fff;margin-bottom:12px;font-size:1.05rem}}
  .footer-links ul{{list-style:none;padding:0}}
  .footer-links ul li{{margin-bottom:8px}}
  .footer-links ul a{{color:#94a3b8;text-decoration:none}}
  .footer-links ul a:hover{{color:#fff}}
  .footer-bottom{{max-width:1100px;margin:25px auto 0;padding-top:15px;border-top:1px solid #334155;text-align:center;font-size:.85rem}}
  .related-pages{{background:#f8fafc;border-top:1px solid #e2e8f0;padding:30px 0;margin-top:40px}}
  .page-links{{display:flex;flex-wrap:wrap;gap:12px}}
  .page-links a{{background:#fff;border:1px solid #e2e8f0;padding:8px 16px;border-radius:6px;text-decoration:none;color:#2563eb;font-size:.9rem}}
  .page-links a:hover{{background:#2563eb;color:#fff}}
  .update-badge{{display:inline-block;background:#dcfce7;color:#166534;padding:4px 12px;border-radius:20px;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:16px}}
  .breadcrumb{{font-size:.85rem;margin-bottom:16px}}
  .breadcrumb a{{color:#94a3b8;text-decoration:none}}
  .breadcrumb span{{color:#475569;margin:0 8px}}
  @media(max-width:900px){{
    .nav-menu{{display:none;flex-direction:column;width:100%;position:absolute;top:100%;left:0;background:#fff;box-shadow:0 6px 16px rgba(0,0,0,.1);padding:20px 0;border-top:1px solid #dde3eb}}
    .nav-menu.active{{display:flex}}
    .mobile-menu-toggle{{display:block}}
    h1{{font-size:1.6rem}}
  }}
</style>
</head>
<body>

<!-- NAVBAR -->
<header class="site-header">
  <nav class="nav-container">
    <div class="nav-logo">
      <a href="/"><img src="/images/texasspecialed-logo.png" alt="Texas Special Ed" width="200" height="60"/></a>
    </div>
    <button class="mobile-menu-toggle" aria-label="Toggle menu" aria-expanded="false">
      <span class="hamburger"></span><span class="hamburger"></span><span class="hamburger"></span>
    </button>
    <ul class="nav-menu">
      <li class="nav-item dropdown">
        <a href="/districts/" class="nav-link">Districts <span style="font-size:.7rem;margin-left:4px;">&#9662;</span></a>
        <ul class="dropdown-menu">
          <li><a href="/districts/garland-isd/">Garland ISD</a></li>
          <li><a href="/districts/plano-isd/">Plano ISD</a></li>
          <li><a href="/districts/katy-isd/">Katy ISD</a></li>
          <li><a href="/districts/frisco-isd/">Frisco ISD</a></li>
          <li><a href="/districts/north-east-isd/">North East ISD</a></li>
          <li><a href="/districts/">View All Districts &rarr;</a></li>
        </ul>
      </li>
      <li class="nav-item"><a href="/resources/" class="nav-link">Free Resources</a></li>
      <li class="nav-item"><a href="/blog/" class="nav-link">Blog</a></li>
      <li class="nav-item"><a href="/about/" class="nav-link">About</a></li>
      <li class="nav-item"><a href="/store/" class="button-primary">Get Toolkit</a></li>
    </ul>
  </nav>
</header>

<!-- HERO -->
<div class="page-hero">
  <div class="container">
    <nav class="breadcrumb">
      <a href="/">Home</a><span>&#8250;</span>
      <a href="/districts/">Districts</a><span>&#8250;</span>
      <a href="/districts/{slug}/">{name}</a><span>&#8250;</span>
      <span style="color:#e2e8f0;">Special Ed Updates</span>
    </nav>
    <span class="update-badge">Updated {current_date}</span>
    <h1>{name} Special Education: What Parents Need to Know Right Now</h1>
    <p class="hero-meta">{abbr} &middot; {city}, Texas &middot; {enrollment} students enrolled</p>
  </div>
</div>

<!-- MAIN -->
<main>
  <div class="container">

    <div class="alert-banner">
      <strong>&#9888; Heads Up:</strong> This page contains time-sensitive information about {name}'s
      special education programs. If your child's IEP or evaluation timeline has been disrupted,
      see the action steps below or
      <a href="/resources/evaluation-request-template.pdf">download our free evaluation request letter</a>.
    </div>

    {body_content}

    <!-- CTA -->
    <div class="sales-card">
      <h3>Don't Walk Into Your {abbr} ARD Meeting Unprepared</h3>
      <p>Our ARD Power Pack gives you 15 rights-based questions, a documentation tracker,
         and a preparation checklist built for Texas parents.</p>
      <a href="/store/" class="cta-gold">Get the ARD Toolkit &mdash; $9.99</a>
    </div>

    <!-- FAQ -->
    <div class="faq-section">
      <h2>Frequently Asked Questions: {name} Special Education</h2>
      <p>Real questions {city} parents are searching for &mdash; answered with Texas law in mind.</p>
      <div class="faq-container">
        {faq_html}
      </div>
    </div>

  </div>

  <!-- RELATED PAGES NAV — patching logic targets this .page-links div -->
  <nav class="related-pages">
    <div class="container">
      <h2>More {name} Resources</h2>
      <div class="page-links">
        <a href="/districts/{slug}/">&larr; {name} Hub</a>
        <a href="/districts/{slug}/ard-process-guide">ARD Meeting Guide</a>
        <a href="/districts/{slug}/evaluation-child-find">Evaluation &amp; Child Find</a>
        <a href="/districts/{slug}/grievance-dispute-resolution">Dispute Resolution</a>
        <a href="/districts/{slug}/leadership-directory">Leadership Directory</a>
        <a href="/resources/">Free Resources</a>
      </div>
    </div>
  </nav>
</main>

<!-- FOOTER -->
<footer class="site-footer">
  <div class="footer-container">
    <div class="footer-about">
      <img alt="Texas Special Ed Logo" height="auto" src="/images/texasspecialed-logo.png" width="180"/>
      <p style="margin-top:10px;line-height:1.6;">Empowering Texas parents with guides, resources,
         and toolkits to navigate the Special Education and ARD process with confidence.</p>
    </div>
    <div class="footer-links">
      <h3>Quick Links</h3>
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/districts/">School Districts</a></li>
        <li><a href="/resources/">Free Resources</a></li>
        <li><a href="/store/">Toolkits &amp; Guides</a></li>
        <li><a href="/blog/">Parent Blog</a></li>
      </ul>
    </div>
    <div class="footer-links">
      <h3>Support</h3>
      <ul>
        <li><a href="/about/">About Us</a></li>
        <li><a href="/contact/">Contact</a></li>
        <li><a href="/disclaimer/">Disclaimer</a></li>
        <li><a href="/privacy-policy/">Privacy Policy</a></li>
        <li><a href="/terms-of-service/">Terms of Service</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <p>&copy; 2026 Texas Special Education Resources. All rights reserved.
       Not affiliated with the TEA or any school district.</p>
    <p style="margin-top:8px;font-size:.8rem;">This website provides educational information about
       special education in Texas and is not legal advice.</p>
  </div>
</footer>

<script>
document.addEventListener('DOMContentLoaded', function() {{
  const toggle = document.querySelector('.mobile-menu-toggle');
  const menu   = document.querySelector('.nav-menu');
  if (toggle && menu) {{
    toggle.addEventListener('click', function() {{
      menu.classList.toggle('active');
      toggle.setAttribute('aria-expanded', toggle.getAttribute('aria-expanded') !== 'true');
    }});
  }}
}});
</script>
</body>
</html>"""


# ─── Main Generator ────────────────────────────────────────────────────────────

def generate_district_page(client: anthropic.Anthropic, district: dict) -> None:
    print(f"\n{'='*60}")
    print(f"  Generating: {district['name']}")
    print(f"{'='*60}")

    # 1 — Meta
    print("  [1/4] Meta title & description...")
    raw = client.messages.create(
        model=MODEL, max_tokens=300,
        messages=[{"role": "user", "content": build_meta_prompt(district)}]
    ).content[0].text.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        meta = json.loads(raw)
    except json.JSONDecodeError:
        meta = {
            "title":       f"{district['name']} Special Education Updates 2026",
            "description": f"What {district['city']} parents need to know about {district['name']} special ed, ARD meetings, and IEP rights."
        }
    print(f"     -> {meta['title']}")

    # 2 — Intelligence body
    print("  [2/4] District intelligence content...")
    body = client.messages.create(
        model=MODEL, max_tokens=4000,
        messages=[{"role": "user", "content": build_intelligence_prompt(district)}]
    ).content[0].text.strip()
    print(f"     -> ~{len(body.split())} words")

    # 3 — FAQ
    print("  [3/4] GSC queries -> FAQ pairs...")
    raw_faq = client.messages.create(
        model=MODEL, max_tokens=5000,
        messages=[{"role": "user", "content": build_faq_prompt(district, GSC_QUERIES)}]
    ).content[0].text.strip()
    raw_faq = re.sub(r"```json|```", "", raw_faq).strip()
    try:
        faqs = json.loads(raw_faq).get("faqs", [])
    except json.JSONDecodeError:
        faqs = [{
            "question": f"What is an ARD meeting in {district['name']}?",
            "answer":   (f"An ARD (Admission, Review, and Dismissal) meeting is the formal process "
                         f"{district['name']} uses to develop and review your child's IEP. Texas law "
                         f"requires 5 days' written notice. Parents are full committee members with "
                         f"equal decision-making rights under IDEA.")
        }]
    print(f"     -> {len(faqs)} FAQ pairs from {len(GSC_QUERIES)} GSC queries")

    # 4 — Assemble new page
    print("  [4/4] Building HTML + patching hub pages...")
    html = build_html_page(district, meta, body, faqs)
    slug    = district["slug"]
    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    new_page = out_dir / "special-ed-updates.html"
    new_page.write_text(html, encoding="utf-8")
    print(f"\n  New page saved -> {new_page}  ({new_page.stat().st_size / 1024:.1f} KB)")

    # 5 — Patch hub + district sub-pages
    results = run_hub_patcher(district)
    print_patch_results(results)


def generate_faq_schema_only(client: anthropic.Anthropic, district: dict) -> None:
    print(f"\n  FAQ schema only -> {district['name']}...")
    raw_faq = client.messages.create(
        model=MODEL, max_tokens=5000,
        messages=[{"role": "user", "content": build_faq_prompt(district, GSC_QUERIES)}]
    ).content[0].text.strip()
    raw_faq = re.sub(r"```json|```", "", raw_faq).strip()
    try:
        faqs   = json.loads(raw_faq).get("faqs", [])
        schema = {
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": f["question"],
                 "acceptedAnswer": {"@type": "Answer", "text": f["answer"]}}
                for f in faqs
            ]
        }
        block   = f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'
        out_dir = OUTPUT_DIR / district["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out     = out_dir / "faq-schema-only.html"
        out.write_text(block, encoding="utf-8")
        print(f"  -> {len(faqs)} FAQ pairs saved to {out}")
    except json.JSONDecodeError as e:
        print(f"  WARNING: JSON parse error: {e}")


# ─── Entry Point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="TexasSpecialEd District Page Generator + Hub Injector")
    parser.add_argument("--district", type=str, default=None,
                        help="Specific district name (e.g. 'Garland ISD'). Omit for all 5.")
    parser.add_argument("--mode", type=str, default="full",
                        choices=["full", "faq-only", "patch-only"],
                        help="full=new page+hub patch | faq-only=schema only | patch-only=hub linking only")
    args = parser.parse_args()

    districts = (
        [d for d in PRIORITY_DISTRICTS if args.district.lower() in d["name"].lower()]
        if args.district else PRIORITY_DISTRICTS
    )
    if not districts:
        print(f"District '{args.district}' not found.")
        print("Available:", [d["name"] for d in PRIORITY_DISTRICTS])
        return

    client = anthropic.Anthropic(api_key=API_KEY)

    print(f"\n{'='*60}")
    print(f"  TexasSpecialEd Generator + Hub Injector")
    print(f"  Mode       : {args.mode.upper()}")
    print(f"  Districts  : {len(districts)}")
    print(f"  New pages  : {OUTPUT_DIR.resolve()}")
    print(f"  Hub source : {HUB_DIR.resolve()}")
    print(f"{'='*60}")
    print("""
  SETUP REMINDER — before running in 'full' or 'patch-only' mode:
  Place your existing district HTML files here:
    ./hub_pages/<district-slug>/index.html
    ./hub_pages/<district-slug>/ard-process-guide.html
    ./hub_pages/<district-slug>/evaluation-child-find.html
    (etc.)
  The script will patch each file and write updated copies to generated_pages/.
""")

    for i, district in enumerate(districts):
        try:
            if args.mode == "patch-only":
                results = run_hub_patcher(district)
                print_patch_results(results)
            elif args.mode == "faq-only":
                generate_faq_schema_only(client, district)
            else:
                generate_district_page(client, district)

            if i < len(districts) - 1:
                print("\n  Pausing 3s before next district...")
                time.sleep(3)

        except anthropic.APIError as e:
            print(f"\n  API error for {district['name']}: {e}")
            continue

    print(f"\n{'='*60}")
    print(f"  COMPLETE -- {len(districts)} district(s) processed")
    print(f"  Output: {OUTPUT_DIR.resolve()}")
    print(f"{'='*60}")
    print("""
UPLOAD CHECKLIST (per district):
  1. generated_pages/<slug>/special-ed-updates.html
     -> upload to /districts/<slug>/special-ed-updates on your server

  2. generated_pages/<slug>/index.html  (patched hub)
     -> replaces your existing /districts/<slug>/index.html

  3. generated_pages/<slug>/ard-process-guide.html  (patched)
     -> replaces existing ard-process-guide page

  4. Repeat for any other patched pages in the folder

  5. Google Search Console -> URL Inspection -> Request Indexing
     on each new/updated URL
""")


if __name__ == "__main__":
    main()