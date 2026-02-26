import os
import re

# Your exact requested footer
NEW_FOOTER = """<footer class="site-footer">
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

# Directories we DO NOT want to modify (protecting backups and git history)
SKIP_DIRS = {'.git', '_canonical_backups', '_trailing_slash_backups', 'districts_updated'}

def sync_footers():
    # Regex to match the footer, re.DOTALL makes '.' match newlines
    footer_pattern = re.compile(r'<footer[^>]*>.*?</footer>', re.DOTALL | re.IGNORECASE)
    updated_count = 0

    for root, dirs, files in os.walk('.'):
        # Modify dirs in-place to skip backup directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                
                try:
                    # Enforce utf-8 to prevent charmap encoding crashes on Windows
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Apply the replacement
                    new_content = re.sub(footer_pattern, NEW_FOOTER, content)

                    # Only write to disk if a change actually occurred
                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        updated_count += 1
                        print(f"Updated: {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    print(f"\n✅ Success! Synchronized the footer across {updated_count} files.")

if __name__ == "__main__":
    sync_footers()