import os
import json
from bs4 import BeautifulSoup

# The directory where your existing Spanish HTML files live
DIRECTORY = os.path.join("blog", "es")

def update_spanish_html_files():
    if not os.path.exists(DIRECTORY):
        print(f"Directory not found: {DIRECTORY}")
        return

    count = 0
    for filename in os.listdir(DIRECTORY):
        if filename.endswith(".html"):
            filepath = os.path.join(DIRECTORY, filename)
            slug = filename.replace('.html', '')
            
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # 1. Update the Bot Funnel Text (String replace to avoid changing your DOM structure)
            html_content = html_content.replace("Herramienta Gratis", "Generador de Carta FIE")
            html_content = html_content.replace("Genere Su Carta de Evaluación FIE — $25", "Carta Profesional — $25")

            # Parse the HTML to safely update the <head>
            soup = BeautifulSoup(html_content, 'html.parser')
            head = soup.head

            if not head:
                print(f"Skipping {filename}: No <head> tag found.")
                continue

            # Extract current Title and Description to use in Schema
            title_tag = head.find('title')
            title_text = title_tag.text if title_tag else "Educación Especial en Texas"
            
            desc_tag = head.find('meta', attrs={'name': 'description'})
            desc_text = desc_tag['content'] if desc_tag and 'content' in desc_tag.attrs else "Recursos de educación especial en Texas."

            # 2. Fix Canonical URL
            correct_url = f"https://www.texasspecialed.com/blog/es/{slug}.html"
            canonical = head.find('link', rel='canonical')
            if canonical:
                canonical['href'] = correct_url
            else:
                new_canonical = soup.new_tag('link', rel='canonical', href=correct_url)
                head.append(new_canonical)

            # 3. Fix Hreflang 'es' URL
            hreflang_es = head.find('link', rel='alternate', hreflang='es')
            if hreflang_es:
                hreflang_es['href'] = correct_url
            else:
                new_hreflang = soup.new_tag('link', rel='alternate', hreflang='es', href=correct_url)
                head.append(new_hreflang)

            # 4. Inject JSON-LD Article Schema (Check if it exists first to avoid duplicates)
            schema_exists = False
            for script in head.find_all('script', type='application/ld+json'):
                if '"@type": "Article"' in script.text or '"@type":"Article"' in script.text:
                    schema_exists = True
                    break

            if not schema_exists:
                schema_dict = {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    "headline": title_text,
                    "description": desc_text,
                    "inLanguage": "es",
                    "author": {
                        "@type": "Organization",
                        "name": "Texas Special Ed"
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": "Texas Special Ed"
                    }
                }
                schema_tag = soup.new_tag('script', type='application/ld+json')
                # Format nicely
                schema_tag.string = "\n" + json.dumps(schema_dict, indent=2, ensure_ascii=False) + "\n"
                head.append(schema_tag)

            # Write the updated HTML back to the file
            with open(filepath, 'w', encoding='utf-8') as f:
                # Use formatter='html' to prevent BeautifulSoup from altering standard HTML formatting
                f.write(soup.encode(formatter="html").decode('utf-8'))
            
            print(f"Updated SEO & Bot funnels for: {filename}")
            count += 1

    print(f"\nSuccess! Fixed {count} existing Spanish HTML articles.")

if __name__ == "__main__":
    update_spanish_html_files()