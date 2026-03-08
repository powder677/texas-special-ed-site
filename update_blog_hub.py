import os
from bs4 import BeautifulSoup

# Path to your main blog index
BLOG_INDEX_PATH = os.path.join("blog", "index.html")

# The HTML block for the Spanish Section
SPANISH_SECTION_HTML = """
<section class="spanish-resources" style="margin: 40px 0; padding: 30px; background: #fdfbf7; border-radius: 12px; border-left: 5px solid #b8963a; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
    <h2 style="font-family: 'Cormorant Garamond', serif; font-size: 2.2rem; color: #1a1410; margin-bottom: 15px;">Recursos en Español</h2>
    <p style="font-family: 'DM Sans', sans-serif; font-size: 1.1rem; color: #4a4a4a; margin-bottom: 20px;">
        Guías, recursos e información para ayudar a las familias hispanohablantes a navegar la educación especial, evaluaciones FIE y reuniones ARD en Texas.
    </p>
    
    <ul style="list-style: none; padding: 0; margin-bottom: 25px; font-family: 'DM Sans', sans-serif;">
        <li style="margin-bottom: 12px;">📄 <a href="/blog/es/que-es-fie-texas.html" style="color: #b8963a; text-decoration: none; font-weight: 600; margin-left: 8px;">¿Qué es una evaluación FIE?</a></li>
        <li style="margin-bottom: 12px;">📄 <a href="/blog/es/como-solicitar-evaluacion-educacion-especial.html" style="color: #b8963a; text-decoration: none; font-weight: 600; margin-left: 8px;">Cómo solicitar una evaluación de educación especial</a></li>
        <li style="margin-bottom: 12px;">📄 <a href="/blog/es/escuela-nego-evaluacion.html" style="color: #b8963a; text-decoration: none; font-weight: 600; margin-left: 8px;">Qué hacer cuando la escuela niega una evaluación</a></li>
    </ul>
    
    <a href="/blog/es/index.html" class="btn" style="display: inline-block; padding: 12px 24px; background-color: #1a1410; color: #fff; text-decoration: none; font-family: 'DM Sans', sans-serif; font-weight: 600; border-radius: 4px; transition: background-color 0.3s ease;">
        Ver todos los artículos en español →
    </a>
</section>
"""

def inject_spanish_hub():
    if not os.path.exists(BLOG_INDEX_PATH):
        print(f"Error: Could not find {BLOG_INDEX_PATH}")
        return

    with open(BLOG_INDEX_PATH, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')

    # Check if we already injected it so we don't duplicate
    if soup.find('section', class_='spanish-resources'):
        print("Spanish section already exists in blog/index.html!")
        return

    spanish_soup = BeautifulSoup(SPANISH_SECTION_HTML, 'html.parser')

    # Try to find the best place to inject it. 
    # Usually right after the main H1 header/intro paragraph, or before the main article grid.
    main_header = soup.find('h1')
    
    if main_header:
        # Find the paragraph immediately following the H1 to put the section under the intro
        intro_p = main_header.find_next_sibling('p')
        if intro_p:
            intro_p.insert_after(spanish_soup)
        else:
            main_header.insert_after(spanish_soup)
        
        # Save the updated file
        with open(BLOG_INDEX_PATH, 'w', encoding='utf-8') as file:
            file.write(soup.encode(formatter="html").decode('utf-8'))
        print("Success! Injected Spanish Hub section into blog/index.html")
    else:
        print("Could not find the <h1> tag to anchor the Spanish section. Manual insertion required.")

if __name__ == "__main__":
    inject_spanish_hub()