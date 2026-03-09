"""
generate_fie_html_pages.py
--------------------------
Generates a "What is an FIE?" HTML page for each of the bottom 70 Texas
school districts (by enrollment), matching the exact layout and structure
of the Houston ISD FIE page.

Claude API is used ONLY for the district-specific written content sections.
All CSS, nav, sidebar, footer, and scripts are hard-coded from the template.

Usage:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python generate_fie_html_pages.py

Output:
    ./fie_html_pages/what-is-an-fie-{slug}.html
    e.g. fie_html_pages/what-is-an-fie-katy-isd.html
"""

import os
import re
import json
import time
import anthropic

# ── District data ─────────────────────────────────────────────────────────────

DISTRICTS = [
    {"name": "Alvin ISD", "enrollment": 29320, "region": "Houston"},
    {"name": "Amarillo ISD", "enrollment": 29729, "region": "Panhandle"},
    {"name": "Northwest ISD", "enrollment": 29660, "region": "Fort Worth"},
    {"name": "Comal ISD", "enrollment": 29480, "region": "San Antonio"},
    {"name": "Edinburg CISD", "enrollment": 29450, "region": "Rio Grande Valley"},
    {"name": "Midland ISD", "enrollment": 28340, "region": "West Texas"},
    {"name": "Judson ISD", "enrollment": 25670, "region": "San Antonio"},
    {"name": "Pflugerville ISD", "enrollment": 25480, "region": "Austin"},
    {"name": "Carrollton-Farmers Branch ISD", "enrollment": 25120, "region": "DFW"},
    {"name": "Lubbock ISD", "enrollment": 24329, "region": "South Plains"},
    {"name": "Hays CISD", "enrollment": 23450, "region": "Austin"},
    {"name": "La Joya ISD", "enrollment": 23998, "region": "Rio Grande Valley"},
    {"name": "Eagle Mountain-Saginaw ISD", "enrollment": 23870, "region": "Fort Worth"},
    {"name": "Goose Creek CISD", "enrollment": 23810, "region": "Houston"},
    {"name": "McKinney ISD", "enrollment": 23320, "region": "DFW"},
    {"name": "Tomball ISD", "enrollment": 22530, "region": "Houston"},
    {"name": "Birdville ISD", "enrollment": 22180, "region": "Fort Worth"},
    {"name": "Allen ISD", "enrollment": 21790, "region": "DFW"},
    {"name": "Hurst-Euless-Bedford ISD", "enrollment": 21890, "region": "Fort Worth"},
    {"name": "Laredo ISD", "enrollment": 20592, "region": "Laredo"},
    {"name": "McAllen ISD", "enrollment": 20095, "region": "Rio Grande Valley"},
    {"name": "Wylie ISD", "enrollment": 19530, "region": "DFW"},
    {"name": "New Caney ISD", "enrollment": 18540, "region": "Houston"},
    {"name": "Rockwall ISD", "enrollment": 18650, "region": "DFW"},
    {"name": "Harlingen CISD", "enrollment": 17160, "region": "Rio Grande Valley"},
    {"name": "Crowley ISD", "enrollment": 16920, "region": "Fort Worth"},
    {"name": "Forney ISD", "enrollment": 16840, "region": "DFW"},
    {"name": "Weslaco ISD", "enrollment": 16040, "region": "Rio Grande Valley"},
    {"name": "Bryan ISD", "enrollment": 15530, "region": "Central Texas"},
    {"name": "Schertz-Cibolo-Universal City ISD", "enrollment": 15590, "region": "San Antonio"},
    {"name": "Magnolia ISD", "enrollment": 14580, "region": "Houston"},
    {"name": "Belton ISD", "enrollment": 14140, "region": "Central Texas"},
    {"name": "Abilene ISD", "enrollment": 14890, "region": "West Texas"},
    {"name": "College Station ISD", "enrollment": 14080, "region": "Central Texas"},
    {"name": "Mission CISD", "enrollment": 14020, "region": "Rio Grande Valley"},
    {"name": "Donna ISD", "enrollment": 13240, "region": "Rio Grande Valley"},
    {"name": "Coppell ISD", "enrollment": 13180, "region": "DFW"},
    {"name": "Grapevine-Colleyville ISD", "enrollment": 13120, "region": "DFW"},
    {"name": "San Angelo ISD", "enrollment": 13120, "region": "West Texas"},
    {"name": "Bastrop ISD", "enrollment": 12940, "region": "Austin"},
    {"name": "Wichita Falls ISD", "enrollment": 12980, "region": "North Texas"},
    {"name": "Dickinson ISD", "enrollment": 12340, "region": "Houston"},
    {"name": "Burleson ISD", "enrollment": 12740, "region": "Fort Worth"},
    {"name": "Lake Travis ISD", "enrollment": 11640, "region": "Austin"},
    {"name": "East Central ISD", "enrollment": 11040, "region": "San Antonio"},
    {"name": "Del Valle ISD", "enrollment": 11240, "region": "Austin"},
    {"name": "Clint ISD", "enrollment": 10340, "region": "El Paso"},
    {"name": "Sherman ISD", "enrollment": 10650, "region": "North Texas"},
    {"name": "Georgetown ISD", "enrollment": 13670, "region": "Austin"},
    {"name": "Montgomery ISD", "enrollment": 9870, "region": "Houston"},
    {"name": "Royse City ISD", "enrollment": 9430, "region": "DFW"},
    {"name": "Rio Grande City Grulla ISD", "enrollment": 9480, "region": "Rio Grande Valley"},
    {"name": "San Benito CISD", "enrollment": 9120, "region": "Rio Grande Valley"},
    {"name": "Waller ISD", "enrollment": 9120, "region": "Houston"},
    {"name": "Little Elm ISD", "enrollment": 8920, "region": "DFW"},
    {"name": "Midway ISD", "enrollment": 8420, "region": "Central Texas"},
    {"name": "Temple ISD", "enrollment": 8340, "region": "Central Texas"},
    {"name": "San Marcos CISD", "enrollment": 8210, "region": "Austin"},
    {"name": "Longview ISD", "enrollment": 8050, "region": "East Texas"},
    {"name": "Eanes ISD", "enrollment": 7890, "region": "Austin"},
    {"name": "Texas City ISD", "enrollment": 7870, "region": "Houston"},
    {"name": "Seguin ISD", "enrollment": 7140, "region": "San Antonio"},
    {"name": "Texarkana ISD", "enrollment": 7230, "region": "East Texas"},
    {"name": "Copperas Cove ISD", "enrollment": 7980, "region": "Central Texas"},
    {"name": "Crosby ISD", "enrollment": 6680, "region": "Houston"},
    {"name": "Princeton ISD", "enrollment": 8720, "region": "DFW"},
    {"name": "Melissa ISD", "enrollment": 6250, "region": "DFW"},
    {"name": "Friendswood ISD", "enrollment": 5890, "region": "Houston"},
    {"name": "Channelview ISD", "enrollment": 9320, "region": "Houston"},
    {"name": "Victoria ISD", "enrollment": 12890, "region": "Coastal Bend"},
    {"name": "Waco ISD", "enrollment": 14240, "region": "Central Texas"},
    {"name": "Beaumont ISD", "enrollment": 16520, "region": "Southeast Texas"},
    {"name": "Tyler ISD", "enrollment": 17890, "region": "East Texas"},
    {"name": "Santa Fe ISD", "enrollment": 4230, "region": "Houston"},
    {"name": "Grand Prairie ISD", "enrollment": 26638, "region": "DFW"},
]

