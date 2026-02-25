"""
generate_free_resources.py
─────────────────────────────────────────────────────────────
Uses Vertex AI (Gemini) to research free / non-profit special-
education resources for each Texas ISD and injects a three-
banner "Free Resources" section (National · Texas · Local)
into every district partner page.

USAGE
──────
1.  pip install google-cloud-aiplatform beautifulsoup4 lxml
2.  gcloud auth application-default login   (or set GOOGLE_APPLICATION_CREDENTIALS)
3.  Edit CONFIG below
4.  python generate_free_resources.py

OUTPUT
──────
One updated HTML file per district written to OUTPUT_DIR.
A summary CSV (resources_found.csv) listing every resource discovered.
"""

import os
import re
import csv
import json
import time
import logging
from pathlib import Path
from bs4 import BeautifulSoup

# ── Vertex AI ──────────────────────────────────────────────
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# ══════════════════════════════════════════════════════════
#  CONFIG — edit these before running
# ══════════════════════════════════════════════════════════
CONFIG = {
    "GCP_PROJECT":    "texasspecialed",            # Project ID
    "GCP_PROJECT_NUM": "196104920649",             # Project Number
    "GCP_LOCATION":   "us-central1",               # Gemini region
    "MODEL":          "gemini-2.0-flash-001",      # Gemini 2.0 Flash
    "PARTNERS_DIR":   "./districts",               # root folder of partner HTML files
    "OUTPUT_DIR":     "./districts_updated",       # where to write updated files
    "SLEEP_BETWEEN":  2,                           # seconds between API calls
    "MAX_RETRIES":    3,
}

# ── District data (from your CSV paste) ──────────────────
DISTRICT_RAW = """Houston ISD,175777,Houston
Dallas ISD,139046,Dallas
Cypress-Fairbanks ISD,118010,Houston (Northwest)
Northside ISD,101095,San Antonio
Katy ISD,96119,Katy
Fort Bend ISD,80985,Sugar Land
IDEA Public Schools,80246,Weslaco (Statewide)
Conroe ISD,73380,Conroe
Austin ISD,72830,Austin
Fort Worth ISD,71060,Fort Worth
Frisco ISD,67327,Frisco
Aldine ISD,57844,Houston (North)
North East ISD,57374,San Antonio
Arlington ISD,54750,Arlington
Klein ISD,54082,Klein
Garland ISD,51659,Garland
El Paso ISD,49139,El Paso
Lewisville ISD,48440,Lewisville
Plano ISD,47899,Plano
Pasadena ISD,47486,Pasadena
Humble ISD,47460,Humble
Socorro ISD,47020,El Paso (Socorro)
Round Rock ISD,46197,Round Rock
San Antonio ISD,44670,San Antonio
Killeen ISD,43760,Killeen
Lamar CISD,43620,Rosenberg
United ISD,40950,Laredo
Alief ISD,39474,Houston (West)
Mansfield ISD,35660,Mansfield
Ysleta ISD,34918,El Paso (Ysleta)
Denton ISD,33670,Denton
Ector County ISD,33560,Odessa
Spring ISD,33490,Spring
Corpus Christi ISD,33053,Corpus Christi
Keller ISD,33030,Keller
Prosper ISD,30860,Prosper
Pharr-San Juan-Alamo ISD,30008,Pharr
Amarillo ISD,29729,Amarillo
Northwest ISD,29660,Justin/Fort Worth
Comal ISD,29480,New Braunfels
Edinburg CISD,29450,Edinburg
Midland ISD,28340,Midland
Mesquite ISD,37900,Mesquite
Richardson ISD,36880,Richardson
Leander ISD,41920,Leander
Grand Prairie ISD,26638,Grand Prairie
Carrollton-Farmers Branch ISD,25120,Carrollton
Lubbock ISD,24329,Lubbock
La Joya ISD,23998,La Joya
Eagle Mountain-Saginaw ISD,23870,Fort Worth (North)
McKinney ISD,23320,McKinney
Birdville ISD,22180,Haltom City
Alvin ISD,29320,Alvin
Spring Branch ISD,33260,Houston (Spring Branch)
Clear Creek ISD,40150,League City
Tyler ISD,17890,Tyler
Wylie ISD,19530,Wylie
Tomball ISD,22530,Tomball
Allen ISD,21790,Allen
Hurst-Euless-Bedford ISD,21890,Bedford
Goose Creek CISD,23810,Baytown
Beaumont ISD,16520,Beaumont
Rockwall ISD,18650,Rockwall
Harmony Public Schools (Combined),38000,Houston/Statewide
Irving ISD,30580,Irving
New Caney ISD,18540,New Caney
Georgetown ISD,13670,Georgetown
Bryan ISD,15530,Bryan
College Station ISD,14080,College Station
Waco ISD,14240,Waco
Sherman ISD,10650,Sherman
Victoria ISD,12890,Victoria
Longview ISD,8050,Longview
San Angelo ISD,13120,San Angelo
Wichita Falls ISD,12980,Wichita Falls
Harlingen CISD,17160,Harlingen
Weslaco ISD,16040,Weslaco
Mission CISD,14020,Mission
Brownsville ISD,37065,Brownsville
Del Valle ISD,11240,Del Valle
Hays CISD,23450,Kyle/Buda
Schertz-Cibolo-Universal City ISD,15590,Schertz
Judson ISD,25670,Live Oak
East Central ISD,11040,San Antonio
Bastrop ISD,12940,Bastrop
Pflugerville ISD,25480,Pflugerville
Lake Travis ISD,11640,Austin (Lake Travis)
Eanes ISD,7890,Austin (Westlake)
Coppell ISD,13180,Coppell
Grapevine-Colleyville ISD,13120,Grapevine
Little Elm ISD,8920,Little Elm
Crowley ISD,16920,Crowley
Burleson ISD,12740,Burleson
Forney ISD,16840,Forney
Royse City ISD,9430,Royse City
Princeton ISD,8720,Princeton
Melissa ISD,6250,Melissa
Magnolia ISD,14580,Magnolia
Waller ISD,9120,Waller
Montgomery ISD,9870,Montgomery
Channelview ISD,9320,Channelview
Crosby ISD,6680,Crosby
Dickinson ISD,12340,Dickinson
Texas City ISD,7870,Texas City
Friendswood ISD,5890,Friendswood
Santa Fe ISD,4230,Santa Fe
Laredo ISD,20592,Laredo
McAllen ISD,20095,McAllen
Rio Grande City Grulla ISD,9480,Rio Grande City
San Benito CISD,9120,San Benito
Donna ISD,13240,Donna
Clint ISD,10340,Clint
San Marcos CISD,8210,San Marcos
Seguin ISD,7140,Seguin
Temple ISD,8340,Temple
Belton ISD,14140,Belton
Copperas Cove ISD,7980,Copperas Cove
Midway ISD,8420,Waco (Midway)
Abilene ISD,14890,Abilene
Texarkana ISD,7230,Texarkana"""

