"""
generate_district_content.py
Generates unique local content blocks for unindexed district pages on texasspecialed.com
Uses Claude API to differentiate thin/duplicate pages so Google will index them.

Usage:
    pip install anthropic
    export ANTHROPIC_API_KEY=
    python generate_district_content.py

Output:
    generated_content.json  — full results with HTML content per page
    failed.txt              — any pages that errored, for retry
"""

import anthropic
import json
import time
import re

client = anthropic.Anthropic()

# ── 153 unindexed pages from GSC Coverage export ──────────────────────────────
UNINDEXED_PAGES = [
    "hurst-euless-bedford-isd/leadership-directory",
    "lubbock-isd/evaluation-child-find",
    "sherman-isd/evaluation-child-find",
    "wylie-isd/grievance-dispute-resolution",
    "fort-bend-isd/evaluation-child-find",
    "little-elm-isd/evaluation-child-find",
    "pflugerville-isd/evaluation-child-find",
    "dallas-isd/evaluation-child-find",
    "dickinson-isd/ard-process-guide",
    "ysleta-isd/ard-process-guide",
    "eanes-isd/evaluation-child-find",
    "georgetown-isd/partners",
    "midway-isd/ard-process-guide",
    "crowley-isd/evaluation-child-find",
    "la-joya-isd/evaluation-child-find",
    "ysleta-isd/dyslexia-services",
    "rio-grande-city-grulla-isd/dyslexia-services",
    "forney-isd/partners",
    "santa-fe-isd/evaluation-child-find",
    "princeton-isd/evaluation-child-find",
    "socorro-isd/grievance-dispute-resolution",
    "houston-isd/ard-process-guide",
    "houston-isd/dyslexia-services",
    "carrollton-farmers-branch-isd/evaluation-child-find",
    "ysleta-isd/leadership-directory",
    "copperas-cove-isd/ard-process-guide",
    "comal-isd/what-is-fie",
    "klein-isd/ard-process-guide",
    "lewisville-isd/partners",
    "fort-bend-isd/dyslexia-services",
    "comal-isd/dyslexia-services",
    "denton-isd/evaluation-child-find",
    "brownsville-isd/evaluation-child-find",
    "copperas-cove-isd/evaluation-child-find",
    "donna-isd/leadership-directory",
    "college-station-isd/dyslexia-services",
    "tomball-isd/grievance-dispute-resolution",
    "mansfield-isd/leadership-directory",
    "la-joya-isd/dyslexia-services",
    "longview-isd/leadership-directory",
    "irving-isd/ard-process-guide",
    "mission-cisd/leadership-directory",
    "pflugerville-isd/grievance-dispute-resolution",
    "melissa-isd/leadership-directory",
    "goose-creek-cisd/grievance-dispute-resolution",
    "royse-city-isd/leadership-directory",
    "north-east-isd/evaluation-child-find",
    "texarkana-isd/evaluation-child-find",
    "texarkana-isd/ard-process-guide",
    "burleson-isd/evaluation-child-find",
    "mckinney-isd/evaluation-child-find",
    "royse-city-isd/evaluation-child-find",
    "allen-isd/leadership-directory",
    "wylie-isd/partners",
    "weslaco-isd/ard-process-guide",
    "round-rock-isd/dyslexia-services",
    "ector-county-isd/evaluation-child-find",
    "mission-cisd/partners",
    "alief-isd/partners",
    "mckinney-isd/ard-process-guide",
    "victoria-isd/grievance-dispute-resolution",
    "bastrop-isd/evaluation-child-find",
    "corpus-christi-isd/ard-process-guide",
    "waco-isd/grievance-dispute-resolution",
    "judson-isd/dyslexia-services",
    "texas-city-isd/ard-process-guide",
    "laredo-isd/dyslexia-services",
    "prosper-isd/dyslexia-services",
    "humble-isd/evaluation-child-find",
    "denton-isd/grievance-dispute-resolution",
    "lubbock-isd/leadership-directory",
    "klein-isd/evaluation-child-find",
    "victoria-isd/partners",
    "abilene-isd/ard-process-guide",
    "judson-isd/ard-process-guide",
    "belton-isd/evaluation-child-find",
    "college-station-isd/leadership-directory",
    "northwest-isd/partners",
    "eagle-mountain-saginaw-isd/grievance-dispute-resolution",
    "dickinson-isd/grievance-dispute-resolution",
    "keller-isd/leadership-directory",
    "little-elm-isd/leadership-directory",
    "mission-cisd/dyslexia-services",
    "leander-isd/leadership-directory",
    "la-joya-isd/leadership-directory",
    "pasadena-isd/leadership-directory",
    "mission-cisd/grievance-dispute-resolution",
    "amarillo-isd/partners",
    "prosper-isd/leadership-directory",
    "east-central-isd/grievance-dispute-resolution",
    "round-rock-isd/ard-process-guide",
    "princeton-isd/grievance-dispute-resolution",
    "wylie-isd/leadership-directory",
    "socorro-isd/partners",
    "spring-isd/evaluation-child-find",
    "clear-creek-isd/evaluation-child-find",
    "arlington-isd/partners",
    "channelview-isd/grievance-dispute-resolution",
    "eagle-mountain-saginaw-isd/partners",
    "coppell-isd/grievance-dispute-resolution",
    "fort-bend-isd/leadership-directory",
    "alvin-isd/partners",
    "copperas-cove-isd/grievance-dispute-resolution",
    "wichita-falls-isd/ard-process-guide",
    "friendswood-isd/partners",
    "forney-isd/grievance-dispute-resolution",
    "alief-isd/ard-process-guide",
    "clint-isd/partners",
    "texas-city-isd/grievance-dispute-resolution",
    "harlingen-cisd/leadership-directory",
    "el-paso-isd/evaluation-child-find",
    "midway-isd/partners",
    "victoria-isd/leadership-directory",
    "alief-isd/leadership-directory",
    "harmony-public-schools-combined/partners",
    "eagle-mountain-saginaw-isd/dyslexia-services",
    "channelview-isd/leadership-directory",
    "tomball-isd/dyslexia-services",
    "corpus-christi-isd/dyslexia-services",
    "wichita-falls-isd/evaluation-child-find",
    "aldine-isd/evaluation-child-find",
    "longview-isd/dyslexia-services",
    "east-central-isd/dyslexia-services",
    "grand-prairie-isd/evaluation-child-find",
    "bastrop-isd/ard-process-guide",
    "garland-isd/partners",
    "katy-isd/partners",
    "copperas-cove-isd/partners",
    "cypress-fairbanks-isd/dyslexia-services",
    "east-central-isd/evaluation-child-find",
    "lake-travis-isd/evaluation-child-find",
    "frisco-isd/leadership-directory",
    "dallas-isd/dyslexia-services",
    "weslaco-isd/dyslexia-services",
    "royse-city-isd/partners",
    "spring-branch-isd/dyslexia-services",
    "clint-isd/evaluation-child-find",
    "melissa-isd/dyslexia-services",
    "abilene-isd/evaluation-child-find",
    "friendswood-isd/leadership-directory",
    "rio-grande-city-grulla-isd/grievance-dispute-resolution",
    "burleson-isd/leadership-directory",
    "midway-isd/leadership-directory",
    "weslaco-isd/partners",
    "hurst-euless-bedford-isd/grievance-dispute-resolution",
    "belton-isd/ard-process-guide",
    "lake-travis-isd/leadership-directory",
    "goose-creek-cisd/leadership-directory",
    "magnolia-isd/leadership-directory",
    "beaumont-isd/partners",
    "laredo-isd/partners",
    "la-joya-isd/ard-process-guide",
    "san-angelo-isd/leadership-directory",
]

