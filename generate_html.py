import os
import re
import markdown

# --- CONFIGURATION ---
TARGET_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\blog\es"

# --- HTML TEMPLATE ---
# This matches the exact shell of carta-evaluacion-educacion-especial-texas.html
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">

<head>
   <script async src="https://www.googletagmanager.com/gtag/js?id=G-GVLPE273XH"></script>
   <script>
      window.dataLayer = window.dataLayer || [];
      function gtag() { dataLayer.push(arguments); }
      gtag('js', new Date());
      gtag('config', 'G-GVLPE273XH');
   </script>
   <meta charset="utf-8" />
   <meta content="width=device-width, initial-scale=1.0" name="viewport" />
   <title>{title} | Texas Special Ed</title>
   <meta content="{description}" name="description" />
   <link href="https://www.texasspecialed.com/es/{slug}" rel="canonical" />
   <link rel="alternate" hreflang="es" href="https://www.texasspecialed.com/es/{slug}" />

   <link href="https://fonts.googleapis.com" rel="preconnect" />
   <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&family=Lora:wght@400;600;700&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet" />
   <link href="/style.css" rel="stylesheet" />
   <style>
      body { background: #f8fafc; }
      .es-hero { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 52px 24px 44px; text-align: center; position: relative; overflow: hidden; }
      .es-hero::before { content: ''; position: absolute; inset: 0; background: radial-gradient(ellipse at 60% 0%, rgba(212, 175, 55, 0.12) 0%, transparent 60%); pointer-events: none; }
      .es-badge { display: inline-block; background: rgba(212, 175, 55, 0.15); border: 1px solid rgba(212, 175, 55, 0.4); color: #d4af37; font-size: 11px; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; padding: 6px 16px; border-radius: 50px; margin-bottom: 18px; font-family: 'DM Sans', sans-serif; }
      .es-hero h1 { font-family: 'Lora', serif; font-size: clamp(1.7rem, 4vw, 2.4rem); color: #fff; line-height: 1.2; margin-bottom: 14px; max-width: 680px; margin-left: auto; margin-right: auto; }
      .es-hero h1 em { color: #d4af37; font-style: italic; }
      .es-hero p { color: #94a3b8; font-size: 1.05rem; max-width: 560px; margin: 0 auto 24px; line-height: 1.65; font-family: 'Source Sans 3', sans-serif; }
      .hero-trust { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; }
      .trust-item { display: flex; align-items: center; gap: 7px; color: #94a3b8; font-size: 13px; font-family: 'DM Sans', sans-serif; }
      .trust-dot { width: 7px; height: 7px; border-radius: 50%; background: #d4af37; flex-shrink: 0; }
      .page-container { max-width: 1100px; margin: 0 auto; padding: 0 20px; }
      .page-grid { display: grid; grid-template-columns: minmax(0, 1fr) 360px; gap: 40px; margin-top: 40px; margin-bottom: 80px; align-items: start; }
      @media (max-width: 960px) { .page-grid { grid-template-columns: 1fr; } .sidebar-col { order: -1; } }
      .main-col { display: flex; flex-direction: column; gap: 32px; min-width: 0; }
      
      /* Content card styling */
      .content-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 36px; font-family: 'Source Sans 3', sans-serif; font-size: 17px; line-height: 1.75; color: #1a1a2e; }
      .content-card h2 { font-family: 'Lora', serif; font-size: 1.5rem; color: #0a2342; margin: 2rem 0 1rem; padding-top: 1.5rem; border-top: 2px solid #e8f0fe; }
      .content-card h2:first-child { border-top: none; margin-top: 0; padding-top: 0; }
      .content-card h3 { font-family: 'Lora', serif; font-size: 1.25rem; color: #0a2342; margin: 1.5rem 0 0.5rem; }
      .content-card p { margin: 0 0 1.25rem; }
      .content-card ul, .content-card ol { margin: 0 0 1.25rem 1.5rem; padding: 0; }
      .content-card li { margin-bottom: 0.5rem; }
      
      /* Specialty elements styling */
      .quick-answer { background: #f0fdf4; border-left: 5px solid #16a34a; padding: 20px 24px; border-radius: 6px; margin-bottom: 28px; }
      .quick-answer .label { font-size: 0.75rem; text-transform: uppercase; color: #16a34a; font-weight: 800; margin-bottom: 8px; letter-spacing: 0.05em; font-family: 'DM Sans', sans-serif; }
      .quick-answer p { margin: 0; font-size: 1rem; line-height: 1.6; }
      .pull-quote { border-left: 4px solid #1a56db; margin: 1.5rem 0; padding: 16px 20px; background: #f8fbff; border-radius: 0 8px 8px 0; font-size: 1.1rem; font-style: italic; color: #1e3a8a; line-height: 1.6; }
      .warning-box { background: #fef2f2; border-left: 4px solid #ef4444; border-radius: 6px; padding: 16px 20px; margin: 1.5rem 0; font-size: 15px; color: #7f1d1d; line-height: 1.6; }
      
      /* FAQs */
      .faq-section { margin-top: 8px; }
      .faq-section details { border-bottom: 1px solid #e2e8f0; padding: 16px 0; }
      .faq-section summary { font-weight: 600; cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: center; font-family: 'Source Sans 3', sans-serif; font-size: 1.02rem; color: #0f172a; }
      .faq-section summary::-webkit-details-marker { display: none; }
      .faq-section details p { margin: 12px 0 0; color: #475569; line-height: 1.7; font-family: 'Source Sans 3', sans-serif; font-size: 15px; }

      /* Bot & Sidebar */
      .bot-wrap { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06); }
      .bot-header { background: linear-gradient(135deg, #0f172a, #1e3a8a); padding: 18px 24px; display: flex; align-items: center; gap: 12px; }
      .bot-badge { background: #d4af37; color: #0f172a; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; padding: 4px 12px; border-radius: 50px; font-family: 'DM Sans', sans-serif; }
      .bot-title { font-family: 'Lora', serif; font-weight: 600; color: #fff; margin: 0; font-size: 1.05rem; }
      .bot-wrap iframe { width: 100%; height: 820px; border: none; display: block; }
      
      .sidebar-col { position: sticky; top: 24px; display: flex; flex-direction: column; gap: 20px; }
      .sidebar-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 24px; }
      .sidebar-card h3 { font-family: 'Lora', serif; font-size: 1.1rem; color: #0a2342; margin: 0 0 16px; padding-bottom: 12px; border-bottom: 2px solid #e8f0fe; }
      .cta-card { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); border: none; text-align: center; }
      .cta-card h3 { color: #fff; border-bottom-color: rgba(255, 255, 255, 0.15); }
      .cta-card p { color: #94a3b8; font-family: 'Source Sans 3', sans-serif; font-size: 14px; line-height: 1.55; margin: 0 0 18px; }
      .btn-gold { display: block; background: #d4af37; color: #0f172a; padding: 14px; border-radius: 6px; text-decoration: none; font-weight: 800; font-family: 'DM Sans', sans-serif; font-size: 14px; transition: background 0.2s; text-align: center;}
      .btn-gold:hover { background: #b8963a; }
      .law-box { background: #f0f6ff; border: 1px solid #bfdbfe; border-left: 4px solid #1a56db; border-radius: 8px; padding: 20px; font-family: 'Source Sans 3', sans-serif; font-size: 14px; line-height: 1.65; color: #1e3a8a; }
      .law-box strong { display: block; margin-bottom: 6px; color: #0a2342; font-family: 'DM Sans', sans-serif; font-size: 15px; }
      .tl { list-style: none; padding: 0; margin: 0; border-left: 3px solid #1a56db; padding-left: 20px; display: flex; flex-direction: column; gap: 16px; }
      .tl li { position: relative; font-family: 'Source Sans 3', sans-serif; font-size: 14px; line-height: 1.55; color: #475569; }
      .tl li::before { content: ''; position: absolute; left: -27px; top: 4px; width: 12px; height: 12px; border-radius: 50%; background: #1a56db; border: 2px solid #fff; box-shadow: 0 0 0 2px #1a56db; }
      .tl li strong { display: block; color: #0f172a; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 3px; font-family: 'DM Sans', sans-serif; }
   </style>
</head>

<body>
   <header class="site-header">
      <nav aria-label="Main navigation" class="navbar" role="navigation">
         <div class="nav-container">
            <div class="nav-logo">
               <a aria-label="Texas Special Ed Home" class="text-logo" href="/">Texas <em>Special Ed</em></a>
            </div>
            <button aria-expanded="false" aria-label="Toggle menu" class="mobile-menu-toggle">
               <span class="hamburger"></span>
               <span class="hamburger"></span>
               <span class="hamburger"></span>
            </button>
            <ul class="nav-menu">
               <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
               <li class="nav-item dropdown">
                  <a aria-haspopup="true" class="nav-link dropdown-toggle" href="/districts/index.html">Districts <span class="dropdown-arrow">▼</span></a>
                  <ul class="dropdown-menu">
                     <li><a href="/districts/index.html"><strong>Directory: All Districts</strong></a></li>
                     <li class="dropdown-divider"></li>
                     <li><a href="/districts/houston-isd/index.html">Houston ISD</a></li>
                     <li><a href="/districts/dallas-isd/index.html">Dallas ISD</a></li>
                     <li><a href="/districts/frisco-isd/index.html">Frisco ISD</a></li>
                     <li><a href="/districts/katy-isd/index.html">Katy ISD</a></li>
                     <li class="dropdown-divider"></li>
                     <li><a class="view-all-link" href="/districts/index.html">Ver Todos los Distritos →</a></li>
                  </ul>
               </li>
               <li class="nav-item"><a class="nav-link" href="/resources/index.html">Recursos</a></li>
               <li class="nav-item"><a class="nav-link" href="/blog/index.html">Blog</a></li>
               <li class="nav-item nav-cta">
                  <a class="btn-outline" href="/resources/ard-checklist.pdf" target="_blank">Lista ARD Gratis</a>
               </li>
               <li class="nav-item nav-cta" style="margin-left:8px;">
                  <a href="/get-your-letter.html" style="background:#d4af37;color:#0f172a;padding:10px 18px;border-radius:4px;font-weight:700;font-size:14px;text-decoration:none;font-family:'DM Sans',sans-serif;white-space:nowrap;">Su Carta — $25</a>
               </li>
            </ul>
         </div>
      </nav>
   </header>

   <section class="es-hero">
      <div class="es-badge">Educación Especial · Texas · Para Padres</div>
      <h1>{title}</h1>
      <p>{description}</p>
      <div class="hero-trust">
         <span class="trust-item"><span class="trust-dot"></span>Cita la ley de Texas exactamente</span>
         <span class="trust-item"><span class="trust-dot"></span>Dirigida al Director y al Director de Ed. Especial</span>
         <span class="trust-item"><span class="trust-dot"></span>$25 · Entregada en 24 horas</span>
      </div>
   </section>

   <div class="page-container">
      <div class="page-grid">
         <div class="main-col">
            <div class="content-card">
               {content}
            </div>

            <div class="bot-wrap">
               <div class="bot-header">
                  <span class="bot-badge">Herramienta Gratis</span>
                  <h3 class="bot-title">Genere Su Carta de Evaluación FIE — $25</h3>
               </div>
               <iframe src="https://texas-fie-bot-831148457361.us-central1.run.app" title="Generador de Carta FIE Texas" allow="clipboard-write" loading="lazy">
               </iframe>
            </div>
         </div>

         <aside class="sidebar-col">
            <div class="sidebar-card cta-card">
               <h3>Muéstrele al Distrito que Va en Serio</h3>
               <p>Una solicitud verbal no tiene validez. Una carta escrita inicia el reloj de 45 días y obliga a una respuesta en 15 días escolares.</p>
               <a class="btn-gold" href="/get-your-letter.html">Obtener Su Carta — $25 →</a>
            </div>

            <div class="law-box">
               <strong>Base Legal</strong>
               Su solicitud se fundamenta en IDEA (20 U.S.C. § 1414), 19 TAC Capítulo 89 Subcapítulo AA, y el Código de Educación de Texas Capítulo 29. Bajo Child Find, su distrito debe identificar y evaluar a todos los niños con discapacidades sospechadas — sin importar su estatus en RTI.
            </div>

            <div class="sidebar-card">
               <h3>Cronograma Legal</h3>
               <ul class="tl">
                  <li>
                     <strong>Usted envía la carta</strong>
                     Al director del plantel Y al Director de Educación Especial. Este es el Día 0.
                  </li>
                  <li>
                     <strong>Dentro de 15 días escolares</strong>
                     El distrito debe responderle por escrito con un formulario de consentimiento o una negativa formal.
                  </li>
                  <li>
                     <strong>Usted firma el consentimiento</strong>
                     El reloj oficial de 45 días comienza en este momento.
                  </li>
                  <li>
                     <strong>Dentro de 45 días escolares</strong>
                     Evaluación completa entregada por escrito antes de cualquier reunión ARD.
                  </li>
                  <li>
                     <strong>Dentro de 30 días calendario</strong>
                     Reunión ARD para determinar elegibilidad y escribir el IEP si su hijo califica.
                  </li>
               </ul>
            </div>
         </aside>

      </div>
   </div>

   <footer class="site-footer">
      <div class="footer-container">
         <div class="footer-about">
            <img alt="Texas Special Ed Logo" height="auto" src="/images/texasspecialed-logo.png" width="160" />
            <p style="margin-top:.75rem;">Ayudando a padres de Texas a navegar el proceso de educación especial y ARD con confianza.</p>
         </div>
         <div class="footer-col">
            <h3>Enlaces Rápidos</h3>
            <ul>
               <li><a href="/">Inicio</a></li>
               <li><a href="/districts/index.html">Distritos</a></li>
               <li><a href="/resources/index.html">Recursos para Padres</a></li>
               <li><a href="/blog/index.html">Blog y Artículos</a></li>
               <li><a href="/about/index.html">Acerca de Nosotros</a></li>
            </ul>
         </div>
         <div class="footer-col">
            <h3>Recursos Gratis</h3>
            <ul>
               <li><a href="/resources/ard-checklist.pdf" target="_blank">Lista de Verificación ARD</a></li>
               <li><a href="/resources/evaluation-request-letter.pdf" target="_blank">Carta de Solicitud de Evaluación</a></li>
               <li><a href="/resources/parent-rights-guide.pdf" target="_blank">Guía de Derechos de Padres</a></li>
            </ul>
         </div>
         <div class="footer-col">
            <h3>English Version</h3>
            <ul>
               <li><a href="/blog/what-is-fie">What Is a FIE in Texas?</a></li>
               <li><a href="/blog/what-is-an-ard-meeting">What Is an ARD Meeting?</a></li>
               <li><a href="/get-your-letter.html">Get Your Letter</a></li>
            </ul>
         </div>
      </div>
      <div class="footer-bottom">
         <p>© 2026 Texas Special Education Resources. Todos los derechos reservados. No afiliado con TEA ni ningún distrito escolar. No es asesoría legal.</p>
      </div>
   </footer>

   <script>
      document.addEventListener('DOMContentLoaded', function() {
         var toggle = document.querySelector('.mobile-menu-toggle');
         var menu = document.querySelector('.nav-menu');
         if (toggle && menu) {
            toggle.addEventListener('click', function() {
               menu.classList.toggle('active');
               toggle.setAttribute('aria-expanded', menu.classList.contains('active'));
            });
         }
         const allDetails = document.querySelectorAll('details');
         allDetails.forEach(target => {
            target.addEventListener('click', () => {
               allDetails.forEach(d => {
                  if (d !== target) d.removeAttribute('open');
               });
            });
         });
      });
   </script>
</body>
</html>
"""

def format_faq_section(html_content):
    """
    Finds the 'Preguntas Frecuentes' section and converts the H3 tags into 
    interactive accordion <details><summary> tags, matching the reference HTML format.
    """
    # Regex to find the FAQ H2 header and everything after it
    match = re.search(r'(<h2>.*?Preguntas Frecuentes.*?</h2>)(.*)', html_content, flags=re.IGNORECASE | re.DOTALL)
    
    if not match:
        return html_content
    
    faq_header = match.group(1)
    faq_body = match.group(2)
    
    # Wrap the body in the faq-section div
    formatted_body = '<div class="faq-section">\n'
    
    # Split the faq body by <h3> tags
    qa_blocks = re.split(r'<h3>(.*?)</h3>', faq_body)
    
    # The first element is any text before the first <h3> (often empty)
    formatted_body += qa_blocks[0]
    
    # Process the Question/Answer pairs
    for i in range(1, len(qa_blocks), 2):
        question = qa_blocks[i]
        answer = qa_blocks[i+1] if i+1 < len(qa_blocks) else ""
        
        # Build the details/summary block perfectly matching your CSS
        details_block = f"""
        <details>
           <summary>{question} <span style="font-size:1.2rem;color:#64748b;">+</span></summary>
           {answer}
        </details>
        """
        formatted_body += details_block
        
    formatted_body += '\n</div>'
    
    # Put the document back together
    new_html = html_content[:match.start()] + faq_header + formatted_body
    return new_html

def process_markdown_files():
    if not os.path.exists(TARGET_DIR):
        print(f"Error: The directory {TARGET_DIR} does not exist.")
        return

    for filename in os.listdir(TARGET_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(TARGET_DIR, filename)
            base_slug = filename.replace('.md', '')
            output_filename = filename.replace('.md', '.html')
            
            with open(filepath, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # 1. Extract Title
            title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
            title = title_match.group(1) if title_match else "Evaluación de Educación Especial en Texas"
            md_content = re.sub(r'^#\s+(.+)$\n?', '', md_content, flags=re.MULTILINE, count=1)

            # 2. Extract Description (first paragraph)
            desc_match = re.search(r'^(?!#|\*|-|\s)(.+)$', md_content.strip(), re.MULTILINE)
            description = desc_match.group(1) if desc_match else "Guía completa para padres en Texas sobre la educación especial y el proceso de evaluación."
            if len(description) > 160:
                description = description[:157] + "..."

            # 3. Convert Markdown to HTML
            html_content = markdown.markdown(md_content)
            
            # 4. Process the FAQ Section into HTML Accordions
            html_content = format_faq_section(html_content)

            # 5. Inject into the Master Template
            final_html = HTML_TEMPLATE.replace("{title}", title)
            final_html = final_html.replace("{description}", description)
            final_html = final_html.replace("{slug}", base_slug)
            final_html = final_html.replace("{content}", html_content)

            # 6. Save
            output_filepath = os.path.join(TARGET_DIR, output_filename)
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(final_html)
            
            print(f"✅ Generated and formatted: {output_filename}")

if __name__ == "__main__":
    process_markdown_files()
    print("\n🎉 All files converted with perfect header, footer, sidebar, and FAQ formatting!")