import os
import re

# =========================================================
# NEW COMPONENTS
# =========================================================

NAVBAR_HTML = """<nav class="navbar" role="navigation" aria-label="Main navigation">
   <div class="nav-container">
      <div class="nav-logo">
         <a href="/" aria-label="Texas Special Ed Home">
            <img src="/images/texasspecialed-logo.png" alt="Texas Special Ed" width="200" height="auto">
         </a>
      </div>
      <button class="mobile-menu-toggle" aria-label="Toggle menu" aria-expanded="false">
         <span class="hamburger"></span>
         <span class="hamburger"></span>
         <span class="hamburger"></span>
      </button>
      <ul class="nav-menu">
         <li class="nav-item"><a href="/" class="nav-link">Home</a></li>
         <li class="nav-item dropdown">
            <a href="/districts/index.html" class="nav-link dropdown-toggle" aria-haspopup="true">Districts <span class="dropdown-arrow">▼</span></a>
            <ul class="dropdown-menu">
               <li><a href="/districts/index.html"><strong>Directory: All Districts</strong></a></li>
               <li class="dropdown-divider"></li>
               <li><a href="/districts/houston-isd/index.html">Houston ISD</a></li>
               <li><a href="/districts/dallas-isd/index.html">Dallas ISD</a></li>
               <li><a href="/districts/austin-isd/index.html">Austin ISD</a></li>
               <li><a href="/districts/cypress-fairbanks-isd/index.html">Cypress-Fairbanks ISD</a></li>
               <li><a href="/districts/katy-isd/index.html">Katy ISD</a></li>
               <li><a href="/districts/frisco-isd/index.html">Frisco ISD</a></li>
               <li><a href="/districts/plano-isd/index.html">Plano ISD</a></li>
               <li><a href="/districts/round-rock-isd/index.html">Round Rock ISD</a></li>
               <li class="dropdown-divider"></li>
               <li><a href="/districts/index.html" class="view-all-link">View All 120+ Districts →</a></li>
            </ul>
         </li>
         <li class="nav-item"><a href="/resources/index.html" class="nav-link">Free Resources</a></li>
         <li class="nav-item"><a href="/store/index.html" class="nav-link">Toolkits</a></li>
         <li class="nav-item"><a href="/blog/index.html" class="nav-link">Blog</a></li>
         <li class="nav-item"><a href="/about/index.html" class="nav-link">About</a></li>
         <li class="nav-item"><a href="/contact/index.html" class="nav-link">Contact</a></li>
         <li class="nav-item nav-cta"><a href="/resources/ard-checklist.pdf" class="button-primary" target="_blank">Free ARD Checklist</a></li>
      </ul>
   </div>
</nav>"""

FOOTER_HTML = """<footer class="site-footer">
   <div class="footer-container">
      <div class="footer-about">
         <img src="/images/texasspecialed-logo.png" alt="Texas Special Ed Logo" width="180" height="auto">
         <p>Empowering Texas parents with guides, resources, and toolkits to navigate the Special Education and ARD process with confidence.</p>
      </div>
      <div class="footer-links">
         <h3>Quick Links</h3>
         <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/districts/index.html">School Districts</a></li>
            <li><a href="/resources/index.html">Free Resources</a></li>
            <li><a href="/store/index.html">Toolkits & Guides</a></li>
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
      <p>&copy; 2026 Texas Special Education Resources. All rights reserved. Not affiliated with the TEA or any school district.</p>
   </div>
</footer>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.querySelector('.mobile-menu-toggle');
    const menu = document.querySelector('.nav-menu');
    if(toggle && menu) {
        toggle.addEventListener('click', function() {
            menu.classList.toggle('active');
            const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
            toggle.setAttribute('aria-expanded', !isExpanded);
        });
    }
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(drop => {
        drop.addEventListener('click', function(e) {
            if (window.innerWidth <= 900) {
                e.preventDefault();
                this.parentElement.classList.toggle('active');
            }
        });
    });
});
</script>"""

