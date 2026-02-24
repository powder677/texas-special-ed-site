import csv
import json
import time
import random
import requests
import logging
import os
import re
from bs4 import BeautifulSoup
from pathlib import Path
import anthropic

# ─── CONFIG ───────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "your-api-key-here")
MODEL_NAME   = "claude-sonnet-4-5"
INPUT_CSV    = "texas_special_ed_leads_top20.csv"
OUTPUT_CSV   = "texas_leads_ready_to_send.csv"

SCRAPE_TIMEOUT   = 12
SCRAPE_MAX_CHARS = 5000
SCRAPE_RETRIES   = 2
AI_RETRIES       = 3
RATE_LIMIT_PAUSE = 0.5

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


# ─── EMAIL EXTRACTION ─────────────────────────────────────────────────────────
def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) and len(email) < 80

def is_junk_email(email: str) -> bool:
    junk_domains = {
        'example.com', 'domain.com', 'email.com', 'youremail.com',
        'sentry.io', 'wixpress.com', 'squarespace.com', 'wordpress.com',
    }
    junk_keywords = [
        'noreply', 'no-reply', 'donotreply', 'wordpress', 'wix',
        'placeholder', 'test@', 'user@', 'name@', 'email@',
        '.png', '.jpg', '.gif', '.js', '.css',
    ]
    domain = email.split('@')[-1].lower()
    if domain in junk_domains:
        return True
    return any(kw in email.lower() for kw in junk_keywords)

def extract_email(soup) -> str:
    """
    Strategy 1: mailto: links — most reliable, check first.
    Strategy 2: Regex scan of all visible page text.
    Returns best match or empty string.
    """
    # mailto: links
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        if href.startswith('mailto:'):
            email = href.replace('mailto:', '').split('?')[0].strip().lower()
            if is_valid_email(email) and not is_junk_email(email):
                return email

    # Regex scan of visible text
    text = ' '.join(soup.stripped_strings)
    found = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text)
    for email in found:
        email = email.lower().strip('.')
        if is_valid_email(email) and not is_junk_email(email):
            return email

    return ''


