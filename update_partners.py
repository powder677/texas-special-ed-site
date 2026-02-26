"""
update_partners.py
------------------
Loops through every district folder in your texas-special-ed-site/districts
directory, reads partners.html, sends it to Vertex AI (Gemini) for custom
content generation, then writes the updated file back in place.

WHAT IT CHANGES:
  1. <meta name="description"> — district-specific SEO meta description
  2. Green "Did you know" box — district-specific program paragraph
  3. "Navigating Special Ed" process grid — tailored h4 + p per card
  4. Marks each file with an HTML comment so it won't be re-processed

SETUP (run once in terminal):
  pip install google-cloud-aiplatform beautifulsoup4 lxml

AUTHENTICATION:
  Option A (recommended): run `gcloud auth application-default login`
  Option B: set env variable GOOGLE_APPLICATION_CREDENTIALS to your
            service account JSON key path

USAGE:
  python update_partners.py

  # Dry run (prints changes, does NOT save files):
  python update_partners.py --dry-run

  # Process only one district (for testing):
  python update_partners.py --district abilene-isd

  # Skip already-processed files (default: ON):
  python update_partners.py --no-skip
"""

import os
import re
import sys
import time
import argparse
import logging
from pathlib import Path
from bs4 import BeautifulSoup
import vertexai
from vertexai.generative_models import GenerativeModel

# ─────────────────────────────────────────────
# CONFIG — edit these to match your setup
# ─────────────────────────────────────────────

DISTRICTS_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"

GCP_PROJECT_ID = "ny-build-487810"   # e.g. "my-project-123"
GCP_REGION     = "us-central1"
GEMINI_MODEL   = "gemini-2.0-flash"      # fast + cheap for batch work

# Seconds to wait between API calls (avoid rate limiting)
RATE_LIMIT_DELAY = 2

# HTML comment stamped into processed files so they're skipped on re-runs
PROCESSED_MARKER = "<!-- partners-content-updated-v1 -->"

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# DISTRICT CONTEXT
# Enriches the prompt so Vertex can make better
# content decisions per district type.
# Add rows as needed — anything not listed falls
# back to the "default" type.
# ─────────────────────────────────────────────

DISTRICT_CONTEXT = {
    # slug : { "type": urban|suburban|rural, "notes": freeform hints }
    "houston-isd":          {"type": "urban",    "notes": "largest TX district, high ELL population, many bilingual sped programs"},
    "dallas-isd":           {"type": "urban",    "notes": "large urban, diverse demographics, bilingual ARD rights critical"},
    "austin-isd":           {"type": "urban",    "notes": "tech-adjacent families, high IEE request rate, autism support demand"},
    "cypress-fairbanks-isd":{"type": "suburban", "notes": "fast-growing Houston suburb, large enrollment, LRE placement disputes common"},
    "katy-isd":             {"type": "suburban", "notes": "affluent Houston suburb, parents often seek private neuropsych evals"},
    "frisco-isd":           {"type": "suburban", "notes": "high-income fast-growing DFW suburb, gifted/2e overlap common"},
    "plano-isd":            {"type": "suburban", "notes": "established DFW suburb, high parental advocacy, private eval culture"},
    "round-rock-isd":       {"type": "suburban", "notes": "growing Austin suburb, autism and dyslexia services in demand"},
    "abilene-isd":          {"type": "urban",    "notes": "mid-sized west TX city, limited local provider options, rural-adjacent challenges"},
    # default fallback is applied for any slug not listed above
    "default":              {"type": "suburban", "notes": "mid-size Texas school district"},
}

def get_district_context(slug: str) -> dict:
    return DISTRICT_CONTEXT.get(slug, DISTRICT_CONTEXT["default"])


def slug_to_name(slug: str) -> str:
    """Convert folder slug to human readable name. e.g. abilene-isd -> Abilene ISD"""
    return " ".join(
        word.upper() if word in ("isd", "cisd", "uisd", "hisd", "gisd") else word.capitalize()
        for word in slug.replace("-", " ").split()
    )


# ─────────────────────────────────────────────
# VERTEX AI PROMPT
# ─────────────────────────────────────────────

