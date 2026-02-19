import os
from bs4 import BeautifulSoup

# Define the root directory where the district folders are located
DISTRICTS_DIR = 'districts'

# The specific internal pages we want to update in every district folder
TARGET_PAGES = [
    'resources.html',
    'dyslexia-services.html',
    'evaluation-child-find.html',
    'grievance-dispute-resolution.html',
    'leadership-directory.html',
    'ard-process-guide.html'
]

# 1. NEW STYLES (Includes layout fixes, container fix, and tightened footer)
NEW_CSS = """
  /* Base Styles */
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1e293b; background: #fff; line-height: 1.6; }
  
  /* Typography */
  h1 { font-size: 2.25rem; margin-bottom: 20px; color: #0f172a; }
  h2 { font-size: 1.5rem; margin: 30px 0 10px; color: #0f172a; }
  h3 { font-size: 1.2rem; margin: 20px 0 8px; color: #0f172a; }
  p { margin-bottom: 14px; color: #374151; }
  a { color: #2563eb; }

  /* Layout Containers */
  .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; min-height: 50vh; }
  
  /* Navbar (Fixed - No longer stuck) */
  .site-header { background: #0f172a; padding: 14px 0; position: relative; z-index: 100; }
  .nav-container { max-width: 1100px; margin: 0 auto; padding: 0 20px; display: flex; align-items: center; justify-content: space-between; width: 100%; }
  .nav-logo img { height: auto; width: 200px; display: block; }
  .nav-menu { display: flex; list-style: none; gap: 24px; align-items: center; margin: 0; padding: 0; }
  .nav-link { color: #fff; text-decoration: none; font-size: 0.95rem; font-weight: 500; transition: opacity 0.2s; }
  .nav-link:hover { opacity: 0.8; }
  
  /* Dropdown Styles */
  .dropdown { position: relative; }
  .dropdown-menu { display: none; position: absolute; background: #fff; padding: 10px 0; border-radius: 6px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); top: 100%; left: 0; min-width: 220px; list-style: none; }
  .dropdown:hover .dropdown-menu { display: block; }
  .dropdown-menu a { color: #1e293b; text-decoration: none; padding: 10px 20px; display: block; font-size: 0.9rem; }
  .dropdown-menu a:hover { background: #f1f5f9; color: #2563eb; }
  .dropdown-divider { height: 1px; background: #e2e8f0; margin: 8px 0; }
  .dropdown-arrow { font-size: 0.7rem; margin-left: 4px; vertical-align: middle; }

  /* Buttons */
  .button-primary { background: #2563eb; color: #fff; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 0.9rem; transition: background 0.2s; }
  .button-primary:hover { background: #1d4ed8; }
  
  /* Mobile Menu Toggle */
  .mobile-menu-toggle { display: none; background: transparent; border: none; cursor: pointer; padding: 5px; }
  .hamburger { display: block; width: 25px; height: 3px; background: #fff; margin: 5px 0; border-radius: 2px; }

  /* Internal Page Content Areas */
  .content-section { background: #f8fafc; border: 1px solid #e2e8f0; padding: 30px; border-radius: 8px; margin-bottom: 30px; }
  ul.custom-list { list-style: none; margin-bottom: 20px; padding-left: 0; }
  ul.custom-list li { margin-bottom: 10px; padding-left: 24px; position: relative; }
  ul.custom-list li::before { content: "•"; color: #2563eb; font-weight: bold; position: absolute; left: 0; }

  /* Tightened Footer */
  .site-footer { background: #0f172a; color: #94a3b8; padding: 40px 20px 20px; margin-top: 50px; font-size: 0.9rem; }
  .footer-container { max-width: 1100px; margin: 0 auto; display: flex; flex-wrap: wrap; gap: 30px; justify-content: space-between; }
  .footer-about { flex: 2; min-width: 250px; }
  .footer-about img { margin-bottom: 12px; }
  .footer-links { flex: 1; min-width: 150px; }
  .footer-links h3 { color: #fff; margin-bottom: 12px; font-size: 1.05rem; }
  .footer-links ul { list-style: none; padding: 0; }
  .footer-links ul li { margin-bottom: 8px; }
  .footer-links ul a { color: #94a3b8; text-decoration: none; transition: color 0.2s; }
  .footer-links ul a:hover { color: #fff; }
  .footer-bottom { max-width: 1100px; margin: 25px auto 0; padding-top: 15px; border-top: 1px solid #334155; text-align: center; font-size: 0.85rem; }

  @media (max-width: 900px) {
    .nav-menu { display: none; flex-direction: column; width: 100%; position: absolute; top: 100%; left: 0; background: #0f172a; padding: 20px 0; border-top: 1px solid #1e293b; }
    .nav-menu.active { display: flex; }
    .nav-item { width: 100%; text-align: center; }
    .nav-link { display: block; padding: 10px; }
    .mobile-menu-toggle { display: block; }
    .dropdown-menu { position: static; box-shadow: none; background: #1e293b; display: none; margin-top: 10px; padding: 10px 0; }
    .dropdown.active .dropdown-menu { display: block; }
    .dropdown-menu a { color: #e2e8f0; }
    .dropdown-menu a:hover { background: #334155; color: #fff; }
    .nav-cta { margin-top: 15px; }
  }
"""