# ── National resources (static — always included) ─────────
NATIONAL_RESOURCES = [
    {
        "name": "Wrightslaw",
        "url": "https://www.wrightslaw.com",
        "desc": "Free guides on special education law, IEPs, and parent rights under IDEA.",
        "icon": "fa-balance-scale",
    },
    {
        "name": "Parent Training & Information Centers (PTI)",
        "url": "https://www.parentcenterhub.org/find-your-center/",
        "desc": "Federally funded free training and information for families of children with disabilities.",
        "icon": "fa-users",
    },
    {
        "name": "PACER Center",
        "url": "https://www.pacer.org",
        "desc": "Free resources, workshops, and publications on special education and disability rights.",
        "icon": "fa-hand-holding-heart",
    },
    {
        "name": "National Center for Learning Disabilities",
        "url": "https://www.ncld.org",
        "desc": "Research, advocacy, and free toolkits for families of students with learning disabilities.",
        "icon": "fa-brain",
    },
    {
        "name": "IDA (Dyslexia Handbook)",
        "url": "https://dyslexiaida.org/resources/",
        "desc": "Free dyslexia fact sheets, screenings, and support for parents and educators.",
        "icon": "fa-book-open",
    },
]

# ── Texas-level resources (static — always included) ──────
TEXAS_RESOURCES = [
    {
        "name": "SPEDTex",
        "url": "https://www.spedtex.org",
        "desc": "Texas Education Agency's free parent support line and resource library for special education.",
        "icon": "fa-phone",
    },
    {
        "name": "Disability Rights Texas",
        "url": "https://www.drtx.org",
        "desc": "Free legal advocacy and self-advocacy resources for Texans with disabilities.",
        "icon": "fa-gavel",
    },
    {
        "name": "Texas Parent to Parent",
        "url": "https://www.txp2p.org",
        "desc": "Connects Texas families of children with disabilities with trained volunteer parents.",
        "icon": "fa-heart",
    },
    {
        "name": "Texas Workforce Commission – VR",
        "url": "https://www.twc.texas.gov/vocational-rehabilitation",
        "desc": "Free vocational rehabilitation services for students with disabilities transitioning to work.",
        "icon": "fa-briefcase",
    },
    {
        "name": "Texas School for the Blind & Visually Impaired",
        "url": "https://www.tsbvi.edu",
        "desc": "Free outreach and resources for students with visual impairments across Texas.",
        "icon": "fa-eye",
    },
]

