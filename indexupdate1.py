import os
import glob
from bs4 import BeautifulSoup

# HTML Templates for re-insertion
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

def update_evaluation_file(filepath):
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. Clean up CSS - Remove competing grid rules and force single column
    for style_tag in soup.find_all('style'):
        if not style_tag.string:
            continue
        
        content = style_tag.string
        # Replace the 70/30 split and the fie-core-formatting grid
        content = content.replace("display: grid;", "display: block;")
        content = content.replace("grid-template-columns: 1fr 380px;", "")
        content = content.replace("grid-template-columns: 1fr;", "")
        
        # Ensure .layout-grid is clean and wide
        if ".layout-grid" in content:
            content = content.replace(".layout-grid {", ".layout-grid { max-width: 850px !important; margin: 40px auto !important; display: block !important; width: 100% !important;")
        
        style_tag.string = content

    # 2. Remove Sidebar
    sidebar = soup.find('aside', class_='sidebar-column')
    if sidebar:
        sidebar.decompose()

    # 3. Clean up existing CTAs/Bots to prevent duplicates
    for div in soup.find_all('div', class_=['integrated-cta', 'mobile-only', 'inline-cta']):
        div.decompose()
        
    for card in soup.find_all('div', class_='sales-card'):
        if "Show the ISD You Mean Business" in card.get_text():
            card.decompose()

    for div in soup.find_all('div', style=lambda s: s and 'background: linear-gradient(145deg' in s):
        if "Free ARD Rights Scan" in div.get_text():
            div.decompose()

    # 4. Handle Bundle/Old Formats
    bundle_header = soup.find(lambda tag: tag.name == "h3" and "Complete Texas Special Ed Bundle" in tag.text)
    if bundle_header:
        bundle_parent = bundle_header.find_parent('div', style=lambda s: s and 'border: 2px solid' in s)
        if bundle_parent:
            bundle_parent.decompose()

    # 5. Re-insert Integrated CTAs in correct hierarchy
    intro_h2 = soup.find(lambda tag: tag.name == "h2" and "Requesting a Special Education Evaluation" in tag.text)
    action_steps = soup.find('div', class_='action-steps')
    
    if intro_h2:
        # Hierarchy: Letter CTA at the Top
        letter_soup = BeautifulSoup(LETTER_CTA_HTML, 'html.parser')
        intro_h2.insert_after(letter_soup)

    if action_steps:
        # Hierarchy: AI Scan under "How to Submit"
        ai_soup = BeautifulSoup(AI_SCAN_CTA_HTML, 'html.parser')
        action_steps.insert_after(ai_soup)

    # 6. Final check on styles - Ensure no lingering sidebar css hidden in the second style block
    for style_tag in soup.find_all('style', id='fie-core-formatting'):
        style_tag.decompose() # Remove the automated patch as it often conflicts with our clean layout

    # Save
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"✅ Successfully updated {filepath}")

def main():
    search_pattern = 'districts/*/evaluation-child-find.html'
    files = glob.glob(search_pattern)
    
    if not files:
        print("No evaluation guide files found.")
        return

    print(f"Found {len(files)} files to update.")
    for f in files:
        try:
            update_evaluation_file(f)
        except Exception as e:
            print(f"Error on {f}: {e}")

if __name__ == "__main__":
    main()