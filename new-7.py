import os
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
OUTPUT_DIR = "districts"

# Define the exact file names and display titles for your silo
SILO_PAGES = [
    {"title": "What is an FIE?", "file": "what-is-fie.html"},
    {"title": "IEE Guide", "file": "independent-educational-evaluation.html"},
    {"title": "Special Ed Rights", "file": "special-education-rights.html"},
    {"title": "Contact Consultant", "file": "contact.html"}
]

TARGET_DISTRICTS = [
    {"name": "Houston ISD", "slug": "houston-isd"},
    {"name": "Dallas ISD", "slug": "dallas-isd"},
    {"name": "Cypress-Fairbanks ISD", "slug": "cypress-fairbanks-isd"},
    {"name": "Northside ISD", "slug": "northside-isd"},
    {"name": "Katy ISD", "slug": "katy-isd"},
    {"name": "Fort Bend ISD", "slug": "fort-bend-isd"},
    {"name": "IDEA Public Schools", "slug": "idea-public-schools"},
    {"name": "Conroe ISD", "slug": "conroe-isd"},
    {"name": "Austin ISD", "slug": "austin-isd"},
    {"name": "Fort Worth ISD", "slug": "fort-worth-isd"},
    {"name": "Frisco ISD", "slug": "frisco-isd"},
    {"name": "Aldine ISD", "slug": "aldine-isd"},
    {"name": "North East ISD", "slug": "north-east-isd"},
    {"name": "Arlington ISD", "slug": "arlington-isd"},
    {"name": "Klein ISD", "slug": "klein-isd"},
    {"name": "Garland ISD", "slug": "garland-isd"},
    {"name": "El Paso ISD", "slug": "el-paso-isd"},
    {"name": "Lewisville ISD", "slug": "lewisville-isd"},
    {"name": "Plano ISD", "slug": "plano-isd"},
    {"name": "Pasadena ISD", "slug": "pasadena-isd"},
    {"name": "Humble ISD", "slug": "humble-isd"},
    {"name": "Socorro ISD", "slug": "socorro-isd"},
    {"name": "Round Rock ISD", "slug": "round-rock-isd"},
    {"name": "San Antonio ISD", "slug": "san-antonio-isd"},
    {"name": "Killeen ISD", "slug": "killeen-isd"},
    {"name": "Lamar CISD", "slug": "lamar-cisd"},
    {"name": "Leander ISD", "slug": "leander-isd"},
    {"name": "United ISD", "slug": "united-isd"},
    {"name": "Clear Creek ISD", "slug": "clear-creek-isd"},
    {"name": "Alief ISD", "slug": "alief-isd"},
    {"name": "Harmony Public Schools", "slug": "harmony-public-schools"},
    {"name": "Mesquite ISD", "slug": "mesquite-isd"},
    {"name": "Richardson ISD", "slug": "richardson-isd"},
    {"name": "Mansfield ISD", "slug": "mansfield-isd"},
    {"name": "Ysleta ISD", "slug": "ysleta-isd"},
    {"name": "Denton ISD", "slug": "denton-isd"},
    {"name": "Ector County ISD", "slug": "ector-county-isd"},
    {"name": "Spring ISD", "slug": "spring-isd"},
    {"name": "Spring Branch ISD", "slug": "spring-branch-isd"},
    {"name": "Corpus Christi ISD", "slug": "corpus-christi-isd"},
    {"name": "Keller ISD", "slug": "keller-isd"},
    {"name": "Prosper ISD", "slug": "prosper-isd"},
    {"name": "Irving ISD", "slug": "irving-isd"},
    {"name": "Pharr-San Juan-Alamo ISD", "slug": "pharr-san-juan-alamo-isd"},
    {"name": "Amarillo ISD", "slug": "amarillo-isd"},
    {"name": "Northwest ISD", "slug": "northwest-isd"},
    {"name": "Comal ISD", "slug": "comal-isd"},
    {"name": "Edinburg CISD", "slug": "edinburg-cisd"}
]

def generate_nav_html(current_file, district_name):
    """Creates a clean, SEO-optimized horizontal navigation bar."""
    html = f'\n<nav class="district-silo-nav" style="background:#f4f4f4; padding:15px; border-bottom:1px solid #ccc; margin-bottom:20px; font-family:sans-serif;">'
    html += f'<div style="max-width:1200px; margin:0 auto;">'
    html += f'<span style="margin-right:20px; font-weight:bold; color:#333;">{district_name} Resources:</span>'
    
    links = []
    for page in SILO_PAGES:
        if page['file'] == current_file:
            # Active page (not a link)
            links.append(f'<span style="color:#000; font-weight:bold; text-decoration:underline;">{page["title"]}</span>')
        else:
            # Other pages (relative links)
            links.append(f'<a href="./{page["file"]}" style="color:#0056b3; text-decoration:none;">{page["title"]}</a>')
    
    html += " | ".join(links)
    html += '</div></nav>\n'
    return html

def apply_cross_linking():
    print("🚀 Starting Universal Cross-Linking for all silos...")
    
    for district in TARGET_DISTRICTS:
        district_folder = os.path.join(OUTPUT_DIR, district['slug'])
        
        if not os.path.exists(district_folder):
            print(f"⚠️ Folder not found: {district_folder}")
            continue

        print(f"Linking {district['name']}...")

        # Process every file that should be in the silo
        for silo_page in SILO_PAGES:
            file_name = silo_page['file']
            file_path = os.path.join(district_folder, file_name)

            if not os.path.exists(file_path):
                # If the file doesn't exist yet, we can't link to it, so skip
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # 1. Remove any existing nav to avoid duplicates if re-running script
            existing_nav = soup.find('nav', class_='district-silo-nav')
            if existing_nav:
                existing_nav.decompose()

            # 2. Generate the new Nav HTML
            nav_html = generate_nav_html(file_name, district['name'])
            nav_soup = BeautifulSoup(nav_html, "html.parser")

            # 3. Insert the Nav Bar at the very top of the <body>
            body = soup.find('body')
            if body:
                body.insert(0, nav_soup)
                
                # 4. Save the updated file
                with open(file_path, "w", encoding="utf-8") as out:
                    out.write(str(soup))
            else:
                print(f"❌ No <body> tag found in {file_path}")

    print("\n✅ Success! All silo pages are now cross-linked.")

if __name__ == "__main__":
    apply_cross_linking()