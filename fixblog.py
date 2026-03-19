import os
import re

# ======================================================================
# CONFIGURATION
# ======================================================================
TEMPLATE_PATH = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\tefa\index.html"
OUT_DIR_EN = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\tefa\en"
OUT_DIR_ES = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\tefa\es"

# ======================================================================
# URL SLUGS
# ======================================================================
# This ensures the links correctly point to the subfolders
BASE_SLUG_EN = "/tefa/en/"
BASE_SLUG_ES = "/tefa/es/"

# ======================================================================
# ARTICLE DATA
# ======================================================================
EN_ARTICLES = [
    {"file": "URGENT-tefa-deadline-extended-march-31-2026.html", "title": "Missed the TEFA Deadline? Here's What Families Need to Know", "tag": "⚡ Breaking News", "urgent": True},
    {"file": "WARNING-texas-tefa-private-school-idea-rights-gotcha.html", "title": "The Private School 'Gotcha': TEFA Funding vs. IDEA Rights", "tag": "⚠️ Warning", "urgent": True},
    {"file": "texas-esa-tefa-complete-guide-2026.html", "title": "Texas Education Savings Accounts 2026: Complete Guide", "tag": "Master Guide", "urgent": False},
    {"file": "texas-esa-30000-disability-iep-requirements.html", "title": "How to Get the $30,000 ESA: The IEP Is the Key", "tag": "IEP Strategy", "urgent": False},
    {"file": "texas-special-education-evaluation-45-day-timeline.html", "title": "The 45-Day Rule: If Your District Misses the Deadline", "tag": "Timelines", "urgent": False},
    {"file": "tefa-voucher-504-plan-vs-iep-texas.html", "title": "TEFA vs. 504 Plan: Which Gets the Funding?", "tag": "504 vs IEP", "urgent": False},
    {"file": "ard-meeting-prep-guide-texas-tefa-voucher.html", "title": "The ARD Meeting Playbook for TEFA Parents", "tag": "ARD Prep", "urgent": False},
    {"file": "texas-esa-application-window-dates-2026.html", "title": "Application Window 2026: Dates & Deadlines", "tag": "Deadlines", "urgent": False},
    {"file": "adhd-texas-esa-disability-funding-guide.html", "title": "ADHD and the Texas ESA: Does My Child Qualify?", "tag": "ADHD", "urgent": False},
    {"file": "what-texas-school-districts-wont-tell-you-esa.html", "title": "What Districts Won't Tell You About ESAs", "tag": "Advocacy", "urgent": False},
    {"file": "tefa-approved-private-schools-texas-disability.html", "title": "How to Choose a TEFA-Approved Private School", "tag": "Private Schools", "urgent": False},
    {"file": "autism-texas-esa-voucher-30000-funding.html", "title": "Texas ESA for Autism: A Step-by-Step Guide", "tag": "Autism", "urgent": False}
]

ES_ARTICLES = [
    {"file": "URGENTE-loteria-tefa-prioridad-ingresos-familias-latinas.html", "title": "Prioridad TEFA: Por Qué las Familias Latinas Van Primero", "tag": "⚡ Urgente", "urgent": True},
    {"file": "guia-completa-cuentas-ahorro-educativo-texas-2026.html", "title": "Guía Completa: Cuentas de Ahorro Educativo 2026", "tag": "Guía Principal", "urgent": False},
    {"file": "como-obtener-30000-esa-texas-iep-espanol.html", "title": "¿Cómo Obtener los $30,000? El IEP Es la Clave", "tag": "Estrategia IEP", "urgent": False},
    {"file": "evaluacion-educacion-especial-texas-regla-45-dias.html", "title": "La Regla de los 45 Días: Si el Distrito se Retrasa", "tag": "Tiempos", "urgent": False},
    {"file": "tdah-texas-voucher-discapacidad-guia-familias.html", "title": "Mi Hijo Tiene TDAH: ¿Califica para la Ayuda?", "tag": "TDAH", "urgent": False},
    {"file": "preparacion-reunion-ard-texas-espanol.html", "title": "La Reunión ARD: Cómo Prepararte para el Éxito", "tag": "Preparación ARD", "urgent": False},
    {"file": "fechas-limite-cuenta-ahorro-educativo-texas-2026.html", "title": "Fechas Límite 2026: Lo Que Debes Hacer Ahora", "tag": "Fechas Límite", "urgent": False},
    {"file": "autismo-texas-esa-voucher-familias-hispanas.html", "title": "Autismo y Cuentas de Ahorro: Guía Paso a Paso", "tag": "Autismo", "urgent": False},
    {"file": "lo-que-distritos-escolares-texas-no-dicen-esa.html", "title": "Lo Que Tu Distrito Escolar No Te Dirá", "tag": "Defensa", "urgent": False},
    {"file": "escuelas-privadas-aprobadas-tefa-texas-discapacidad.html", "title": "Cómo Elegir una Escuela Privada Aprobada", "tag": "Escuelas Privadas", "urgent": False},
    {"file": "recursos-espanol-educacion-especial-texas-2026.html", "title": "Guía de Recursos en Español para Familias", "tag": "Recursos", "urgent": False}
]