sorted_districts = sorted(DISTRICTS, key=lambda d: d["enrollment"])
bottom_70 = sorted_districts[:70]

# ── Helpers ───────────────────────────────────────────────────────────────────

def to_slug(name):
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = slug.strip()
    slug = re.sub(r"\s+", "-", slug)
    return slug

# ── Claude prompt → returns structured JSON ───────────────────────────────────

CONTENT_PROMPT = """You are a content writer for texasspecialed.com, a Texas special education parent resource site.

Generate district-specific content for a "What Is an FIE?" page for **{DISTRICT_NAME}** in the **{REGION}** region of Texas ({ENROLLMENT} students enrolled).

Return ONLY a valid JSON object with NO markdown fences, NO preamble. The object must have exactly these keys:

{{
  "meta_description": "155-char SEO meta description mentioning FIE, {DISTRICT_NAME}, Texas, parent rights",

  "quick_answer": "2–3 sentence featured-snippet answer starting with 'An FIE — Full Individual Evaluation — is the comprehensive testing process {DISTRICT_NAME} must complete...' Mention the 45-school-day deadline and 15-school-day response window.",

  "intro_p1": "Opening paragraph (3–4 sentences) welcoming parents in {REGION} navigating special ed at {DISTRICT_NAME} for the first time. Explain what FIE stands for and why it matters.",
  "intro_p2": "Second paragraph (2–3 sentences) referencing IDEA and Texas Education Code Chapter 29. Emphasize this is the legal foundation.",
  "pull_quote": "One powerful italic pull-quote sentence about parent power in the FIE process (no quotes characters, just the sentence).",

  "fie_vs_fiie_items": [
    {{"title": "FIE — Full Individual Evaluation", "body": "explanation..."}},
    {{"title": "FIIE — Full Individual and Initial Evaluation", "body": "explanation mentioning the exact phrase to use in the request letter..."}},
    {{"title": "Triennial Re-Evaluation", "body": "explanation of the 3-year re-eval rule..."}}
  ],

  "timeline_steps": [
    {{"badge": "DAY 0 — YOU ACT", "title": "Submit Your Written Request", "body": "who to email and what the request starts..."}},
    {{"badge": "WITHIN 15 SCHOOL DAYS", "title": "{DISTRICT_NAME} Must Respond in Writing", "body": "what the district must send back..."}},
    {{"badge": "YOU SIGN THE CONSENT FORM", "title": "45-Day Testing Clock Begins", "body": "what happens once consent is signed..."}},
    {{"badge": "WITHIN 30 CALENDAR DAYS OF REPORT", "title": "ARD Eligibility Meeting Must Be Held", "body": "what happens at the ARD and what comes next..."}}
  ],

  "warning_box": "One ⚠️ warning paragraph about school-day timing (summer, holidays) and why to submit early.",

  "action_steps": [
    {{"title": "Use the Correct Language", "body": "exact wording to use in the request letter..."}},
    {{"title": "Address It to the Right People", "body": "who to CC at {DISTRICT_NAME}..."}},
    {{"title": "Send via Email for a Time-Stamped Record", "body": "why email matters legally..."}},
    {{"title": "Keep a Paper Trail", "body": "how to document everything..."}}
  ],

  "fie_covers_items": [
    {{"title": "Academic Achievement", "body": "reading, writing, math testing detail..."}},
    {{"title": "Cognitive Ability / IQ", "body": "what cognitive testing covers..."}},
    {{"title": "Speech and Language", "body": "when and how speech is assessed..."}},
    {{"title": "Social-Emotional and Behavioral Assessment", "body": "what behavioral assessment involves..."}},
    {{"title": "Occupational Therapy / Fine Motor Skills", "body": "when OT is included..."}},
    {{"title": "Adaptive Behavior", "body": "when adaptive behavior is assessed..."}}
  ],

  "urgent_cta_text": "2-sentence warning paragraph: Is {DISTRICT_NAME} delaying or refusing the FIE? Mention RTI delay tactic and Child Find violation.",

  "after_fie_p1": "Paragraph explaining parents must receive the written report BEFORE the ARD meeting, and their right to stop and reschedule if handed it at the table.",

  "review_checklist": [
    "Did the evaluation address all areas you specifically requested?",
    "Are test scores explained in plain language — not buried in technical jargon?",
    "Does the report include a clear eligibility recommendation and the specific disability category?",
    "Are there concrete, actionable recommendations the ARD committee can use to build IEP goals?"
  ],

  "iee_p1": "Paragraph explaining the right to an IEE if the parent disagrees with the FIE, mentioning {DISTRICT_NAME} by name.",
  "iee_p2": "Follow-up paragraph with the exact written statement a parent should send to request an IEE at public expense.",

  "faq_items": [
    {{"q": "What is an FIE in {DISTRICT_NAME}?", "a": "comprehensive answer..."}},
    {{"q": "How do I request an FIE from {DISTRICT_NAME}?", "a": "step-by-step answer with exact phrase to use..."}},
    {{"q": "How long does {DISTRICT_NAME} have to complete an FIE?", "a": "45 school days detail..."}},
    {{"q": "Can {DISTRICT_NAME} refuse to evaluate my child?", "a": "prior written notice + RTI tactic answer..."}},
    {{"q": "What does an FIE cover in Texas?", "a": "all areas of suspected disability..."}},
    {{"q": "What is the difference between an FIE and an FIIE in Texas?", "a": "FIE vs FIIE distinction..."}},
    {{"q": "What happens after the FIE is completed in {DISTRICT_NAME}?", "a": "report + 30-day ARD timeline..."}},
    {{"q": "What is an IEE and when can I request one?", "a": "IEE rights after disagreement with FIE..."}}
  ]
}}

All text must be parent-friendly, warm, and specific to {DISTRICT_NAME} in the {REGION} region. Do NOT include any markdown, HTML tags, or code fences in the JSON values — plain text only."""


