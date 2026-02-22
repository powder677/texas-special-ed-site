"""
TexasSpecialEd.com — District Patcher & Special Ed Updates Page Generator
==========================================================================
What this script does for each district:

  1. Adds a "Special Ed Updates" card to the hub index.html resource grid
  2. Adds a "Special Ed Updates" link to the related-pages nav on all sub-pages
     (creates the nav from scratch on pages that don't have one yet)
  3. Generates a fully-styled special-ed-updates.html page that matches the
     real site design — header, footer, CSS, and card styles extracted
     directly from your index.html

Folder layout (create this next to the script):
  hub_pages/
    frisco-isd/
      index.html
      ard-process-guide.html
      evaluation-child-find.html
      grievance-dispute-resolution.html
      leadership-directory.html
    garland-isd/
      index.html
      ...

Output lands in:
  generated_pages/
    frisco-isd/
      index.html                  <- patched (new card added)
      ard-process-guide.html      <- patched (new nav link added)
      ...
      special-ed-updates.html     <- NEW page

Requirements:
  pip install anthropic beautifulsoup4

Usage:
  python patch_districts.py                          # all districts
  python patch_districts.py --district "Frisco ISD" # one district
  python patch_districts.py --mode patch-only        # skip Claude API, patch HTML only
  python patch_districts.py --mode generate-only     # only generate new page, no patching
"""

import re
import json
import argparse
import shutil
import time
from pathlib import Path
from datetime import datetime

import anthropic
from bs4 import BeautifulSoup, NavigableString

# ─── Configuration ─────────────────────────────────────────────────────────────

API_KEY    = "YOUR_ANTHROPIC_API_KEY_HERE"
MODEL      = "claude-opus-4-6"
HUB_DIR    = Path("./districts")
OUTPUT_DIR = Path("./generated_pages")

# ─── District Registry ─────────────────────────────────────────────────────────

DISTRICTS = [
    {
        "name":         "Frisco ISD",
        "slug":         "frisco-isd",
        "abbreviation": "FISD",
        "city":         "Frisco",
        "region":       "Collin County / DFW",
        "enrollment":   "~65,000",
    },
    {
        "name":         "Garland ISD",
        "slug":         "garland-isd",
        "abbreviation": "GISD",
        "city":         "Garland",
        "region":       "DFW / Dallas County",
        "enrollment":   "~55,000",
    },
    {
        "name":         "Plano ISD",
        "slug":         "plano-isd",
        "abbreviation": "PISD",
        "city":         "Plano",
        "region":       "Collin County / DFW",
        "enrollment":   "~50,000",
    },
    {
        "name":         "Katy ISD",
        "slug":         "katy-isd",
        "abbreviation": "KISD",
        "city":         "Katy",
        "region":       "West Houston / Harris County",
        "enrollment":   "~85,000",
    },
    {
        "name":         "North East ISD",
        "slug":         "north-east-isd",
        "abbreviation": "NEISD",
        "city":         "San Antonio",
        "region":       "Bexar County / San Antonio",
        "enrollment":   "~60,000",
    },
]

# Sub-pages to patch with the new nav link (filenames inside each district folder)
PAGES_TO_PATCH = [
    "ard-process-guide.html",
    "evaluation-child-find.html",
    "grievance-dispute-resolution.html",
    "leadership-directory.html",
]

# GSC queries to convert into FAQs
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


# ═══════════════════════════════════════════════════════════════════════════════
# HTML PATCHING
# ═══════════════════════════════════════════════════════════════════════════════

