#!/usr/bin/env python3
"""
Fix internal links on Spanish pages that are missing /es/ in the path
Example: /districts/abilene-isd/como-solicitar... 
Should be: /districts/abilene-isd/es/como-solicitar...
"""

import sys
from pathlib import Path
import re

def fix_spanish_links(file_path):
    """Fix internal district links missing /es/ in Spanish pages."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match district links missing /es/
        # Matches: /districts/DISTRICT-NAME/page.html (without /es/)
        # Replaces with: /districts/DISTRICT-NAME/es/page.html
        
        # This pattern matches links like:
        # href="/districts/abilene-isd/como-solicitar-una-evaluacion-fie-en-abilene-isd"
        # and adds /es/ before the page name
        
        pattern = re.compile(
            r'href="(/districts/[^/]+/)([^/"]+\.html)"',
            re.IGNORECASE
        )
        
        changes = 0
        
        def replace_link(match):
            nonlocal changes
            district_path = match.group(1)  # e.g., "/districts/abilene-isd/"
            page_name = match.group(2)      # e.g., "como-solicitar-una-evaluacion-fie-en-abilene-isd.html"
            
            # Check if it's already correct (has /es/)
            full_match = match.group(0)
            if '/es/' in full_match:
                return full_match
            
            # Add /es/ before the page name
            changes += 1
            return f'href="{district_path}es/{page_name}"'
        
        new_content = pattern.sub(replace_link, content)
        
        # Also fix links without .html extension
        pattern2 = re.compile(
            r'href="(/districts/[^/]+/)([^/"]+)"(?!\s*[^>]*\.html)',
            re.IGNORECASE
        )
        
        def replace_link2(match):
            nonlocal changes
            district_path = match.group(1)
            page_name = match.group(2)
            
            full_match = match.group(0)
            if '/es/' in full_match or page_name == 'index.html' or page_name == '':
                return full_match
            
            changes += 1
            return f'href="{district_path}es/{page_name}"'
        
        new_content = pattern2.sub(replace_link2, new_content)
        
        # Write back if changes were made
        if changes > 0 and new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, f"Fixed {changes} links"
        else:
            return False, "No links to fix"
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def process_directory(base_path):
    """Process all HTML files in /es/ directories."""
    
    base_path = Path(base_path)
    
    if not base_path.exists():
        print(f"❌ Error: {base_path} does not exist")
        return
    
    # Find all HTML files
    all_files = list(base_path.rglob('*.html'))
    
    # Filter to only /es/ files
    html_files = [f for f in all_files if '/es/' in str(f) or '\\es\\' in str(f)]
    
    if not html_files:
        print(f"❌ No Spanish (/es/) HTML files found in {base_path}")
        return
    
    print(f"🇪🇸 Found {len(html_files)} Spanish files to process")
    print("=" * 70)
    
    updated = 0
    skipped = 0
    errors = 0
    total_links_fixed = 0
    
    for html_file in html_files:
        success, message = fix_spanish_links(html_file)
        
        if success:
            updated += 1
            # Extract number of links fixed from message
            if "Fixed" in message:
                num = int(message.split()[1])
                total_links_fixed += num
            
            # Show first 50 to avoid spam
            if updated <= 50:
                print(f"✓ {html_file.name}: {message}")
        else:
            if "Error" in message:
                errors += 1
                print(f"✗ {html_file.name}: {message}")
            else:
                skipped += 1
    
    print("=" * 70)
    print(f"\n✓ Files updated: {updated}")
    print(f"✓ Total links fixed: {total_links_fixed}")
    print(f"○ Skipped: {skipped}")
    if errors > 0:
        print(f"✗ Errors: {errors}")
    print("\nDone!")


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("FIX SPANISH INTERNAL LINKS - Add /es/ to paths")
        print("=" * 70)
        print("\nUsage:")
        print("  python fix_spanish_links.py <directory>")
        print("\nExamples:")
        print("  python fix_spanish_links.py districts")
        print("\nThis will fix links like:")
        print("  /districts/abilene-isd/como-solicitar-una-evaluacion...")
        print("To:")
        print("  /districts/abilene-isd/es/como-solicitar-una-evaluacion...")
        print("\nOnly processes files in /es/ directories")
        print("=" * 70)
        sys.exit(1)
    
    base_path = sys.argv[1]
    process_directory(base_path)


if __name__ == '__main__':
    main()