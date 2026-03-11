r"""
Extract and Separate Batch Content into English and Spanish
============================================================
This script extracts content from your batch file and separates it:
- English pages → /districts/
- Spanish pages → /es-districts/

Usage:
    python extract_existing_batch.py
"""

import json
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

# Paths
BATCH_FILE = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\msgbatch_01MGmmvhTMRMVyLZDNVYkqGe_results.jsonl"
ENGLISH_OUTPUT = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"
SPANISH_OUTPUT = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts"
ENGLISH_TEMPLATE = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts\template.html"
SPANISH_TEMPLATE = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts\template.html"


def clean_html_content(html_str):
    """Remove markdown code fences and clean HTML."""
    html_str = re.sub(r'^```html\s*', '', html_str, flags=re.MULTILINE)
    html_str = re.sub(r'\s*```$', '', html_str, flags=re.MULTILINE)
    return html_str.strip()


def get_district_info(district_slug):
    """Convert district slug to proper names."""
    parts = district_slug.split('-')
    parts = [p for p in parts if p != 'isd']
    
    district_name = ' '.join(word.capitalize() for word in parts) + ' ISD'
    city_name = ' '.join(word.capitalize() for word in parts)
    acronym = ''.join(word[0].upper() for word in parts) + 'ISD'
    
    return {
        'district_name': district_name,
        'district_slug': district_slug,
        'city_name': city_name,
        'acronym': acronym
    }


def determine_filename(page_type, district_slug, is_spanish):
    """Create appropriate filename."""
    if page_type == 'index':
        return 'index.html'
    
    # Map page types to filenames
    filename_map = {
        'evaluation-child-find': 'evaluation-child-find',
        'ard-process-guide': 'ard-process-guide', 
        'grievance-dispute-resolution': 'grievance-dispute-resolution',
        'como-solicitar-una-evaluacion-fie': 'como-solicitar-una-evaluacion-fie'
    }
    
    base_name = filename_map.get(page_type, page_type)
    
    # Add district slug
    return f"{base_name}-{district_slug}.html"


