"""
scrape_district_contacts.py
────────────────────────────────────────────────────────────────────────────
Scrapes Texas school district websites for Special Education staff contacts.

Targets per district:
  - Executive Director of Special Education (name + email)
  - Main Special Ed Office Phone
  - Office Address
  - Dyslexia Coordinator
  - Autism Specialist
  - Evaluation Coordinator
  - Records Clerk

Strategy (tried in order per district):
  1. Check TEA's public staff directory URL pattern
  2. Search district site for /special-ed, /special-education, /sped pages
  3. Search for a /staff or /directory page filtered to special ed
  4. Fall back to Google search: site:{domain} "special education" "director"

Output:
  - contacts.csv  — one row per district, all fields
  - contacts_missing.csv — districts where key fields are still empty (for manual review)
  - scrape_log.txt — full activity log

Usage:
  python scrape_district_contacts.py

  Resume after a crash (skips already-found districts):
  python scrape_district_contacts.py --resume
"""

import os
import re
import csv
import sys
import time
import logging
import argparse
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

INPUT_CSV       = "texas_districts_data.csv"
OUTPUT_CSV      = "contacts.csv"
MISSING_CSV     = "contacts_missing.csv"
LOG_FILE        = "scrape_log.txt"

REQUEST_TIMEOUT = 12       # seconds per request
DELAY_BETWEEN   = 2.5      # seconds between districts (be polite)
MAX_PAGES       = 8        # max pages to check per district before giving up

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Fields we want in the output CSV (order matters for readability)
OUTPUT_FIELDS = [
    "district_name",
    "district_website",
    "sped_page_found",
    "exec_director_name",
    "exec_director_email",
    "main_phone",
    "office_address",
    "dyslexia_coordinator",
    "autism_specialist",
    "evaluation_coordinator",
    "records_clerk",
    "notes",
]

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# URL PATTERNS TO TRY FOR SPECIAL ED PAGES
# Ordered from most to least likely to be the right page.
# ─────────────────────────────────────────────────────────────────────────────

SPED_URL_SLUGS = [
    "/special-education",
    "/special-education/staff",
    "/special-education/contact",
    "/special-education/about",
    "/departments/special-education",
    "/departments/special-ed",
    "/sped",
    "/sped/staff",
    "/special-ed",
    "/special-ed/staff",
    "/special-services",
    "/special-services/staff",
    "/student-services/special-education",
    "/student-services/sped",
    "/academics/special-education",
    "/disability-services",
]

STAFF_URL_SLUGS = [
    "/staff",
    "/directory",
    "/our-staff",
    "/departments/staff",
    "/about/staff",
    "/contact/staff",
]

# Keywords that signal we're on the right page
SPED_PAGE_SIGNALS = [
    "special education", "sped", "individualized education",
    "iep", "ard meeting", "child find", "idea", "disability services",
]

# ─────────────────────────────────────────────────────────────────────────────
# ROLE PATTERNS — regex to identify each role from surrounding text
# Each entry: (field_name, [list_of_keyword_patterns])
# ─────────────────────────────────────────────────────────────────────────────

ROLE_PATTERNS = [
    ("exec_director_name", [
        r"executive\s+director",
        r"director\s+of\s+special\s+ed",
        r"special\s+education\s+director",
        r"director,?\s+special",
        r"dept\.?\s+head.{0,30}special",
    ]),
    ("dyslexia_coordinator", [
        r"dyslexia\s+coord",
        r"dyslexia\s+specialist",
        r"coord.{0,20}dyslexia",
    ]),
    ("autism_specialist", [
        r"autism\s+specialist",
        r"autism\s+coord",
        r"behavior\s+specialist",
        r"bcba",
        r"coord.{0,20}autism",
    ]),
    ("evaluation_coordinator", [
        r"evaluation\s+coord",
        r"assessment\s+coord",
        r"diagnostician\s+coord",
        r"coord.{0,20}eval",
        r"eval.{0,20}coord",
    ]),
    ("records_clerk", [
        r"records\s+clerk",
        r"records\s+manager",
        r"records\s+specialist",
        r"student\s+records",
        r"data\s+clerk",
    ]),
]

