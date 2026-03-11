import os
import glob
from bs4 import BeautifulSoup

# Define the HTML snippets for the integrated cards
LETTER_CTA_HTML = """
<div class="sales-card" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%); margin: 32px 0;">
<h3 style="margin-top:0; color:#fff;">Show the ISD You Mean Business</h3>
<p style="font-size:15px; color:#cbd5e1; margin-bottom: 24px;">A verbal request has no legal weight. A written letter starts the 45-day clock and forces a response within 15 school days.</p>
<a href="/resources/Iep-letter.html" style="background:#d4af37; color:#0f172a; padding: 16px 32px; text-decoration: none; border-radius: 6px; font-weight: 700; display: inline-block;">Get Your Letter — $25 →</a>
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

def update_dispute_file(filepath):
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. Update CSS for single column
    for style_tag in soup.find_all('style'):
        if style_tag.string:
            style_tag.string = style_tag.string.replace(
                ".layout-grid { display: grid; grid-template-columns: 1fr; gap: 50px; margin-top: 40px; align-items: start; }",
                ".layout-grid { max-width: 850px; margin: 40px auto; display: block; }"
            ).replace(
                "@media (min-width: 1024px) { .layout-grid { grid-template-columns: 1fr 380px; } }",
                ""
            ).replace(
                ".sidebar-column { position: sticky; top: 100px; z-index: 10; } /* Clears tight navbar */",
                ""
            )

    # 2. Remove Sidebar
    sidebar = soup.find('aside', class_='sidebar-column')
    if sidebar:
        sidebar.decompose()

    # 3. Remove Attorney CTA ("Facing an MDR or Expulsion Hearing?")
    attorney_cta = soup.find(lambda tag: tag.name == "h3" and "Facing an MDR" in tag.text)
    if attorney_cta and attorney_cta.find_parent('div', class_='inline-cta'):
        attorney_cta.find_parent('div', class_='inline-cta').decompose()

    # 4. Remove Bundle Offer and clean up offers-container
    bundle_header = soup.find(lambda tag: tag.name == "h3" and "Complete Texas Special Ed Bundle" in tag.text)
    if bundle_header:
        # If it's the old version with the big manual div
        bundle_parent = bundle_header.find_parent('div', style=lambda s: s and 'border: 2px solid' in s)
        if bundle_parent:
            bundle_parent.decompose()
            
    # Remove the generic bundle card if it exists in the 70/30 version
    bundle_generic = soup.find(lambda tag: tag.name == "h3" and "Parent Protection" in tag.text)
    if bundle_generic and bundle_generic.find_parent('div', class_='sales-card'):
        bundle_generic.find_parent('div', class_='sales-card').decompose()

    # 5. Insert New Integrated CTAs
    
    # Insert Letter card after the first pull-quote (regarding 10th day)
    pull_quote = soup.find('div', class_='pull-quote')
    if pull_quote:
        if "Show the ISD You Mean Business" not in soup.get_text():
            letter_soup = BeautifulSoup(LETTER_CTA_HTML, 'html.parser')
            pull_quote.insert_after(letter_soup)

    # Insert AI Scan after the Action Steps (How to file Level 1)
    action_steps = soup.find('div', class_='action-steps')
    if action_steps:
        if "Free ARD Rights Scan" not in soup.get_text():
            ai_soup = BeautifulSoup(AI_SCAN_CTA_HTML, 'html.parser')
            action_steps.insert_after(ai_soup)

    # Save changes
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"✅ Updated {filepath}")

def main():
    search_pattern = 'districts/*/grievance-dispute-resolution.html'
    files = glob.glob(search_pattern)
    
    if not files:
        print("No dispute resolution files found.")
        return

    print(f"Found {len(files)} files to update.")
    for f in files:
        try:
            update_dispute_file(f)
        except Exception as e:
            print(f"Error on {f}: {e}")

if __name__ == "__main__":
    main()