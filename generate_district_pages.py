#!/usr/bin/env python3
"""
Texas Special Ed — District Page Generator
Uses Vertex AI (Gemini) to generate district-specific special-ed-updates pages
with SEO + AEO optimizations baked in.

Requirements:
    pip install google-cloud-aiplatform beautifulsoup4 jinja2 tqdm

Usage:
    # Generate pages for all districts in districts.csv
    python generate_district_pages.py --mode all

    # Generate for a single district (good for testing)
    python generate_district_pages.py --mode single --district "Frisco ISD"

    # Apply SEO/AEO patches to existing pages
    python generate_district_pages.py --mode patch --input-dir ./existing_pages

    # Estimate Vertex AI token cost before running
    python generate_district_pages.py --mode estimate
"""

import os
import csv
import json
import time
import argparse
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from jinja2 import Template
from tqdm import tqdm

# ── Vertex AI ────────────────────────────────────────────────────────────────
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# ── Config ────────────────────────────────────────────────────────────────────

PROJECT_ID   = "texasspecialed"   # ← replace with your GCP project ID
LOCATION     = "us-central1"
MODEL        = "gemini-2.0-flash"        # best quality; use "gemini-1.5-flash" to cut cost ~10x

OUTPUT_DIR   = Path("./output/district_pages")
LOG_FILE     = Path("./output/generation.log")

# Vertex AI pricing (approximate, as of early 2026)
# Gemini 1.5 Pro: $3.50 / 1M input tokens, $10.50 / 1M output tokens
# Gemini 1.5 Flash: $0.35 / 1M input tokens, $1.05 / 1M output tokens
INPUT_COST_PER_1M  = 3.50   # Pro
OUTPUT_COST_PER_1M = 10.50  # Pro
AVG_INPUT_TOKENS   = 1_800  # estimated per district call
AVG_OUTPUT_TOKENS  = 2_500  # estimated per district call

# ── Logging ───────────────────────────────────────────────────────────────────

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ── District data model ───────────────────────────────────────────────────────

@dataclass
class District:
    """One Texas school district with metadata for content generation."""
    slug: str                      # e.g. "frisco-isd"
    name: str                      # e.g. "Frisco ISD"
    county: str                    # e.g. "Collin and Denton Counties"
    city: str                      # e.g. "Frisco"
    enrollment: str                # e.g. "66,000+"
    campuses: str                  # e.g. "75+"
    region: str                    # e.g. "DFW Metroplex"
    sped_contact_email: str        # e.g. "specialeducation@friscoisd.com"
    unique_context: str            # 1-2 sentences of district-specific detail
    existing_pages: list[str] = field(default_factory=list)  # sibling page slugs


# ── District list (extend this CSV or add inline below) ──────────────────────

