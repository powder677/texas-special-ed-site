"""
fix_spanish_sidebar_card.py
---------------------------
Replaces the English sidebar CTA card with the Spanish version across
all como-solicitar-una-evaluacion-fie-en-*-texas.html files.

Handles both Windows (CRLF) and Unix (LF) line endings.
No API needed.
"""

import os
import glob
import re

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
DISTRICTS_DIR = os.path.join(SCRIPT_DIR, "districts")

SPANISH_CARD = """<aside class="sidebar-column">
<div class="sidebar-card cta-card" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);padding:28px;border-radius:12px;text-align:center;color:#fff;border:none;margin-bottom:24px;">
<h4 style="font-family:'Lora',serif;font-size:1.25rem;margin:0 0 10px;color:#fff;">Demuéstrale al Distrito<br/>que Vas en Serio</h4>
<p style="font-family:'Source Sans 3',sans-serif;font-size:14px;color:#94a3b8;margin:0 0 18px;line-height:1.5;">Una solicitud verbal no tiene peso legal. Una carta escrita inicia el plazo de 45 días y obliga al distrito a responder en 15 días escolares.</p>
<a href="/resources/iep-letter-spanish/" style="display:block;background:#d4af37;color:#0f172a;padding:14px;border-radius:6px;text-decoration:none;font-weight:800;font-family:'DM Sans',sans-serif;font-size:14px;transition:background 0.2s;">Obtener Tu Carta — $25 →</a>
</div>"""

def replace_sidebar_card(html):
    """
    Replace the English sidebar card using a regex so line endings
    (CRLF or LF) don't matter.
    """
    pattern = re.compile(
        r'<aside class="sidebar-column">\s*'
        r'<div class="sidebar-card cta-card"[^>]*>\s*'
        r'<h4[^>]*>Show the ISD<br/>You Mean Business</h4>\s*'
        r'<p[^>]*>A verbal request[^<]*</p>\s*'
        r'<a[^>]*>.*?</a>\s*'
        r'</div>',
        re.DOTALL
    )
    return pattern.sub(SPANISH_CARD, html, count=1)

def main():
    # Match both naming conventions: with and without -texas suffix
    files = sorted(set(
        glob.glob(os.path.join(DISTRICTS_DIR, "**", "como-solicitar-una-evaluacion-fie-en-*-texas.html"), recursive=True) +
        glob.glob(os.path.join(DISTRICTS_DIR, "**", "como-solicitar-una-evaluacion-fie-en-*.html"), recursive=True)
    ))
    total   = len(files)

    updated   = 0
    skipped   = 0
    not_found = 0

    print(f"Found {total} Spanish FIE pages...\n")

    for filepath in files:
        slug = os.path.basename(os.path.dirname(filepath))

        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()

        # Already fixed?
        if "Demuéstrale al Distrito" in html:
            skipped += 1
            print(f"  –  already done   {slug}")
            continue

        # English card still present?
        if "Show the ISD" not in html:
            not_found += 1
            print(f"  ⚠  not found      {slug}")
            continue

        new_html = replace_sidebar_card(html)

        if new_html == html:
            not_found += 1
            print(f"  ⚠  regex no match {slug}")
            continue

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_html)

        updated += 1
        print(f"  ✓  {slug}")

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅  Updated  : {updated}
  ⏭️   Skipped  : {skipped}  (already done)
  ⚠️   No match : {not_found}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

if __name__ == "__main__":
    main()