def patch_hub_index(district: dict, html: str) -> tuple:
    """
    Add a Special Ed Updates card to the .grid-4 resource card grid in index.html.
    Matches the exact card style of the existing site.
    Returns (patched_html, strategy)
    """
    slug        = district["slug"]
    name        = district["name"]
    updates_url = f"/districts/{slug}/special-ed-updates"

    # Idempotency — never inject twice
    if updates_url in html:
        return html, "already_present"

    soup = BeautifulSoup(html, "html.parser")

    # Build the new card matching the exact existing card style
    new_card_html = (
        f'\n          <a href="{updates_url}" class="card-link" '
        f'style="display: block; padding: 20px; border: 1px solid #ddd; border-radius: 8px; '
        f'text-decoration: none; color: inherit; transition: all 0.2s;">\n'
        f'            <h3 style="color: #0056b3; margin-top: 0;">Special Ed Updates</h3>\n'
        f'            <p>What\'s happening right now in {name} — evaluation timelines, '
        f'TEA compliance, program changes, and parent action steps.</p>\n'
        f'          </a>\n'
    )

    # Strategy 1: append inside the .grid-4 div
    grid = soup.find("div", class_="grid-4")
    if grid:
        new_card_tag = BeautifulSoup(new_card_html, "html.parser")
        grid.append(new_card_tag)
        return str(soup), "grid-4"

    # Strategy 2: append inside .district-quick-links section
    section = soup.find("section", class_="district-quick-links")
    if section:
        new_card_tag = BeautifulSoup(new_card_html, "html.parser")
        section.append(new_card_tag)
        return str(soup), "district-quick-links"

    # Strategy 3: inject a full new section before </main>
    main_tag = soup.find("main")
    if main_tag:
        new_section_html = f"""
      <section class="district-quick-links" style="margin-top: 40px;">
        <h2>More Resources</h2>
        <div class="grid-4" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-top: 20px;">
          {new_card_html}
        </div>
      </section>"""
        new_section_tag = BeautifulSoup(new_section_html, "html.parser")
        main_tag.append(new_section_tag)
        return str(soup), "new-section-in-main"

    return html, "no_injection_point"


def patch_sub_page(district: dict, html: str, filename: str) -> tuple:
    """
    Add a Special Ed Updates link to the .page-links nav on a district sub-page.
    If no related-pages nav exists (e.g. grievance page), creates one from scratch.
    Returns (patched_html, strategy)
    """
    slug        = district["slug"]
    name        = district["name"]
    updates_url = f"/districts/{slug}/special-ed-updates"

    if updates_url in html:
        return html, "already_present"

    soup = BeautifulSoup(html, "html.parser")

    # Strategy 1: append inside existing .page-links div
    page_links = soup.find("div", class_="page-links")
    if page_links:
        new_link = soup.new_tag("a", href=updates_url)
        new_link.string = "Special Ed Updates"
        page_links.append(NavigableString(" "))
        page_links.append(new_link)
        return str(soup), "page-links"

    # Strategy 2: append inside existing .related-pages nav
    related_nav = soup.find("nav", class_="related-pages")
    if related_nav:
        container = related_nav.find("div", class_="container") or related_nav
        link_p = soup.new_tag("p", style="margin-top: 12px;")
        new_link = soup.new_tag("a", href=updates_url)
        new_link.string = "Special Ed Updates →"
        link_p.append(new_link)
        container.append(link_p)
        return str(soup), "related-pages-nav"

    # Strategy 3: create a full related-pages nav before </main> (for grievance etc.)
    main_tag = soup.find("main")
    if main_tag:
        nav_html = f"""
      <nav class="related-pages">
         <div class="container">
            <h2>Related Resources</h2>
            <div class="page-links">
               <a href="/districts/{slug}">← Back to {name} Hub</a>
               <a href="/districts/{slug}/ard-process-guide">ARD Process Guide</a>
               <a href="/districts/{slug}/evaluation-child-find">Evaluation Process</a>
               <a href="/districts/{slug}/leadership-directory">Leadership Directory</a>
               <a href="{updates_url}">Special Ed Updates</a>
            </div>
         </div>
      </nav>"""
        nav_tag = BeautifulSoup(nav_html, "html.parser")
        main_tag.append(nav_tag)
        return str(soup), "created-related-pages-nav"

    return html, "no_injection_point"