def apply_simple_wrapper(html_content, district_info, is_spanish):
    """Apply a simple HTML wrapper if template is not available."""
    
    # Create basic HTML structure
    lang = "es" if is_spanish else "en"
    
    wrapper = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>{district_info['district_name']} Special Education</title>
    <link href="/style.css" rel="stylesheet"/>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>"""
    
    # Replace district tokens
    replacements = {
        'BROWNSVILLE ISD': district_info['district_name'],
        'brownsville-isd': district_info['district_slug'],
        'BISD': district_info['acronym'],
        'Brownsville': district_info['city_name']
    }
    
    for old_val, new_val in replacements.items():
        wrapper = wrapper.replace(old_val, new_val)
    
    return wrapper


def process_batch_file(batch_path):
    """Process the batch file and separate into English and Spanish."""
    
    print("=" * 70)
    print("Extracting and Separating Batch Content")
    print("=" * 70)
    print()
    
    if not os.path.exists(batch_path):
        print(f"❌ Error: Batch file not found: {batch_path}")
        return
    
    # Stats
    stats = {
        'total': 0,
        'english': 0,
        'spanish': 0,
        'failed': 0,
        'by_district': {}
    }
    
    # Process each line
    with open(batch_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            stats['total'] += 1
            
            try:
                # Parse JSON
                data = json.loads(line)
                custom_id = data.get('custom_id', '')
                result = data.get('result', {})
                
                # Check if successful
                if result.get('type') != 'succeeded':
                    stats['failed'] += 1
                    continue
                
                # Extract content
                message = result.get('message', {})
                content_blocks = message.get('content', [])
                
                if not content_blocks:
                    stats['failed'] += 1
                    continue
                
                html_content = content_blocks[0].get('text', '')
                if not html_content:
                    stats['failed'] += 1
                    continue
                
                # Clean HTML
                html_content = clean_html_content(html_content)
                
                # Extract district and page type
                parts = custom_id.split('_', 1)
                if len(parts) != 2:
                    stats['failed'] += 1
                    continue
                
                district_slug = parts[0]
                page_type = parts[1]
                
                # Determine language and output directory
                is_spanish = 'como-solicitar' in page_type
                output_dir = SPANISH_OUTPUT if is_spanish else ENGLISH_OUTPUT
                
                # Get district info
                district_info = get_district_info(district_slug)
                
                # Apply wrapper (simple since templates may not exist yet)
                formatted_html = apply_simple_wrapper(html_content, district_info, is_spanish)
                
                # Create output directory
                district_dir = os.path.join(output_dir, district_slug)
                os.makedirs(district_dir, exist_ok=True)
                
                # Create filename
                filename = determine_filename(page_type, district_slug, is_spanish)
                output_path = os.path.join(district_dir, filename)
                
                # Write file
                with open(output_path, 'w', encoding='utf-8') as out_file:
                    out_file.write(formatted_html)
                
                # Update stats
                if is_spanish:
                    stats['spanish'] += 1
                    lang_marker = "🇪🇸"
                else:
                    stats['english'] += 1
                    lang_marker = "🇺🇸"
                
                print(f"{lang_marker} {district_slug}/{filename}")
                
                # Track by district
                if district_slug not in stats['by_district']:
                    stats['by_district'][district_slug] = {'english': 0, 'spanish': 0}
                
                if is_spanish:
                    stats['by_district'][district_slug]['spanish'] += 1
                else:
                    stats['by_district'][district_slug]['english'] += 1
                
            except Exception as e:
                print(f"❌ Line {line_num}: Error - {e}")
                stats['failed'] += 1
    
    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total lines processed: {stats['total']}")
    print(f"✓ English pages created: {stats['english']} → {ENGLISH_OUTPUT}")
    print(f"✓ Spanish pages created: {stats['spanish']} → {SPANISH_OUTPUT}")
    print(f"❌ Failed: {stats['failed']}")
    print()
    
    print(f"Total districts: {len(stats['by_district'])}")
    print()
    
    # Show what's missing
    print("=" * 70)
    print("📋 WHAT YOU HAVE vs. WHAT YOU NEED")
    print("=" * 70)
    print()
    
    print("For each district, you need:")
    print("  English: 5 pages (index, evaluation, ard, grievance, como-solicitar)")
    print("  Spanish: 5 pages (index, evaluation, ard, grievance, como-solicitar)")
    print()
    
    print("Current status:")
    complete_english = sum(1 for d in stats['by_district'].values() if d['english'] == 4)
    complete_spanish = sum(1 for d in stats['by_district'].values() if d['spanish'] == 5)
    
    print(f"  English: {complete_english}/{len(stats['by_district'])} districts have 4/5 pages")
    print(f"  Spanish: {complete_spanish}/{len(stats['by_district'])} districts have 1/5 pages")
    print()
    
    print("Still need to generate:")
    print(f"  • {len(stats['by_district'])} English 'como-solicitar' pages")
    print(f"  • {len(stats['by_district']) * 4} Spanish pages:")
    print(f"    - {len(stats['by_district'])} Spanish index pages")
    print(f"    - {len(stats['by_district'])} Spanish evaluation pages")
    print(f"    - {len(stats['by_district'])} Spanish ARD pages")
    print(f"    - {len(stats['by_district'])} Spanish grievance pages")
    print()
    
    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print()
    print("1. ✅ You now have extracted all existing content")
    print("2. 📝 Review the files to make sure they look good")
    print("3. 🔄 Generate the missing content:")
    print("   - Option A: Use Claude API batch mode (fastest)")
    print("   - Option B: Use translation + formatting scripts")
    print("   - Option C: Generate manually with Claude.ai")
    print()


def main():
    """Main execution."""
    process_batch_file(BATCH_FILE)
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()