#!/usr/bin/env python3
"""
vertex_content_builder.py
==========================
Uses Google Vertex AI (Gemini) to generate and inject content across the site.

TASKS:
  --task leadership   Add 400 words of localized content to every leadership page
  --task blog         Write full blog post content for all stub blog pages
  --task blog-index   Write/rebuild the blog index page
  --task district     Add 250-400 words of localized content to every district index
  --task all          Run all four tasks in sequence

USAGE:
  python vertex_content_builder.py --site-dir "C:\\...\\texas-special-ed-site" --task district --dry-run
  python vertex_content_builder.py --site-dir "C:\\...\\texas-special-ed-site" --task all
  python vertex_content_builder.py --site-dir "C:\\...\\texas-special-ed-site" --task blog --limit 10

REQUIREMENTS:
  pip install google-cloud-aiplatform
  gcloud auth application-default login
  (or set GOOGLE_APPLICATION_CREDENTIALS env var to your service account JSON)
"""

import re
import time
import shutil
import argparse
from pathlib import Path

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False
    print("WARNING: google-cloud-aiplatform not installed.")
    print("Run: pip install google-cloud-aiplatform\n")


# ─── CONFIG — EDIT THESE ──────────────────────────────────────────────────────

VERTEX_PROJECT   = "ny-build-487810"   # ← replace with your GCP project ID
VERTEX_LOCATION  = "us-central1"
VERTEX_MODEL     = "gemini-2.0-flash"       # cheapest model, more than capable

RETRY_DELAY      = 2.0    # seconds between API calls (polite rate limiting)
MAX_RETRIES      = 3      # retries on transient errors

# Blog topics to generate if pages are stubs (no content yet)
BLOG_TOPICS = [
    ("what-is-an-ard-meeting",          "What Is an ARD Meeting? A Texas Parent's Complete Guide"),
    ("fie-evaluation-timeline",          "The 45 School Day FIE Timeline: What Texas Parents Need to Know"),
    ("dyslexia-hb3928-changes",          "HB 3928 Explained: How Texas Changed Dyslexia Law"),
    ("iep-vs-504-texas",                 "IEP vs. 504 Plan in Texas: What's the Difference?"),
    ("how-to-request-evaluation",        "How to Request a Special Education Evaluation in Texas"),
    ("ard-rights-parents",               "Your Rights at an ARD Meeting: What Every Texas Parent Must Know"),
    ("manifestation-determination",      "What Is a Manifestation Determination Review (MDR)?"),
    ("prior-written-notice-texas",       "Prior Written Notice: The Most Important Document in Special Ed"),
    ("due-process-texas",                "How to File for Due Process in Texas Special Education"),
    ("special-ed-discipline-texas",      "Special Education and School Discipline: Your Child's Rights in Texas"),
    ("child-find-obligations",           "Child Find: Why Schools Must Proactively Identify Students with Disabilities"),
    ("ard-meeting-tips",                 "12 Tips to Prepare for Your Child's ARD Meeting"),
]


# ─── VERTEX AI SETUP ──────────────────────────────────────────────────────────

def init_vertex():
    if not VERTEX_AVAILABLE:
        raise RuntimeError("google-cloud-aiplatform not installed.")
    vertexai.init(project=VERTEX_PROJECT, location=VERTEX_LOCATION)
    model = GenerativeModel(VERTEX_MODEL)
    return model


def call_gemini(model, prompt: str, retries: int = MAX_RETRIES) -> str:
    config = GenerationConfig(
        temperature=0.7,
        max_output_tokens=2048,
    )
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt, generation_config=config)
            return response.text.strip()
        except Exception as e:
            if attempt < retries - 1:
                print(f"    ⚠️  Retry {attempt+1}/{retries}: {e}")
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                raise
    return ""


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def get_district_slug(html_file: Path, root: Path) -> str | None:
    try:
        parts = html_file.relative_to(root).parts
        # Expect: districts/{slug}/file.html
        if len(parts) >= 3 and parts[0] == "districts":
            return parts[1]
    except ValueError:
        pass
    return None


def slug_to_name(slug: str) -> str:
    return slug.replace("-", " ").title().replace(" Isd", " ISD").replace(" Cisd", " CISD")


def inject_before_closing_main(content: str, new_html: str) -> str:
    """Insert new_html just before </main>."""
    if "</main>" in content:
        return content.replace("</main>", new_html + "\n</main>", 1)
    return content + new_html


