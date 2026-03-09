"""
generate_fie_pages.py
---------------------
Generates a "What is a FIE?" (Full Individual Evaluation) markdown page
for each of the bottom 70 Texas school districts (by enrollment) using
the Anthropic Claude API.

Usage:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python generate_fie_pages.py

Output:
    One .md file per district saved to ./fie_pages/
    e.g. fie_pages/friendswood-isd-what-is-fie.md
"""

import os
import re
import time
import anthropic

# ── 1. All districts from your index.html ────────────────────────────────────

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

# ── 2. Pick bottom 70 by enrollment ──────────────────────────────────────────

sorted_districts = sorted(DISTRICTS, key=lambda d: d["enrollment"])
bottom_70 = sorted_districts[:70]

print(f"Bottom 70 districts range from {bottom_70[0]['name']} "
      f"({bottom_70[0]['enrollment']:,}) to {bottom_70[-1]['name']} "
      f"({bottom_70[-1]['enrollment']:,}) students.\n")

# ── 3. Helpers ────────────────────────────────────────────────────────────────

def to_slug(name: str) -> str:
    """Convert district name to URL-safe slug (mirrors your JS toSlug)."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = slug.strip()
    slug = re.sub(r"\s+", "-", slug)
    return slug


def build_prompt(district: dict) -> str:
    name = district["name"]
    region = district["region"]
    enrollment = district["enrollment"]
    return f"""You are a helpful writer for a Texas special education parent resource website called "Texas Special Ed" (texasspecialed.com).

Write a comprehensive, parent-friendly "What is a FIE?" page for **{name}** in the **{region}** region of Texas (approximately {enrollment:,} students).

A FIE (Full Individual Evaluation) is the Texas-specific comprehensive special education evaluation that a school district must conduct before a child can receive special education services. It is sometimes called a "psychoeducational evaluation" and is required under both IDEA and the Texas Education Code.

The page should:
- Be written in warm, accessible language for parents (not legal jargon)
- Open with a short intro paragraph specific to {name} parents
- Cover these sections with H2 headings:
  1. What Is a FIE (Full Individual Evaluation)?
  2. Why Is a FIE Important at {name}?
  3. What Does a FIE Evaluate?
  4. How to Request a FIE at {name}
  5. The FIE Timeline: What Texas Law Requires
  6. Understanding Your FIE Report
  7. What Happens After the FIE? (The ARD Meeting)
  8. Your Rights During the FIE Process at {name}
  9. FIE Tips for {region} Families
  10. Helpful Resources
- Naturally reference Texas-specific law (IDEA + Texas Education Code Chapter 29)
- Include a short FAQ (4–5 questions) at the bottom covering common parent concerns
- End with a compassionate closing paragraph encouraging the parent
- Output ONLY the markdown content — no preamble, no code fences

The page URL will be: /districts/{to_slug(name)}/what-is-fie/
"""


# ── 4. Generate pages ─────────────────────────────────────────────────────────

def generate_fie_page(client: anthropic.Anthropic, district: dict) -> str:
    """Call Claude API and return the markdown content."""
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        messages=[{"role": "user", "content": build_prompt(district)}],
    )
    return message.content[0].text


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set. "
            "Run: export ANTHROPIC_API_KEY='sk-ant-...'"
        )

    client = anthropic.Anthropic(api_key=api_key)

    output_dir = "fie_pages"
    os.makedirs(output_dir, exist_ok=True)

    total = len(bottom_70)
    for idx, district in enumerate(bottom_70, start=1):
        slug = to_slug(district["name"])
        filename = os.path.join(output_dir, f"{slug}-what-is-fie.md")

        # Skip if already generated (useful for re-runs after interruption)
        if os.path.exists(filename):
            print(f"[{idx:02d}/{total}] SKIP  {district['name']} (already exists)")
            continue

        print(f"[{idx:02d}/{total}] Generating: {district['name']} ...", end=" ", flush=True)
        try:
            content = generate_fie_page(client, district)

            # Write markdown with YAML front matter for easy CMS ingestion
            front_matter = f"""---
title: "What Is a FIE? | {district['name']} Special Education Guide"
description: "A parent-friendly guide to the Full Individual Evaluation (FIE) at {district['name']} in the {district['region']} region of Texas. Learn your rights, timelines, and how to advocate for your child."
district: "{district['name']}"
region: "{district['region']}"
enrollment: {district['enrollment']}
slug: "{slug}"
url: "/districts/{slug}/what-is-fie/"
---

"""
            with open(filename, "w", encoding="utf-8") as f:
                f.write(front_matter + content)

            print(f"✓  saved → {filename}")

        except anthropic.RateLimitError:
            print("⚠  Rate limited — waiting 60 s …")
            time.sleep(60)
            # Retry once
            content = generate_fie_page(client, district)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓  saved → {filename}")

        except Exception as exc:
            print(f"✗  ERROR: {exc}")

        # Polite pause between requests to avoid rate limits
        if idx < total:
            time.sleep(1.5)

    print(f"\n✅  Done! {total} markdown files saved to ./{output_dir}/")
    print("\nNext step: copy each file to your site at:")
    print("  /districts/<slug>/what-is-fie/index.md  (or .html)\n")


if __name__ == "__main__":
    main()