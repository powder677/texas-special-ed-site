import os
import bs4
from bs4 import BeautifulSoup

# Configuration
BLOG_DIR = 'blog'
BOT_IFRAME_HTML = """
<div class="bot-wrap" style="margin-bottom: 40px;">
    <h2 style="font-family: 'Lora', serif; color: #0a2342; margin-bottom: 20px;">Need an Official FIE Request Letter?</h2>
    <iframe 
        src="https://texas-fie-bot-831148457361.us-central1.run.app" 
        title="Texas FIE Letter Builder" 
        style="width: 100%; height: 820px; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,0.05);"
        allow="clipboard-write" 
        loading="lazy">
    </iframe>
</div>
"""

SIDEBAR_HTML = """
<aside class="sidebar-col">
    <div class="law-box">
        <strong>Legal Basis</strong>
        Your request is grounded in IDEA (20 U.S.C. § 1414), 19 TAC Chapter 89 Subchapter AA, and Texas Education Code Chapter 29. Under Child Find, your district must identify and evaluate all children with suspected disabilities.
    </div>

    <div class="timeline-card">
        <h3 style="font-family: 'Lora', serif; color: #0a2342; margin-top:0;">Action Timeline</h3>
        <ul class="tl">
            <li><strong>Day 1-15:</strong> District must respond in writing with Consent or Refusal.</li>
            <li><strong>Day 15-60:</strong> Once you sign, the 45-school-day evaluation clock begins.</li>
            <li><strong>Day 90:</strong> ARD meeting held to determine eligibility and IEP.</li>
        </ul>
    </div>
</aside>
"""

EXTRA_STYLES = """
<style>
.page-grid { display: grid; grid-template-columns: 1fr 320px; gap: 40px; margin-top: 40px; align-items: start; }
.sidebar-col { position: sticky; top: 20px; display: flex; flex-direction: column; gap: 20px; }
.law-box { background: #f0f6ff; border: 1px solid #bfdbfe; border-left: 4px solid #1a56db; border-radius: 8px; padding: 20px; font-size: 14px; line-height: 1.6; color: #1e3a8a; }
.timeline-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 24px; }
.tl { list-style: none; padding: 0; margin: 0; border-left: 3px solid #1a56db; padding-left: 20px; display: flex; flex-direction: column; gap: 16px; }
.tl li { position: relative; font-size: 14px; color: #475569; }
.tl li::before { content: ''; position: absolute; left: -27px; top: 5px; width: 12px; height: 12px; border-radius: 50%; background: #1a56db; border: 2px solid #fff; box-shadow: 0 0 0 2px #1a56db; }
@media (max-width: 900px) { .page-grid { grid-template-columns: 1fr; } .sidebar-col { order: 1; position: static; } }
</style>
"""

def transform_page(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 1. Add Styles
    if soup.head:
        soup.head.append(BeautifulSoup(EXTRA_STYLES, 'html.parser'))

    # 2. Find the main content area (usually <main> or a specific container)
    # We look for the container holding the blog text
    content_area = soup.find('main') or soup.find('div', class_='container')
    
    if content_area:
        # Create the Grid Structure
        grid_wrapper = soup.new_tag("div", attrs={"class": "page-grid"})
        main_col = soup.new_tag("div", attrs={"class": "main-content-col"})
        
        # Move existing content into the 70% column
        for element in list(content_area.contents):
            main_col.append(element)
        
        # Add the Bot to the 70% column
        main_col.append(BeautifulSoup(BOT_IFRAME_HTML, 'html.parser'))
        
        # Assemble the grid
        grid_wrapper.append(main_col)
        grid_wrapper.append(BeautifulSoup(SIDEBAR_HTML, 'html.parser'))
        
        # Clear main and add the grid
        content_area.clear()
        content_area.append(grid_wrapper)

        # Save changes
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"Successfully transformed: {file_path}")

# Run on all blog files
if os.path.exists(BLOG_DIR):
    for root, dirs, files in os.walk(BLOG_DIR):
        for file in files:
            if file.endswith('.html'):
                transform_page(os.path.join(root, file))