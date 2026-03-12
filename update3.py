import os
from bs4 import BeautifulSoup

BASE_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"

TARGET_FOLDERS = [
    "brownsville-isd", "hallsville-isd", "pearland-isd", "galena-park-isd", "southwest-isd", 
    "eagle-pass-isd", "fort-stockton-isd", "cleveland-isd", "roscoe-collegiate-isd", "deer-park-isd", 
    "frenship-isd", "canyon-isd", "duncanville-isd", "midlothian-isd", "waxahachie-isd", 
    "brazosport-isd", "boerne-isd", "huntsville-isd", "sheldon-isd", "harlandale-isd", 
    "hutto-isd", "los-fresnos-cisd", "manor-isd", "new-braunfels-isd", "sharyland-isd", 
    "liberty-hill-isd", "san-felipe-del-rio-cisd", "medina-valley-isd", "willis-isd", "dripping-springs-isd", 
    "aledo-isd", "edgewood-isd", "carroll-isd", "port-arthur-isd", "lubbock-cooper-isd", 
    "weatherford-isd", "granbury-isd", "barbers-hill-isd", "azle-isd", "angleton-isd", 
    "la-porte-isd", "highland-park-isd", "south-san-antonio-isd", "crandall-isd", "cleburne-isd", 
    "lufkin-isd", "white-settlement-isd", "lancaster-isd", "lockhart-isd", "red-oak-isd", 
    "ennis-isd", "cedar-hill-isd", "argyle-isd", "anna-isd", "joshua-isd", 
    "roma-isd", "corsicana-isd", "galveston-isd", "elgin-isd", "nacogdoches-isd", 
    "canutillo-isd", "southside-isd", "splendora-isd", "dayton-isd", "flour-bluff-isd", 
    "desoto-isd", "port-neches-groves-isd", "celina-isd", "nederland-isd", "community-isd", 
    "greenville-isd", "mount-pleasant-isd", "gregory-portland-isd", "everman-isd", "denison-isd", 
    "terrell-isd", "brenham-isd", "alamo-heights-isd", "jacksonville-isd", "marshall-isd", 
    "whitehouse-isd", "south-texas-isd", "lindale-isd", "kerrville-isd", "aubrey-isd", 
    "pine-tree-isd", "dumas-isd", "kaufman-isd", "alice-isd", "somerset-isd", 
    "valley-view-isd", "sulphur-springs-isd", "andrews-isd", "springtown-isd", "vidor-isd", 
    "jarrell-isd", "lumberton-isd", "edcouch-elsa-isd", "plainview-isd", "floresville-isd", 
    "uvalde-cisd", "livingston-isd", "marble-falls-isd", "mercedes-isd", "hereford-isd", 
    "mabank-isd", "lovejoy-isd", "castleberry-isd", "paris-isd", "alvarado-isd", 
    "decatur-isd", "chapel-hill-isd", "calallen-isd", "lake-dallas-isd", "needville-isd", 
    "huffman-isd", "lampasas-isd", "stephenville-isd", "tuloso-midway-isd", "la-vernia-isd", 
    "kilgore-isd", "calhoun-county-isd", "bay-city-isd", "pleasanton-isd", "brownwood-isd", 
    "big-spring-isd", "greenwood-isd", "little-cypress-mauriceville-cisd", "mineral-wells-isd", "zapata-county-isd", 
    "el-campo-isd", "lake-worth-isd", "henderson-isd", "burnet-cisd", "godley-isd", 
    "bridge-city-isd", "pampa-isd", "navasota-isd", "gainesville-isd", "sealy-isd", 
    "seminole-isd", "caddo-mills-isd", "beeville-isd", "burkburnett-isd", "ferris-isd", 
    "palestine-isd", "gilmer-isd", "china-spring-isd", "quinlan-isd", "taylor-isd", 
    "pecos-barstow-toyah-isd", "la-vega-isd", "sanger-isd", "fredericksburg-isd", "columbia-brazoria-isd", 
    "athens-isd", "bullard-isd", "hudson-isd", "hidalgo-isd", "rockport-fulton-isd", 
    "hardin-jefferson-isd", "san-elizario-isd", "kennedale-isd", "royal-isd", "wills-point-isd", 
    "navarro-isd", "gatesville-isd", "la-feria-isd", "carthage-isd", "van-alstyne-isd", 
    "west-orange-cove-cisd", "silsbee-isd", "levelland-isd", "gonzales-isd", "krum-isd", 
    "kingsville-isd", "wimberley-isd", "brownsboro-isd", "liberty-isd", "robstown-isd", 
    "farmersville-isd", "north-lamar-isd", "robinson-isd"
]

# -----------------------------------
# SEO Filename Map
# -----------------------------------