def inject_before_closing_section(content: str, new_html: str, section_class: str) -> str:
    """Insert new_html before a specific closing section tag."""
    pattern = rf'(</section>\s*</main>)'
    if re.search(pattern, content):
        return re.sub(pattern, new_html + r'\n\1', content, count=1)
    return inject_before_closing_main(content, new_html)


def already_expanded(content: str, marker: str) -> bool:
    """Check if content was already expanded by this script."""
    return f'data-generated="{marker}"' in content


def backup_and_write(file_path: Path, content: str, no_backup: bool):
    if not no_backup:
        shutil.copy2(file_path, file_path.with_suffix(".html.bak"))
    file_path.write_text(content, encoding="utf-8")


# ─── TASK 1: LEADERSHIP PAGES ─────────────────────────────────────────────────

LEADERSHIP_PROMPT = """
You are writing content for a Texas special education parent resource website.
Write exactly 400 words of helpful, practical HTML content for the leadership directory page
for {district_name}.

The content should include these sections wrapped in appropriate HTML:
1. A section titled "How to Effectively Contact {district_name} Special Education Staff"
   - Best times to contact, email vs phone guidance, what to say in your first message
   - Tip: always follow up in writing after phone calls
2. A section titled "What to Do If You Can't Reach Anyone"
   - Escalation steps: teacher → campus sped coordinator → district director → TEA complaint
   - Reference Texas Education Code Chapter 29
3. A section titled "Your Right to District Records"
   - FERPA 45-day records request right
   - Public Information Act (Texas Gov Code Ch. 552) for staff contact info
   - How to submit a records request in writing

RULES:
- Use <h2> for section titles
- Use <p> tags for paragraphs
- Use <ul> with <li> for any lists
- Do NOT include <html>, <head>, <body>, or <style> tags
- Do NOT include any markdown — pure HTML only
- Wrap the entire output in: <div class="content-section" data-generated="leadership-expansion">
- Keep it practical, empowering, and specific to Texas law
- Total word count: 380-420 words
- District name to use: {district_name}
"""


def task_leadership(model, site_dir: Path, dry_run: bool, no_backup: bool, limit: int):
    print("\n" + "="*60)
    print("  TASK: Leadership Page Expansion")
    print("="*60)

    districts_root = site_dir / "districts"
    pages = sorted(districts_root.rglob("leadership-directory.html"))

    if limit:
        pages = pages[:limit]

    print(f"  Found {len(pages)} leadership pages\n")

    done = skipped = errors = 0

    for page in pages:
        slug = get_district_slug(page, site_dir)
        if not slug:
            continue

        district_name = slug_to_name(slug)
        content = page.read_text(encoding="utf-8", errors="ignore")

        if already_expanded(content, "leadership-expansion"):
            print(f"  SKIP  {slug} (already expanded)")
            skipped += 1
            continue

        print(f"  → {district_name}...", end=" ", flush=True)

        if dry_run:
            print("(dry run)")
            done += 1
            continue

        try:
            prompt   = LEADERSHIP_PROMPT.format(district_name=district_name)
            new_html = call_gemini(model, prompt)
            new_content = inject_before_closing_main(content, new_html)
            backup_and_write(page, new_content, no_backup)
            print(f"✅ ({len(new_html.split())} words added)")
            done += 1
        except Exception as e:
            print(f"❌ {e}")
            errors += 1

        time.sleep(RETRY_DELAY)

    print(f"\n  Done: {done} | Skipped: {skipped} | Errors: {errors}")


# ─── TASK 2: DISTRICT INDEX EXPANSION ─────────────────────────────────────────

DISTRICT_INDEX_PROMPT = """
You are writing localized content for a Texas special education parent resource website.
Write 300-350 words of HTML content specifically about {district_name}'s special education
program to add to their resource hub page.

Include:
1. A section "About Special Education in {district_name}"
   - Reference the district's approximate size/region if known (use: {district_name} serves the {region} area)
   - Mention that the district operates under TEA Region {esc_region} oversight
   - Note the ARD process timeline (45 school days for FIE, 5-day ARD notice)
2. A section "Common Questions from {district_name} Families"
   - 3 specific, realistic questions parents in this district would ask
   - Brief answer to each (2-3 sentences)
3. One practical tip for parents navigating a {district_size} district
   ({enrollment} students — {size_tip})

RULES:
- Use <h2> for section titles, <h3> for question subheadings
- Use <p> tags for all paragraphs
- Do NOT include <html>, <head>, <body>, or <style> tags  
- Do NOT include markdown — pure HTML only
- Wrap entire output in: <div class="content-section" data-generated="district-expansion">
- Total: 300-350 words
- Be specific to {district_name}, not generic
"""


