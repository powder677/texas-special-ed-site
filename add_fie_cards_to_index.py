"""
add_fie_cards_to_index.py
--------------------------
Adds two hub-cards to the hub-grid in each district's index.html:

  Card 1 — English FIE page:
    href="/districts/{slug}/what-is-an-fie-{slug}.html"

  Card 2 — Spanish FIE page:
    href="/districts/{slug}/como-solicitar-una-evaluacion-fie-en-{slug}.html"
    (also checks -texas suffix variant)

Skips any card that already exists. Safe to re-run.

Usage:
    python add_fie_cards_to_index.py
"""

import os
import re
import glob

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
DISTRICTS_DIR = os.path.join(SCRIPT_DIR, "districts")


def to_slug(name):
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = slug.strip()
    slug = re.sub(r"\s+", "-", slug)
    return slug


def english_fie_card(slug):
    return (
        f'<a class="hub-card" href="/districts/{slug}/what-is-an-fie-{slug}.html" style="border-left-color: #1a56db;">\n'
        f'<div class="hub-card-icon">📄</div>\n'
        f'<h3>What Is an FIE?</h3>\n'
        f'<p>Understand your child\'s Full Individual Evaluation rights — timelines, what\'s covered, and how to request one.</p>\n'
        f'</a>'
    )


def spanish_fie_card(slug):
    # Detect which Spanish filename exists on disk
    texas_file = os.path.join(DISTRICTS_DIR, slug, f"como-solicitar-una-evaluacion-fie-en-{slug}-texas.html")
    plain_file  = os.path.join(DISTRICTS_DIR, slug, f"como-solicitar-una-evaluacion-fie-en-{slug}.html")
    if os.path.exists(texas_file):
        href = f"/districts/{slug}/como-solicitar-una-evaluacion-fie-en-{slug}-texas.html"
    else:
        href = f"/districts/{slug}/como-solicitar-una-evaluacion-fie-en-{slug}.html"

    return (
        f'<a class="hub-card" href="{href}" style="border-left-color: #b8963a; background:#fdfaf5;">\n'
        f'<div class="hub-card-icon">🇲🇽</div>\n'
        f'<h3>¿Cómo solicitar una FIE?</h3>\n'
        f'<p>Guía en español para padres hispanos — plazos legales, tus derechos y cómo obtener una evaluación para tu hijo.</p>\n'
        f'</a>'
    )


def get_district_name(html):
    m = re.search(r'<h1[^>]*>([^<]+?) Special Education Resources', html)
    if m:
        return m.group(1).strip()
    m = re.search(r'<title>([^|<]+?) Special Education', html)
    if m:
        return m.group(1).strip()
    return None


def inject_cards(html, slug):
    """Insert missing cards just before the closing </div> of .hub-grid."""

    en_already = f'what-is-an-fie-{slug}' in html
    es_already = f'como-solicitar-una-evaluacion-fie-en-{slug}' in html

    if en_already and es_already:
        return html, []

    cards_added = []
    inject_block = ""

    if not en_already:
        inject_block += english_fie_card(slug) + "\n"
        cards_added.append("EN-FIE")
    if not es_already:
        inject_block += spanish_fie_card(slug) + "\n"
        cards_added.append("ES-FIE")

    # Find end of hub-grid div — match class="hub-grid" ... </div>
    # Use a regex that handles CRLF and LF
    pattern = re.compile(
        r'(class="hub-grid"[\s\S]*?)(</div>)',
        re.DOTALL
    )

    def replacer(m):
        return m.group(1) + inject_block + m.group(2)

    new_html, n = pattern.subn(replacer, html, count=1)
    if n == 0:
        return html, []

    return new_html, cards_added


def main():
    # Find all district index.html files (exclude top-level districts/index.html)
    all_files = glob.glob(os.path.join(DISTRICTS_DIR, "**", "index.html"), recursive=True)
    index_files = sorted([
        f for f in all_files
        if os.path.basename(os.path.dirname(f)) not in ("districts",)
        and os.path.dirname(f) != DISTRICTS_DIR
    ])

    total   = len(index_files)
    updated = 0
    skipped = 0
    errors  = []

    print(f"Processing {total} district index.html files...\n")

    for filepath in index_files:
        slug = os.path.basename(os.path.dirname(filepath))

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                html = f.read()

            # Skip pages without a hub-grid (not a district hub page)
            if 'class="hub-grid"' not in html:
                skipped += 1
                print(f"  –  no hub-grid    {slug}")
                continue

            new_html, cards_added = inject_cards(html, slug)

            if not cards_added:
                skipped += 1
                print(f"  –  already done   {slug}")
                continue

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_html)

            updated += 1
            print(f"  ✓  {slug:<50} [{', '.join(cards_added)}]")

        except Exception as e:
            errors.append((slug, str(e)))
            print(f"  ✗  ERROR  {slug}: {e}")

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total district indexes : {total}
  ✅  Updated            : {updated}
  ⏭️   Already complete   : {skipped}
  ❌  Errors             : {len(errors)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

    if errors:
        print("Error details:")
        for s, msg in errors:
            print(f"  {s}: {msg}")


if __name__ == "__main__":
    main()