# ═══════════════════════════════════════════════════════════════════════════════
# NEW PAGE GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def extract_site_chrome(index_html: str) -> dict:
    """
    Pull the real <head> CSS links, <header>, and <footer> out of the district
    index.html so the new page is pixel-perfect with the rest of the site.
    """
    soup = BeautifulSoup(index_html, "html.parser")

    # CSS stylesheet links (keep all <link rel="stylesheet"> tags)
    css_links = ""
    for tag in soup.find_all("link", rel="stylesheet"):
        css_links += str(tag) + "\n  "

    # Full <header> block
    header = soup.find("header")
    header_html = str(header) if header else ""

    # Full <footer> block
    footer = soup.find("footer")
    footer_html = str(footer) if footer else ""

    # Google Apps Script subscribe handler (keep it working on the new page)
    subscribe_script = ""
    for script in soup.find_all("script"):
        if script.string and "GOOGLE_SCRIPT_URL" in script.string:
            subscribe_script = str(script)
            break

    # Mobile menu script
    mobile_script = ""
    for script in soup.find_all("script"):
        if script.string and "mobile-menu-toggle" in script.string:
            mobile_script = str(script)
            break

    # Pull the real CTA/promo box directly from index.html (dark gradient Stripe block)
    cta_block = ""
    for div in soup.find_all("div", style=True):
        style = div.get("style", "")
        if "linear-gradient" in style and "buy.stripe.com" in str(div):
            cta_block = str(div)
            break

    return {
        "css_links":        css_links,
        "header_html":      header_html,
        "footer_html":      footer_html,
        "subscribe_script": subscribe_script,
        "mobile_script":    mobile_script,
        "cta_block":        cta_block,
    }


