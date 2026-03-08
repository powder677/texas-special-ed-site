import os
import random
from bs4 import BeautifulSoup

ES_DIR = os.path.join("blog", "es")

def fix_paths_and_interlink():
    if not os.path.exists(ES_DIR):
        print(f"Error: Directory not found: {ES_DIR}")
        return
        
    # 1. Gather all Spanish articles and extract their exact titles
    articles = []
    for filename in os.listdir(ES_DIR):
        if filename.endswith(".html") and filename != "index.html":
            filepath = os.path.join(ES_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                # Try to grab the real H1 title of the page
                h1 = soup.find('h1')
                title = h1.text.strip() if h1 else filename.replace('.html', '').replace('-', ' ').title()
                articles.append({'filename': filename, 'title': title})

    print(f"Found {len(articles)} Spanish articles. Fixing links and cross-linking...")

    # 2. Process all HTML files in blog/es/ (including the index.html hub)
    for filename in os.listdir(ES_DIR):
        if not filename.endswith(".html"):
            continue
            
        filepath = os.path.join(ES_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # --- A. Fix Absolute Paths to Relative Paths (Fixes the local broken links) ---
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('/blog/es/'):
                a_tag['href'] = href.replace('/blog/es/', './')
            elif href == '/blog/index.html':
                a_tag['href'] = '../index.html'
            elif href == '/districts/index.html':
                a_tag['href'] = '../../districts/index.html'
            elif href == '/resources/index.html':
                a_tag['href'] = '../../resources/index.html'
            elif href == '/index.html':
                a_tag['href'] = '../../index.html'

        # --- B. Inject "Related Articles" (Only for actual articles, skipping the hub index) ---
        if filename != "index.html" and len(articles) >= 3:
            # Remove the related block if it already exists (prevents duplicates if run twice)
            old_related = soup.find('div', class_='related-articles')
            if old_related:
                old_related.decompose()

            # Pick 3 other articles that are NOT the current article
            other_articles = [a for a in articles if a['filename'] != filename]
            
            # Use the filename as a random seed so the 3 links stay consistent on page reloads
            random.seed(filename) 
            selected = random.sample(other_articles, min(3, len(other_articles)))

            # Build the internal linking HTML block
            related_html = f"""
            <div class="related-articles" style="margin-top: 50px; margin-bottom: 40px; padding: 25px; background-color: #fdfbf7; border-radius: 8px; border-top: 4px solid #b8963a; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                <h3 style="font-family: 'Cormorant Garamond', serif; font-size: 1.8rem; color: #1a1410; margin-top: 0; margin-bottom: 15px;">Otros Artículos Recomendados</h3>
                <ul style="list-style: none; padding: 0; margin: 0; font-family: 'DM Sans', sans-serif;">
                    <li style="margin-bottom: 12px;">📄 <a href="./{selected[0]['filename']}" style="color: #b8963a; font-weight: 600; text-decoration: none; font-size: 1.1rem; margin-left: 8px;">{selected[0]['title']}</a></li>
                    <li style="margin-bottom: 12px;">📄 <a href="./{selected[1]['filename']}" style="color: #b8963a; font-weight: 600; text-decoration: none; font-size: 1.1rem; margin-left: 8px;">{selected[1]['title']}</a></li>
                    <li style="margin-bottom: 12px;">📄 <a href="./{selected[2]['filename']}" style="color: #b8963a; font-weight: 600; text-decoration: none; font-size: 1.1rem; margin-left: 8px;">{selected[2]['title']}</a></li>
                </ul>
            </div>
            """
            related_soup = BeautifulSoup(related_html, 'html.parser')
            
            # Insert the related links right before the bot generator tool
            article_tag = soup.find('article', class_='content')
            if article_tag:
                bot_embed = article_tag.find('div', class_='bot-embed')
                if bot_embed:
                    bot_embed.insert_before(related_soup)
                else:
                    article_tag.append(related_soup)

        # Write the fixed HTML back to the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(soup.encode(formatter="html").decode('utf-8'))

    print("Done! All links are fixed and articles are now cross-linked.")

if __name__ == "__main__":
    fix_paths_and_interlink()