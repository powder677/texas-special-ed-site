import os
from bs4 import BeautifulSoup

# The path to your districts folder
base_dir = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"

# Only these specific folders will be processed. Everything else is ignored.
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

def build_blog_links():
    """Creates the HTML for the 4 required blog links."""
    html = """
    <div class="blog-links-section" style="max-width: 850px; margin: 40px auto; padding: 24px; background: #fff; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
        <h3 style="font-family: 'Lora', serif; font-size: 1.3rem; color: #0a2342; margin-top: 0; margin-bottom: 15px;">Helpful Special Education Articles</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 15px;">
            <a href="/blog/what-is-fie" style="color: #1a56db; font-weight: 600; text-decoration: none; background: #f8fbff; padding: 10px 18px; border-radius: 6px; border: 1px solid #dbe8fb; font-family: 'DM Sans', sans-serif;">→ What is an FIE?</a>
            <a href="/blog/manifestation-determination" style="color: #1a56db; font-weight: 600; text-decoration: none; background: #f8fbff; padding: 10px 18px; border-radius: 6px; border: 1px solid #dbe8fb; font-family: 'DM Sans', sans-serif;">→ Manifestation Determination</a>
            <a href="/blog/fie-evaluation-timeline" style="color: #1a56db; font-weight: 600; text-decoration: none; background: #f8fbff; padding: 10px 18px; border-radius: 6px; border: 1px solid #dbe8fb; font-family: 'DM Sans', sans-serif;">→ FIE Evaluation Timeline</a>
            <a href="/blog/what-is-an-ard-meeting" style="color: #1a56db; font-weight: 600; text-decoration: none; background: #f8fbff; padding: 10px 18px; border-radius: 6px; border: 1px solid #dbe8fb; font-family: 'DM Sans', sans-serif;">→ What is an ARD Meeting?</a>
        </div>
    </div>
    """
    return BeautifulSoup(html, 'html.parser')

def build_resource_bar(district_folder):
    """Creates the Resource Bar specific to the current district."""
    html = f"""
    <div class="silo-nav" style="background-color: #e9ecef; padding: 14px 20px; border-radius: 8px; margin: 20px 0 30px; font-size: 15px; font-family: 'DM Sans', sans-serif; display: flex; flex-wrap: wrap; gap: 16px; align-items: center; border-left: 4px solid #6c757d;">
        <strong style="color: #334155;">District Resources:</strong>
        <a href="ard-process-guide-{district_folder}.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">ARD Guide</a> •
        <a href="evaluation-child-find-{district_folder}.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">Evaluations (FIE)</a> •
        <a href="grievance-dispute-resolution-{district_folder}.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">Dispute Resolution</a> •
        <a href="what-is-fie.html" style="text-decoration: none; color: #2563eb; font-weight: 500;">What Is an FIE?</a>
    </div>
    """
    return BeautifulSoup(html, 'html.parser')

def process_districts():
    for district_folder in target_folders:
        district_path = os.path.join(base_dir, district_folder)
        
        # Skip if the folder doesn't exist
        if not os.path.exists(district_path) or not os.path.isdir(district_path):
            print(f"⚠️ Skipping {district_folder} - Folder not found")
            continue
            
        for filename in os.listdir(district_path):
            if not filename.endswith(".html"):
                continue
                
            file_path = os.path.join(district_path, filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                
            modified = False
            
            # --- TASK 1 & 2: Process the Hub Page (index.html) ---
            if filename == "index.html":
                
                # 1. Fix the Hub Cards dynamically
                silo_grid = soup.find('div', class_='silo-grid')
                if silo_grid:
                    for a_tag in silo_grid.find_all('a'):
                        href = a_tag.get('href', '')
                        if href:
                            file_target = href.split('/')[-1] 
                            
                            # Adapt the hardcoded gonzales link to the current folder name
                            if 'gonzales' in file_target:
                                file_target = file_target.replace('gonzales-isd', district_folder).replace('gonzales', district_folder)
                            
                            new_href = f"/districts/{district_folder}/{file_target}"
                            if a_tag['href'] != new_href:
                                a_tag['href'] = new_href
                                modified = True
                
                # 2. Inject Resource Bar under the first H1 if it doesn't exist
                if not soup.find('div', class_='silo-nav'):
                    h1_tag = soup.find('h1')
                    if h1_tag:
                        resource_bar = build_resource_bar(district_folder)
                        h1_tag.insert_after(resource_bar)
                        modified = True

            # --- TASK 3: Inject the 4 Blog Links into ALL files ---
            if not soup.find('div', class_='blog-links-section'):
                footer = soup.find('footer', class_='site-footer')
                if footer:
                    blog_links = build_blog_links()
                    footer.insert_before(blog_links)
                    modified = True

            # Save changes back to the file
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                print(f"✅ Processed: {filename} in {district_folder}")

if __name__ == "__main__":
    print("Starting targeted site update...")
    process_districts()
    print("Update complete!")