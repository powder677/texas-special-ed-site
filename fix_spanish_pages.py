"""
fix_spanish_pages.py
--------------------
Fixes all 4 issues found in spanish_page_issues.txt across all 113 pages.
No API needed.

Fixes applied to every como-solicitar-una-evaluacion-fie-en-*.html:
  1. Truncated inline-cta → replaced with complete Spanish CTA block
  2. Quick Answer box → translated to Spanish
  3. Silo nav "What Is an FIE?" → translated to Spanish
  4. FAQ JSON-LD schema → removed (it was English, not needed on Spanish pages)
"""

import os
import re
import glob

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
DISTRICTS_DIR = os.path.join(SCRIPT_DIR, "districts")

# ── The complete Spanish CTA block that replaces the truncated one ─────────────

SPANISH_CTA_BLOCK = """<div class="inline-cta" style="background:#fdfaf5;border:1px solid #d6cbbf;border-left:4px solid #b8963a;border-radius:6px;padding:24px;margin:2.5rem 0;display:flex;gap:16px;align-items:flex-start;">
<div class="cta-icon">📝</div>
<div>
<h3 style="margin:0 0 8px;font-family:'Lora',serif;font-size:1.3rem;color:#0a2342;border:none;padding:0;">¿Lista para enviar tu solicitud?</h3>
<p style="margin:0 0 16px;font-size:16px;color:#475569;">Usa nuestro generador gratuito en español para redactar una carta con validez legal en minutos. El sistema cita el Capítulo 29 del Código de Educación de Texas y obliga al distrito a responder en 15 días escolares.</p>
<a href="/resources/iep-letter-spanish/" style="background:#b8963a;color:#fff;padding:12px 24px;text-decoration:none;border-radius:4px;font-weight:600;font-size:15px;display:inline-block;">Generar mi carta en español →</a>
</div>
</div>"""

# ── Fix 1: Truncated inline-cta ───────────────────────────────────────────────

def fix_truncated_cta(html):
    """
    The inline-cta div was cut off mid-tag. Replace everything from
    the broken <div class="inline-cta" up to </section> with the
    complete CTA block + closing </section>.
    """
    pattern = re.compile(
        r'<div class="inline-cta".*?</section>',
        re.DOTALL
    )
    replacement = SPANISH_CTA_BLOCK + "\n</section>"
    new_html, count = pattern.subn(replacement, html, count=1)
    return new_html, count > 0


# ── Fix 2: Quick Answer box ───────────────────────────────────────────────────

def fix_quick_answer(html, district_name):
    """
    Replace the English Quick Answer paragraph with Spanish.
    The label (⚡ Respuesta Rápida) was already translated — only the
    paragraph content needs replacing.
    """
    pattern = re.compile(
        r'(<p style="[^"]*font-size:0\.8rem[^"]*">.*?Respuesta Rápida.*?</p>\s*)'
        r'<p[^>]*>.*?</p>',
        re.DOTALL
    )
    spanish_para = (
        f'\\1'
        f'<p style="margin:0;font-size:1.05rem;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;line-height:1.6;">'
        f'<strong>¿Qué es una FIE en {district_name}?</strong><br/>'
        f'Una FIE — Evaluación Individual Completa — es el proceso de evaluación integral que {district_name} debe completar para determinar si tu hijo tiene una discapacidad y califica para servicios de educación especial. Debe cubrir <strong>todas las áreas de discapacidad sospechada</strong>, no puede ser una sola prueba y debe completarse dentro de <strong>45 días escolares</strong> a partir de tu consentimiento escrito. Una vez que envíes una solicitud escrita, {district_name} tiene <strong>15 días escolares</strong> para responder.'
        f'</p>'
    )
    new_html, count = pattern.subn(spanish_para, html, count=1)
    return new_html, count > 0


# ── Fix 3: Silo nav ───────────────────────────────────────────────────────────

def fix_silo_nav(html):
    """Replace 'What Is an FIE?' with Spanish in the silo nav."""
    new_html = html.replace(
        '>What Is an FIE?<',
        '>¿Cómo solicitar una FIE?<'
    )
    changed = new_html != html
    return new_html, changed


# ── Fix 4: Remove English FAQ schema ─────────────────────────────────────────

def fix_faq_schema(html):
    """Remove the FAQPage JSON-LD block entirely — it's in English."""
    pattern = re.compile(
        r'<!-- FAQPage Schema.*?</script>\s*',
        re.DOTALL
    )
    new_html, count = pattern.subn('', html, count=1)
    return new_html, count > 0


# ── Extract district name from file ──────────────────────────────────────────

def get_district_name(html, slug):
    """Pull district name from the h1 or title tag."""
    # Try Spanish h1 first
    m = re.search(r'<h1[^>]*>Cómo solicitar una evaluación FIE en ([^:]+?):', html)
    if m:
        return m.group(1).strip()
    # Try English h1
    m = re.search(r'<h1[^>]*>What Is an FIE.*?in\s+([^?]+)\?', html)
    if m:
        return m.group(1).strip()
    # Try title tag
    m = re.search(r'<title>(?:Cómo solicitar[^|]+en\s+)?([^|<]+?)(?:\s*\||\s*-)', html)
    if m:
        return m.group(1).strip()
    # Fallback: reconstruct from slug
    return slug.replace('-', ' ').title().replace(' Isd', ' ISD').replace(' Cisd', ' CISD')


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    files = sorted(set(
        glob.glob(os.path.join(DISTRICTS_DIR, "**", "como-solicitar-una-evaluacion-fie-en-*.html"), recursive=True)
    ))
    total = len(files)

    fixed_cta    = 0
    fixed_qa     = 0
    fixed_nav    = 0
    fixed_schema = 0
    errors       = []

    print(f"Fixing {total} Spanish FIE pages...\n")

    for filepath in files:
        slug = os.path.basename(os.path.dirname(filepath))

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                html = f.read()

            district_name = get_district_name(html, slug)
            changes = []

            # Fix 1 — truncated CTA
            if 'inline-cta' in html and 'Generar mi carta' not in html:
                html, ok = fix_truncated_cta(html)
                if ok:
                    fixed_cta += 1
                    changes.append("CTA")

            # Fix 2 — English Quick Answer
            if 'What is an FIE in' in html:
                html, ok = fix_quick_answer(html, district_name)
                if ok:
                    fixed_qa += 1
                    changes.append("QuickAnswer")

            # Fix 3 — English silo nav
            if '>What Is an FIE?<' in html:
                html, ok = fix_silo_nav(html)
                if ok:
                    fixed_nav += 1
                    changes.append("SiloNav")

            # Fix 4 — English FAQ schema
            if '"What is an FIE' in html and 'application/ld+json' in html:
                html, ok = fix_faq_schema(html)
                if ok:
                    fixed_schema += 1
                    changes.append("Schema")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)

            status = ", ".join(changes) if changes else "nothing to fix"
            print(f"  ✓  {slug:<45} [{status}]")

        except Exception as e:
            errors.append((slug, str(e)))
            print(f"  ✗  {slug}  ERROR: {e}")

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Pages processed      : {total}
  ✅  CTA fixed        : {fixed_cta}
  ✅  Quick Answer fixed: {fixed_qa}
  ✅  Silo nav fixed   : {fixed_nav}
  ✅  Schema removed   : {fixed_schema}
  ❌  Errors           : {len(errors)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run check_spanish_pages.py again to verify all issues are resolved.
""")

    if errors:
        print("Error details:")
        for slug, msg in errors:
            print(f"  {slug}: {msg}")


if __name__ == "__main__":
    main()