# ─────────────────────────────────────────────────────────────────────────────
# EXTRACTION HELPERS
# ─────────────────────────────────────────────────────────────────────────────

EMAIL_RE   = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE   = re.compile(r"\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}")
# Matches "Firstname Lastname" or "Lastname, Firstname" — at least two capitalized words
NAME_RE    = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b")


def fetch(url, session):
    """Fetch a URL, return (BeautifulSoup, final_url) or (None, None)."""
    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
            soup = BeautifulSoup(resp.text, "lxml")
            return soup, resp.url
        log.debug(f"  Non-200 ({resp.status_code}): {url}")
        return None, None
    except Exception as e:
        log.debug(f"  Fetch error {url}: {e}")
        return None, None


def is_sped_page(soup):
    """Return True if this page is likely a special education department page."""
    text = soup.get_text(" ", strip=True).lower()
    hits = sum(1 for signal in SPED_PAGE_SIGNALS if signal in text)
    return hits >= 2


def extract_emails(soup):
    """Return all emails found in the page."""
    text = soup.get_text(" ", strip=True)
    raw = EMAIL_RE.findall(text)
    # Also check href="mailto:..."
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("mailto:"):
            raw.append(href[7:].split("?")[0])
    return list(set(e.lower().strip() for e in raw))


def extract_phones(soup):
    """Return the first phone number found on the page."""
    text = soup.get_text(" ", strip=True)
    matches = PHONE_RE.findall(text)
    return matches[0].strip() if matches else ""


def extract_address(soup):
    """
    Try to find a physical address. Looks for common address patterns:
    street number + street name, or address-labeled divs.
    """
    # Try schema.org address markup first
    for tag in soup.find_all(["span", "div", "p", "address"], itemprop="streetAddress"):
        addr = tag.get_text(" ", strip=True)
        if addr:
            return addr

    # Try <address> tag
    addr_tag = soup.find("address")
    if addr_tag:
        return addr_tag.get_text(" ", strip=True)[:200]

    # Regex: "123 Main Street, City, TX 12345"
    text = soup.get_text(" ", strip=True)
    addr_re = re.compile(
        r"\d{2,5}\s+[A-Za-z][\w\s.]{5,50}(?:Street|St|Avenue|Ave|Blvd|Boulevard|Drive|Dr|Road|Rd|Lane|Ln|Way|Pkwy|Parkway)"
        r"[^,\n]{0,50}(?:TX|Texas)\s+\d{5}",
        re.IGNORECASE
    )
    m = addr_re.search(text)
    return m.group().strip() if m else ""


def find_name_near_role(text_block, role_pattern):
    """
    Given a block of text and a role regex, look for a person's name
    within 150 characters of the role keyword.
    Returns the first plausible name found, or "".
    """
    text_lower = text_block.lower()
    for pattern in role_pattern:
        m = re.search(pattern, text_lower, re.IGNORECASE)
        if m:
            # Grab surrounding context
            start = max(0, m.start() - 100)
            end   = min(len(text_block), m.end() + 150)
            context = text_block[start:end]
            names = NAME_RE.findall(context)
            # Filter out common false positives (section headers, city names, etc.)
            stop_words = {
                "Special Education", "Executive Director", "Autism Specialist",
                "Dyslexia Coordinator", "Evaluation Coordinator", "Records Clerk",
                "Main Phone", "Phone Number", "Email Address", "Office Address",
                "Texas Education", "Education Agency", "Service Center",
            }
            for name in names:
                if name not in stop_words and len(name.split()) >= 2:
                    return name
    return ""


def find_email_near_role(text_block, emails, role_patterns):
    """
    Given a block of text, look for an email near a role keyword.
    Cross-references with the list of emails found on the page.
    """
    text_lower = text_block.lower()
    for pattern in role_patterns:
        m = re.search(pattern, text_lower, re.IGNORECASE)
        if m:
            start = max(0, m.start() - 50)
            end   = min(len(text_block), m.end() + 200)
            context_lower = text_block[start:end].lower()
            for email in emails:
                if email in context_lower:
                    return email
    return ""


