import os
from bs4 import BeautifulSoup

# The path to your districts folder
base_dir = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"

# The target folders
target_folders = [
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

# The single, unified, wide-reading CSS block
universal_css = """
<style id="universal-core-formatting">
/* ── AUTOMATED CRO PATCH: Standardized Wide Layout ── */
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f8fafc; }
h1 { font-size: 2.2rem; margin-top: 10px; font-family: 'Lora', serif; color: #0a2342; }

/* Core Layout - Single Wide Column */
.layout-grid { max-width: 850px; margin: 30px auto; display: block; width: 100%; box-sizing: border-box; }
.content-column { font-family: 'Source Sans 3', sans-serif; font-size: 17px; line-height: 1.75; color: #1a1a2e; background: #fff; padding: 40px 60px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0; width: 100%; box-sizing: border-box; }
.content-column h2 { font-family: 'Lora', serif; font-size: 1.6rem; font-weight: 700; color: #0a2342; margin: 2.5rem 0 1rem; padding-top: 1.5rem; border-top: 2px solid #e8f0fe; }
.content-column h3 { font-family: 'Lora', serif; font-size: 1.3rem; font-weight: 700; color: #1e3a8a; margin: 2rem 0 1rem; }
.content-column p { margin: 0 0 1.25rem; }
.content-column ul, .content-column ol { padding-left: 20px; margin-bottom: 1.5rem; }
.content-column li { margin-bottom: 8px; }

/* Mobile Fixes */
@media (max-width: 950px) {
    .content-column { padding: 25px 20px !important; margin: 0 !important; border: none !important; border-radius: 0 !important; box-shadow: none !important; }
    .nav-menu { display: none !important; }
}

/* Scannable Blocks */
.pull-quote { border-left: 4px solid #1a56db; margin: 2rem 0; padding: 20px 24px; background: #f8fbff; border-radius: 0 8px 8px 0; font-size: 1.15rem; font-style: italic; color: #1e3a8a; line-height: 1.6; }
.action-steps { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 28px 32px; margin: 2.5rem 0; }
.action-steps h2, .action-steps h3 { border-top: none; margin-top: 0; padding-top: 0; color: #166534; }
.action-steps li { color: #166534; }

/* Standardized Buttons */
.banner-btn { text-decoration: none !important; display: inline-block; border-radius: 6px; font-weight: 800; font-family: 'DM Sans', sans-serif; font-size: 16px; transition: all 0.2s ease; padding: 14px 28px; margin-top: 10px;}
.banner-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.banner-btn-gold { background: #d4af37; color: #0f172a !important; border: none; cursor: pointer; }
.banner-btn-blue { background: #1a56db; color: #fff !important; border: none; cursor: pointer; }
</style>
"""

def format_all_layouts():
    for district_folder in target_folders:
        district_path = os.path.join(base_dir, district_folder)
        
        if not os.path.exists(district_path) or not os.path.isdir(district_path):
            continue
            
        for filename in os.listdir(district_path):
            if not filename.endswith(".html"):
                continue
                
            file_path = os.path.join(district_path, filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                
            modified = False
            
            # --- 1. NUKE THE SIDEBAR ---
            sidebar = soup.find('aside', class_='sidebar-column')
            if sidebar:
                sidebar.decompose()
                modified = True
                
            # --- 2. CLEAN UP OLD STYLES ---
            for style_tag in soup.find_all('style'):
                tag_id = style_tag.get('id', '')
                if tag_id in ['cro-core-formatting', 'fie-core-formatting', 'grievance-formatting', 'universal-core-formatting']:
                    style_tag.decompose()
                    modified = True
                elif style_tag.string and '.layout-grid { display: grid;' in style_tag.string:
                    style_tag.decompose()
                    modified = True

            # --- 3. INJECT THE NEW UNIVERSAL STYLE ---
            head = soup.find('head')
            if head:
                # CREATING A FRESH PARSE FOR EVERY SINGLE FILE
                fresh_style = BeautifulSoup(universal_css, 'html.parser')
                head.append(fresh_style)
                modified = True
                
            # --- 4. REMOVE INLINE STYLES FROM CONTENT COLUMN ---
            content_col = soup.find('article', class_='content-column') or soup.find('div', class_='content-column')
            if content_col and content_col.has_attr('style'):
                del content_col['style']
                modified = True

            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                print(f"✨ Layout Standardized: {filename} in {district_folder}")

if __name__ == "__main__":
    print("Starting visual cleanup and formatting...")
    format_all_layouts()
    print("Done! Check your pages to ensure the text looks wide and clean.")