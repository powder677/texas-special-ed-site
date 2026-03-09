#!/usr/bin/env python3
"""
generate_fie_pages.py
─────────────────────
Generates a "What is an FIE?" markdown page for every Texas district that
does NOT already have an HTML file at:
    {EXISTING_SITE_ROOT}/districts/{slug}/what-is-an-fie-{slug}.html

SETUP
  pip install anthropic
  export ANTHROPIC_API_KEY="sk-ant-..."

USAGE
  python generate_fie_pages.py

  # Override site root without editing this file:
  SITE_ROOT=/path/to/your/site python generate_fie_pages.py

OUTPUT
  output_fie_pages/{slug}/what-is-fie.md   (700–850 words each)
  output_fie_pages/manifest.json           (word counts + status)
"""

import os
import re
import time
import json
import pathlib
import textwrap
import anthropic

# ──────────────────────────────────────────────────────────────────────────────
# ★ CONFIGURE THESE TWO PATHS ★
#
#   EXISTING_SITE_ROOT  →  root of your live site folder.
#                          Skip any district where this file already exists:
#                          {EXISTING_SITE_ROOT}/districts/{slug}/what-is-an-fie-{slug}.html
#
#   OUTPUT_DIR          →  where new .md files are written.
# ──────────────────────────────────────────────────────────────────────────────

EXISTING_SITE_ROOT = pathlib.Path(
    os.environ.get("SITE_ROOT", ".")   # set SITE_ROOT env var, or edit the "." here
)
OUTPUT_DIR = pathlib.Path("output_fie_pages")

DELAY_SECONDS = 2
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1500


# ──────────────────────────────────────────────────────────────────────────────
# ALL 120 DISTRICTS  (name, slug, abbreviation)
# ──────────────────────────────────────────────────────────────────────────────

