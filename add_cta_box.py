import os
from bs4 import BeautifulSoup

def add_cta_to_sidebar(directory):
    # The exact HTML snippet for your blue CTA box
    # (Note: I added margin-bottom: 24px so it doesn't touch the element below it)
    cta_html = """
    <div class="sidebar-card cta-card" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);padding:28px;border-radius:12px;text-align:center;color:#fff;border:none;margin-bottom:24px;">
     <h4 style="font-family:'Lora',serif;font-size:1.25rem;margin:0 0 10px;color:#fff;">Show the ISD<br/>You Mean Business</h4>
     <p style="font-family:'Source Sans 3',sans-serif;font-size:14px;color:#94a3b8;margin:0 0 18px;line-height:1.5;">A verbal request has no legal weight. A written letter starts the 45-day clock and forces a response within 15 school days.</p>
     <a href="/resources/Iep-letter.html" style="display:block;background:#d4af37;color:#0f172a;padding:14px;border-radius:6px;text-decoration:none;font-weight:800;font-family:'DM Sans',sans-serif;font-size:14px;transition:background 0.2s;">Get Your Letter — $25 →</a>
    </div>
    """

    modified_count = 0

    # os.walk will search your main folder AND all subfolders (like /districts/)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                # 1. Skip the partner page
                if "partner" in file.lower():
                    print(f"⏭️ Skipped (Partner Page): {file}")
                    continue
                    
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 2. Find the sidebar (checks for both sidebar-col and sidebar-column)
                sidebar = soup.find('aside', class_=lambda x: x and ('sidebar-col' in x or 'sidebar-column' in x))
                
                if sidebar:
                    # 3. Check if the CTA is already in this sidebar to avoid double-pasting
                    if "Show the ISD" not in str(sidebar):
                        cta_soup = BeautifulSoup(cta_html, 'html.parser')
                        
                        # Insert the CTA at the very top of the sidebar (index 0)
                        sidebar.insert(0, cta_soup)
                        
                        # Save the file
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(str(soup))
                            
                        print(f"✅ Added CTA to: {filepath}")
                        modified_count += 1

    print(f"\n🎉 Done! Successfully added the CTA box to {modified_count} pages.")

if __name__ == '__main__':
    # '.' means it will run on the current directory and all folders inside it
    add_cta_to_sidebar('.')