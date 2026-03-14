#!/usr/bin/env python3
"""
Find and rename Spanish files that have wrong district name in filename
Example: /districts/canyon-isd/es/como-solicitar-una-evaluacion-fie-en-abilene-isd.html
Should be: /districts/canyon-isd/es/como-solicitar-una-evaluacion-fie-en-canyon-isd.html
"""

import sys
from pathlib import Path
import re

def find_misnamed_files(base_path):
    """Find files where the filename contains a different district than the folder."""
    
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
    
    print(f"🔍 Scanning {len(html_files)} Spanish files for misnamed files...")
    print("=" * 70)
    
    misnamed = []
    
    for html_file in html_files:
        file_str = str(html_file)
        
        # Extract district folder name
        if '\\es\\' in file_str:
            parts = file_str.split('\\')
        elif '/es/' in file_str:
            parts = file_str.split('/')
        else:
            continue
        
        try:
            districts_idx = parts.index('districts')
            correct_district = parts[districts_idx + 1]
        except (ValueError, IndexError):
            continue
        
        # Check if filename contains a district pattern like "-en-DISTRICT-isd"
        # Example: como-solicitar-una-evaluacion-fie-en-waco-isd.html
        district_in_filename_pattern = re.search(r'-en-([\w-]+)-isd', filename)
        
        if district_in_filename_pattern:
            wrong_district = district_in_filename_pattern.group(1)  # e.g., "waco"
            correct_district_base = correct_district.replace('-isd', '')  # e.g., "weslaco"
            
            # Check if they're different
            if wrong_district != correct_district_base:
                # Replace just the district name part, keep everything else
                # Replace "-en-waco-isd" with "-en-weslaco-isd"
                correct_filename = filename.replace(
                    f'-en-{wrong_district}-isd',
                    f'-en-{correct_district_base}-isd'
                )
                
                misnamed.append({
                    'file': html_file,
                    'current': filename,
                    'correct': correct_filename,
                    'district': correct_district
                })
    
    if not misnamed:
        print("✓ No misnamed files found!")
        return
    
    print(f"\n⚠️  Found {len(misnamed)} misnamed files:\n")
    
    for item in misnamed:
        print(f"📁 District: {item['district']}")
        print(f"   Current:  {item['current']}")
        print(f"   Should be: {item['correct']}")
        print()
    
    print("=" * 70)
    print(f"\nWould you like to rename these {len(misnamed)} files? (y/n): ", end='')
    
    response = input().strip().lower()
    
    if response == 'y':
        renamed = 0
        errors = 0
        
        for item in misnamed:
            try:
                old_path = item['file']
                new_path = old_path.parent / item['correct']
                
                old_path.rename(new_path)
                renamed += 1
                print(f"✓ Renamed: {item['current']}")
                
            except Exception as e:
                errors += 1
                print(f"✗ Error renaming {item['current']}: {e}")
        
        print("\n" + "=" * 70)
        print(f"\n✓ Successfully renamed: {renamed}")
        if errors > 0:
            print(f"✗ Errors: {errors}")
        print("\nDone!")
    else:
        print("\nCancelled. No files were renamed.")


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("FIND AND RENAME MISNAMED SPANISH FILES")
        print("=" * 70)
        print("\nUsage:")
        print("  python find_misnamed_files.py <directory>")
        print("\nExamples:")
        print("  python find_misnamed_files.py districts")
        print("\nThis finds files like:")
        print("  /districts/canyon-isd/es/como-solicitar...en-abilene-isd.html")
        print("And renames to:")
        print("  /districts/canyon-isd/es/como-solicitar...en-canyon-isd.html")
        print("=" * 70)
        sys.exit(1)
    
    base_path = sys.argv[1]
    find_misnamed_files(base_path)


if __name__ == '__main__':
    main()