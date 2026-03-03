import os
import re
import string

# --- CONFIGURATION ---
TEMPLATE_PATH = "What_is_fie_template.html"
OUTPUT_DIR = "districts"

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

def generate_short_name(name):
    """Converts 'Cypress-Fairbanks ISD' to 'CFISD'"""
    special_cases = {
        "Cypress-Fairbanks ISD": "CFISD",
        "Pharr-San Juan-Alamo ISD": "PSJA ISD",
        "IDEA Public Schools": "IDEA",
        "Harmony Public Schools": "Harmony"
    }
    if name in special_cases:
        return special_cases[name]
        
    if " ISD" in name or " CISD" in name:
        parts = name.replace(" ISD", "").replace(" CISD", "").replace("-", " ").split()
        short = "".join(word[0].upper() for word in parts)
        return short + ("CISD" if "CISD" in name else "ISD")
    return name

def main():
    try:
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Could not find {TEMPLATE_PATH}. Make sure your master file is in this folder.")
        return

    # Optional: Strip out the instruction comment block if it uses standard HTML comments
    template = re.sub(r'', '', template, flags=re.DOTALL)

    count = 0
    print("🚀 Restoring full content for all district pages...\n")

    for district in TARGET_DISTRICTS:
        dist_name = district['name']
        dist_city = district['city']
        dist_slug = clean_slug(dist_name)
        dist_short = generate_short_name(dist_name)

        print(f"Rebuilding: {dist_name}...")

        # Replace the 4 exact tokens inside the master template
        page_content = template
        page_content = page_content.replace("[[DISTRICT_NAME]]", dist_name)
        page_content = page_content.replace("[[DISTRICT_SLUG]]", dist_slug)
        page_content = page_content.replace("[[DISTRICT_SHORT]]", dist_short)
        page_content = page_content.replace("[[DISTRICT_CITY]]", dist_city)

        # Create output directory for the district if it doesn't exist
        folder_path = os.path.join(OUTPUT_DIR, dist_slug)
        os.makedirs(folder_path, exist_ok=True)

        # Write the full, restored file
        file_path = os.path.join(folder_path, "what-is-fie.html")
        with open(file_path, "w", encoding="utf-8") as out:
            out.write(page_content)
        
        count += 1

    print(f"\n✅ Success! Restored {count} complete FIE pages with full content.")

if __name__ == "__main__":
    main()