def scrape_staff_table(soup, result, emails):
    """
    Many district sites use HTML tables or definition lists for staff directories.
    This extracts role/name/email from table rows.
    """
    # Try tables
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        for row in rows:
            cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
            if len(cells) < 2:
                continue
            row_text = " ".join(cells).lower()
            row_emails = EMAIL_RE.findall(" ".join(cells))

            for field, patterns in ROLE_PATTERNS:
                if result.get(field):
                    continue
                for pat in patterns:
                    if re.search(pat, row_text, re.IGNORECASE):
                        # Name: usually first non-empty cell
                        for cell in cells:
                            names = NAME_RE.findall(cell)
                            if names:
                                result[field] = names[0]
                                break
                        # Email from this row
                        if field == "exec_director_name" and row_emails:
                            result["exec_director_email"] = row_emails[0].lower()
                        break

    # Try definition lists / card-style divs common in modern district CMSes
    for container in soup.find_all(["div", "article", "li", "section"],
                                    class_=re.compile(r"staff|card|person|member|contact", re.I)):
        block_text = container.get_text(" ", strip=True)
        block_lower = block_text.lower()
        block_emails = EMAIL_RE.findall(block_text)

        for field, patterns in ROLE_PATTERNS:
            if result.get(field):
                continue
            for pat in patterns:
                if re.search(pat, block_lower, re.IGNORECASE):
                    names = NAME_RE.findall(block_text)
                    stop_words = {"Special Education", "Executive Director", "Dyslexia Coordinator"}
                    for name in names:
                        if name not in stop_words and len(name.split()) >= 2:
                            result[field] = name
                            break
                    if field == "exec_director_name" and block_emails and not result.get("exec_director_email"):
                        result["exec_director_email"] = block_emails[0].lower()
                    break


def scrape_free_text(soup, result, emails):
    """
    Fallback: scan all page text for role keywords and grab nearby names/emails.
    """
    full_text = soup.get_text(" ", strip=True)

    for field, patterns in ROLE_PATTERNS:
        if not result.get(field):
            result[field] = find_name_near_role(full_text, patterns)

    if not result.get("exec_director_email") and result.get("exec_director_name"):
        result["exec_director_email"] = find_email_near_role(
            full_text, emails, [p for _, p in ROLE_PATTERNS[:1]]
        )

    if not result.get("main_phone"):
        result["main_phone"] = extract_phones(soup)

    if not result.get("office_address"):
        result["office_address"] = extract_address(soup)


# ─────────────────────────────────────────────────────────────────────────────
# DISTRICT WEBSITE FINDER
# Most ISD websites follow predictable patterns.
# ─────────────────────────────────────────────────────────────────────────────

def guess_district_domains(district_name):
    """
    Generate likely domain names to try for a given district.
    Texas ISDs almost always end in .net or .org.
    """
    # Normalize: "Katy ISD" -> "katy", "Cypress-Fairbanks ISD" -> "cfisd"
    name = district_name.lower()
    name = re.sub(r'\s+(isd|cisd|csd)$', '', name).strip()

    # Short slug: remove hyphens and spaces
    slug = re.sub(r'[\s\-]+', '', name)
    # Hyphenated slug
    slug_hyph = re.sub(r'\s+', '-', name)
    # Abbreviation for compound names (e.g. "cypress-fairbanks" -> "cfisd")
    parts = re.split(r'[\s\-]+', name)
    abbr = ''.join(p[0] for p in parts if p)

    domains = []
    for base in [slug, slug_hyph, abbr]:
        for tld in [".net", ".org", ".edu", ".com"]:
            for prefix in ["www.", ""]:
                domains.append(f"https://{prefix}{base}{tld}")
                domains.append(f"https://{prefix}{base}isd{tld}")

    # Also try: katy-isd.org, katyisd.org, katyisd.net
    return domains


def find_district_website(district_name, session):
    """
    Try to find the district's main website by probing likely domains.
    Returns the working base URL or None.
    """
    log.info(f"  Finding website for: {district_name}")
    for url in guess_district_domains(district_name):
        try:
            resp = session.get(url, timeout=8, allow_redirects=True)
            if resp.status_code == 200:
                final = resp.url
                # Sanity check: make sure it looks like a school site
                text_lower = resp.text.lower()
                if any(kw in text_lower for kw in ["school", "district", "isd", "student", "parent"]):
                    log.info(f"  Found: {final}")
                    return final
        except Exception:
            continue
    return None


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SCRAPER PER DISTRICT
# ─────────────────────────────────────────────────────────────────────────────