# ══════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)


def parse_districts():
    districts = []
    for line in DISTRICT_RAW.strip().splitlines():
        parts = line.strip().split(",", 2)
        if len(parts) == 3:
            name, enrollment, region = parts
            districts.append({
                "name": name.strip(),
                "enrollment": enrollment.strip(),
                "region": region.strip(),
                "slug": name.strip().lower()
                        .replace(" ", "-")
                        .replace("(", "")
                        .replace(")", "")
                        .replace("/", "-"),
            })
    return districts


def district_city(district: dict) -> str:
    """Best guess at the primary city name."""
    region = district["region"]
    city = region.split("(")[0].strip()
    city = city.split("/")[0].strip()
    return city


# ══════════════════════════════════════════════════════════
#  Vertex AI helper
# ══════════════════════════════════════════════════════════
_model = None

def validate_config():
    """Quick sanity check before running 100+ API calls."""
    if CONFIG["GCP_PROJECT"] == "your-gcp-project-id":
        raise ValueError("Edit GCP_PROJECT in CONFIG before running.")
    log.info("Config OK — project: %s (%s), model: %s",
             CONFIG["GCP_PROJECT"], CONFIG["GCP_PROJECT_NUM"], CONFIG["MODEL"])


def get_model():
    global _model
    if _model is None:
        vertexai.init(
            project=CONFIG["GCP_PROJECT"],   # texasspecialed
            location=CONFIG["GCP_LOCATION"],  # us-central1
        )
        # Gemini 2.0 Flash — fast and cost-efficient for bulk generation
        _model = GenerativeModel("gemini-2.0-flash-001")
        log.info("Initialized Vertex AI: project=%s  model=gemini-2.0-flash-001",
                 CONFIG["GCP_PROJECT"])
    return _model


PROMPT_TEMPLATE = """
You are a research assistant helping a special education parent resource website.

Find 3-5 REAL, FREE, non-profit or government resources specifically available to parents
of children with special education needs in {city}, Texas (serving {district_name}).

For each resource return ONLY valid JSON in this exact format (array of objects):
[
  {{
    "name": "Organization Name",
    "url": "https://real-url.org",
    "desc": "One sentence description under 20 words.",
    "icon": "fa-heart"  // choose from: fa-heart, fa-users, fa-phone, fa-gavel, fa-brain, fa-book-open, fa-hands-helping, fa-star, fa-child, fa-home
  }}
]

Rules:
- Only include organizations that actually exist and serve the {city} / {region} area
- No paid services, no advertising, no lead-gen sites
- Prefer: Arc chapters, Autism Society chapters, parent support groups, county health, 
  nonprofit advocacy orgs, university clinics with free/sliding-scale services
- If fewer than 3 genuine local resources exist, return what you can find (minimum 1)
- Return ONLY the JSON array, no markdown fences, no extra text
"""


def fetch_local_resources(district: dict, retries: int = CONFIG["MAX_RETRIES"]) -> list:
    city = district_city(district)
    prompt = PROMPT_TEMPLATE.format(
        city=city,
        region=district["region"],
        district_name=district["name"],
    )
    for attempt in range(1, retries + 1):
        try:
            model = get_model()
            response = model.generate_content(
                prompt,
                generation_config=GenerationConfig(temperature=0.2, max_output_tokens=1024),
            )
            raw = response.text.strip()
            # strip accidental markdown code fences
            raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
            resources = json.loads(raw)
            if isinstance(resources, list):
                return resources
        except json.JSONDecodeError as e:
            log.warning("JSON parse error on attempt %d for %s: %s", attempt, district["name"], e)
        except Exception as e:
            log.warning("API error attempt %d for %s: %s", attempt, district["name"], e)
        if attempt < retries:
            time.sleep(CONFIG["SLEEP_BETWEEN"] * attempt)
    log.error("Failed to get resources for %s after %d attempts", district["name"], retries)
    return []