def build_new_page(district: dict, chrome: dict, meta: dict,
                   body_sections: str, faqs: list, cta_html: str = "") -> str:
    """
    Assemble the complete special-ed-updates.html using:
    - Real header/footer extracted from the district's index.html
    - Claude-generated body content
    - FAQ section with JSON-LD schema
    """
    slug         = district["slug"]
    name         = district["name"]
    abbr         = district["abbreviation"]
    city         = district["city"]
    enrollment   = district["enrollment"]
    current_date = datetime.now().strftime("%B %d, %Y")
    page_url     = f"https://www.texasspecialed.com/districts/{slug}/special-ed-updates"

    # JSON-LD schemas
    faq_schema = json.dumps({
        "@context":   "https://schema.org",
        "@type":      "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name":  f["question"],
                "acceptedAnswer": {"@type": "Answer", "text": f["answer"]}
            }
            for f in faqs
        ]
    }, indent=2)

    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type":    "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",
             "item": "https://www.texasspecialed.com"},
            {"@type": "ListItem", "position": 2, "name": "Districts",
             "item": "https://www.texasspecialed.com/districts/"},
            {"@type": "ListItem", "position": 3, "name": f"{name}",
             "item": f"https://www.texasspecialed.com/districts/{slug}"},
            {"@type": "ListItem", "position": 4, "name": "Special Ed Updates",
             "item": page_url},
        ]
    }, indent=2)

    article_schema = json.dumps({
        "@context":        "https://schema.org",
        "@type":           "Article",
        "headline":        meta["title"],
        "description":     meta["description"],
        "dateModified":    datetime.now().strftime("%Y-%m-%d"),
        "publisher":       {"@type": "Organization", "name": "TexasSpecialEd.com",
                            "url": "https://www.texasspecialed.com"},
        "mainEntityOfPage": page_url,
    }, indent=2)

    # Build FAQ HTML blocks — matching the site's clean paragraph style
    faq_items_html = ""
    for faq in faqs:
        faq_items_html += f"""
               <div class="faq-item" style="border-bottom: 1px solid #e2e8f0; padding: 20px 0;">
                  <h3 style="font-size: 1.05rem; color: #0f172a; margin-bottom: 8px;">{faq['question']}</h3>
                  <p style="color: #374151; margin: 0;">{faq['answer']}</p>
               </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{meta['title']}</title>
  <meta name="description" content="{meta['description']}">

  <link rel="canonical" href="{page_url}">

  <meta property="og:title" content="{meta['title']}">
  <meta property="og:description" content="{meta['description']}">
  <meta property="og:url" content="{page_url}">
  <meta property="og:type" content="article">

  {chrome['css_links']}

  <script type="application/ld+json">
{faq_schema}
  </script>
  <script type="application/ld+json">
{breadcrumb_schema}
  </script>
  <script type="application/ld+json">
{article_schema}
  </script>

  <style>
    /* Page-specific styles only — layout comes from global.css */
    .key-info-box {{
      background: #f0f7ff;
      padding: 20px;
      border-left: 5px solid #0056b3;
      margin: 20px 0;
      border-radius: 4px;
    }}
    .update-badge {{
      display: inline-block;
      background: #dcfce7;
      color: #166534;
      padding: 4px 14px;
      border-radius: 50px;
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-bottom: 12px;
    }}
    .content-section {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 28px 30px;
      margin-bottom: 28px;
    }}
    .action-box {{
      background: #eff6ff;
      border-left: 4px solid #2563eb;
      padding: 18px 22px;
      border-radius: 6px;
      margin: 20px 0;
    }}
    .action-box p {{ margin: 0; }}
    ul.guide-list {{ padding-left: 0; list-style: none; margin-bottom: 16px; }}
    ul.guide-list li {{
      padding: 8px 0 8px 24px;
      position: relative;
      border-bottom: 1px solid #f1f5f9;
    }}
    ul.guide-list li:last-child {{ border-bottom: none; }}
    ul.guide-list li::before {{
      content: "›";
      color: #0056b3;
      font-weight: 700;
      position: absolute;
      left: 4px;
    }}
    .faq-container {{
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      overflow: hidden;
      margin-top: 16px;
    }}
    .faq-item:last-child {{ border-bottom: none !important; }}
    .stats-row {{ margin-top: 20px; display: flex; gap: 20px; flex-wrap: wrap; }}
    .stat-box {{
      background: #fff;
      padding: 15px;
      border-radius: 6px;
      border: 1px solid #eee;
    }}
    .stat-number {{ font-weight: 700; font-size: 1.2em; color: #0056b3; }}
    .stat-label {{ display: block; font-size: 0.9em; color: #666; }}
  </style>
</head>

<body>

{chrome['header_html']}

<main>
   <div class="container">

      <!-- AEO Quick Answer Block -->
      <div class="aeo-authority-block" style="background: #f0f7ff; padding: 20px; border-left: 5px solid #0056b3; margin: 20px 0; border-radius: 4px;">
        <p><strong>Quick Answer:</strong> This page covers the current state of special education in <strong>{name}</strong> — including evaluation timelines, IEP rights, TEA compliance trends, and specific action steps for {city} families navigating the system right now.</p>
      </div>

      <!-- Breadcrumb -->
      <nav aria-label="breadcrumb" class="breadcrumb">
        <div class="container">
          <a href="/">Home</a> ›
          <a href="/districts/">Districts</a> ›
          <a href="/districts/{slug}">{name}</a> ›
          <span>Special Ed Updates</span>
        </div>
      </nav>

      <!-- Page Hero -->
      <section class="hero district-hero">
        <span class="update-badge">Updated {current_date}</span>
        <h1>{name} Special Education: What Parents Need to Know Right Now</h1>
        <p class="lead">District-specific intelligence on evaluation timelines, ARD compliance, and parent rights in {city}, Texas.</p>
        <div class="stats-row">
          <div class="stat-box">
            <span class="stat-number">{enrollment}</span>
            <span class="stat-label">Students Enrolled</span>
          </div>
          <div class="stat-box">
            <span class="stat-number">{abbr}</span>
            <span class="stat-label">District Abbreviation</span>
          </div>
        </div>
      </section>

      <!-- Claude-generated body sections -->
      {body_sections}

      <!-- CTA block pulled directly from district index.html -->
      {cta_html}

      <!-- FAQ Section -->
      <section style="margin-top: 40px;">
        <h2>Frequently Asked Questions: {name} Special Education</h2>
        <p>Real questions {city} parents are searching for — answered with Texas law in mind.</p>
        <div class="faq-container">
          {faq_items_html}
        </div>
      </section>

      <!-- Email Subscribe — same form as index.html -->
      <section class="cta-section" style="margin-top: 60px; background: #f8f9fa; padding: 40px; text-align: center; border-radius: 8px;">
        <h2>Get {abbr} Special Education Updates</h2>
        <p>Subscribe to receive alerts about {name} program changes, evaluation deadlines, and parent training events.</p>
        <form action="/subscribe" method="post" class="subscribe-form" style="margin-top: 20px; display: inline-flex; gap: 10px; flex-wrap: wrap; justify-content: center;">
          <input type="email" name="email" placeholder="Your email address" required aria-label="Email address" style="padding: 10px; min-width: 250px; border: 1px solid #ccc; border-radius: 4px;">
          <input type="hidden" name="district" value="{slug}">
          <button type="submit" class="button-primary" style="background: #0056b3; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">Subscribe</button>
        </form>
      </section>

   </div>

   <!-- Related Pages Nav — links back to hub and sibling pages -->
   <nav class="related-pages">
      <div class="container">
         <h2>Related Resources</h2>
         <div class="page-links">
            <a href="/districts/{slug}">← Back to {name} Hub</a>
            <a href="/districts/{slug}/ard-process-guide">ARD Process Guide</a>
            <a href="/districts/{slug}/evaluation-child-find">Evaluation Process</a>
            <a href="/districts/{slug}/grievance-dispute-resolution">Dispute Resolution</a>
            <a href="/districts/{slug}/leadership-directory">Leadership Directory</a>
         </div>
      </div>
   </nav>
</main>

{chrome['footer_html']}

{chrome['subscribe_script']}

{chrome['mobile_script']}

</body>
</html>"""


