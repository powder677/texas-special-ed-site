"""
extract_spanish_to_new_page.py
-------------------------------
No API needed. Free.

The inject_spanish_fie.py script already generated Spanish content and
injected it into each English FIE page. This script:

  1. Reads each districts/{slug}/what-is-an-fie-{slug}.html
  2. Extracts the Spanish section between the injected comment markers
  3. Builds a complete standalone Spanish HTML page around it
     (reusing the same nav, CSS, sidebar, footer from the English page)
  4. Saves it as:
     districts/{slug}/como-solicitar-una-evaluacion-fie-en-{slug}.html
  5. Restores the English page back to its original .bak (removes the injection)

Usage:
    python extract_spanish_to_new_page.py
"""

import os
import re
import glob

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
DISTRICTS_DIR = os.path.join(SCRIPT_DIR, "districts")

SPANISH_BOT_URL = "/resources/iep-letter-spanish/"

# These are the comment markers the inject script wrapped around the Spanish block
SPANISH_START = "<!-- SECCION EN ESPAÑOL"
SPANISH_END   = "<!-- FIN SECCION EN ESPAÑOL"

# ── Helpers ───────────────────────────────────────────────────────────────────

def to_slug(name):
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = slug.strip()
    slug = re.sub(r"\s+", "-", slug)
    return slug

def to_spanish_slug(name):
    return "como-solicitar-una-evaluacion-fie-en-" + to_slug(name)


def extract_spanish_content(html):
    """Pull out everything between the injected comment markers."""
    pattern = re.compile(
        r'<!-- SECCION EN ESPAÑOL.*?-->(.*?)<!-- FIN SECCION EN ESPAÑOL.*?-->',
        re.DOTALL
    )
    match = pattern.search(html)
    if not match:
        return None
    # Return just the inner HTML (the actual section tag and content)
    return match.group(1).strip()


def remove_spanish_injection(html):
    """Strip the injected Spanish block out of the English page, restoring it cleanly."""
    pattern = re.compile(
        r'\n?<!-- SECCION EN ESPAÑOL.*?<!-- FIN SECCION EN ESPAÑOL.*?-->\s*\n?',
        re.DOTALL
    )
    return pattern.sub('', html)


def extract_district_name_from_html(html):
    """Pull the district name from the <h1> tag."""
    match = re.search(r'<h1[^>]*>What Is an FIE.*?in\s+(.*?)\?', html)
    if match:
        return match.group(1).strip()
    # Fallback: pull from <title>
    match = re.search(r'<title>FIE Evaluation Guide for (.+?) Parents', html)
    if match:
        return match.group(1).strip()
    return None


