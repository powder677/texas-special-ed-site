#!/usr/bin/env python3
"""
Fix broken href links in HTML files
Fixes patterns like: href="/districts/weatherford-isd/a>
"""

import sys
from pathlib import Path
import re

def fix_broken_links(file_path):
    """Fix broken href links in a file."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = 0
        
        # Pattern 1: Fix href="/districts/DISTRICT/a> or similar malformed endings
        # These should probably be removed or fixed to proper links
        # Common pattern: <a href="/districts/DISTRICT/a></a> (broken)
        # Should be: <a href="/districts/DISTRICT/"></a> or similar
        
        # First, let's fix the most common pattern: href="...../a>
        # Replace with href="...../" (remove the 'a>')
        pattern1 = re.compile(
            r'href="([^"]*?)/a>"',
            re.IGNORECASE
        )
        
        def fix_href(match):
            nonlocal changes
            path = match.group(1)
            # Remove trailing /a and just leave the path with /
            changes += 1
            return f'href="{path}/"'
        
        content = pattern1.sub(fix_href, content)
        
        # Pattern 2: Sometimes there's no closing quote
        # href="/districts/DISTRICT/a></li>
        # This needs to add the closing quote
        pattern2 = re.compile(
            r'href="([^"]*?/a>)([^"])',
            re.IGNORECASE
        )
        
        def fix_href_no_quote(match):
            nonlocal changes
            path = match.group(1)  # "/districts/DISTRICT/a>"
            next_char = match.group(2)  # The next character
            
            # Remove /a> and add proper closing
            clean_path = path.replace('/a>', '/')
            changes += 1
            return f'href="{clean_path}"{next_char}'
        
        content = pattern2.sub(fix_href_no_quote, content)
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"Fixed {changes} broken links"
        else:
            return False, "No broken links found"
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def process_directory(base_path):
    """Process all HTML files."""
    
    base_path = Path(base_path)
    
    if not base_path.exists():
        print(f"❌ Error: {base_path} does not exist")
        return
    
    # Find all HTML files
    html_files = list(base_path.rglob('*.html'))
    
    if not html_files:
        print(f"❌ No HTML files found in {base_path}")
        return
    
    print(f"🔧 Found {len(html_files)} HTML files to check")
    print("=" * 70)
    
    updated = 0
    skipped = 0
    errors = 0
    total_fixes = 0
    
    for html_file in html_files:
        success, message = fix_broken_links(html_file)
        
        if success:
            updated += 1
            # Extract number of fixes
            if "Fixed" in message:
                num = int(message.split()[1])
                total_fixes += num
            
            # Show first 50
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
    print(f"✓ Total broken links fixed: {total_fixes}")
    print(f"○ Skipped (no issues): {skipped}")
    if errors > 0:
        print(f"✗ Errors: {errors}")
    print("\nDone!")


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("FIX BROKEN HREF LINKS")
        print("=" * 70)
        print("\nUsage:")
        print("  python fix_broken_links.py <directory>")
        print("\nExamples:")
        print("  python fix_broken_links.py districts")
        print("\nThis fixes broken patterns like:")
        print('  href="/districts/weatherford-isd/a>" → href="/districts/weatherford-isd/"')
        print("=" * 70)
        print("\n⚠️  IMPORTANT: Run find_broken_links.py first to see what will be fixed!")
        print("\nContinue? (y/n): ", end='')
        
        response = input().strip().lower()
        if response != 'y':
            print("Cancelled.")
            sys.exit(0)
        
        print()
        sys.exit(1)
    
    base_path = sys.argv[1]
    process_directory(base_path)


if __name__ == '__main__':
    main()