# ══════════════════════════════════════════════════════════
#  HTML Banner Builder
# ══════════════════════════════════════════════════════════
def resource_card(r: dict, tag_class: str = "tag-teal") -> str:
    icon = r.get("icon", "fa-star")
    return f"""
      <a href="{r['url']}" target="_blank" rel="noopener" class="free-resource-card">
        <div class="frc-icon"><i class="fas {icon}"></i></div>
        <div class="frc-body">
          <div class="frc-name">{r['name']}</div>
          <div class="frc-desc">{r['desc']}</div>
        </div>
        <div class="frc-arrow"><i class="fas fa-external-link-alt"></i></div>
      </a>"""


def build_free_section(district: dict, local_resources: list, city: str) -> str:
    national_cards = "".join(resource_card(r) for r in NATIONAL_RESOURCES)
    texas_cards    = "".join(resource_card(r) for r in TEXAS_RESOURCES)
    local_cards    = "".join(resource_card(r) for r in local_resources) if local_resources else \
        '<p style="color:#64748b; font-size:0.9rem; padding:12px;">No verified local-only resources found. See Texas and National sections above.</p>'

    return f"""
<!-- ══ FREE RESOURCES SECTION (auto-generated) ══ -->
<style>
  .free-resources-section {{ margin: 40px 0; }}
  .free-banner {{
    border-radius: 10px; overflow: hidden; margin-bottom: 24px;
    border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  }}
  .free-banner-header {{
    display: flex; align-items: center; gap: 10px;
    padding: 12px 20px; font-weight: 800; font-size: 0.75rem;
    text-transform: uppercase; letter-spacing: 0.1em;
  }}
  .banner-national .free-banner-header {{ background:#1e3a8a; color:#fff; }}
  .banner-texas    .free-banner-header {{ background:#b91c1c; color:#fff; }}
  .banner-local    .free-banner-header {{ background:#065f46; color:#fff; }}
  .free-banner-body {{ background:#fff; padding: 12px 16px; }}
  .free-resource-card {{
    display: flex; align-items: flex-start; gap: 14px;
    padding: 14px 12px; border-bottom: 1px solid #f1f5f9;
    text-decoration: none; transition: background 0.15s; color: inherit;
  }}
  .free-resource-card:last-child {{ border-bottom: none; }}
  .free-resource-card:hover {{ background: #f8fafc; }}
  .frc-icon {{
    width: 36px; height: 36px; border-radius: 8px;
    background: #f1f5f9; display: flex; align-items: center;
    justify-content: center; color: #2563eb; flex-shrink: 0; font-size: 0.9rem;
  }}
  .frc-body {{ flex: 1; }}
  .frc-name {{ font-weight: 700; color: #0f172a; font-size: 0.9rem; margin-bottom: 2px; }}
  .frc-desc {{ font-size: 0.82rem; color: #64748b; line-height: 1.4; }}
  .frc-arrow {{ color: #94a3b8; font-size: 0.75rem; padding-top: 4px; }}
  .free-section-label {{
    display: flex; align-items: center; gap: 8px;
    background: #f0fdf4; border: 1px solid #bbf7d0;
    border-radius: 8px; padding: 10px 16px; margin-bottom: 20px;
  }}
  .free-section-label i {{ color: #16a34a; }}
  .free-section-label span {{ font-size: 0.85rem; color: #166534; font-weight: 600; }}
</style>

<div class="free-resources-section">
  <div class="free-section-label">
    <i class="fas fa-hand-holding-heart fa-lg"></i>
    <span>Free &amp; Non-Profit Resources — No cost to families</span>
  </div>

  <!-- National Banner -->
  <div class="free-banner banner-national">
    <div class="free-banner-header">
      <i class="fas fa-flag-usa"></i> National Free Resources
    </div>
    <div class="free-banner-body">
      {national_cards}
    </div>
  </div>

  <!-- Texas Banner -->
  <div class="free-banner banner-texas">
    <div class="free-banner-header">
      <i class="fas fa-star"></i> Texas State Resources
    </div>
    <div class="free-banner-body">
      {texas_cards}
    </div>
  </div>

  <!-- Local Banner -->
  <div class="free-banner banner-local">
    <div class="free-banner-header">
      <i class="fas fa-map-marker-alt"></i> Local Resources — {city} Area
    </div>
    <div class="free-banner-body">
      {local_cards}
    </div>
  </div>
</div>
<!-- ══ END FREE RESOURCES SECTION ══ -->
"""