# ─── SCRAPER ──────────────────────────────────────────────────────────────────
def scrape_website(url: str) -> tuple[str | None, str]:
    """
    Returns (page_text, email_address).
    page_text is None on failure.
    """
    if not url or not url.startswith('http'):
        log.warning(f"  Skipping invalid URL: {url}")
        return None, ''

    for attempt in range(1, SCRAPE_RETRIES + 2):
        try:
            response = requests.get(
                url, headers=HEADERS,
                timeout=SCRAPE_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract email BEFORE stripping tags
            email = extract_email(soup)

            # Clean text for AI
            for tag in soup(['script', 'style', 'noscript', 'nav', 'footer', 'header']):
                tag.decompose()
            text = ' '.join(soup.stripped_strings)
            text = ' '.join(text.split())

            return text[:SCRAPE_MAX_CHARS], email

        except requests.exceptions.HTTPError as e:
            log.warning(f"  HTTP {e.response.status_code} for {url} — skipping")
            return None, ''
        except requests.exceptions.RequestException as e:
            if attempt <= SCRAPE_RETRIES:
                wait = 2 ** attempt + random.uniform(0, 1)
                log.warning(f"  Scrape attempt {attempt} failed. Retrying in {wait:.1f}s...")
                time.sleep(wait)
            else:
                log.warning(f"  All scrape attempts failed for {url}: {e}")
                return None, ''


# ─── DEDUPLICATION ────────────────────────────────────────────────────────────
def load_completed_keys(output_path: str) -> set:
    completed = set()
    p = Path(output_path)
    if not p.exists():
        return completed
    with open(p, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row.get('Business Name', '').strip(), row.get('District', '').strip())
            completed.add(key)
    return completed

def deduplicate_input(rows: list) -> list:
    seen = {}
    unique = []
    for row in rows:
        url = row.get('Website', '').strip().split('?')[0].rstrip('/')
        key = (row.get('Business Name', '').strip().lower(), url)
        if key in seen:
            log.info(f"  [DEDUP] Skipping duplicate: {row['Business Name']} ({row['District']})")
            continue
        seen[key] = True
        unique.append(row)
    return unique


# ─── PROMPT ───────────────────────────────────────────────────────────────────
PROMPT_TEMPLATE = """
You are writing a cold outreach email on behalf of texasspecialed.com — a free resource site 
that helps Texas parents navigate the special education system (ARD meetings, evaluations, IEP 
disputes, dyslexia services, and parent rights).

First, analyze the website text below and categorize the business into exactly one of:
  1. Attorney   — Special education law firms representing parents in IEP/ARD disputes or due process.
  2. Advocate   — Independent advocates who attend ARD meetings and review IEPs (non-attorneys).
  3. Tutor      — Tutors, reading specialists, dyslexia therapists, OT, speech, or learning centers.
  4. Irrelevant — Does not fit any of the above (general law firm, unrelated business, school district, etc.)

If Irrelevant: return category "Irrelevant" and empty string for email. Stop.

If relevant, write a cold email using this exact 4-part structure. 5-7 sentences total maximum.

PART 1 — THE SCENE (1-2 sentences)
  Describe exactly what a specific parent is doing right now on the page where this ad appears.
  Be concrete and specific. Name {district}. No "I" statements. Don't mention the business yet.
  - Attorney: Parent just learned their child is being suspended. They're reading about 
    manifestation determination or due process rights, then scrolling to find an attorney.
  - Advocate: Parent has an ARD meeting in two weeks, no idea what to expect, reads the whole 
    ARD Meeting Guide, then looks for someone to come sit next to them.
  - Tutor: Parent has been quietly worried about their child's reading for months. Lands on the 
    Dyslexia Services page already convinced they need help, just looking for who to call.

PART 2 — THE OPPORTUNITY (1 sentence)
  What texasspecialed.com is, and that there is an ad placement on that exact page at that moment.

PART 3 — THE OFFER (1-2 sentences)
  Monthly price only. ROI anchor. No "just" or "only."
  - Attorney: $249/mo. One retained client covers 12 months.
  - Advocate: $59/mo (less than $2/day). One new client covers months of cost.
  - Tutor: $39/mo. One new student covers 6 months.

PART 4 — CTA (exactly this line, word for word):
  You can see exactly where your ad would appear and get started here: {advertise_url}

Sign off exactly as:
-- The Texas Special Ed Team

Rules:
- Plain text only. No HTML, markdown, bullets, or subject line.
- No greeting. Start with the scene.
- No filler ("I hope", "I wanted to reach out", "I noticed", "I'm reaching out").
- Never name the business in the body. Use "you" / "your."
- No placeholders like [Name].

Return ONLY valid JSON, no other text:
{{
  "actual_category": "Attorney" or "Advocate" or "Tutor" or "Irrelevant",
  "drafted_email": "email text or empty string"
}}

Website text for {business_name} in {district}:
{website_text}
"""


# ─── AI CALL ──────────────────────────────────────────────────────────────────
def analyze_and_draft(client, business_name: str, district: str, website_text: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(
        business_name=business_name,
        district=district,
        website_text=website_text,
        advertise_url=ADVERTISE_URL,
    )

    for attempt in range(1, AI_RETRIES + 2):
        try:
            message = client.messages.create(
                model=MODEL_NAME,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = message.content[0].text.strip()

            # Strip markdown fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            result = json.loads(raw)

            # Sanitize stray placeholders
            email = result.get('drafted_email', '')
            for p in ['[Name]', '[Your Name]', '[Business Name]']:
                email = email.replace(p, '').strip()
            result['drafted_email'] = email
            return result

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            log.warning(f"  Parse error attempt {attempt}: {e} | raw: {raw[:100] if 'raw' in dir() else ''}")
        except anthropic.RateLimitError:
            log.warning(f"  Rate limit hit. Waiting 30s...")
            time.sleep(30)
            continue
        except anthropic.APIError as e:
            log.warning(f"  API error attempt {attempt}: {e}")

        if attempt <= AI_RETRIES:
            wait = 2 ** attempt + random.uniform(0, 1)
            log.info(f"  Retrying in {wait:.1f}s...")
            time.sleep(wait)

    return {"actual_category": "Error", "drafted_email": ""}


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    with open(INPUT_CSV, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)
        original_fields = list(reader.fieldnames or [])

    total_input = len(all_rows)
    log.info(f"Loaded {total_input} rows from {INPUT_CSV}")

    all_rows = deduplicate_input(all_rows)
    log.info(f"After deduplication: {len(all_rows)} unique leads")

    completed_keys = load_completed_keys(OUTPUT_CSV)
    log.info(f"Already completed: {len(completed_keys)} rows — skipping")

    output_exists = Path(OUTPUT_CSV).exists() and len(completed_keys) > 0
    # Add Email column to output
    new_fields = original_fields + ['Scraped_Email', 'AI_Verified_Category', 'Drafted_Email']
    write_mode = 'a' if output_exists else 'w'

    processed = skipped = errors = 0

    with open(OUTPUT_CSV, mode=write_mode, newline='', encoding='utf-8-sig') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=new_fields, extrasaction='ignore')
        if not output_exists:
            writer.writeheader()

        for i, row in enumerate(all_rows, 1):
            name     = row.get('Business Name', '').strip()
            district = row.get('District', '').strip()
            key      = (name, district)

            if key in completed_keys:
                log.info(f"[{i}/{len(all_rows)}] SKIP: {name}")
                skipped += 1
                continue

            log.info(f"[{i}/{len(all_rows)}] Processing: {name} ({district})")

            url = row.get('Website', '').strip()
            website_text, scraped_email = scrape_website(url)

            row['Scraped_Email'] = scraped_email
            if scraped_email:
                log.info(f"  -> Email found: {scraped_email}")

            if not website_text:
                row['AI_Verified_Category'] = "Scrape Failed"
                row['Drafted_Email'] = ""
                writer.writerow(row)
                outfile.flush()
                errors += 1
                continue

            result = analyze_and_draft(client, name, district, website_text)
            row['AI_Verified_Category'] = result['actual_category']
            row['Drafted_Email']        = result['drafted_email']

            writer.writerow(row)
            outfile.flush()
            processed += 1

            log.info(f"  -> {result['actual_category']}")

            if i < len(all_rows):
                time.sleep(RATE_LIMIT_PAUSE)

    log.info("")
    log.info("=" * 50)
    log.info(f"  Total input    : {total_input}")
    log.info(f"  Unique leads   : {len(all_rows)}")
    log.info(f"  Processed      : {processed}")
    log.info(f"  Skipped        : {skipped}")
    log.info(f"  Scrape failed  : {errors}")
    log.info(f"  Output         : {OUTPUT_CSV}")
    log.info("=" * 50)