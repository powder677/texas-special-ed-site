#!/usr/bin/env python3
"""
fix_page_issues.py
==================
Fixes all known structural and CSS issues across district pages.

WHAT IT FIXES:
  1. Injects missing CSS for .stacked-card, .btn-premium, .topic-tag etc (all pages)
  2. Repairs broken HTML structure — footer/content injected inside <main> or after </html>
  3. Removes bad grievance sales card (red card with placeholder Stripe link)
  4. Strips markdown ```html code fences left by Vertex AI (leadership pages)
  5. Adds missing All-Access bottom sales card where absent
  6. Fixes dropdown:hover display:block (was display:none)
  7. Ensures </body></html> exists at end of file

USAGE:
  Dry run:
    python fix_page_issues.py --districts-dir "C:\\...\\districts" --dry-run

  Live run:
    python fix_page_issues.py --districts-dir "C:\\...\\districts"

  Single page type only:
    python fix_page_issues.py --districts-dir "C:\\...\\districts" --page-type leadership
    (choices: ard, dyslexia, grievance, leadership, evaluation, all)
"""

import re
import shutil
import argparse
from pathlib import Path


# ─── MISSING CSS FOR OFFER BOXES ─────────────────────────────────────────────
# This block is missing from all district pages — the HTML exists but renders
# as unstyled because the style block never got these rules.

OFFER_BOX_CSS = """
  /* ── Premium Offer Cards ── */
  .premium-offers-container { margin: 30px 0 35px; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; background: #f8fafc; }
  .offers-header-badge { background: #0f172a; color: #d4af37; text-align: center; padding: 8px 16px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.12em; }
  .premium-offers-header { text-align: center; padding: 20px 20px 8px; }
  .premium-offers-header h2 { font-size: 1.3rem; color: #0f172a; margin-bottom: 6px; margin-top: 0; }
  .premium-offers-header p { color: #64748b; font-size: 0.9rem; margin: 0; }
  .stacked-card { background: #fff; border-top: 1px solid #e2e8f0; padding: 20px 24px; }
  .card-inner { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
  .card-main-content { flex: 1; min-width: 200px; }
  .card-checkout-zone { min-width: 150px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; border-left: 1px solid #e2e8f0; padding-left: 20px; }
  .topic-tag { display: inline-block; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 3px 10px; border-radius: 4px; margin-bottom: 8px; }
  .tag-gold    { background: #fdf4e3; color: #8a6914; }
  .tag-blue    { background: #e8edf5; color: #002868; }
  .tag-red     { background: #fde8eb; color: #c8102e; }
  .tag-purple  { background: #ede6f6; color: #5b3e96; }
  .tag-teal    { background: #e6f5f5; color: #0e7c7b; }
  .tag-slate   { background: #eef0f4; color: #475569; }
  .card-title   { font-size: 1.05rem; color: #0f172a; margin: 0 0 4px; }
  .card-tagline { font-size: 0.85rem; color: #c8102e; font-style: italic; font-weight: 600; margin-bottom: 8px; }
  .card-desc    { font-size: 0.87rem; color: #475569; line-height: 1.6; margin-bottom: 10px; }
  .card-bullets { list-style: none; padding: 0; margin: 0; }
  .card-bullets li { font-size: 0.82rem; color: #475569; padding: 3px 0 3px 18px; position: relative; }
  .card-bullets li::before { content: "✓"; position: absolute; left: 0; color: #0e7c7b; font-weight: 700; }
  .price-block  { text-align: center; }
  .price-label  { display: block; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; font-weight: 600; margin-bottom: 2px; }
  .price-amount { display: block; font-size: 1.5rem; font-weight: 700; color: #0f172a; }
  .btn-premium  { display: inline-block; background: #2563eb; color: #fff !important; padding: 10px 18px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 0.85rem; transition: background 0.2s; white-space: nowrap; margin-top: 4px; }
  .btn-premium:hover { background: #1d4ed8; }
  .border-gold   { border-left: 4px solid #d4af37; }
  .border-blue   { border-left: 4px solid #2563eb; }
  .border-red    { border-left: 4px solid #ef4444; }
  .border-purple { border-left: 4px solid #5b3e96; }
  .border-teal   { border-left: 4px solid #0e7c7b; }
  .border-slate  { border-left: 4px solid #475569; }
"""