# ═══════════════════════════════════════════════════════════════════════════════
# CLAUDE API PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

def build_meta_prompt(district: dict) -> str:
    return f"""Generate an SEO meta title and description for a page about {district['name']} special education news and parent intelligence.
Site: texasspecialed.com

- Title: under 60 chars, include district name, one urgency/benefit word
- Description: under 155 chars, lead with benefit, mention {district['city']}

Output ONLY valid JSON, nothing else:
{{"title": "...", "description": "..."}}"""


def build_content_prompt(district: dict) -> str:
    name = district["name"]
    abbr = district["abbreviation"]
    city = district["city"]
    return f"""You are a special education parent advocate for Texas families.

Write a "District Intelligence Brief" for {name} ({abbr}) in {city}, Texas.
This is hyper-local content for parents actively navigating this specific district — not generic Texas content.

Tone: Knowledgeable, warm, direct. Use "you" and "your child" throughout. Never third-person "parents."

Write these four sections using the exact HTML structure shown:

<div class="content-section">
<h2>What's Happening in {name} Special Education Right Now</h2>
[2-3 paragraphs: recent program changes, enrollment trends affecting capacity,
any TEA monitoring patterns, budget signals affecting speech/OT/PT minutes.
Be specific to {name} — mention local campuses or initiatives where relevant.]
</div>

<div class="content-section">
<h2>Why {city} Families Are Searching for Special Ed Help</h2>
[1-2 paragraphs: what triggers a parent to start googling their rights,
specific pressures in a district this size ({district['enrollment']} students),
caseload realities, what "following the IEP" looks like in {name}.]
</div>

<div class="content-section">
<h2>IEP & ARD Timeline Red Flags in {name}</h2>
[Cover the 60-school-day evaluation clock, signs the district is behind,
what to do when ARDs keep getting rescheduled.]
<div class="action-box">
<p><strong>Action you can take today:</strong> [One specific, concrete step — not generic advice.]</p>
</div>
</div>

<div class="content-section">
<h2>What {city} Parents Should Do This Week</h2>
<ul class="guide-list">
[6-7 specific, concrete action items. Real tasks, not advice platitudes.
Each <li> should be a complete sentence with a clear action.]
</ul>
</div>

Total length: 700-900 words.
Output ONLY the four HTML div blocks above. No extra tags, no preamble.
"""


