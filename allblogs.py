import os
from bs4 import BeautifulSoup

BLOG_DIR = 'blog'

# --- THE CSS TO INJECT ---
LAYOUT_CSS = """
<style id="blog-70-30-layout">
    /* Base Page Setup */
    .page-container { max-width: 1150px; margin: 0 auto; padding: 0 20px; }
    
    /* 70/30 Grid Structure */
    .page-grid {
        display: grid;
        grid-template-columns: minmax(0, 1fr) 360px;
        gap: 40px;
        margin-top: 40px;
        margin-bottom: 80px;
        align-items: start;
    }

    @media (max-width: 960px) {
        .page-grid { grid-template-columns: 1fr; gap: 30px; }
        .sidebar-col { order: -1; } /* Brings sidebar features to top on mobile */
    }

    /* Main Content Column & Bot */
    .main-col { display: flex; flex-direction: column; gap: 40px; min-width: 0; }
    
    .bot-wrap {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    .bot-header {
        background: #f8fafc;
        border-bottom: 1px solid #e2e8f0;
        padding: 16px 24px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .bot-badge {
        background: #1e3a8a;
        color: white;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 4px 10px;
        border-radius: 50px;
    }
    .bot-title { font-family: 'Lora', serif; font-weight: 600; color: #0f172a; margin: 0; font-size: 1.1rem;}
    .bot-wrap iframe { width: 100%; height: 750px; border: none; display: block; }

    /* Post Content Styling Constraints */
    .post-content-wrapper { background: #fff; padding: 40px; border-radius: 12px; border: 1px solid #e2e8f0; }
    .post-content-wrapper h2 { font-family: 'Lora', serif; color: #0a2342; margin-top: 30px; }
    .post-content-wrapper p, .post-content-wrapper li { font-family: 'Source Sans 3', sans-serif; font-size: 1.05rem; line-height: 1.7; color: #334155; }

    /* Sidebar Elements */
    .sidebar-col {
        position: sticky;
        top: 30px;
        display: flex;
        flex-direction: column;
        gap: 24px;
    }
    .sidebar-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 28px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .sidebar-card h3 {
        font-family: 'Lora', serif;
        font-size: 1.2rem;
        color: #0f172a;
        margin: 0 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 2px solid #f1f5f9;
    }
    
    .law-box { background: #f0f6ff; border: 1px solid #bfdbfe; border-left: 4px solid #1a56db; }
    .law-box strong { display: block; margin-bottom: 8px; color: #0a2342; font-size: 15px; font-family: 'DM Sans', sans-serif; }
    .law-box p { font-family: 'Source Sans 3', sans-serif; font-size: 14px; line-height: 1.6; color: #1e3a8a; margin: 0; }

    /* Timeline styling */
    .tl { list-style: none; padding: 0; margin: 0; border-left: 3px solid #1a56db; padding-left: 24px; display: flex; flex-direction: column; gap: 20px; }
    .tl li { position: relative; font-family: 'Source Sans 3', sans-serif; font-size: 14px; line-height: 1.55; color: #475569; }
    .tl li::before {
        content: ''; position: absolute; left: -31.5px; top: 3px; width: 12px; height: 12px;
        border-radius: 50%; background: #1a56db; border: 3px solid #fff; box-shadow: 0 0 0 1px #e2e8f0;
    }
    .tl li strong { display: block; color: #0f172a; font-size: 14px; font-weight: 600; margin-bottom: 4px; font-family: 'DM Sans', sans-serif;}

    /* Sidebar CTA */
    .cta-card { background: #0f172a; color: white; text-align: center; border: none;}
    .cta-card h4 { font-family: 'Lora', serif; font-size: 1.3rem; margin: 0 0 10px 0; }
    .cta-card p { font-family: 'Source Sans 3', sans-serif; font-size: 14px; color: #94a3b8; margin: 0 0 20px 0; line-height: 1.5; }
    .btn-gold {
        display: block;
        background: #d4af37;
        color: #0f172a;
        padding: 14px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 700;
        font-family: 'DM Sans', sans-serif;
        transition: background 0.2s;
    }
    .btn-gold:hover { background: #b8963a; }
</style>
"""

