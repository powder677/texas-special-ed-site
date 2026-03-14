#!/usr/bin/env python3
"""
Replace old navbar with simplified version across all HTML pages
New nav: TEXAS SPECIAL ED | Districts | Spanish Districts | Parent Resources | 
Articles | Contact | Free ARD Checklist | Get Your Letter $25
"""

import sys
from pathlib import Path
import re

# New simplified navbar HTML
NEW_NAVBAR_HTML = '''<header class="site-header">
<nav aria-label="Main navigation" class="navbar" role="navigation">
<div class="nav-container">
<div class="nav-logo">
<a aria-label="Texas Special Ed Home" class="text-logo" href="/">
Texas <em>Special Ed</em>
</a>
</div>
<button aria-expanded="false" aria-label="Toggle menu" class="mobile-menu-toggle">
<span class="hamburger"></span>
<span class="hamburger"></span>
<span class="hamburger"></span>
</button>
<ul class="nav-menu">
<li class="nav-item"><a class="nav-link" href="/districts/index.html">Districts</a></li>
<li class="nav-item"><a class="nav-link" href="/districts/es-index.html">Spanish Districts</a></li>
<li class="nav-item"><a class="nav-link" href="/resources/index.html">Parent Resources</a></li>
<li class="nav-item"><a class="nav-link" href="/blog/index.html">Articles</a></li>
<li class="nav-item"><a class="nav-link" href="/contact/index.html">Contact</a></li>
<li class="nav-item nav-cta">
<a class="btn-outline" href="/resources/ard-checklist.pdf" target="_blank">Free ARD Checklist</a>
</li>
<li class="nav-item nav-cta" style="margin-left:8px;">
<a href="/resources/iep-letter/index.html" style="background:#d4af37;color:#0f172a;padding:10px 18px;border-radius:4px;font-weight:700;font-size:14px;text-decoration:none;font-family:'DM Sans',sans-serif;white-space:nowrap;">Get Your Letter — $25</a>
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

# Spanish version
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
<li class="nav-item"><a class="nav-link" href="/districts/es/index.html">Distritos en Español</a></li>
<li class="nav-item"><a class="nav-link" href="/resources/index.html">Recursos para Padres</a></li>
<li class="nav-item"><a class="nav-link" href="/blog/index.html">Artículos</a></li>
<li class="nav-item"><a class="nav-link" href="/contact/index.html">Contacto</a></li>
<li class="nav-item nav-cta">
<a class="btn-outline" href="/resources/ard-checklist.pdf" target="_blank">Lista de Verificación ARD</a>
</li>
<li class="nav-item nav-cta" style="margin-left:8px;">
<a href="/resources/iep-letter" style="background:#d4af37;color:#0f172a;padding:10px 18px;border-radius:4px;font-weight:700;font-size:14px;text-decoration:none;font-family:'DM Sans',sans-serif;white-space:nowrap;">Obtenga Su Carta — $25</a>
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


def replace_navbar(file_path, is_spanish=False):
    """Replace navbar in a single file."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has a navbar
        if '<header class="site-header">' not in content and '<nav' not in content:
            return False, "No navbar found"
        
        # Pattern to match the entire header/nav block
        # This matches from <header> to </header>
        pattern = re.compile(
            r'<header class="site-header">.*?</header>',
            re.DOTALL | re.IGNORECASE
        )
        
        if not pattern.search(content):
            return False, "No matching header found"
        
        # Choose the right navbar based on language
        new_navbar = NEW_NAVBAR_HTML_ES if is_spanish else NEW_NAVBAR_HTML
        
        # Replace
        new_content = pattern.sub(new_navbar, content)
        
        # Write back
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, "Updated"
        else:
            return False, "No changes needed"
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def process_directory(base_path, exclude_es=False):
    """Process all HTML files in directory."""
    
    base_path = Path(base_path)
    
    if not base_path.exists():
        print(f"❌ Error: {base_path} does not exist")
        return
    
    # Find all HTML files
    html_files = list(base_path.rglob('*.html'))
    
    if not html_files:
        print(f"❌ No HTML files found in {base_path}")
        return
    
    # Filter out /es/ paths if exclude_es is True
    if exclude_es:
        original_count = len(html_files)
        html_files = [f for f in html_files if '/es/' not in str(f)]
        excluded_count = original_count - len(html_files)
        if excluded_count > 0:
            print(f"ℹ️  Excluded {excluded_count} files from /es/ directory")
    
    print(f"Found {len(html_files)} HTML files to process")
    print("=" * 70)
    
    english_updated = 0
    spanish_updated = 0
    skipped = 0
    errors = 0
    
    for html_file in html_files:
        # Determine if Spanish or English based on path
        is_spanish = '/es/' in str(html_file) or str(html_file).endswith('index-es.html')
        
        success, message = replace_navbar(html_file, is_spanish)
        
        if success:
            if is_spanish:
                spanish_updated += 1
                lang = "ES"
            else:
                english_updated += 1
                lang = "EN"
            
            # Only show first 100 to avoid spam
            if (english_updated + spanish_updated) <= 100:
                print(f"✓ [{lang}] {html_file.name}: {message}")
        else:
            if "Error" in message:
                errors += 1
                print(f"✗ {html_file.name}: {message}")
            else:
                skipped += 1
    
    print("=" * 70)
    print(f"\n✓ English pages updated: {english_updated}")
    print(f"✓ Spanish pages updated: {spanish_updated}")
    print(f"○ Skipped: {skipped}")
    if errors > 0:
        print(f"✗ Errors: {errors}")
    print("\nDone!")


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("REPLACE NAVBAR SITE-WIDE")
        print("=" * 70)
        print("\nUsage:")
        print("  python replace_navbar.py <directory> [--exclude-es]")
        print("\nExamples:")
        print("  python replace_navbar.py .")
        print("  python replace_navbar.py districts")
        print("  python replace_navbar.py districts --exclude-es")
        print("\nOptions:")
        print("  --exclude-es    Skip all files in /es/ directories")
        print("\nNew navbar structure:")
        print("  • Districts")
        print("  • Spanish Districts (NEW)")
        print("  • Parent Resources")
        print("  • Articles")
        print("  • Contact")
        print("  • Free ARD Checklist")
        print("  • Get Your Letter — $25")
        print("\n(No more dropdown menu)")
        print("=" * 70)
        sys.exit(1)
    
    base_path = sys.argv[1]
    exclude_es = '--exclude-es' in sys.argv
    
    if exclude_es:
        print("🚫 Excluding /es/ directories from processing\n")
    
    process_directory(base_path, exclude_es)


if __name__ == '__main__':
    main()