def build_faq_prompt(district: dict) -> str:
    query_list = "\n".join(f"  - {q}" for q in GSC_QUERIES)
    name = district["name"]
    abbr = district["abbreviation"]
    city = district["city"]
    return f"""Convert these raw Google Search Console queries into FAQ pairs for {name} in {city}, Texas.
Published on texasspecialed.com — optimized for Google AI Overviews and featured snippets.

Queries:
{query_list}

Rules:
- One FAQ per query. Do not skip or combine any.
- Rewrite each as a natural parent question, district-specific where possible.
  Example: "ard committee" → "Who serves on the ARD Committee in {name}?"
- Answer: 75-150 words. Direct answer in sentence ONE. Standalone (no cross-references).
  Reference Texas law (IDEA, TEC 29) where relevant. Mention {name} or {abbr} in at least half.

Output ONLY valid JSON:
{{"faqs": [{{"question": "...", "answer": "..."}}, ...]}}"""


# ═══════════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def process_district(district: dict, client, mode: str) -> None:
    slug = district["slug"]
    name = district["name"]
    source_dir = HUB_DIR / slug
    dest_dir   = OUTPUT_DIR / slug
    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  {name}  [{mode}]")
    print(f"{'='*60}")

    # ── Read source files ────────────────────────────────────────────────────
    index_path = source_dir / "index.html"
    if not source_dir.exists() or not index_path.exists():
        print(f"  ❌  Source folder or index.html not found: {source_dir}")
        print(f"      Create districts/{slug}/ and add the district HTML files.")
        return

    index_html = index_path.read_text(encoding="utf-8")

    # ── Patch hub index ──────────────────────────────────────────────────────
    if mode != "generate-only":
        patched_index, strat = patch_hub_index(district, index_html)
        (dest_dir / "index.html").write_text(patched_index, encoding="utf-8")
        icon = "✅" if strat != "already_present" else "⏭ "
        print(f"  {icon} index.html patched  [{strat}]")

        # ── Patch sub-pages ──────────────────────────────────────────────────
        for filename in PAGES_TO_PATCH:
            page_path = source_dir / filename
            if not page_path.exists():
                print(f"  –  {filename}  (not found, skipped)")
                continue
            page_html = page_path.read_text(encoding="utf-8")
            patched, strat = patch_sub_page(district, page_html, filename)
            (dest_dir / filename).write_text(patched, encoding="utf-8")
            icon = "✅" if strat != "already_present" else "⏭ "
            print(f"  {icon} {filename}  [{strat}]")

        # Copy any other files unchanged (CSS, images, etc.)
        processed = {"index.html"} | set(PAGES_TO_PATCH)
        for f in source_dir.iterdir():
            if f.is_file() and f.name not in processed:
                dest = dest_dir / f.name
                if not dest.exists():
                    shutil.copy2(f, dest)

    # ── Generate new special-ed-updates page ────────────────────────────────
    if mode != "patch-only":
        chrome = extract_site_chrome(index_html)

        # Meta
        print(f"  [API 1/3] Generating meta...")
        raw = client.messages.create(
            model=MODEL, max_tokens=300,
            messages=[{"role": "user", "content": build_meta_prompt(district)}]
        ).content[0].text.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        try:
            meta = json.loads(raw)
        except json.JSONDecodeError:
            meta = {
                "title":       f"{name} Special Education Updates {datetime.now().year}",
                "description": f"Current special ed news and parent action steps for {district['city']} families in {name}."
            }
        print(f"         → {meta['title']}")

        # Content
        print(f"  [API 2/3] Generating content sections...")
        body = client.messages.create(
            model=MODEL, max_tokens=4000,
            messages=[{"role": "user", "content": build_content_prompt(district)}]
        ).content[0].text.strip()
        print(f"         → ~{len(body.split())} words")

        # FAQs
        print(f"  [API 3/3] Converting {len(GSC_QUERIES)} GSC queries → FAQs...")
        raw_faq = client.messages.create(
            model=MODEL, max_tokens=5000,
            messages=[{"role": "user", "content": build_faq_prompt(district)}]
        ).content[0].text.strip()
        raw_faq = re.sub(r"```json|```", "", raw_faq).strip()
        try:
            faqs = json.loads(raw_faq).get("faqs", [])
        except json.JSONDecodeError:
            faqs = [{
                "question": f"What is an ARD meeting in {name}?",
                "answer":   f"An ARD (Admission, Review, and Dismissal) meeting in {name} is the formal committee process used to develop and review your child's IEP. Texas law (IDEA and TEC 29) requires {name} to give you 5 school days' written notice before scheduling an ARD. As a parent, you are a full member of the committee with equal decision-making rights."
            }]
        print(f"         → {len(faqs)} FAQ pairs")

        # Assemble and save
        new_page = build_new_page(district, chrome, meta, body, faqs, chrome.get('cta_block', ''))
        out_path = dest_dir / "special-ed-updates.html"
        out_path.write_text(new_page, encoding="utf-8")
        print(f"\n  ✅ special-ed-updates.html  ({out_path.stat().st_size / 1024:.1f} KB)")
        print(f"     → {out_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="TexasSpecialEd District Patcher + Page Generator")
    parser.add_argument("--district", type=str, default=None,
                        help="Single district name, e.g. 'Frisco ISD'. Omit for all 5.")
    parser.add_argument("--mode", type=str, default="full",
                        choices=["full", "patch-only", "generate-only"],
                        help=(
                            "full          = patch hub pages + generate new page (default)\n"
                            "patch-only    = patch hub/sub-pages only, no Claude API calls\n"
                            "generate-only = generate new page only, no HTML patching"
                        ))
    args = parser.parse_args()

    districts = DISTRICTS
    if args.district:
        districts = [d for d in DISTRICTS if args.district.lower() in d["name"].lower()]
        if not districts:
            print(f"District '{args.district}' not found.")
            print("Available:", [d["name"] for d in DISTRICTS])
            return

    client = None
    if args.mode != "patch-only":
        client = anthropic.Anthropic(api_key=API_KEY)

    print(f"\n{'='*60}")
    print(f"  TexasSpecialEd District Patcher + Generator")
    print(f"  Mode       : {args.mode}")
    print(f"  Districts  : {len(districts)}")
    print(f"  Source     : {HUB_DIR.resolve()}")
    print(f"  Output     : {OUTPUT_DIR.resolve()}")
    print(f"{'='*60}")
    print(f"""
  SETUP: Your existing district folders are used directly:
    districts/<district-slug>/index.html
    districts/<district-slug>/ard-process-guide.html
    districts/<district-slug>/evaluation-child-find.html
    districts/<district-slug>/grievance-dispute-resolution.html
    districts/<district-slug>/leadership-directory.html
""")

    for i, district in enumerate(districts):
        try:
            process_district(district, client, args.mode)
            if i < len(districts) - 1 and args.mode != "patch-only":
                print("\n  Pausing 3s...")
                time.sleep(3)
        except anthropic.APIError as e:
            print(f"\n  ❌ API error for {district['name']}: {e}")
            continue

    print(f"\n{'='*60}")
    print(f"  DONE — output in: {OUTPUT_DIR.resolve()}")
    print(f"{'='*60}")
    print("""
UPLOAD CHECKLIST (per district):
  1. generated_pages/<slug>/index.html         → replaces existing hub
  2. generated_pages/<slug>/ard-process-guide.html  → replaces existing
  3. generated_pages/<slug>/evaluation-child-find.html
  4. generated_pages/<slug>/grievance-dispute-resolution.html
  5. generated_pages/<slug>/leadership-directory.html
  6. generated_pages/<slug>/special-ed-updates.html  → NEW page

  Then in Google Search Console:
  URL Inspection → Request Indexing on each updated URL
""")


if __name__ == "__main__":
    main()