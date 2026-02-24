import csv
import json
import time
import random
import requests
import logging
from bs4 import BeautifulSoup
from pathlib import Path
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# ─── CONFIG ───────────────────────────────────────────────────────────────────
PROJECT_ID   = "texasspecialed"
LOCATION     = "us-central1"
MODEL_NAME   = "gemini-2.0-flash"
INPUT_CSV    = "texas_special_ed_leads_top20.csv"
OUTPUT_CSV   = "texas_leads_ready_to_send.csv"
PROGRESS_LOG = "progress.log"          # Tracks completed rows so reruns skip them

SCRAPE_TIMEOUT   = 12                  # seconds per request
SCRAPE_MAX_CHARS = 5000                # chars sent to AI
SCRAPE_RETRIES   = 2                   # retries on network failure
AI_RETRIES       = 3                   # retries on AI failure
RATE_LIMIT_PAUSE = 1.5                 # seconds between AI calls

ADVERTISE_URL = "https://www.texasspecialed.com/advertise"

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9',
}

# ─── LOGGING ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-8s  %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('run.log', encoding='utf-8'),
    ]
)
log = logging.getLogger(__name__)


# ─── SCRAPER ──────────────────────────────────────────────────────────────────
def scrape_website_text(url: str) -> str | None:
    """
    Fetches a URL and returns clean readable text (up to SCRAPE_MAX_CHARS).
    Retries on transient network errors. Returns None on permanent failure.
    """
    if not url or not url.startswith('http'):
        log.warning(f"  Skipping invalid URL: {url}")
        return None

    for attempt in range(1, SCRAPE_RETRIES + 2):
        try:
            response = requests.get(
                url, headers=HEADERS,
                timeout=SCRAPE_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            for tag in soup(['script', 'style', 'noscript', 'nav', 'footer', 'header']):
                tag.decompose()

            text = ' '.join(soup.stripped_strings)
            text = ' '.join(text.split())           # collapse whitespace
            return text[:SCRAPE_MAX_CHARS]

        except requests.exceptions.HTTPError as e:
            # 4xx errors won't get better on retry
            log.warning(f"  HTTP {e.response.status_code} for {url} — skipping")
            return None
        except requests.exceptions.RequestException as e:
            if attempt <= SCRAPE_RETRIES:
                wait = 2 ** attempt + random.uniform(0, 1)
                log.warning(f"  Scrape attempt {attempt} failed ({e}). Retrying in {wait:.1f}s...")
                time.sleep(wait)
            else:
                log.warning(f"  All scrape attempts failed for {url}: {e}")
                return None


# ─── DEDUPLICATION ────────────────────────────────────────────────────────────
def load_completed_keys(output_path: str) -> set:
    """
    Returns a set of (Business Name, District) tuples already written to output.
    Allows safe reruns without reprocessing completed rows.
    """
    completed = set()
    p = Path(output_path)
    if not p.exists():
        return completed
    with open(p, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row.get('Business Name', '').strip(), row.get('District', '').strip())
            completed.add(key)
    return completed


def deduplicate_input(rows: list[dict]) -> list[dict]:
    """
    Removes rows where the same business website appears more than once.
    Keeps the first occurrence. Logs skipped duplicates.
    """
    seen_urls = {}
    unique = []
    for row in rows:
        url = row.get('Website', '').strip().rstrip('/')
        # Normalize: strip utm params
        base_url = url.split('?')[0]
        key = (row.get('Business Name', '').strip().lower(), base_url)
        if key in seen_urls:
            log.info(f"  [DEDUP] Skipping duplicate: {row['Business Name']} ({row['District']})")
            continue
        seen_urls[key] = True
        unique.append(row)
    return unique


# ─── AI ANALYSIS + EMAIL DRAFT ────────────────────────────────────────────────
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "actual_category": {
            "type": "STRING",
            "enum": ["Attorney", "Advocate", "Tutor", "Irrelevant"]
        },
        "drafted_email": {
            "type": "STRING",
            "description": "Cold email body text, or empty string if Irrelevant."
        }
    },
    "required": ["actual_category", "drafted_email"]
}

PROMPT_TEMPLATE = """
You are doing cold sales outreach for texasspecialed.com — a resource site helping Texas parents 
navigate the special education system. The advertise page is: {advertise_url}

Analyze the website text below and categorize the business into exactly one of:
  1. Attorney   — Special education law firms representing parents in IEP/ARD disputes or due process.
  2. Advocate   — Independent advocates who attend ARD meetings and review IEPs (non-attorneys).
  3. Tutor      — Tutors, reading specialists, dyslexia therapists, OT, speech, or learning centers.
  4. Irrelevant — Does not fit any of the above (general law, unrelated business, school district itself, etc.)

Then write a 4-5 sentence cold email to {business_name} in the {district} area.
Rules:
- If Irrelevant: leave drafted_email as an empty string. Do not write anything.
- Write in plain text only. No HTML. No markdown. No subject line. No greeting line — start directly with the value proposition.
- Always lead with monthly pricing. Never mention annual pricing.
- End every email with this exact call to action on its own line:
  "You can review placements and set up your listing here: {advertise_url}"
- Keep tone professional, warm, and brief — no filler phrases like "I hope this email finds you well."
- Do NOT use placeholder text like [Name] or [Your Name]. Sign off as: — The Texas Special Ed Team

Category-specific pitch rules:
  Attorney → Tier 2 at $249/mo on the Grievance & Discipline page or ARD Guide page.
    Emphasize: parents on these pages are in active crisis (facing suspension/expulsion) and urgently 
    seeking legal representation. One retained client typically covers 12 months of ad cost.
    
  Advocate → Tier 1 at $59/mo or Tier 2 at $129/mo on the ARD Meeting Guide page.
    Emphasize: parents reading this page are terrified of their upcoming ARD meeting and looking for 
    someone to sit next to them. $59/mo is less than $2 a day.
    
  Tutor → Tier 1 at $39/mo or Tier 2 at $89/mo on the Dyslexia Services page.
    Emphasize: parents on this page are in the early "something is wrong" phase — actively researching 
    support for a child they suspect has a reading challenge. One new student covers 6 months of ad cost.

Website Text for {business_name}:
{website_text}
"""

