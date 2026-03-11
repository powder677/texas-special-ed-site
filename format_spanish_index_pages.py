r"""
Format Spanish District Index Pages
====================================
This script reformats Spanish district index/overview pages.
These are the main landing pages for each district (index.html files).

Usage:
    python format_spanish_index_pages.py

Directory Structure Expected:
    C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts\
        district-name\
            index.html (Spanish version of district overview)
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

# Path to your Spanish districts folder
BASE_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts"

# Template file path for index pages (you may need a separate index template)
INDEX_TEMPLATE_PATH = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts\index-template.html"


def extract_district_info(filepath):
    """Extract district name and slug from filepath."""
    parent_dir = os.path.basename(os.path.dirname(filepath))
    
    # Extract district slug from parent directory
    district_slug = parent_dir
    
    # Convert slug to display name (e.g., "fort-worth-isd" -> "Fort Worth ISD")
    parts = district_slug.replace('-isd', '').split('-')
    district_name = ' '.join(word.capitalize() for word in parts) + ' ISD'
    
    # Extract city name (e.g., "Fort Worth")
    city_parts = district_slug.replace('-isd', '').split('-')
    city_name = ' '.join(word.capitalize() for word in city_parts)
    
    # Create acronym (e.g., "FWISD")
    acronym = ''.join(word[0].upper() for word in parts) + 'ISD'
    
    return {
        'district_name': district_name,
        'district_slug': district_slug,
        'city_name': city_name,
        'acronym': acronym
    }


def extract_index_content(html_content):
    """Extract content from an existing index HTML file."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Try to find existing title
    title_tag = soup.find('title')
    title = title_tag.text if title_tag else ''
    
    # Try to find existing meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    description = meta_desc['content'] if meta_desc and 'content' in meta_desc.attrs else ''
    
    # Try to find h1
    h1_tag = soup.find('h1')
    h1_text = h1_tag.text if h1_tag else ''
    
    # Try to find main content
    content_section = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
    
    if content_section:
        main_content = str(content_section)
    else:
        body = soup.find('body')
        main_content = str(body) if body else html_content
    
    # Try to extract any district-specific information
    # This could include contact info, addresses, etc.
    contact_info = {}
    
    return {
        'title': title,
        'description': description,
        'h1': h1_text,
        'content': main_content,
        'contact_info': contact_info
    }


def apply_index_template(template_content, page_data, district_info):
    """Apply the index template to a page's content."""
    
    if not template_content:
        # If no template provided, just do token replacement on existing content
        html_str = page_data['content']
    else:
        template_soup = BeautifulSoup(template_content, 'html.parser')
        
        # Replace title
        if page_data['title']:
            title_tag = template_soup.find('title')
            if title_tag:
                title_tag.string = page_data['title']
        
        # Replace meta description
        if page_data['description']:
            meta_tag = template_soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_tag['content'] = page_data['description']
        
        html_str = str(template_soup)
    
    # Replace district-specific tokens throughout the entire HTML
    replacements = {
        'Fort Worth ISD': district_info['district_name'],
        'fort-worth-isd': district_info['district_slug'],
        'FWISD': district_info['acronym'],
        'Fort Worth': district_info['city_name']
    }
    
    for old_val, new_val in replacements.items():
        html_str = html_str.replace(old_val, new_val)
    
    return html_str


def format_index_file(filepath, template_content=None):
    """Format a single Spanish index file."""
    print(f"Processing: {filepath}")
    
    # Extract district information
    district_info = extract_district_info(filepath)
    print(f"  District: {district_info['district_name']}")
    
    # Read the existing file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False
    
    # Extract page content
    page_data = extract_index_content(original_content)
    
    # Apply template (or just do replacements if no template)
    new_content = apply_index_template(template_content, page_data, district_info)
    
    # Create backup
    backup_path = filepath + '.backup'
    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"  ✓ Backup created: {backup_path}")
    except Exception as e:
        print(f"  ⚠️  Warning: Could not create backup: {e}")
    
    # Write new formatted content
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✓ File formatted successfully")
        return True
    except Exception as e:
        print(f"  ❌ Error writing file: {e}")
        return False


def find_spanish_index_pages(base_dir):
    """Find all Spanish index pages."""
    index_pages = []
    
    # Walk through the es-districts directory
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            # Look for index.html files
            if file.lower() == 'index.html':
                filepath = os.path.join(root, file)
                # Make sure it's in a district subdirectory, not the root
                if os.path.dirname(filepath) != base_dir:
                    index_pages.append(filepath)
    
    return index_pages


def main():
    """Main execution function."""
    print("=" * 70)
    print("Spanish District Index Pages Formatter")
    print("=" * 70)
    print()
    
    # Check if base directory exists
    if not os.path.exists(BASE_DIR):
        print(f"❌ Error: Directory not found: {BASE_DIR}")
        print("Please update BASE_DIR in the script to match your folder location.")
        return
    
    # Try to load template (optional for index pages)
    template_content = None
    if os.path.exists(INDEX_TEMPLATE_PATH):
        try:
            with open(INDEX_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
                template_content = f.read()
            print(f"✓ Template loaded: {INDEX_TEMPLATE_PATH}")
        except Exception as e:
            print(f"⚠️  Warning: Could not load template: {e}")
            print("Will proceed with token replacement only")
    else:
        print(f"ℹ️  No index template found at: {INDEX_TEMPLATE_PATH}")
        print("Will proceed with token replacement only")
    
    print()
    
    # Find all Spanish index pages
    index_pages = find_spanish_index_pages(BASE_DIR)
    
    if not index_pages:
        print(f"❌ No Spanish index pages found in: {BASE_DIR}")
        return
    
    print(f"Found {len(index_pages)} Spanish index pages to format")
    print()
    
    # Confirm before proceeding
    response = input("Do you want to proceed? Backups will be created. (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Cancelled by user.")
        return
    
    print()
    print("Processing files...")
    print("-" * 70)
    
    # Process each file
    success_count = 0
    error_count = 0
    
    for filepath in index_pages:
        if format_index_file(filepath, template_content):
            success_count += 1
        else:
            error_count += 1
        print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total files: {len(index_pages)}")
    print(f"✓ Successfully formatted: {success_count}")
    print(f"❌ Errors: {error_count}")
    print()
    print("Backups have been created with .backup extension")
    print("To restore a file, rename the .backup file to remove the extension")


if __name__ == "__main__":
    main()