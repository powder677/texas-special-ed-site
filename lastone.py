import os
import glob
from bs4 import BeautifulSoup

# Standardized CTA Templates
LETTER_CTA_HTML = """
<div class="sales-card" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%); margin: 32px 0;">
<h3 style="margin-top:0; color:#fff;">Show the ISD You Mean Business</h3>
<p style="font-size:15px; color:#cbd5e1; margin-bottom: 24px;">A verbal request has no legal weight. A written letter starts the 45-day clock and forces a response within 15 school days.</p>
<a href="/resources/Iep-letter.html" style="background:#d4af37; color:#0f172a; padding: 16px 32px; text-decoration: none; border-radius: 6px; font-weight: 700; display: inline-block; font-family: 'DM Sans', sans-serif;">Get Your Letter — $25 →</a>
</div>
"""

AI_SCAN_CTA_HTML = """
<div style="background: linear-gradient(145deg, #0f172a 0%, #1e3a8a 100%); border-radius: 12px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15); padding: 36px 24px; text-align: center; margin: 32px 0;">
<span style="display: inline-block; background: #d4af37; color: #0f172a; padding: 4px 12px; border-radius: 50px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 14px; font-family: 'DM Sans', sans-serif;">Free AI Tool</span>
<h3 style="margin: 0 0 10px; color: #ffffff; font-family: 'Lora', serif; font-size: 1.6rem;">Free ARD Rights Scan</h3>
<p style="font-size: 15px; color: #cbd5e1; margin: 0 0 22px; line-height: 1.55; font-family: 'Source Sans 3', sans-serif;">
    Wondering if the school violated your rights? Answer a few questions for an instant analysis based on Texas law.
  </p>
<a href="/tools/ard-rights-scan/index.html" style="display: block; background: #d4af37; color: #0f172a; padding: 14px 20px; border-radius: 8px; text-decoration: none; font-weight: 800; font-family: 'DM Sans', sans-serif; font-size: 15px; max-width: 280px; margin: 0 auto;">Run My Free ARD Scan →</a>
<p style="font-size: 11px; color: #64748b; margin: 12px 0 0; font-family: 'Source Sans 3', sans-serif;">🔒 Free &nbsp;·&nbsp; No account needed</p>
</div>
"""

def clean_and_format_css(soup):
    """Fixes the narrow column issue by forcing display block and clearing grid rules."""
    for style_tag in soup.find_all('style'):
        if not style_tag.string: continue
        content = style_tag.string
        # Replace grid layouts with centered block layout
        content = content.replace("display: grid;", "display: block !important;")
        content = content.replace("grid-template-columns: 1fr 380px;", "")
        content = content.replace("grid-template-columns: 1fr;", "")
        if ".layout-grid" in content:
            content = content.replace(".layout-grid {", ".layout-grid { max-width: 850px !important; margin: 40px auto !important; display: block !important; width: 100% !important;")
        style_tag.string = content
    
    # Remove older automated formatting patches that conflict with our clean layout
    for patch in soup.find_all('style', id=['fie-core-formatting', 'cro-core-formatting']):
        patch.decompose()

def remove_distractions(soup):
    """Removes sidebar, old bots, and duplicate sales offers."""
    # Remove Sidebar
    sidebar = soup.find('aside', class_='sidebar-column')
    if sidebar: sidebar.decompose()
    
    # Remove old inline bots/CTAs
    for div in soup.find_all('div', class_=['integrated-cta', 'mobile-only', 'inline-cta']):
        div.decompose()
        
    # Remove old bundle offers
    bundle_header = soup.find(lambda tag: tag.name == "h3" and "Complete Texas Special Ed Bundle" in tag.text)
    if bundle_header:
        bundle_parent = bundle_header.find_parent('div', style=lambda s: s and 'border: 2px solid' in s)
        if bundle_parent: bundle_parent.decompose()
    
    # Remove existing copies of these specific CTAs to prevent duplicates on rerun
    for card in soup.find_all('div', class_='sales-card'):
        if "Show the ISD" in card.get_text(): card.decompose()
    for ai in soup.find_all('div', style=lambda s: s and 'background: linear-gradient(145deg' in s):
        if "Free ARD Rights Scan" in ai.get_text(): ai.decompose()

def process_file(filepath, file_type):
    print(f"Processing {file_type}: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    clean_and_format_css(soup)
    remove_distractions(soup)

    article = soup.find('article', class_='content-column')
    if not article: return

    if file_type == "fie_guide":
        # Hierarchy: 1st H2 -> Letter CTA | Action Steps -> AI Scan
        intro_h2 = article.find('h2')
        if intro_h2: 
            intro_h2.insert_after(BeautifulSoup(LETTER_CTA_HTML, 'html.parser'))
        
        steps = article.find('div', class_='action-steps')
        if steps: 
            steps.insert_after(BeautifulSoup(AI_SCAN_CTA_HTML, 'html.parser'))
    
    elif file_type == "leadership":
        # Hierarchy: Add Letter CTA to the very bottom of the content
        article.append(BeautifulSoup(LETTER_CTA_HTML, 'html.parser'))

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"✅ Updated {filepath}")

def main():
    # Update all "What is an FIE" Pages
    # Targets files like what-is-an-fie-dallas-isd.html or what-is-an-fie-abilene-isd.html
    fie_files = glob.glob('districts/*/what-is-an-fie-*.html')
    for f in fie_files: process_file(f, "fie_guide")

    # Update all Leadership Directory Pages
    leadership_files = glob.glob('districts/*/leadership-directory.html')
    for f in leadership_files: process_file(f, "leadership")

if __name__ == "__main__":
    main()