def generate_cards_html(articles, base_slug):
    html = ""
    for art in articles:
        urgent_class = "blog-card--urgent" if art["urgent"] else ""
        # The base_slug is injected here to format the path correctly
        html += f"""
        <a href="{base_slug}{art['file']}" class="blog-card {urgent_class}">
           <div class="blog-card__tag">{art['tag']}</div>
           <div class="blog-card__title">{art['title']}</div>
           <div class="blog-card__meta">March 2026 · 5 min read</div>
        </a>"""
    return html

# ======================================================================
# LANGUAGE DICTIONARIES
# ======================================================================
CONTENT_EN = {
    "PAGE_LANG": "en",
    "META_TITLE": "Texas Education Savings Account (TEFA) Guide - 2026 | TexasSpecialEd",
    "META_DESCRIPTION": "Texas Education Savings Accounts give students with disabilities up to $30,000. Learn how to qualify, get your IEP, and navigate the application window.",
    "SHOW_TICKER": "block",
    "TICKER_TEXT": "⚡ TEFA Application Window Extended: <strong>Closes March 31, 2026</strong> — <a href='../tools/tefa-scan/index.html'>Act Now →</a>",
    "BREADCRUMB_HOME": "Home",
    "BREADCRUMB_LABEL": "TEFA Disability Guide",
    "HERO_BADGE_TEXT": "Up to $30,000 Available",
    "HERO_DATE_BADGE": "Updated March 2026",
    "H1_TITLE": "Texas Education Savings Accounts for Students with Disabilities",
    "HERO_SUBTITLE": "Your child may qualify for up to $30,000 to pay for private school, therapies, and curriculum. Most families don't know how to get it. We do.",
    "CTA_PRIMARY_LABEL": "Get the Free ESA Checklist",
    "CTA_SECONDARY_LABEL": "Book a Free 15-Min Call",
    "CTA_SECONDARY_URL": "#contact",
    "TRUST_ITEM_1": "Based on Texas SB 2",
    "TRUST_ITEM_2": "March 31 Deadline",
    "TRUST_ITEM_3": "IEP Strategy Experts",
    "MONEY_SECTION_TITLE": "The Funding Gap You Need to Know",
    "MONEY_SECTION_INTRO": "The state offers two different funding amounts. The difference between getting $10,500 and $30,000 comes down to one piece of paper: a developed IEP.",
    "MONEY_STD_LABEL": "Standard TEFA",
    "MONEY_STD_AMOUNT": "~$10,500",
    "MONEY_STD_NOTE": "For general education students",
    "MONEY_DIS_LABEL": "Disability TEFA",
    "MONEY_DIS_AMOUNT": "Up to $30,000",
    "MONEY_DIS_NOTE": "For students with an IEP",
    "MONEY_CALLOUT_BOLD": "The Catch:",
    "MONEY_CALLOUT_TEXT": "A 504 plan is usually not enough. You need a full public school evaluation and an Individualized Education Program (IEP).",
    "PRIORITY_BOX_TITLE": "Lottery Priority Order Confirmed",
    "PRIORITY_LIST_HTML": "<li><strong>First:</strong> Disability + Income ≤500% FPL</li><li><strong>Second:</strong> Income ≤200% FPL</li><li><strong>Third:</strong> Income 201–500% FPL</li><li><strong>Fourth:</strong> All other applicants</li>",
    "QUALIFY_TITLE": "Does My Child Qualify?",
    "QUALIFY_INTRO": "To trigger the higher disability tier, your child needs an official diagnosis recognized by Texas and IDEA.",
    "DISABILITY_TAGS_HTML": "<span class='disability-tag'>Autism</span><span class='disability-tag'>ADHD (OHI)</span><span class='disability-tag'>Dyslexia</span><span class='disability-tag'>Speech Impairment</span><span class='disability-tag'>Intellectual Disability</span>",
    "REQUIREMENTS_TITLE": "The 3 Non-Negotiables",
    "REQUIREMENTS_CARDS_HTML": "<div class='req-card'><div class='req-card__num'>1</div><strong>Texas Resident</strong><br><span style='font-size:.85rem;color:var(--slate)'>Must live in Texas and meet age requirements.</span></div><div class='req-card'><div class='req-card__num'>2</div><strong>School Evaluation</strong><br><span style='font-size:.85rem;color:var(--slate)'>Completed Full Individual Evaluation (FIE) from a public district.</span></div><div class='req-card'><div class='req-card__num'>3</div><strong>Developed IEP</strong><br><span style='font-size:.85rem;color:var(--slate)'>An active ARD committee document detailing services.</span></div>",
    "TIMELINE_TITLE": "Your Action Timeline",
    "TIMELINE_INTRO": "Districts are backlogged. If you don't start the evaluation process now, you will miss the application window.",
    "TIMELINE_STEPS_HTML": "<div class='timeline__step'><div class='timeline__dot'>1</div><div class='timeline__title'>Request Evaluation</div><div class='timeline__note'>Send a certified letter to your district.</div></div><div class='timeline__step'><div class='timeline__dot'>2</div><div class='timeline__title'>45-Day Clock <span class='tag tag--warn'>Legal Deadline</span></div><div class='timeline__note'>The district has 45 school days to evaluate.</div></div><div class='timeline__step'><div class='timeline__dot'>3</div><div class='timeline__title'>ARD Meeting</div><div class='timeline__note'>Review results and develop the IEP.</div></div><div class='timeline__step'><div class='timeline__dot'>4</div><div class='timeline__title'>Apply for TEFA <span class='tag tag--dead'>Closes Mar 31</span></div><div class='timeline__note'>Submit your IEP to the state portal.</div></div>",
    "TRAPS_TITLE": "The Hidden Traps",
    "TRAPS_INTRO": "Districts lose funding when you take the TEFA voucher. Here is what to watch out for.",
    "CRITICAL_ALERT_TITLE": "Private School 'Gotcha'",
    "CRITICAL_ALERT_BODY": "While an IEP gets you the money, private schools are NOT legally required to provide the services in it. You lose your IDEA rights.",
    "TRAPS_CARDS_HTML": "<div class='trap-card'><div class='trap-card__title'>The Backlog Delay</div><div class='trap-card__body'>Districts push your evaluation past the 45-day mark, making you miss the TEFA window.</div><div class='trap-card__solution'>File a Due Process complaint</div></div><div class='trap-card'><div class='trap-card__title'>The Minimum IEP</div><div class='trap-card__body'>They offer a bare-bones IEP that undersells your child's needs to save the district money.</div><div class='trap-card__solution'>Bring an advocate to ARD</div></div>",
    "MAGNET_TITLE": "Get the Free ESA Checklist",
    "MAGNET_SUBTITLE": "The 12 steps you must take before you apply to guarantee your $30,000 eligibility.",
    "MAGNET_LIST_ITEMS_HTML": "<li>Evaluation request templates</li><li>IEP goal bank for max funding</li><li>Application timeline tracker</li>",
    "MAGNET_FORM_TITLE": "Download Instantly",
    "MAGNET_FORM_SUBTITLE": "Sent directly to your inbox.",
    "FORM_ACTION_URL": "#",
    "FORM_LABEL_NAME": "First Name",
    "FORM_PLACEHOLDER_NAME": "Enter your name",
    "FORM_LABEL_EMAIL": "Email Address",
    "FORM_PLACEHOLDER_EMAIL": "Enter your email",
    "FORM_LABEL_DISTRICT": "School District (Optional)",
    "FORM_PLACEHOLDER_DISTRICT": "e.g. Socorro ISD",
    "FORM_SUBMIT_LABEL": "Send Me The Checklist",
    "FORM_PRIVACY_TEXT": "We never share your information.",
    "BLOGS_TITLE": "Master the ESA Process",
    "BLOGS_INTRO": "Everything you need to know to secure your funding and place your child in the right school.",
    "BLOG_TAB_EN": "English Guides",
    "BLOG_TAB_ES": "Guías en Español",
    "SITE_NAME": "TexasSpecialEd",
    "FOOTER_ABOUT_TEXT": "We help Texas families navigate the special education system, secure IEPs, and access Education Freedom Accounts.",
    "FOOTER_COPYRIGHT": "© 2026 TexasSpecialEd.com. All rights reserved.",
    "FAQ_TITLE": "", "FAQ_ITEMS_HTML": "", "PRODUCTS_TITLE": "", "PRODUCTS_INTRO": "", "PRODUCT_ITEMS_HTML": "", "DISTRICTS_TITLE": "", "DISTRICTS_INTRO": "", "DISTRICT_PILLS_HTML": "", "SPANISH_TITLE": "", "SPANISH_BODY": "", "SPANISH_CTA_LABEL": "", "SPANISH_URL": ""
}