# 2. NEW HEADER (Freed from container)
NEW_HEADER = """
<header class="site-header">
  <nav aria-label="Main navigation" class="navbar" role="navigation">
    <div class="nav-container">
      <div class="nav-logo">
        <a aria-label="Texas Special Ed Home" href="/">
          <img alt="Texas Special Ed" height="auto" src="/images/texasspecialed-logo.png" width="200"/>
        </a>
      </div>
      <button aria-expanded="false" aria-label="Toggle menu" class="mobile-menu-toggle">
        <span class="hamburger"></span>
        <span class="hamburger"></span>
        <span class="hamburger"></span>
      </button>
      <ul class="nav-menu">
        <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
        <li class="nav-item dropdown">
          <a aria-haspopup="true" class="nav-link dropdown-toggle" href="/districts/index.html">Districts <span class="dropdown-arrow">▼</span></a>
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
            <li><a class="view-all-link" href="/districts/index.html">View All 120+ Districts →</a></li>
          </ul>
        </li>
        <li class="nav-item"><a class="nav-link" href="/resources/index.html">Free Resources</a></li>
        <li class="nav-item"><a class="nav-link" href="/store/index.html">Toolkits</a></li>
        <li class="nav-item"><a class="nav-link" href="/blog/index.html">Blog</a></li>
        <li class="nav-item"><a class="nav-link" href="/about/index.html">About</a></li>
        <li class="nav-item"><a class="nav-link" href="/contact/index.html">Contact</a></li>
        <li class="nav-item nav-cta"><a class="button-primary" href="/resources/ard-checklist.pdf" target="_blank">Free ARD Checklist</a></li>
      </ul>
    </div>
  </nav>
</header>
"""

# 3. NEW FOOTER (Tightened spacing)
NEW_FOOTER = """
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
    <p>© 2026 Texas Special Education Resources. All rights reserved. Not affiliated with the TEA or any school district.</p>
  </div>
</footer>
"""

# 4. NAVBAR JS LOGIC
NAV_JS = """
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
</script>
"""

def process_internal_pages():
    if not os.path.exists(DISTRICTS_DIR):
        print(f"Error: Directory '{DISTRICTS_DIR}' not found. Run this from your project root.")
        return

    updated_count = 0
    
    # Loop through every sub-folder in /districts/
    for district_folder in os.listdir(DISTRICTS_DIR):
        district_path = os.path.join(DISTRICTS_DIR, district_folder)
        
        # Skip files, we only want directories
        if not os.path.isdir(district_path):
            continue
            
        # Loop through the specific internal pages we want to target
        for target_page in TARGET_PAGES:
            filepath = os.path.join(district_path, target_page)
            
            # If the page exists, let's parse and update it
            if os.path.exists(filepath):
                print(f"Surgically updating {filepath}...")
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                
                # 1. SWAP STYLES
                style_tag = soup.find('style')
                new_style_soup = BeautifulSoup(f"<style>{NEW_CSS}</style>", 'html.parser')
                if style_tag:
                    style_tag.replace_with(new_style_soup)
                elif soup.head:
                    soup.head.append(new_style_soup)

                # 2. SWAP HEADER
                header_tag = soup.find('header')
                new_header_soup = BeautifulSoup(NEW_HEADER, 'html.parser')
                if header_tag:
                    header_tag.replace_with(new_header_soup)
                elif soup.body:
                    soup.body.insert(0, new_header_soup)

                # 3. SWAP FOOTER
                footer_tag = soup.find('footer')
                new_footer_soup = BeautifulSoup(NEW_FOOTER, 'html.parser')
                if footer_tag:
                    footer_tag.replace_with(new_footer_soup)
                elif soup.body:
                    soup.body.append(new_footer_soup)

                # 4. INJECT JS (if missing)
                html_str = str(soup)
                if 'mobile-menu-toggle' not in html_str or 'DOMContentLoaded' not in html_str:
                    js_soup = BeautifulSoup(NAV_JS, 'html.parser')
                    if soup.body:
                        soup.body.append(js_soup)

                # Save the successfully manipulated file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                    
                updated_count += 1
                
    print(f"\n✅ Operation Complete! Surgically updated the layout on {updated_count} internal pages.")

if __name__ == "__main__":
    process_internal_pages()