def build_prompt(district_name: str, slug: str, current_html: str) -> str:
    ctx = get_district_context(slug)

    return f"""You are editing an HTML file for a Texas special education parent resource website.
The district is: {district_name}
District type: {ctx['type']} (urban | suburban | rural)
Additional context: {ctx['notes']}

Your job is to return ONLY a valid JSON object with exactly these 4 keys.
No markdown fences. No explanation. No extra text. Just the raw JSON.

{{
  "meta_description": "...",
  "did_you_know_h3": "...",
  "did_you_know_p": "...",
  "process_cards": [
    {{"h4": "...", "p": "..."}},
    {{"h4": "...", "p": "..."}},
    {{"h4": "...", "p": "..."}}
  ]
}}

RULES FOR EACH FIELD:

meta_description:
- 140-155 characters
- Mention {district_name} by name
- Focus on parents finding IEP help, evaluations, and local advocates
- Do not start with the word "Find"
- Example style: "Navigating special education in {district_name}? Get IEP guides, evaluation timelines, and local advocate resources for Texas parents."

did_you_know_h3:
- Plain text only (no HTML tags), keep it short
- Must include "{district_name}" in the text
- Format: "Did you know {district_name} offers these free resources?"

did_you_know_p:
- 2-3 sentences, plain text only (no HTML tags)
- Mention 1-2 real program types appropriate for this district type
- For urban districts: mention bilingual special ed, autism support classrooms, or transition programs
- For suburban districts: mention inclusion programs, gifted/2e overlap, or extended school year
- For rural districts: mention ESC regional services, telehealth therapy, or co-op programs
- Do NOT fabricate specific named programs — use general descriptions
- Keep tone warm and informative for a stressed parent

process_cards (exactly 3 cards):
- h4: short title (3-5 words)
- p: one sentence (max 15 words), plain text only
- Tailor to what parents in THIS district type struggle with most:
  * Urban: evaluation delays, bilingual ARD rights, discipline/MDR issues
  * Suburban: LRE placement fights, private eval rights, transition planning
  * Rural: finding local providers, ESC support, telehealth services
- Keep all 3 cards distinct topics

CURRENT FILE EXCERPT (for context only — do not copy this text):
{current_html[:800]}
"""


# ─────────────────────────────────────────────
# HTML MANIPULATION
# ─────────────────────────────────────────────

