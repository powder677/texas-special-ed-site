"""
add_partners_card.py

Injects the Featured Partner ad box into every district index.html
that is missing it. Inserts after the .grid-links closing div.

Usage:
    python add_partners_card.py --root "C:/path/to/your/site"

Dry run (preview only, no files written):
    python add_partners_card.py --root "C:/path/to/your/site" --dry-run
"""

import argparse
import re
import sys
from pathlib import Path

# ─── CARD TEMPLATE ────────────────────────────────────────────────────────────
CARD_TEMPLATE = """\n\n  <!-- Staged Premium Ad Box -->
  <div class="featured-ad-container">
    <span class="ad-badge">Featured Partner</span>
    <div class="ad-content">
      <h2>🤝 Need Professional Advocacy in Your District?</h2>
      <p>Connect with our highest-rated local partner. Get hands-on help from experienced educational advocates who know {district_name} inside and out. Perfect for difficult ARDs, mediations, and complex IEP negotiations.</p>
      <a href="/districts/{district_slug}/partners.html" class="btn-ad">Partner Name - Learn More &amp; Get Support</a>
    </div>
  </div>\n"""

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def get_district_name(html: str, slug: str) -> str:
    """Pull district name from <h1>, fall back to slug."""
    match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    if match:
        raw = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        # Strip common suffixes
        raw = re.sub(
            r'\s*(special education|resources|hub|parent rights guide).*',
            '', raw, flags=re.IGNORECASE
        ).strip()
        if raw:
            return raw
    return slug.replace('-', ' ').title()


def already_has_card(html: str) -> bool:
    return 'featured-ad-container' in html


def find_insertion_point(html: str) -> int | None:
    """
    Returns the index to insert the card at, using three strategies:
    1. If the comment marker already exists (card was removed), insert there.
    2. Walk the .grid-links div to find its closing </div>.
    3. Fall back to just before .content-section.
    """
    # Strategy 1: re-insert at where the comment marker was left behind
    marker = '<!-- Staged Premium Ad Box -->'
    idx = html.find(marker)
    if idx != -1:
        return idx

    # Strategy 2: find grid-links div, walk nesting to closing </div>
    start = html.find('class="grid-links"')
    if start == -1:
        start = html.find("class='grid-links'")

    if start != -1:
        tag_open = html.rfind('<', 0, start)
        if tag_open != -1:
            depth = 0
            i = tag_open
            while i < len(html):
                if html[i:i+4] == '<!--':
                    end = html.find('-->', i)
                    i = end + 3 if end != -1 else i + 1
                elif html[i:i+2] == '</':
                    end = html.find('>', i)
                    tag = html[i+2:end].strip().lower().split()[0] if end != -1 else ''
                    if tag == 'div':
                        depth -= 1
                        if depth == 0:
                            return end + 1
                    i = end + 1 if end != -1 else i + 1
                elif html[i] == '<':
                    end = html.find('>', i)
                    tag_content = html[i+1:end].strip() if end != -1 else ''
                    tag_name = re.split(r'[\s/]', tag_content)[0].lower() if tag_content else ''
                    if tag_name == 'div' and not tag_content.endswith('/'):
                        depth += 1
                    i = end + 1 if end != -1 else i + 1
                else:
                    i += 1

    # Strategy 3: insert before the content-section block
    fallback = html.find('<div class="content-section"')
    if fallback != -1:
        return fallback

    return None


def process_file(path: Path, dry_run: bool) -> str:
    try:
        html = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        html = path.read_text(encoding='latin-1')

    if already_has_card(html):
        return 'SKIPPED — already has card'

    insert_at = find_insertion_point(html)
    if insert_at is None:
        return 'SKIPPED — no insertion point found (no .grid-links or .content-section)'

    slug          = path.parent.name
    district_name = get_district_name(html, slug)
    card          = CARD_TEMPLATE.format(district_name=district_name, district_slug=slug)

    new_html = html[:insert_at] + card + html[insert_at:]

    if not dry_run:
        path.write_text(new_html, encoding='utf-8')

    return f'ADDED → {district_name}'


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Inject the Featured Partner card into district index pages.'
    )
    parser.add_argument(
        '--root', required=True,
        help='Path to site root folder (must contain a /districts/ subfolder)'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Preview what would change without writing any files'
    )
    args = parser.parse_args()

    root         = Path(args.root)
    districts_dir = root / 'districts'

    if not districts_dir.exists():
        print(f'ERROR: /districts/ folder not found at {districts_dir}')
        sys.exit(1)

    # district index pages are at districts/*/index.html
    # exclude the top-level districts/index.html itself
    targets = sorted([
        p for p in districts_dir.glob('*/index.html')
        if p.parent != districts_dir
    ])

    if not targets:
        print('No district index.html files found.')
        sys.exit(0)

    print(f'Found {len(targets)} district index pages.')
    if args.dry_run:
        print('DRY RUN — no files will be modified.\n')

    added = skipped_card = skipped_no_point = 0

    for path in targets:
        result = process_file(path, dry_run=args.dry_run)
        slug   = path.parent.name
        print(f'  [{slug}]  {result}')

        if result.startswith('ADDED'):
            added += 1
        elif 'already has card' in result:
            skipped_card += 1
        else:
            skipped_no_point += 1

    print()
    print('=' * 55)
    print(f'  Cards added          : {added}')
    print(f'  Already had card     : {skipped_card}')
    print(f'  No insertion point   : {skipped_no_point}')
    print(f'  Total files checked  : {len(targets)}')
    if args.dry_run:
        print()
        print('  Run without --dry-run to apply all changes.')
    print('=' * 55)


if __name__ == '__main__':
    main()