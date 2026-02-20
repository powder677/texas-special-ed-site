"""
Texas Special Ed — Ad Prospect Finder
Uses Vertex AI (Gemini) to research and surface potential advertisers
across 4 audience-matched categories, then exports a CSV for cold outreach.

Setup:
    pip install google-cloud-aiplatform
    gcloud auth application-default login   (or set GOOGLE_APPLICATION_CREDENTIALS)
    Update PROJECT_ID and LOCATION below.
"""

import os
import csv
import json
import time
from datetime import datetime
import vertexai
from vertexai.generative_models import GenerativeModel

# ─── CONFIG ─────────────────────────────────────────────────────────────────
PROJECT_ID = "texasspecialed"   # ← replace with your GCP project ID
LOCATION   = "us-central1"            # ← change if needed
MODEL      = "gemini-2.0-flash"

OUTPUT_CSV = "ad_prospects.csv"

# ─── AUDIENCE CONTEXT ────────────────────────────────────────────────────────
SITE_CONTEXT = """
Website: TexasSpecialEd.com
Audience: Texas parents of children with learning disabilities, ADHD, Autism,
Dyslexia, or other special needs who are navigating IEPs, ARD meetings,
504 plans, and special education evaluations within Texas school districts.
Typical visitor: Parent of a school-age child (K–12), likely in a major Texas
metro (Houston, DFW, Austin, San Antonio), actively researching their child's
rights and educational options. High purchase intent for services that can help
their child succeed academically or legally.
"""

# ─── AD CATEGORIES ───────────────────────────────────────────────────────────
CATEGORIES = [
    {
        "name": "Special Education Attorneys & Advocates",
        "description": (
            "Law firms, solo attorneys, and non-attorney advocates who specialize in "
            "special education law in Texas. These professionals help parents in IEP "
            "disputes, due process hearings, and TEA complaints."
        ),
        "search_focus": "Texas special education attorneys, IDEA lawyers, parent advocates",
        "why_it_fits": "High-intent audience actively seeking legal help with IEPs/ARDs",
    },
    {
        "name": "Tutoring & Learning Centers (Dyslexia / LD Focus)",
        "description": (
            "Private tutoring companies, Orton-Gillingham providers, and learning "
            "centers that specialize in dyslexia, reading disabilities, ADHD, or "
            "structured literacy instruction. Both franchise and independent operators."
        ),
        "search_focus": "Texas dyslexia tutoring, structured literacy centers, Lindamood-Bell, learning disability tutoring",
        "why_it_fits": "Parents on this site are actively looking for reading intervention options",
    },
    {
        "name": "Pediatric Therapy Clinics (OT, Speech, ABA)",
        "description": (
            "Occupational therapy, speech-language pathology, and ABA therapy clinics "
            "serving school-age children. Especially relevant to Autism, sensory "
            "processing, and communication delay families."
        ),
        "search_focus": "Texas pediatric OT speech therapy ABA clinics, autism therapy centers",
        "why_it_fits": "Autism and behavior toolkit buyers are a direct match for therapy service ads",
    },
    {
        "name": "Educational Psychologists & Neuropsychologists",
        "description": (
            "Private practitioners who conduct independent educational evaluations (IEEs), "
            "psychoeducational assessments, and neuropsychological testing for school-age "
            "children. Parents often seek private evals when they distrust district testing."
        ),
        "search_focus": "Texas independent educational evaluation IEE, neuropsychological testing children",
        "why_it_fits": "Evaluation guide readers are primed to seek private testing options",
    },
]


# ─── PROMPT BUILDER ──────────────────────────────────────────────────────────
def build_prompt(category: dict) -> str:
    return f"""
You are a business development researcher helping a Texas special education
parent resource website find advertisers for cold outreach.

SITE CONTEXT:
{SITE_CONTEXT}

AD CATEGORY: {category["name"]}
CATEGORY DESCRIPTION: {category["description"]}
WHY IT FITS: {category["why_it_fits"]}

Your task:
Identify 8 specific, real businesses or types of businesses in Texas that would
benefit from advertising to this audience. For each one, provide:

1. business_name: A real company name OR a detailed business type description
   (e.g., "Lone Star Dyslexia Center" or "Independent OT clinic serving Austin metro")
2. business_type: Solo practice / Small firm / Regional chain / National franchise / Nonprofit
3. texas_metros: Which Texas cities/metros they likely operate in
4. contact_approach: How to find and contact them (e.g., "Search Google Maps for OT clinics near Houston", "LinkedIn outreach to owners", "State bar attorney directory")
5. ad_pitch: A one-sentence pitch for why advertising on TexasSpecialEd.com benefits them
6. estimated_monthly_budget: Low / Medium / High (based on typical ad spend for this business type)
7. priority: High / Medium / Low (how well they match the audience)

Return ONLY a valid JSON array with exactly 8 objects. No markdown fences, no explanation.
Each object must have all 7 keys above.
"""