# ── HTML template builder ─────────────────────────────────────────────────────

def build_faq_schema(district_name, faq_items):
    entities = []
    for item in faq_items:
        entities.append({
            "@type": "Question",
            "name": item["q"],
            "acceptedAnswer": {"@type": "Answer", "text": item["a"]}
        })
    return json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities}, indent=3)


def build_breadcrumb_schema(district_name, slug):
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://texasspecialed.com"},
            {"@type": "ListItem", "position": 2, "name": "Districts", "item": "https://texasspecialed.com/districts/"},
            {"@type": "ListItem", "position": 3, "name": district_name, "item": f"https://texasspecialed.com/districts/{slug}/"},
            {"@type": "ListItem", "position": 4, "name": f"What Is an FIE in {district_name}?",
             "item": f"https://texasspecialed.com/districts/{slug}/what-is-an-fie-{slug}"}
        ]
    }, indent=3)


def render_iep_list(items):
    html = '<ul class="iep-list">\n'
    for item in items:
        html += f"""<li><div><strong>{item['title']}</strong>{item['body']}</div></li>\n"""
    html += '</ul>\n'
    return html


def render_timeline(steps, district_name):
    html = '<ul class="timeline">\n'
    for step in steps:
        html += f"""<li>
<span class="day-badge">{step['badge']}</span>
<strong>{step['title']}</strong>
<span>{step['body']}</span>
</li>\n"""
    html += '</ul>\n'
    return html


def render_action_steps(steps):
    html = '<ol>\n'
    for step in steps:
        html += f'<li><strong>{step["title"]}:</strong> {step["body"]}</li>\n'
    html += '</ol>\n'
    return html


def render_faq(faq_items):
    html = ''
    for item in faq_items:
        html += f"""<details>
<summary>{item['q']} <span style="font-size:1.3rem;color:#64748b;">+</span></summary>
<p>{item['a']}</p>
</details>\n"""
    return html