DISTRICTS: list[District] = [
    District(
        slug="frisco-isd",
        name="Frisco ISD",
        county="Collin and Denton Counties",
        city="Frisco",
        enrollment="66,000+",
        campuses="75+",
        region="DFW Metroplex",
        sped_contact_email="specialeducation@friscoisd.com",
        unique_context=(
            "Frisco ISD has seen rapid growth that has outpaced its special education "
            "staffing pipeline, leading to heavy reliance on contracted service providers "
            "for speech therapy and OT. The district's affluent demographics create pressure "
            "to maintain high academic ratings, which can subtly discourage referrals to "
            "special education in favor of 504 plans or RTI loops."
        ),
        existing_pages=["ard-process-guide", "evaluation-child-find", "dyslexia-services",
                        "grievance-dispute-resolution"],
    ),
    District(
        slug="katy-isd",
        name="Katy ISD",
        county="Harris, Fort Bend, and Waller Counties",
        city="Katy",
        enrollment="90,000+",
        campuses="90+",
        region="Houston Metro",
        sped_contact_email="specialeducation@katyisd.org",
        unique_context=(
            "Katy ISD is one of the largest suburban districts in Texas, serving a highly "
            "diverse student population with significant ELL overlap with special education "
            "eligibility. The district operates multiple specialized campuses and programs, "
            "but wait times for diagnostician evaluations have been a reported concern."
        ),
        existing_pages=["ard-process-guide", "evaluation-child-find", "dyslexia-services",
                        "grievance-dispute-resolution", "leadership-directory"],
    ),
    District(
        slug="garland-isd",
        name="Garland ISD",
        county="Dallas County",
        city="Garland",
        enrollment="54,000+",
        campuses="70+",
        region="DFW Metroplex",
        sped_contact_email="specialeducation@garlandisd.net",
        unique_context=(
            "Garland ISD serves one of the most economically and linguistically diverse "
            "student populations in the Dallas area. The district has a higher-than-average "
            "percentage of students qualifying under the Other Health Impairment (OHI) category, "
            "particularly for ADHD, and parent advocates report challenges navigating bilingual "
            "special education processes."
        ),
        existing_pages=["evaluation-child-find", "dyslexia-services"],
    ),
    District(
        slug="allen-isd",
        name="Allen ISD",
        county="Collin County",
        city="Allen",
        enrollment="22,000+",
        campuses="25+",
        region="DFW Metroplex / Collin County",
        sped_contact_email="specialeducation@allenisd.org",
        unique_context=(
            "Allen ISD is a mid-sized, high-performing district where academic pressure "
            "and community expectations around college readiness can create friction for "
            "families seeking special education services. The district shares a TEA ESC "
            "Region 10 service area with Frisco and McKinney ISDs."
        ),
        existing_pages=["ard-process-guide", "evaluation-child-find"],
    ),
    District(
        slug="mckinney-isd",
        name="McKinney ISD",
        county="Collin County",
        city="McKinney",
        enrollment="25,000+",
        campuses="30+",
        region="DFW Metroplex / Collin County",
        sped_contact_email="specialeducation@mckinneyisd.net",
        unique_context=(
            "McKinney ISD has grown quickly alongside Collin County's residential expansion. "
            "The district recently reorganized its special education department, and parents "
            "report inconsistent communication between campus-level ARD facilitators and "
            "central office representatives."
        ),
        existing_pages=["grievance-dispute-resolution"],
    ),
    # ── Add more districts here or load from districts.csv ──
    # District(slug="plano-isd", name="Plano ISD", ...),
]


def load_districts_from_csv(csv_path: str) -> list[District]:
    """
    Optional: load district list from a CSV file.

    Expected columns:
        slug, name, county, city, enrollment, campuses, region,
        sped_contact_email, unique_context, existing_pages (pipe-separated)
    """
    districts = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            districts.append(District(
                slug=row["slug"],
                name=row["name"],
                county=row["county"],
                city=row["city"],
                enrollment=row["enrollment"],
                campuses=row["campuses"],
                region=row["region"],
                sped_contact_email=row["sped_contact_email"],
                unique_context=row["unique_context"],
                existing_pages=row.get("existing_pages", "").split("|"),
            ))
    return districts


# ── Prompt template ───────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are an expert SEO content strategist and special education policy writer.
You write for a website (texasspecialed.com) that helps Texas parents navigate
the special education system, specifically IEP/ARD meetings, evaluations, and
their rights under IDEA and Texas Education Code Chapter 29.

Your writing style:
- Direct, urgent, parent-facing (not academic)
- Never use filler phrases like "in conclusion" or "it's important to note"
- Short paragraphs (3-4 sentences max)
- Specific legal references (TEC §29.005, 19 TAC §89.1050, IDEA Section 300.321)
- Always position the parent as an equal decision-maker, not a passive recipient
""".strip()

CONTENT_PROMPT_TEMPLATE = """
Generate the BODY CONTENT ONLY (no HTML shell, no <html>/<head>/<body> tags)
for a special-ed-updates page targeting parents in {{ district.name }}.

This page must be DISTRICT-SPECIFIC — not generic Texas special ed content.
Reference the district's size, location, unique challenges, and contact info below.

=== DISTRICT PROFILE ===
Name: {{ district.name }}
Slug: {{ district.slug }}
Location: {{ district.city }}, Texas ({{ district.county }})
Enrollment: {{ district.enrollment }} students, {{ district.campuses }} campuses
Region: {{ district.region }}
Special Ed Contact: {{ district.sped_contact_email }}
Unique Context: {{ district.unique_context }}

