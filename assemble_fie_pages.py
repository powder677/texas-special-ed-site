"""
assemble_fie_pages.py
---------------------
Clones the Houston ISD FIE page for all bottom-70 districts using
simple string find & replace. No API key needed.

Usage:
    pip install beautifulsoup4
    python assemble_fie_pages.py

Put your Houston template at: what-is-an-fie-houston-isd.html
Output: fie_html_pages/what-is-an-fie-{slug}.html
"""

import os
import re

# ── Read the Houston template ─────────────────────────────────────────────────

# Looks for the template in the same folder as this script
SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(SCRIPT_DIR, "what-is-an-fie-houston-isd.html")

if not os.path.exists(TEMPLATE_FILE):
    raise FileNotFoundError(
        f"\n\n❌ Template not found!\n"
        f"   Expected: {TEMPLATE_FILE}\n\n"
        f"   Fix: Copy 'what-is-an-fie-houston-isd.html' into the same folder as this script:\n"
        f"   {SCRIPT_DIR}\n"
    )

with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
    TEMPLATE = f.read()

print(f"✓ Template loaded from: {TEMPLATE_FILE}\n")

# ── Districts (bottom 70 by enrollment) ───────────────────────────────────────

DISTRICTS = [
    {"name": "Santa Fe ISD",                     "enrollment": 4230,  "region": "Houston",            "abbr": "SFISD"},
    {"name": "Melissa ISD",                       "enrollment": 6250,  "region": "DFW",                "abbr": "MISD"},
    {"name": "Friendswood ISD",                   "enrollment": 5890,  "region": "Houston",            "abbr": "FISD"},
    {"name": "Crosby ISD",                        "enrollment": 6680,  "region": "Houston",            "abbr": "CISD"},
    {"name": "Seguin ISD",                        "enrollment": 7140,  "region": "San Antonio",        "abbr": "SISD"},
    {"name": "Texarkana ISD",                     "enrollment": 7230,  "region": "East Texas",         "abbr": "TISD"},
    {"name": "Texas City ISD",                    "enrollment": 7870,  "region": "Houston",            "abbr": "TCISD"},
    {"name": "Eanes ISD",                         "enrollment": 7890,  "region": "Austin",             "abbr": "EISD"},
    {"name": "Copperas Cove ISD",                 "enrollment": 7980,  "region": "Central Texas",      "abbr": "CCISD"},
    {"name": "Longview ISD",                      "enrollment": 8050,  "region": "East Texas",         "abbr": "LISD"},
    {"name": "San Marcos CISD",                   "enrollment": 8210,  "region": "Austin",             "abbr": "SMCISD"},
    {"name": "Temple ISD",                        "enrollment": 8340,  "region": "Central Texas",      "abbr": "TISD"},
    {"name": "Midway ISD",                        "enrollment": 8420,  "region": "Central Texas",      "abbr": "MISD"},
    {"name": "Little Elm ISD",                    "enrollment": 8920,  "region": "DFW",                "abbr": "LEISD"},
    {"name": "Princeton ISD",                     "enrollment": 8720,  "region": "DFW",                "abbr": "PISD"},
    {"name": "San Benito CISD",                   "enrollment": 9120,  "region": "Rio Grande Valley",  "abbr": "SBCISD"},
    {"name": "Waller ISD",                        "enrollment": 9120,  "region": "Houston",            "abbr": "WISD"},
    {"name": "Channelview ISD",                   "enrollment": 9320,  "region": "Houston",            "abbr": "CVISD"},
    {"name": "Rio Grande City Grulla ISD",        "enrollment": 9480,  "region": "Rio Grande Valley",  "abbr": "RGCGISD"},
    {"name": "Royse City ISD",                    "enrollment": 9430,  "region": "DFW",                "abbr": "RCISD"},
    {"name": "Montgomery ISD",                    "enrollment": 9870,  "region": "Houston",            "abbr": "MISD"},
    {"name": "Clint ISD",                         "enrollment": 10340, "region": "El Paso",            "abbr": "CISD"},
    {"name": "Sherman ISD",                       "enrollment": 10650, "region": "North Texas",        "abbr": "SISD"},
    {"name": "East Central ISD",                  "enrollment": 11040, "region": "San Antonio",        "abbr": "ECISD"},
    {"name": "Del Valle ISD",                     "enrollment": 11240, "region": "Austin",             "abbr": "DVISD"},
    {"name": "Lake Travis ISD",                   "enrollment": 11640, "region": "Austin",             "abbr": "LTISD"},
    {"name": "Burleson ISD",                      "enrollment": 12740, "region": "Fort Worth",         "abbr": "BISD"},
    {"name": "Dickinson ISD",                     "enrollment": 12340, "region": "Houston",            "abbr": "DISD"},
    {"name": "Wichita Falls ISD",                 "enrollment": 12980, "region": "North Texas",        "abbr": "WFISD"},
    {"name": "Bastrop ISD",                       "enrollment": 12940, "region": "Austin",             "abbr": "BISD"},
    {"name": "Victoria ISD",                      "enrollment": 12890, "region": "Coastal Bend",       "abbr": "VISD"},
    {"name": "Grapevine-Colleyville ISD",         "enrollment": 13120, "region": "DFW",                "abbr": "GCISD"},
    {"name": "San Angelo ISD",                    "enrollment": 13120, "region": "West Texas",         "abbr": "SAISD"},
    {"name": "Coppell ISD",                       "enrollment": 13180, "region": "DFW",                "abbr": "CISD"},
    {"name": "Donna ISD",                         "enrollment": 13240, "region": "Rio Grande Valley",  "abbr": "DISD"},
    {"name": "Georgetown ISD",                    "enrollment": 13670, "region": "Austin",             "abbr": "GISD"},
    {"name": "Mission CISD",                      "enrollment": 14020, "region": "Rio Grande Valley",  "abbr": "MCISD"},
    {"name": "College Station ISD",               "enrollment": 14080, "region": "Central Texas",      "abbr": "CSISD"},
    {"name": "Belton ISD",                        "enrollment": 14140, "region": "Central Texas",      "abbr": "BISD"},
    {"name": "Waco ISD",                          "enrollment": 14240, "region": "Central Texas",      "abbr": "WISD"},
    {"name": "Abilene ISD",                       "enrollment": 14890, "region": "West Texas",         "abbr": "AISD"},
    {"name": "Magnolia ISD",                      "enrollment": 14580, "region": "Houston",            "abbr": "MISD"},
    {"name": "Schertz-Cibolo-Universal City ISD", "enrollment": 15590, "region": "San Antonio",        "abbr": "SCUCISD"},
    {"name": "Bryan ISD",                         "enrollment": 15530, "region": "Central Texas",      "abbr": "BISD"},
    {"name": "Weslaco ISD",                       "enrollment": 16040, "region": "Rio Grande Valley",  "abbr": "WISD"},
    {"name": "Beaumont ISD",                      "enrollment": 16520, "region": "Southeast Texas",    "abbr": "BEAUISD"},
    {"name": "Crowley ISD",                       "enrollment": 16920, "region": "Fort Worth",         "abbr": "CRISD"},
    {"name": "Forney ISD",                        "enrollment": 16840, "region": "DFW",                "abbr": "FISD"},
    {"name": "Harlingen CISD",                    "enrollment": 17160, "region": "Rio Grande Valley",  "abbr": "HCISD"},
    {"name": "Tyler ISD",                         "enrollment": 17890, "region": "East Texas",         "abbr": "TISD"},
    {"name": "Rockwall ISD",                      "enrollment": 18650, "region": "DFW",                "abbr": "RISD"},
    {"name": "New Caney ISD",                     "enrollment": 18540, "region": "Houston",            "abbr": "NCISD"},
    {"name": "Wylie ISD",                         "enrollment": 19530, "region": "DFW",                "abbr": "WISD"},
    {"name": "McAllen ISD",                       "enrollment": 20095, "region": "Rio Grande Valley",  "abbr": "MAISD"},
    {"name": "Laredo ISD",                        "enrollment": 20592, "region": "Laredo",             "abbr": "LISD"},
    {"name": "Allen ISD",                         "enrollment": 21790, "region": "DFW",                "abbr": "AISD"},
    {"name": "Hurst-Euless-Bedford ISD",          "enrollment": 21890, "region": "Fort Worth",         "abbr": "HEBISD"},
    {"name": "Birdville ISD",                     "enrollment": 22180, "region": "Fort Worth",         "abbr": "BVISD"},
    {"name": "Tomball ISD",                       "enrollment": 22530, "region": "Houston",            "abbr": "TISD"},
    {"name": "McKinney ISD",                      "enrollment": 23320, "region": "DFW",                "abbr": "MKISD"},
    {"name": "Goose Creek CISD",                  "enrollment": 23810, "region": "Houston",            "abbr": "GCCISD"},
    {"name": "Eagle Mountain-Saginaw ISD",        "enrollment": 23870, "region": "Fort Worth",         "abbr": "EMSISD"},
    {"name": "La Joya ISD",                       "enrollment": 23998, "region": "Rio Grande Valley",  "abbr": "LJISD"},
    {"name": "Hays CISD",                         "enrollment": 23450, "region": "Austin",             "abbr": "HCISD"},
    {"name": "Lubbock ISD",                       "enrollment": 24329, "region": "South Plains",       "abbr": "LISD"},
    {"name": "Carrollton-Farmers Branch ISD",     "enrollment": 25120, "region": "DFW",                "abbr": "CFBISD"},
    {"name": "Pflugerville ISD",                  "enrollment": 25480, "region": "Austin",             "abbr": "PFISD"},
    {"name": "Judson ISD",                        "enrollment": 25670, "region": "San Antonio",        "abbr": "JISD"},
    {"name": "Midland ISD",                       "enrollment": 28340, "region": "West Texas",         "abbr": "MISD"},
    {"name": "Edinburg CISD",                     "enrollment": 29450, "region": "Rio Grande Valley",  "abbr": "ECISD"},
    {"name": "Comal ISD",                         "enrollment": 29480, "region": "San Antonio",        "abbr": "COMISD"},
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def to_slug(name):
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = slug.strip()
    slug = re.sub(r"\s+", "-", slug)
    return slug

def make_page(template, district):
    name    = district["name"]
    slug    = to_slug(name)
    abbr    = district["abbr"]
    region  = district["region"]

    page = template

    # Swap the district name (longest patterns first to avoid partial matches)
    page = page.replace("Houston ISD", name)
    page = page.replace("houston-isd", slug)
    page = page.replace("HISD", abbr)
    page = page.replace("Houston", region)          # region label in sidebar eyebrow

    # Fix canonical URL
    page = page.replace(
        f"https://www.texasspecialed.com/districts/{slug}/what-is-an-fie-houston-isd",
        f"https://www.texasspecialed.com/districts/{slug}/what-is-an-fie-{slug}"
    )

    return page

# ── Generate ──────────────────────────────────────────────────────────────────

def main():
    output_dir = "fie_html_pages"
    os.makedirs(output_dir, exist_ok=True)

    total = len(DISTRICTS)
    print(f"Assembling {total} FIE pages from template...\n")

    for idx, district in enumerate(DISTRICTS, start=1):
        slug     = to_slug(district["name"])
        filename = os.path.join(output_dir, f"what-is-an-fie-{slug}.html")

        if os.path.exists(filename):
            print(f"[{idx:02d}/{total}] SKIP  {district['name']} (exists)")
            continue

        page = make_page(TEMPLATE, district)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(page)

        print(f"[{idx:02d}/{total}] ✓  {filename}")

    print(f"\n✅ Done! {total} files in ./{output_dir}/")
    print("Deploy to: /districts/<slug>/what-is-an-fie-<slug>.html\n")

if __name__ == "__main__":
    main()