# --- THE BOT HTML ---
BOT_HTML = """
<div class="bot-wrap" id="letter-builder">
    <div class="bot-header">
        <span class="bot-badge">Free Tool</span>
        <h2 class="bot-title">Texas FIE Request Letter Builder</h2>
    </div>
    <iframe
        src="https://texas-fie-bot-831148457361.us-central1.run.app"
        title="Texas FIE Letter Builder"
        allow="clipboard-write"
        loading="lazy">
    </iframe>
</div>
"""

# --- THE SIDEBAR HTML ---
SIDEBAR_HTML = """
<aside class="sidebar-col">
    <div class="sidebar-card law-box">
        <strong>The Legal Basis</strong>
        <p>Your request is grounded in IDEA (20 U.S.C. § 1414), 19 TAC Chapter 89 Subchapter AA, and Texas Education Code Chapter 29. Under <em>Child Find</em>, your district must evaluate all children with suspected disabilities.</p>
    </div>
    <div class="sidebar-card">
        <h3>Evaluation Timeline</h3>
        <ul class="tl">
            <li>
                <strong>15 School Days</strong>
                District must provide Prior Written Notice responding to your written request.
            </li>
            <li>
                <strong>45 School Days</strong>
                The evaluation clock begins the day you sign and return the consent form.
            </li>
            <li>
                <strong>30 Calendar Days</strong>
                The ARD committee must meet to discuss the results and determine eligibility.
            </li>
        </ul>
    </div>
    <div class="sidebar-card cta-card">
        <h4>Stop Waiting</h4>
        <p>Districts often use verbal requests to delay. Start the legal clock today by putting your request in writing.</p>
        <a href="#letter-builder" class="btn-gold">Build Letter Free</a>
    </div>
</aside>
"""

def update_blog_post(filepath):
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Skip index.html since you just manually updated it
    if filepath.endswith('index.html'):
        print("Skipping index.html...")
        return

    # 1. Inject CSS if not present
    if not soup.find(id="blog-70-30-layout") and soup.head:
        soup.head.append(BeautifulSoup(LAYOUT_CSS, 'html.parser'))

    # 2. Identify the main content container
    # Typical blog posts wrap their text in a <main> or <div class="container">
    content_area = soup.find('main')
    if not content_area:
        containers = soup.find_all('div', class_='container')
        # Filter out header/footer containers, find the one with the blog text
        for c in containers:
            if not c.find_parent('header') and not c.find_parent('footer'):
                content_area = c
                break

    if not content_area:
        print(f"-> WARNING: Could not find main content area in {filepath}. Skipping.")
        return
        
    # Check if we already transformed this file
    if content_area.find('div', class_='page-grid'):
        print(f"-> Already updated. Skipping.")
        return

    # Extract all the original article content
    original_contents = list(content_area.children)
    
    # Clear the original container
    content_area.clear()

    # 3. Build the new structure
    # <div class="page-container">
    #   <div class="page-grid">
    #      <main class="main-col"> [BOT] <div class="post-content-wrapper"> [ORIGINAL ARTICLE] </div> </main>
    #      <aside> [SIDEBAR] </aside>
    #   </div>
    # </div>
    
    page_container = soup.new_tag("div", attrs={"class": "page-container"})
    page_grid = soup.new_tag("div", attrs={"class": "page-grid"})
    main_col = soup.new_tag("main", attrs={"class": "main-col"})
    article_wrapper = soup.new_tag("div", attrs={"class": "post-content-wrapper"})

    # Add the Bot to the top
    main_col.append(BeautifulSoup(BOT_HTML, 'html.parser'))

    # Add the original text into the article wrapper
    for child in original_contents:
        article_wrapper.append(child)
    
    main_col.append(article_wrapper)
    
    # Add Main column and Sidebar to the Grid
    page_grid.append(main_col)
    page_grid.append(BeautifulSoup(SIDEBAR_HTML, 'html.parser'))

    # Add Grid to Container, and Container back into the document
    page_container.append(page_grid)
    content_area.append(page_container)

    # Save the file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print(f"-> Successfully updated!")

if __name__ == "__main__":
    if not os.path.exists(BLOG_DIR):
        print(f"Error: Could not find directory '{BLOG_DIR}'. Ensure you are running this in the root folder.")
    else:
        for root, _, files in os.walk(BLOG_DIR):
            for file in files:
                if file.endswith('.html'):
                    update_blog_post(os.path.join(root, file))
        
        print("\nAll blog pages successfully updated!")