=== OUTPUT REQUIREMENTS ===
Return a valid JSON object with these exact keys:

{
  "meta_title": "...",          // 55-60 chars. Include district name + year (2026)
  "meta_description": "...",    // 145-155 chars. Urgent, specific, parent-facing
  "h1": "...",                  // 60-80 chars. Action-oriented
  "quick_answer_html": "...",   // 2-3 sentence HTML paragraph. Defines ARD + most urgent parent right
  "section_whats_happening": {
    "heading": "...",
    "paragraphs": ["...", "...", "..."]  // 3 paragraphs, district-specific
  },
  "section_red_flags": {
    "heading": "...",
    "items": [                  // 4 bullet points, district-specific red flags
      {"title": "...", "body": "..."},
      {"title": "...", "body": "..."},
      {"title": "...", "body": "..."},
      {"title": "...", "body": "..."}
    ]
  },
  "section_action_steps": {
    "heading": "...",
    "items": ["...", "...", "...", "..."]  // 4 concrete action steps with email addresses where relevant
  },
  "faq_items": [               // 6 FAQ items optimized for AEO / AI Overview citations
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."}
  ],
  "speakable_summary": "..."   // 2-3 sentences. Will be used in speakable schema. Plain text, no HTML.
}

=== AEO REQUIREMENTS ===
- FAQ questions must be exact phrases parents type into Google/AI assistants
  (e.g., "How do I request an ARD meeting in {{ district.name }}?")
- FAQ answers must be 2-4 sentences, self-contained, cite specific law
- The quick_answer_html must start with a direct definition, not a question
- Include at least one FAQ about what to do if the district misses a timeline
- One FAQ must address the 45 school day evaluation timeline specifically

=== SEO REQUIREMENTS ===
- meta_title must include "{{ district.name }}" and "(2026)"
- Primary keyword density target: "{{ district.name }} special education" 3-5x naturally
- Include "ARD meeting", "IEP", "FAPE", "TEA" as secondary keywords
- h1 should NOT repeat the meta_title exactly