DISTRICTS = [
    # ── Top 50 (largest) ──────────────────────────────────────────────────────
    ("Houston ISD",                      "houston-isd",                       "HISD"),
    ("Dallas ISD",                       "dallas-isd",                        "DISD"),
    ("Cypress-Fairbanks ISD",            "cypress-fairbanks-isd",             "CFISD"),
    ("Northside ISD",                    "northside-isd",                     "NISD"),
    ("Katy ISD",                         "katy-isd",                          "KISD"),
    ("Fort Bend ISD",                    "fort-bend-isd",                     "FBISD"),
    ("IDEA Public Schools",              "idea-public-schools",               "IDEA"),
    ("Conroe ISD",                       "conroe-isd",                        "CISD"),
    ("Austin ISD",                       "austin-isd",                        "AISD"),
    ("Fort Worth ISD",                   "fort-worth-isd",                    "FWISD"),
    ("Frisco ISD",                       "frisco-isd",                        "FISD"),
    ("Aldine ISD",                       "aldine-isd",                        "ALDISD"),
    ("North East ISD",                   "north-east-isd",                    "NEISD"),
    ("Arlington ISD",                    "arlington-isd",                     "ARISD"),
    ("Klein ISD",                        "klein-isd",                         "KISD"),
    ("Garland ISD",                      "garland-isd",                       "GISD"),
    ("El Paso ISD",                      "el-paso-isd",                       "EPISD"),
    ("Lewisville ISD",                   "lewisville-isd",                    "LISD"),
    ("Plano ISD",                        "plano-isd",                         "PISD"),
    ("Pasadena ISD",                     "pasadena-isd",                      "PASISD"),
    ("Humble ISD",                       "humble-isd",                        "HUMBISD"),
    ("Socorro ISD",                      "socorro-isd",                       "SISD"),
    ("Round Rock ISD",                   "round-rock-isd",                    "RRISD"),
    ("San Antonio ISD",                  "san-antonio-isd",                   "SAISD"),
    ("Killeen ISD",                      "killeen-isd",                       "KILISD"),
    ("Lamar CISD",                       "lamar-cisd",                        "LCISD"),
    ("Leander ISD",                      "leander-isd",                       "LISD"),
    ("United ISD",                       "united-isd",                        "UISD"),
    ("Clear Creek ISD",                  "clear-creek-isd",                   "CCISD"),
    ("Harmony Public Schools",           "harmony-public-schools",            "HPS"),
    ("Mesquite ISD",                     "mesquite-isd",                      "MESISD"),
    ("Richardson ISD",                   "richardson-isd",                    "RISD"),
    ("Alief ISD",                        "alief-isd",                         "ALIEF"),
    ("Mansfield ISD",                    "mansfield-isd",                     "MANSISD"),
    ("Ysleta ISD",                       "ysleta-isd",                        "YISD"),
    ("Denton ISD",                       "denton-isd",                        "DENTISD"),
    ("Ector County ISD",                 "ector-county-isd",                  "ECISD"),
    ("Spring ISD",                       "spring-isd",                        "SPRINGISD"),
    ("Spring Branch ISD",                "spring-branch-isd",                 "SBISD"),
    ("Corpus Christi ISD",               "corpus-christi-isd",                "CCISD"),
    ("Keller ISD",                       "keller-isd",                        "KELISD"),
    ("Irving ISD",                       "irving-isd",                        "IISD"),
    ("Prosper ISD",                      "prosper-isd",                       "PRSISD"),
    ("Pharr-San Juan-Alamo ISD",         "pharr-san-juan-alamo-isd",          "PSJA"),
    ("Alvin ISD",                        "alvin-isd",                         "AVISD"),
    ("Amarillo ISD",                     "amarillo-isd",                      "AMISD"),
    ("Northwest ISD",                    "northwest-isd",                     "NWISD"),
    ("Comal ISD",                        "comal-isd",                         "COMISD"),
    ("Edinburg CISD",                    "edinburg-cisd",                     "ECISD"),
    ("Midland ISD",                      "midland-isd",                       "MISD"),
    # ── Districts 51–120 ──────────────────────────────────────────────────────
    ("Judson ISD",                       "judson-isd",                        "JISD"),
    ("Pflugerville ISD",                 "pflugerville-isd",                  "PFISD"),
    ("Carrollton-Farmers Branch ISD",    "carrollton-farmers-branch-isd",     "CFBISD"),
    ("Lubbock ISD",                      "lubbock-isd",                       "LUBISD"),
    ("Hays CISD",                        "hays-cisd",                         "HCISD"),
    ("La Joya ISD",                      "la-joya-isd",                       "LJISD"),
    ("Eagle Mountain-Saginaw ISD",       "eagle-mountain-saginaw-isd",        "EMSISD"),
    ("Goose Creek CISD",                 "goose-creek-cisd",                  "GCCISD"),
    ("McKinney ISD",                     "mckinney-isd",                      "MCKISD"),
    ("Tomball ISD",                      "tomball-isd",                       "TOMISD"),
    ("Birdville ISD",                    "birdville-isd",                     "BVLISD"),
    ("Allen ISD",                        "allen-isd",                         "ALLISD"),
    ("Hurst-Euless-Bedford ISD",         "hurst-euless-bedford-isd",          "HEBISD"),
    ("Laredo ISD",                       "laredo-isd",                        "LRDISD"),
    ("McAllen ISD",                      "mcallen-isd",                       "MAISD"),
    ("Wylie ISD",                        "wylie-isd",                         "WYLISD"),
    ("New Caney ISD",                    "new-caney-isd",                     "NCISD"),
    ("Rockwall ISD",                     "rockwall-isd",                      "RWISD"),
    ("Harlingen CISD",                   "harlingen-cisd",                    "HRLCISD"),
    ("Crowley ISD",                      "crowley-isd",                       "CRISD"),
    ("Forney ISD",                       "forney-isd",                        "FORNISD"),
    ("Weslaco ISD",                      "weslaco-isd",                       "WESISD"),
    ("Bryan ISD",                        "bryan-isd",                         "BRYISD"),
    ("Schertz-Cibolo-Universal City ISD","schertz-cibolo-universal-city-isd", "SCUCISD"),
    ("Magnolia ISD",                     "magnolia-isd",                      "MGISD"),
    ("Belton ISD",                       "belton-isd",                        "BELISD"),
    ("Abilene ISD",                      "abilene-isd",                       "ABISD"),
    ("College Station ISD",              "college-station-isd",               "CSISD"),
    ("Mission CISD",                     "mission-cisd",                      "MCISD"),
    ("Donna ISD",                        "donna-isd",                         "DNISD"),
    ("Coppell ISD",                      "coppell-isd",                       "COPISD"),
    ("Grapevine-Colleyville ISD",        "grapevine-colleyville-isd",         "GCISD"),
    ("San Angelo ISD",                   "san-angelo-isd",                    "SANISD"),
    ("Bastrop ISD",                      "bastrop-isd",                       "BSTRISD"),
    ("Wichita Falls ISD",                "wichita-falls-isd",                 "WFISD"),
    ("Dickinson ISD",                    "dickinson-isd",                     "DICISD"),
    ("Burleson ISD",                     "burleson-isd",                      "BURISD"),
    ("Lake Travis ISD",                  "lake-travis-isd",                   "LTISD"),
    ("East Central ISD",                 "east-central-isd",                  "ECISD"),
    ("Del Valle ISD",                    "del-valle-isd",                     "DVISD"),
    ("Clint ISD",                        "clint-isd",                         "CLTISD"),
    ("Sherman ISD",                      "sherman-isd",                       "SHISD"),
    ("Georgetown ISD",                   "georgetown-isd",                    "GTWNISD"),
    ("Montgomery ISD",                   "montgomery-isd",                    "MONTISD"),
    ("Royse City ISD",                   "royse-city-isd",                    "RCISD"),
    ("Rio Grande City Grulla ISD",       "rio-grande-city-grulla-isd",        "RGCGISD"),
    ("San Benito CISD",                  "san-benito-cisd",                   "SBCISD"),
    ("Waller ISD",                       "waller-isd",                        "WLRISD"),
    ("Little Elm ISD",                   "little-elm-isd",                    "LEISD"),
    ("Midway ISD",                       "midway-isd",                        "MWISD"),
    ("Temple ISD",                       "temple-isd",                        "TEMPISD"),
    ("San Marcos CISD",                  "san-marcos-cisd",                   "SMCISD"),
    ("Longview ISD",                     "longview-isd",                      "LVISD"),
    ("Eanes ISD",                        "eanes-isd",                         "EANES"),
    ("Texas City ISD",                   "texas-city-isd",                    "TCISD"),
    ("Seguin ISD",                       "seguin-isd",                        "SEGISD"),
    ("Texarkana ISD",                    "texarkana-isd",                     "TXKISD"),
    ("Copperas Cove ISD",                "copperas-cove-isd",                 "CCVISD"),
    ("Crosby ISD",                       "crosby-isd",                        "CRSBY"),
    ("Princeton ISD",                    "princeton-isd",                     "PRISD"),
    ("Melissa ISD",                      "melissa-isd",                       "MELISD"),
    ("Friendswood ISD",                  "friendswood-isd",                   "FRDSISD"),
    ("Channelview ISD",                  "channelview-isd",                   "CHVISD"),
    ("Victoria ISD",                     "victoria-isd",                      "VISD"),
    ("Waco ISD",                         "waco-isd",                          "WACOISD"),
    ("Beaumont ISD",                     "beaumont-isd",                      "BMISD"),
    ("Tyler ISD",                        "tyler-isd",                         "TYLISD"),
    ("Santa Fe ISD",                     "santa-fe-isd",                      "SFISD"),
    ("Grand Prairie ISD",                "grand-prairie-isd",                 "GPISD"),
]


