"""
Add "What Is an FIE?" link to the silo navigation on all existing district pages
AND add a card for the new page on each district's index.html
"""

import os
import re
from pathlib import Path

# Configuration
DISTRICTS_FOLDER = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"

# The new link HTML to add
NEW_SILO_LINK = ''''''

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
        
        # Find the silo-nav div
        # Pattern: look for the closing </div> of silo-nav and add link before it
        pattern = r'(<div class="silo-nav"[^>]*>.*?)(</div>)'
        
        def replacer(match):
            nav_content = match.group(1)
            closing_tag = match.group(2)
            # Add the new link before the closing tag
            return nav_content + '\n   ' + NEW_SILO_LINK + '\n' + closing_tag
        
        new_content = re.sub(pattern, replacer, content, count=1, flags=re.DOTALL)
        
        if new_content == content:
            return False, "Could not find silo-nav"
        
        # Write back
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
        
        # Find the last resource-card and add the new one after it
        # Look for the closing </div> of a resource-card
        pattern = r'(</div>\s*<!-- [^>]+ Card -->|<div class="resource-card">.*?</div>)(?=\s*</div>\s*<!-- End resources grid -->|$)'
        
        # Simpler approach: find the closing of the resources grid and add before it
        grid_pattern = r'(<!-- End resources grid -->|</div>\s*</div>\s*<!-- /\.resources-grid -->)'
        
        new_content = re.sub(
            grid_pattern,
            NEW_INDEX_CARD + r'\n\1',
            content,
            count=1,
            flags=re.DOTALL
        )
        
        if new_content == content:
            return False, "Could not find resources grid"
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "Added FIE card"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    print("=" * 60)
    print("ADDING 'WHAT IS AN FIE?' TO ALL DISTRICT PAGES")
    print("=" * 60)
    print()
    
    districts_path = Path(DISTRICTS_FOLDER)
    
    if not districts_path.exists():
        print(f"❌ Districts folder not found: {DISTRICTS_FOLDER}")
        return
    
    # Get all district subdirectories
    district_dirs = [d for d in districts_path.iterdir() if d.is_dir()]
    
    print(f"Found {len(district_dirs)} districts")
    print()
    
    silo_updated = 0
    index_updated = 0
    errors = []
    
    for district_dir in district_dirs:
        district_name = district_dir.name
        
        # Update all HTML files in the district (except index and what-is-fie)
        html_files = list(district_dir.glob("*.html"))
        
        for html_file in html_files:
            filename = html_file.name
            
            # Skip what-is-fie.html itself
            if filename == "what-is-fie.html":
                continue
            
            # Handle index.html differently (add card)
            if filename == "index.html":
                success, msg = add_fie_card_to_index(html_file)
                if success:
                    index_updated += 1
                    print(f"  ✓ {district_name}/index.html - {msg}")
                else:
                    if "Already" not in msg:
                        errors.append(f"{district_name}/index.html: {msg}")
            
            # For other pages, add silo nav link
            else:
                success, msg = add_fie_link_to_silo_nav(html_file)
                if success:
                    silo_updated += 1
                    print(f"  ✓ {district_name}/{filename} - {msg}")
                else:
                    if "Already" not in msg and "Could not find" not in msg:
                        errors.append(f"{district_name}/{filename}: {msg}")
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✓ Silo nav links added: {silo_updated} files")
    print(f"✓ Index cards added: {index_updated} files")
    
    if errors:
        print(f"\n⚠ Errors encountered: {len(errors)}")
        for error in errors[:10]:
            print(f"  - {error}")
    
    print()
    print("Done! Check a few files to verify the changes look good.")

if __name__ == "__main__":
    main()