Return ONLY the JSON object. No markdown, no code blocks, no explanation.
""".strip()


def build_prompt(district: District) -> str:
    tpl = Template(CONTENT_PROMPT_TEMPLATE)
    return tpl.render(district=district)


# ── HTML page template ────────────────────────────────────────────────────────

PAGE_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
  <title>{{ meta_title }}</title>
  <meta content="{{ meta_description }}" name="description"/>
  <link href="https://www.texasspecialed.com/districts/{{ slug }}/special-ed-updates" rel="canonical"/>
  <meta content="{{ meta_title }}" property="og:title"/>
  <meta content="{{ meta_description }}" property="og:description"/>
  <meta content="https://texasspecialed.com/districts/{{ slug }}/special-ed-updates" property="og:url"/>
  <meta content="article" property="og:type"/>
  <link href="/style.css" rel="stylesheet"/>

  <!-- FAQ Schema (SEO + AEO) -->
  <script type="application/ld+json">{{ faq_schema | tojson }}</script>

  <!-- Article Schema -->
  <script type="application/ld+json">{{ article_schema | tojson }}</script>

  <!-- Speakable Schema (AEO: voice search + AI assistants) -->
  <script type="application/ld+json">{{ speakable_schema | tojson }}</script>

  <!-- BreadcrumbList Schema -->
  <script type="application/ld+json">{{ breadcrumb_schema | tojson }}</script>
</head>
<body>

  <!-- NAVBAR (included via JS/CMS in production) -->

  <!-- HERO -->
  <div class="page-hero">
    <div class="container">
      <nav class="breadcrumb">
        <a href="/">Home</a><span>›</span>
        <a href="/districts/">Districts</a><span>›</span>
        <a href="/districts/{{ slug }}/">{{ district_name }}</a><span>›</span>
        <span style="color:#e2e8f0;">Special Ed Updates</span>
      </nav>
      <span class="update-badge">Updated {{ updated_date }}</span>
      <h1>{{ h1 }}</h1>

      <!-- Silo navigation -->
      <div class="silo-nav" style="background-color:#e9ecef;padding:12px 16px;border-radius:6px;
           margin:20px 0;font-size:14px;display:flex;flex-wrap:wrap;gap:12px;
           align-items:center;border-left:4px solid #6c757d;">
        <strong style="color:#495057;">{{ district_name }} Resources:</strong>
        {% for page in existing_pages %}
        <a href="{{ page.href }}" style="text-decoration:none;color:#0056b3;font-weight:500;">{{ page.label }}</a>
        {% if not loop.last %} • {% endif %}
        {% endfor %}
      </div>

      <!-- AEO Quick Answer Box -->
      <div class="quick-answer" style="background:#f0fdf4;border-left:5px solid #16a34a;
           padding:20px;border-radius:4px;margin:0 0 30px;">
        <p style="font-size:0.75rem;text-transform:uppercase;color:#16a34a;
           font-weight:700;margin:0 0 8px;">⚡ Quick Answer</p>
        {{ quick_answer_html }}
      </div>

      <p class="hero-meta">{{ district_name }} · {{ city }}, Texas · {{ enrollment }} students enrolled</p>
    </div>
  </div>

  <!-- MAIN -->
  <main>
    <div class="container">

      <!-- Alert Banner -->
      <div class="alert-banner">
        <strong>⚠ Heads Up:</strong> If your child's IEP or evaluation timeline has been disrupted,
        see the action steps below or
        <a href="/resources/evaluation-request-template.pdf">download our free evaluation request letter</a>.
      </div>

      <!-- Section 1: What's Happening -->
      <div class="content-section">
        <h2>{{ section_whats_happening.heading }}</h2>
        {% for para in section_whats_happening.paragraphs %}
        <p>{{ para }}</p>
        {% endfor %}
      </div>

      <!-- Section 2: Red Flags -->
      <div class="content-section">
        <h2>{{ section_red_flags.heading }}</h2>
        <ul class="custom-list">
          {% for item in section_red_flags.items %}
          <li><strong>{{ item.title }}:</strong> {{ item.body }}</li>
          {% endfor %}
        </ul>

        <div class="action-box" style="background:#eff6ff;border-left:4px solid #2563eb;
             padding:20px;border-radius:6px;margin:20px 0;">
          <h3>One Action Step You Can Take Today</h3>
          <p>Send a <strong>written, dated request</strong> via email to
          <a href="mailto:{{ sped_contact_email }}">{{ sped_contact_email }}</a>
          requesting a Full and Individual Evaluation — or requesting your child's complete
          educational record under FERPA if they are already receiving services.
          Texas law does not require you to use a district form. A clear written statement
          is legally sufficient.</p>
        </div>
      </div>

      <!-- Section 3: Action Steps -->
      <div class="content-section">
        <h2>{{ section_action_steps.heading }}</h2>
        <div class="action-box" style="background:#eff6ff;border-left:4px solid #2563eb;
             padding:20px;border-radius:6px;margin:20px 0;">
          <ul class="custom-list">
            {% for step in section_action_steps.items %}
            <li>{{ step }}</li>
            {% endfor %}
          </ul>
        </div>
      </div>

      <!-- FAQ Section (AEO optimized) -->
      <div class="faq-section">
        <h2>Frequently Asked Questions: {{ district_name }} Special Education</h2>
        <p>Real questions {{ district_name }} parents are searching for — answered with Texas law in mind.</p>
        <div class="faq-container">
          {% for item in faq_items %}
          <div class="faq-item" style="border-bottom:1px solid #e2e8f0;padding:20px 0;">
            <h3 style="font-size:1.05rem;color:#0f172a;margin-bottom:8px;">{{ item.question }}</h3>
            <p style="color:#374151;margin:0;">{{ item.answer }}</p>
          </div>
          {% endfor %}
        </div>
      </div>

    </div>

    <!-- Related Pages Nav -->
    <nav class="related-pages">
      <div class="container">
        <h2>More {{ district_name }} Resources</h2>
        <div class="page-links">
          <a href="/districts/{{ slug }}/">← {{ district_name }} Hub</a>
          {% for page in existing_pages %}
          <a href="{{ page.href }}">{{ page.label }}</a>
          {% endfor %}
          <a href="/resources/">Parent Resources</a>
        </div>
      </div>
    </nav>
  </main>

</body>
</html>"""


