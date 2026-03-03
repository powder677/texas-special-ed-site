"""
Add "What Is an FIE?" link to silo navigation on district pages
AND add a hub-card for the new page on each district's index.html
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

# The new link HTML to add to silo navigation
NEW_SILO_LINK = '''<a href="what-is-fie.html" style="color: #495057; text-decoration: none; font-weight: 500; padding: 6px 12px; border-radius: 4px; background: white; transition: all 0.2s; border: 1px solid #dee2e6;">📝 What Is an FIE?</a>'''

# The new hub-card for index pages (matches existing format)
NEW_INDEX_CARD = '''<a class="hub-card" href="what-is-fie.html">
<div class="hub-card-icon">📝</div>
<h3>What Is an FIE?</h3>
<p>Learn about Full Individual Evaluations — the 45-day timeline, what's tested, and how to request one in writing.</p>
</a>
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
            return False, "No silo-nav found"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "Added link"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def add_fie_card_to_index(file_path):
    """Add the FIE hub-card to the index.html"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if card already exists
        if 'What Is an FIE?' in content:
            return False, "Already has card"
        
        # Find the last hub-card closing tag and insert after it
        # Look for pattern: </a> followed by either <div class="sales-card" or </main>
        pattern = r'(</a>\s*)(<div class="sales-card"|</main>)'
        
        new_content = re.sub(
            pattern,
            r'\1' + NEW_INDEX_CARD + r'\2',
            content,
            count=1
        )
        
        if new_content == content:
            return False, "No insertion point found"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "Added card"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    print("=" * 70)
    print("ADDING 'WHAT IS AN FIE?' TO 48 TARGET DISTRICTS")
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
    
    print(f"Found {len(district_dirs)}/48 target districts")
    print()
    
    silo_updated = 0
    index_updated = 0
    
    for district_dir in sorted(district_dirs, key=lambda x: x.name):
        district_slug = district_dir.name
        
        # Get all HTML files
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
                    print(f"✓ {district_slug}/index.html - {msg}")
            
            # For other pages - add silo nav link
            else:
                success, msg = add_fie_link_to_silo_nav(html_file)
                if success:
                    silo_updated += 1
    
    print()
    print("=" * 70)
    print(f"✓ Silo nav links added: {silo_updated}")
    print(f"✓ Index cards added: {index_updated}")
    print(f"✓ Districts updated: {len(district_dirs)}")
    print("=" * 70)

if __name__ == "__main__":
    main()