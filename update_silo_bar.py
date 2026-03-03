import os
import re
import string

# --- CONFIGURATION ---
OUTPUT_DIR = "districts"

# The exact list of pages in your silo based on your snippet
SILO_PAGES = [
    {"file": "index.html", "title": "District Home"},
    {"file": "ard-process-guide.html", "title": "ARD Guide"},
    {"file": "evaluation-child-find.html", "title": "Evaluations (FIE)"},
    {"file": "dyslexia-services.html", "title": "Dyslexia / 504"},
    {"file": "grievance-dispute-resolution.html", "title": "Dispute Resolution"},
    {"file": "leadership-directory.html", "title": "Staff Directory"},
    {"file": "partners.html", "title": "Providers & Support"}
]

TARGET_DISTRICTS = [
    {"name": "Houston ISD", "city": "Houston"},
    {"name": "Dallas ISD", "city": "Dallas"},
    {"name": "Cypress-Fairbanks ISD", "city": "Cypress"},
    {"name": "Northside ISD", "city": "San Antonio"},
    {"name": "Katy ISD", "city": "Katy"},
    {"name": "Fort Bend ISD", "city": "Sugar Land"},
    {"name": "IDEA Public Schools", "city": "Texas"},
    {"name": "Conroe ISD", "city": "Conroe"},
    {"name": "Austin ISD", "city": "Austin"},
    {"name": "Fort Worth ISD", "city": "Fort Worth"},
    {"name": "Frisco ISD", "city": "Frisco"},
    {"name": "Aldine ISD", "city": "Houston"},
    {"name": "North East ISD", "city": "San Antonio"},
    {"name": "Arlington ISD", "city": "Arlington"},
    {"name": "Klein ISD", "city": "Klein"},
    {"name": "Garland ISD", "city": "Garland"},
    {"name": "El Paso ISD", "city": "El Paso"},
    {"name": "Lewisville ISD", "city": "Lewisville"},
    {"name": "Plano ISD", "city": "Plano"},
    {"name": "Pasadena ISD", "city": "Pasadena"},
    {"name": "Humble ISD", "city": "Humble"},
    {"name": "Socorro ISD", "city": "El Paso"},
    {"name": "Round Rock ISD", "city": "Round Rock"},
    {"name": "San Antonio ISD", "city": "San Antonio"},
    {"name": "Killeen ISD", "city": "Killeen"},
    {"name": "Lamar CISD", "city": "Rosenberg"},
    {"name": "Leander ISD", "city": "Leander"},
    {"name": "United ISD", "city": "Laredo"},
    {"name": "Clear Creek ISD", "city": "League City"},
    {"name": "Alief ISD", "city": "Houston"},
    {"name": "Harmony Public Schools", "city": "Texas"},
    {"name": "Mesquite ISD", "city": "Mesquite"},
    {"name": "Richardson ISD", "city": "Richardson"},
    {"name": "Mansfield ISD", "city": "Mansfield"},
    {"name": "Ysleta ISD", "city": "El Paso"},
    {"name": "Denton ISD", "city": "Denton"},
    {"name": "Ector County ISD", "city": "Odessa"},
    {"name": "Spring ISD", "city": "Spring"},
    {"name": "Spring Branch ISD", "city": "Houston"},
    {"name": "Corpus Christi ISD", "city": "Corpus Christi"},
    {"name": "Keller ISD", "city": "Keller"},
    {"name": "Prosper ISD", "city": "Prosper"},
    {"name": "Irving ISD", "city": "Irving"},
    {"name": "Pharr-San Juan-Alamo ISD", "city": "Pharr"},
    {"name": "Amarillo ISD", "city": "Amarillo"},
    {"name": "Northwest ISD", "city": "Fort Worth"},
    {"name": "Comal ISD", "city": "New Braunfels"},
    {"name": "Edinburg CISD", "city": "Edinburg"}
]

def clean_slug(name):
    """Converts 'Katy ISD' to 'katy-isd'"""
    clean_name = name.translate(str.maketrans('', '', string.punctuation)).lower()
    return "-".join(clean_name.split())

def generate_dynamic_nav(current_file, district_slug):
    """Generates the navigation bar, highlighting the active page."""
    links = []
    
    for i, page in enumerate(SILO_PAGES):
        # Determine if this is the page we are currently looking at
        font_weight = "800" if page["file"] == current_file else "500"
        
        # Build the exact path: /districts/katy-isd/ard-process-guide.html
        url_path = f"/districts/{district_slug}/{page['file']}"
        
        anchor_tag = f'<a href="{url_path}" style="text-decoration: none; color: #2563eb; font-weight: {font_weight};">{page["title"]}</a>'
        links.append(anchor_tag)
    
    # Join the links with the bullet point separator
    links_html = " &bull;\n    ".join(links)
    
    # Wrap it in comments so it's easy to find and update again in the future
    return f"""
<div class="district-top-nav" style="padding: 15px; text-align: center; font-family: sans-serif; background: #f8fafc; border-bottom: 1px solid #e2e8f0; margin-bottom: 20px;">
    {links_html}
</div>
"""

def update_all_pages():
    print("🚀 Updating the navigation bar across all silo pages...\n")
    
    updated_count = 0
    
    for district in TARGET_DISTRICTS:
        dist_slug = clean_slug(district['name'])
        folder_path = os.path.join(OUTPUT_DIR, dist_slug)
        
        # Skip if the district folder doesn't exist yet
        if not os.path.exists(folder_path):
            continue
            
        # Iterate through every possible page in the silo
        for silo_page in SILO_PAGES:
            file_name = silo_page["file"]
            file_path = os.path.join(folder_path, file_name)
            
            # Skip if this specific file doesn't exist
            if not os.path.exists(file_path):
                continue
                
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # 1. Strip out the old version of the dynamic bar if we previously ran this script
            content = re.sub(r'\n?.*?\n?', '', content, flags=re.DOTALL)
            
            # 2. (Optional) Strip out the old hardcoded Katy ISD bar if it exists in the template
            content = re.sub(r'<a href="/districts/[^/]+/index\.html".*?</div>', '', content, flags=re.DOTALL)
            
            # 3. Generate the correct new bar for this specific district and active file
            new_nav = generate_dynamic_nav(file_name, dist_slug)
            
            # 4. Inject it right after the opening <body> tag
            if "<body" in content:
                body_end_idx = content.find(">", content.find("<body")) + 1
                content = content[:body_end_idx] + "\n" + new_nav + content[body_end_idx:]
                
            # 5. Save the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            updated_count += 1
            
        print(f"✅ Updated navigation for {district['name']}")
        
    print(f"\n🎉 Success! Added/updated the dynamic navigation bar on {updated_count} files.")

if __name__ == "__main__":
    update_all_pages()