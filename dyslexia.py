import os
import shutil
from bs4 import BeautifulSoup

def process_html_file(filepath):
    print(f"Inspecting: {filepath}")
    
    # 1. Create a safe backup
    backup_path = filepath + ".bak"
    shutil.copy2(filepath, backup_path)
    print(f"Created backup at {backup_path}")

    with open(filepath, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # 2. Fix Heading Structure (Ensure only one H1)
    h1_tags = soup.find_all('h1')
    if len(h1_tags) > 1:
        print("Multiple H1s found. Converting subsequent H1s to H2s.")
        for i, h1 in enumerate(h1_tags):
            if i > 0:
                h1.name = 'h2'

    # 3. Break Long Paragraphs (> 120 words)
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        text = p.get_text()
        words = text.split()
        if len(words) > 120:
            print("Splitting long paragraph...")
            sentences = text.split('. ')
            midpoint = len(sentences) // 2
            
            part1_text = '. '.join(sentences[:midpoint]) + '.'
            part2_text = '. '.join(sentences[midpoint:])
            
            p.string = part1_text
            new_p = soup.new_tag('p')
            new_p.string = part2_text
            p.insert_after(new_p)

    # 4. Normalize Containers & Add Wrapper
    content_column = soup.find('article', class_='content-column')
    if content_column:
        # Check if already wrapped
        if not content_column.find('div', class_='content-container'):
            print("Wrapping content in .content-container...")
            wrapper = soup.new_tag('div', attrs={'class': 'content-container'})
            
            # Move children into wrapper
            for child in list(content_column.children):
                wrapper.append(child.extract())
            
            content_column.append(wrapper)

    # 5. Remove conflicting / duplicate embedded CSS & Fix Nav Menu
    cro_style = soup.find('style', id='cro-core-formatting')
    if cro_style:
        cro_style.decompose() # Removes the block hiding the mobile menu
        print("Removed conflicting CRO styling block.")

    # 6. Inject Global Mobile & Layout Fixes
    global_fixes = """
    /* --- MOBILE USABILITY & LAYOUT FIXES --- */
    img { max-width: 100%; height: auto; }
    table { display: block; overflow-x: auto; white-space: nowrap; }
    .content-container { max-width: 700px; margin: 0 auto; }
    
    /* Fix Mobile Menu Visibility */
    .nav-menu { display: flex; }
    @media (max-width: 950px) {
        .nav-menu { display: none; flex-direction: column; width: 100%; }
        .nav-menu.active { display: flex !important; }
        .layout-grid { gap: 20px !important; margin-top: 20px; }
        .content-column { padding: 20px !important; }
        .quick-answer, .inline-cta, .sales-card { padding: 15px !important; }
        h1 { font-size: 1.8rem; }
    }
    """
    
    head = soup.find('head')
    if head:
        new_style = soup.new_tag('style', id="mobile-usability-fixes")
        new_style.string = global_fixes
        head.append(new_style)
        print("Injected mobile formatting constraints.")

    # 7. Clean up bloated inline styles that break mobile
    for el in soup.find_all(style=True):
        style_str = el['style'].lower()
        if 'padding: 24px' in style_str or 'padding:24px' in style_str or 'padding: 28px' in style_str:
            # We strip aggressive inline padding so our CSS media queries can take over
            del el['style']

    # 8. Save the corrected file
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(str(soup))
    
    print(f"Successfully repaired: {filepath}\n")

if __name__ == "__main__":
    # Define the target file
    target_file = "dyslexia-services.html"
    
    if os.path.exists(target_file):
        process_html_file(target_file)
    else:
        print(f"Error: {target_file} not found in the current directory.")