# ─── ALL-ACCESS BOTTOM SALES CARD ────────────────────────────────────────────
ALL_ACCESS_CARD = """
<div class="sales-card" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);padding:32px;margin:40px 0;border-radius:8px;text-align:center;color:white;box-shadow:0 10px 15px -3px rgba(0,0,0,0.1);">
  <span style="background:#d4af37;color:#0f172a;padding:6px 16px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;">Most Popular</span>
  <h3 style="margin:20px 0 12px;color:#ffffff;font-size:1.6rem;">The &#34;Parent Protection&#34; All-Access Pass</h3>
  <p style="color:#e2e8f0;max-width:600px;margin:0 auto 24px;font-size:1.05rem;line-height:1.6;">Every toolkit in one bundle &#8212; ARD Prep, Behavior Defense, Dyslexia, ADHD, Autism Supplement, and the Accommodations Encyclopedia.</p>
  <a href="https://buy.stripe.com/3cIcN4a8l7Q4d0j7mBbbG0G" style="background:#d4af37;color:#0f172a;padding:16px 32px;text-decoration:none;border-radius:4px;font-weight:700;font-size:1.05rem;display:inline-block;">GET ALL 6 KITS FOR $97</a>
  <p style="margin-top:16px;font-size:0.85rem;color:#cbd5e1;">Instant Digital Access &#8226; Secure Stripe Checkout</p>
</div>"""

# ─── STANDARD FOOTER ─────────────────────────────────────────────────────────
STANDARD_FOOTER = """
<footer class="site-footer">
  <div class="footer-container">
    <div class="footer-about">
      <img alt="Texas Special Ed Logo" height="auto" src="/images/texasspecialed-logo.png" width="180"/>
      <p style="margin-top:10px;line-height:1.6;">Empowering Texas parents with guides, resources, and toolkits to navigate the Special Education and ARD process with confidence.</p>
    </div>
    <div class="footer-links">
      <h3>Quick Links</h3>
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/districts/index.html">School Districts</a></li>
        <li><a href="/resources/index.html">Free Resources</a></li>
        <li><a href="/store/index.html">Toolkits &amp; Guides</a></li>
        <li><a href="/blog/index.html">Parent Blog</a></li>
      </ul>
    </div>
    <div class="footer-links">
      <h3>Support</h3>
      <ul>
        <li><a href="/about/index.html">About Us</a></li>
        <li><a href="/contact/index.html">Contact</a></li>
        <li><a href="/disclaimer/index.html">Disclaimer</a></li>
        <li><a href="/privacy-policy">Privacy Policy</a></li>
        <li><a href="/terms-of-service">Terms of Service</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <p>&#169; 2026 Texas Special Education Resources. All rights reserved. Not affiliated with the TEA or any school district.</p>
  </div>
</footer>"""