# ══════════════════════════════════════════════════════════
#  Inject into HTML
# ══════════════════════════════════════════════════════════
# We look for the LAST .service-category block (the paid ads end there)
# and insert the free section immediately after it, before </main>.
INSERT_MARKER_AFTER = 'class="service-category"'


def inject_free_section(html: str, free_html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    # Find all service-category divs; insert after the last one
    all_sc = soup.find_all("div", class_="service-category")
    if all_sc:
        last_sc = all_sc[-1]
        # Build a fragment
        fragment = BeautifulSoup(free_html, "lxml")
        # Insert the whole body of the fragment after last_sc
        for tag in reversed(list(fragment.body.children)):
            last_sc.insert_after(tag)
    else:
        # Fallback: insert before </main>
        main = soup.find("main")
        if main:
            fragment = BeautifulSoup(free_html, "lxml")
            for tag in fragment.body.children:
                main.append(tag)

    return str(soup)


# ══════════════════════════════════════════════════════════
#  File discovery
# ══════════════════════════════════════════════════════════
def find_html_file(district: dict, root: Path) -> Path | None:
    slug = district["slug"]
    candidates = [
        root / slug / "index.html",
        root / slug / "partners.html",
        root / f"{slug}.html",
        root / f"{slug}-isd" / "index.html",
        root / f"{slug}-isd" / "partners.html",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


# ══════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════
def main():
    validate_config()
    districts = parse_districts()
    partners_dir = Path(CONFIG["PARTNERS_DIR"])
    output_dir   = Path(CONFIG["OUTPUT_DIR"])
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = []

    for i, district in enumerate(districts, 1):
        name = district["name"]
        city = district_city(district)
        log.info("[%d/%d] Processing %s (%s)", i, len(districts), name, city)

        # ── Find local file (optional — works even without existing files)
        html_path = find_html_file(district, partners_dir)

        if html_path:
            html_content = html_path.read_text(encoding="utf-8")
        else:
            # Use the uploaded template as base, swapping district-specific text
            template_path = Path("/mnt/user-data/uploads/partners.html")
            html_content = template_path.read_text(encoding="utf-8")
            html_content = html_content.replace("Austin ISD", name)
            html_content = html_content.replace("austin-isd", district["slug"])
            log.info("  No existing file found — using template for %s", name)

        # ── Skip if already injected
        if "free-resources-section" in html_content:
            log.info("  Already has free section — skipping %s", name)
            continue

        # ── Fetch local resources from Vertex AI
        log.info("  Querying Vertex AI for local resources in %s …", city)
        local_resources = fetch_local_resources(district)
        log.info("  → Found %d local resources", len(local_resources))

        # ── Build HTML section
        free_html = build_free_section(district, local_resources, city)

        # ── Inject into page
        updated_html = inject_free_section(html_content, free_html)

        # ── Write output
        out_path = output_dir / district["slug"] / "partners.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(updated_html, encoding="utf-8")
        log.info("  ✓ Written → %s", out_path)

        # ── Track for summary
        for r in local_resources:
            summary_rows.append({
                "district": name,
                "city": city,
                "resource_name": r.get("name", ""),
                "url": r.get("url", ""),
                "desc": r.get("desc", ""),
                "type": "local",
            })

        # Rate-limit courtesy pause
        if i < len(districts):
            time.sleep(CONFIG["SLEEP_BETWEEN"])

    # ── Write summary CSV
    csv_path = output_dir / "resources_found.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["district", "city", "resource_name", "url", "desc", "type"])
        writer.writeheader()
        writer.writerows(summary_rows)
    log.info("\n✅  Done! Summary CSV → %s", csv_path)
    log.info("    Total districts processed: %d", len(districts))
    log.info("    Total local resources found: %d", len(summary_rows))


if __name__ == "__main__":
    main()