import os
import glob
from bs4 import BeautifulSoup

CTA_HTML = """
<div class="cta-card" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);padding:36px;border-radius:12px;text-align:center;color:#fff;border:none;margin-top:40px;box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15);">
<h3 style="font-family:'Lora',serif;font-size:1.6rem;margin:0 0 12px;color:#fff;">Show the ISD You Mean Business</h3>
<p style="font-family:'Source Sans 3',sans-serif;font-size:16px;color:#cbd5e1;margin:0 auto 24px;line-height:1.6;max-width:90%;">A verbal request has no legal weight. A written letter starts the 45-day clock and forces a response within 15 school days.</p>
<a href="/resources/Iep-letter.html" style="display:inline-block;background:#d4af37;color:#0f172a;padding:16px 32px;border-radius:6px;text-decoration:none;font-weight:800;font-family:'DM Sans',sans-serif;font-size:16px;transition:background 0.2s;">Get Your Letter — $25 →</a>
</div>
"""

CLEAN_SCRIPT = """
document.addEventListener('DOMContentLoaded', function() {
    var toggle = document.querySelector('.mobile-menu-toggle');
    var menu   = document.querySelector('.nav-menu');
    if (toggle && menu) {
        toggle.addEventListener('click', function() {
            menu.classList.toggle('active');
            toggle.setAttribute('aria-expanded', menu.classList.contains('active'));
        });
    }
});
"""

def update_index_file(filepath):
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. Update CSS layout rules in <style> tags
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

    # 2. Remove the Spanish FIE card
    # Finds any anchor tag containing "como-solicitar" in its href link
    spanish_card = soup.find(lambda tag: tag.name == "a" and tag.has_attr('href') and "como-solicitar-una-evaluacion-fie" in tag['href'])
    if spanish_card:
        spanish_card.decompose()

    # 3. Remove Sidebar (This also removes the "Need Help Now" form inside it)
    sidebar = soup.find('aside', class_='sidebar-column')
    if sidebar:
        sidebar.decompose()

    # 4. Insert New CTA at the bottom of the content column
    article = soup.find('article', class_='content-column')
    if article:
        # Check if already inserted to prevent duplicates if script is run twice
        if "Show the ISD You Mean Business" not in article.text:
            cta_soup = BeautifulSoup(CTA_HTML, 'html.parser')
            article.append(cta_soup)

    # 5. Clean up the JavaScript (Remove form submission logic)
    for script_tag in soup.find_all('script'):
        if script_tag.string and 'leadForms' in script_tag.string and 'fetch' in script_tag.string:
            script_tag.string = CLEAN_SCRIPT

    # Save the modified HTML back to the file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"✅ Successfully updated {filepath}")


def main():
    # Use glob to find index.html specifically inside district subfolders
    # Example: districts/abilene-isd/index.html (ignores districts/index.html)
    search_pattern = 'districts/*/index.html'
    
    files_to_update = glob.glob(search_pattern, recursive=False)
    
    if not files_to_update:
        print(f"No files found matching pattern: {search_pattern}")
        return

    print(f"Found {len(files_to_update)} files to process.\n")
    
    for filepath in files_to_update:
        try:
            update_index_file(filepath)
        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")

if __name__ == "__main__":
    main()