def scrape_district(district_name, session):
    result = {field: "" for field in OUTPUT_FIELDS}
    result["district_name"] = district_name

    # ── Step 1: Find the district website ─────────────────────────
    base_url = find_district_website(district_name, session)
    if not base_url:
        result["notes"] = "Could not find district website"
        log.warning(f"  No website found for {district_name}")
        return result

    domain = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
    result["district_website"] = domain

    # ── Step 2: Find the special education page ────────────────────
    sped_soup = None
    sped_url  = None
    pages_checked = 0

    for slug in SPED_URL_SLUGS:
        if pages_checked >= MAX_PAGES:
            break
        url = domain + slug
        soup, final_url = fetch(url, session)
        pages_checked += 1
        if soup and is_sped_page(soup):
            sped_soup = soup
            sped_url  = final_url
            result["sped_page_found"] = final_url
            log.info(f"  SpEd page: {final_url}")
            break
        time.sleep(0.3)

    # ── Step 3: If no dedicated sped page, try staff/directory pages
    if not sped_soup:
        for slug in STAFF_URL_SLUGS:
            if pages_checked >= MAX_PAGES:
                break
            url = domain + slug
            soup, final_url = fetch(url, session)
            pages_checked += 1
            if soup:
                text_lower = soup.get_text(" ", strip=True).lower()
                if "special education" in text_lower or "sped" in text_lower:
                    sped_soup = soup
                    sped_url  = final_url
                    result["sped_page_found"] = final_url
                    log.info(f"  Staff page with SpEd content: {final_url}")
                    break
            time.sleep(0.3)

    # ── Step 4: Also check for links TO a sped page from homepage ──
    if not sped_soup:
        home_soup, _ = fetch(domain, session)
        if home_soup:
            for a in home_soup.find_all("a", href=True):
                href = a["href"].lower()
                text = a.get_text().lower()
                if any(kw in href or kw in text for kw in
                       ["special-ed", "special_ed", "sped", "special education"]):
                    full_url = urljoin(domain, a["href"])
                    soup, final_url = fetch(full_url, session)
                    if soup and is_sped_page(soup):
                        sped_soup = soup
                        result["sped_page_found"] = final_url
                        log.info(f"  Linked SpEd page: {final_url}")
                        break

    if not sped_soup:
        result["notes"] = "Special ed page not found — manual review needed"
        log.warning(f"  No SpEd page found for {district_name}")
        return result

    # ── Step 5: Extract data from the sped page ────────────────────
    all_emails = extract_emails(sped_soup)
    log.info(f"  Found {len(all_emails)} emails on page")

    # Try structured extraction first (tables, cards)
    scrape_staff_table(sped_soup, result, all_emails)

    # Fill any remaining gaps with free-text extraction
    scrape_free_text(sped_soup, result, all_emails)

    # If exec director email is still empty but we have one email, use it
    if not result["exec_director_email"] and len(all_emails) == 1:
        result["exec_director_email"] = all_emails[0]

    # ── Step 6: Check linked staff sub-pages if fields still missing
    if not result["exec_director_name"]:
        for a in sped_soup.find_all("a", href=True):
            href_lower = a["href"].lower()
            text_lower = a.get_text().lower()
            if any(kw in href_lower or kw in text_lower
                   for kw in ["staff", "directory", "contact", "team", "personnel"]):
                full_url = urljoin(sped_url, a["href"])
                sub_soup, _ = fetch(full_url, session)
                if sub_soup:
                    sub_emails = extract_emails(sub_soup)
                    scrape_staff_table(sub_soup, result, sub_emails)
                    scrape_free_text(sub_soup, result, sub_emails)
                    break

    log.info(
        f"  Result: director='{result['exec_director_name']}' "
        f"email='{result['exec_director_email']}' "
        f"phone='{result['main_phone']}'"
    )
    return result