STANDARD_CLOSE = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    var toggle = document.querySelector('.mobile-menu-toggle');
    var menu   = document.querySelector('.nav-menu');
    if (toggle && menu) {
        toggle.addEventListener('click', function() {
            menu.classList.toggle('active');
            toggle.setAttribute('aria-expanded', menu.classList.contains('active'));
        });
    }
    document.querySelectorAll('.dropdown-toggle').forEach(function(drop) {
        drop.addEventListener('click', function(e) {
            if (window.innerWidth <= 900) {
                e.preventDefault();
                this.parentElement.classList.toggle('active');
            }
        });
    });
    // Desktop hover for dropdowns
    document.querySelectorAll('.dropdown').forEach(function(d) {
        d.addEventListener('mouseenter', function() {
            if (window.innerWidth > 900) {
                var m = this.querySelector('.dropdown-menu');
                if (m) m.style.display = 'block';
            }
        });
        d.addEventListener('mouseleave', function() {
            if (window.innerWidth > 900) {
                var m = this.querySelector('.dropdown-menu');
                if (m) m.style.display = '';
            }
        });
    });
});
</script>
</body>
</html>"""


# ─── FIX FUNCTIONS ───────────────────────────────────────────────────────────

def inject_offer_box_css(content: str) -> tuple[str, bool]:
    """Add missing offer box CSS into the <style> block if not already present."""
    if 'stacked-card' in content and '.stacked-card' in content:
        return content, False  # already has CSS
    if '.stacked-card' not in content and 'stacked-card' in content:
        # Has HTML but no CSS — inject before </style>
        new = content.replace('</style>', OFFER_BOX_CSS + '\n</style>', 1)
        return new, True
    return content, False


def fix_dropdown_hover(content: str) -> tuple[str, bool]:
    """Fix dropdown:hover display:none → display:block."""
    pattern = r'(\.dropdown:hover\s+\.dropdown-menu\s*\{[^}]*?)display:\s*none'
    new = re.sub(pattern, r'\1display: block', content)
    changed = new != content
    # Same for .dropdown.active
    pattern2 = r'(\.dropdown\.active\s+\.dropdown-menu\s*\{[^}]*?)display:\s*none'
    new = re.sub(pattern2, r'\1display: block', new)
    return new, changed or new != content


def extract_main_content(content: str) -> str:
    """
    For broken files where footer/body/html tags appear before </main>:
    Extract everything between <main...> and the LAST </main>, 
    stripping any footer, script, body, html tags that snuck in.
    """
    # Find first <main...>
    main_open = re.search(r'<main\b[^>]*>', content)
    if not main_open:
        return content

    # Find LAST </main>
    last_main_close = content.rfind('</main>')
    if last_main_close == -1:
        return content

    inner = content[main_open.end():last_main_close]

    # Strip any footer block that crept in
    inner = re.sub(r'<footer\b.*?</footer>', '', inner, flags=re.DOTALL)
    # Strip </body>, </html>, <script data-cfasync...>, stray json-ld after </section>
    inner = re.sub(r'</body>\s*</html>', '', inner, flags=re.IGNORECASE)
    inner = re.sub(r'<script[^>]*cfasync[^>]*>.*?</script>', '', inner, flags=re.DOTALL)
    # Strip json-ld scripts that shouldn't be inside main
    inner = re.sub(r'<script type="application/ld\+json">.*?</script>', '', inner, flags=re.DOTALL)
    # Strip trailing whitespace-only lines
    inner = re.sub(r'\n\s*\n\s*\n', '\n\n', inner)

    return main_open.group(0) + inner + '\n</main>'


def fix_broken_structure(content: str) -> tuple[str, bool]:
    """
    Detect and fix files where the footer landed inside <main> due to 
    Vertex AI appending content after </html>.
    Broken signature: footer appears BEFORE the last </main>.
    """
    footer_pos   = content.find('<footer class="site-footer">')
    last_main    = content.rfind('</main>')
    first_main_close = content.find('</main>')

    if footer_pos == -1 or last_main == -1:
        return content, False

    # If footer appears before the last </main>, structure is broken
    if footer_pos > last_main:
        return content, False  # normal — footer after all main closes

    # ── BROKEN: reconstruct ──
    # 1. Everything before <main>
    main_open_match = re.search(r'<main\b[^>]*>', content)
    if not main_open_match:
        return content, False

    before_main = content[:main_open_match.start()]

    # 2. Rebuild clean main content
    clean_main = extract_main_content(content)

    # 3. Find the JSON-LD scripts that belong after main (before footer)
    # These come from after the last </main> in the broken file
    after_last_main = content[last_main + len('</main>'):]
    # Extract only the json-ld script blocks
    jsonld_scripts = re.findall(r'<script type="application/ld\+json">.*?</script>', after_last_main, re.DOTALL)
    jsonld_block   = '\n'.join(jsonld_scripts) if jsonld_scripts else ''

    # 4. Assemble correctly
    rebuilt = (
        before_main
        + clean_main
        + '\n'
        + (jsonld_block + '\n' if jsonld_block else '')
        + STANDARD_FOOTER
        + STANDARD_CLOSE
    )

    return rebuilt, True


def remove_bad_grievance_card(content: str) -> tuple[str, bool]:
    """
    Remove the red emergency sales card with placeholder Stripe link 
    that appears in grievance pages.
    """
    pattern = r'<div[^>]*class="sales-card"[^>]*style="[^"]*fee2e2[^"]*"[^>]*>.*?</div>'
    new = re.sub(pattern, '', content, flags=re.DOTALL)
    # Also catch any remaining YOUR_BEHAVIOR_LINK cards
    pattern2 = r'<div[^>]*>.*?YOUR_BEHAVIOR_LINK.*?</div>'
    new = re.sub(pattern2, '', new, flags=re.DOTALL)
    return new, new != content


def remove_code_fences(content: str) -> tuple[str, bool]:
    """Remove markdown ```html and ``` fences left by Vertex AI."""
    new = re.sub(r'```html\s*\n?', '', content)
    new = re.sub(r'\n?```\s*\n', '\n', new)
    new = re.sub(r'```', '', new)
    return new, new != content


def add_bottom_sales_card(content: str) -> tuple[str, bool]:
    """Add All-Access sales card before </main> if not already present."""
    if 'GET ALL 6 KITS FOR $97' in content or 'All-Access Pass' in content:
        return content, False
    if '3cIcN4a8l7Q4d0j7mBbbG0G' in content:
        return content, False
    new = content.replace('</main>', ALL_ACCESS_CARD + '\n</main>', 1)
    return new, True


def ensure_closing_tags(content: str) -> tuple[str, bool]:
    """Make sure file ends with </body></html>."""
    stripped = content.rstrip()
    if stripped.endswith('</html>'):
        return content, False
    # Remove any trailing partial closing and re-add clean ones
    stripped = re.sub(r'(</body>\s*</html>\s*)+$', '', stripped)
    new = stripped + '\n</body>\n</html>\n'
    return new, True


def fix_leadership_back_link(content: str) -> tuple[str, bool]:
    """Fix the back link in leadership pages: resources.html → index.html."""
    new = content.replace('href="resources.html"', 'href="/districts/abilene-isd/index.html"')
    # Generic fix for any district
    new = re.sub(r'href="resources\.html"', 'href="index.html"', new)
    return new, new != content


# ─── MAIN PROCESSOR ──────────────────────────────────────────────────────────

PAGE_FIXES = {
    # filename pattern → list of fix functions to apply
    'ard-process-guide':          ['css', 'dropdown', 'sales_card', 'closing'],
    'evaluation-child-find':      ['css', 'dropdown', 'sales_card', 'closing'],
    'dyslexia-services':          ['css', 'dropdown', 'structure', 'sales_card', 'closing'],
    'grievance-dispute-resolution':['css', 'dropdown', 'structure', 'bad_card', 'sales_card', 'closing'],
    'leadership-directory':       ['css', 'dropdown', 'code_fence', 'back_link', 'sales_card', 'closing'],
    'partners':                   ['css', 'dropdown', 'closing'],
    'index':                      ['css', 'dropdown', 'closing'],
}

def get_page_type(html_file: Path) -> str:
    stem = html_file.stem.lower()
    for key in PAGE_FIXES:
        if stem == key:
            return key
    return 'index' if stem == 'index' else 'unknown'


def process_file(f: Path, dry_run: bool, no_backup: bool, page_type_filter: str) -> list[str]:
    page_type = get_page_type(f)
    if page_type == 'unknown':
        return []

    if page_type_filter != 'all':
        # Map CLI filter to page type
        filter_map = {
            'ard': 'ard-process-guide',
            'dyslexia': 'dyslexia-services',
            'grievance': 'grievance-dispute-resolution',
            'leadership': 'leadership-directory',
            'evaluation': 'evaluation-child-find',
            'partners': 'partners',
        }
        if page_type != filter_map.get(page_type_filter, page_type_filter):
            return []

    fixes_to_run = PAGE_FIXES.get(page_type, [])
    if not fixes_to_run:
        return []

    try:
        content = f.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return [f'ERROR reading: {e}']

    original = content
    applied  = []

    for fix in fixes_to_run:
        if fix == 'css':
            content, changed = inject_offer_box_css(content)
            if changed: applied.append('injected offer box CSS')

        elif fix == 'dropdown':
            content, changed = fix_dropdown_hover(content)
            if changed: applied.append('fixed dropdown hover display:block')

        elif fix == 'structure':
            content, changed = fix_broken_structure(content)
            if changed: applied.append('rebuilt broken HTML structure (footer was inside main)')

        elif fix == 'bad_card':
            content, changed = remove_bad_grievance_card(content)
            if changed: applied.append('removed bad red sales card with placeholder link')

        elif fix == 'code_fence':
            content, changed = remove_code_fences(content)
            if changed: applied.append('removed markdown ```html code fences')

        elif fix == 'back_link':
            content, changed = fix_leadership_back_link(content)
            if changed: applied.append('fixed back link: resources.html → index.html')

        elif fix == 'sales_card':
            content, changed = add_bottom_sales_card(content)
            if changed: applied.append('added All-Access bottom sales card')

        elif fix == 'closing':
            content, changed = ensure_closing_tags(content)
            if changed: applied.append('added missing </body></html>')

    if not applied or content == original:
        return []

    if not dry_run:
        if not no_backup:
            shutil.copy2(f, f.with_suffix('.html.bak'))
        f.write_text(content, encoding='utf-8')

    return applied


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

def run(districts_dir: str, dry_run: bool, no_backup: bool, page_type: str):
    root = Path(districts_dir).resolve()

    if not root.exists():
        print(f'\nERROR: Directory not found: {root}\n')
        return

    print(f'\n{"="*64}')
    print(f'  Page Structure & CSS Fixer')
    print(f'{"="*64}')
    print(f'  Root   : {root}')
    print(f'  Mode   : {"DRY RUN" if dry_run else "LIVE"}')
    print(f'  Filter : {page_type}')
    print(f'{"="*64}\n')

    files = sorted(root.rglob('*.html'))
    if not files:
        print('  No HTML files found.\n')
        return

    print(f'  Scanning {len(files)} files...\n')

    total = fixed = skipped = 0
    for f in files:
        total += 1
        if '.bak' in f.name:
            continue

        changes = process_file(f, dry_run, no_backup, page_type)

        if not changes:
            skipped += 1
            continue

        fixed += 1
        rel = f.relative_to(root)
        print(f'  {rel}')
        for c in changes:
            print(f'    ✓ {c}')

    print(f'\n{"="*64}')
    print(f'  Files scanned : {total}')
    print(f'  Files updated : {fixed}')
    print(f'  Already OK    : {skipped}')
    print()
    if dry_run:
        print('  ℹ️  Dry run. Run without --dry-run to apply.')
    elif fixed:
        print(f'  ✅ Done. {fixed} files fixed.')
        if not no_backup:
            print('  💾 Originals backed up as .html.bak')
    print(f'{"="*64}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fix page structure and CSS issues across district pages.')
    parser.add_argument('--districts-dir', required=True)
    parser.add_argument('--dry-run',   action='store_true')
    parser.add_argument('--no-backup', action='store_true')
    parser.add_argument('--page-type', default='all',
                        choices=['all', 'ard', 'dyslexia', 'grievance', 'leadership', 'evaluation', 'partners'])
    args = parser.parse_args()
    run(args.districts_dir, args.dry_run, args.no_backup, args.page_type)