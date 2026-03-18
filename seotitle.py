import os
import re
import markdown
from datetime import datetime

# ======================================================================
# CONFIGURATION & PATHS
# ======================================================================
MD_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\tefa_markdown_pages"
TEMPLATE_PATH = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\tefa\tefa-template.html"

OUT_DIR_EN = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\tefa\en"
OUT_DIR_ES = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\tefa\es"

# ======================================================================
# SEO URL SLUG MAPPING
# ======================================================================
SEO_FILENAMES = {
    # ENGLISH POSTS
    "EN-01": "texas-esa-tefa-complete-guide-2026.html",
    "EN-02": "texas-esa-30000-disability-iep-requirements.html",
    "EN-03": "texas-special-education-evaluation-45-day-timeline.html",
    "EN-04": "tefa-voucher-504-plan-vs-iep-texas.html",
    "EN-05": "ard-meeting-prep-guide-texas-tefa-voucher.html",
    "EN-06": "texas-esa-application-window-dates-2026.html",
    "EN-07": "adhd-texas-esa-disability-funding-guide.html",
    "EN-08": "what-texas-school-districts-wont-tell-you-esa.html",
    "EN-09": "tefa-approved-private-schools-texas-disability.html",
    "EN-10": "autism-texas-esa-voucher-30000-funding.html",
    
    # URGENCY / ADVOCACY POSTS
    "EN-11": "URGENT-tefa-deadline-extended-march-31-2026.html",
    "EN-12": "WARNING-texas-tefa-private-school-idea-rights-gotcha.html",

    # SPANISH POSTS
    "ES-01": "guia-completa-cuentas-ahorro-educativo-texas-2026.html",
    "ES-02": "como-obtener-30000-esa-texas-iep-espanol.html",
    "ES-03": "evaluacion-educacion-especial-texas-regla-45-dias.html",
    "ES-04": "tdah-texas-voucher-discapacidad-guia-familias.html",
    "ES-05": "preparacion-reunion-ard-texas-espanol.html",
    "ES-06": "fechas-limite-cuenta-ahorro-educativo-texas-2026.html",
    "ES-07": "autismo-texas-esa-voucher-familias-hispanas.html",
    "ES-08": "lo-que-distritos-escolares-texas-no-dicen-esa.html",
    "ES-09": "escuelas-privadas-aprobadas-tefa-texas-discapacidad.html",
    "ES-10": "recursos-espanol-educacion-especial-texas-2026.html",
    
    # URGENCY / ADVOCACY POSTS (SPANISH)
    "ES-11": "URGENTE-loteria-tefa-prioridad-ingresos-familias-latinas.html"
}

def extract_title(md_content):
    """Finds the first H1 (#) or H2 (##) in the markdown to use as the page title."""
    match = re.search(r'^(?:#|##)\s+(.+)', md_content, re.MULTILINE)
    if match:
        return match.group(1).replace('*', '').strip()
    return "Texas Special Education Guide"

def build_pages():
    os.makedirs(OUT_DIR_EN, exist_ok=True)
    os.makedirs(OUT_DIR_ES, exist_ok=True)

    try:
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as tf:
            base_template = tf.read()
    except FileNotFoundError:
        print(f"❌ Error: Could not find template at {TEMPLATE_PATH}")
        return

    md_files = [f for f in os.listdir(MD_DIR) if f.endswith(".md")]
    
    if not md_files:
        print(f"No Markdown files found in {MD_DIR}.")
        return

    current_date = datetime.now().strftime("%B %d, %Y")

    for filename in md_files:
        md_filepath = os.path.join(MD_DIR, filename)
        file_id = filename.replace(".md", "")
        
        with open(md_filepath, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Extract title before removing frontmatter
        page_title = extract_title(raw_content)

        # Remove the YAML frontmatter
        content_to_convert = re.sub(r'^---.*?---\n', '', raw_content, flags=re.DOTALL)
        html_content = markdown.markdown(content_to_convert, extensions=['extra'])

        # Start replacing template tags
        final_html = base_template.replace("{{POST_BODY_HTML}}", html_content)
        final_html = final_html.replace("{{H1_TITLE}}", page_title)
        final_html = final_html.replace("{{META_TITLE}}", f"{page_title} | TexasSpecialEd")
        
        # Generic fill-ins for standard tags
        final_html = final_html.replace("{{AUTHOR_NAME}}", "TexasSpecialEd Advocate")
        final_html = final_html.replace("{{DATE_PUBLISHED_DISPLAY}}", current_date)
        final_html = final_html.replace("{{DATE_MODIFIED_DISPLAY}}", current_date)
        final_html = final_html.replace("{{SITE_NAME}}", "TexasSpecialEd.com")
        final_html = final_html.replace("{{BREADCRUMB_HOME}}", "Home")

        # Handle Urgency Tags for the last 3 posts
        urgent_html = '<span class="post-tag post-tag--urgent">⚡ Time-Sensitive</span>'
        if file_id in ["EN-11", "EN-12", "ES-11"]:
            final_html = final_html.replace("{{POST_TAG_URGENT_HTML}}", urgent_html)
        else:
            final_html = final_html.replace("{{POST_TAG_URGENT_HTML}}", "")

        # Handle Spanish Tags
        espanol_html = '<span class="post-tag post-tag--espanol">En Español</span>'
        if file_id.startswith("ES"):
            final_html = final_html.replace("{{POST_TAG_ESPANOL_HTML}}", espanol_html)
            final_html = final_html.replace("{{PAGE_LANG}}", "es")
            final_html = final_html.replace("{{BREADCRUMB_SECTION_LABEL}}", "Recursos")
        else:
            final_html = final_html.replace("{{POST_TAG_ESPANOL_HTML}}", "")
            final_html = final_html.replace("{{PAGE_LANG}}", "en")
            final_html = final_html.replace("{{BREADCRUMB_SECTION_LABEL}}", "Guides")

        # Cleanup remaining un-filled bracket tags so they don't show on the live site
        final_html = re.sub(r'\{\{[A-Z0-9_]+\}\}', '', final_html)

        # Save the file
        seo_filename = SEO_FILENAMES.get(file_id, f"{file_id}.html")
        out_filepath = os.path.join(OUT_DIR_ES if file_id.startswith("ES") else OUT_DIR_EN, seo_filename)

        with open(out_filepath, "w", encoding="utf-8") as out_f:
            out_f.write(final_html)
            
        print(f"✅ Created: {seo_filename} (Urgent: {'Yes' if file_id in ['EN-11', 'EN-12', 'ES-11'] else 'No'})")

if __name__ == "__main__":
    build_pages()