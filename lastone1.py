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

def build_resource_bar(district_folder):
    """Creates a resource bar with hardcoded, perfectly formatted links."""
    html = f"""
    <div class="silo-nav" style="background-color: #e9ecef; padding: 14px 20px; border-radius: 8px; margin: 20px 0 30px; font-size: 15px; font-family: 'DM Sans', sans-serif; display: flex; flex-wrap: wrap; gap: 16px; align-items: center; border-left: 4px solid #6c757d;">
        <strong style="color: #334155;">District Resources:</strong>
        <a href="ard-process-guide-{district_folder}.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">ARD Guide</a> •
        <a href="evaluation-child-find-{district_folder}.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">Evaluations (FIE)</a> •
        <a href="grievance-dispute-resolution-{district_folder}.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">Dispute Resolution</a> •
        <a href="what-is-an-fie-{district_folder}.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">What Is an FIE?</a>
    </div>
    """
    return BeautifulSoup(html, 'html.parser')

def fix_all_links():
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
            
            # --- UPDATE INDEX.HTML HUB CARDS ---
            if filename == "index.html":
                silo_grid = soup.find('div', class_='silo-grid')
                if silo_grid:
                    cards = silo_grid.find_all('a')
                    if len(cards) >= 4:
                        # Card 1: ARD Guide
                        cards[0]['href'] = f"/districts/{district_folder}/ard-process-guide-{district_folder}.html"
                        # Card 2: Evaluations
                        cards[1]['href'] = f"/districts/{district_folder}/evaluation-child-find-{district_folder}.html"
                        # Card 3: Dispute Resolution
                        cards[2]['href'] = f"/districts/{district_folder}/grievance-dispute-resolution-{district_folder}.html"
                        # Card 4: What is an FIE
                        cards[3]['href'] = f"/districts/{district_folder}/what-is-an-fie-{district_folder}.html"
                        
                        # Update text on the 4th card to match the new FIE link
                        h4_tag = cards[3].find('h4')
                        if h4_tag and "Dyslexia" in h4_tag.text:
                            h4_tag.string = "What Is an FIE?"
                            p_tag = cards[3].find('p')
                            if p_tag:
                                p_tag.string = "Understanding the Full Individual Evaluation process."
                                
                        modified = True

            # --- UPDATE THE RESOURCE BAR (.silo-nav) ON ALL PAGES ---
            existing_nav = soup.find('div', class_='silo-nav')
            new_nav = build_resource_bar(district_folder)
            
            if existing_nav:
                existing_nav.replace_with(new_nav)
                modified = True
            else:
                h1_tag = soup.find('h1')
                if h1_tag:
                    h1_tag.insert_after(new_nav)
                    modified = True

            # --- SAVE IF MODIFIED ---
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                print(f"🔗 Links locked in: {filename} in {district_folder}")

if __name__ == "__main__":
    print("Starting final link enforcement...")
    fix_all_links()
    print("Done! All navigation menus and cards are updated.")