# ──────────────────────────────────────────────────────────────────────────────
# PROMPTS
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = textwrap.dedent("""
    You are an expert Texas special-education content writer.
    You write clear, parent-friendly pages about the FIE (Full Individual
    Evaluation) process under IDEA and Texas Education Code Chapter 29.
    Your tone is warm, authoritative, and empowering — never legalistic.
    All content is accurate to Texas law as of 2025.
""").strip()

USER_PROMPT_TEMPLATE = textwrap.dedent("""
    Write a "What is an FIE?" guide for **{district_name}** ({abbr}).

    STRICT REQUIREMENTS
    • Exactly 700–850 words (count carefully)
    • Output ONLY valid Markdown — no HTML, no preamble, no commentary
    • Use the exact structure below (H2 headings, no H1)

    REQUIRED STRUCTURE
    ## What Is an FIE in {district_name}?
    [2–3 sentence intro specific to {district_name} parents]

    ## Why {abbr} Must Conduct a Full Individual Evaluation
    [Explain Child Find duty, IDEA requirement, multi-area coverage]

    ## How to Request an FIE from {district_name}
    [Written request to principal + Director of Special Ed, exact magic phrase,
     15-school-day response clock, tip about keeping a copy]

    ## The 45-School-Day Timeline
    [When clock starts (consent), what counts as school days, what {abbr}
     must deliver, the 30-calendar-day ARD window after the report]

    ## What the {abbr} Evaluation Must Cover
    [All suspected disability areas: academic, cognitive, speech/language,
     social-emotional, OT if needed, adaptive behavior if ID suspected,
     primary-language requirement]

    ## Can {district_name} Refuse to Evaluate My Child?
    [Yes — but only via Prior Written Notice; RTI cannot block eval;
     options: mediation, TEA State Complaint, due process]

    ## What Happens After the FIE?
    [Written report before ARD, ARD within 30 calendar days, IEP if eligible,
     right to an IEE at district expense if parent disagrees]

    ## FIE vs. FIIE in Texas: What's the Difference?
    [FIE = general term; FIIE = Full Individual and Initial Evaluation (first
     eval in this district); same rules apply to both]

    ## Your Rights as a {district_name} Parent
    [Bullet list: receive report in advance, bring advocate, request IEE,
     request reconsideration, file TEA complaint]

    Do NOT include calls to action, product mentions, or external links.
    Do NOT include an H1 heading.
    Output the Markdown and nothing else.
""").strip()


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def html_exists(slug: str) -> bool:
    """Return True if the district's HTML page already exists in the site folder."""
    html_path = EXISTING_SITE_ROOT / "districts" / slug / f"what-is-an-fie-{slug}.html"
    return html_path.exists()