def apply_updates(html: str, district_name: str, updates: dict) -> str:
    """
    Parse the HTML and surgically replace only the target sections.
    Uses BeautifulSoup so we don't accidentally break other markup.
    """
    soup = BeautifulSoup(html, "lxml")

    # 1. Meta description
    meta = soup.find("meta", {"name": "description"})
    if meta:
        meta["content"] = updates["meta_description"]
        log.debug("  ✓ meta description updated")
    else:
        # Insert one after <meta charset>
        charset = soup.find("meta", {"charset": True})
        if charset:
            new_meta = soup.new_tag("meta", attrs={
                "name": "description",
                "content": updates["meta_description"]
            })
            charset.insert_after(new_meta)
            log.debug("  ✓ meta description inserted")

    # 2. Green "Did you know" box
    # Find the div with the specific background color style
    green_box = soup.find("div", style=lambda s: s and "f0fdf4" in s)
    if green_box:
        h3 = green_box.find("h3")
        p  = green_box.find("p")
        if h3:
            # Preserve the icon, just update the text node
            icon = h3.find("i")
            h3.clear()
            if icon:
                h3.append(icon)
                h3.append(" " + updates["did_you_know_h3"])
            else:
                h3.string = updates["did_you_know_h3"]
        if p:
            p.string = updates["did_you_know_p"]
        log.debug("  ✓ did-you-know box updated")
    else:
        log.warning(f"  ⚠ Could not find green did-you-know box in {district_name}")

    # 3. Process grid cards
    process_section = soup.find("section", style=lambda s: s and "margin-bottom: 3rem" in s if s else False)
    if not process_section:
        # fallback: find by h3 text content
        for section in soup.find_all("section"):
            h3 = section.find("h3")
            if h3 and "Navigating Special Ed" in h3.get_text():
                process_section = section
                break

    if process_section:
        # Update the h3 heading too
        h3 = process_section.find("h3")
        if h3:
            h3.string = f"Navigating Special Ed in {district_name}"

        cards = process_section.find_all("div", class_="process-card")
        for i, card in enumerate(cards):
            if i < len(updates["process_cards"]):
                card_data = updates["process_cards"][i]
                h4 = card.find("h4")
                p  = card.find("p")
                if h4:
                    h4.string = card_data["h4"]
                if p:
                    p.string = card_data["p"]
        log.debug("  ✓ process cards updated")
    else:
        log.warning(f"  ⚠ Could not find process grid in {district_name}")

    # 4. Stamp processed marker so we skip this file next run
    if PROCESSED_MARKER not in str(soup):
        body = soup.find("body")
        if body:
            marker_tag = BeautifulSoup(f"\n{PROCESSED_MARKER}\n", "lxml")
            body.insert(0, marker_tag)

    return str(soup)


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Batch update partners.html with Vertex AI")
    parser.add_argument("--dry-run",    action="store_true", help="Print changes but do not save files")
    parser.add_argument("--district",   type=str, default=None, help="Process only this district slug")
    parser.add_argument("--no-skip",    action="store_true", help="Re-process already-updated files")
    args = parser.parse_args()

    # Init Vertex AI
    log.info(f"Initializing Vertex AI (project={GCP_PROJECT_ID}, region={GCP_REGION})")
    vertexai.init(project=GCP_PROJECT_ID, location=GCP_REGION)
    model = GenerativeModel(GEMINI_MODEL)

    districts_path = Path(DISTRICTS_DIR)
    if not districts_path.exists():
        log.error(f"Districts directory not found: {DISTRICTS_DIR}")
        sys.exit(1)

    # Collect district folders
    folders = sorted([
        f for f in districts_path.iterdir()
        if f.is_dir() and (args.district is None or f.name == args.district)
    ])

    log.info(f"Found {len(folders)} district folder(s) to process")

    processed = 0
    skipped   = 0
    errors    = 0

    for folder in folders:
        partners_file = folder / "partners.html"

        if not partners_file.exists():
            log.debug(f"  SKIP {folder.name} — no partners.html")
            skipped += 1
            continue

        html = partners_file.read_text(encoding="utf-8", errors="replace")

        # Skip already-processed files unless --no-skip
        if not args.no_skip and PROCESSED_MARKER in html:
            log.info(f"  SKIP {folder.name} — already updated (use --no-skip to re-run)")
            skipped += 1
            continue

        district_name = slug_to_name(folder.name)
        log.info(f"  Processing: {district_name} ({folder.name})")

        # Build prompt and call Vertex
        prompt = build_prompt(district_name, folder.name, html)

        try:
            response = model.generate_content(prompt)
            raw_json = response.text.strip()

            # Strip any accidental markdown fences Gemini sometimes adds
            raw_json = re.sub(r"^```json\s*", "", raw_json)
            raw_json = re.sub(r"^```\s*",     "", raw_json)
            raw_json = re.sub(r"\s*```$",     "", raw_json)

            import json
            updates = json.loads(raw_json)

        except json.JSONDecodeError as e:
            log.error(f"  ✗ JSON parse error for {district_name}: {e}")
            log.error(f"    Raw response: {raw_json[:300]}")
            errors += 1
            continue
        except Exception as e:
            log.error(f"  ✗ Vertex API error for {district_name}: {e}")
            errors += 1
            continue

        # Validate expected keys
        required_keys = {"meta_description", "did_you_know_h3", "did_you_know_p", "process_cards"}
        if not required_keys.issubset(updates.keys()):
            log.error(f"  ✗ Missing keys in response for {district_name}: {updates.keys()}")
            errors += 1
            continue

        # Apply HTML changes
        updated_html = apply_updates(html, district_name, updates)

        if args.dry_run:
            log.info(f"  [DRY RUN] Would update {partners_file}")
            log.info(f"    meta_description : {updates['meta_description']}")
            log.info(f"    did_you_know_p   : {updates['did_you_know_p'][:80]}...")
            log.info(f"    card 1           : {updates['process_cards'][0]['h4']}")
        else:
            partners_file.write_text(updated_html, encoding="utf-8")
            log.info(f"  ✓ Saved: {partners_file}")

        processed += 1

        # Rate limiting
        if processed < len(folders):
            time.sleep(RATE_LIMIT_DELAY)

    # Summary
    log.info("─" * 50)
    log.info(f"Done. Processed: {processed}  |  Skipped: {skipped}  |  Errors: {errors}")
    if errors:
        log.warning("Some files had errors — check logs above. Those files were NOT modified.")


if __name__ == "__main__":
    main()