def analyze_and_draft(model, business_name: str, district: str, website_text: str) -> dict:
    """Calls Vertex AI to categorize and draft. Retries on failure."""
    prompt = PROMPT_TEMPLATE.format(
        business_name=business_name,
        district=district,
        website_text=website_text,
        advertise_url=ADVERTISE_URL,
    )

    for attempt in range(1, AI_RETRIES + 2):
        try:
            response = model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                    temperature=0.2,
                    max_output_tokens=600,
                )
            )
            result = json.loads(response.text)
            # Sanitize: strip any accidental placeholder text
            email = result.get('drafted_email', '')
            if '[Name]' in email or '[Your Name]' in email:
                email = email.replace('[Name]', '').replace('[Your Name]', '').strip()
            result['drafted_email'] = email
            return result

        except (json.JSONDecodeError, KeyError) as e:
            log.warning(f"  AI parse error (attempt {attempt}): {e}")
        except Exception as e:
            log.warning(f"  AI call failed (attempt {attempt}): {e}")

        if attempt <= AI_RETRIES:
            wait = 2 ** attempt + random.uniform(0, 1)
            log.info(f"  Retrying AI in {wait:.1f}s...")
            time.sleep(wait)

    return {"actual_category": "Error", "drafted_email": ""}


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    ai_model = GenerativeModel(MODEL_NAME)

    # Load input
    with open(INPUT_CSV, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)
        original_fields = reader.fieldnames

    total_input = len(all_rows)
    log.info(f"Loaded {total_input} rows from {INPUT_CSV}")

    # Deduplicate
    all_rows = deduplicate_input(all_rows)
    log.info(f"After deduplication: {len(all_rows)} unique leads")

    # Load already-completed rows (safe rerun)
    completed_keys = load_completed_keys(OUTPUT_CSV)
    log.info(f"Already completed: {len(completed_keys)} rows — will skip these")

    # Determine if output file is new (write header) or existing (append)
    output_exists = Path(OUTPUT_CSV).exists() and len(completed_keys) > 0
    new_fields = (original_fields or []) + ['AI_Verified_Category', 'Drafted_Email']

    write_mode = 'a' if output_exists else 'w'

    processed = 0
    skipped   = 0
    errors    = 0

    with open(OUTPUT_CSV, mode=write_mode, newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=new_fields, extrasaction='ignore')
        if not output_exists:
            writer.writeheader()

        for i, row in enumerate(all_rows, 1):
            name     = row.get('Business Name', '').strip()
            district = row.get('District', '').strip()
            key      = (name, district)

            # Skip if already done
            if key in completed_keys:
                log.info(f"[{i}/{len(all_rows)}] SKIP (already done): {name}")
                skipped += 1
                continue

            log.info(f"[{i}/{len(all_rows)}] Processing: {name} ({district})")

            # Step 1: Scrape
            url = row.get('Website', '').strip()
            website_text = scrape_website_text(url)

            if not website_text:
                row['AI_Verified_Category'] = "Scrape Failed"
                row['Drafted_Email'] = ""
                writer.writerow(row)
                outfile.flush()
                errors += 1
                log.warning(f"  -> Scrape failed. Marked and continuing.")
                continue

            # Step 2: AI analysis + draft
            ai_result = analyze_and_draft(ai_model, name, district, website_text)

            row['AI_Verified_Category'] = ai_result['actual_category']
            row['Drafted_Email']        = ai_result['drafted_email']

            writer.writerow(row)
            outfile.flush()   # Write immediately so reruns don't lose progress
            processed += 1

            log.info(f"  -> {ai_result['actual_category']}")

            # Rate limit pause (skip on last row)
            if i < len(all_rows):
                time.sleep(RATE_LIMIT_PAUSE)

    # ─── Summary ───
    log.info("")
    log.info("═" * 50)
    log.info(f"  Done.")
    log.info(f"  Total input rows : {total_input}")
    log.info(f"  Unique leads     : {len(all_rows)}")
    log.info(f"  Newly processed  : {processed}")
    log.info(f"  Skipped (done)   : {skipped}")
    log.info(f"  Scrape failures  : {errors}")
    log.info(f"  Output file      : {OUTPUT_CSV}")
    log.info("═" * 50)