def count_words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def generate_fie_page(client: anthropic.Anthropic, district_name: str, abbr: str) -> str:
    prompt = USER_PROMPT_TEMPLATE.format(district_name=district_name, abbr=abbr)
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def save_page(slug: str, content: str) -> pathlib.Path:
    folder = OUTPUT_DIR / slug
    folder.mkdir(parents=True, exist_ok=True)
    filepath = folder / "what-is-fie.md"
    filepath.write_text(content, encoding="utf-8")
    return filepath


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("❌  Set ANTHROPIC_API_KEY before running this script.")

    client = anthropic.Anthropic(api_key=api_key)
    OUTPUT_DIR.mkdir(exist_ok=True)

    # ── Pre-flight: sort districts into skip / generate ───────────────────────
    to_generate = []
    skipped_names = []

    for district_name, slug, abbr in DISTRICTS:
        if html_exists(slug):
            skipped_names.append(district_name)
        else:
            to_generate.append((district_name, slug, abbr))

    print(f"\n📂  Site root  : {EXISTING_SITE_ROOT.resolve()}")
    print(f"⏭   Skipping   : {len(skipped_names)} districts (HTML already exists)")
    if skipped_names:
        for name in skipped_names:
            print(f"       • {name}")
    print(f"\n🚀  Generating : {len(to_generate)} districts\n")

    if not to_generate:
        print("✅  Nothing to do — all districts already have HTML pages.")
        return

    summary = []
    total = len(to_generate)

    for i, (district_name, slug, abbr) in enumerate(to_generate, start=1):
        try:
            print(f"  [{i:02d}/{total}] ⏳  {district_name} …", end=" ", flush=True)
            content = generate_fie_page(client, district_name, abbr)
            words = count_words(content)

            flag = ""
            if words < 700:
                flag = f"  ⚠️  UNDER target ({words} words)"
            elif words > 850:
                flag = f"  ⚠️  OVER target ({words} words)"

            filepath = save_page(slug, content)
            status = "ok" if not flag else "range-warn"
            summary.append((district_name, slug, words, status))
            print(f"✅  {words} words → {filepath}{flag}")

        except anthropic.RateLimitError:
            print("⏸  Rate limited — sleeping 60 s …")
            time.sleep(60)
            try:
                content = generate_fie_page(client, district_name, abbr)
                words = count_words(content)
                filepath = save_page(slug, content)
                summary.append((district_name, slug, words, "ok-retry"))
                print(f"  ✅  {words} words → {filepath}")
            except Exception as err:
                print(f"  ❌  Failed after retry: {err}")
                summary.append((district_name, slug, 0, f"error: {err}"))

        except Exception as err:
            print(f"  ❌  Error: {err}")
            summary.append((district_name, slug, 0, f"error: {err}"))

        if i < total:
            time.sleep(DELAY_SECONDS)

    # ── Summary report ────────────────────────────────────────────────────────
    print("\n" + "─" * 65)
    print(f"{'District':<40} {'Words':>6}  Status")
    print("─" * 65)
    for district_name, slug, words, status in summary:
        print(f"  {district_name:<38} {words:>6}  {status}")

    ok_count   = sum(1 for *_, s in summary if s.startswith("ok"))
    warn_count = sum(1 for *_, s in summary if "warn" in s)
    err_count  = sum(1 for *_, s in summary if "error" in s)
    good_words = [w for _, _, w, s in summary if not s.startswith("error") and w > 0]
    avg_words  = sum(good_words) // len(good_words) if good_words else 0

    print("─" * 65)
    print(f"\n✅ {ok_count} ok  |  ⚠️  {warn_count} range warn  |  ❌ {err_count} errors")
    print(f"📝 Average word count  : {avg_words}")
    print(f"⏭  Skipped (had HTML)  : {len(skipped_names)}")
    print(f"📁 Files saved to      : {OUTPUT_DIR.resolve()}\n")

    # ── JSON manifest ─────────────────────────────────────────────────────────
    manifest = {
        "skipped_had_html": skipped_names,
        "generated": [
            {"district": d, "slug": s, "words": w, "status": st,
             "file": f"{s}/what-is-fie.md"}
            for d, s, w, st in summary
        ],
    }
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"📋 Manifest → {manifest_path}")


if __name__ == "__main__":
    main()