# ── Page type context for the prompt ──────────────────────────────────────────
PAGE_TYPE_CONTEXT = {
    "evaluation-child-find": (
        "How parents in this district can request a Full Individual Evaluation (FIE) "
        "under Texas Child Find obligations. The district must evaluate within 45 school days "
        "of signed consent. Written requests carry legal weight; verbal requests do not."
    ),
    "ard-process-guide": (
        "How ARD (Admission, Review, Dismissal) committee meetings work in this district. "
        "The ARD committee determines eligibility and writes the IEP. Parents are full members."
    ),
    "dyslexia-services": (
        "Dyslexia identification and intervention services in this district under the "
        "Texas Dyslexia Handbook. Districts must screen all students and provide structured "
        "literacy intervention to identified students."
    ),
    "leadership-directory": (
        "Special education leadership, department contacts, and organizational structure "
        "for this district. Includes the Special Education Director and department office."
    ),
    "grievance-dispute-resolution": (
        "How parents can file complaints, request mediation, or pursue due process "
        "against this district under IDEA and Texas Education Code."
    ),
    "partners": (
        "Local therapists, special education advocates, educational diagnosticians, "
        "and service providers who work with families in this district's area."
    ),
    "what-is-fie": (
        "What a Full Individual Evaluation (FIE) is, how to request one from this district, "
        "and what the evaluation process looks like under Texas law."
    ),
}