CONTENT_ES = CONTENT_EN.copy()
CONTENT_ES.update({
    "PAGE_LANG": "es",
    "META_TITLE": "Cuentas de Ahorro Educativo (TEFA) Texas - 2026 | TexasSpecialEd",
    "META_DESCRIPTION": "Las Cuentas de Ahorro Educativo dan hasta $30,000 para estudiantes. Aprende cómo calificar y navegar el proceso.",
    "TICKER_TEXT": "⚡ Ventana de Solicitud TEFA Extendida: <strong>Cierra el 31 de Marzo, 2026</strong> — <a href='../tools/tefa-scan/index.html'>Actúa Ahora →</a>",
    "BREADCRUMB_HOME": "Inicio",
    "BREADCRUMB_LABEL": "Guía TEFA",
    "HERO_BADGE_TEXT": "Hasta $30,000 Disponibles",
    "HERO_DATE_BADGE": "Actualizado Marzo 2026",
    "H1_TITLE": "Cuentas de Ahorro Educativo de Texas para Estudiantes",
    "HERO_SUBTITLE": "Tu hijo puede calificar para recibir hasta $30,000 para escuela privada y terapias. Aseguremos el éxito escolar de tu familia.",
    "CTA_PRIMARY_LABEL": "Obtener Lista de Verificación",
    "CTA_SECONDARY_LABEL": "Consulta Gratuita de 15 Min",
    "TRUST_ITEM_1": "Basado en SB 2 de Texas",
    "TRUST_ITEM_2": "Límite: 31 de Marzo",
    "TRUST_ITEM_3": "Expertos en Estrategia IEP",
    "MONEY_SECTION_TITLE": "La Diferencia en los Fondos",
    "MONEY_SECTION_INTRO": "El estado ofrece dos montos diferentes. La diferencia entre recibir $10,500 y $30,000 depende de un documento: un IEP desarrollado.",
    "MONEY_STD_NOTE": "Para estudiantes de educación general",
    "MONEY_DIS_NOTE": "Para estudiantes con un IEP",
    "MONEY_CALLOUT_BOLD": "Ojo:",
    "MONEY_CALLOUT_TEXT": "Un plan 504 no es suficiente. Necesitas una evaluación completa de la escuela pública y un Programa de Educación Individualizado (IEP).",
    "PRIORITY_BOX_TITLE": "Orden de Prioridad Confirmado",
    "PRIORITY_LIST_HTML": "<li><strong>Primero:</strong> Discapacidad + Ingresos ≤500% Nivel de Pobreza</li><li><strong>Segundo:</strong> Ingresos ≤200%</li><li><strong>Tercero:</strong> Ingresos 201–500%</li>",
    "QUALIFY_TITLE": "¿Califica Mi Hijo?",
    "REQUIREMENTS_TITLE": "Los 3 Requisitos",
    "REQUIREMENTS_CARDS_HTML": "<div class='req-card'><div class='req-card__num'>1</div><strong>Residente de Texas</strong></div><div class='req-card'><div class='req-card__num'>2</div><strong>Evaluación Escolar</strong></div><div class='req-card'><div class='req-card__num'>3</div><strong>IEP Desarrollado</strong></div>",
    "TIMELINE_TITLE": "Tu Plan de Acción",
    "TIMELINE_INTRO": "Los distritos están atrasados. Si no comienzas el proceso de evaluación ahora, perderás la oportunidad.",
    "TIMELINE_STEPS_HTML": "<div class='timeline__step'><div class='timeline__dot'>1</div><div class='timeline__title'>Solicitar Evaluación</div></div><div class='timeline__step'><div class='timeline__dot'>2</div><div class='timeline__title'>Regla de 45 Días</div></div><div class='timeline__step'><div class='timeline__dot'>3</div><div class='timeline__title'>Reunión ARD</div></div><div class='timeline__step'><div class='timeline__dot'>4</div><div class='timeline__title'>Aplicar a TEFA</div></div>",
    "TRAPS_TITLE": "Lo Que No Te Dicen",
    "CRITICAL_ALERT_TITLE": "Cuidado con las Escuelas Privadas",
    "CRITICAL_ALERT_BODY": "Las escuelas privadas que aceptan fondos TEFA no están obligadas por ley a proporcionar los servicios listados en el IEP.",
    "MAGNET_TITLE": "Lista de Verificación Gratuita",
    "MAGNET_SUBTITLE": "Los 12 pasos antes de aplicar.",
    "MAGNET_FORM_TITLE": "Descarga Instantánea",
    "FORM_LABEL_NAME": "Nombre",
    "FORM_LABEL_EMAIL": "Correo Electrónico",
    "FORM_LABEL_DISTRICT": "Distrito Escolar",
    "FORM_SUBMIT_LABEL": "Enviar",
    "BLOGS_TITLE": "Recursos para Tu Familia",
    "BLOGS_INTRO": "Todo lo que necesitas saber para asegurar el futuro de tu hijo."
})