# ─────────────────────────────────────────────────────────────────────────────
# CSV HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def load_already_scraped(output_csv):
    """Returns a set of district names already present in the output CSV."""
    done = set()
    if os.path.exists(output_csv):
        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                done.add(row.get("district_name", "").strip())
    return done


def append_row(output_csv, row):
    file_exists = os.path.exists(output_csv)
    with open(output_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def write_missing_report(all_results, missing_csv):
    key_fields = ["exec_director_name", "exec_director_email", "main_phone"]
    missing = [r for r in all_results if not any(r.get(f) for f in key_fields)]
    if not missing:
        log.info("No missing records to report.")
        return
    with open(missing_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(missing)
    log.info(f"Missing report: {len(missing)} districts → {missing_csv}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def parse_input_csv(input_csv):
    """Read district names from the texas_districts_data.csv."""
    districts = []
    with open(input_csv, "r", encoding="utf-8-sig") as f:
        for line in f.readlines()[1:]:   # skip header
            line = line.strip()
            if not line:
                continue
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]
            parts = line.split(",")
            if parts:
                name = parts[0].strip()
                if name and not name.isdigit():
                    districts.append(name)
    return districts


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true",
                        help="Skip districts already in contacts.csv")
    parser.add_argument("--district", type=str, default=None,
                        help="Scrape a single district by name for testing")
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update(HEADERS)

    # ── Single district test mode ──────────────────────────────────
    if args.district:
        log.info(f"Single district test: {args.district}")
        result = scrape_district(args.district, session)
        for k, v in result.items():
            print(f"  {k:<30} {v}")
        sys.exit(0)

    # ── Full run ───────────────────────────────────────────────────
    districts = parse_input_csv(INPUT_CSV)
    log.info(f"Loaded {len(districts)} districts from {INPUT_CSV}")

    already_done = load_already_scraped(OUTPUT_CSV) if args.resume else set()
    if already_done:
        log.info(f"Resuming — {len(already_done)} districts already scraped.")

    all_results = []
    skipped = 0
    scraped = 0

    for i, district_name in enumerate(districts, 1):
        if district_name in already_done:
            log.info(f"[{i}/{len(districts)}] SKIP (already done): {district_name}")
            skipped += 1
            continue

        log.info(f"[{i}/{len(districts)}] Scraping: {district_name}")

        try:
            result = scrape_district(district_name, session)
        except Exception as e:
            log.error(f"  Unexpected error for {district_name}: {e}")
            result = {f: "" for f in OUTPUT_FIELDS}
            result["district_name"] = district_name
            result["notes"] = f"Scrape error: {e}"

        all_results.append(result)
        append_row(OUTPUT_CSV, result)    # write immediately so crashes don't lose data
        scraped += 1

        # Progress summary every 10 districts
        if scraped % 10 == 0:
            found = sum(1 for r in all_results if r.get("exec_director_name"))
            log.info(f"  Progress: {scraped} scraped, {found} with director names found.")

        time.sleep(DELAY_BETWEEN)

    # ── Final report ───────────────────────────────────────────────
    write_missing_report(all_results, MISSING_CSV)

    found_name    = sum(1 for r in all_results if r.get("exec_director_name"))
    found_email   = sum(1 for r in all_results if r.get("exec_director_email"))
    found_phone   = sum(1 for r in all_results if r.get("main_phone"))
    found_dyslexia = sum(1 for r in all_results if r.get("dyslexia_coordinator"))

    print("\n" + "="*60)
    print(f"SCRAPE COMPLETE")
    print(f"  Districts scraped : {scraped}")
    print(f"  Already skipped   : {skipped}")
    print(f"  Director name     : {found_name}/{scraped}")
    print(f"  Director email    : {found_email}/{scraped}")
    print(f"  Main phone        : {found_phone}/{scraped}")
    print(f"  Dyslexia coord    : {found_dyslexia}/{scraped}")
    print(f"  Output            : {OUTPUT_CSV}")
    print(f"  Missing report    : {MISSING_CSV}")
    print(f"  Full log          : {LOG_FILE}")
    print("="*60)