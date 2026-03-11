r"""
Format Spanish District Sub-Pages
===================================
This script reformats Spanish district sub-pages to match the template structure.
It preserves the unique content of each page while applying the standard template format.

Usage:
    python format_spanish_subpages.py

Directory Structure Expected:
    C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts\
        district-name\
            como-solicitar-una-evaluacion-fie-en-district-name.html
            que-es-una-evaluacion-fie-en-district-name.html
            etc.
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

# Path to your Spanish districts folder
BASE_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts"

# Template file path (update this to where your template is)
TEMPLATE_PATH = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts\template.html"


def extract_district_info(filepath):
    """Extract district name and slug from filepath or filename."""
    filename = os.path.basename(filepath)
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


def extract_page_content(html_content):
    """Extract the main content from an existing HTML file."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Try to find existing title
    title_tag = soup.find('title')
    title = title_tag.text if title_tag else ''
    
    # Try to find existing meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    description = meta_desc['content'] if meta_desc and 'content' in meta_desc.attrs else ''
    
    # Try to find main content
    content_section = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
    
    if content_section:
        # Get all the HTML content
        main_content = str(content_section)
    else:
        # If no specific content section found, get body content
        body = soup.find('body')
        main_content = str(body) if body else html_content
    
    return {
        'title': title,
        'description': description,
        'content': main_content
    }


def apply_template(template_content, page_data, district_info):
    """Apply the template to a page's content with district-specific replacements."""
    
    # Load template
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
    
    # Get the template HTML as string for bulk replacements
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


def format_file(filepath, template_content):
    """Format a single Spanish file using the template."""
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
    page_data = extract_page_content(original_content)
    
    # Apply template
    new_content = apply_template(template_content, page_data, district_info)
    
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


def find_spanish_subpages(base_dir):
    """Find all Spanish sub-pages (excluding index pages)."""
    subpages = []
    
    # Walk through the es-districts directory
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            # Skip index pages and non-HTML files
            if file.endswith('.html') and 'index' not in file.lower():
                filepath = os.path.join(root, file)
                subpages.append(filepath)
    
    return subpages


def main():
    """Main execution function."""
    print("=" * 70)
    print("Spanish District Sub-Pages Formatter")
    print("=" * 70)
    print()
    
    # Check if base directory exists
    if not os.path.exists(BASE_DIR):
        print(f"❌ Error: Directory not found: {BASE_DIR}")
        print("Please update BASE_DIR in the script to match your folder location.")
        return
    
    # Load template
    if not os.path.exists(TEMPLATE_PATH):
        print(f"❌ Error: Template file not found: {TEMPLATE_PATH}")
        print("Please save the template file and update TEMPLATE_PATH in the script.")
        return
    
    try:
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            template_content = f.read()
        print(f"✓ Template loaded: {TEMPLATE_PATH}")
        print()
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return
    
    # Find all Spanish sub-pages
    subpages = find_spanish_subpages(BASE_DIR)
    
    if not subpages:
        print(f"❌ No Spanish sub-pages found in: {BASE_DIR}")
        return
    
    print(f"Found {len(subpages)} Spanish sub-pages to format")
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
    
    for filepath in subpages:
        if format_file(filepath, template_content):
            success_count += 1
        else:
            error_count += 1
        print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total files: {len(subpages)}")
    print(f"✓ Successfully formatted: {success_count}")
    print(f"❌ Errors: {error_count}")
    print()
    print("Backups have been created with .backup extension")
    print("To restore a file, rename the .backup file to remove the extension")


if __name__ == "__main__":
    main()