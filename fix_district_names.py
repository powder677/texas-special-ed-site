#!/usr/bin/env python3
"""
Fix hardcoded Abilene ISD references on Spanish pages
Fixes BOTH:
1. Text: "Recursos de Abilene ISD:" -> "Recursos de Houston ISD:" (or whatever district)
2. Links: /districts/abilene-isd/... -> /districts/houston-isd/... (or whatever district)
"""

import sys
from pathlib import Path
import re

def folder_to_display_name(folder_name):
    """Convert folder name to display name."""
    
    # Special cases
    special_cases = {
        'zapata-county-isd': 'Zapata County ISD',
        'white-settlement-isd': 'White Settlement ISD',
    }
    
    if folder_name in special_cases:
        return special_cases[folder_name]
    
    # Auto-generate: convert "houston-isd" to "Houston ISD"
    parts = folder_name.split('-')
    display_parts = []
    for part in parts:
        if part.upper() == 'ISD':
            display_parts.append('ISD')
        else:
            display_parts.append(part.capitalize())
    
    return ' '.join(display_parts)


def fix_district_references(file_path):
    """Fix both text and links to match the correct district."""
    
    try:
        # Extract district folder name from path
        file_str = str(file_path)
        
        # Find the district folder name
        if '\\es\\' in file_str:
            parts = file_str.split('\\')
        elif '/es/' in file_str:
            parts = file_str.split('/')
        else:
            return False, "Not in es folder"
        
        # Find "districts" in the path
        try:
            districts_idx = parts.index('districts')
            correct_district_folder = parts[districts_idx + 1]
        except (ValueError, IndexError):
            return False, "Could not extract district name"
        
        # Get the proper display name
        correct_display_name = folder_to_display_name(correct_district_folder)
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = []
        
        # FIX 1: Replace "Recursos de [WRONG DISTRICT]:" with correct district
        pattern_text = re.compile(r'Recursos de [^:]+:', re.IGNORECASE)
        correct_text = f'Recursos de {correct_display_name}:'
        
        if correct_text not in content and pattern_text.search(content):
            content = pattern_text.sub(correct_text, content)
            changes.append("text")
        
        # FIX 2: Replace wrong district links with correct district
        # Match: href="/districts/WRONG-DISTRICT/...
        # Replace with: href="/districts/CORRECT-DISTRICT/...
        pattern_links = re.compile(
            r'href="(/districts/)([^/]+)(/[^"]*)"',
            re.IGNORECASE
        )
        
        def replace_district_in_link(match):
            prefix = match.group(1)  # "/districts/"
            wrong_district = match.group(2)  # "abilene-isd" or whatever
            rest_of_path = match.group(3)  # "/es/page.html" or similar
            
            # Only replace if it's pointing to a different district
            if wrong_district != correct_district_folder:
                return f'href="{prefix}{correct_district_folder}{rest_of_path}"'
            return match.group(0)
        
        new_content = pattern_links.sub(replace_district_in_link, content)
        if new_content != content:
            content = new_content
            changes.append("links")
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"Fixed: {', '.join(changes)}"
        else:
            return False, "Already correct"
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def process_directory(base_path):
    """Process all Spanish HTML files."""
    
    base_path = Path(base_path)
    
    if not base_path.exists():
        print(f"❌ Error: {base_path} does not exist")
        return
    
    # Find all HTML files in /es/ directories
    all_files = list(base_path.rglob('*.html'))
    html_files = [f for f in all_files if '/es/' in str(f) or '\\es\\' in str(f)]
    
    if not html_files:
        print(f"❌ No Spanish (/es/) HTML files found in {base_path}")
        return
    
    print(f"🇪🇸 Found {len(html_files)} Spanish files to process")
    print("🔧 Fixing district names in BOTH text and links")
    print("=" * 70)
    
    updated = 0
    skipped = 0
    errors = 0
    
    for html_file in html_files:
        success, message = fix_district_references(html_file)
        
        if success:
            updated += 1
            # Show first 50 to avoid spam
            if updated <= 50:
                print(f"✓ {html_file.name}: {message}")
        else:
            if "Error" in message:
                errors += 1
                if errors <= 10:
                    print(f"✗ {html_file.name}: {message}")
            else:
                skipped += 1
    
    print("=" * 70)
    print(f"\n✓ Files updated: {updated}")
    print(f"○ Skipped (already correct): {skipped}")
    if errors > 0:
        print(f"✗ Errors: {errors}")
    print("\nDone!")


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("FIX DISTRICT NAMES - Spanish Pages")
        print("=" * 70)
        print("\nUsage:")
        print("  python fix_district_names.py <directory>")
        print("\nExamples:")
        print("  python fix_district_names.py districts")
        print("\nThis fixes:")
        print("  1. Text: 'Recursos de Abilene ISD:' -> 'Recursos de Houston ISD:'")
        print("  2. Links: /districts/abilene-isd/... -> /districts/houston-isd/...")
        print("\nEach page will be fixed to match its own district folder")
        print("=" * 70)
        sys.exit(1)
    
    base_path = sys.argv[1]
    process_directory(base_path)


if __name__ == '__main__':
    main()