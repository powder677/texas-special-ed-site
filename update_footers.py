import os
from bs4 import BeautifulSoup, Comment

# The new standardized footer
NEW_FOOTER_HTML = """<footer class="site-footer">
<div class="footer-container">
<div class="footer-about">
<img alt="Texas Special Ed Logo" height="auto" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';" src="/images/texasspecialed-logo.png" width="160"/>
<span style="display:none; font-family:'Playfair Display',serif; font-size:1.1rem; font-weight:800; color:#fff;">Texas Special Ed</span>
<p style="margin-top:0.75rem;">Empowering Texas parents with guides, resources, and toolkits to navigate the Special Education and ARD process with confidence.</p>
</div>
<div class="footer-col">
<h3>Quick Links</h3>
<ul>
<li><a href="/">Home</a></li>
<li><a href="/districts/index.html">Browse Districts</a></li>
<li><a href="/resources/index.html">Parent Resources</a></li>
<li><a href="/blog/index.html">Blog &amp; Articles</a></li>
<li><a href="/about/index.html">About Us</a></li>
<li><a href="/contact/index.html">Contact Us</a></li>
</ul>
</div>
<div class="footer-col">
<h3>Popular Districts</h3>
<ul>
<li><a href="/districts/round-rock-isd/index.html">Round Rock ISD</a></li>
<li><a href="/districts/frisco-isd/index.html">Frisco ISD</a></li>
<li><a href="/districts/plano-isd/index.html">Plano ISD</a></li>
<li><a href="/districts/lewisville-isd/index.html">Lewisville ISD</a></li>
<li><a href="/districts/conroe-isd/index.html">Conroe ISD</a></li>
<li><a href="/districts/index.html">View All Districts →</a></li>
</ul>
</div>
<div class="footer-col">
<h3>Free Resources</h3>
<ul>
<li><a href="/resources/ard-checklist.pdf" target="_blank">ARD Meeting Checklist</a></li>
<li><a href="/resources/evaluation-request-letter.pdf" target="_blank">Evaluation Request Letter</a></li>
<li><a href="/resources/iep-goal-tracker.pdf" target="_blank">IEP Goal Tracker</a></li>
<li><a href="/resources/parent-rights-guide.pdf" target="_blank">Parent Rights Guide</a></li>
</ul>
</div>
</div>
<div class="footer-bottom">
<p>© 2026 Texas Special Education Resources. All rights reserved. Not affiliated with the TEA or any school district.</p>
</div>
</footer>"""

def replace_footer(root_dir):
    updated_count = 0
    
    # Parse the new footer so BeautifulSoup can insert it cleanly
    new_footer_soup = BeautifulSoup(NEW_FOOTER_HTML, 'html.parser')
    # Extract the elements to inject (the comment and the footer tag)
    elements_to_inject = list(new_footer_soup.body.children) if new_footer_soup.body else list(new_footer_soup.children)
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Safely skip backup directories to prevent clutter
        if '_backup' in dirpath.lower() or '.git' in dirpath:
            continue

        for filename in filenames:
            if filename.endswith('.html'):
                filepath = os.path.join(dirpath, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Load the HTML document
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Check if it has a body tag (if not, it might be a partial/fragment we shouldn't edit)
                if not soup.body:
                    continue

                # 1. Find and destroy ALL existing footers
                existing_footers = soup.find_all('footer')
                for footer in existing_footers:
                    # Also look for any immediate preceding comments that say "FOOTER" to clean them up
                    prev_node = footer.previous_sibling
                    if isinstance(prev_node, Comment) and 'FOOTER' in prev_node.string.upper():
                        prev_node.extract()
                    footer.decompose()

                # 2. Inject the new standardized footer immediately inside the closing </body> tag
                # We do this by appending it to the body tag
                for el in elements_to_inject:
                    soup.body.append(el.__copy__()) # Copy the element to avoid mutating the original parsed snippet
                
                # 3. Write the fixed file back
                # Using str(soup) preserves the rest of the original HTML layout
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                
                print(f"✅ Unified footer in: {filepath}")
                updated_count += 1

    print("\n" + "="*40)
    print(f"🎉 Footer Audit & Replacement Complete!")
    print(f"Total pages synced: {updated_count}")
    print("="*40)

if __name__ == "__main__":
    replace_footer('.')