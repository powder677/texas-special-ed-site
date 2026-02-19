import os
from bs4 import BeautifulSoup

def update_css(css_path):
    css_updates = """
/* =========================================
   LAYOUT & FORMATTING FIXES
   ========================================= */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #333333;
    background-color: #f8f9fa;
}

main {
    flex: 1;
}

.main-container, .container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
    background-color: #ffffff;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.05);
    border-radius: 8px;
    margin-top: 2rem;
    margin-bottom: 2rem;
}

.navbar {
    background-color: #ffffff;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 1000;
}

.site-footer {
    background-color: #222222;
    color: #ffffff;
    padding: 3rem 0;
    margin-top: auto;
}
"""
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Avoid duplicate appending if the script is run twice
        if "LAYOUT & FORMATTING FIXES" not in content:
            with open(css_path, 'a', encoding='utf-8') as f:
                f.write(css_updates)
            print(f"✅ Appended layout fixes to {css_path}")
    else:
        print(f"⚠️ Could not find {css_path}. Make sure the script is in the root directory.")

def fix_html_files(base_dir):
    updated_count = 0
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                soup = BeautifulSoup(html_content, 'html.parser')
                body = soup.find('body')
                
                if not body:
                    continue
                
                # Skip if the file has already been wrapped to prevent double-nesting
                if soup.find('main', class_='main-container'):
                    continue
                
                nav = soup.find('nav')
                footer = soup.find('footer')
                
                # Gather everything in the body that isn't the nav, footer, or backend scripts
                elements_to_wrap = []
                for child in body.find_all(recursive=False):
                    if child.name not in ['nav', 'footer', 'script', 'style', 'noscript']:
                        elements_to_wrap.append(child)
                
                if not elements_to_wrap:
                    continue

                # Create the <main> container and move the body content into it
                main_tag = soup.new_tag('main', attrs={'class': 'main-container'})
                for el in elements_to_wrap:
                    main_tag.append(el.extract())
                
                # Re-insert the main container perfectly between the nav and the footer
                if footer:
                    footer.insert_before(main_tag)
                elif nav:
                    nav.insert_after(main_tag)
                else:
                    body.insert(0, main_tag)
                
                # Ensure the nav and footer have the foundational CSS classes targeted above
                if nav and 'navbar' not in nav.get('class', []):
                    nav['class'] = nav.get('class', []) + ['navbar']
                if footer and 'site-footer' not in footer.get('class', []):
                    footer['class'] = footer.get('class', []) + ['site-footer']
                
                # Save the new structure
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                
                updated_count += 1
                if updated_count % 50 == 0:
                    print(f"Processed {updated_count} files...")

    print(f"✅ Finished! Successfully updated layout on {updated_count} HTML files.")

if __name__ == '__main__':
    print("Starting layout update...")
    update_css('style.css')
    fix_html_files('.')