SYSTEM_PROMPT = """You are a Texas special education content writer for texasspecialed.com, 
a parent resource site. Your job is to write a SHORT, district-specific content block 
(150–200 words) to be inserted into a page about special education services in a specific 
Texas school district.

The content MUST:
1. Be genuinely specific to the named district — mention the city/region it serves, 
   approximate student enrollment if you know it, and any notable characteristics 
   (fast-growing suburb, large urban district, border community, rural district, etc.)
2. Use the district name and city naturally in sentences — not just as a header
3. Connect directly to the page topic (e.g. a Child Find page should mention the district's 
   legal obligation to identify children in that specific city/community)
4. End with a "local hook" — 1–2 sentences that are meaningfully unique to this district, 
   such as its size, location, county, regional context, or a notable characteristic
5. Be written for a stressed parent — plain English, no jargon, warm but direct
6. NOT invent staff names, phone numbers, or addresses. If unsure, omit specifics.

Output ONLY the content as plain HTML <p> tags. No headers, no markdown, no preamble."""


def slug_to_name(slug: str) -> str:
    """Convert district slug to readable name."""
    name = slug.replace("-", " ").title()
    # Fix common abbreviations
    name = re.sub(r'\bIsd\b', 'ISD', name)
    name = re.sub(r'\bCisd\b', 'CISD', name)
    name = re.sub(r'\bGrulla\b', 'Grulla', name)
    return name


def generate_content(district_slug: str, page_type: str) -> str:
    district_name = slug_to_name(district_slug)
    context = PAGE_TYPE_CONTEXT.get(page_type, f"Special education {page_type} information")

    user_message = f"""District: {district_name}
Page topic: {page_type} — {context}

Write the local content block for this page."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    return response.content[0].text.strip()


def main():
    results = []
    failed = []

    total = len(UNINDEXED_PAGES)
    print(f"Generating content for {total} pages...\n")

    for i, path in enumerate(UNINDEXED_PAGES, 1):
        parts = path.split("/", 1)
        if len(parts) != 2:
            print(f"  SKIP (no page type): {path}")
            continue

        district_slug, page_type = parts

        try:
            content = generate_content(district_slug, page_type)
            results.append({
                "url": f"https://www.texasspecialed.com/districts/{path}",
                "district": district_slug,
                "page_type": page_type,
                "district_name": slug_to_name(district_slug),
                "generated_html": content
            })
            print(f"  [{i}/{total}] ✓ {district_slug}/{page_type}")

        except Exception as e:
            print(f"  [{i}/{total}] ✗ FAILED: {district_slug}/{page_type} — {e}")
            failed.append(path)

        # Avoid rate limiting
        time.sleep(0.3)

    # Save results
    with open("generated_content.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Saved {len(results)} results to generated_content.json")

    if failed:
        with open("failed.txt", "w") as f:
            f.write("\n".join(failed))
        print(f"✗ {len(failed)} failed — see failed.txt for retry")

    # Print a sample
    if results:
        print("\n── SAMPLE OUTPUT ──────────────────────────────")
        print(f"URL: {results[0]['url']}")
        print(results[0]['generated_html'])


if __name__ == "__main__":
    main()