#!/usr/bin/env python3
"""
Replace navbar ONLY on Spanish (/es/) pages
"""

import sys
from pathlib import Path
import re

# Spanish navbar - UPDATE THE LETTER LINK BELOW AS NEEDED
NEW_NAVBAR_HTML_ES = '''<header class="site-header">
<nav aria-label="Navegación principal" class="navbar" role="navigation">
<div class="nav-container">
<div class="nav-logo">
<a aria-label="Texas Special Ed Inicio" class="text-logo" href="/districts/es/index.html">
Texas <em>Special Ed</em>
</a>
</div>
<button aria-expanded="false" aria-label="Alternar menú" class="mobile-menu-toggle">
<span class="hamburger"></span>
<span class="hamburger"></span>
<span class="hamburger"></span>
</button>
<ul class="nav-menu">
<li class="nav-item"><a class="nav-link" href="/districts/index.html">Distritos</a></li>
<li class="nav-item"><a class="nav-link" href="/districts/es-index.html">Distritos en Español</a></li>
<li class="nav-item"><a class="nav-link" href="/resources/index.html">Recursos para Padres</a></li>
<li class="nav-item"><a class="nav-link" href="/blog/index.html">Artículos</a></li>
<li class="nav-item"><a class="nav-link" href="/contact/index.html">Contacto</a></li>
<li class="nav-item nav-cta">
<a class="btn-outline" href="/resources/ard-checklist.pdf" target="_blank">Lista de Verificación ARD</a>
</li>
<li class="nav-item nav-cta" style="margin-left:8px;">
<a href="/resources/iep-letter-spanish/index.html" style="background:#d4af37;color:#0f172a;padding:10px 18px;border-radius:4px;font-weight:700;font-size:14px;text-decoration:none;font-family:'DM Sans',sans-serif;white-space:nowrap;">Obtenga Su Carta — $25</a>
</li>
<li class="nav-item nav-cta" style="margin-left:8px;">
<a href="/" style="background:#fff;color:#1a56db;padding:10px 18px;border-radius:4px;font-weight:700;font-size:14px;text-decoration:none;font-family:'DM Sans',sans-serif;white-space:nowrap;border:2px solid #1a56db;">English</a>
</li>
</ul>
</div>
</nav>
</header>
<script>
document.addEventListener('DOMContentLoaded', function() {
   const toggle = document.querySelector('.mobile-menu-toggle');
   const menu = document.querySelector('.nav-menu');
   if (toggle && menu) {
      toggle.addEventListener('click', function() {
         menu.classList.toggle('active');
         const expanded = toggle.getAttribute('aria-expanded') === 'true';
         toggle.setAttribute('aria-expanded', !expanded);
      });
   }
});
</script>'''


def replace_navbar(file_path):
    """Replace navbar in a single file."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has a navbar
        if '<header class="site-header">' not in content and '<nav' not in content:
            return False, "No navbar found"
        
        # Pattern to match the entire header/nav block
        pattern = re.compile(
            r'<header class="site-header">.*?</header>',
            re.DOTALL | re.IGNORECASE
        )
        
        if not pattern.search(content):
            return False, "No matching header found"
        
        # Replace with Spanish navbar
        new_content = pattern.sub(NEW_NAVBAR_HTML_ES, content)
        
        # Write back
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, "Updated"
        else:
            return False, "No changes needed"
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def process_directory(base_path):
    """Process all HTML files in /es/ directories."""
    
    base_path = Path(base_path)
    
    if not base_path.exists():
        print(f"❌ Error: {base_path} does not exist")
        return
    
    # Find all HTML files
    all_files = list(base_path.rglob('*.html'))
    
    # Filter to only /es/ files
    html_files = [f for f in all_files if '/es/' in str(f)]
    
    if not html_files:
        print(f"❌ No Spanish (/es/) HTML files found in {base_path}")
        return
    
    print(f"🇪🇸 Found {len(html_files)} Spanish files to process")
    print("=" * 70)
    
    updated = 0
    skipped = 0
    errors = 0
    
    for html_file in html_files:
        success, message = replace_navbar(html_file)
        
        if success:
            updated += 1
            # Only show first 100 to avoid spam
            if updated <= 100:
                print(f"✓ {html_file.name}: {message}")
        else:
            if "Error" in message:
                errors += 1
                print(f"✗ {html_file.name}: {message}")
            else:
                skipped += 1
    
    print("=" * 70)
    print(f"\n✓ Spanish pages updated: {updated}")
    print(f"○ Skipped: {skipped}")
    if errors > 0:
        print(f"✗ Errors: {errors}")
    print("\nDone!")


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("REPLACE NAVBAR - SPANISH PAGES ONLY")
        print("=" * 70)
        print("\nUsage:")
        print("  python replace_navbar_spanish.py <directory>")
        print("\nExamples:")
        print("  python replace_navbar_spanish.py .")
        print("  python replace_navbar_spanish.py districts")
        print("\nThis will ONLY update files in /es/ directories")
        print("\n⚠️  BEFORE RUNNING: Edit line 29 in this script to set your letter link!")
        print("=" * 70)
        sys.exit(1)
    
    # Check if placeholder link is still there
    if "YOUR_LETTER_LINK_HERE" in NEW_NAVBAR_HTML_ES:
        print("\n⚠️  WARNING: Letter link is still set to 'YOUR_LETTER_LINK_HERE'")
        print("Please edit line 29 in this script to set the correct link")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    base_path = sys.argv[1]
    process_directory(base_path)


if __name__ == '__main__':
    main()