# District metadata for localized prompts
# Format: slug → (region_name, esc_region, enrollment)
DISTRICT_META = {
    "houston-isd":           ("Houston",        "4",  "194,000"),
    "dallas-isd":            ("Dallas",         "10", "145,000"),
    "cypress-fairbanks-isd": ("Houston",        "4",  "118,470"),
    "northside-isd":         ("San Antonio",    "20", "101,095"),
    "katy-isd":              ("Houston",        "4",  "94,785"),
    "austin-isd":            ("Austin",         "13", "73,000"),
    "conroe-isd":            ("Houston",        "6",  "72,352"),
    "fort-bend-isd":         ("Houston",        "4",  "82,000"),
    "lewisville-isd":        ("DFW",            "10", "48,440"),
    "plano-isd":             ("DFW",            "10", "47,899"),
    "round-rock-isd":        ("Austin",         "13", "46,197"),
    "allen-isd":             ("DFW",            "10", "22,000"),
    "frisco-isd":            ("DFW",            "10", "66,698"),
    "alief-isd":             ("Houston",        "4",  "47,000"),
    "aldine-isd":            ("Houston",        "4",  "67,000"),
    "abilene-isd":           ("West Texas",     "14", "15,500"),
    "amarillo-isd":          ("Panhandle",      "16", "32,000"),
    "arlington-isd":         ("DFW",            "11", "57,000"),
    "beaumont-isd":          ("Southeast Texas","5",  "18,500"),
    "corpus-christi-isd":    ("Coastal Bend",   "2",  "37,000"),
    "el-paso-isd":           ("El Paso",        "19", "57,000"),
    "garland-isd":           ("DFW",            "10", "55,000"),
    "grand-prairie-isd":     ("DFW",            "10", "28,000"),
    "humble-isd":            ("Houston",        "4",  "45,000"),
    "lubbock-isd":           ("West Texas",     "17", "27,000"),
    "mcallen-isd":           ("Rio Grande Valley","1", "21,000"),
    "mesquite-isd":          ("DFW",            "10", "40,000"),
    "midland-isd":           ("West Texas",     "18", "24,000"),
    "pasadena-isd":          ("Houston",        "4",  "52,000"),
    "pflugerville-isd":      ("Austin",         "13", "26,000"),
    "richardson-isd":        ("DFW",            "10", "40,000"),
    "san-antonio-isd":       ("San Antonio",    "20", "45,000"),
    "spring-isd":            ("Houston",        "4",  "38,000"),
    "waco-isd":              ("Central Texas",  "12", "15,000"),
    "ysleta-isd":            ("El Paso",        "19", "41,000"),
}

DEFAULT_META = ("Texas", "unknown", "10,000")


def task_district_index(model, site_dir: Path, dry_run: bool, no_backup: bool, limit: int):
    print("\n" + "="*60)
    print("  TASK: District Index Expansion")
    print("="*60)

    districts_root = site_dir / "districts"
    pages = sorted(districts_root.rglob("index.html"))

    if limit:
        pages = pages[:limit]

    print(f"  Found {len(pages)} district index pages\n")

    done = skipped = errors = 0

    for page in pages:
        slug = get_district_slug(page, site_dir)
        if not slug:
            continue

        district_name = slug_to_name(slug)
        content = page.read_text(encoding="utf-8", errors="ignore")

        if already_expanded(content, "district-expansion"):
            print(f"  SKIP  {slug} (already expanded)")
            skipped += 1
            continue

        meta   = DISTRICT_META.get(slug, DEFAULT_META)
        region, esc_region, enrollment = meta

        # Pre-compute size tip — avoids conditional logic inside .format()
        enroll_num    = int(enrollment.replace(",", ""))
        district_size = "large" if enroll_num > 20000 else "small"
        size_tip      = (
            "tip: large districts have dedicated campus sped coordinators — start there before escalating to the district office"
            if enroll_num > 20000 else
            "tip: small districts often have one sped director handling everything — email is better than phone so you have a paper trail"
        )

        print(f"  → {district_name}...", end=" ", flush=True)

        if dry_run:
            print("(dry run)")
            done += 1
            continue

        try:
            prompt = DISTRICT_INDEX_PROMPT.format(
                district_name=district_name,
                region=region,
                esc_region=esc_region,
                enrollment=enrollment,
                district_size=district_size,
                size_tip=size_tip,
            )
            new_html    = call_gemini(model, prompt)
            new_content = inject_before_closing_main(content, new_html)
            backup_and_write(page, new_content, no_backup)
            print(f"✅ ({len(new_html.split())} words added)")
            done += 1
        except Exception as e:
            print(f"❌ {e}")
            errors += 1

        time.sleep(RETRY_DELAY)

    print(f"\n  Done: {done} | Skipped: {skipped} | Errors: {errors}")


