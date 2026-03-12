import os
from bs4 import BeautifulSoup
from pathlib import Path

def main():
    # Define your base directory
    base_dir = Path(r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts")

    # The New Banner CTA HTML
    banner_html = """
    <div class="premium-banner-cta" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);padding:30px;border-radius:12px;text-align:center;color:#fff;margin: 0 auto 40px;max-width:800px;box-shadow:0 10px 25px -5px rgba(0,0,0,0.15);">
       <span style="background:#d4af37;color:#0f172a;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;padding:6px 14px;border-radius:50px;display:inline-block;margin-bottom:15px;font-family:'DM Sans',sans-serif;">Generador de Carta FIE</span>
       <h2 style="font-family:'Lora',serif;font-size:1.8rem;color:#fff;margin:0 0 12px;border:none;padding:0;">Redacta Tu Solicitud Oficial con Validez Legal</h2>
       <p style="font-family:'Source Sans 3',sans-serif;font-size:16px;color:#cbd5e1;margin:0 auto 24px;max-width:600px;">Una solicitud verbal no inicia el reloj de 45 días. Usa nuestra herramienta para generar una carta que obliga al distrito a responder en 15 días.</p>
       <a href="/resources/iep-letter-spanish/" style="background:#d4af37;color:#0f172a;padding:16px 32px;border-radius:6px;text-decoration:none;font-weight:800;font-family:'DM Sans',sans-serif;font-size:16px;transition:0.2s;display:inline-block;">Obtener Mi Carta — $25 →</a>
    </div>
    """

    # The Complete Spanish Blog List HTML
    blog_list_html = """
    <div class="related-blogs-box" style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #1a56db; border-radius: 8px; padding: 24px 28px; margin: 3rem auto; max-width: 800px;">
       <h3 style="font-family: 'Lora', serif; font-size: 1.4rem; color: #0a2342; margin: 0 0 16px;">📚 Recursos Adicionales en Español</h3>
       <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 12px;">
          <li><a href="/blog/es/que-es-fie-texas.html" style="color:#1d4ed8;text-decoration:none;font-weight:600;font-family:'DM Sans',sans-serif;">→ ¿Qué es una Evaluación FIE en Texas? Guía Completa</a></li>
          <li><a href="/blog/es/tiempo-evaluacion-fie-texas.html" style="color:#1d4ed8;text-decoration:none;font-weight:600;font-family:'DM Sans',sans-serif;">→ Tiempos y Plazos de la Evaluación FIE en Texas</a></li>
          <li><a href="/blog/es/carta-evaluacion-educacion-especial-texas.html" style="color:#1d4ed8;text-decoration:none;font-weight:600;font-family:'DM Sans',sans-serif;">→ Ejemplo de Carta para Solicitar Evaluación en Texas</a></li>
          <li><a href="/blog/es/como-solicitar-evaluacion-educacion-especial.html" style="color:#1d4ed8;text-decoration:none;font-weight:600;font-family:'DM Sans',sans-serif;">→ Cómo solicitar una evaluación de educación especial paso a paso</a></li>
          <li><a href="/blog/es/escuela-nego-evaluacion.html" style="color:#1d4ed8;text-decoration:none;font-weight:600;font-family:'DM Sans',sans-serif;">→ Qué hacer si la escuela se niega a evaluar a tu hijo</a></li>
          <li><a href="/blog/es/la-escuela-dice-esperar-rti.html" style="color:#1d4ed8;text-decoration:none;font-weight:600;font-family:'DM Sans',sans-serif;">→ Qué hacer si la escuela dice que debes esperar por RTI</a></li>
          <li><a href="/blog/es/mi-hijo-no-aprende-a-leer.html" style="color:#1d4ed8;text-decoration:none;font-weight:600;font-family:'DM Sans',sans-serif;">→ Mi hijo no aprende a leer: ¿Cómo puede ayudar la escuela?</a></li>
          <li><a href="/blog/es/mi-hijo-no-se-concentra-en-clase.html" style="color:#1d4ed8;text-decoration:none;font-weight:600;font-family:'DM Sans',sans-serif;">→ Mi hijo no se concentra en clase: TDAH y Evaluaciones FIE</a></li>
          <li><a href="/blog/es/maestro-dice-mi-hijo-no-se-esfuerza.html" style="color:#1d4ed8;text-decoration:none;font-weight:600;font-family:'DM Sans',sans-serif;">→ El maestro dice que mi hijo "no se esfuerza": ¿Qué significa?</a></li>
          <li><a href="/blog/es/mi-hijo-esta-atrasado-en-la-escuela.html" style="color:#1d4ed8;text-decoration:none;font-weight:600;font-family:'DM Sans',sans-serif;">→ Mi hijo está atrasado en la escuela: Primeros pasos</a></li>
       </ul>
    </div>
    """

    files_formatted = 0

    print("Scanning directories and updating HTML files...\n")

    # Loop through every folder in the districts directory
    for district_folder in base_dir.iterdir():
        if district_folder.is_dir():
            
            # Loop through every HTML file in the folder
            for file_path in district_folder.glob("*.html"):
                if file_path.name == "index.html":
                    continue # Skip the index page
                
                with open(file_path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f, "html.parser")
                
                # 1. Remove the old bot iframe wrap if it exists
                bot_wrap = soup.find("div", class_="bot-wrap")
                if bot_wrap:
                    bot_wrap.decompose()
                    
                # 2. Prevent duplicate insertions if you run the script twice
                existing_banner = soup.find("div", class_="premium-banner-cta")
                if existing_banner:
                    existing_banner.decompose()
                existing_blogs = soup.find("div", class_="related-blogs-box")
                if existing_blogs:
                    existing_blogs.decompose()
                
                # 3. Find the main content area with multiple fallback options
                content_area = soup.find("article") or soup.find("div", class_="content-wrapper") or soup.find("main") or soup.find("body")
                
                # If no container is found, use the whole file (soup root) as the content area
                if not content_area:
                    content_area = soup
                
                # Insert the banner at the very top of the content area
                banner_soup = BeautifulSoup(banner_html, "html.parser")
                content_area.insert(0, banner_soup)
                
                # Append the blog list to the very bottom of the content area
                blogs_soup = BeautifulSoup(blog_list_html, "html.parser")
                content_area.append(blogs_soup)
                
                # Save the formatted HTML back to the file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(str(soup))
                
                print(f"✅ Formatted: {district_folder.name} / {file_path.name}")
                files_formatted += 1

    print(f"\nSuccess! Formatted {files_formatted} pages.")

if __name__ == "__main__":
    main()