def build_spanish_page(english_html, spanish_content, district_name, slug):
    """
    Build a full Spanish page by:
    - Taking the English page structure (nav, CSS, sidebar, footer, scripts)
    - Swapping in the Spanish content as the main article body
    - Updating title, meta, h1, lang, canonical, and CTA links
    """
    spanish_slug = to_spanish_slug(district_name)
    page = english_html

    # 1. lang attribute
    page = page.replace('<html lang="en">', '<html lang="es">')

    # 2. <title>
    page = re.sub(
        r'<title>.*?</title>',
        f'<title>Cómo solicitar una evaluación FIE en {district_name} | Guía para Padres de Texas</title>',
        page
    )

    # 3. meta description
    page = re.sub(
        r'<meta content="[^"]*" name="description"/>',
        f'<meta content="Guía completa para padres hispanos sobre cómo solicitar una evaluación FIE en {district_name}. Conoce tus derechos, los plazos legales y cómo obtener servicios de educación especial para tu hijo." name="description"/>',
        page
    )

    # 4. canonical URL
    page = re.sub(
        r'(https://www\.texasspecialed\.com/districts/' + slug + r'/)[^\s"]+',
        rf'\g<1>{spanish_slug}',
        page
    )

    # 5. h1
    page = re.sub(
        r'<h1>What Is an FIE.*?</h1>',
        f'<h1>Cómo solicitar una evaluación FIE en {district_name}: Guía para Padres de Texas</h1>',
        page
    )

    # 6. breadcrumb last item
    page = re.sub(
        r'<span>What Is an FIE\?</span>',
        '<span>¿Cómo solicitar una FIE?</span>',
        page
    )

    # 7. Replace English article content with the Spanish section
    #    Find the <article ...> ... </article> block and replace its body
    article_pattern = re.compile(r'(<article[^>]*>).*?(</article>)', re.DOTALL)
    spanish_article = (
        r'\1\n'
        f'{spanish_content}\n'
        r'\2'
    )
    page = article_pattern.sub(spanish_article, page, count=1)

    # 8. Swap all English CTA letter links to Spanish bot
    page = page.replace('/resources/Iep-letter"', f'{SPANISH_BOT_URL}"')
    page = page.replace('/resources/Iep-letter.html"', f'{SPANISH_BOT_URL}"')
    page = page.replace('/resources/iep-letter"', f'{SPANISH_BOT_URL}"')
    page = page.replace('/resources/iep-letter.html"', f'{SPANISH_BOT_URL}"')
    # Nav CTA button text
    page = page.replace('Get Your Letter — $25', 'Obtener Tu Carta — $25')

    # 9. Sidebar eyebrow — swap "Special Ed Law" label
    page = re.sub(
        r'(<p class="sf-eyebrow">)[^<]*(</p>)',
        rf'\1{district_name} Ley de Educación Especial\2',
        page
    )

    # 10. Sidebar form button
    page = page.replace(
        'Get My Free 15-Minute Call',
        'Obtener Mi Llamada Gratuita de 15 Minutos'
    )

    # 11. Sidebar "Not sure how to request" text
    page = page.replace(
        'Not sure how to request an FIE?',
        '¿No sabes cómo solicitar una FIE?'
    )

    # 12. Quick Answer box label
    page = page.replace('⚡ Quick Answer', '⚡ Respuesta Rápida')

    # 13. Sidebar top CTA card
    page = page.replace(
        'Show the ISD<br/>You Mean Business',
        'Demuéstrale al Distrito<br/>que Vas en Serio'
    )
    page = page.replace(
        'A verbal request has no legal weight. A written letter starts the 45-day clock and forces a response within 15 school days.',
        'Una solicitud verbal no tiene peso legal. Una carta escrita inicia el plazo de 45 días y obliga al distrito a responder en 15 días escolares.'
    )
    page = page.replace(
        'Get Your Letter — $25 →',
        'Obtener Tu Carta — $25 →'
    )

    return page


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Find all modified English FIE pages that contain the injected Spanish block
    pattern  = os.path.join(DISTRICTS_DIR, "**", "what-is-an-fie-*.html")
    all_files = [f for f in glob.glob(pattern, recursive=True)
                 if not f.endswith(".bak") and not f.endswith("-es.html")]

    total    = len(all_files)
    created  = 0
    skipped  = 0
    restored = 0
    no_spanish = 0

    print(f"Found {total} FIE HTML files to process...\n")

    for filepath in sorted(all_files):
        slug = os.path.basename(os.path.dirname(filepath))

        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()

        # ── No Spanish injection found in this file ───────────────────────────
        if SPANISH_START not in html:
            no_spanish += 1
            print(f"  –  NO SPANISH  {slug}/what-is-an-fie-{slug}.html")
            continue

        # Get district name
        district_name = extract_district_name_from_html(html)
        if not district_name:
            print(f"  ⚠  Could not detect district name in {slug} — skipping")
            no_spanish += 1
            continue

        spanish_slug = to_spanish_slug(district_name)
        output_path  = os.path.join(os.path.dirname(filepath), f"{spanish_slug}.html")

        # ── Already done ──────────────────────────────────────────────────────
        if os.path.exists(output_path):
            skipped += 1
            print(f"  –  EXISTS      {slug}/{spanish_slug}.html")
        else:
            # Extract Spanish content
            spanish_content = extract_spanish_content(html)
            if not spanish_content:
                print(f"  ⚠  Extraction failed for {slug} — skipping")
                no_spanish += 1
                continue

            # Build full Spanish page
            spanish_page = build_spanish_page(html, spanish_content, district_name, slug)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(spanish_page)

            created += 1
            print(f"  ✓  CREATED     {slug}/{spanish_slug}.html")

        # ── Restore English page from .bak (remove the injection) ────────────
        bak_path = filepath + ".bak"
        if os.path.exists(bak_path):
            with open(bak_path, "r", encoding="utf-8") as f:
                original = f.read()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(original)
            os.remove(bak_path)
            restored += 1
            print(f"  ↩  RESTORED    {slug}/what-is-an-fie-{slug}.html (removed injection)")
        else:
            # No .bak — clean the injection out of the live file
            cleaned = remove_spanish_injection(html)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(cleaned)
            print(f"  ↩  CLEANED     {slug}/what-is-an-fie-{slug}.html (injection stripped)")

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅  Spanish pages created  : {created}
  ⏭️   Already existed        : {skipped}
  ↩️   English pages restored : {restored}
  ⚠️   No Spanish found       : {no_spanish}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Spanish files saved to each district silo:
  districts/{{slug}}/como-solicitar-una-evaluacion-fie-en-{{slug}}.html

English FIE pages restored to their originals.
""")


if __name__ == "__main__":
    main()