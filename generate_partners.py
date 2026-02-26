"""
generate_partners.py
────────────────────
Generates partners.html for every district folder under DISTRICTS_DIR.

Data sources (checked in priority order):
  1. DISTRICT_OVERRIDES dict  — manually verified contacts
  2. leadership-directory.html — auto-extracts name, phone, contact table
  3. index.html / other pages  — fallback for name and phone
  4. extracted_resources.csv   — existing free-resource cards, converted to
                                  new CSS classes automatically (all 120 covered)
  5. Hard defaults             — folder-name to display name, region keyword guess

Usage:
    pip install beautifulsoup4
    python generate_partners.py

Set OVERWRITE = True to regenerate files that already exist.
"""

import csv
import re
from pathlib import Path
from bs4 import BeautifulSoup

# ── CONFIG ────────────────────────────────────────────────────────────────────
DISTRICTS_DIR = Path(r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts")
RESOURCES_CSV = DISTRICTS_DIR.parent / "extracted_resources.csv"   # auto-detected from project root
OVERWRITE     = True  # True = regenerate all, False = skip existing
# ─────────────────────────────────────────────────────────────────────────────


# ── DISTRICT OVERRIDES (verified contact data) ────────────────────────────────
DISTRICT_OVERRIDES = {
    "aldine-isd": {
        "name":       "Aldine ISD",
        "region":     "Houston Area",
        "phone":      "281.985.6053",
        "phone_href": "2819856053",
        "sped_url":   "https://www.aldineisd.org/departments/special-education/",
        "contacts": [
            {"role": "Exec. Director, Spec. Ed.", "name": "tybailey@aldineisd.org"},
            {"role": "Dyslexia Coordinator",      "name": "Kimberly Sinclair"},
            {"role": "Evaluation Coordinator",    "name": ""},
            {"role": "Records Request",            "name": ""},
        ],
    },
    "wichita-falls-isd": {
        "name":       "Wichita Falls ISD",
        "region":     "North Texas",
        "phone":      "940.235.1000",
        "phone_href": "9402351000",
        "sped_url":   "https://www.wfisd.net/domain/49",
        "contacts": [
            {"role": "Exec. Director, Spec. Ed.", "name": ""},
            {"role": "Dyslexia Coordinator",      "name": ""},
            {"role": "Evaluation Coordinator",    "name": ""},
            {"role": "Records Request",            "name": ""},
        ],
    },
    # Add more districts here as you verify their contact data
}


# ── REGION LOOKUP ─────────────────────────────────────────────────────────────
REGION_DEFAULTS = {
    "houston": "Houston Area",     "aldine": "Houston Area",
    "cypress": "Houston Area",     "katy": "Houston Area",
    "fort-bend": "Houston Area",   "conroe": "Houston Area",
    "alief": "Houston Area",       "spring": "Houston Area",
    "humble": "Houston Area",      "pasadena": "Houston Area",
    "galveston": "Houston Area",   "clear-creek": "Houston Area",
    "dallas": "Dallas–Fort Worth", "frisco": "Dallas–Fort Worth",
    "plano": "Dallas–Fort Worth",  "lewisville": "Dallas–Fort Worth",
    "irving": "Dallas–Fort Worth", "garland": "Dallas–Fort Worth",
    "arlington": "Dallas–Fort Worth", "allen": "Dallas–Fort Worth",
    "mckinney": "Dallas–Fort Worth",  "denton": "Dallas–Fort Worth",
    "mansfield": "Dallas–Fort Worth", "grand-prairie": "Dallas–Fort Worth",
    "austin": "Central Texas",     "round-rock": "Central Texas",
    "pflugerville": "Central Texas",  "bastrop": "Central Texas",
    "hays": "Central Texas",       "killeen": "Central Texas",
    "temple": "Central Texas",     "waco": "Central Texas",
    "san-antonio": "San Antonio Area", "northside": "San Antonio Area",
    "northeast": "San Antonio Area",   "south-san": "San Antonio Area",
    "el-paso": "El Paso",          "ysleta": "El Paso",
    "wichita": "North Texas",      "amarillo": "Panhandle",
    "lubbock": "West Texas",       "abilene": "West Texas",
    "midland": "West Texas",       "odessa": "West Texas",
    "corpus": "Coastal Bend",      "laredo": "South Texas",
    "mcallen": "Rio Grande Valley","edinburg": "Rio Grande Valley",
    "harlingen": "Rio Grande Valley", "mission": "Rio Grande Valley",
    "beaumont": "Southeast Texas", "port-arthur": "Southeast Texas",
    "tyler": "East Texas",         "longview": "East Texas",
    "lufkin": "East Texas",        "nacogdoches": "East Texas",
}


# ── LOAD CSV ──────────────────────────────────────────────────────────────────
def load_resources_csv(csv_path: Path) -> dict:
    """Returns {slug: html_block_string} for all 120 districts."""
    if not csv_path.exists():
        print(f"WARNING: Resources CSV not found at {csv_path}\n"
              f"  Free resources will use fallback for all districts.")
        return {}
    resources = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            resources[row["DistrictSlug"].strip()] = row["HTMLBlock"]
    print(f"Loaded free resources for {len(resources)} districts from CSV\n")
    return resources


# ── CONVERT OLD HTML → NEW CSS CLASSES ───────────────────────────────────────
def convert_resources_html(raw_html: str) -> str:
    """
    Parses the old free-resources HTML (banner-national / banner-texas /
    banner-local with frc-* classes) and re-renders with new tier-* /
    free-card / free-card-* CSS classes from style-additions.css.
    Preserves all existing district-specific cards exactly as-is.
    """
    soup = BeautifulSoup(raw_html, "html.parser")

    banner_map = {
        "banner-national": ("tier-national", "fas fa-flag-usa",       "National Resources"),
        "banner-texas":    ("tier-texas",    "fas fa-star",            "Texas State Resources"),
        "banner-local":    ("tier-local",    "fas fa-map-marker-alt",  "Local Resources"),
    }

    tiers_html = []

    for old_cls, (new_cls, hdr_icon, default_label) in banner_map.items():
        banner = soup.find(class_=old_cls)
        if not banner:
            continue

        # Extract header text (e.g. "Local Resources — Houston Area")
        header_el = banner.find(class_="free-banner-header")
        if header_el:
            for tag in header_el.find_all("i"):
                tag.decompose()
            label = header_el.get_text(strip=True) or default_label
        else:
            label = default_label

        # Convert each resource card
        cards_html = []
        for card in banner.find_all(class_="free-resource-card"):
            href = card.get("href", "#")

            icon_wrap = card.find(class_="frc-icon")
            i_tag     = icon_wrap.find("i") if icon_wrap else None
            icon_cls  = " ".join(i_tag.get("class", ["fas", "fa-link"])) if i_tag else "fas fa-link"

            name_el = card.find(class_="frc-name")
            desc_el = card.find(class_="frc-desc")
            name = name_el.get_text(strip=True) if name_el else ""
            desc = desc_el.get_text(strip=True) if desc_el else ""

            cards_html.append(
                f'          <a class="free-card" href="{href}" target="_blank" rel="noopener">\n'
                f'            <div class="free-card-icon"><i class="{icon_cls}"></i></div>\n'
                f'            <div class="free-card-text">\n'
                f'              <strong>{name}</strong>\n'
                f'              <span>{desc}</span>\n'
                f'            </div>\n'
                f'            <i class="fas fa-external-link-alt free-card-arrow"></i>\n'
                f'          </a>'
            )

        if not cards_html:
            continue

        tiers_html.append(
            f'      <div class="resource-tier {new_cls}">\n'
            f'        <div class="tier-header"><i class="{hdr_icon}"></i> {label}</div>\n'
            f'        <div class="tier-body">\n'
            + "\n".join(cards_html) + "\n"
            f'        </div>\n'
            f'      </div>'
        )

    return "\n".join(tiers_html)


# ── HTML EXTRACTION FROM EXISTING FILES ───────────────────────────────────────
def extract_from_html(directory: Path) -> dict:
    data = {}
    for filename in ["leadership-directory.html", "index.html"]:
        filepath = directory / filename
        if not filepath.exists():
            continue
        soup = BeautifulSoup(
            filepath.read_text(encoding="utf-8", errors="ignore"), "html.parser"
        )

        # District name from <h1>
        if not data.get("name"):
            h1 = soup.find("h1")
            if h1:
                text = h1.get_text(strip=True)
                for suffix in [
                    "Special Education Staff Directory", "Special Education Services",
                    "ARD Meeting Guide:", "Dyslexia Services in",
                    "Requesting an Evaluation in", "Dispute & Discipline Rights in",
                ]:
                    text = text.replace(suffix, "").strip(": ")
                if text:
                    data["name"] = text

        # Phone from any tel: link
        if not data.get("phone"):
            for tag in soup.find_all("a", href=re.compile(r"^tel:")):
                digits = re.sub(r"\D", "", tag["href"])
                if len(digits) >= 10:
                    d10 = digits[-10:]
                    data["phone"]      = f"{d10[0:3]}.{d10[3:6]}.{d10[6:10]}"
                    data["phone_href"] = d10
                    break

        # Contacts from table rows in leadership-directory.html
        if filename == "leadership-directory.html" and not data.get("contacts"):
            contacts = []
            for row in soup.select("table tbody tr"):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    role = cells[0].get_text(strip=True)
                    name = cells[1].get_text(strip=True)
                    if any(x in name.lower() for x in ["not on file", "check district"]):
                        name = ""
                    contacts.append({"role": role, "name": name})
            if contacts:
                data["contacts"] = contacts[:4]

        # District SPED URL
        if not data.get("sped_url"):
            for a in soup.find_all("a", href=True):
                if "special-education" in a["href"] and a["href"].startswith("http"):
                    data["sped_url"] = a["href"]
                    break

        if data:
            break

    return data


def guess_region(folder_name: str) -> str:
    for key, region in REGION_DEFAULTS.items():
        if key in folder_name:
            return region
    return "Texas"


def folder_to_display_name(folder_name: str) -> str:
    return (folder_name.replace("-", " ").title()
            .replace("Isd", "ISD").replace("Cisd", "CISD"))


def build_district_data(folder_name: str, directory: Path) -> dict:
    base = dict(DISTRICT_OVERRIDES.get(folder_name, {}))
    for key, value in extract_from_html(directory).items():
        if key not in base or not base[key]:
            base[key] = value
    base.setdefault("name",       folder_to_display_name(folder_name))
    base.setdefault("region",     guess_region(folder_name))
    base.setdefault("phone",      "")
    base.setdefault("phone_href", "")
    base.setdefault("sped_url",   "#")
    base.setdefault("contacts", [
        {"role": "Exec. Director, Spec. Ed.", "name": ""},
        {"role": "Dyslexia Coordinator",      "name": ""},
        {"role": "Evaluation Coordinator",    "name": ""},
        {"role": "Records Request",            "name": ""},
    ])
    base["slug"] = folder_name
    return base


# ── PAGE RENDERER ─────────────────────────────────────────────────────────────
def render_page(d: dict, resources_tiers_html: str) -> str:
    name       = d["name"]
    region     = d["region"]
    phone      = d["phone"]
    phone_href = d["phone_href"]
    slug       = d["slug"]

    phone_stat = (
        f'<div class="hero-stat"><i class="fas fa-phone"></i>'
        f'SPED Office: <a href="tel:{phone_href}">{phone}</a></div>'
        if phone else ""
    )

    contacts_html = "\n".join(
        f'        <div class="contact-cell">\n'
        f'          <span class="contact-role">{c["role"]}</span>\n'
        f'          <span class="{"contact-name" if c["name"] else "contact-name contact-name-empty"}">'
        f'{c["name"] if c["name"] else "Not on file — check district site"}</span>\n'
        f'          {"<span class=\"contact-phone\"><a href=\"tel:" + phone_href + "\">" + phone + "</a></span>" if phone else ""}\n'
        f'        </div>'
        for c in d["contacts"]
    )

    if not resources_tiers_html.strip():
        resources_tiers_html = (
            f'      <div class="resource-tier tier-local">\n'
            f'        <div class="tier-header"><i class="fas fa-map-marker-alt"></i> Local Resources &mdash; {region}</div>\n'
            f'        <div class="tier-body">\n'
            f'          <a class="free-card" href="{d["sped_url"]}" target="_blank" rel="noopener">\n'
            f'            <div class="free-card-icon"><i class="fas fa-school"></i></div>\n'
            f'            <div class="free-card-text">\n'
            f'              <strong>{name} Special Education Dept.</strong>\n'
            f'              <span>Official resources and information from the district.</span>\n'
            f'            </div>\n'
            f'            <i class="fas fa-external-link-alt free-card-arrow"></i>\n'
            f'          </a>\n'
            f'        </div>\n'
            f'      </div>'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Special Education Services &amp; Support in {name} | Texas Special Ed</title>
<meta content="Need special education help in {name}? Find IEP guides, evaluation timelines, and local advocates in Texas." name="description"/>
<link href="https://www.texasspecialed.com/districts/{slug}/partners" rel="canonical"/>
<meta content="Special Education Services &amp; Support in {name} | Texas Special Ed" property="og:title"/>
<meta content="https://texasspecialed.com/districts/{slug}/partners.html" property="og:url"/>
<meta content="article" property="og:type"/>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet"/>
<link href="/style.css" rel="stylesheet"/>
</head>
<body>

<header class="site-header">
  <nav aria-label="Main navigation" class="navbar" role="navigation">
    <div class="nav-container">
      <div class="nav-logo">
        <a aria-label="Texas Special Ed Home" href="/">
          <img alt="Texas Special Ed" height="auto" src="/images/texasspecialed-logo.png" width="200"/>
        </a>
      </div>
      <button aria-expanded="false" aria-label="Toggle menu" class="mobile-menu-toggle">
        <span class="hamburger"></span>
        <span class="hamburger"></span>
        <span class="hamburger"></span>
      </button>
      <ul class="nav-menu">
        <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
        <li class="nav-item dropdown">
          <a aria-haspopup="true" class="nav-link dropdown-toggle" href="/districts/index.html">Districts <span class="dropdown-arrow">&#9660;</span></a>
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
            <li><a class="view-all-link" href="/districts/index.html">View All 120+ Districts &rarr;</a></li>
          </ul>
        </li>
        <li class="nav-item"><a class="nav-link" href="/resources/index.html">Parent Resources</a></li>
        <li class="nav-item"><a class="nav-link" href="/blog/index.html">Blog</a></li>
        <li class="nav-item"><a class="nav-link" href="/about/index.html">About</a></li>
        <li class="nav-item"><a class="nav-link" href="/contact/index.html">Contact</a></li>
        <li class="nav-item nav-cta">
          <a class="btn-outline" href="/resources/ard-checklist.pdf" target="_blank">Free ARD Checklist</a>
        </li>
      </ul>
    </div>
  </nav>
</header>

<section class="page-hero-dark">
  <div class="container">
    <span class="label label-gold">{name} &middot; {region}</span>
    <h1>Special Education Services<br/>in {name}</h1>
    <p class="hero-sub">A parent resource guide for IEPs, evaluations, and connecting with local providers who know Texas special education law.</p>
    <div class="hero-stats">
      {phone_stat}
      <div class="hero-stat">
        <i class="fas fa-address-book"></i>
        <a href="leadership-directory.html">Full Staff Directory</a>
      </div>
    </div>
  </div>
</section>

<main>
  <div class="container">

    <div class="silo-nav">
      <strong>{name} Resources:</strong>
      <a href="index.html">District Home</a>
      <a href="ard-process-guide.html">ARD Guide</a>
      <a href="evaluation-child-find.html">Evaluations (FIE)</a>
      <a href="dyslexia-services.html">Dyslexia / 504</a>
      <a href="grievance-dispute-resolution.html">Dispute Resolution</a>
      <a href="partners.html">Providers &amp; Support</a>
    </div>

    <div class="trust-anchor">
      <strong>Hi, I'm a Texas parent of a 2e child.</strong> When I watched the school system fail her, I realized how broken the process is. I built this resource to help parents like you get the support your child deserves. You are not alone.
    </div>

    <hr class="divider" style="margin:8px 0 40px;"/>

    <div class="featured-ad-zone">
      <span class="ad-badge-premium">District Exclusive</span>
      <div class="ad-logo-box">
        <i class="fas fa-building"></i>
        <span>Your Logo</span>
      </div>
      <div class="ad-content">
        <span class="label label-gold">Featured Partner</span>
        <h3>Position your practice as the trusted authority in {name}</h3>
        <p>Capture high-intent parents seeking IEE evaluations, autism diagnosis, or advocacy support &mdash; right at the moment they need guidance most. One exclusive listing per district.</p>
        <div class="ad-tags">
          <span class="ad-tag">IEE Evaluations</span>
          <span class="ad-tag">Advocacy</span>
          <span class="ad-tag">Autism Diagnosis</span>
          <span class="ad-tag">Legal Support</span>
        </div>
      </div>
      <a class="btn-claim" href="https://www.texasspecialed.com/advertise/index.html">
        Reserve This Spot <i class="fas fa-arrow-right" style="font-size:.75rem;"></i>
      </a>
    </div>

    <div class="contact-panel">
      <div class="contact-panel-header">
        <i class="fas fa-address-book"></i> Who Do I Call in {name}?
      </div>
      <div class="contact-panel-body">
{contacts_html}
      </div>
    </div>

    <div class="insight-box">
      <div class="insight-icon"><i class="fas fa-lightbulb"></i></div>
      <div class="insight-text">
        <h4>{name} offers these services for free</h4>
        <p>The district provides inclusion programs so students with disabilities learn alongside their peers, plus extended school year (ESY) services to prevent regression over summer break.</p>
      </div>
    </div>

    <div class="section-title-row">
      <h2>Navigating Special Ed in {name}</h2>
      <span>Key rights to know</span>
    </div>
    <div class="process-strip">
      <div class="process-item">
        <div class="process-num">1</div>
        <div class="process-body">
          <h4>IEP Placement Matters</h4>
          <p>Understand your rights regarding Least Restrictive Environment (LRE) placement decisions and when to push back.</p>
        </div>
      </div>
      <div class="process-item">
        <div class="process-num">2</div>
        <div class="process-body">
          <h4>Independent Evaluations</h4>
          <p>You have the right to request an Independent Educational Evaluation (IEE) at public expense if you disagree with the district&rsquo;s FIE.</p>
        </div>
      </div>
      <div class="process-item">
        <div class="process-num">3</div>
        <div class="process-body">
          <h4>Transition Planning</h4>
          <p>Begin transition planning meetings by age 14 in Texas. These shape post-secondary goals, vocational training, and independent living plans.</p>
        </div>
      </div>
    </div>

    <div class="section-title-row mt-56">
      <h2>Advocates &amp; ARD Support</h2>
      <span>Local area providers</span>
    </div>
    <div class="ad-slot-card">
      <div class="ad-slot-logo"><i class="fas fa-user-tie fa-lg"></i></div>
      <div class="ad-slot-content">
        <h4>Your Advocacy Firm</h4>
        <p>Be the first advocate parents call when they hit a wall with the district. High-intent placement, exclusive to this category.</p>
      </div>
      <a href="https://www.texasspecialed.com/advertise/index.html" class="ad-slot-cta">
        Claim this listing <i class="fas fa-chevron-right" style="font-size:.65rem;"></i>
      </a>
    </div>

    <div class="section-title-row mt-48">
      <h2>Special Education Attorneys</h2>
      <span>Legal representation &amp; due process</span>
    </div>
    <div class="ad-slot-card">
      <div class="ad-slot-logo"><i class="fas fa-scale-balanced fa-lg"></i></div>
      <div class="ad-slot-content">
        <h4>Your Law Firm</h4>
        <p>Position your firm as the go-to legal defense for families navigating due process, mediation, or TEA complaints.</p>
      </div>
      <a href="https://www.texasspecialed.com/advertise/index.html" class="ad-slot-cta">
        Claim this listing <i class="fas fa-chevron-right" style="font-size:.65rem;"></i>
      </a>
    </div>

    <div class="section-title-row mt-48">
      <h2>Independent Evaluators</h2>
      <span>IEE, psychoeducational &amp; specialty</span>
    </div>
    <div class="ad-slot-card">
      <div class="ad-slot-logo"><i class="fas fa-brain fa-lg"></i></div>
      <div class="ad-slot-content">
        <h4>Your Evaluation Practice</h4>
        <p>Reach parents weighing an independent second opinion after the district&rsquo;s FIE is complete.</p>
      </div>
      <a href="https://www.texasspecialed.com/advertise/index.html" class="ad-slot-cta">
        Claim this listing <i class="fas fa-chevron-right" style="font-size:.65rem;"></i>
      </a>
    </div>

  </div>

  <div class="container">
    <div class="partner-cta-band">
      <div class="partner-cta-copy">
        <span class="label label-muted">For Practices &amp; Firms</span>
        <h2>Why Partner With Texas Special Ed?</h2>
        <p>We are the only independent, data-driven resource hub for Texas special education parents. Our pages capture high-intent traffic from families actively seeking evaluations and legal support &mdash; often within hours of an ARD meeting.</p>
      </div>
      <a href="https://www.texasspecialed.com/advertise/index.html" class="btn-partner">
        Become a Partner <i class="fas fa-arrow-right" style="font-size:.75rem;"></i>
      </a>
    </div>
  </div>

  <div class="container">
    <section class="free-resources-section">
      <div class="free-resources-intro">
        <span class="label label-green">No cost to families</span>
        <h2>Free &amp; Non-Profit Resources</h2>
      </div>
{resources_tiers_html}
    </section>
  </div>

</main>

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
        <li><a href="/districts/index.html">View All Districts &rarr;</a></li>
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
    <p>&copy; 2026 Texas Special Education Resources. All rights reserved. Not affiliated with the TEA or any school district.</p>
  </div>
</footer>

<script>
document.addEventListener('DOMContentLoaded', function() {{
  var toggle = document.querySelector('.mobile-menu-toggle');
  var menu   = document.querySelector('.nav-menu');
  if (toggle && menu) {{
    toggle.addEventListener('click', function() {{
      menu.classList.toggle('active');
      toggle.setAttribute('aria-expanded', menu.classList.contains('active'));
    }});
  }}
  document.querySelectorAll('.dropdown-toggle').forEach(function(drop) {{
    drop.addEventListener('click', function(e) {{
      if (window.innerWidth <= 900) {{
        e.preventDefault();
        this.parentElement.classList.toggle('active');
      }}
    }});
  }});
}});
</script>

</body>
</html>"""


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not DISTRICTS_DIR.exists():
        print(f"ERROR: Districts directory not found:\n  {DISTRICTS_DIR}")
        raise SystemExit(1)

    all_resources = load_resources_csv(RESOURCES_CSV)

    folders = sorted([
        f for f in DISTRICTS_DIR.iterdir()
        if f.is_dir() and not f.name.startswith(".")
    ])
    print(f"Found {len(folders)} district folders\n")

    created, skipped, errors = [], [], []

    for folder in folders:
        out_path = folder / "partners.html"

        if out_path.exists() and not OVERWRITE:
            skipped.append(folder.name)
            continue

        try:
            d = build_district_data(folder.name, folder)

            raw = all_resources.get(folder.name, "")
            resources_html = convert_resources_html(raw) if raw else ""

            html = render_page(d, resources_html)
            out_path.write_text(html, encoding="utf-8")
            created.append(folder.name)

            src = "CSV" if raw else "fallback"
            print(f"  ✓  {folder.name}  (resources: {src})")

        except Exception as e:
            errors.append((folder.name, str(e)))
            print(f"  ✗  {folder.name}  →  {e}")

    print(f"\n── Summary ───────────────────────────────────────────")
    print(f"  Created : {len(created)}")
    print(f"  Skipped : {len(skipped)}  (set OVERWRITE=True to regenerate)")
    print(f"  Errors  : {len(errors)}")
    if errors:
        print("\nFailed districts:")
        for name, err in errors:
            print(f"  {name}: {err}")