# ── Schema builders ───────────────────────────────────────────────────────────

def build_faq_schema(faq_items: list[dict]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["answer"],
                },
            }
            for item in faq_items
        ],
    }


def build_article_schema(district: District, meta_title: str, meta_description: str) -> dict:
    from datetime import date
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": meta_title,
        "description": meta_description,
        "publisher": {
            "@type": "Organization",
            "name": "TexasSpecialEd.com",
            "url": "https://texasspecialed.com",
        },
        "dateModified": date.today().isoformat(),
        "mainEntityOfPage": f"https://texasspecialed.com/districts/{district.slug}/special-ed-updates",
    }


def build_speakable_schema(district: District, speakable_summary: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": f"{district.name} Special Education Updates",
        "speakable": {
            "@type": "SpeakableSpecification",
            "cssSelector": [".quick-answer", ".faq-section h3"],
        },
        "description": speakable_summary,
    }


def build_breadcrumb_schema(district: District) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://texasspecialed.com"},
            {"@type": "ListItem", "position": 2, "name": "Districts", "item": "https://texasspecialed.com/districts/"},
            {"@type": "ListItem", "position": 3, "name": f"{district.name} Hub", "item": f"https://texasspecialed.com/districts/{district.slug}/"},
            {"@type": "ListItem", "position": 4, "name": "Special Ed Updates", "item": f"https://texasspecialed.com/districts/{district.slug}/special-ed-updates"},
        ],
    }


def slug_to_label(slug: str) -> str:
    labels = {
        "ard-process-guide":         "ARD Guide",
        "evaluation-child-find":     "Evaluations (FIE)",
        "dyslexia-services":         "Dyslexia/504",
        "grievance-dispute-resolution": "Dispute Resolution",
        "leadership-directory":      "Leadership Directory",
    }
    return labels.get(slug, slug.replace("-", " ").title())


# ── Vertex AI client ──────────────────────────────────────────────────────────

def init_vertex():
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    return GenerativeModel(
        MODEL,
        system_instruction=SYSTEM_PROMPT,
        generation_config=GenerationConfig(
            temperature=0.4,      # lower = more factual, less hallucination
            max_output_tokens=3_000,
            response_mime_type="application/json",  # forces JSON output
        ),
    )