def build_html(district, content):
    name = district["name"]
    slug = to_slug(name)
    region = district["region"]

    faq_schema = build_faq_schema(name, content["faq_items"])
    breadcrumb_schema = build_breadcrumb_schema(name, slug)

    iep_list_fie_vs_fiie = render_iep_list(content["fie_vs_fiie_items"])
    timeline_html = render_timeline(content["timeline_steps"], name)
    action_steps_html = render_action_steps(content["action_steps"])
    fie_covers_html = render_iep_list(content["fie_covers_items"])
    faq_html = render_faq(content["faq_items"])

    review_items = "".join(
        f'<li style="margin-bottom:10px;">{item}</li>\n'
        for item in content["review_checklist"]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-GVLPE273XH"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-GVLPE273XH');
</script>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>FIE Evaluation Guide for {name} Parents - Texas</title>
<meta content="{content['meta_description']}" name="description"/>
<link href="https://www.texasspecialed.com/districts/{slug}/what-is-an-fie-{slug}" rel="canonical"/>
<script type="application/ld+json">
{faq_schema}
</script>
<script type="application/ld+json">
{breadcrumb_schema}
</script>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&family=Lora:wght@400;600;700&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet"/>
<link href="/style.css" rel="stylesheet"/>
<style>
   body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f8fafc; }}
   .container {{ max-width: 1100px; margin: 0 auto; padding: 20px; }}
   .site-header {{ background: #fff; padding: 15px 20px; border-bottom: 1px solid #ddd; }}
   h1 {{ font-size: 2.2rem; margin-top: 10px; font-family: 'Lora', serif; color: #0a2342; }}
   .layout-grid {{ display: grid; grid-template-columns: 1fr; gap: 50px; margin-top: 30px; align-items: start; }}
   @media (min-width: 1024px) {{ .layout-grid {{ grid-template-columns: 1fr 380px; }} }}
   .sidebar-column {{ position: sticky; top: 20px; z-index: 10; }}
   .content-column {{ min-width: 0; font-family: 'Source Sans 3', sans-serif; font-size: 17px; line-height: 1.75; color: #1a1a2e; background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
   .content-column h2 {{ font-family: 'Lora', serif; font-size: 1.6rem; font-weight: 700; color: #0a2342; margin: 2.5rem 0 1rem; padding-top: 1.5rem; border-top: 2px solid #e8f0fe; }}
   .content-column h3 {{ font-family: 'Lora', serif; font-size: 1.2rem; font-weight: 600; color: #1e3a8a; margin: 1.75rem 0 0.75rem; }}
   .content-column p {{ margin: 0 0 1.25rem; }}
   .timeline {{ list-style: none; padding: 0; margin: 2rem 0; border-left: 3px solid #1a56db; }}
   .timeline li {{ position: relative; padding: 0 0 28px 32px; font-size: 16px; }}
   .timeline li:last-child {{ padding-bottom: 0; }}
   .timeline li::before {{ content: ''; position: absolute; left: -9px; top: 5px; width: 15px; height: 15px; border-radius: 50%; background: #1a56db; border: 3px solid #fff; box-shadow: 0 0 0 2px #1a56db; }}
   .timeline li strong {{ display: block; font-size: 1rem; color: #0a2342; margin-bottom: 4px; }}
   .timeline li span {{ color: #475569; line-height: 1.6; }}
   .day-badge {{ display: inline-block; background: #1a56db; color: #fff; font-size: 11px; font-weight: 700; padding: 2px 10px; border-radius: 50px; margin-bottom: 6px; letter-spacing: 0.05em; }}
   .pull-quote {{ border-left: 4px solid #1a56db; margin: 2rem 0; padding: 20px 24px; background: #f8fbff; border-radius: 0 8px 8px 0; font-size: 1.15rem; font-style: italic; color: #1e3a8a; line-height: 1.6; }}
   .action-steps {{ background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 28px 32px; margin: 2.5rem 0; }}
   .action-steps h3 {{ border: none; padding: 0; margin-top: 0; font-size: 1.35rem; color: #166534; }}
   .action-steps ol {{ padding-left: 1.4rem; margin: 0; font-size: 17px; }}
   .action-steps li {{ margin-bottom: 14px; line-height: 1.65; color: #166534; }}
   .action-steps strong {{ color: #14532d; }}
   .warning-box {{ background: #fef2f2; border-left: 4px solid #ef4444; border-radius: 6px; padding: 20px 24px; margin: 2rem 0; }}
   .warning-box p {{ margin: 0; color: #7f1d1d; font-size: 16px; }}
   .iep-list {{ list-style: none; padding: 0; margin: 1.5rem 0 2.5rem; }}
   .iep-list li {{ display: flex; gap: 20px; padding: 20px 0; border-bottom: 1px solid #e8f0fe; font-size: 17px; }}
   .iep-list li:last-child {{ border-bottom: none; }}
   .iep-list li::before {{ content: "✓"; background: #1a56db; color: #fff; font-weight: 700; font-size: 14px; border-radius: 50%; min-width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px; }}
   .iep-list strong {{ display: block; margin-bottom: 6px; color: #0f172a; font-size: 1.1rem; }}
   .section-divider {{ text-align: center; color: #9ab0cc; font-size: 24px; margin: 3rem 0; letter-spacing: 0.4em; }}
   .inline-cta {{ background: #f8fbff; border: 1px solid #dbe8fb; border-left: 4px solid #1a56db; border-radius: 6px; padding: 24px; margin: 2.5rem 0; display: flex; gap: 16px; align-items: flex-start; }}
   .inline-cta.urgent {{ background: #fef2f2; border-color: #fecaca; border-left-color: #ef4444; }}
   .inline-cta .cta-icon {{ font-size: 2.2rem; line-height: 1; flex-shrink: 0; }}
   .inline-cta h3 {{ margin: 0 0 8px; font-family: 'Lora', serif; font-size: 1.3rem; color: #0a2342; border: none; padding: 0; }}
   .inline-cta p {{ margin: 0 0 16px; font-size: 16px; color: #475569; }}
   .btn-primary {{ background: #1a56db; color: #fff; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 15px; display: inline-block; transition: background 0.2s; }}
   .btn-primary:hover {{ background: #1e3a8a; color: #fff; }}
   .btn-primary.red-btn {{ background: #ef4444; color: #fff; }}
   .btn-primary.red-btn:hover {{ background: #dc2626; }}
   .related-pages-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px 28px; margin: 2.5rem 0; }}
   .related-pages-box h3 {{ font-family: 'Lora', serif; font-size: 1.1rem; color: #0a2342; margin: 0 0 14px; padding: 0; border: none; }}
   .related-pages-box ul {{ list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: 10px; }}
   .related-pages-box ul li a {{ display: inline-block; background: #fff; border: 1px solid #bfdbfe; color: #1d4ed8; text-decoration: none; padding: 8px 16px; border-radius: 4px; font-size: 14px; font-weight: 600; font-family: 'DM Sans', sans-serif; transition: 0.2s; }}
   .related-pages-box ul li a:hover {{ background: #1a56db; color: #fff; border-color: #1a56db; }}
   .faq-section {{ margin-top: 50px; }}
   .faq-section h2 {{ font-size: 1.6rem; margin-bottom: 5px; font-family: 'Lora', serif; border: none; padding: 0; }}
   .faq-section > p {{ color: #64748b; margin-bottom: 20px; font-family: 'DM Sans', sans-serif; }}
   .faq-section details {{ border-bottom: 1px solid #e2e8f0; padding: 16px 0; }}
   .faq-section summary {{ font-weight: 600; cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: center; font-family: 'Source Sans 3', sans-serif; font-size: 1.05rem; color: #0f172a; }}
   .faq-section summary::-webkit-details-marker {{ display: none; }}
   .faq-section details p {{ margin: 12px 0 0; color: #475569; line-height: 1.7; font-family: 'Source Sans 3', sans-serif; }}
   .offers-container {{ display: flex; flex-direction: column; gap: 24px; margin-top: 50px; }}
   .sales-card {{ background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 36px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15); }}
   .sales-card.slate-theme {{ background: linear-gradient(135deg, #334155 0%, #0f172a 100%); }}
   .sales-card .badge {{ background: #d4af37; color: #0f172a; padding: 6px 16px; border-radius: 50px; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; }}
   .sales-card h3 {{ margin: 20px 0 12px; color: #fff; font-size: 1.6rem; font-family: 'Lora', serif; }}
   .sales-card p {{ color: #e2e8f0; margin: 0 auto 24px; font-size: 1.05rem; line-height: 1.6; max-width: 90%; }}
   .sales-card a {{ background: #d4af37; color: #0f172a; padding: 16px 32px; text-decoration: none; border-radius: 6px; font-weight: 700; font-size: 1.1rem; display: inline-block; transition: 0.2s; }}
   .sidebar-form {{ width: 100%; background: #fdfaf5; border: 1px solid #d6cbbf; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.12); overflow: hidden; }}
   .sidebar-form .sf-header {{ background: #1a1410; padding: 24px 24px 20px; border-bottom: 3px solid #b8963a; }}
   .sidebar-form .sf-eyebrow {{ font-size: 10px; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; color: #b8963a; margin: 0 0 6px; font-family: 'DM Sans', sans-serif; }}
   .sidebar-form .sf-name {{ font-family: 'Cormorant Garamond', serif; font-size: 26px; font-weight: 400; color: #f5f0e8; margin: 0; line-height: 1.1; }}
   .sidebar-form .sf-name em {{ color: #d4ad5a; font-style: italic; }}
   .sidebar-form .sf-body {{ padding: 24px; }}
   .sidebar-form .sf-empathy {{ font-family: 'Cormorant Garamond', serif; font-size: 20px; font-weight: 600; color: #1a1410; margin: 0 0 8px; }}
   .sidebar-form .sf-sub {{ font-size: 14px; color: #6b5f53; margin: 0 0 20px; font-family: 'DM Sans', sans-serif; line-height: 1.5; }}
   .sidebar-form .sf-group {{ margin-bottom: 16px; }}
   .sidebar-form label {{ display: block; font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #6b5f53; margin-bottom: 6px; font-family: 'DM Sans', sans-serif; }}
   .sidebar-form input, .sidebar-form select {{ width: 100%; border: 1px solid #d6cbbf; padding: 12px; font-size: 14px; font-family: 'DM Sans', sans-serif; border-radius: 4px; box-sizing: border-box; }}
   .sidebar-form input:focus, .sidebar-form select:focus {{ outline: none; border-color: #b8963a; }}
   .sidebar-form .sf-btn {{ width: 100%; background: #1a1410; color: #d4ad5a; border: none; padding: 16px; font-size: 12px; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; cursor: pointer; border-radius: 4px; transition: 0.2s; font-family: 'DM Sans', sans-serif; margin-top: 8px; }}
   .sidebar-form .sf-btn:hover {{ background: #b8963a; color: #1a1410; }}
   .sidebar-form .sf-trust {{ text-align: center; margin-top: 14px; font-size: 12px; color: #9a8f86; font-family: 'DM Sans', sans-serif; display: flex; align-items: center; justify-content: center; gap: 6px; }}
   .sidebar-form .sf-footer {{ background: #f0ebe3; padding: 12px 24px; text-align: center; font-size: 11px; color: #9a8f86; font-family: 'DM Sans', sans-serif; border-top: 1px solid #d6cbbf; }}
   .sidebar-ad-box {{ background: linear-gradient(135deg, #1c1917 0%, #44403c 100%); border-radius: 10px; padding: 28px 24px; text-align: center; margin-top: 28px; color: #fff; }}
   .sidebar-ad-box .badge {{ background: #d4af37; color: #0f172a; padding: 5px 14px; border-radius: 50px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; display: inline-block; margin-bottom: 14px; }}
   .sidebar-ad-box h3 {{ font-family: 'Lora', serif; font-size: 1.3rem; color: #fff; margin: 0 0 10px; }}
   .sidebar-ad-box p {{ color: #d6cbbf; font-size: 14px; line-height: 1.55; margin: 0 0 18px; font-family: 'DM Sans', sans-serif; }}
   .sidebar-ad-box a {{ display: block; background: #d4af37; color: #0f172a; text-decoration: none; padding: 14px; border-radius: 4px; font-weight: 700; font-size: 13px; transition: 0.2s; font-family: 'DM Sans', sans-serif; }}
</style>
</head>
<body>
<!-- NAVBAR -->
<header class="site-header">
<nav aria-label="Main navigation" class="navbar" role="navigation">
<div class="nav-container">
<div class="nav-logo">
<a aria-label="Texas Special Ed Home" class="text-logo" href="/">Texas <em>Special Ed</em></a>
</div>
<button aria-expanded="false" aria-label="Toggle menu" class="mobile-menu-toggle">
<span class="hamburger"></span><span class="hamburger"></span><span class="hamburger"></span>
</button>
<ul class="nav-menu">
<li class="nav-item"><a class="nav-link" href="/">Home</a></li>
<li class="nav-item dropdown">
<a aria-haspopup="true" class="nav-link dropdown-toggle" href="/districts/index.html">Districts <span class="dropdown-arrow">▼</span></a>
<ul class="dropdown-menu">
<li><a href="/districts/index.html"><strong>Directory: All Districts</strong></a></li>
<li class="dropdown-divider"></li>
<li><a href="/districts/houston-isd/index.html">Houston ISD</a></li>
<li><a href="/districts/dallas-isd/index.html">Dallas ISD</a></li>
<li><a href="/districts/austin-isd/index.html">Austin ISD</a></li>
<li><a href="/districts/cypress-fairbanks-isd/index.html">Cypress-Fairbanks ISD</a></li>
<li><a href="/districts/katy-isd/index.html">Katy ISD</a></li>
<li><a href="/districts/frisco-isd/index.html">Frisco ISD</a></li>
<li><a href="/districts/plano-isd/index.html">Plano ISD</a></li>
<li><a href="/districts/round-rock-isd/index.html">Round Rock ISD</a></li>
<li class="dropdown-divider"></li>
<li><a class="view-all-link" href="/districts/index.html">View All 120+ Districts →</a></li>
</ul>
</li>
<li class="nav-item"><a class="nav-link" href="/resources/index.html">Parent Resources</a></li>
<li class="nav-item"><a class="nav-link" href="/blog/index.html">Blog</a></li>
<li class="nav-item"><a class="nav-link" href="/about/index.html">About</a></li>
<li class="nav-item nav-cta">
<a class="btn-outline" href="/resources/ard-checklist.pdf" target="_blank">Free ARD Checklist</a>
</li>
<li class="nav-item nav-cta" style="margin-left:8px;">
<a href="/resources/Iep-letter" style="background:#d4af37;color:#0f172a;padding:10px 18px;border-radius:4px;font-weight:700;font-size:14px;text-decoration:none;font-family:'DM Sans',sans-serif;white-space:nowrap;">Get Your Letter — $25</a>
</li>
</ul>
</div>
</nav>
</header>
<!-- MAIN -->
<main class="container">
<h1>What Is an FIE (Full Individual Evaluation) in {name}? A Texas Parent's Guide</h1>
<!-- Breadcrumb -->
<nav style="font-size:14px;color:#64748b;margin:8px 0 20px;font-family:'DM Sans',sans-serif;">
<a href="/" style="color:#2563eb;text-decoration:none;">Home</a> ›
<a href="/districts/index.html" style="color:#2563eb;text-decoration:none;">Districts</a> ›
<a href="/districts/{slug}/index.html" style="color:#2563eb;text-decoration:none;">{name}</a> ›
<span>What Is an FIE?</span>
</nav>
<!-- SILO NAV -->
<div class="silo-nav" style="background-color:#e9ecef;padding:14px 20px;border-radius:8px;margin:0 0 30px;font-size:15px;font-family:'DM Sans',sans-serif;display:flex;flex-wrap:wrap;gap:16px;align-items:center;border-left:4px solid #6c757d;">
<strong style="color:#334155;">{name} Resources:</strong>
<a href="/districts/{slug}/index.html" style="text-decoration:none;color:#2563eb;font-weight:500;">District Home</a> •
<a href="/districts/{slug}/ard-process-guide.html" style="text-decoration:none;color:#2563eb;font-weight:500;">ARD Guide</a> •
<a href="/districts/{slug}/evaluation-child-find.html" style="text-decoration:none;color:#2563eb;font-weight:500;">Evaluations (FIE)</a> •
<a href="/districts/{slug}/what-is-an-fie-{slug}.html" style="text-decoration:none;color:#2563eb;font-weight:800;">What Is an FIE?</a> •
<a href="/districts/{slug}/dyslexia-services.html" style="text-decoration:none;color:#2563eb;font-weight:500;">Dyslexia / 504</a> •
<a href="/districts/{slug}/grievance-dispute-resolution.html" style="text-decoration:none;color:#2563eb;font-weight:500;">Dispute Resolution</a> •
<a href="/districts/{slug}/leadership-directory.html" style="text-decoration:none;color:#2563eb;font-weight:500;">Staff Directory</a>
</div>
<!-- QUICK ANSWER -->
<div style="background:#f0fdf4;border-left:5px solid #16a34a;padding:24px;border-radius:6px;margin:0 0 30px;box-shadow:0 2px 4px rgba(0,0,0,0.02);">
<p style="font-size:0.8rem;text-transform:uppercase;color:#16a34a;font-weight:800;margin:0 0 10px;letter-spacing:0.05em;">⚡ Quick Answer</p>
<p style="margin:0;font-size:1.05rem;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.6;">{content['quick_answer']}</p>
</div>
<!-- 70/30 GRID -->
<div class="layout-grid">
<!-- LEFT: CONTENT -->
<article class="content-column">
<h2 style="border-top:none;margin-top:0;padding-top:0;">FIE Meaning: The Full Individual Evaluation Explained</h2>
<p>{content['intro_p1']}</p>
<p>{content['intro_p2']}</p>
<div class="pull-quote">{content['pull_quote']}</div>

<h2>FIE vs. FIIE: What's the Difference?</h2>
<p>You'll see both terms used in {name} documents. Here's the simple breakdown:</p>
{iep_list_fie_vs_fiie}

<div class="section-divider">· · ·</div>
<div class="inline-cta">
<div class="cta-icon">🛡️</div>
<div>
<h3>Not sure how to start the process?</h3>
<p>Many {name} parents don't realize that a verbal conversation with a teacher does NOT start the legal clock. A local advocate can help you draft the right written request — at no cost to you for an initial call.</p>
<a class="btn-primary" href="#leadCaptureForm" onclick="document.querySelector('#leadCaptureForm').scrollIntoView({{behavior:'smooth'}});return false;">Get a Free 15-Minute Call</a>
</div>
</div>
<div class="section-divider">· · ·</div>

<h2>The FIE Timeline in {name} — Step by Step</h2>
<p>Texas law is strict about timelines. Here is exactly what must happen — and when — after you formally request an FIE from {name}:</p>
{timeline_html}

<div class="warning-box">
<p>{content['warning_box']}</p>
</div>
<div class="section-divider">· · ·</div>

<div class="action-steps">
<h3>How to Request an FIE from {name} — The Right Way</h3>
<p style="margin-bottom:15px;font-size:17px;color:#166534;">Do not rely on informal emails or phone calls. A properly worded written request forces {name} into a strict legal timeline. Here's how to do it correctly:</p>
{action_steps_html}
</div>

<h2>What Does an FIE Evaluate? All Areas of Suspected Disability</h2>
<p>A legally complete FIE is not a single IQ test. {name} must assess every area where a disability is suspected. Here is what a comprehensive evaluation must include:</p>
{fie_covers_html}
<p><em style="color:#64748b;font-size:0.95rem;">Note: If the district's FIE omits an area you specifically requested in writing, that is a violation you have the right to challenge — either by requesting an IEE or filing a TEA State Complaint.</em></p>

<div class="inline-cta urgent">
<div class="cta-icon">🛑</div>
<div>
<h3>Is {name} delaying or refusing your FIE?</h3>
<p>{content['urgent_cta_text']}</p>
<a class="btn-primary red-btn" href="#leadCaptureForm" onclick="document.querySelector('#leadCaptureForm').scrollIntoView({{behavior:'smooth'}});return false;">Get Help Forcing Compliance</a>
</div>
</div>
<div class="section-divider">· · ·</div>

<h2>What Happens After the FIE in {name}?</h2>
<p>{content['after_fie_p1']}</p>
<h3>How to Review the FIE Report</h3>
<p>When the report arrives, look for these four things before signing anything:</p>
<ul style="padding-left:1.4rem;margin-bottom:1.5rem;">
{review_items}
</ul>
<h3>Your Right to an Independent Educational Evaluation (IEE)</h3>
<p>{content['iee_p1']}</p>
<p>{content['iee_p2']}</p>

<div class="related-pages-box">
<h3>📂 Related {name} Guides</h3>
<ul>
<li><a href="/districts/{slug}/evaluation-child-find.html">Full Evaluation &amp; Child Find Guide</a></li>
<li><a href="/districts/{slug}/ard-process-guide.html">The ARD Meeting After Your FIE</a></li>
<li><a href="/districts/{slug}/dyslexia-services.html">Dyslexia Testing: 504 vs. IEP</a></li>
<li><a href="/districts/{slug}/grievance-dispute-resolution.html">If {name} Refuses to Evaluate</a></li>
</ul>
</div>
<div class="section-divider">· · ·</div>

<!-- PREMIUM OFFERS -->
<div class="offers-container">
<div class="sales-card slate-theme">
<span class="badge" style="background:#cbd5e1;color:#0f172a;">After Your FIE — Know What to Ask For</span>
<h3>The Accommodations Encyclopedia</h3>
<p>Once the evaluation is done, stop guessing what supports to request at the ARD. Our evidence-based "If/Then" decision matrix matches your child's diagnosis to research-backed IEP accommodations and services.</p>
<a href="https://buy.stripe.com/3cIcN43JX9Yc7FZ6ixbbG0F" style="background:#cbd5e1;color:#0f172a;" target="_blank">Get the Encyclopedia — $27</a>
</div>
<div style="background-color:#f8f9fa;border:2px solid #dc3545;border-radius:8px;padding:20px;margin:20px 0;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
<h3 style="color:#dc3545;font-weight:bold;margin-top:0;">🚨 ARD Meeting in 7 Days? You Need This</h3>
<p style="border-bottom:1px solid #dee2e6;padding-bottom:10px;">Stop going into ARD meetings unprepared. Get the exact scripts Texas advocates charge $200/hr to provide.</p>
<div style="font-weight:bold;margin-bottom:15px;"><span style="color:#ffc107;">⭐⭐⭐⭐⭐</span> <span style="font-weight:normal;font-size:0.9em;color:#6c757d;">4.9/5 stars (327 Texas parents)</span></div>
<ul style="list-style-type:none;padding-left:0;line-height:1.8;margin-bottom:20px;">
<li>✅ Email templates (copy &amp; paste)</li>
<li>✅ Response scripts for district pushback</li>
<li>✅ 10-Day Recess Playbook</li>
<li>✅ IEP Red Flag Analyzer</li>
<li>✅ Meeting prep checklist</li>
</ul>
<p style="font-style:italic;font-size:0.9em;border-left:3px solid #6c757d;padding-left:10px;color:#6c757d;">"Used the eval request template — FIE scheduled in 48 hours!"<br/><strong style="color:#212529;">- Maria, Round Rock ISD</strong></p>
<div style="text-align:center;margin-top:20px;">
<a href="https://buy.stripe.com/6oU8wO2FTgmA5xReP3bbG0L" style="display:block;background-color:#dc3545;color:white;padding:15px 20px;text-decoration:none;font-weight:bold;border-radius:5px;font-size:1.1em;" target="_blank">Get Instant Access — $47</a>
<small style="color:#6c757d;display:block;margin-top:10px;">🔒 30-Day Money-Back Guarantee</small>
</div>
</div>
<div style="background-color:#f8f9fa;border:2px solid #0d6efd;border-radius:8px;padding:20px;margin:20px 0;box-shadow:0 4px 10px rgba(0,0,0,0.1);">
<div style="text-align:center;margin-bottom:15px;"><span style="background-color:#ffc107;color:#000;padding:6px 12px;border-radius:20px;font-weight:bold;font-size:0.85em;text-transform:uppercase;letter-spacing:1px;">🏆 MOST POPULAR • BEST VALUE</span></div>
<h3 style="color:#0d6efd;font-weight:bold;margin-top:10px;text-align:center;margin-bottom:5px;">Complete Texas Special Ed Bundle</h3>
<h4 style="color:#495057;font-weight:600;text-align:center;margin-top:0;margin-bottom:15px;">All 6 Toolkits • Save $185</h4>
<p style="text-align:center;border-bottom:1px solid #dee2e6;padding-bottom:15px;font-size:1.05em;">Instead of buying toolkits one-by-one for $282, get everything for <strong>$97</strong>.</p>
<ul style="list-style-type:none;padding-left:0;line-height:1.8;margin-bottom:20px;font-size:1.05em;">
<li>✅ <strong>Lifetime access + updates</strong></li>
<li>✅ <strong>Works for multiple children</strong></li>
<li>✅ <strong>All Texas districts</strong></li>
</ul>
<div style="text-align:center;margin-top:20px;">
<a href="https://buy.stripe.com/3cIcN4a8l7Q4d0j7mBbbG0G" style="display:block;background-color:#0d6efd;color:white;padding:16px 20px;text-decoration:none;font-weight:bold;border-radius:6px;font-size:1.2em;" target="_blank">Get All 6 Toolkits — $97</a>
</div>
</div>
</div>

<!-- FAQ -->
<section class="faq-section">
<h2>Frequently Asked Questions: FIE in {name}</h2>
<p>The questions {region}-area parents search most often — answered with Texas law in mind.</p>
{faq_html}
</section>
</article>
<!-- END LEFT COLUMN -->

<!-- RIGHT: SIDEBAR -->
<aside class="sidebar-column">
<div class="sidebar-card cta-card" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);padding:28px;border-radius:12px;text-align:center;color:#fff;border:none;margin-bottom:24px;">
<h4 style="font-family:'Lora',serif;font-size:1.25rem;margin:0 0 10px;color:#fff;">Show the ISD<br/>You Mean Business</h4>
<p style="font-family:'Source Sans 3',sans-serif;font-size:14px;color:#94a3b8;margin:0 0 18px;line-height:1.5;">A verbal request has no legal weight. A written letter starts the 45-day clock and forces a response within 15 school days.</p>
<a href="/resources/Iep-letter.html" style="display:block;background:#d4af37;color:#0f172a;padding:14px;border-radius:6px;text-decoration:none;font-weight:800;font-family:'DM Sans',sans-serif;font-size:14px;">Get Your Letter — $25 →</a>
</div>
<!-- LEAD CAPTURE FORM -->
<div class="sidebar-form" id="leadCaptureForm">
<div class="sf-header">
<p class="sf-eyebrow">{name} Special Ed Law</p>
<h3 class="sf-name">Local IEP <em>Advocates</em></h3>
</div>
<div class="sf-body">
<p class="sf-empathy">Not sure how to request an FIE?</p>
<p class="sf-sub">A free 15-minute call with a local advocate can help you understand your rights and get your written request sent today.</p>
<form id="sidebarLeadForm">
<div class="sf-group"><label>Your Name</label><input placeholder="First and last name" required type="text"/></div>
<div class="sf-group"><label>Email Address</label><input placeholder="Where should we reach you?" required type="email"/></div>
<div class="sf-group"><label>Phone <span style="font-size:9px;color:#b0a89e;font-weight:400;">(optional)</span></label><input placeholder="(555) 000-0000" type="tel"/></div>
<div class="sf-group">
<label>What's going on?</label>
<select required>
<option disabled selected value="">Choose what fits best...</option>
<option>I need to request an FIE / initial evaluation</option>
<option>The school refused my FIE request</option>
<option>They missed the 45-day testing timeline</option>
<option>I disagree with the FIE results (I want an IEE)</option>
<option>I need help at the ARD meeting after the FIE</option>
<option>Something else</option>
</select>
</div>
<button class="sf-btn" type="button">Get My Free 15-Minute Call</button>
<p class="sf-trust">
<svg fill="none" height="13" stroke="#b8963a" stroke-width="2.5" viewBox="0 0 24 24" width="13"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
Confidential. No spam. No pressure.
</p>
</form>
</div>
<div class="sf-footer">Independent Educational Consultants</div>
</div>
<!-- SIDEBAR AD -->
<div class="sidebar-ad-box" style="margin-top:28px;">
<span class="badge">Free Resource</span>
<h3>ARD Meeting Checklist</h3>
<p>Don't walk into your {name} ARD meeting empty-handed. Download our free parent checklist and know exactly what to ask for.</p>
<a href="/resources/ard-checklist.pdf" target="_blank">Download Free Checklist →</a>
</div>
</aside>
</div><!-- end layout-grid -->
</main>
<!-- FOOTER -->
<footer class="site-footer">
<div class="footer-container">
<div class="footer-about">
<img alt="Texas Special Ed Logo" height="auto" src="/images/texasspecialed-logo.png" width="160"/>
<p style="margin-top:.75rem;">Empowering Texas parents with guides, resources, and toolkits to navigate the Special Education and ARD process with confidence.</p>
</div>
<div class="footer-col">
<h3>Quick Links</h3>
<ul>
<li><a href="/">Home</a></li>
<li><a href="/districts/index.html">Browse Districts</a></li>
<li><a href="/resources/index.html">Parent Resources</a></li>
<li><a href="/blog/index.html">Blog &amp; Articles</a></li>
<li><a href="/about/index.html">About Us</a></li>
<li><a href="/contact/index.html">Contact Us</a></li>
</ul>
</div>
<div class="footer-col">
<h3>Popular Districts</h3>
<ul>
<li><a href="/districts/houston-isd/index.html">Houston ISD</a></li>
<li><a href="/districts/frisco-isd/index.html">Frisco ISD</a></li>
<li><a href="/districts/plano-isd/index.html">Plano ISD</a></li>
<li><a href="/districts/conroe-isd/index.html">Conroe ISD</a></li>
<li><a href="/districts/index.html">View All Districts →</a></li>
</ul>
</div>
<div class="footer-col">
<h3>Free Resources</h3>
<ul>
<li><a href="/resources/ard-checklist.pdf" target="_blank">ARD Meeting Checklist</a></li>
<li><a href="/resources/evaluation-request-letter.pdf" target="_blank">Evaluation Request Letter</a></li>
<li><a href="/resources/iep-goal-tracker.pdf" target="_blank">IEP Goal Tracker</a></li>
<li><a href="/resources/parent-rights-guide.pdf" target="_blank">Parent Rights Guide</a></li>
</ul>
</div>
</div>
<div class="footer-bottom">
<p>© 2026 Texas Special Education Resources. All rights reserved. Not affiliated with the TEA or any school district.</p>
</div>
</footer>
<!-- SCRIPTS -->
<script>
   document.addEventListener('DOMContentLoaded', function() {{
      var toggle = document.querySelector('.mobile-menu-toggle');
      var menu = document.querySelector('.nav-menu');
      if (toggle && menu) {{
         toggle.addEventListener('click', function() {{
            menu.classList.toggle('active');
            toggle.setAttribute('aria-expanded', menu.classList.contains('active'));
         }});
      }}
      const allDetails = document.querySelectorAll('details');
      allDetails.forEach(target => {{
         target.addEventListener('click', () => {{
            allDetails.forEach(d => {{ if (d !== target) d.removeAttribute('open'); }});
         }});
      }});
      const form = document.getElementById('sidebarLeadForm');
      if (form) {{
         const btn = form.querySelector('button');
         btn.addEventListener('click', function(e) {{
            e.preventDefault();
            const name = form.querySelector('input[type="text"]');
            const email = form.querySelector('input[type="email"]');
            const phone = form.querySelector('input[type="tel"]');
            const issue = form.querySelector('select');
            if (!name.value.trim()) {{ alert('Please enter your name.'); name.focus(); return; }}
            btn.innerHTML = 'Securely Sending...';
            btn.disabled = true;
            btn.style.opacity = '0.7';
            const data = new URLSearchParams();
            data.append('name', name.value || 'Not provided');
            data.append('email', email.value || 'Not provided');
            data.append('phone', phone.value || 'Not provided');
            data.append('concern', issue.value || 'Not provided');
            data.append('pageUrl', window.location.href);
            fetch('https://script.google.com/macros/s/AKfycbwWpGXg3JMJnxyzUlJHPlQRnE_R2Dh6oFvapMureXQWG_0bLOBtN_e7f5s5jnKRdcG-/exec', {{
               method: 'POST', body: data, mode: 'no-cors'
            }}).then(() => {{
               form.innerHTML = `<div style="text-align:center;padding:20px 10px;">
                  <div style="color:#b8963a;font-size:40px;margin-bottom:10px;">✓</div>
                  <h4 style="font-family:'Cormorant Garamond',serif;font-size:26px;color:#1a1410;margin-bottom:10px;">Request Received</h4>
                  <p style="font-size:14px;color:#6b5f53;line-height:1.5;">A local advocate will reach out shortly.</p>
               </div>`;
            }}).catch(() => {{ btn.innerHTML = 'Error. Please Try Again.'; btn.disabled = false; btn.style.opacity = '1'; }});
         }});
      }}
   }});
</script>
</body>
</html>"""


# ── Main generation loop ───────────────────────────────────────────────────────

def generate_content(client, district):
    name = district["name"]
    region = district["region"]
    enrollment = district["enrollment"]

    prompt = CONTENT_PROMPT.format(
        DISTRICT_NAME=name,
        REGION=region,
        ENROLLMENT=f"{enrollment:,}"
    )

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    # Strip any accidental markdown fences
    raw = re.sub(r"^```(?:json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    return json.loads(raw)


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY is not set. Run: export ANTHROPIC_API_KEY='sk-ant-...'")

    client = anthropic.Anthropic(api_key=api_key)
    output_dir = "fie_html_pages"
    os.makedirs(output_dir, exist_ok=True)

    total = len(bottom_70)
    print(f"Generating {total} FIE HTML pages...\n")

    for idx, district in enumerate(bottom_70, start=1):
        slug = to_slug(district["name"])
        filename = os.path.join(output_dir, f"what-is-an-fie-{slug}.html")

        if os.path.exists(filename):
            print(f"[{idx:02d}/{total}] SKIP  {district['name']} (already exists)")
            continue

        print(f"[{idx:02d}/{total}] Generating: {district['name']} ...", end=" ", flush=True)
        try:
            content = generate_content(client, district)
            html = build_html(district, content)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"✓  → {filename}")
        except json.JSONDecodeError as e:
            print(f"✗  JSON parse error: {e}")
        except anthropic.RateLimitError:
            print("⚠  Rate limited — waiting 60s...")
            time.sleep(60)
            content = generate_content(client, district)
            html = build_html(district, content)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"✓  → {filename}")
        except Exception as e:
            print(f"✗  ERROR: {e}")

        if idx < total:
            time.sleep(2)

    print(f"\n✅ Done! {total} HTML files saved to ./{output_dir}/")
    print("Deploy each file to: /districts/<slug>/what-is-an-fie-<slug>.html\n")


if __name__ == "__main__":
    main()