# ─── TASK 3: BLOG POSTS ───────────────────────────────────────────────────────

BLOG_POST_PROMPT = """
You are writing a high-quality blog post for a Texas special education parent resource website
called TexasSpecialEd.com.

Write a complete, authoritative blog post on the topic: "{title}"
Slug: {slug}

Requirements:
- 900-1100 words of actual content
- Target audience: Texas parents of children with disabilities
- Include specific Texas law references (IDEA, Texas Education Code Chapter 29, TEA rules)
- Include at least one mention of the ARD process or TEA
- Structure with clear H2 subheadings (4-5 sections)
- Include a practical "What to Do Next" or "Action Steps" section at the end
- Write in a warm, empowering tone — parents are stressed, be helpful not intimidating
- Do NOT use markdown — pure HTML only
- Do NOT include <html>, <head>, <body>, or <style> tags
- Wrap entire output in: <article class="blog-content" data-generated="blog-post">
- Include a <p class="post-intro"> tag for the opening paragraph
- Close with a <div class="post-cta"> containing a call to action linking to /districts/index.html
"""

BLOG_POST_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{title} | Texas Special Ed</title>
<meta content="{meta_desc}" name="description"/>
<link href="https://texasspecialed.com/blog/{slug}.html" rel="canonical"/>
<link href="/style.css" rel="stylesheet"/>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1e293b; background: #fff; line-height: 1.6; display: flex; flex-direction: column; min-height: 100vh; }}
  h1 {{ font-size: 2.25rem; margin-bottom: 20px; color: #0f172a; }}
  h2 {{ font-size: 1.5rem; margin: 30px 0 10px; color: #0f172a; }}
  h3 {{ font-size: 1.2rem; margin: 20px 0 8px; color: #0f172a; }}
  p {{ margin-bottom: 14px; color: #374151; }}
  a {{ color: #2563eb; }}
  .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
  .site-header {{ background: #ffffff; box-shadow: 0 2px 10px rgba(0,0,0,0.07); padding: 14px 0; position: sticky; top: 0; z-index: 9999; }}
  .nav-container {{ max-width: 1100px; margin: 0 auto; padding: 0 20px; display: flex; align-items: center; justify-content: space-between; }}
  .nav-logo img {{ height: auto; width: 200px; }}
  .nav-menu {{ display: flex; list-style: none; gap: 24px; align-items: center; margin: 0; padding: 0; }}
  .nav-link {{ color: #1e2530; text-decoration: none; font-size: 0.95rem; font-weight: 500; transition: color 0.2s; }}
  .nav-link:hover {{ color: #1560a8; }}
  .button-primary {{ background: #2563eb; color: #fff; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 0.9rem; }}
  .post-intro {{ font-size: 1.1rem; color: #374151; margin-bottom: 30px; line-height: 1.8; border-left: 4px solid #2563eb; padding-left: 20px; }}
  .post-cta {{ background: #f0f9ff; border: 1px solid #bae6fd; padding: 25px; border-radius: 8px; margin-top: 40px; }}
  .post-cta h3 {{ color: #0f172a; margin-bottom: 10px; }}
  .site-footer {{ background: #0f172a; color: #94a3b8; padding: 40px 20px 20px; margin-top: 50px; font-size: 0.9rem; }}
  .footer-bottom {{ max-width: 1100px; margin: 25px auto 0; padding-top: 15px; border-top: 1px solid #334155; text-align: center; font-size: 0.85rem; }}
  .mobile-menu-toggle {{ display: none; background: transparent; border: none; cursor: pointer; padding: 5px; }}
  .hamburger {{ display: block; width: 25px; height: 3px; background: #0a3d6b; margin: 5px 0; border-radius: 2px; }}
  @media (max-width: 900px) {{
    .nav-menu {{ display: none; flex-direction: column; width: 100%; position: absolute; top: 100%; left: 0; background: #ffffff; padding: 20px 0; }}
    .nav-menu.active {{ display: flex; }}
    .mobile-menu-toggle {{ display: block; }}
  }}
</style>
</head>
<body>
<header class="site-header">
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-logo"><a href="/"><img alt="Texas Special Ed" src="/images/texasspecialed-logo.png" width="200" height="auto"/></a></div>
      <button class="mobile-menu-toggle" aria-label="Toggle menu"><span class="hamburger"></span><span class="hamburger"></span><span class="hamburger"></span></button>
      <ul class="nav-menu">
        <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="/districts/index.html">Districts</a></li>
        <li class="nav-item"><a class="nav-link" href="/resources/index.html">Free Resources</a></li>
        <li class="nav-item"><a class="nav-link" href="/blog/index.html">Blog</a></li>
        <li class="nav-item"><a class="nav-link" href="/about/index.html">About</a></li>
        <li class="nav-item nav-cta"><a class="button-primary" href="/resources/ard-checklist.pdf" target="_blank">Free ARD Checklist</a></li>
      </ul>
    </div>
  </nav>
</header>
<main class="container" style="flex:1">
  <h1>{title}</h1>
  {content}
</main>
<footer class="site-footer">
  <div class="footer-bottom">
    <p>© 2026 Texas Special Education Resources. All rights reserved.</p>
  </div>
</footer>
<script>
document.addEventListener('DOMContentLoaded', function() {{
  const toggle = document.querySelector('.mobile-menu-toggle');
  const menu   = document.querySelector('.nav-menu');
  if (toggle && menu) toggle.addEventListener('click', () => menu.classList.toggle('active'));
}});
</script>
</body>
</html>"""


def task_blog(model, site_dir: Path, dry_run: bool, no_backup: bool, limit: int):
    print("\n" + "="*60)
    print("  TASK: Blog Post Generation")
    print("="*60)

    blog_dir = site_dir / "blog"
    blog_dir.mkdir(exist_ok=True)

    topics = BLOG_TOPICS[:limit] if limit else BLOG_TOPICS
    print(f"  Generating {len(topics)} blog posts\n")

    done = skipped = errors = 0

    for slug, title in topics:
        out_file = blog_dir / f"{slug}.html"

        if out_file.exists():
            existing = out_file.read_text(encoding="utf-8", errors="ignore")
            if already_expanded(existing, "blog-post"):
                print(f"  SKIP  {slug} (already written)")
                skipped += 1
                continue

        print(f"  → {title[:55]}...", end=" ", flush=True)

        if dry_run:
            print("(dry run)")
            done += 1
            continue

        try:
            prompt  = BLOG_POST_PROMPT.format(title=title, slug=slug)
            content = call_gemini(model, prompt)

            meta_desc = f"Texas parents guide to {title.lower()}. Understand your rights under IDEA and Texas Education Code."
            full_page = BLOG_POST_SHELL.format(
                title=title,
                slug=slug,
                meta_desc=meta_desc[:155],
                content=content,
            )

            out_file.write_text(full_page, encoding="utf-8")
            print(f"✅ ({len(content.split())} words)")
            done += 1
        except Exception as e:
            print(f"❌ {e}")
            errors += 1

        time.sleep(RETRY_DELAY)

    print(f"\n  Done: {done} | Skipped: {skipped} | Errors: {errors}")


# ─── TASK 4: BLOG INDEX ───────────────────────────────────────────────────────

BLOG_INDEX_INTRO_PROMPT = """
Write a 200-word introduction for the blog index page of TexasSpecialEd.com.
The blog covers Texas special education law, ARD meeting tips, dyslexia rights,
IEP strategies, and parent advocacy for families in Texas school districts.

Tone: warm, empowering, and authoritative.
Output: pure HTML only, no markdown, no wrapper tags.
Use 2-3 <p> tags. No headings needed.
"""


def task_blog_index(model, site_dir: Path, dry_run: bool, no_backup: bool):
    print("\n" + "="*60)
    print("  TASK: Blog Index Page")
    print("="*60)

    blog_dir  = site_dir / "blog"
    index_out = blog_dir / "index.html"
    blog_dir.mkdir(exist_ok=True)

    if dry_run:
        print("  (dry run — would build blog index)")
        return

    # Gather all blog posts
    posts = []
    for slug, title in BLOG_TOPICS:
        post_file = blog_dir / f"{slug}.html"
        posts.append({"slug": slug, "title": title, "exists": post_file.exists()})

    print(f"  Building index with {len(posts)} posts...", end=" ", flush=True)

    try:
        intro = call_gemini(model, BLOG_INDEX_INTRO_PROMPT)
    except Exception as e:
        intro = "<p>Expert guides and practical resources to help Texas parents navigate special education, ARD meetings, and their child's rights under state and federal law.</p>"
        print(f"  (intro generation failed: {e}, using default)")

    # Build post cards
    cards_html = ""
    for p in posts:
        cards_html += f"""
    <a href="/blog/{p['slug']}.html" class="blog-card">
      <h3>{p['title']}</h3>
      <span class="read-more">Read Article →</span>
    </a>"""

    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Texas Special Education Blog | Parent Guides & Resources</title>
<meta content="Expert guides for Texas parents navigating special education, ARD meetings, IEP rights, dyslexia law, and more." name="description"/>
<link href="https://texasspecialed.com/blog/" rel="canonical"/>
<link href="/style.css" rel="stylesheet"/>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1e293b; background: #fff; line-height: 1.6; display: flex; flex-direction: column; min-height: 100vh; }}
  h1 {{ font-size: 2.25rem; margin-bottom: 20px; color: #0f172a; }}
  h2 {{ font-size: 1.5rem; margin: 30px 0 10px; color: #0f172a; }}
  p {{ margin-bottom: 14px; color: #374151; }}
  a {{ color: #2563eb; }}
  .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
  .site-header {{ background: #ffffff; box-shadow: 0 2px 10px rgba(0,0,0,0.07); padding: 14px 0; position: sticky; top: 0; z-index: 9999; }}
  .nav-container {{ max-width: 1100px; margin: 0 auto; padding: 0 20px; display: flex; align-items: center; justify-content: space-between; }}
  .nav-logo img {{ height: auto; width: 200px; }}
  .nav-menu {{ display: flex; list-style: none; gap: 24px; align-items: center; margin: 0; padding: 0; }}
  .nav-link {{ color: #1e2530; text-decoration: none; font-size: 0.95rem; font-weight: 500; transition: color 0.2s; }}
  .nav-link:hover {{ color: #1560a8; }}
  .button-primary {{ background: #2563eb; color: #fff; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 0.9rem; }}
  .blog-intro {{ background: #f8fafc; border-left: 5px solid #2563eb; padding: 25px 30px; border-radius: 4px; margin-bottom: 40px; }}
  .blog-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 30px; }}
  .blog-card {{ background: #fff; border: 1px solid #e2e8f0; padding: 25px; border-radius: 8px; text-decoration: none; display: block; transition: all 0.2s; }}
  .blog-card:hover {{ border-color: #2563eb; transform: translateY(-3px); box-shadow: 0 8px 16px rgba(0,0,0,0.08); }}
  .blog-card h3 {{ color: #0f172a; font-size: 1.05rem; margin-bottom: 10px; }}
  .read-more {{ color: #2563eb; font-size: 0.9rem; font-weight: 600; }}
  .site-footer {{ background: #0f172a; color: #94a3b8; padding: 40px 20px 20px; margin-top: 50px; font-size: 0.9rem; }}
  .footer-bottom {{ max-width: 1100px; margin: 25px auto 0; padding-top: 15px; border-top: 1px solid #334155; text-align: center; font-size: 0.85rem; }}
  .mobile-menu-toggle {{ display: none; background: transparent; border: none; cursor: pointer; padding: 5px; }}
  .hamburger {{ display: block; width: 25px; height: 3px; background: #0a3d6b; margin: 5px 0; border-radius: 2px; }}
  @media (max-width: 900px) {{
    .nav-menu {{ display: none; flex-direction: column; width: 100%; position: absolute; top: 100%; left: 0; background: #fff; padding: 20px 0; }}
    .nav-menu.active {{ display: flex; }}
    .mobile-menu-toggle {{ display: block; }}
  }}
</style>
</head>
<body>
<header class="site-header">
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-logo"><a href="/"><img alt="Texas Special Ed" src="/images/texasspecialed-logo.png" width="200" height="auto"/></a></div>
      <button class="mobile-menu-toggle" aria-label="Toggle menu"><span class="hamburger"></span><span class="hamburger"></span><span class="hamburger"></span></button>
      <ul class="nav-menu">
        <li><a class="nav-link" href="/">Home</a></li>
        <li><a class="nav-link" href="/districts/index.html">Districts</a></li>
        <li><a class="nav-link" href="/resources/index.html">Free Resources</a></li>
        <li><a class="nav-link" href="/blog/index.html">Blog</a></li>
        <li><a class="nav-link" href="/about/index.html">About</a></li>
        <li><a class="button-primary" href="/resources/ard-checklist.pdf" target="_blank">Free ARD Checklist</a></li>
      </ul>
    </div>
  </nav>
</header>
<main class="container" style="flex:1">
  <h1>Texas Special Education Blog</h1>
  <div class="blog-intro" data-generated="blog-index">
    {intro}
  </div>
  <h2>All Articles</h2>
  <div class="blog-grid">
    {cards_html}
  </div>
</main>
<footer class="site-footer">
  <div class="footer-bottom">
    <p>© 2026 Texas Special Education Resources. All rights reserved.</p>
  </div>
</footer>
<script>
document.addEventListener('DOMContentLoaded', function() {{
  const toggle = document.querySelector('.mobile-menu-toggle');
  const menu   = document.querySelector('.nav-menu');
  if (toggle && menu) toggle.addEventListener('click', () => menu.classList.toggle('active'));
}});
</script>
</body>
</html>"""

    index_out.write_text(index_html, encoding="utf-8")
    print(f"✅  ({len(posts)} post cards)")


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def run(site_dir: str, task: str, dry_run: bool, no_backup: bool, limit: int):
    root = Path(site_dir).resolve()

    if not root.exists():
        print(f"\nERROR: Directory not found: {root}\n")
        return

    print(f"\n{'='*60}")
    print(f"  Vertex AI Content Builder")
    print(f"{'='*60}")
    print(f"  Site root : {root}")
    print(f"  Task      : {task}")
    print(f"  Model     : {VERTEX_MODEL}")
    print(f"  Mode      : {'DRY RUN' if dry_run else 'LIVE'}")
    if limit:
        print(f"  Limit     : {limit} pages per task")
    print(f"{'='*60}")

    if VERTEX_PROJECT == "your-gcp-project-id":
        print("\n  ⚠️  ERROR: Set your VERTEX_PROJECT at the top of this script first.\n")
        return

    model = None
    if not dry_run:
        if not VERTEX_AVAILABLE:
            print("\n  ⚠️  ERROR: Run: pip install google-cloud-aiplatform\n")
            return
        print("\n  Initializing Vertex AI...", end=" ")
        try:
            model = init_vertex()
            print("✅")
        except Exception as e:
            print(f"❌ {e}")
            return

    tasks_to_run = ["leadership", "district", "blog", "blog-index"] if task == "all" else [task]

    for t in tasks_to_run:
        if t == "leadership":
            task_leadership(model, root, dry_run, no_backup, limit)
        elif t == "district":
            task_district_index(model, root, dry_run, no_backup, limit)
        elif t == "blog":
            task_blog(model, root, dry_run, no_backup, limit)
        elif t == "blog-index":
            task_blog_index(model, root, dry_run, no_backup)

    print(f"\n{'='*60}")
    print("  All tasks complete.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vertex AI content builder for TexasSpecialEd.com")
    parser.add_argument("--site-dir",  required=True, help="Root of your site folder")
    parser.add_argument("--task",      required=True,
                        choices=["leadership", "district", "blog", "blog-index", "all"],
                        help="Which task to run")
    parser.add_argument("--dry-run",   action="store_true", help="Preview without API calls")
    parser.add_argument("--no-backup", action="store_true", help="Skip .bak files")
    parser.add_argument("--limit",     type=int, default=0,
                        help="Process only N pages per task (useful for testing)")
    args = parser.parse_args()
    run(args.site_dir, args.task, args.dry_run, args.no_backup, args.limit)