# =========================================================
# MAIN SCRIPT
# =========================================================

def fix_site():
    print("Starting site cleanup and error check...")
    
    # 1. Update the base component files just in case the build script uses them later
    with open('navbar.json', 'w', encoding='utf-8') as f:
        f.write(NAVBAR_HTML)
    with open('footer.json', 'w', encoding='utf-8') as f:
        f.write(FOOTER_HTML)
        
    files_processed = 0
    missing_nav = []
    missing_footer = []
    links_fixed = 0

    # 2. Walk through every HTML file in the project
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_content = content
                
                # --- A. Inject Style.css ---
                if '<head>' in content and 'style.css' not in content:
                    content = content.replace('</head>', '    <link rel="stylesheet" href="/style.css">\n</head>')

                # --- B. Replace Navbar ---
                # Matches <nav ...> ... </nav> across multiple lines
                nav_pattern = re.compile(r'<nav[^>]*>.*?</nav>', re.DOTALL)
                if nav_pattern.search(content):
                    content = nav_pattern.sub(lambda m: NAVBAR_HTML, content, count=1)
                else:
                    # Fallback: if no nav, inject after <body>
                    if '<body>' in content:
                        content = content.replace('<body>', f'<body>\n{NAVBAR_HTML}')
                    else:
                        missing_nav.append(filepath)

                # --- C. Replace Footer ---
                # Matches <footer ...> ... </footer> across multiple lines
                footer_pattern = re.compile(r'<footer[^>]*>.*?</footer>', re.DOTALL)
                if footer_pattern.search(content):
                    content = footer_pattern.sub(lambda m: FOOTER_HTML, content, count=1)
                else:
                    # Fallback: if no footer, inject before </body>
                    if '</body>' in content:
                        content = content.replace('</body>', f'{FOOTER_HTML}\n</body>')
                    else:
                        missing_footer.append(filepath)

                # --- D. Fix District Index Links ---
                # Determine if this file is inside a specific district folder
                parts = filepath.replace('\\', '/').split('/')
                if 'districts' in parts:
                    dist_idx = parts.index('districts')
                    # Ensure we are inside a specific district (e.g. /districts/katy-isd/)
                    if dist_idx + 1 < len(parts):
                        district_slug = parts[dist_idx + 1]
                        
                        # Only run link fix if it's a real folder, not the main index.html
                        if district_slug != 'index.html':
                            pages_to_fix = [
                                'ard-process-guide', 'dyslexia-services', 
                                'evaluation-child-find', 'grievance-dispute-resolution', 
                                'leadership-directory', 'resources'
                            ]
                            
                            for page in pages_to_fix:
                                # Find bad links like href="/districts/ard-process-guide.html"
                                bad_link_pattern = rf'href=["\']/districts/{page}(?:\.html|)["\']'
                                correct_link = f'href="/districts/{district_slug}/{page}.html"'
                                
                                # Count matches to report
                                matches = len(re.findall(bad_link_pattern, content))
                                if matches > 0:
                                    links_fixed += matches
                                    content = re.sub(bad_link_pattern, correct_link, content)

                # --- E. Save if modified ---
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    files_processed += 1

    # =========================================================
    # ERROR REPORTING
    # =========================================================
    print("-" * 40)
    print(f"✅ Cleanup Complete! Modified {files_processed} HTML files.")
    print(f"🔗 Fixed {links_fixed} broken routing links inside district folders.")
    
    if missing_nav:
        print("\n⚠️ WARNING: Could not find <nav> tag or <body> tag to inject navbar in these files:")
        for m in missing_nav[:5]: print(f"  - {m}")
        if len(missing_nav) > 5: print(f"  ...and {len(missing_nav)-5} more.")
            
    if missing_footer:
        print("\n⚠️ WARNING: Could not find <footer> tag or </body> tag to inject footer in these files:")
        for m in missing_footer[:5]: print(f"  - {m}")
        if len(missing_footer) > 5: print(f"  ...and {len(missing_footer)-5} more.")

if __name__ == "__main__":
    fix_site()