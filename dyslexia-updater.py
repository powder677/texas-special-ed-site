import os
import glob
from bs4 import BeautifulSoup

# Define the HTML snippets for the new inserted cards
LETTER_CTA_HTML = """
<div class="cta-card" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);padding:36px;border-radius:12px;text-align:center;color:#fff;border:none;margin:32px 0;box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15);">
<h3 style="font-family:'Lora',serif;font-size:1.6rem;margin:0 0 12px;color:#fff;">Show the ISD You Mean Business</h3>
<p style="font-family:'Source Sans 3',sans-serif;font-size:16px;color:#cbd5e1;margin:0 auto 24px;line-height:1.6;max-width:90%;">A verbal request has no legal weight. A written letter starts the 45-day clock and forces a response within 15 school days.</p>
<a href="/resources/Iep-letter.html" style="display:inline-block;background:#d4af37;color:#0f172a;padding:16px 32px;border-radius:6px;text-decoration:none;font-weight:800;font-family:'DM Sans',sans-serif;font-size:16px;transition:background 0.2s;">Get Your Letter — $25 →</a>
</div>
"""

AI_SCAN_CTA_HTML = """
<div style="background: linear-gradient(145deg, #0f172a 0%, #1e3a8a 100%); border-radius: 12px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15); padding: 36px 24px; text-align: center; margin: 32px 0;">
<span style="display: inline-block; background: #d4af37; color: #0f172a; padding: 6px 16px; border-radius: 50px; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 16px; font-family: 'DM Sans', sans-serif;">Free AI Tool</span>
<h3 style="margin: 0 0 12px; color: #ffffff; font-family: 'Lora', serif; font-size: 1.6rem; line-height: 1.3;">Free ARD Rights Scan</h3>
<p style="font-size: 16px; color: #cbd5e1; margin: 0 auto 24px; line-height: 1.6; font-family: 'Source Sans 3', sans-serif; max-width: 90%;">Wondering if the school violated your rights? Answer a few questions for an instant analysis based on Texas law.</p>
<a href="/tools/ard-rights-scan/index.html" style="display: inline-block; background: #d4af37; color: #0f172a; padding: 16px 32px; border-radius: 8px; text-decoration: none; font-weight: 800; font-family: 'DM Sans', sans-serif; font-size: 16px; transition: transform 0.2s, box-shadow 0.2s;">Run My Free ARD Scan →</a>
<p style="font-size: 13px; color: #94a3b8; margin: 16px 0 0; font-family: 'Source Sans 3', sans-serif;">🔒 Free &nbsp;·&nbsp; No account needed</p>
</div>
"""

def update_html_file(filepath):
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. Update CSS layout rules in <style> tags
    for style_tag in soup.find_all('style'):
        if style_tag.string:
            # Replace old grid layout with new single column layout
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

    # 3. Remove old CTAs
    # "Is the school's reading intervention failing?"
    old_cta_1 = soup.find(lambda tag: tag.name == "h3" and "Is the school's reading intervention failing?" in tag.text)
    if old_cta_1 and old_cta_1.find_parent('div', class_='inline-cta'):
        old_cta_1.find_parent('div', class_='inline-cta').decompose()

    # "Tired of the Wait and See approach?"
    old_cta_2 = soup.find(lambda tag: tag.name == "h3" and "Tired of the \"Wait and See\" approach?" in tag.text)
    if old_cta_2 and old_cta_2.find_parent('div', class_='inline-cta'):
        old_cta_2.find_parent('div', class_='inline-cta').decompose()

    # "Complete Texas Special Ed Bundle"
    bundle_cta = soup.find(lambda tag: tag.name == "h3" and "Complete Texas Special Ed Bundle" in tag.text)
    if bundle_cta and bundle_cta.parent:
        bundle_cta.parent.decompose()

    # 4. Insert New CTAs
    
    # Insert Letter CTA after the mandatory screening paragraph
    # Target: The paragraph ending with "request help."
    screening_p = soup.find(lambda tag: tag.name == "p" and "wait for a screener to flag your child" in tag.text)
    if screening_p:
        # Check if already inserted to prevent duplicates on multiple runs
        next_sibling = screening_p.find_next_sibling('div')
        if not next_sibling or "Show the ISD You Mean Business" not in next_sibling.text:
            letter_soup = BeautifulSoup(LETTER_CTA_HTML, 'html.parser')
            screening_p.insert_after(letter_soup)

    # Insert AI Scan CTA after the IEP list
    iep_list = soup.find('ul', class_='iep-list')
    if iep_list:
        next_sibling = iep_list.find_next_sibling('div')
        if not next_sibling or "Free ARD Rights Scan" not in next_sibling.text:
            ai_soup = BeautifulSoup(AI_SCAN_CTA_HTML, 'html.parser')
            iep_list.insert_after(ai_soup)

    # Save the modified HTML back to the file
    # Using str(soup) instead of prettify() to preserve existing inline whitespace formatting
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"Successfully updated {filepath}")


def main():
    # Define the pattern to find all your dyslexia pages
    # Change this pattern if your folder structure is different
    # E.g., '**/*dyslexia-services.html' to search recursively
    search_pattern = 'districts/*/dyslexia-services.html'
    
    # Use glob to find all matching files recursively
    files_to_update = glob.glob(search_pattern, recursive=True)
    
    if not files_to_update:
        print(f"No files found matching pattern: {search_pattern}")
        print("Please ensure you are running this script from the root folder of your project.")
        return

    print(f"Found {len(files_to_update)} files to process.")
    
    for filepath in files_to_update:
        try:
            update_html_file(filepath)
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    main()