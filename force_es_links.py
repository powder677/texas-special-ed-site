import os
from bs4 import BeautifulSoup

# Target the Spanish directory specifically
ES_DIR = os.path.join("blog", "es")

def force_absolute_es_links():
    if not os.path.exists(ES_DIR):
        print(f"Error: Directory not found: {ES_DIR}")
        return
        
    count = 0
    for filename in os.listdir(ES_DIR):
        if not filename.endswith(".html"):
            continue
            
        filepath = os.path.join(ES_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # 1. ENFORCE STRICT CANONICAL & HREFLANG URLS
        # This guarantees Google never loses the 'es' subfolder
        canonical = soup.find('link', rel='canonical')
        if canonical:
            canonical['href'] = f"https://www.texasspecialed.com/blog/es/{filename}"

        hreflang_es = soup.find('link', hreflang='es')
        if hreflang_es:
            hreflang_es['href'] = f"https://www.texasspecialed.com/blog/es/{filename}"

        # 2. ENFORCE STRICT ABSOLUTE PATHS ON ALL LINKS
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.text.strip()
            
            # A. Top Navigation Links (Force to Root)
            if href.endswith('index.html') and not 'blog' in href and not 'districts' in href and not 'resources' in href:
                a['href'] = '/index.html'
            elif 'districts/index.html' in href:
                a['href'] = '/districts/index.html'
            elif 'resources/index.html' in href:
                a['href'] = '/resources/index.html'
            
            # B. English Blog Hub Link
            elif 'blog/index.html' in href or (href.endswith('index.html') and 'English' in text):
                a['href'] = '/blog/index.html'
                
            # C. Read in English Toggle (Points up one folder to the English equivalent)
            elif 'English' in text and '../' in href:
                slug = href.split('/')[-1]
                a['href'] = f'/blog/{slug}'
                
            # D. Spanish Articles (Force /blog/es/ prefix back into the URL)
            elif href.endswith('.html') and 'index.html' not in href and 'districts' not in href:
                # Grab just the filename (e.g. 'que-es-fie.html') and force the full path
                slug = href.split('/')[-1] 
                a['href'] = f'/blog/es/{slug}'

        # Write the repaired HTML back to the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(soup.encode(formatter="html").decode('utf-8'))
            
        count += 1
        
    print(f"Success! Restored and locked absolute paths (/blog/es/...) across {count} Spanish files.")

if __name__ == "__main__":
    force_absolute_es_links()