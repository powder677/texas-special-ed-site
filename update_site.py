import os
from bs4 import BeautifulSoup

# Define your directories
BASE_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"
ALLEN_DIR = os.path.join(BASE_DIR, "districts", "allen-isd")
BLOG_DIR = os.path.join(BASE_DIR, "blog")

# Define file paths
TEMPLATE_SOURCE = os.path.join(BLOG_DIR, "fie-evaluation-timeline.html")
NEW_FIE_PAGE = os.path.join(BLOG_DIR, "what-is-fie.html")
NEW_UPDATES_PAGE = os.path.join(ALLEN_DIR, "district-updates.html")
ALLEN_INDEX = os.path.join(ALLEN_DIR, "index.html")
ALLEN_GRIEVANCE = os.path.join(ALLEN_DIR, "grievance-dispute-resolution.html")

def inject_site_formatting(new_file_path, template_soup):
    """Applies the site's global header, nav, and footer to the new pages."""
    if not os.path.exists(new_file_path):
        print(f"⚠️ File not found, skipping formatting: {new_file_path}")
        return

    with open(new_file_path, 'r', encoding='utf-8') as f:
        page_soup = BeautifulSoup(f, 'html.parser')

    # Extract global header and footer from your existing template
    site_header = template_soup.find('header', class_='site-header')
    site_footer = template_soup.find('footer', class_='site-footer')
    
    # Also grab the main stylesheet link to ensure fonts/colors match
    site_css = template_soup.find('link', rel='stylesheet')

    body = page_soup.find('body')
    head = page_soup.find('head')

    if body and site_header and site_footer:
        # Check if header already exists to prevent duplicate injections
        if not body.find('header', class_='site-header'):
            body.insert(0, site_header)
            body.append(site_footer)
            
        if head and site_css and not head.find('link', href='/style.css'):
            head.append(site_css)

        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.write(str(page_soup))
        print(f"✅ Formatted: {os.path.basename(new_file_path)}")

def add_allen_silo_links():
    """Injects a call-out banner linking to the updates page in the Allen silo."""
    callout_html = """
    <div class="updates-callout" style="background: #fdf3cd; border-left: 5px solid #e67e22; padding: 15px; margin: 25px 0; border-radius: 4px; font-family: sans-serif;">
        <strong>🚨 Allen ISD Active Updates:</strong> Stay informed on the latest civil rights news and PDSES grant deadlines. <a href="/districts/allen-isd/district-updates.html" style="color: #c0392b; font-weight: bold;">Read the 2025-2026 Parent Updates →</a>
    </div>
    """
    callout_soup = BeautifulSoup(callout_html, 'html.parser')

    for file_path in [ALLEN_INDEX, ALLEN_GRIEVANCE]:
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
        # Find the main content area to insert the link at the top
        main_content = soup.find('main') or soup.find('body')
        
        # Prevent duplicate links
        if not soup.find('div', class_='updates-callout'):
            if main_content.find('h1'):
                main_content.find('h1').insert_after(callout_soup)
            else:
                main_content.insert(0, callout_soup)
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(f"🔗 Added link to: {os.path.basename(file_path)}")

def add_blog_silo_links():
    """Injects a link to the new FIE definition page in the timeline article."""
    if not os.path.exists(TEMPLATE_SOURCE):
        return

    with open(TEMPLATE_SOURCE, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    link_html = """
    <div class="fie-callout" style="background: #f0f9ff; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0; border-radius: 4px;">
        <strong>📖 Need a complete breakdown?</strong> Read our comprehensive guide: <a href="/blog/what-is-fie.html" style="font-weight: bold; color: #1560a8;">What is an FIE in Special Education?</a>
    </div>
    """
    link_soup = BeautifulSoup(link_html, 'html.parser')

    # Prevent duplicate links
    if not soup.find('div', class_='fie-callout'):
        # Find the specific section in the timeline article to insert the link
        target_h2 = soup.find(lambda tag: tag.name == 'h2' and 'Understanding the Full and Individual Evaluation' in tag.text)
        
        if target_h2:
            target_h2.insert_after(link_soup)
            with open(TEMPLATE_SOURCE, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print("🔗 Added link to: fie-evaluation-timeline.html")

if __name__ == "__main__":
    print("Starting site update process...")
    
    # Load the template to extract header/footer
    if os.path.exists(TEMPLATE_SOURCE):
        with open(TEMPLATE_SOURCE, 'r', encoding='utf-8') as f:
            template = BeautifulSoup(f, 'html.parser')
            
        # 1. Format the new pages
        inject_site_formatting(NEW_FIE_PAGE, template)
        inject_site_formatting(NEW_UPDATES_PAGE, template)
        
        # 2. Add the cross-links
        add_allen_silo_links()
        add_blog_silo_links()
        
        print("✨ Done! Your site is linked and formatted.")
    else:
        print(f"❌ Error: Could not find template file at {TEMPLATE_SOURCE}")