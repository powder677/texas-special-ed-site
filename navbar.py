import os
from bs4 import BeautifulSoup

def update_navbar_button(directory):
    # The HTML for the new gold button with the updated link
    gold_button_html = """
    <li class="nav-item nav-cta" style="margin-left:8px;">
     <a href="/resources/Iep-letter" style="background:#d4af37;color:#0f172a;padding:10px 18px;border-radius:4px;font-weight:700;font-size:14px;text-decoration:none;font-family:'DM Sans',sans-serif;white-space:nowrap;">Get Your Letter — $25</a>
    </li>
    """
    
    modified_count = 0

    # os.walk searches the main folder and all subfolders
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find the navigation menu
                nav_menu = soup.find('ul', class_='nav-menu')
                
                if nav_menu:
                    changed = False
                    existing_gold_btn = None
                    
                    # Search the navbar to see if a gold button already exists
                    for a_tag in nav_menu.find_all('a'):
                        style = a_tag.get('style', '')
                        if '#d4af37' in style.lower():
                            existing_gold_btn = a_tag
                            break
                            
                    if existing_gold_btn:
                        # If it exists, just update the link to your new path
                        if existing_gold_btn.get('href') != '/resources/Iep-letter':
                            existing_gold_btn['href'] = '/resources/Iep-letter'
                            changed = True
                    else:
                        # If it doesn't exist, append the new button to the end of the menu
                        new_btn_soup = BeautifulSoup(gold_button_html, 'html.parser')
                        nav_menu.append(new_btn_soup)
                        changed = True
                        
                    # Save the file only if a change was made
                    if changed:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(str(soup))
                        print(f"✅ Updated navbar in: {filepath}")
                        modified_count += 1

    print(f"\n🎉 Done! Successfully updated the navbar gold button in {modified_count} pages.")

if __name__ == '__main__':
    # '.' means it runs on the current directory and all folders inside it
    update_navbar_button('.')