def generate_content(model: GenerativeModel, district: District, retries: int = 3) -> dict:
    prompt = build_prompt(district)
    for attempt in range(1, retries + 1):
        try:
            response = model.generate_content(prompt)
            data = json.loads(response.text)
            # Basic validation
            required_keys = [
                "meta_title", "meta_description", "h1", "quick_answer_html",
                "section_whats_happening", "section_red_flags",
                "section_action_steps", "faq_items", "speakable_summary",
            ]
            missing = [k for k in required_keys if k not in data]
            if missing:
                raise ValueError(f"Missing keys in response: {missing}")
            return data
        except Exception as e:
            log.warning(f"[{district.name}] Attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(2 ** attempt)  # exponential backoff
    raise RuntimeError(f"[{district.name}] All {retries} attempts failed.")


# ── Page rendering ────────────────────────────────────────────────────────────

def render_page(district: District, content: dict) -> str:
    from jinja2 import Environment
    from datetime import date

    env = Environment()
    env.filters["tojson"] = lambda v: json.dumps(v, indent=2, ensure_ascii=False)
    tpl = env.from_string(PAGE_HTML_TEMPLATE)

    existing_page_links = [
        {"href": f"/districts/{district.slug}/{slug}", "label": slug_to_label(slug)}
        for slug in district.existing_pages
    ]

    return tpl.render(
        meta_title=content["meta_title"],
        meta_description=content["meta_description"],
        h1=content["h1"],
        slug=district.slug,
        district_name=district.name,
        city=district.city,
        enrollment=district.enrollment,
        sped_contact_email=district.sped_contact_email,
        quick_answer_html=content["quick_answer_html"],
        section_whats_happening=content["section_whats_happening"],
        section_red_flags=content["section_red_flags"],
        section_action_steps=content["section_action_steps"],
        faq_items=content["faq_items"],
        existing_pages=existing_page_links,
        faq_schema=build_faq_schema(content["faq_items"]),
        article_schema=build_article_schema(district, content["meta_title"], content["meta_description"]),
        speakable_schema=build_speakable_schema(district, content["speakable_summary"]),
        breadcrumb_schema=build_breadcrumb_schema(district),
        updated_date=date.today().strftime("%B %-d, %Y"),
    )


# ── Cost estimator ────────────────────────────────────────────────────────────

def estimate_cost(districts: list[District]):
    n = len(districts)
    input_cost  = (AVG_INPUT_TOKENS  * n / 1_000_000) * INPUT_COST_PER_1M
    output_cost = (AVG_OUTPUT_TOKENS * n / 1_000_000) * OUTPUT_COST_PER_1M
    total = input_cost + output_cost
    print(f"\n{'='*55}")
    print(f"  Cost Estimate — Gemini 1.5 Pro")
    print(f"{'='*55}")
    print(f"  Districts to process : {n:>6}")
    print(f"  Avg input tokens     : {AVG_INPUT_TOKENS:>6,}")
    print(f"  Avg output tokens    : {AVG_OUTPUT_TOKENS:>6,}")
    print(f"  Input cost           : ${input_cost:>9.2f}")
    print(f"  Output cost          : ${output_cost:>9.2f}")
    print(f"  ─────────────────────────────────────")
    print(f"  TOTAL ESTIMATED COST : ${total:>9.2f}")
    print(f"\n  Flash alternative    : ~${total/10:.2f}  (use --model flash)")
    print(f"  Remaining budget     : ${1000 - total:.2f} after this run")
    print(f"{'='*55}\n")


# ── Main orchestrator ─────────────────────────────────────────────────────────

def process_district(model: GenerativeModel, district: District) -> bool:
    log.info(f"Generating: {district.name}")
    try:
        content = generate_content(model, district)
        html    = render_page(district, content)

        out_dir = OUTPUT_DIR / district.slug
        out_dir.mkdir(parents=True, exist_ok=True)

        html_path  = out_dir / "special-ed-updates.html"
        json_path  = out_dir / "special-ed-updates.content.json"

        html_path.write_text(html, encoding="utf-8")
        json_path.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")

        log.info(f"  ✓ Written: {html_path}")
        return True
    except Exception as e:
        log.error(f"  ✗ FAILED  {district.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Texas Special Ed — District Page Generator")
    parser.add_argument("--mode", choices=["all", "single", "estimate"], required=True)
    parser.add_argument("--district", help="District name (for --mode single)")
    parser.add_argument("--csv",      help="Path to districts CSV file")
    parser.add_argument("--model",    choices=["pro", "flash"], default="pro",
                        help="Gemini model tier (pro = quality, flash = cost)")
    args = parser.parse_args()

    # Allow model override via CLI
    global MODEL, INPUT_COST_PER_1M, OUTPUT_COST_PER_1M
    if args.model == "flash":
        MODEL = "gemini-1.5-flash"
        INPUT_COST_PER_1M  = 0.35
        OUTPUT_COST_PER_1M = 1.05

    # Load districts
    districts = load_districts_from_csv(args.csv) if args.csv else DISTRICTS

    if args.mode == "estimate":
        estimate_cost(districts)
        return

    if args.mode == "single":
        if not args.district:
            parser.error("--district is required with --mode single")
        districts = [d for d in districts if args.district.lower() in d.name.lower()]
        if not districts:
            log.error(f"District '{args.district}' not found in district list.")
            return

    log.info(f"Starting generation for {len(districts)} district(s).")
    estimate_cost(districts)
    confirm = input("Proceed? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return

    model = init_vertex()

    results = {"success": 0, "failed": 0}
    for district in tqdm(districts, desc="Generating pages"):
        ok = process_district(model, district)
        results["success" if ok else "failed"] += 1
        time.sleep(0.5)  # gentle rate limiting

    print(f"\n{'='*40}")
    print(f"  ✓ Success: {results['success']}")
    print(f"  ✗ Failed : {results['failed']}")
    print(f"  Output   : {OUTPUT_DIR.resolve()}")
    print(f"{'='*40}")


if __name__ == "__main__":
    main()