"""
Add "What Is an FIE?" link to silo navigation on district pages
AND add a card for the new page on each district's index.html
ONLY for the 48 target districts
"""

import os
import re
import string
from pathlib import Path

# Configuration
DISTRICTS_FOLDER = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"

# Only update these 48 districts
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

# Get list of target district slugs
TARGET_SLUGS = set([clean_slug(d['name']) for d in TARGET_DISTRICTS])

# The new link HTML to add
NEW_SILO_LINK = '''<a href="what-is-fie.html" style="color: #495057; text-decoration: none; font-weight: 500; padding: 6px 12px; border-radius: 4px; background: white; transition: all 0.2s; border: 1px solid #dee2e6;">📋 What Is an FIE?</a>'''

# The new card HTML for index pages
NEW_INDEX_CARD = '''
      <!-- What Is an FIE Card -->
      <div class="resource-card">
        <div class="resource-icon">📋</div>
        <h3>What Is an FIE?</h3>
        <p>Learn about Full Individual Evaluations (FIE) — the comprehensive assessment process, 45-day timeline, your legal rights, and how to request one in writing.</p>
        <a href="what-is-fie.html">Learn About FIE →</a>
      </div>
'''

def add_fie_link_to_silo_nav(file_path):
    """Add the FIE link to the silo navigation if not already there"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if link already exists
        if 'what-is-fie' in content.lower():
            return False, "Already has FIE link"
        
        # Find the silo-nav div and add link before the closing tag
        pattern = r'(<div class="silo-nav"[^>]*>.*?)(</div>)'
        
        def replacer(match):
            nav_content = match.group(1)
            closing_tag = match.group(2)
            return nav_content + '\n   ' + NEW_SILO_LINK + '\n' + closing_tag
        
        new_content = re.sub(pattern, replacer, content, count=1, flags=re.DOTALL)
        
        if new_content == content:
            return False, "Could not find silo-nav"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "Added FIE link"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def add_fie_card_to_index(file_path):
    """Add the FIE card to the index.html resources grid"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if card already exists
        if 'What Is an FIE?' in content:
            return False, "Already has FIE card"
        
        # Find the resources grid closing and add card before it
        # Look for patterns like: </div></div> before main content ends
        grid_pattern = r'(</div>\s*</div>\s*</main>)'
        
        new_content = re.sub(
            grid_pattern,
            NEW_INDEX_CARD + '\n' + r'\1',
            content,
            count=1
        )
        
        if new_content == content:
            return False, "Could not find resources grid end"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "Added FIE card"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    print("=" * 70)
    print("ADDING 'WHAT IS AN FIE?' TO 48 TARGET DISTRICT PAGES")
    print("=" * 70)
    print()
    
    districts_path = Path(DISTRICTS_FOLDER)
    
    if not districts_path.exists():
        print(f"❌ Districts folder not found: {DISTRICTS_FOLDER}")
        return
    
    # Get all district directories
    all_dirs = [d for d in districts_path.iterdir() if d.is_dir()]
    
    # Filter to only target districts
    district_dirs = [d for d in all_dirs if d.name in TARGET_SLUGS]
    
    print(f"Found {len(district_dirs)} target districts (out of {len(all_dirs)} total)")
    print(f"Target districts: {len(TARGET_SLUGS)}")
    print()
    
    if len(district_dirs) < len(TARGET_SLUGS):
        print(f"⚠ Warning: Only found {len(district_dirs)} of {len(TARGET_SLUGS)} target districts")
        missing = TARGET_SLUGS - set(d.name for d in district_dirs)
        print(f"Missing: {', '.join(list(missing)[:5])}")
        print()
    
    silo_updated = 0
    index_updated = 0
    errors = []
    
    for district_dir in sorted(district_dirs, key=lambda x: x.name):
        district_slug = district_dir.name
        print(f"Processing: {district_slug}")
        
        # Get all HTML files in this district
        html_files = list(district_dir.glob("*.html"))
        
        for html_file in html_files:
            filename = html_file.name
            
            # Skip what-is-fie.html itself
            if filename == "what-is-fie.html":
                continue
            
            # Handle index.html - add card
            if filename == "index.html":
                success, msg = add_fie_card_to_index(html_file)
                if success:
                    index_updated += 1
                    print(f"  ✓ index.html - {msg}")
                elif "Already" not in msg:
                    print(f"  ⚠ index.html - {msg}")
            
            # For other pages - add silo nav link
            else:
                success, msg = add_fie_link_to_silo_nav(html_file)
                if success:
                    silo_updated += 1
                    print(f"  ✓ {filename} - {msg}")
                elif "Already" not in msg and "Could not find" not in msg:
                    errors.append(f"{district_slug}/{filename}: {msg}")
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✓ Silo nav links added: {silo_updated} files")
    print(f"✓ Index cards added: {index_updated} files")
    print(f"✓ Districts processed: {len(district_dirs)}")
    
    if errors:
        print(f"\n⚠ Errors: {len(errors)}")
        for error in errors[:5]:
            print(f"  - {error}")
    
    print()
    print("✅ Done! Check a few files to verify the changes.")

if __name__ == "__main__":
    main()