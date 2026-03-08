import os
from bs4 import BeautifulSoup

# Map your English slugs to your Spanish slugs
ARTICLE_MAP = {
    'what-is-fie': 'que-es-fie-texas',
    'how-to-request-evaluation': 'como-solicitar-evaluacion-educacion-especial',
    'what-to-do-when-school-denies-evaluation': 'escuela-nego-evaluacion'
    # Add more pairs here as you write them!
}

def inject_language_links(en_path, es_path, en_slug, es_slug):
    # Base URLs
    en_url = f"https://www.texasspecialed.com/blog/{en_slug}.html"
    es_url = f"https://www.texasspecialed.com/blog/es/{es_slug}.html"
    
    # 1. Process English File
    if os.path.exists(en_path):
        with open(en_path, 'r', encoding='utf-8') as f:
            en_soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Add hreflangs
        if not en_soup.head.find('link', hreflang='en'):
            en_soup.head.append(en_soup.new_tag('link', rel='alternate', hreflang='en', href=en_url))
        if not en_soup.head.find('link', hreflang='es'):
            en_soup.head.append(en_soup.new_tag('link', rel='alternate', hreflang='es', href=es_url))
            
        # Add visual UI toggle under H1
        h1 = en_soup.find('h1')
        if h1 and not en_soup.find('div', class_='language-toggle'):
            toggle_div = en_soup.new_tag('div', attrs={'class': 'language-toggle', 'style': 'margin-bottom: 20px; font-weight: bold;'})
            toggle_a = en_soup.new_tag('a', href=f"/blog/es/{es_slug}.html")
            toggle_a.string = "🇪🇸 Leer en Español"
            toggle_div.append(toggle_a)
            h1.insert_after(toggle_div)

        with open(en_path, 'w', encoding='utf-8') as f:
            f.write(en_soup.encode(formatter="html").decode('utf-8'))
            
    # 2. Process Spanish File
    if os.path.exists(es_path):
        with open(es_path, 'r', encoding='utf-8') as f:
            es_soup = BeautifulSoup(f.read(), 'html.parser')
            
        # Add hreflangs
        if not es_soup.head.find('link', hreflang='es'):
            es_soup.head.append(es_soup.new_tag('link', rel='alternate', hreflang='es', href=es_url))
        if not es_soup.head.find('link', hreflang='en'):
            es_soup.head.append(es_soup.new_tag('link', rel='alternate', hreflang='en', href=en_url))
            
        # Add visual UI toggle under H1
        h1 = es_soup.find('h1')
        if h1 and not es_soup.find('div', class_='language-toggle'):
            toggle_div = es_soup.new_tag('div', attrs={'class': 'language-toggle', 'style': 'margin-bottom: 20px; font-weight: bold;'})
            toggle_a = es_soup.new_tag('a', href=f"/blog/{en_slug}.html")
            toggle_a.string = "🇺🇸 Read in English"
            toggle_div.append(toggle_a)
            h1.insert_after(toggle_div)

        with open(es_path, 'w', encoding='utf-8') as f:
            f.write(es_soup.encode(formatter="html").decode('utf-8'))

def main():
    for en_slug, es_slug in ARTICLE_MAP.items():
        en_file = os.path.join("blog", f"{en_slug}.html")
        es_file = os.path.join("blog", "es", f"{es_slug}.html")
        
        print(f"Syncing pairs: {en_slug} <---> {es_slug}")
        inject_language_links(en_file, es_file, en_slug, es_slug)
        
    print("Language sync complete. Hreflang and Toggles injected.")

if __name__ == "__main__":
    main()