TOPIC_MAP = {
    "ard-process-guide": "ard-process-guide",
    "evaluation-child-find": "evaluation-child-find",
    "grievance-dispute-resolution": "grievance-dispute-resolution",
    "what-is-an-fie": "what-is-an-fie",
    "what-is-fie": "what-is-an-fie",
    "dyslexia": "dyslexia"
}


def get_perfect_seo_name(filename, district):
    """Return standardized SEO filename."""

    for key in TOPIC_MAP:
        if key in filename:
            return f"{TOPIC_MAP[key]}-{district}.html"

    return None


# -----------------------------------
# Blog Links
# -----------------------------------

def build_blog_links():

    html = """
    <div class="blog-links-section" style="max-width:850px;margin:40px auto;padding:24px;background:#fff;border-radius:8px;border:1px solid #e2e8f0;">
        <h3 style="font-size:1.3rem;margin-bottom:15px;">Helpful Special Education Articles</h3>

        <div style="display:flex;flex-wrap:wrap;gap:15px;">
            <a href="/blog/what-is-fie">→ What is an FIE?</a>
            <a href="/blog/manifestation-determination">→ Manifestation Determination</a>
            <a href="/blog/fie-evaluation-timeline">→ FIE Evaluation Timeline</a>
            <a href="/blog/what-is-an-ard-meeting">→ What is an ARD Meeting?</a>
        </div>
    </div>
    """

    return BeautifulSoup(html, "html.parser")


# -----------------------------------
# Resource Bar
# -----------------------------------

def build_resource_bar(district):

    html = f"""
    <div class="silo-nav" style="background:#e9ecef;padding:14px 20px;border-radius:8px;margin:20px 0;display:flex;flex-wrap:wrap;gap:12px;">
        <strong>District Resources:</strong>

        <a href="ard-process-guide-{district}.html">ARD Guide</a> •

        <a href="evaluation-child-find-{district}.html">Evaluations (FIE)</a> •

        <a href="grievance-dispute-resolution-{district}.html">Dispute Resolution</a> •

        <a href="what-is-an-fie-{district}.html">What Is an FIE?</a>
    </div>
    """

    return BeautifulSoup(html, "html.parser")


# -----------------------------------
# Rename Files
# -----------------------------------

def standardize_filenames(path, district):

    for filename in os.listdir(path):

        if filename == "index.html" or not filename.endswith(".html"):
            continue

        perfect = get_perfect_seo_name(filename, district)

        if not perfect or perfect == filename:
            continue

        old = os.path.join(path, filename)
        new = os.path.join(path, perfect)

        if os.path.exists(new):
            print(f"Duplicate removed: {filename}")
            os.remove(old)
        else:
            os.rename(old, new)
            print(f"Renamed: {filename} -> {perfect}")


# -----------------------------------
# Update HTML Content
# -----------------------------------

def update_html(file_path, district):

    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    modified = False

    filename = os.path.basename(file_path)

    # HUB PAGE
    if filename == "index.html":

        grid = soup.find("div", class_="silo-grid")

        if grid:

            cards = grid.find_all("a")

            links = [
                f"/districts/{district}/ard-process-guide-{district}.html",
                f"/districts/{district}/evaluation-child-find-{district}.html",
                f"/districts/{district}/grievance-dispute-resolution-{district}.html",
                f"/districts/{district}/dyslexia-{district}.html",
            ]

            for i, link in enumerate(links):
                if i < len(cards):
                    cards[i]["href"] = link
                    modified = True

    # RESOURCE BAR
    existing_nav = soup.find("div", class_="silo-nav")
    new_nav = build_resource_bar(district)

    if existing_nav:
        existing_nav.replace_with(new_nav)
    else:
        h1 = soup.find("h1")
        if h1:
            h1.insert_after(new_nav)

    modified = True

    # BLOG LINKS
    if not soup.find("div", class_="blog-links-section"):

        footer = soup.find("footer")

        if footer:
            footer.insert_before(build_blog_links())
            modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(soup))

        print(f"Updated HTML: {filename}")


# -----------------------------------
# Main Processor
# -----------------------------------

def process_districts():

    for district in TARGET_FOLDERS:

        path = os.path.join(BASE_DIR, district)

        if not os.path.isdir(path):
            continue

        print(f"\nProcessing: {district}")

        # Step 1 rename
        standardize_filenames(path, district)

        # Step 2 update HTML
        for file in os.listdir(path):

            if file.endswith(".html"):

                update_html(
                    os.path.join(path, file),
                    district
                )


# -----------------------------------

if __name__ == "__main__":

    print("\nStarting SEO Standardizer...\n")

    process_districts()

    print("\nAll districts processed.\n")