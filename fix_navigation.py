import os
import re

# Set your exact base directory path for the districts
BASE_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"

# The restored main header navigation (with the dropdown included)
NEW_NAV_MENU = r"""<ul class="nav-menu">
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
<li class="nav-item nav-cta">
<a class="btn-outline" href="/resources/ard-checklist.pdf" target="_blank">Free ARD Checklist</a>
</li>
</ul>"""

def get_district_name(folder_name):
    words = folder_name.split('-')
    capitalized_words = [w.upper() if w.lower() in ['isd', 'cisd'] else w.capitalize() for w in words]
    return " ".join(capitalized_words)

# This generates the gray sub-page menu using proper RELATIVE links
def generate_silo_nav(district_name, current_file):
    links = [
        ("index.html", "District Home"),
        ("ard-process-guide.html", "ARD Guide"),
        ("evaluation-child-find.html", "Evaluations (FIE)"),
        ("dyslexia-services.html", "Dyslexia / 504"),
        ("grievance-dispute-resolution.html", "Dispute Resolution"),
        ("leadership-directory.html", "Staff Directory"),
        ("partners.html", "Providers & Support")
    ]
    
    nav_html = f'<div class="silo-nav" style="background-color: #e9ecef; padding: 14px 20px; border-radius: 8px; margin: 20px 0 30px; font-size: 15px; font-family: \'DM Sans\', sans-serif; display: flex; flex-wrap: wrap; gap: 16px; align-items: center; border-left: 4px solid #6c757d;">\n'
    nav_html += f'    <strong style="color: #334155;">{district_name} Resources:</strong>\n'
    
    link_strings = []
    for href, text in links:
        if href == current_file:
            # Bolds the current page you are on
            link_strings.append(f'    <a href="{href}" style="text-decoration: none; color: #2563eb; font-weight: 800;">{text}</a>')
        else:
            link_strings.append(f'    <a href="{href}" style="text-decoration: none; color: #2563eb; font-weight: 500;">{text}</a>')
            
    nav_html += " •\n".join(link_strings) + "\n</div>"
    return nav_html

def main():
    if not os.path.exists(BASE_DIR):
        print(f"Error: Could not find directory at {BASE_DIR}")
        return

    count = 0
    
    # Regex to safely target the top header menu and the gray sub-menu
    nav_pattern = re.compile(r'<ul\s+class=["\']nav-menu["\']>.*?(</div>\s*</nav>)', re.IGNORECASE | re.DOTALL)
    silo_pattern = re.compile(r'<div\s+class=["\']silo-nav["\'].*?</div>', re.IGNORECASE | re.DOTALL)

    for root, dirs, files in os.walk(BASE_DIR):
        # Skip the parent "districts" directory so we only edit individual ISD folders
        if root == BASE_DIR:
            continue
            
        folder_name = os.path.basename(root)
        district_name = get_district_name(folder_name)

        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    new_content = content
                    
                    # 1. Restore the Dropdown Nav Menu at the top
                    if nav_pattern.search(new_content):
                        new_content = nav_pattern.sub(NEW_NAV_MENU + r'\n\1', new_content)
                        
                    # 2. Fix the Sub-Page Links (ARD, Eval, etc.) to be relative so they work locally
                    if silo_pattern.search(new_content):
                        new_silo = generate_silo_nav(district_name, file)
                        new_content = silo_pattern.sub(new_silo, new_content)
                        
                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        count += 1
                        
                except Exception as e:
                    print(f"Skipped {filepath}: {e}")

    print(f"\nSuccess! Repaired navigation links on {count} pages.")

if __name__ == "__main__":
    main()