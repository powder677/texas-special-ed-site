import os
import re

NEW_NAVBAR = """<nav aria-label="Main navigation" class="navbar" role="navigation">
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
<li class="nav-item"><a class="nav-link" href="/resources/index.html">Parent Resources</a></li>
<li class="nav-item"><a class="nav-link" href="/blog/index.html">Blog</a></li>
<li class="nav-item"><a class="nav-link" href="/about/index.html">About</a></li>
<li class="nav-item"><a class="nav-link" href="/contact/index.html">Contact</a></li>
<li class="nav-item nav-cta">
    <a class="btn-outline" href="/resources/ard-checklist.pdf" target="_blank">Free ARD Checklist</a>
</li>
</ul>
</div>
</nav>"""

SKIP_DIRS = {'.git', '_canonical_backups', '_trailing_slash_backups', 'districts_updated'}

def sync_navbars():
    # Targets <nav> elements specifically possessing the 'navbar' class
    nav_pattern = re.compile(r'<nav[^>]*class=["\'][^>]*navbar[^>]*["\'][^>]*>.*?</nav>', re.DOTALL | re.IGNORECASE)
    updated_count = 0

    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Apply the replacement
                    new_content = re.sub(nav_pattern, NEW_NAVBAR, content)

                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        updated_count += 1
                        print(f"Updated Navbar in: {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    print(f"\n✅ Success! Synchronized the Navbar across {updated_count} files.")

if __name__ == "__main__":
    sync_navbars()