def build_hubs():
    os.makedirs(OUT_DIR_EN, exist_ok=True)
    os.makedirs(OUT_DIR_ES, exist_ok=True)

    try:
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as tf:
            base_template = tf.read()
    except FileNotFoundError:
        print(f"❌ Error: Could not find template at {TEMPLATE_PATH}")
        return

    # Pass the appropriate slugs to the HTML generator
    cards_en_html = generate_cards_html(EN_ARTICLES, BASE_SLUG_EN)
    cards_es_html = generate_cards_html(ES_ARTICLES, BASE_SLUG_ES)

    base_template = base_template.replace("{{BLOG_CARDS_EN_HTML}}", cards_en_html)
    base_template = base_template.replace("{{BLOG_CARDS_ES_HTML}}", cards_es_html)

    # 1. Build English Index
    en_html = base_template
    for key, value in CONTENT_EN.items():
        en_html = en_html.replace("{{" + key + "}}", str(value))
    
    en_html = re.sub(r'\{\{[A-Z0-9_]+\}\}', '', en_html)

    with open(os.path.join(OUT_DIR_EN, "index.html"), "w", encoding="utf-8") as f:
        f.write(en_html)
    print("✅ Created: en/index.html")

    # 2. Build Spanish Index
    es_html = base_template
    for key, value in CONTENT_ES.items():
        es_html = es_html.replace("{{" + key + "}}", str(value))
    
    es_html = es_html.replace("id=\"grid-en\" class=\"blog-grid\"", "id=\"grid-en\" class=\"blog-grid\" style=\"display:none\"")
    es_html = es_html.replace("id=\"grid-es\" class=\"blog-grid\" style=\"display:none\"", "id=\"grid-es\" class=\"blog-grid\"")
    es_html = es_html.replace("aria-selected=\"true\" onclick=\"switchTab('en')\" style=\"padding:9px 22px;font-size:.88rem;font-weight:600;background:none;border:none;border-bottom:2px solid var(--teal);color:var(--navy);", "aria-selected=\"false\" onclick=\"switchTab('en')\" style=\"padding:9px 22px;font-size:.88rem;font-weight:500;background:none;border:none;border-bottom:2px solid transparent;color:var(--muted);")
    es_html = es_html.replace("aria-selected=\"false\" onclick=\"switchTab('es')\" style=\"padding:9px 22px;font-size:.88rem;font-weight:500;background:none;border:none;border-bottom:2px solid transparent;color:var(--muted);", "aria-selected=\"true\" onclick=\"switchTab('es')\" style=\"padding:9px 22px;font-size:.88rem;font-weight:600;background:none;border:none;border-bottom:2px solid var(--teal);color:var(--navy);")
    
    es_html = re.sub(r'\{\{[A-Z0-9_]+\}\}', '', es_html)

    with open(os.path.join(OUT_DIR_ES, "index.html"), "w", encoding="utf-8") as f:
        f.write(es_html)
    print("✅ Created: es/index.html")

if __name__ == "__main__":
    build_hubs()