# ─── VERTEX AI QUERY ─────────────────────────────────────────────────────────
def query_vertex(model: GenerativeModel, prompt: str, category_name: str) -> list[dict]:
    print(f"\n  Querying Gemini for: {category_name}...")
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 2048,
            },
        )
        raw = response.text.strip()

        # Strip markdown fences if Gemini wraps anyway
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        results = json.loads(raw)
        print(f"  ✓ Got {len(results)} prospects for '{category_name}'")
        return results

    except json.JSONDecodeError as e:
        print(f"  ✗ JSON parse error for '{category_name}': {e}")
        print(f"  Raw response snippet: {raw[:300]}")
        return []
    except Exception as e:
        print(f"  ✗ Vertex AI error for '{category_name}': {e}")
        return []


# ─── CSV EXPORT ──────────────────────────────────────────────────────────────
CSV_FIELDS = [
    "category",
    "why_it_fits",
    "business_name",
    "business_type",
    "texas_metros",
    "contact_approach",
    "ad_pitch",
    "estimated_monthly_budget",
    "priority",
    "outreach_status",    # blank — fill in as you work the list
    "contact_name",       # blank
    "contact_email",      # blank
    "notes",              # blank
    "date_added",
]

def export_csv(all_prospects: list[dict], path: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in all_prospects:
            row.setdefault("outreach_status", "Not contacted")
            row.setdefault("contact_name", "")
            row.setdefault("contact_email", "")
            row.setdefault("notes", "")
            row.setdefault("date_added", datetime.today().strftime("%Y-%m-%d"))
            writer.writerow(row)
    print(f"\n✅  Saved {len(all_prospects)} prospects → {path}")


# ─── SUMMARY PRINTER ─────────────────────────────────────────────────────────
def print_summary(all_prospects: list[dict]):
    print("\n" + "═" * 60)
    print("  PROSPECT SUMMARY")
    print("═" * 60)

    from collections import Counter
    by_cat    = Counter(p["category"] for p in all_prospects)
    by_prio   = Counter(p.get("priority", "?") for p in all_prospects)
    by_budget = Counter(p.get("estimated_monthly_budget", "?") for p in all_prospects)

    print(f"\n  Total prospects: {len(all_prospects)}")

    print("\n  By category:")
    for cat, count in by_cat.items():
        print(f"    {cat[:50]:<50} {count}")

    print("\n  By priority:")
    for prio in ["High", "Medium", "Low"]:
        print(f"    {prio:<10} {by_prio.get(prio, 0)}")

    print("\n  By estimated budget:")
    for budget in ["High", "Medium", "Low"]:
        print(f"    {budget:<10} {by_budget.get(budget, 0)}")

    print("\n  High-priority picks:")
    highs = [p for p in all_prospects if p.get("priority") == "High"]
    for p in highs[:10]:
        print(f"    • [{p['category'][:25]}] {p['business_name']}")
    print()


# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    print("━" * 60)
    print("  Texas Special Ed — Ad Prospect Finder")
    print("  Powered by Vertex AI (Gemini)")
    print("━" * 60)

    # Init Vertex AI
    print(f"\nInitializing Vertex AI (project={PROJECT_ID}, location={LOCATION})...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel(MODEL)
    print("✓ Vertex AI ready")

    all_prospects = []

    for category in CATEGORIES:
        prompt = build_prompt(category)
        prospects = query_vertex(model, prompt, category["name"])

        for p in prospects:
            p["category"]    = category["name"]
            p["why_it_fits"] = category["why_it_fits"]

        all_prospects.extend(prospects)

        # Polite rate-limit pause between calls
        if category != CATEGORIES[-1]:
            time.sleep(2)

    if not all_prospects:
        print("\n⚠️  No prospects returned. Check your Project ID, credentials, and Vertex AI quota.")
        return

    print_summary(all_prospects)
    export_csv(all_prospects, OUTPUT_CSV)

    print("  Next steps:")
    print(f"  1. Open {OUTPUT_CSV} in Excel or Google Sheets")
    print("  2. Sort by 'priority' = High to work your best leads first")
    print("  3. Use 'contact_approach' column to find real contact info")
    print("  4. Fill in 'contact_name', 'contact_email', 'outreach_status' as you go")
    print("  5. Re-run this script anytime to add more categories or refresh prospects\n")


if __name__ == "__main__":
    main()